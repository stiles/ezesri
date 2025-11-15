import time
import requests
from typing import Tuple, List

try:
    import fiona
except Exception:
    fiona = None

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