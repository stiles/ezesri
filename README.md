# ezesri

A lightweight Python package for extracting data from Esri REST API endpoints.

## Installation

```bash
pip install .
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