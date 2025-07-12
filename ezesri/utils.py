import time
import requests

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