# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-09-06

### Fixed
- **Silent truncation**: `extract_layer` now asks the server for a feature count before downloading, checks `exceededTransferLimit` on the object ID query, and warns when the download comes up short. Previously a server that capped `returnIdsOnly` produced an incomplete file with no indication anything was wrong.
- **`--where` sent as `None`**: omitting `--where` passed `None` through to the query, which `requests` drops, so the request went out with no where clause at all and some servers rejected it. The CLI and library now default to `1=1`.
- **`--geometry` did not work**: the CLI parsed GeoJSON into a dict and passed it straight into the query parameters. Esri expects Esri JSON (`rings`, `paths`) as a string, and `geometryType` was hardcoded to polygon. GeoJSON is now converted to Esri JSON, with the geometry type inferred and ring winding corrected. Points, multipoints, linestrings, multilinestrings, polygons, multipolygons, Features and FeatureCollections are all accepted.
- **`spatial_rel` ignored for bounding boxes**: the bbox branch hardcoded `esriSpatialRelIntersects`.
- **Bulk export could not be filtered**: `bulk_export` called `extract_layer` with no filter pass-through, so `bulk-fetch` was all-or-nothing.
- **NDJSON export produced invalid JSON**: `NaN` was written literally, which strict parsers reject, and timestamps could not be serialized at all. Both are now written as `null` and ISO-8601 respectively.

### Added
- **Coded-value domain decoding**, on by default. Esri layers routinely store a status as `3` with a domain that maps 3 to "Under construction", so every export previously needed a manual join back to the layer metadata before it was usable. Labels now replace codes, including per-subtype domain overrides where the same code means different things depending on the subtype. Codes with no matching label are left as-is and reported rather than blanked out. Use `--raw-codes` to opt out.
- **Date field parsing**, on by default. Esri returns dates as epoch milliseconds, so a filing date arrived as `1735689600000`. Date fields now become tz-aware UTC timestamps, and ISO string responses are handled too. Use `--raw-dates` to opt out.
- `get_codebook()`, an `ezesri codebook` command, a `--codebook` option on `fetch` and `--codebooks` on `bulk-fetch`, which record every coded value and date field so the original codes stay recoverable alongside a decoded export.
- `decode_dataframe()` and `build_codebook()` are exported for callers who fetch data themselves.
- `get_count()` and a matching `ezesri count` command, which report how many features match a query without downloading them. Both take the same filters as `fetch`.
- `out_sr` on `extract_layer` and `bulk_export`, plus `--out-sr` on `fetch` and `bulk-fetch`, for requesting output in a spatial reference other than WGS84. This was documented in the README and API docs but had never been implemented.
- `--where`, `--bbox`, `--geometry` and `--spatial-rel` on `bulk-fetch`.
- A `pyproject.toml` replacing `setup.py`.

### Changed
- **Breaking**: domain decoding and date parsing are on by default, so existing scripts will see labels where they previously saw codes, and timestamps where they previously saw epoch milliseconds. Anything downstream that parses those columns itself needs either updating or `--raw-codes` / `--raw-dates` (`decode_domains=False` / `parse_dates=False` in the library). This is the most disruptive change in the release.
- **Breaking**: removed the `--srs` alias for `--spatial-rel`. It read as "spatial reference system" to anyone familiar with GIS, which is what `--out-sr` now actually does. Use `--spatial-rel` for the spatial relationship.
- Corrected the package author metadata, which named the wrong person.
- Raised `requires-python` from `>=3.6` to `>=3.9`, matching what the dependencies actually support.
- Added `ezesri.__version__` and `ezesri --version`, both read from the installed package metadata so they cannot drift from `pyproject.toml`.

## [0.3.3] - 2026-03-07

### Added
- Added `--where` (and `-w` shorthand) option to the `fetch` command for SQL WHERE clause filtering.

## [0.3.2] - 2025-11-15

### Added
- Added support for exporting to GeoPackage (`.gpkg`) in CLI and bulk export.
- Added support for GeoParquet (`--format geoparquet`), Parquet (`--format parquet`) and streaming NDJSON (`--format ndjson`).
- Added parallel bulk export with `--workers` and global request rate limiting with `--rate`.

## [0.3.1] - 2025-11-15

### Changed
- Improved FileGDB driver detection and error guidance. When FileGDB write support is unavailable, the CLI now suggests a concrete `--format gpkg` alternative.
- Bulk export emits a helpful tip to rerun with `--format gpkg` when FileGDB write is not available.
- Clean up null/empty geometries before writes and provide clearer messages when mixed geometry types prevent FileGDB writes.

## [0.3.0] - 2025-07-12

### Added
- Added support for exporting to File Geodatabase (`.gdb`).
- Added CLI command aliases (`--output`, `--fmt`, `--srs`) for improved usability.
- Created a `pytest` test suite to ensure code quality and prevent regressions.
- Added a `TESTING.md` guide to explain how to run the test suite.

### Changed
- The `publish.sh` script now runs the test suite automatically before publishing to prevent releasing broken code.

## [0.2.2] - 2025-07-11

### Fixed
- Updated `README.md` to fix inadvertently removed sections. 

## [0.2.1] - 2025-07-11

### Fixed
- Updated `README.md` to remove an inaccurate reference to asynchronous downloads.
- Improved the release script to include a pre-flight checklist for documentation.

## [0.2.0] - 2025-07-11

### Added
- A progress bar (`tqdm`) now appears during data extraction to provide visual feedback on large downloads.
- The `fetch` command now detects service URLs and guides users to the `bulk-fetch` command.
- A user-friendly note is now displayed when shapefile field names are truncated, explaining what happened.
- A `publish.sh` script to automate the release process.

### Changed
- The version was bumped to `0.2.0` to reflect the new features and improvements.

### Fixed
- Implemented a robust retry and timeout mechanism to handle network errors and prevent the tool from hanging.
- Suppressed the raw `UserWarning` and `RuntimeWarning` from `geopandas` and `pyogrio` when saving shapefiles.

## [0.1.0] - 2026-07-10

- Initial release of `ezesri`.
- Core functionality for extracting layers and metadata.
- CLI for `fetch`, `metadata`, and `bulk-fetch`. 