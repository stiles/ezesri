from importlib.metadata import PackageNotFoundError, version as _version

from .extract import (
    get_metadata,
    get_count,
    get_codebook,
    extract_layer,
    bulk_export,
    summarize_metadata,
    EsriLayerError,
    DEFAULT_MAX_BATCH_SIZE,
)
from .utils import decode_dataframe, build_codebook

try:
    # Single source of truth is pyproject.toml, read at runtime so it cannot drift
    __version__ = _version("ezesri")
except PackageNotFoundError:  # running from a source tree with no install
    __version__ = "unknown"

__all__ = [
    "__version__",
    "get_metadata",
    "get_count",
    "get_codebook",
    "extract_layer",
    "bulk_export",
    "summarize_metadata",
    "decode_dataframe",
    "build_codebook",
    "EsriLayerError",
    "DEFAULT_MAX_BATCH_SIZE",
]
