# ezesri

Extract data from Esri REST API endpoints. Available as a **[web app](https://ezesri.com)**, Python library and CLI.

## Web app

Don't have Python installed? Use the web app at **[ezesri.com](https://ezesri.com)** to extract GeoJSON directly in your browser. No installation required.

## Public Data Directory

Browse **24,000+ public ArcGIS Feature Services** from government agencies worldwide at **[ezesri.com/directory](https://ezesri.com/directory)**. Find parcels, zoning, elections, crime, weather, sports facilities, wildlife data and more — all searchable and filterable by 32 categories.

## Python package

`ezesri` is also a lightweight Python package for extracting data and metadata from Esri REST API endpoints. It provides a modular API and optional CLI for exporting feature layers and metadata to common formats, with robust handling of Esri-specific pagination and filtering.

### Why use the Python package?

Many tools exist for interacting with Esri services, but they often come with trade-offs:
-   **pysridump/esridump**: Simple and widely used, but not modular, lacks modern export formats, and is not actively maintained.
-   **ArcGIS API for Python**: A full-featured Esri SDK, but its heavy dependencies make it overkill for simple data extraction.
-   **ogr2ogr (GDAL)**: Extremely powerful, but can be complex to use and is not a native Python library.

### Key features

-   **Multiple export formats**: GeoJSON, Shapefile, GeoPackage, File Geodatabase, GeoParquet, Parquet, NDJSON
-   **Readable output**: Coded values become labels and Esri's epoch-millisecond dates become timestamps, by default
-   **Automatic pagination**: Handles Esri's record limits seamlessly
-   **Filtering**: Filter by bounding box, geometry, or SQL where clause
-   **Bulk exports**: Download all layers from a MapServer or FeatureServer
-   **CLI**: Command-line interface for quick extraction
-   **Clean metadata**: Human-readable layer summaries

### Installation

```bash
pip install ezesri
```

### Quickstart

Here's a simple example of how to use `ezesri` as a library to extract data and metadata.

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

## Documentation

Full documentation is available at **[ezesri.com/docs](https://ezesri.com/docs)**

## Usage

### Python library

`ezesri` is designed to be used as a library for integration with your Python scripts.

-   **`get_metadata(url)`**: Fetches the raw metadata for a layer.
-   **`summarize_metadata(metadata)`**: Returns a human-readable summary of the metadata.
-   **`get_count(url, where, bbox, geometry, spatial_rel)`**: Asks the server how many features match a query, without downloading them.
-   **`get_codebook(url)`**: Returns a record of the layer's coded-value domains and date fields.
-   **`decode_dataframe(df, metadata, decode_domains, parse_dates)`**: Decodes an already-fetched DataFrame, returning `(df, report)`.
-   **`extract_layer(url, where, bbox, geometry, spatial_rel, out_sr, decode_domains, parse_dates)`**: Extracts a layer to a GeoDataFrame, with optional filters.
-   **`bulk_export(service_url, output_dir, output_format, ...)`**: Downloads all layers from a MapServer or FeatureServer.

`geometry` accepts a GeoJSON geometry, Feature or FeatureCollection, as either a
dict or a JSON string, and is converted to Esri JSON before the query is sent.

### Command-line interface (CLI)

`ezesri` also provides a command-line tool for quick data extraction.

#### Fetch metadata

Get a clean, human-readable summary of a layer's metadata.
```bash
ezesri metadata "https://gis.countyofriverside.us/arcgis/rest/services/mmc/mmc_mSrvc_v12_prod/MapServer/8"
```

To get the raw JSON output, use the `--json` flag:
```bash
ezesri metadata <YOUR_ESRI_LAYER_URL> --json
```

#### Fetch layer data

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

#### Count features before downloading

Check how big a layer is before committing to a download. `count` takes the same
filters as `fetch`.
```bash
ezesri count <URL>
ezesri count <URL> --where "STATUS = 'ACTIVE'"
```

#### Filtering

You can filter by a bounding box (in WGS84 coordinates), an attribute query or a
GeoJSON geometry:
```bash
ezesri fetch <URL> --bbox <xmin,ymin,xmax,ymax> --out <FILE>
ezesri fetch <URL> --where "STATUS = 'ACTIVE'" --out <FILE>
ezesri fetch <URL> --geometry boundary.geojson --out <FILE>
```

#### Reprojecting output

Output is WGS84 (EPSG:4326) by default. Use `--out-sr` with any WKID the server supports:
```bash
ezesri fetch <URL> --out-sr 3857 --format geojson --out output.geojson
```

#### Large or fragile layers

Object ID queries page past the ArcGIS 1,000,000-ID transfer limit automatically,
so layers larger than 1M features extract in full. Feature batches default to the
lesser of the server's advertised `maxRecordCount` and 1,000, and halve on failure
before retrying — servers often advertise a `maxRecordCount` they cannot actually
serialize with geometry attached. Override it if you need to:

```bash
ezesri fetch <URL> --batch-size 250 --format geojson --out output.geojson
```

#### Coded values and dates

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
ezesri fetch <URL> --raw-codes --raw-dates --out output.csv --format csv
```

Write a codebook alongside the export so the original codes stay recoverable:
```bash
ezesri fetch <URL> --format csv --out output.csv --codebook codebook.json

# or inspect a layer's codes without downloading anything
ezesri codebook <URL>
```

#### Bulk-fetch all layers from a service

You can discover and export all layers from a MapServer or FeatureServer to a specified directory.
```bash
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format gdb
```
Or use GeoPackage as an open, broadly supported alternative:
```bash
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format gpkg
```

You can also write per-layer files in these formats:
```bash
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format geoparquet
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format parquet
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format ndjson
```

Speed and politeness options:
```bash
# use 4 parallel workers
ezesri bulk-fetch <SERVICE_URL> <OUT_DIR> --format geoparquet --workers 4
# apply a global rate limit of 2 requests/second across all workers
ezesri bulk-fetch <SERVICE_URL> <OUT_DIR> --format geoparquet --workers 4 --rate 2
```

Bulk export takes the same filters as `fetch`, applied to every layer:
```bash
ezesri bulk-fetch <SERVICE_URL> <OUT_DIR> --format gpkg --where "STATE = 'CA'"
ezesri bulk-fetch <SERVICE_URL> <OUT_DIR> --format gpkg --bbox <xmin,ymin,xmax,ymax>
```

## Examples

For a detailed, real-world example of using `ezesri` to acquire, process, and visualize data, see the scripts in the `examples/` directory. These examples demonstrate how to download data, merge it, and create a map.

To run these examples, you will first need to install the required dependencies:
```bash
pip install geopandas matplotlib
```
Then, you can run the scripts directly:
```bash
python examples/00_palm_springs_fetch.py
python examples/01_palm_springs_pools_map.py
```

## Testing

This project uses `pytest` for unit testing. For details on how to run the test suite, please see the [testing guide](https://ezesri.com/docs/testing).

## Deploying the Web App

The web app consists of two parts:

### Frontend (Next.js on Vercel)

The frontend auto-deploys to Vercel on push to `main`. No manual steps required.

### Backend (AWS Lambda)

The API backend requires manual deployment via AWS SAM:

```bash
cd web/lambda
sam build && sam deploy
```

Prerequisites:
- AWS CLI configured with credentials
- AWS SAM CLI installed (`brew install aws-sam-cli` on Mac)

See `web/lambda/README.md` for more details.

## Contributing

Contributions are welcome! Please see the [contributing guide](CONTRIBUTING.md) for more information.
