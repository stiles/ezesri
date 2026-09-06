import time
import requests
from typing import Any, Dict, Tuple, List, Optional
import json
import threading
import datetime as _dt

import pandas as pd

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

# Esri field types that carry a date or timestamp
ESRI_DATE_FIELD_TYPES = {
    "esriFieldTypeDate",
    "esriFieldTypeDateOnly",
    "esriFieldTypeTimestampOffset",
}


def _subtype_field_name(metadata: dict) -> Optional[str]:
    """Returns the layer's subtype field, which Esri spells inconsistently."""
    return metadata.get("subtypeField") or metadata.get("subtypeFieldName") or None


def _subtype_code(subtype: dict):
    """Returns a subtype's code, which Esri spells inconsistently."""
    code = subtype.get("code")
    if code is None:
        code = subtype.get("subtypeCode")
    return code


def coded_value_map(domain: Optional[dict]) -> Optional[Dict[Any, str]]:
    """
    Builds a {code: label} lookup from an Esri coded-value domain.

    Codes are registered under both their raw value and their string form, because
    a field's values and its domain codes do not always share a type.

    Args:
        domain: An Esri domain dict, or None.

    Returns:
        The lookup, or None if the domain is absent or not a coded-value domain.
        Range domains need no decoding and yield None.
    """
    if not domain or domain.get("type") != "codedValue":
        return None

    mapping: Dict[Any, str] = {}
    for coded_value in domain.get("codedValues") or []:
        code = coded_value.get("code")
        label = coded_value.get("name")
        if code is None or label is None:
            continue
        mapping[code] = label
        mapping.setdefault(str(code), label)

    return mapping or None


def build_codebook(metadata: dict) -> dict:
    """
    Builds a record of every decoding that applies to a layer.

    Written alongside an export so the original codes stay recoverable.

    Args:
        metadata: The layer metadata dict.

    Returns:
        A JSON-serializable codebook.
    """
    fields = {}
    for field in metadata.get("fields") or []:
        name = field.get("name")
        if not name:
            continue

        entry = {
            "alias": field.get("alias"),
            "type": field.get("type"),
        }

        mapping = coded_value_map(field.get("domain"))
        if mapping:
            # Only the raw codes, not the duplicated string keys
            codes = {
                cv.get("code"): cv.get("name")
                for cv in field["domain"].get("codedValues") or []
            }
            entry["domain"] = {
                "name": field["domain"].get("name"),
                "codedValues": codes,
            }

        if field.get("type") in ESRI_DATE_FIELD_TYPES:
            entry["decodedAs"] = "ISO-8601 UTC timestamp"

        fields[name] = entry

    codebook = {
        "layer": metadata.get("name"),
        "fields": fields,
    }

    subtype_field = _subtype_field_name(metadata)
    if subtype_field and metadata.get("subtypes"):
        subtypes = {}
        for subtype in metadata["subtypes"]:
            code = _subtype_code(subtype)
            if code is None:
                continue
            domains = {}
            for field_name, domain in (subtype.get("domains") or {}).items():
                mapping = coded_value_map(domain)
                if mapping:
                    domains[field_name] = {
                        cv.get("code"): cv.get("name")
                        for cv in domain.get("codedValues") or []
                    }
            subtypes[code] = {"name": subtype.get("name"), "domains": domains}

        codebook["subtypeField"] = subtype_field
        codebook["subtypes"] = subtypes

    return codebook


def _decode_series(series, code_map: Dict[Any, str]):
    """
    Maps coded values to their labels, leaving anything unrecognised untouched.

    Returns (decoded_series, set_of_unmapped_codes).
    """
    unmapped = set()

    def convert(value):
        try:
            if value is None or pd.isna(value):
                return value
        except (TypeError, ValueError):
            # Non-scalar values cannot be null-checked; fall through
            pass

        try:
            if value in code_map:
                return code_map[value]
            key = str(value)
            if key in code_map:
                return code_map[key]
            unmapped.add(value)
        except TypeError:
            # Unhashable value, nothing to look up
            return value

        return value

    return series.map(convert), unmapped


def _to_datetime(series):
    """
    Converts an Esri date column to tz-aware UTC timestamps.

    Esri returns dates as epoch milliseconds in its JSON responses, though some
    servers hand back ISO strings instead, so both are handled.
    """
    numeric = pd.to_numeric(series, errors="coerce")
    # If essentially everything parsed as a number, treat it as epoch milliseconds
    non_null = series.notna().sum()
    if non_null and numeric.notna().sum() >= non_null:
        return pd.to_datetime(numeric, unit="ms", utc=True, errors="coerce")

    try:
        return pd.to_datetime(series, utc=True, errors="coerce", format="mixed")
    except (TypeError, ValueError):
        return pd.to_datetime(series, utc=True, errors="coerce")


