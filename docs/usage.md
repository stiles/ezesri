# Usage

## Python library

`ezesri` is designed to be used as a library for integration with your Python scripts.

-   **`get_metadata(url)`**: Fetches the raw metadata for a layer.
-   **`summarize_metadata(metadata)`**: Returns a human-readable summary of the metadata.
-   **`extract_layer(url, where, bbox, geometry, out_sr)`**: Extracts a layer to a GeoDataFrame, with optional filters.
-   **`bulk_fetch(service_url, output_dir, file_format)`**: Downloads all layers from a MapServer or FeatureServer.

### Example

```python
import ezesri

# URL for Riverside County, CA parcels layer
url = "https://gis.countyofriverside.us/arcgis/rest/services/mmc/mmc_mSrvc_v12_prod/MapServer/8"

# Get layer metadata
metadata = ezesri.get_metadata(url)
print("## Layer Metadata Summary")
print(ezesri.summarize_metadata(metadata))

# Extract layer to a GeoDataFrame
print("\n## Extracting Layer to GeoDataFrame")
gdf = ezesri.extract_layer(url, where="APN LIKE '750%'")
print(f"Successfully extracted {len(gdf)} features.")
print(gdf.head())
```

## Command-line interface (CLI)

`ezesri` also provides a command-line tool for quick data extraction.

### Fetch metadata

Get a clean, human-readable summary of a layer's metadata.
```bash
ezesri metadata "https://gis.countyofriverside.us/arcgis/rest/services/mmc/mmc_mSrvc_v12_prod/MapServer/8"
```

To get the raw JSON output, use the `--json` flag:
```bash
ezesri metadata <YOUR_ESRI_LAYER_URL> --json
```

### Fetch layer data

You can fetch a layer and save it to a file in various formats.

-   **GeoJSON**
```bash
ezesri fetch <URL> --format geojson --out output.geojson
```

-   **Shapefile**
```bash
ezesri fetch <URL> --format shapefile --out output.shp
```

-   **GeoPackage**
```bash
ezesri fetch <URL> --format gpkg --out output.gpkg
```

-   **File Geodatabase**
```bash
ezesri fetch <URL> --format gdb --out output.gdb
```

-   **GeoParquet (spatial)**
```bash
ezesri fetch <URL> --format geoparquet --out output.parquet
```

-   **Parquet (tabular)**
```bash
ezesri fetch <URL> --format parquet --out output.parquet
```

-   **NDJSON (streaming)**
```bash
# to stdout
ezesri fetch <URL> --format ndjson
# to file
ezesri fetch <URL> --format ndjson --out output.ndjson
```
You can also filter by a bounding box (in WGS84 coordinates) or an attribute query:
```bash
ezesri fetch <URL> --bbox <xmin,ymin,xmax,ymax> --out <FILE>
ezesri fetch <URL> --where "STATUS = 'ACTIVE'" --out <FILE>
```

### Bulk export example

```bash
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format gpkg
```

Per-layer bulk outputs:
```bash
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format geoparquet
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format parquet
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format ndjson
```

Parallelism and rate limiting:
```bash
# run with 4 workers
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format gpkg --workers 4
# limit overall request rate to 1 req/s across workers
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format gpkg --workers 4 --rate 1
```

### Bulk-fetch all layers from a service

You can discover and export all layers from a MapServer or FeatureServer to a specified directory.
```bash
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format gdb
```