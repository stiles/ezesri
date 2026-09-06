# Usage

## Python library

`ezesri` is designed to be used as a library for integration with your Python scripts.

-   **`get_metadata(url)`**: Fetches the raw metadata for a layer.
-   **`summarize_metadata(metadata)`**: Returns a human-readable summary of the metadata.
-   **`get_count(url, where, bbox, geometry, spatial_rel)`**: Asks the server how many features match a query, without downloading them.
-   **`get_codebook(url)`**: Returns a record of the layer's coded-value domains and date fields.
-   **`decode_dataframe(df, metadata, decode_domains, parse_dates)`**: Decodes an already-fetched DataFrame, returning `(df, report)`.
-   **`extract_layer(url, where, bbox, geometry, spatial_rel, out_sr, decode_domains, parse_dates)`**: Extracts a layer to a GeoDataFrame, with optional filters.
-   **`bulk_export(service_url, output_dir, output_format, workers, rate, where, bbox, geometry, spatial_rel, out_sr)`**: Downloads all layers from a MapServer or FeatureServer.

`geometry` accepts a GeoJSON geometry, Feature or FeatureCollection, as either a
dict or a JSON string. It is converted to Esri JSON before the query is sent, so
you never have to hand-build `rings` or `paths`.

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
### Count features before downloading

Check how big a layer is before committing to a download. The same filters apply.
```bash
ezesri count <URL>
ezesri count <URL> --where "STATUS = 'ACTIVE'"
ezesri count <URL> --bbox <xmin,ymin,xmax,ymax>
```

### Filtering

You can filter by a bounding box (in WGS84 coordinates), an attribute query or a
GeoJSON geometry:
```bash
ezesri fetch <URL> --bbox <xmin,ymin,xmax,ymax> --out <FILE>
ezesri fetch <URL> --where "STATUS = 'ACTIVE'" --out <FILE>
ezesri fetch <URL> --geometry boundary.geojson --out <FILE>
ezesri fetch <URL> --geometry boundary.geojson --spatial-rel esriSpatialRelWithin --out <FILE>
```

### Reprojecting output

Output is WGS84 (EPSG:4326) by default. Use `--out-sr` with any WKID the server
supports:
```bash
ezesri fetch <URL> --out-sr 3857 --format geojson --out output.geojson
```

### Large or fragile layers

Object ID queries page past the ArcGIS 1,000,000-ID transfer limit automatically,
so layers larger than 1M features extract in full. Feature batches default to the
lesser of the server's advertised `maxRecordCount` and 1,000, and halve on failure
before retrying — servers often advertise a `maxRecordCount` they cannot actually
serialize with geometry attached. Override it if you need to:

```bash
ezesri fetch <URL> --batch-size 250 --format geojson --out output.geojson
ezesri bulk-fetch <SERVICE_URL> <OUT_DIR> --format gpkg --batch-size 250
```

When a layer or a batch cannot be fetched, `extract_layer` raises `EsriLayerError`
rather than returning a partial frame. Check the size first with `ezesri count` if
you want to know what you are in for.

### Coded values and dates

Esri layers routinely store a status as `3`, with a domain elsewhere in the
metadata that maps 3 to "Under construction". Dates come back as epoch
milliseconds, so a filing date arrives as `1735689600000`. `ezesri` decodes both
by default:

| Field | Raw Esri value | ezesri output |
|---|---|---|
| `STATUS` | `3` | `Under construction` |
| `FILED` | `1735689600000` | `2025-01-01 00:00:00+00:00` |

Codes with no matching label are left alone and reported, rather than silently
blanked. Layers that use subtypes are handled too, where the same code can mean
different things depending on the subtype.

To keep the raw values:
```bash
ezesri fetch <URL> --raw-codes --raw-dates --format csv --out output.csv
```

Write a codebook alongside the export so the original codes stay recoverable:
```bash
ezesri fetch <URL> --format csv --out output.csv --codebook codebook.json

# inspect a layer's codes without downloading anything
ezesri codebook <URL>

# one codebook per layer during a bulk export
ezesri bulk-fetch <SERVICE_URL> <OUT_DIR> --format gpkg --codebooks
```

In Python, decoding is controlled the same way, and you can decode a DataFrame
you fetched yourself:

```python
import ezesri

gdf = ezesri.extract_layer(url)                      # decoded
raw = ezesri.extract_layer(url, decode_domains=False, parse_dates=False)

metadata = ezesri.get_metadata(url)
decoded, report = ezesri.decode_dataframe(raw, metadata)
print(report["decoded_fields"], report["unmapped_codes"])
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

Bulk export takes the same filters as `fetch`, applied to every layer in the
service:
```bash
ezesri bulk-fetch <SERVICE_URL> <OUT_DIR> --format gpkg --where "STATE = 'CA'"
ezesri bulk-fetch <SERVICE_URL> <OUT_DIR> --format gpkg --bbox <xmin,ymin,xmax,ymax>
```

### Bulk-fetch all layers from a service

You can discover and export all layers from a MapServer or FeatureServer to a specified directory.
```bash
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format gdb
```