def decode_dataframe(
    df,
    metadata: dict,
    decode_domains: bool = True,
    parse_dates: bool = True,
) -> Tuple[Any, dict]:
    """
    Replaces Esri coded values with their labels and turns date fields into
    timestamps.

    Esri layers routinely store a status as `3` with a domain that maps 3 to
    "Under construction", and dates as epoch milliseconds. Both are unusable in an
    export without the layer metadata alongside, so they are decoded here.

    Args:
        df: The DataFrame or GeoDataFrame to decode, modified on a copy.
        metadata: The layer metadata the data was extracted from.
        decode_domains: Whether to replace coded values with their labels.
        parse_dates: Whether to convert date fields to timestamps.

    Returns:
        (decoded_df, report), where report records which fields changed and which
        codes had no matching label.
    """
    report = {"decoded_fields": [], "date_fields": [], "unmapped_codes": {}}

    if df is None or len(df) == 0 or not metadata:
        return df, report

    fields = metadata.get("fields") or []
    if not fields:
        return df, report

    df = df.copy()

    # Per-subtype domain overrides, keyed by field then subtype code
    subtype_field = _subtype_field_name(metadata)
    subtype_overrides: Dict[str, Dict[Any, Dict[Any, str]]] = {}
    subtype_names: Dict[Any, str] = {}

    if metadata.get("subtypes"):
        for subtype in metadata["subtypes"]:
            code = _subtype_code(subtype)
            if code is None:
                continue
            if subtype.get("name"):
                subtype_names[code] = subtype["name"]
            for field_name, domain in (subtype.get("domains") or {}).items():
                mapping = coded_value_map(domain)
                if mapping:
                    subtype_overrides.setdefault(field_name, {})[code] = mapping

    # Capture subtype codes before the column itself is decoded
    subtype_codes = None
    if decode_domains and subtype_field and subtype_field in df.columns:
        subtype_codes = df[subtype_field].copy()

    for field in fields:
        name = field.get("name")
        if not name or name not in df.columns:
            continue

        if parse_dates and field.get("type") in ESRI_DATE_FIELD_TYPES:
            df[name] = _to_datetime(df[name])
            report["date_fields"].append(name)
            continue

        if not decode_domains:
            continue

        base_map = coded_value_map(field.get("domain"))
        overrides = subtype_overrides.get(name)

        if overrides and subtype_codes is not None:
            # Decode each subtype's rows with that subtype's own domain, falling
            # back to the field-level domain where a subtype has no override.
            # Object dtype first: labels are strings and the source column is
            # usually numeric, which pandas refuses to upcast in place.
            decoded = df[name].astype(object).copy()
            unmapped = set()
            changed = False

            for code, mapping in overrides.items():
                mask = subtype_codes == code
                if not mask.any():
                    continue
                decoded_part, part_unmapped = _decode_series(df.loc[mask, name], mapping)
                decoded.loc[mask] = decoded_part
                unmapped |= part_unmapped
                changed = True

            if base_map:
                handled = pd.Series(False, index=df.index)
                for code in overrides:
                    handled |= (subtype_codes == code)
                remaining = ~handled
                if remaining.any():
                    decoded_part, part_unmapped = _decode_series(
                        df.loc[remaining, name], base_map
                    )
                    decoded.loc[remaining] = decoded_part
                    unmapped |= part_unmapped
                    changed = True

            if changed:
                # Restore a narrower dtype if nothing was actually relabelled
                df[name] = decoded.infer_objects()
                report["decoded_fields"].append(name)
                if unmapped:
                    report["unmapped_codes"][name] = sorted(unmapped, key=str)
            continue

        if base_map:
            df[name], unmapped = _decode_series(df[name], base_map)
            report["decoded_fields"].append(name)
            if unmapped:
                report["unmapped_codes"][name] = sorted(unmapped, key=str)

    # Finally, decode the subtype field itself
    if decode_domains and subtype_codes is not None and subtype_names:
        df[subtype_field], unmapped = _decode_series(subtype_codes, subtype_names)
        report["decoded_fields"].append(subtype_field)
        if unmapped:
            report["unmapped_codes"][subtype_field] = sorted(unmapped, key=str)

    return df, report


def _ring_is_clockwise(ring: list) -> bool:
    """Returns True if a linear ring is wound clockwise (shoelace formula)."""
    area = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[i + 1][0], ring[i + 1][1]
        area += (x2 - x1) * (y2 + y1)
    return area > 0


def _orient_ring(ring: list, clockwise: bool) -> list:
    """Returns the ring wound in the requested direction."""
    return ring if _ring_is_clockwise(ring) == clockwise else list(reversed(ring))


def _polygon_rings(coordinates: list) -> list:
    """
    Converts GeoJSON polygon coordinates to Esri rings.

    Esri winds exterior rings clockwise and holes counter-clockwise, which is the
    opposite of the GeoJSON spec, and plenty of real-world GeoJSON ignores both.
    Re-orient every ring rather than trusting the input.
    """
    rings = []
    for i, ring in enumerate(coordinates):
        rings.append(_orient_ring(list(ring), clockwise=(i == 0)))
    return rings


