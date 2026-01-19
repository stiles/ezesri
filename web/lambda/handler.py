"""
AWS Lambda handler for ezesri web API.

Provides endpoints for extracting data from Esri REST services.
Currently supports GeoJSON export. Shapefile/GeoParquet require additional setup.
"""

import json
import logging
import base64
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlparse

import requests

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Feature count limit to prevent timeout on massive layers
MAX_FEATURES = 50000


def get_metadata(url: str) -> dict:
    """Fetches layer metadata from an Esri REST API endpoint."""
    params = {'f': 'json'}
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch metadata: {e}")
        return {"error": str(e)}


def summarize_metadata(metadata: dict) -> dict:
    """Creates a structured summary from metadata."""
    if "error" in metadata:
        return metadata
    
    # Get feature count
    feature_count = None
    try:
        # Try to get actual count via query
        base_url = metadata.get('_source_url', '')
        if base_url:
            count_response = requests.get(
                f"{base_url}/query",
                params={'where': '1=1', 'returnCountOnly': 'true', 'f': 'json'},
                timeout=30
            )
            if count_response.ok:
                count_data = count_response.json()
                feature_count = count_data.get('count')
    except Exception as e:
        logger.warning(f"Could not get feature count: {e}")
    
    # Extract fields info
    fields = []
    for field in metadata.get('fields', []):
        fields.append({
            'name': field.get('name'),
            'type': field.get('type', '').replace('esriFieldType', ''),
            'alias': field.get('alias')
        })
    
    # Extract extent
    extent = metadata.get('extent', {})
    extent_info = None
    if extent:
        extent_info = {
            'xmin': extent.get('xmin'),
            'ymin': extent.get('ymin'),
            'xmax': extent.get('xmax'),
            'ymax': extent.get('ymax'),
            'spatialReference': extent.get('spatialReference', {}).get('wkid')
        }
    
    return {
        'name': metadata.get('name', 'Unknown'),
        'description': metadata.get('description', ''),
        'geometryType': metadata.get('geometryType', '').replace('esriGeometry', ''),
        'featureCount': feature_count,
        'maxRecordCount': metadata.get('maxRecordCount'),
        'spatialReference': metadata.get('spatialReference', {}).get('wkid'),
        'extent': extent_info,
        'fields': fields,
        'hasGeometry': metadata.get('geometryType') is not None
    }


def extract_layer(
    url: str,
    where: str = '1=1',
    bbox: Optional[tuple] = None,
    max_features: int = MAX_FEATURES
) -> Dict[str, Any]:
    """
    Extracts features from an Esri layer and returns as GeoJSON.
    
    Returns dict with 'type': 'FeatureCollection' and 'features' array.
    """
    # Get metadata first
    metadata = get_metadata(url)
    if "error" in metadata:
        return {"error": metadata["error"]}
    
    has_geometry = metadata.get('geometryType') is not None
    max_record_count = metadata.get('maxRecordCount', 1000)
    
    # Get object IDs first
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
    
    # Check feature count limit
    total_features = len(object_ids)
    if total_features > max_features:
        return {
            "error": f"Layer has {total_features:,} features, which exceeds the limit of {max_features:,}. Please add a filter to reduce the number of features.",
            "featureCount": total_features
        }
    
    # Fetch features in batches
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


def handle_metadata(url: str) -> Dict[str, Any]:
    """Handle /metadata endpoint."""
    if not url:
        return {
            "statusCode": 400,
            "body": {"error": "Missing 'url' parameter"}
        }
    
    # Validate URL format
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return {
            "statusCode": 400,
            "body": {"error": "Invalid URL format"}
        }
    
    metadata = get_metadata(url)
    if "error" in metadata:
        return {
            "statusCode": 400,
            "body": metadata
        }
    
    # Add source URL for count query
    metadata['_source_url'] = url
    summary = summarize_metadata(metadata)
    
    return {
        "statusCode": 200,
        "body": summary
    }


