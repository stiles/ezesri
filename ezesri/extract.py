import geopandas as gpd
import pandas as pd
import os
from typing import Optional, Union
from .utils import make_request, has_filegdb_write_support, drop_empty_geometries, unique_geometry_types, write_ndjson, set_rate_limit
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Cap per-request feature batches. Servers often advertise a high
# maxRecordCount they cannot actually serialize with full geometry.
DEFAULT_MAX_BATCH_SIZE = 1000


class EsriLayerError(Exception):
    """Raised when an Esri layer metadata or query response contains an error."""

    def __init__(self, message: str, code=None, details=None):
        self.code = code
        self.details = details
        super().__init__(message)


def _raise_for_esri_error(payload: dict, context: str):
    """Raise EsriLayerError when a response body includes Esri's error object."""
    if not isinstance(payload, dict) or 'error' not in payload:
        return
    err = payload['error'] or {}
    if isinstance(err, dict):
        code = err.get('code')
        message = err.get('message') or err.get('description') or str(err)
        details = err.get('details')
    else:
        code = None
        message = str(err)
        details = None
    raise EsriLayerError(
        f"{context}: code={code} message={message}",
        code=code,
        details=details,
    )


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

def _fetch_all_object_ids(url: str, query_params: dict, oid_field: str = 'OBJECTID') -> list:
    """Fetch all matching object IDs, paging past ArcGIS transfer limits.

    Hosted Feature Services often cap a single ``returnIdsOnly`` response at
    1,000,000 IDs and set ``exceededTransferLimit``. Subsequent pages use
    ``resultOffset`` with a stable ``orderByFields`` so IDs are not skipped or
    duplicated.
    """
    all_ids = []
    offset = 0

    while True:
        params = dict(query_params)
        params.update({
            'f': 'json',
            'returnIdsOnly': 'true',
            'orderByFields': f'{oid_field} ASC',
        })
        if offset:
            params['resultOffset'] = offset

        try:
            r = make_request(f"{url}/query", params=params)
            data = r.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise EsriLayerError(f"Failed to get object IDs from {url}: {e}") from e

        if 'error' in data:
            # Some older services reject orderByFields / resultOffset on
            # returnIdsOnly. Retry once without them when still on page one.
            if offset == 0 and all_ids == []:
                try:
                    r = make_request(f"{url}/query", params=query_params)
                    data = r.json()
                except (requests.exceptions.RequestException, ValueError) as e:
                    raise EsriLayerError(f"Failed to get object IDs from {url}: {e}") from e
                if 'error' in data:
                    _raise_for_esri_error(data, f"Could not get Object IDs for {url}")
                ids = data.get('objectIds') or []
                if data.get('exceededTransferLimit'):
                    print(
                        f"Warning: Object ID query for {url} hit the server transfer "
                        f"limit ({len(ids)} IDs). This service does not support paging "
                        "ID queries, so some features may be missing."
                    )
                return ids

            _raise_for_esri_error(data, f"Could not get Object IDs for {url}")

        ids = data.get('objectIds') or []
        if not ids:
            break

        all_ids.extend(ids)

        if not data.get('exceededTransferLimit'):
            break

        offset += len(ids)
        print(f"Object ID transfer limit reached; fetching next page at offset {offset}...")

    return all_ids


def _query_features_batch(
    url: str,
    object_ids: list,
    where: str,
    has_geometry: bool,
    query_format: str,
) -> list:
    """Fetch one batch of features by object ID. Raises EsriLayerError on failure."""
    params = {
        'f': query_format,
        'where': where,
        'objectIds': ','.join(map(str, object_ids)),
        'outFields': '*',
    }
    if has_geometry:
        params['returnGeometry'] = 'true'
        params['outSR'] = '4326'

    try:
        r = make_request(f"{url}/query", method='post', data=params)
        features_json = r.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        raise EsriLayerError(f"Failed to fetch a batch from {url}: {e}") from e

    _raise_for_esri_error(features_json, f"Error fetching batch from {url}")
    return features_json.get('features', [])


