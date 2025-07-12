# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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