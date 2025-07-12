# ezesri

A lightweight Python package for extracting data from Esri REST API endpoints.

[![PyPI version](https://badge.fury.io/py/ezesri.svg)](https://badge.fury.io/py/ezesri)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Multiple export formats**: Export to GeoJSON, Shapefile, CSV, File Geodatabase, and GeoDataFrame.
- **Robust extraction**: Automatically handles Esri's pagination.
- **Filtering**: Filter data by bounding box or attribute query.
- **Bulk exports**: Download all layers from a MapServer or FeatureServer.
- **Simple CLI**: An easy-to-use command-line interface for all features.
- **Human-readable metadata**: Get a clean summary of layer metadata.

## Installation

```bash
pip install ezesri
```

## Usage

### Python library

You can use `ezesri` as a library to integrate with your Python scripts.

```python
import ezesri

# URL for a public Esri feature layer, e.g. City of Los Angeles boundaries: 
# https://services5.arcgis.com/VAb1qw880ksyBtIL/ArcGIS/rest/services/City_Boundary_of_Los_Angeles_(new)/FeatureServer/0
url = "your_esri_layer_url_here"

# Get layer metadata
metadata = ezesri.get_metadata(url)
print(ezesri.summarize_metadata(metadata))

# Extract layer to a GeoDataFrame
gdf = ezesri.extract_layer(url)
print(gdf.head())
```

### Command-line interface

`ezesri` also provides a command-line tool for quick data extraction.

#### Fetch metadata

Get a clean, human-readable summary of a layer's metadata.

```bash
ezesri metadata <YOUR_ESRI_LAYER_URL>
```

To get the raw JSON output, use the `--json` flag:
```bash
ezesri metadata <YOUR_ESRI_LAYER_URL> --json
```

#### Fetch layer data

You can fetch a layer and save it to a file in various formats.

-   **GeoJSON**
    ```bash
    ezesri fetch <YOUR_ESRI_LAYER_URL> --format geojson --out output.geojson
    ```

-   **Shapefile**
    ```bash
    ezesri fetch <YOUR_ESRI_LAYER_URL> --format shapefile --out output.shp
    ```

-   **CSV** (geometry is dropped)
    ```bash
    ezesri fetch <YOUR_ESRI_LAYER_URL> --format csv --out output.csv
    ```

-   **File Geodatabase**
    ```bash
    ezesri fetch <YOUR_ESRI_LAYER_URL> --format gdb --out output.gdb
    ```

You can also filter by a bounding box (in WGS84 coordinates):
```bash
ezesri fetch <URL> --bbox <xmin,ymin,xmax,ymax> --format geojson --out <FILE>
```

Or, use a more advanced spatial filter with a GeoJSON object:
```bash
ezesri fetch <URL> --geometry '{"type": "Polygon", ...}' --format geojson --out <FILE>
```

#### Bulk-fetch all layers from a service

You can discover and export all layers from a MapServer or FeatureServer to a specified directory.

```bash
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY> --format gdb
```

## CLI command aliases

To make the CLI easier to use, the following aliases are available for common options:

- `--out`: `--output`
- `--format`: `--fmt`
- `--spatial-rel`: `--srs`

## Examples

For a detailed, real-world example of using `ezesri` to acquire, process, and visualize data, see the scripts in the `examples/` directory:

-   `examples/palm_springs_fetch.py`: Demonstrates how to use `ezesri` to download data from multiple Esri feature layers, merge them based on a common attribute, and save the result as a GeoJSON file.
-   `examples/palm_springs_pools_map.py`: Shows how to load the prepared data, perform analysis to identify residential properties, and create a final map visualizing the results with `matplotlib`.

To run these examples, you will first need to install the required dependencies:
```bash
pip install geopandas matplotlib
```
Then, you can run the scripts directly:
```bash
python examples/palm_springs_fetch.py
python examples/palm_springs_pools_map.py
```

## Testing

This project uses `pytest` for unit testing. For details on how to run the test suite, please see the [testing guide](TESTING.md).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss your ideas.
