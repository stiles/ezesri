import time
import requests
from typing import Tuple, List, Optional
import json
import threading

try:
    import fiona
except Exception:
    fiona = None

try:
    from shapely.geometry import mapping as shapely_mapping
except Exception:
    shapely_mapping = None

def make_request(url: str, method: str = 'get', **kwargs):
    """
    Makes an HTTP request with retries and a delay.

    Args:
        url: The URL to make the request to.
        method: The HTTP method to use ('get' or 'post').
        **kwargs: Additional keyword arguments to pass to the requests method.

    Returns:
        The response object.
    """
    if not isinstance(url, str):
        raise TypeError("URL must be a string.")
        
    retries = 3
    delay = 1  # in seconds
    
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 30  # Default timeout of 30 seconds

    last_exception = None

    for i in range(retries):
        try:
            # Optional global rate limiter
            if _rate_limiter is not None:
                _rate_limiter.acquire()
            if method.lower() == 'get':
                response = requests.get(url, **kwargs)
            elif method.lower() == 'post':
                response = requests.post(url, **kwargs)
            else:
                raise ValueError("Unsupported HTTP method.")
            
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            last_exception = e
            print(f"Request to {url} failed: {e}. Retrying in {delay} seconds... ({i + 1}/{retries})")
            time.sleep(delay)
    
    # If all retries fail, raise the last exception
    raise requests.exceptions.RequestException(f"All retries failed for {url}: {last_exception}")

def truncate_field_names(gdf):
    """Truncates field names in a GeoDataFrame to 10 characters for shapefiles."""
    original_columns = list(gdf.columns)
    new_columns = []
    truncated_cols = {}
    for col in original_columns:
        # The geometry column should not be renamed
        if col.lower() == 'geometry':
            new_columns.append(col)
            continue
            
        # Truncate other columns
        new_col = col[:10]
        if new_col in new_columns:
            # Handle duplicates by adding a suffix
            suffix = 1
            while f"{new_col[:8]}_{suffix}" in new_columns:
                suffix += 1
            new_col = f"{new_col[:8]}_{suffix}"
        
        if new_col != col:
            truncated_cols[col] = new_col
        new_columns.append(new_col)
        
    gdf.columns = new_columns
    return gdf, truncated_cols 

def has_filegdb_write_support() -> Tuple[bool, str]:
    """
    Detects whether the GDAL/FileGDB driver is available for writing.

    Returns:
        (supported, message): A tuple where 'supported' indicates if FileGDB write
        is available, and 'message' contains guidance when not supported.
    """
    if fiona is None:
        return False, "Fiona is not available. Install geopandas with fiona/GDAL support."

    drivers = getattr(fiona, "supported_drivers", {})
    # fiona.supported_drivers is a dict like {'GeoJSON': 'rw', 'OpenFileGDB': 'r', 'FileGDB': 'raw'}
    # Write support requires a mode containing 'w'
    filegdb_mode = drivers.get("FileGDB")
    if filegdb_mode and "w" in str(filegdb_mode):
        return True, ""

    open_filegdb_mode = drivers.get("OpenFileGDB")
    if open_filegdb_mode:
        # OpenFileGDB is read-only; provide a targeted message
        return False, (
            "FileGDB write driver is not available. Found OpenFileGDB (read-only) but not FileGDB (write). "
            "You cannot write .gdb with this GDAL build. Try a different format (GeoJSON, Shapefile, GeoPackage) "
            "or install GDAL with FileGDB write support."
        )

    return False, (
        "FileGDB write driver is not available in your GDAL/Fiona installation. "
        "Try a different output format (GeoJSON, Shapefile, GeoPackage) or install GDAL with FileGDB support."
    )

class _SimpleRateLimiter:
    """
    A simple thread-safe rate limiter that spaces requests at ~1/rate seconds.
    Not bursty; each acquire waits until the next allowed time.
    """
    def __init__(self, max_per_second: float):
        if max_per_second <= 0:
            raise ValueError("max_per_second must be > 0")
        self.interval = 1.0 / float(max_per_second)
        self._lock = threading.Lock()
        self._next_allowed = time.monotonic()

    def acquire(self):
        with self._lock:
            now = time.monotonic()
            if now < self._next_allowed:
                sleep_for = self._next_allowed - now
                time.sleep(sleep_for)
                now = time.monotonic()
            self._next_allowed = now + self.interval

_rate_limiter: Optional[_SimpleRateLimiter] = None

def set_rate_limit(max_per_second: Optional[float]):
    """
    Set a global, process-wide rate limit for outbound HTTP requests.
    Pass None or 0 to disable.
    """
    global _rate_limiter
    if not max_per_second:
        _rate_limiter = None
    else:
        _rate_limiter = _SimpleRateLimiter(max_per_second)

def drop_empty_geometries(gdf):
    """
    Drops rows with null or empty geometries. Returns (clean_gdf, dropped_count).
    """
    if "geometry" not in gdf.columns:
        return gdf, 0
    # Handle None geometries
    is_null = gdf.geometry.isna()
    # Handle empty shapes (only evaluate on non-null to avoid attribute errors)
    non_null = gdf.loc[~is_null]
    is_empty = non_null.geometry.is_empty if len(non_null) else non_null.geometry
    to_drop_index = list(non_null.loc[is_empty].index) if len(non_null) else []
    total_drop = int(is_null.sum()) + len(to_drop_index)
    if total_drop == 0:
        return gdf, 0
    keep_mask = ~is_null
    if len(to_drop_index):
        keep_mask.loc[to_drop_index] = False
    return gdf.loc[keep_mask], total_drop

def unique_geometry_types(gdf) -> List[str]:
    """
    Returns the list of unique geometry types among non-empty geometries.
    """
    if "geometry" not in gdf.columns:
        return []
    # Only consider non-null and non-empty geometries
    valid = gdf.loc[gdf.geometry.notna()]
    if len(valid) == 0:
        return []
    valid = valid.loc[~valid.geometry.is_empty]
    if len(valid) == 0:
        return []
    return list(valid.geometry.geom_type.unique())

def write_ndjson(df, output_path: str):
    """
    Writes a DataFrame/GeoDataFrame to newline-delimited JSON (GeoJSON Features when geometry exists).
    If output_path is '-' writes to stdout.
    """
    is_spatial = hasattr(df, "geometry")
    use_stdout = (not output_path) or (output_path == "-")

    if is_spatial and shapely_mapping is None:
        raise RuntimeError("shapely is required for NDJSON export of spatial layers.")

    def iter_features():
        if is_spatial:
            for _, row in df.iterrows():
                props = row.drop(labels=["geometry"], errors="ignore").to_dict()
                geom = None
                if "geometry" in df.columns and row.geometry is not None and not row.geometry.is_empty:
                    geom = shapely_mapping(row.geometry)
                yield {"type": "Feature", "properties": props, "geometry": geom}
        else:
            for _, row in df.iterrows():
                yield row.to_dict()

    if use_stdout:
        for obj in iter_features():
            print(json.dumps(obj, ensure_ascii=False))
        return

    with open(output_path, "w", encoding="utf-8") as f:
        for obj in iter_features():
            f.write(json.dumps(obj, ensure_ascii=False))
            f.write("\n")