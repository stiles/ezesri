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

### Phase 4 - Continuing improvements

- **Create a test suite (Complete)**: Develop a suite of unit tests using `pytest` to ensure code quality and prevent regressions.
- **Build more documentation (Complete)**: Full documentation on Read the Docs: https://ezesri.readthedocs.io/. Examples added.
- **Support more output formats (Complete)**: Add support for exporting to other formats, such as File Geodatabase (`.gdb`).
- **Add advanced CLI options (Complete)**: Improve the CLI with more convenient aliases for options. 

### UX-focused enhancements (status)

1.  **Better CLI UX (Partial)**: NDJSON writes to stdout. Still open: read URLs from a file or stdin, `--dry-run`.
2.  **Streaming/NDJSON export (Complete)**: Stream features to newline-delimited GeoJSON to handle very large layers with low memory use.
3.  **Validation and report (Open)**: Emit a simple report alongside outputs (feature counts, skipped features, missing fields).
4.  **Parallel bulk export (Complete)**: `--workers` fetches multiple layers concurrently.
5.  **Output packaging (Open)**: Zip shapefiles automatically; optional `--gzip` for GeoJSON.
6.  **Field selection helpers (Open)**: Support patterns like `--fields *,-shape_area,-shape_len` and sampling via `--top N`.
7.  **GeoParquet/Parquet output (Complete)**: Writes GeoParquet for spatial layers and Parquet for non-spatial tables.
8.  **CRS controls (Open)**: Add `--out-sr` in CLI and API with clear errors when reprojection data is missing.
9.  **Domain decoding (Open)**: Replace coded domain values with aliases on export.
10. **Retry/backoff options (Open)**: Make retry, backoff and rate limit settings configurable.
11. **Caching (Open)**: Optional local cache using ETag/Last-Modified to skip unchanged layers.

---

## Phase 5 - Correctness, then leverage

### 5a. Correctness fixes (Complete, 0.4.0)

These undercut trust in every downstream feature, so they landed before any new
capability.

- **Silent truncation**: solved independently in 0.3.4 and 0.3.5, and better than
  the detection this section originally proposed. `_fetch_all_object_ids` pages
  past `exceededTransferLimit` with `resultOffset`, so the full ID list is
  retrieved rather than merely flagged as short, and `_fetch_features_adaptive`
  raises rather than continuing past a failed batch. A pre-flight count check on
  every extraction would now only add a round-trip, so `get_count()` and
  `ezesri count` remain as an explicit, user-invoked pre-flight instead. One
  residual gap: a server that truncates *without* setting `exceededTransferLimit`
  is still undetected, and `ezesri count` is the manual check for that.
- **`--where` passed as `None`**: the CLI always forwards `where=where`, which
  overrides the `'1=1'` default when the flag is omitted. `requests` drops `None`
  params, so the query goes out with no where clause at all and some servers
  reject it.
- **`--geometry` is broken**: the CLI parses GeoJSON into a dict and the extractor
  drops that dict straight into the query params. Esri wants Esri-JSON
  (`{"rings": [...]}`) as a string, and `geometryType` is hardcoded to polygon.
  Convert GeoJSON to Esri-JSON and infer the geometry type.
- **`out_sr` documented but missing**: `README.md` and `docs/usage.md` both list it
  in the `extract_layer` signature. Implement it and add `--out-sr`.
- **`--srs` is misleading**: it currently aliases `--spatial-rel`, which every GIS
  user will read as "spatial reference system." Remove the alias.
- **`spatial_rel` ignored for bbox**: the bbox branch hardcodes
  `esriSpatialRelIntersects`.
- **Bulk export can't be filtered**: `bulk_export` calls `extract_layer(layer_url)`
  with no filter pass-through.
- **Packaging metadata**: `setup.py` names the wrong author, and
  `python_requires='>=3.6'` is well below what geopandas supports. Add a
  `pyproject.toml`.

### 5b. Feature roadmap (prioritized)

1.  **Domain decoding and date coercion (Complete, 0.4.0)**: Coded-value domains
    are decoded to their labels and `esriFieldTypeDate` epoch-milliseconds become
    timestamps, both on by default. `--raw-codes` and `--raw-dates` opt out, and
    `--codebook` writes a sidecar JSON so the original codes stay recoverable.
    Per-subtype domain overrides are handled, since the same code can mean
    different things depending on the subtype.
2.  **Field selection and row caps**: `--fields`, `--exclude`, `--limit`.
    `outFields='*'` is hardcoded, and it is the dominant cost on wide layers — a
    county parcel layer carries 120 fields when you want six. `--limit` also
    supplies the recon step the tool currently lacks.
3.  **`ezesri count` and `--dry-run` (Partial, 0.4.0)**: `get_count()` and
    `ezesri count` report the real feature count before committing to a download.
    Still open: `--dry-run` on `fetch`, and an estimated output size.
4.  **Change detection for scheduled pipelines**: `ezesri check <url>` plus an
    `--if-changed` flag backed by a manifest (`editingInfo.lastEditDate`, feature
    count, content hash). Lets a cron job skip the download when nothing moved and
    report what changed when something did. The item with the most leverage for
    production data pipelines.
5.  **Directory search from the CLI and library**: `ezesri search "parcels" --place TX`
    against a slim index derived from the catalog. The directory is the
    differentiator versus pyesridump, but today you cannot get from "find the
    layer" to "download the layer" without a browser round trip. Ship a compact
    index; keep the full catalog remote.
6.  **Related tables and attachments**: Esri services expose `relationships`, and
    permit and inspection services routinely split parent features from child
    tables. Add `--with-related` to fetch and join them, plus attachment download
    for the PDFs and photos hanging off code-enforcement layers.
7.  **Shared writer, and a Lambda that imports the library**: Format-writing logic
    is duplicated between `cli.py` and `extract.py`, and `web/lambda/handler.py` is
    a third independent implementation that has already diverged — it has feature
    caps and lat/lon CSV columns the library lacks, and lacks the retries the
    library has. A shared `ezesri.write(df, path, format)` collapses the
    duplication and gives the web app domain decoding for free.
8.  **Resumable bulk export**: A failure 40 layers into a 60-layer service loses
    everything. The manifest from item 4 makes resume nearly free.

Suggested sequencing: 5a and features 1-3 ship together as a "trustworthy,
usable output" release; then 4 and 7; then 5.