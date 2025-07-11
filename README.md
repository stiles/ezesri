# ezesri

A lightweight Python package for extracting data from Esri REST API endpoints.

[![PyPI version](https://badge.fury.io/py/ezesri.svg)](https://badge.fury.io/py/ezesri)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Multiple export formats**: Export to GeoJSON, Shapefile, CSV, and GeoDataFrame.
- **Robust extraction**: Automatically handles Esri's pagination.
- **Filtering**: Filter data by bounding box or attribute query.
- **Bulk exports**: Download all layers from a MapServer or FeatureServer.
- **Simple CLI**: An easy-to-use command-line interface for all features.

## Installation

```bash
pip install ezesri
```

## Usage

### Python library

You can use `ezesri` as a library to integrate with your Python scripts.

```python
import ezesri

# URL for a public Esri feature layer
url = "your_esri_layer_url_here"

# Get layer metadata
metadata = ezesri.get_metadata(url)
print(metadata)

# Extract layer to a GeoDataFrame
gdf = ezesri.extract_layer(url)
print(gdf.head())
```

### Command-line interface

`ezesri` also provides a command-line tool for quick data extraction.

#### Fetch metadata

```bash
ezesri metadata <YOUR_ESRI_LAYER_URL>
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

You can also filter by a bounding box (in WGS84 coordinates):
```bash
ezesri fetch <URL> --bbox <xmin,ymin,xmax,ymax> --format geojson --out <FILE>
```

#### Bulk-fetch all layers from a service

You can discover and export all layers from a MapServer or FeatureServer to a specified directory.

```bash
ezesri bulk-fetch <YOUR_ESRI_SERVICE_URL> <YOUR_OUTPUT_DIRECTORY>
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss your ideas.
