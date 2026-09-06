import json

import pytest

from ezesri.utils import geojson_to_esri_geometry


def test_polygon_converts_to_rings():
    """A GeoJSON Polygon becomes Esri rings."""
    geojson = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
    }
    esri, geom_type = geojson_to_esri_geometry(geojson)

    assert geom_type == "esriGeometryPolygon"
    parsed = json.loads(esri)
    assert "rings" in parsed
    assert parsed["spatialReference"]["wkid"] == 4326


def test_polygon_exterior_ring_is_clockwise():
    """Esri winds exterior rings clockwise, the opposite of the GeoJSON spec."""
    # This ring is counter-clockwise, per RFC 7946
    geojson = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
    }
    esri, _ = geojson_to_esri_geometry(geojson)
    ring = json.loads(esri)["rings"][0]

    # Shoelace: a positive sum means clockwise
    area = sum(
        (ring[i + 1][0] - ring[i][0]) * (ring[i + 1][1] + ring[i][1])
        for i in range(len(ring) - 1)
    )
    assert area > 0


def test_multipolygon_flattens_rings():
    """Esri has no MultiPolygon, so every part's rings go in one list."""
    geojson = {
        "type": "MultiPolygon",
        "coordinates": [
            [[[0, 0], [0, 1], [1, 1], [0, 0]]],
            [[[5, 5], [5, 6], [6, 6], [5, 5]]],
        ],
    }
    esri, geom_type = geojson_to_esri_geometry(geojson)

    assert geom_type == "esriGeometryPolygon"
    assert len(json.loads(esri)["rings"]) == 2


def test_point_converts_to_xy():
    geojson = {"type": "Point", "coordinates": [-118.2, 34.0]}
    esri, geom_type = geojson_to_esri_geometry(geojson)
    parsed = json.loads(esri)

    assert geom_type == "esriGeometryPoint"
    assert parsed["x"] == -118.2
    assert parsed["y"] == 34.0


def test_linestring_converts_to_paths():
    geojson = {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}
    esri, geom_type = geojson_to_esri_geometry(geojson)

    assert geom_type == "esriGeometryPolyline"
    assert json.loads(esri)["paths"] == [[[0, 0], [1, 1]]]


def test_feature_is_unwrapped():
    """A Feature wrapper is unwrapped to its geometry."""
    geojson = {
        "type": "Feature",
        "properties": {},
        "geometry": {"type": "Point", "coordinates": [1, 2]},
    }
    _, geom_type = geojson_to_esri_geometry(geojson)
    assert geom_type == "esriGeometryPoint"


def test_feature_collection_uses_first_feature():
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [1, 2]}}
        ],
    }
    _, geom_type = geojson_to_esri_geometry(geojson)
    assert geom_type == "esriGeometryPoint"


def test_accepts_json_string():
    """A raw JSON string is parsed, not passed through."""
    _, geom_type = geojson_to_esri_geometry('{"type": "Point", "coordinates": [1, 2]}')
    assert geom_type == "esriGeometryPoint"


def test_output_is_a_string():
    """Esri expects the geometry parameter as a string, not a dict."""
    esri, _ = geojson_to_esri_geometry({"type": "Point", "coordinates": [1, 2]})
    assert isinstance(esri, str)


def test_custom_wkid():
    esri, _ = geojson_to_esri_geometry({"type": "Point", "coordinates": [1, 2]}, wkid=3857)
    assert json.loads(esri)["spatialReference"]["wkid"] == 3857


def test_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported GeoJSON geometry type"):
        geojson_to_esri_geometry({"type": "GeometryCollection", "geometries": []})


def test_invalid_json_raises():
    with pytest.raises(ValueError, match="not valid JSON"):
        geojson_to_esri_geometry("not json at all")


def test_empty_feature_collection_raises():
    with pytest.raises(ValueError, match="no features"):
        geojson_to_esri_geometry({"type": "FeatureCollection", "features": []})