def handle_extract(params: dict) -> Dict[str, Any]:
    """Handle /extract endpoint."""
    url = params.get('url')
    if not url:
        return {
            "statusCode": 400,
            "body": {"error": "Missing 'url' parameter"}
        }
    
    # Parse optional parameters
    where = params.get('where', '1=1')
    format_type = params.get('format', 'geojson').lower()
    
    # Parse bbox if provided
    bbox = None
    bbox_str = params.get('bbox')
    if bbox_str:
        try:
            bbox = tuple(map(float, bbox_str.split(',')))
            if len(bbox) != 4:
                raise ValueError("bbox must have 4 values")
        except (ValueError, AttributeError) as e:
            return {
                "statusCode": 400,
                "body": {"error": f"Invalid bbox format: {e}. Expected: xmin,ymin,xmax,ymax"}
            }
    
    # Extract the layer
    result = extract_layer(url, where=where, bbox=bbox)
    
    if "error" in result:
        return {
            "statusCode": 400,
            "body": result
        }
    
    # Return based on format
    if format_type == 'geojson':
        return {
            "statusCode": 200,
            "body": result,
            "contentType": "application/geo+json",
            "filename": "export.geojson"
        }
    else:
        # Shapefile and GeoParquet require geopandas which needs a container deployment
        return {
            "statusCode": 400,
            "body": {"error": f"Format '{format_type}' is not yet supported. Currently only 'geojson' is available."}
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for ezesri web API.
    
    Supports both API Gateway and Lambda Function URL event formats.
    """
    try:
        # Log event for debugging
        logger.info(f"Event: {json.dumps(event)[:500]}")
        
        # Handle warmup pings
        if event.get("warmup"):
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "warm"})
            }
        
        # Parse request - handle both API Gateway and Function URL formats
        request_context = event.get('requestContext', {})
        
        # API Gateway format
        if 'httpMethod' in event:
            method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
        # Function URL format
        else:
            http_info = request_context.get('http', {})
            method = http_info.get('method', 'GET')
            path = http_info.get('path', '/')
        
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        
        # Parse body for POST requests
        body_params = {}
        if method == 'POST' and event.get('body'):
            body = event['body']
            if event.get('isBase64Encoded'):
                body = base64.b64decode(body).decode('utf-8')
            
            # Try JSON first, then form-urlencoded
            content_type = (event.get('headers') or {}).get('content-type', '')
            if 'application/json' in content_type:
                body_params = json.loads(body)
            else:
                # Parse form-urlencoded
                parsed = parse_qs(body)
                body_params = {k: v[0] for k, v in parsed.items()}
        
        # Merge params (body takes precedence)
        params = {**query_params, **body_params}
        
        # Route to handler
        if path == '/metadata' or path.endswith('/metadata'):
            result = handle_metadata(params.get('url'))
        elif path == '/extract' or path.endswith('/extract'):
            result = handle_extract(params)
        elif path == '/' or path == '':
            # Health check / info endpoint
            result = {
                "statusCode": 200,
                "body": {
                    "service": "ezesri",
                    "version": "1.0.0",
                    "formats": ["geojson"],
                    "endpoints": {
                        "/metadata": "GET - Fetch layer metadata",
                        "/extract": "POST - Extract layer data (GeoJSON)"
                    }
                }
            }
        else:
            result = {
                "statusCode": 404,
                "body": {"error": f"Unknown path: {path}"}
            }
        
        # Build response
        status_code = result.get('statusCode', 200)
        body = result.get('body', {})
        content_type = result.get('contentType', 'application/json')
        is_base64 = result.get('isBase64Encoded', False)
        
        headers = {
            "Content-Type": content_type,
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        
        # Add download headers if filename provided
        if 'filename' in result:
            headers['Content-Disposition'] = f"attachment; filename=\"{result['filename']}\""
        
        response = {
            "statusCode": status_code,
            "headers": headers,
        }
        
        if is_base64:
            response["body"] = body
            response["isBase64Encoded"] = True
        else:
            response["body"] = json.dumps(body)
        
        return response
        
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
