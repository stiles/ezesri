# ezesri Lambda API

AWS Lambda backend for the ezesri web interface.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and API info |
| `/metadata` | GET | Fetch layer metadata |
| `/extract` | POST | Extract layer data as GeoJSON or Shapefile |

## Parameters

### `/metadata`

| Parameter | Required | Description |
|-----------|----------|-------------|
| `url` | Yes | Esri REST layer URL |

### `/extract`

| Parameter | Required | Description |
|-----------|----------|-------------|
| `url` | Yes | Esri REST layer URL |
| `format` | No | `geojson` (default) or `shapefile` |
| `where` | No | SQL where clause filter |
| `bbox` | No | Bounding box: `xmin,ymin,xmax,ymax` |

## Deployment

### Prerequisites

1. AWS CLI configured
2. AWS SAM CLI installed
3. Docker (for building)

### First deployment

```bash
cd web/lambda
sam build
sam deploy --guided
```

### Subsequent deployments

```bash
sam build && sam deploy
```

### Get your Function URL

After deployment, SAM outputs the Function URL:

```
Outputs
-------
Key                 FunctionUrl
Value               https://abc123xyz.lambda-url.us-west-2.on.aws/
```

## Lambda layer

The function requires geopandas for shapefile export. Options:

1. **Use existing shapely layer** (GeoJSON only): Already configured in template.yaml
2. **Create geopandas layer** (full shapefile support): See [lambgeo/docker-lambda](https://github.com/lambgeo/docker-lambda)

To create your own layer:

```bash
# Build geopandas layer
docker run --rm -v $(pwd):/var/task lambci/lambda:build-python3.11 \
    pip install geopandas -t python/

# Zip and upload
zip -r geopandas-layer.zip python/
aws lambda publish-layer-version \
    --layer-name geopandas-python311 \
    --zip-file fileb://geopandas-layer.zip \
    --compatible-runtimes python3.11
```

## Local testing

```bash
# Start local API
sam local start-api

# Test metadata endpoint
curl "http://localhost:3000/metadata?url=https://services.arcgis.com/.../FeatureServer/0"

# Test extract endpoint
curl -X POST "http://localhost:3000/extract" \
    -d "url=https://services.arcgis.com/.../FeatureServer/0" \
    -d "format=geojson"
```
