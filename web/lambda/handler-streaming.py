"""
AWS Lambda handler with streaming response support for large payloads.
"""

import csv
import io
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlparse
from awslambdaric.lambda_context import LambdaContext
import awslambdaric

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MAX_FEATURES = 100000


def geojson_to_csv(geojson: dict) -> str:
    """Convert GeoJSON to CSV."""
    features = geojson.get('features', [])
    if not features:
        return ""
    
    all_fields = set()
    for feature in features:
        props = feature.get('properties', {})
        if props:
            all_fields.update(props.keys())
    
    field_names = sorted(all_fields)
    has_geometry = features[0].get('geometry') is not None
    geom_type = features[0].get('geometry', {}).get('type', '') if has_geometry else ''
    include_latlon = geom_type == 'Point'
    
    output = io.StringIO()
    
    if include_latlon:
        columns = field_names + ['latitude', 'longitude']
    else:
        columns = field_names
    
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    
    for feature in features:
        row = feature.get('properties', {}) or {}
        
        if include_latlon and feature.get('geometry'):
            coords = feature['geometry'].get('coordinates', [])
            if len(coords) >= 2:
                row['longitude'] = coords[0]
                row['latitude'] = coords[1]
        
        writer.writerow(row)
    
    return output.getvalue()


def get_metadata(url: str) -> dict:
    """Fetch layer metadata."""
    params = {'f': 'json'}
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch metadata: {e}")
        return {"error": str(e)}


def extract_layer(url: str, where: str = '1=1', bbox: Optional[tuple] = None, max_features: int = MAX_FEATURES) -> Dict[str, Any]:
    """Extract features from Esri layer."""
    metadata = get_metadata(url)
    if "error" in metadata:
        return {"error": metadata["error"]}
    
    has_geometry = metadata.get('geometryType') is not None
    max_record_count = metadata.get('maxRecordCount', 1000)
    
    params = {
        'f': 'json',
        'where': where,
        'returnIdsOnly': 'true'
    }
    
    if bbox and has_geometry:
        params['geometry'] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        params['geometryType'] = 'esriGeometryEnvelope'
        params['inSR'] = '4326'
        params['spatialRel'] = 'esriSpatialRelIntersects'
    
    try:
        r = requests.get(f"{url}/query", params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to get object IDs: {e}"}
    
    if 'error' in data:
        return {"error": f"Esri API error: {data['error']}"}
    
    object_ids = data.get('objectIds', [])
    
    if not object_ids:
        return {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {"featureCount": 0}
        }
    
    total_features = len(object_ids)
    if total_features > max_features:
        return {
            "error": f"Layer has {total_features:,} features, which exceeds limit of {max_features:,}. Add a filter to reduce the count.",
            "featureCount": total_features,
            "limitExceeded": True
        }
    
    all_features = []
    
    for i in range(0, len(object_ids), max_record_count):
        batch = object_ids[i:i + max_record_count]
        params = {
            'f': 'geojson' if has_geometry else 'json',
            'where': where,
            'objectIds': ','.join(map(str, batch)),
            'outFields': '*',
        }
        if has_geometry:
            params['returnGeometry'] = 'true'
            params['outSR'] = '4326'
        
        try:
            r = requests.post(f"{url}/query", data=params, timeout=120)
            r.raise_for_status()
            features_json = r.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch batch: {e}")
            continue
        
        if 'error' in features_json:
            logger.error(f"Esri error in batch: {features_json['error']}")
            continue
        
        features = features_json.get('features', [])
        all_features.extend(features)
    
    return {
        "type": "FeatureCollection",
        "features": all_features,
        "metadata": {
            "featureCount": len(all_features),
            "hasGeometry": has_geometry
        }
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for Function URL."""
    try:
        logger.info(f"Event: {json.dumps(event)[:500]}")
        
        request_context = event.get('requestContext', {})
        http_info = request_context.get('http', {})
        method = http_info.get('method', 'GET')
        path = http_info.get('path', '/')
        
        # Handle OPTIONS for CORS
        if method == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": ""
            }
        
        query_params = event.get('queryStringParameters') or {}
        body_params = {}
        
        if method == 'POST' and event.get('body'):
            body = event['body']
            if event.get('isBase64Encoded'):
                import base64
                body = base64.b64decode(body).decode('utf-8')
            
            headers = event.get('headers') or {}
            content_type = headers.get('content-type') or headers.get('Content-Type') or ''
            
            if 'application/json' in content_type:
                body_params = json.loads(body)
            else:
                parsed = parse_qs(body)
                body_params = {k: v[0] for k, v in parsed.items()}
        
        params = {**query_params, **body_params}
        
        # Route requests
        if path == '/metadata' or path.endswith('/metadata'):
            url = params.get('url')
            if not url:
                return {"statusCode": 400, "body": json.dumps({"error": "Missing 'url' parameter"})}
            
            metadata = get_metadata(url)
            if "error" in metadata:
                return {"statusCode": 400, "body": json.dumps(metadata)}
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(metadata)
            }
        
        elif path == '/extract' or path.endswith('/extract'):
            url = params.get('url')
            if not url:
                return {"statusCode": 400, "body": json.dumps({"error": "Missing 'url' parameter"})}
            
            where = params.get('where', '1=1')
            format_type = params.get('format', 'geojson').lower()
            
            bbox = None
            bbox_str = params.get('bbox')
            if bbox_str:
                try:
                    bbox = tuple(map(float, bbox_str.split(',')))
                    if len(bbox) != 4:
                        raise ValueError("bbox must have 4 values")
                except (ValueError, AttributeError) as e:
                    return {"statusCode": 400, "body": json.dumps({"error": f"Invalid bbox: {e}"})}
            
            result = extract_layer(url, where=where, bbox=bbox)
            
            if "error" in result:
                return {"statusCode": 400, "body": json.dumps(result)}
            
            if format_type == 'geojson':
                body_content = json.dumps(result)
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/geo+json",
                        "Content-Disposition": "attachment; filename=\"export.geojson\"",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Expose-Headers": "Content-Disposition",
                    },
                    "body": body_content
                }
            elif format_type == 'csv':
                csv_data = geojson_to_csv(result)
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "text/csv",
                        "Content-Disposition": "attachment; filename=\"export.csv\"",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Expose-Headers": "Content-Disposition",
                    },
                    "body": csv_data
                }
            else:
                return {"statusCode": 400, "body": json.dumps({"error": f"Format '{format_type}' not supported"})}
        
        else:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({
                    "service": "ezesri",
                    "version": "2.0.0",
                    "formats": ["geojson", "csv"],
                    "endpoints": {
                        "/metadata": "GET - Fetch layer metadata",
                        "/extract": "POST - Extract layer data"
                    }
                })
            }
        
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }
