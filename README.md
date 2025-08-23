# ezesri

<p align="center">
  <strong>A lightweight Python package for extracting data from Esri REST API endpoints.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/ezesri/">
    <img src="https://badge.fury.io/py/ezesri.svg" alt="PyPI version">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
</p>

---

`ezesri` is a lightweight Python package for extracting data and metadata from Esri REST API endpoints. It provides a modular API and optional CLI for exporting feature layers and metadata to common formats, with robust handling of Esri-specific pagination and filtering.

## Why ezesri?

Many tools exist for interacting with Esri services, but they often come with trade-offs:
-   **pysridump/esridump**: Simple and widely used, but not modular, lacks modern export formats, and is not actively maintained.
-   **ArcGIS API for Python**: A full-featured Esri SDK, but its heavy dependencies make it overkill for simple data extraction.
-   **ogr2ogr (GDAL)**: Extremely powerful, but can be complex to use and is not a native Python library.

`ezesri` aims to be:
-   **Lightweight**: Minimal dependencies, keeping your environment clean.
-   **Pythonic**: A simple, intuitive API that integrates seamlessly into your workflows.
-   **Flexible**: A modular API with an optional CLI for quick, one-off tasks.
-   **Robust**: Handles Esri pagination automatically so you don't have to.
-   **Modern**: Exports to common formats like GeoJSON, Shapefile, and GeoDataFrame.

## Key Features

-   **Multiple export formats**: Export to GeoJSON, Shapefile, CSV, File Geodatabase, and GeoDataFrame.
-   **Robust extraction**: Automatically handles Esri's pagination.
-   **Filtering**: Filter data by bounding box, geometry, or attribute query.
-   **Bulk exports**: Download all layers from a MapServer or FeatureServer.
-   **Simple CLI**: An easy-to-use command-line interface for all features.
-   **Human-readable metadata**: Get a clean summary of layer metadata.

## Installation

```bash
pip install ezesri
```

## Quickstart

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

## Usage

### Python Library

`ezesri` is designed to be used as a library for integration with your Python scripts.

-   **`get_metadata(url)`**: Fetches the raw metadata for a layer.
-   **`summarize_metadata(metadata)`**: Returns a human-readable summary of the metadata.
-   **`extract_layer(url, where, bbox, geometry, out_sr)`**: Extracts a layer to a GeoDataFrame, with optional filters.
-   **`bulk_fetch(service_url, output_dir, file_format)`**: Downloads all layers from a MapServer or FeatureServer.

### Command-Line Interface (CLI)

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

-   **File Geodatabase**
    ```bash
    ezesri fetch <URL> --format gdb --out output.gdb
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

This project uses `pytest` for unit testing. For details on how to run the test suite, please see the [testing guide](docs/testing.md).

## Contributing

Contributions are welcome! Please see the [contributing guide](CONTRIBUTING.md) for more information.
