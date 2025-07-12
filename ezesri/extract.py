import geopandas as gpd
import pandas as pd
import os
from typing import Union
from .utils import make_request
import requests
from tqdm import tqdm


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

def extract_layer(
    url: str,
    where: str = '1=1',
    bbox: tuple = None,
    geometry: str = None,
    spatial_rel: str = 'esriSpatialRelIntersects',
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

    Returns:
        A GeoDataFrame or DataFrame containing the features from the layer.
    """
    metadata = get_metadata(url)
    if not metadata:
        return gpd.GeoDataFrame()

    has_geometry = metadata.get('geometryType') is not None
    max_record_count = metadata.get('maxRecordCount', 1000)

    # 1. Get Object IDs
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

    try:
        r = make_request(f"{url}/query", params=params)
        data = r.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get object IDs from {url}. Error: {e}")
        return gpd.GeoDataFrame() if has_geometry else pd.DataFrame()

    if 'error' in data:
        print(f"Could not get Object IDs for {url}. Server response: {data['error']}")
        return gpd.GeoDataFrame() if has_geometry else pd.DataFrame()

    object_ids = data.get('objectIds')

    if not object_ids:
        return gpd.GeoDataFrame() if has_geometry else pd.DataFrame()

    # 2. Fetch features in batches
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
            params['outSR'] = '4326'

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

    # 3. Create DataFrame or GeoDataFrame
    if not all_features:
        return gpd.GeoDataFrame() if has_geometry else pd.DataFrame()
        
    if has_geometry:
        return gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
    else:
        rows = [f['attributes'] for f in all_features]
        return pd.DataFrame(rows)

def bulk_export(service_url: str, output_dir: str, output_format: str = 'geojson'):
    """
    Discovers and exports all layers from a MapServer or FeatureServer.

    Args:
        service_url: The base URL of the Esri service.
        output_dir: The directory to save the output files to.
        output_format: The format to save the files in ('geojson', 'shapefile', 'csv', 'gdb').
    """
    print(f"Fetching service metadata from: {service_url}")
    service_metadata = get_metadata(service_url)
    if not service_metadata or 'layers' not in service_metadata:
        print("Could not fetch service metadata or no layers found.")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    gdb_path = None
    if output_format == 'gdb':
        # Sanitize service name for the GDB filename
        service_name = os.path.basename(service_url.rstrip('/'))
        sanitized_name = "".join(c for c in service_name if c.isalnum() or c in (' ', '_')).rstrip()
        gdb_path = os.path.join(output_dir, f"{sanitized_name}.gdb")
        print(f"Output will be saved to File Geodatabase: {gdb_path}")

    for layer in service_metadata['layers']:
        if layer.get('type') == 'Group Layer':
            print(f"--- Skipping Group Layer: {layer.get('name', 'Unnamed')} (ID: {layer['id']}) ---")
            continue

        layer_id = layer['id']
        layer_name = layer.get('name', f"layer_{layer_id}").replace(" ", "_").replace("/", "-")
        layer_url = f"{service_url}/{layer_id}"
        
        print(f"--- Processing layer: {layer_name} (ID: {layer_id}) ---")
        
        try:
            df = extract_layer(layer_url)
            if df.empty:
                print(f"Layer is empty or could not be extracted. Skipping.")
                continue

            is_spatial = isinstance(df, gpd.GeoDataFrame)
            
            if not is_spatial and output_format in ['geojson', 'shapefile', 'gdb']:
                print(f"Cannot save non-spatial layer {layer_name} as {output_format}. Skipping.")
                continue
            
            if output_format == 'gdb':
                print(f"Saving to {gdb_path}...")
                df.to_file(gdb_path, driver='FileGDB', layer=layer_name)
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

        except Exception as e:
            print(f"Failed to process layer {layer_name} (ID: {layer_id}). Error: {e}") 