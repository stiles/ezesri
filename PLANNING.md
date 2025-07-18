# Project overview

ezesri is a lightweight Python package for extracting data and metadata from Esri REST API endpoints. It provides a modular API and optional CLI for exporting feature layers and metadata to common formats, with robust handling of Esri-specific pagination and filtering.

## Core features

### Layer data extraction
- Export a feature layer to:
  - GeoDataFrame
  - GeoJSON
  - Shapefile
  - CSV (if geometry is not needed)
- Handle Esri pagination automatically
- Allow spatial filters (geometry, bbox) and attribute filters (where clause)
- Optional field selection (outFields)

### Metadata extraction
- Pull full layer metadata (f=json) from any endpoint
- Flatten and export to:
  - JSON
  - CSV (tabular field info)
- Return info such as:
  - name
  - geometryType
  - fields
  - spatialReference
  - extent
  - maxRecordCount

### CLI tool
- Command-line interface for data and metadata export
- Example usage:
  - `ezesri fetch --url <layer_url> --format geojson --out riverside_trees.geojson`
  - `ezesri metadata --url <layer_url> --out metadata.csv`

### Bulk exporter
- Given a base service URL, iterate through all layers (e.g., /MapServer or /FeatureServer)
- Save each as its own GeoJSON or Shapefile

## Dependencies
- requests
- geopandas (for GeoJSON and shapefile conversion)
- pandas
- pyproj, shapely (via geopandas)
- Optional: click for CLI

## Pagination strategy
Esri supports two main methods for pagination:

- Object ID batching:
  - Get all objectIds
  - Fetch in chunks using objectIds=<comma-separated-list>
  - Reliable and flexible
- resultOffset / resultRecordCount:
  - Works if the server supports pagination
  - Simpler to implement, but not always supported

The package will:
- Detect support for usePagination
- Prefer objectIds if needed

## Existing libraries and differentiation

- pyesridump / esridump: Simple, widely used, but not modular, lacks shapefile/CSV export and metadata extraction, not actively maintained
- arcgis: Full Esri SDK, heavy dependencies, overkill for light data extraction
- ogr2ogr (GDAL CLI): Powerful, but complex and not Pythonic

ezesri aims to be:
- Lightweight and modular
- Pythonic API with CLI option
- Support for GeoJSON, shapefile, CSV output
- Metadata export
- Robust pagination handling
- Open source and vendor neutral

## Implementation roadmap

### Phase 1 – Core functionality (Complete)
- `extract_layer(url, out_format='geojson')`
- `get_metadata(url)`
- Internal pagination handler
- Output to GeoJSON or GeoDataFrame

### Phase 2 – CLI and export (Complete)
- CLI wrapper via click
- Add shapefile, CSV, and GeoPackage options

### Phase 3 – Bulk and advanced features (Complete)
- Recursive export of all layers in a service
- Geometry filters (bbox, within, intersects)
- Rate limiting and retry backoff
- Improved error handling (e.g., suggesting `bulk-fetch` for service URLs)
- Summarized metadata output

### Phase 4 - Future improvements

This section lists potential features and improvements for future releases, prioritized from most to least critical.

1.  **Add authentication support**: Allow users to provide an authentication token to access secured Esri services.
2.  **Create a test suite (Complete)**: Develop a suite of unit tests using `pytest` to ensure code quality and prevent regressions.
3.  **Build more documentation**: Create a full documentation site using Sphinx or MkDocs and host it on Read the Docs. Include more examples with real-world URLs. (Examples added)
4.  **Support more output formats (Complete)**: Add support for exporting to other formats, such as File Geodatabase (`.gdb`).
5.  **Add advanced CLI options (Complete)**: Improve the CLI with more convenient aliases for options. 