def _fetch_features_adaptive(
    url: str,
    object_ids: list,
    where: str,
    has_geometry: bool,
    query_format: str,
    batch_size: int,
) -> list:
    """Download features in batches, halving batch size when a request fails."""
    all_features = []
    batch_size = max(1, batch_size)
    i = 0

    with tqdm(total=len(object_ids), desc="Downloading features") as pbar:
        while i < len(object_ids):
            size = min(batch_size, len(object_ids) - i)
            batch = object_ids[i:i + size]
            try:
                features = _query_features_batch(
                    url, batch, where, has_geometry, query_format
                )
            except EsriLayerError as e:
                if size <= 1:
                    raise EsriLayerError(
                        f"Failed to fetch features from {url} even with batch size 1: {e}"
                    ) from e
                new_size = max(1, size // 2)
                print(
                    f"Batch of {size} failed ({e}); "
                    f"retrying with batch size {new_size}..."
                )
                batch_size = new_size
                continue

            all_features.extend(features)
            i += size
            pbar.update(size)

    return all_features


def extract_layer(
    url: str,
    where: str = '1=1',
    bbox: tuple = None,
    geometry: str = None,
    spatial_rel: str = 'esriSpatialRelIntersects',
    batch_size: Optional[int] = None,
) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Extracts a feature layer or table into a GeoDataFrame or DataFrame.

    If the layer has geometry, it returns a GeoDataFrame.
    If the layer is a table (no geometry), it returns a pandas DataFrame.

    Args:
        url: The URL of the feature layer or table.
        where: An optional SQL-like where clause to filter features.
        bbox: An optional tuple defining a bounding box (xmin, ymin, xmax, ymax) to filter by.
        geometry: An optional GeoJSON string or dictionary representing a geometry to filter by.
        spatial_rel: The spatial relationship to use for filtering. Defaults to 'esriSpatialRelIntersects'.
        batch_size: Optional per-request feature count. Defaults to the lesser of the
            layer's maxRecordCount and 1000. On failure the batch is halved and retried.

    Returns:
        A GeoDataFrame or DataFrame containing the features from the layer.

    Raises:
        EsriLayerError: If the layer metadata or a feature query returns an Esri error,
            or if feature batches keep failing after shrinking to size 1.
    """
    metadata = get_metadata(url)
    if not metadata:
        return gpd.GeoDataFrame()

    _raise_for_esri_error(metadata, f"Esri layer metadata request failed for {url}")

    where = where or '1=1'
    has_geometry = metadata.get('geometryType') is not None
    advertised_max = metadata.get('maxRecordCount') or DEFAULT_MAX_BATCH_SIZE
    if batch_size is not None:
        max_record_count = max(1, batch_size)
    else:
        max_record_count = max(1, min(int(advertised_max), DEFAULT_MAX_BATCH_SIZE))
    oid_field = metadata.get('objectIdField') or 'OBJECTID'

    # 1. Get Object IDs (paged when the server hits its transfer limit)
    params = {
        'f': 'json',
        'where': where,
        'returnIdsOnly': 'true'
    }

    if bbox is not None and has_geometry:
        params['geometry'] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        params['geometryType'] = 'esriGeometryEnvelope'
        params['inSR'] = '4326'  # Assume WGS84 for bbox input
        params['spatialRel'] = 'esriSpatialRelIntersects'
    elif geometry and has_geometry:
        params['geometry'] = geometry
        params['geometryType'] = 'esriGeometryPolygon'  # Assumes polygon, could be expanded
        params['inSR'] = '4326'
        params['spatialRel'] = spatial_rel

    object_ids = _fetch_all_object_ids(url, params, oid_field=oid_field)

    if not object_ids:
        return gpd.GeoDataFrame() if has_geometry else pd.DataFrame()

    # 2. Fetch features in adaptive batches
    query_format = 'geojson' if has_geometry else 'json'
    all_features = _fetch_features_adaptive(
        url,
        object_ids,
        where=where,
        has_geometry=has_geometry,
        query_format=query_format,
        batch_size=max_record_count,
    )

    # 3. Create DataFrame or GeoDataFrame
    if not all_features:
        return gpd.GeoDataFrame() if has_geometry else pd.DataFrame()
        
    if has_geometry:
        return gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
    else:
        rows = [f['attributes'] for f in all_features]
        return pd.DataFrame(rows)

def bulk_export(service_url: str, output_dir: str, output_format: str = 'geojson', workers: int = 1, rate: float = 0.0):
    """
    Discovers and exports all layers from a MapServer or FeatureServer.

    Args:
        service_url: The base URL of the Esri service.
        output_dir: The directory to save the output files to.
        output_format: The format to save the files in ('geojson', 'shapefile', 'csv', 'gdb', 'gpkg', 'geoparquet', 'parquet', 'ndjson').
        workers: Number of parallel workers to use.
        rate: Global max requests per second across all workers (0 to disable).
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
            df = extract_layer(layer_url)
            if df.empty:
                print(f"Layer is empty or could not be extracted. Skipping.")
                return False

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