def geojson_to_esri_geometry(geojson: Any, wkid: int = 4326) -> Tuple[str, str]:
    """
    Converts a GeoJSON geometry to an Esri JSON geometry string.

    Accepts a geometry, a Feature, a FeatureCollection (first feature is used) or a
    JSON string of any of those.

    Args:
        geojson: The GeoJSON input.
        wkid: The spatial reference WKID to attach to the geometry.

    Returns:
        (esri_json_string, esri_geometry_type) suitable for the 'geometry' and
        'geometryType' query parameters.

    Raises:
        ValueError: If the input is not valid GeoJSON or the geometry type is
            unsupported.
    """
    if isinstance(geojson, (str, bytes)):
        try:
            geojson = json.loads(geojson)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Geometry is not valid JSON: {e}")

    if not isinstance(geojson, dict):
        raise ValueError("Geometry must be a GeoJSON object or a JSON string.")

    # Unwrap Feature / FeatureCollection down to a bare geometry
    gj_type = geojson.get("type")
    if gj_type == "FeatureCollection":
        features = geojson.get("features") or []
        if not features:
            raise ValueError("FeatureCollection contains no features.")
        return geojson_to_esri_geometry(features[0], wkid=wkid)
    if gj_type == "Feature":
        geometry = geojson.get("geometry")
        if not geometry:
            raise ValueError("Feature has no geometry.")
        return geojson_to_esri_geometry(geometry, wkid=wkid)

    coords = geojson.get("coordinates")
    sr = {"spatialReference": {"wkid": wkid}}

    if gj_type == "Polygon":
        if not coords:
            raise ValueError("Polygon has no coordinates.")
        esri = {"rings": _polygon_rings(coords), **sr}
        return json.dumps(esri), "esriGeometryPolygon"

    if gj_type == "MultiPolygon":
        if not coords:
            raise ValueError("MultiPolygon has no coordinates.")
        # Esri has no MultiPolygon: every ring from every part goes in one list
        rings = []
        for polygon in coords:
            rings.extend(_polygon_rings(polygon))
        esri = {"rings": rings, **sr}
        return json.dumps(esri), "esriGeometryPolygon"

    if gj_type == "LineString":
        if not coords:
            raise ValueError("LineString has no coordinates.")
        esri = {"paths": [coords], **sr}
        return json.dumps(esri), "esriGeometryPolyline"

    if gj_type == "MultiLineString":
        if not coords:
            raise ValueError("MultiLineString has no coordinates.")
        esri = {"paths": coords, **sr}
        return json.dumps(esri), "esriGeometryPolyline"

    if gj_type == "Point":
        if not coords or len(coords) < 2:
            raise ValueError("Point has no coordinates.")
        esri = {"x": coords[0], "y": coords[1], **sr}
        return json.dumps(esri), "esriGeometryPoint"

    if gj_type == "MultiPoint":
        if not coords:
            raise ValueError("MultiPoint has no coordinates.")
        esri = {"points": coords, **sr}
        return json.dumps(esri), "esriGeometryMultipoint"

    raise ValueError(
        f"Unsupported GeoJSON geometry type: {gj_type!r}. Supported types are Point, "
        "MultiPoint, LineString, MultiLineString, Polygon and MultiPolygon."
    )


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

def _json_default(value):
    """
    Serializes values the JSON encoder does not handle natively.

    Timestamps become ISO-8601 strings; missing values and numpy scalars are
    unwrapped to their Python equivalents.
    """
    if isinstance(value, (_dt.datetime, _dt.date, _dt.time)):
        return value.isoformat()
    if isinstance(value, _dt.timedelta):
        return value.total_seconds()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    # pandas NaT and numpy scalar types
    try:
        if value is pd.NaT or pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    item = getattr(value, "item", None)
    if callable(item):
        try:
            return item()
        except (AttributeError, ValueError):
            pass

    return str(value)


def _json_safe(obj):
    """Recursively replaces NaN and NaT with None so the output is valid JSON."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, float) and obj != obj:  # NaN
        return None
    try:
        if obj is not None and not isinstance(obj, (str, bytes)) and pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass
    return obj


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
                yield {"type": "Feature", "properties": _json_safe(props), "geometry": geom}
        else:
            for _, row in df.iterrows():
                yield _json_safe(row.to_dict())

    if use_stdout:
        for obj in iter_features():
            print(json.dumps(obj, ensure_ascii=False, default=_json_default))
        return

    with open(output_path, "w", encoding="utf-8") as f:
        for obj in iter_features():
            f.write(json.dumps(obj, ensure_ascii=False, default=_json_default))
            f.write("\n")