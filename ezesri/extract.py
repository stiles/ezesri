import geopandas as gpd
import pandas as pd
import json
import os
from typing import Optional, Union
from .utils import (
    make_request,
    has_filegdb_write_support,
    drop_empty_geometries,
    unique_geometry_types,
    write_ndjson,
    set_rate_limit,
    geojson_to_esri_geometry,
    decode_dataframe,
    build_codebook,
)
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def get_metadata(url: str) -> dict:
    """Fetches layer metadata from an Esri REST API endpoint.

    Args:
        url: The URL of the feature layer.

    Returns:
        A dictionary containing the layer's metadata.
    """
    params = {'f': 'json'}
    try:
        response = make_request(url, params=params)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {}

def summarize_metadata(metadata: dict) -> str:
    """
    Creates a human-readable summary from a metadata dictionary.

    Args:
        metadata: The metadata dictionary from the Esri JSON response.

    Returns:
        A formatted string containing the summarized metadata.
    """
    summary = []
    
    # Basic info
    summary.append(f"Layer Name: {metadata.get('name', 'N/A')}")
    summary.append(f"Description: {metadata.get('description', 'N/A')}")
    summary.append(f"Geometry Type: {metadata.get('geometryType', 'N/A')}")
    summary.append(f"Record Count: {metadata.get('maxRecordCount', 'N/A')}")
    
    # Spatial reference
    sr = metadata.get('spatialReference', {})
    if sr:
        summary.append(f"Spatial Reference (WKID): {sr.get('wkid', 'N/A')}")

    # Extent
    extent = metadata.get('extent')
    if extent:
        summary.append("Extent:")
        summary.append(f"  XMin: {extent.get('xmin')}, YMin: {extent.get('ymin')}")
        summary.append(f"  XMax: {extent.get('xmax')}, YMax: {extent.get('ymax')}")

    # Fields
    fields = metadata.get('fields')
    if fields:
        summary.append("\nFields:")
        for field in fields:
            summary.append(f"  - {field.get('name', 'N/A')} (Type: {field.get('type', 'N/A')}, Alias: {field.get('alias', 'N/A')})")
            
    return "\n".join(summary)

def get_codebook(url: str) -> dict:
    """
    Builds a codebook of every coded-value domain and date field on a layer.

    Write this alongside an export so the original codes stay recoverable.

    Args:
        url: The URL of the feature layer or table.

    Returns:
        A JSON-serializable codebook, or an empty dict if metadata is unavailable.
    """
    metadata = get_metadata(url)
    if not metadata:
        return {}
    return build_codebook(metadata)


def _build_spatial_filter(
    bbox: tuple = None,
    geometry=None,
    spatial_rel: str = 'esriSpatialRelIntersects',
) -> dict:
    """
    Builds the Esri query parameters for a spatial filter.

    Args:
        bbox: A bounding box (xmin, ymin, xmax, ymax) in WGS84.
        geometry: A GeoJSON geometry, Feature, FeatureCollection or JSON string.
        spatial_rel: The spatial relationship to apply.

    Returns:
        A dict of query parameters, empty when no spatial filter is requested.
    """
    if bbox is not None:
        return {
            'geometry': f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
            'geometryType': 'esriGeometryEnvelope',
            'inSR': '4326',  # bbox input is documented as WGS84
            'spatialRel': spatial_rel,
        }

    if geometry:
        esri_geometry, geometry_type = geojson_to_esri_geometry(geometry)
        return {
            'geometry': esri_geometry,
            'geometryType': geometry_type,
            'inSR': '4326',
            'spatialRel': spatial_rel,
        }

    return {}


def get_count(
    url: str,
    where: str = '1=1',
    bbox: tuple = None,
    geometry=None,
    spatial_rel: str = 'esriSpatialRelIntersects',
) -> Optional[int]:
    """
    Asks the server how many features match a query, without downloading them.

    Args:
        url: The URL of the feature layer or table.
        where: An optional SQL-like where clause to filter features.
        bbox: An optional bounding box (xmin, ymin, xmax, ymax) in WGS84.
        geometry: An optional GeoJSON geometry to filter by.
        spatial_rel: The spatial relationship to use for filtering.

    Returns:
        The feature count, or None if the server does not report one.
    """
    params = {
        'f': 'json',
        'where': where or '1=1',
        'returnCountOnly': 'true',
    }
    params.update(_build_spatial_filter(bbox, geometry, spatial_rel))

    try:
        r = make_request(f"{url}/query", params=params)
        data = r.json()
    except requests.exceptions.RequestException as e:
        print(f"Could not get a feature count from {url}. Error: {e}")
        return None

    if 'error' in data:
        print(f"Could not get a feature count for {url}. Server response: {data['error']}")
        return None

    count = data.get('count')
    return int(count) if count is not None else None


