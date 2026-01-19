# ezesri

Extract data from Esri REST API endpoints. Available as a **[web app](https://ezesri.com)**, Python library and CLI.

## Web app

Don't have Python installed? Use the web app at **[ezesri.com](https://ezesri.com)** to extract GeoJSON directly in your browser. No installation required.

## Python package

`ezesri` is also a lightweight Python package for extracting data and metadata from Esri REST API endpoints. It provides a modular API and optional CLI for exporting feature layers and metadata to common formats, with robust handling of Esri-specific pagination and filtering.

### Why use the Python package?

Many tools exist for interacting with Esri services, but they often come with trade-offs:
-   **pysridump/esridump**: Simple and widely used, but not modular, lacks modern export formats, and is not actively maintained.
-   **ArcGIS API for Python**: A full-featured Esri SDK, but its heavy dependencies make it overkill for simple data extraction.
-   **ogr2ogr (GDAL)**: Extremely powerful, but can be complex to use and is not a native Python library.

### Key features

-   **Multiple export formats**: GeoJSON, Shapefile, GeoPackage, File Geodatabase, GeoParquet, Parquet, NDJSON
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
-   **`extract_layer(url, where, bbox, geometry, out_sr)`**: Extracts a layer to a GeoDataFrame, with optional filters.
-   **`bulk_fetch(service_url, output_dir, file_format)`**: Downloads all layers from a MapServer or FeatureServer.

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

You can also filter by a bounding box (in WGS84 coordinates) or an attribute query:
```bash
ezesri fetch <URL> --bbox <xmin,ymin,xmax,ymax> --out <FILE>
ezesri fetch <URL> --where "STATUS = 'ACTIVE'" --out <FILE>
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

## Contributing

Contributions are welcome! Please see the [contributing guide](CONTRIBUTING.md) for more information.
