# Testing ezesri

This project uses `pytest` to ensure code quality and prevent regressions. The tests cover core data extraction logic and the command-line interface.

## Running tests

### Prerequisites

Before running the tests, you need to install the required dependencies:

```bash
pip install pytest pytest-mock pytest-click geopandas
```

### How to run the test suite

To run the full test suite, execute the `pytest` command from the root of the project:

```bash
python3 -m pytest
```

## When to run tests

It is recommended to run the test suite at the following times:

-   Before committing any changes to the codebase.
-   After pulling new changes from the repository.
-   Before publishing a new version to PyPI.

The automated publishing script (`publish.sh`) will automatically run the tests to ensure that only stable code is released.