def extract_layer(
    url: str,
    where: str = '1=1',
    bbox: tuple = None,
    geometry=None,
    spatial_rel: str = 'esriSpatialRelIntersects',
    out_sr: int = 4326,
    decode_domains: bool = True,
    parse_dates: bool = True,
) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Extracts a feature layer or table into a GeoDataFrame or DataFrame.

    If the layer has geometry, it returns a GeoDataFrame.
    If the layer is a table (no geometry), it returns a pandas DataFrame.

    Args:
        url: The URL of the feature layer or table.
        where: An optional SQL-like where clause to filter features.
        bbox: An optional tuple defining a bounding box (xmin, ymin, xmax, ymax) to filter by.
        geometry: An optional GeoJSON geometry, Feature, FeatureCollection or JSON
            string to filter by.
        spatial_rel: The spatial relationship to use for filtering. Defaults to 'esriSpatialRelIntersects'.
        out_sr: The WKID of the output spatial reference. Defaults to 4326 (WGS84).
        decode_domains: Replace Esri coded values with their labels. Defaults to True.
        parse_dates: Convert Esri date fields to timestamps. Defaults to True.

    Returns:
        A GeoDataFrame or DataFrame containing the features from the layer.
    """
    # A None where clause would be dropped by requests, sending a query with no
    # filter at all, which some servers reject.
    where = where or '1=1'

    metadata = get_metadata(url)
    if not metadata:
        return gpd.GeoDataFrame()

    has_geometry = metadata.get('geometryType') is not None
    max_record_count = metadata.get('maxRecordCount', 1000)

    empty = gpd.GeoDataFrame() if has_geometry else pd.DataFrame()

    try:
        spatial_filter = _build_spatial_filter(
            bbox if has_geometry else None,
            geometry if has_geometry else None,
            spatial_rel,
        )
    except ValueError as e:
        print(f"Invalid geometry filter: {e}")
        return empty

    # 1. Ask the server for the expected count so truncation can be detected
    expected_count = get_count(
        url,
        where=where,
        bbox=bbox if has_geometry else None,
        geometry=geometry if has_geometry else None,
        spatial_rel=spatial_rel,
    )

    # 2. Get Object IDs
    params = {
        'f': 'json',
        'where': where,
        'returnIdsOnly': 'true'
    }
    params.update(spatial_filter)

    try:
        r = make_request(f"{url}/query", params=params)
        data = r.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get object IDs from {url}. Error: {e}")
        return empty

    if 'error' in data:
        print(f"Could not get Object IDs for {url}. Server response: {data['error']}")
        return empty

    object_ids = data.get('objectIds')

    if not object_ids:
        return empty

    # Some servers cap returnIdsOnly, which would silently truncate the download
    if data.get('exceededTransferLimit'):
        print(
            f"Warning: {url} reported exceededTransferLimit while listing object IDs. "
            f"Only {len(object_ids):,} IDs were returned and the export will be incomplete. "
            "Narrow the query with --where or --bbox."
        )
    elif expected_count is not None and len(object_ids) < expected_count:
        print(
            f"Warning: the server reports {expected_count:,} matching features but returned only "
            f"{len(object_ids):,} object IDs. The export will be incomplete. "
            "Narrow the query with --where or --bbox."
        )

    # 3. Fetch features in batches
    all_features = []
    query_format = 'geojson' if has_geometry else 'json'

    for i in tqdm(range(0, len(object_ids), max_record_count), desc="Downloading features"):
        batch = object_ids[i:i + max_record_count]
        params = {
            'f': query_format,
            'where': where,
            'objectIds': ','.join(map(str, batch)),
            'outFields': '*',
        }
        if has_geometry:
            params['returnGeometry'] = 'true'
            params['outSR'] = str(out_sr)

        try:
            r = make_request(f"{url}/query", method='post', data=params)
            features_json = r.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch a batch from {url}. Error: {e}")
            continue

        if 'error' in features_json:
            print(f"Error fetching batch from {url}: {features_json['error']}")
            continue

        features = features_json.get('features', [])
        all_features.extend(features)

    # 4. Verify the download against what the server said it had
    if expected_count is not None and len(all_features) != expected_count:
        print(
            f"Warning: expected {expected_count:,} features from {url} but downloaded "
            f"{len(all_features):,}. Some batches may have failed."
        )

    # 5. Create DataFrame or GeoDataFrame
    if not all_features:
        return empty

    if has_geometry:
        df = gpd.GeoDataFrame.from_features(all_features, crs=f"EPSG:{out_sr}")
    else:
        rows = [f['attributes'] for f in all_features]
        df = pd.DataFrame(rows)

    # 6. Replace coded values with labels and turn epoch dates into timestamps
    if decode_domains or parse_dates:
        df, report = decode_dataframe(
            df, metadata, decode_domains=decode_domains, parse_dates=parse_dates
        )
        if report['decoded_fields']:
            print(f"Decoded coded values in: {', '.join(report['decoded_fields'])}")
        if report['date_fields']:
            print(f"Parsed dates in: {', '.join(report['date_fields'])}")
        for field, codes in report['unmapped_codes'].items():
            preview = ', '.join(str(c) for c in codes[:5])
            suffix = f" (and {len(codes) - 5} more)" if len(codes) > 5 else ""
            print(
                f"Note: {field} had codes with no matching label, left as-is: {preview}{suffix}"
            )

    return df

def bulk_export(
    service_url: str,
    output_dir: str,
    output_format: str = 'geojson',
    workers: int = 1,
    rate: float = 0.0,
    where: str = '1=1',
    bbox: tuple = None,
    geometry=None,
    spatial_rel: str = 'esriSpatialRelIntersects',
    out_sr: int = 4326,
    decode_domains: bool = True,
    parse_dates: bool = True,
    write_codebook: bool = False,
):
    """
    Discovers and exports all layers from a MapServer or FeatureServer.

    Args:
        service_url: The base URL of the Esri service.
        output_dir: The directory to save the output files to.
        output_format: The format to save the files in ('geojson', 'shapefile', 'csv', 'gdb', 'gpkg', 'geoparquet', 'parquet', 'ndjson').
        workers: Number of parallel workers to use.
        rate: Global max requests per second across all workers (0 to disable).
        where: An optional SQL-like where clause applied to every layer.
        bbox: An optional bounding box (xmin, ymin, xmax, ymax) in WGS84.
        geometry: An optional GeoJSON geometry to filter by.
        spatial_rel: The spatial relationship to use for filtering.
        out_sr: The WKID of the output spatial reference.
        decode_domains: Replace Esri coded values with their labels. Defaults to True.
        parse_dates: Convert Esri date fields to timestamps. Defaults to True.
        write_codebook: Write a <layer>.codebook.json next to each layer's output.
    """
    if rate and rate > 0:
        set_rate_limit(rate)

    print(f"Fetching service metadata from: {service_url}")
    service_metadata = get_metadata(service_url)
    if not service_metadata or 'layers' not in service_metadata:
        print("Could not fetch service metadata or no layers found.")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    gdb_path = None
    gpkg_path = None
    if output_format == 'gdb':
        supported, msg = has_filegdb_write_support()
        if not supported:
            print(msg)
            print(f"Tip: Try: ezesri bulk-fetch {service_url} {output_dir} --format gpkg")
            return
        # Sanitize service name for the GDB filename
        service_name = os.path.basename(service_url.rstrip('/'))
        sanitized_name = "".join(c for c in service_name if c.isalnum() or c in (' ', '_')).rstrip()
        gdb_path = os.path.join(output_dir, f"{sanitized_name}.gdb")
        print(f"Output will be saved to File Geodatabase: {gdb_path}")
    elif output_format == 'gpkg':
        service_name = os.path.basename(service_url.rstrip('/'))
        sanitized_name = "".join(c for c in service_name if c.isalnum() or c in (' ', '_')).rstrip()
        gpkg_path = os.path.join(output_dir, f"{sanitized_name}.gpkg")
        print(f"Output will be saved to GeoPackage: {gpkg_path}")

    # Locks for container formats to prevent concurrent writes to the same file
    container_write_lock = threading.Lock()

    def process_layer(layer):
        if layer.get('type') == 'Group Layer':
            print(f"--- Skipping Group Layer: {layer.get('name', 'Unnamed')} (ID: {layer['id']}) ---")
            return False

        layer_id = layer['id']
        layer_name = layer.get('name', f"layer_{layer_id}").replace(" ", "_").replace("/", "-")
        layer_url = f"{service_url}/{layer_id}"

        print(f"--- Processing layer: {layer_name} (ID: {layer_id}) ---")
        try:
            df = extract_layer(
                layer_url,
                where=where,
                bbox=bbox,
                geometry=geometry,
                spatial_rel=spatial_rel,
                out_sr=out_sr,
                decode_domains=decode_domains,
                parse_dates=parse_dates,
            )
            if df.empty:
                print(f"Layer is empty or could not be extracted. Skipping.")
                return False

            if write_codebook:
                codebook = get_codebook(layer_url)
                if codebook:
                    codebook_path = os.path.join(output_dir, f"{layer_name}.codebook.json")
                    with open(codebook_path, 'w', encoding='utf-8') as f:
                        json.dump(codebook, f, indent=2, default=str)

            is_spatial = isinstance(df, gpd.GeoDataFrame)

            if not is_spatial and output_format in ['geojson', 'shapefile', 'gdb', 'gpkg', 'geoparquet']:
                print(f"Cannot save non-spatial layer {layer_name} as {output_format}. Skipping.")
                return False

            if output_format == 'gdb':
                print(f"Saving to {gdb_path}...")
                df_clean, dropped = drop_empty_geometries(df)
                if dropped:
                    print(f"Warning: Dropped {dropped} features with null/empty geometry for layer {layer_name}.")
                geom_types = unique_geometry_types(df_clean)
                if len(geom_types) > 1:
                    print(
                        f"Skipping layer {layer_name}: mixed geometry types detected {geom_types}. "
                        "GDB writes generally require a single geometry type per layer."
                    )
                    return False
                with container_write_lock:
                    df_clean.to_file(gdb_path, driver='FileGDB', layer=layer_name)
            elif output_format == 'gpkg':
                print(f"Saving to {gpkg_path}...")
                df_clean, dropped = drop_empty_geometries(df)
                if dropped:
                    print(f"Warning: Dropped {dropped} features with null/empty geometry for layer {layer_name}.")
                with container_write_lock:
                    df_clean.to_file(gpkg_path, driver='GPKG', layer=layer_name)
            elif output_format in ['geoparquet', 'parquet', 'ndjson']:
                ext = '.parquet' if output_format in ['geoparquet', 'parquet'] else '.ndjson'
                output_path = os.path.join(output_dir, f"{layer_name}{ext}")
                print(f"Saving to {output_path}...")
                if output_format == 'parquet':
                    df_to_save = df.drop(columns='geometry', errors='ignore')
                    df_to_save.to_parquet(output_path)
                elif output_format == 'geoparquet':
                    df_clean, dropped = drop_empty_geometries(df)
                    if dropped:
                        print(f"Warning: Dropped {dropped} features with null/empty geometry for layer {layer_name}.")
                    df_clean.to_parquet(output_path)
                else:  # ndjson
                    df_clean, dropped = (drop_empty_geometries(df) if is_spatial else (df, 0))
                    if dropped:
                        print(f"Warning: Dropped {dropped} features with null/empty geometry for layer {layer_name}.")
                    write_ndjson(df_clean, output_path)
            else:
                file_extension = {
                    'geojson': '.geojson', 'shapefile': '.shp', 'csv': '.csv'
                }[output_format]
                output_path = os.path.join(output_dir, f"{layer_name}{file_extension}")
                print(f"Saving to {output_path}...")
                if output_format == 'csv':
                    df.drop(columns='geometry', errors='ignore').to_csv(output_path, index=False)
                else:
                    df.to_file(output_path, driver='GeoJSON' if output_format == 'geojson' else None)

            print(f"Successfully saved {layer_name}.")
            return True
        except Exception as e:
            print(f"Failed to process layer {layer_name} (ID: {layer_id}). Error: {e}")
            return False

    layers = service_metadata['layers']
    if workers <= 1:
        for layer in layers:
            process_layer(layer)
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(process_layer, layer) for layer in layers]
            for _ in as_completed(futures):
                pass