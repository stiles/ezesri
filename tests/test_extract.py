import json

import pytest
from ezesri import get_metadata, get_count, extract_layer
import requests

# URL for a known public Esri feature layer
URL = "https://services5.arcgis.com/VAb1qw880ksyBtIL/ArcGIS/rest/services/City_Boundary_of_Los_Angeles_(new)/FeatureServer/0"

def test_get_metadata_success():
    """Tests successfully fetching metadata from a live service."""
    metadata = get_metadata(URL)
    assert isinstance(metadata, dict)
    assert "name" in metadata
    assert metadata["name"] == "City_Boundary"

def test_get_metadata_request_error(mocker):
    """Tests the handling of a request exception."""
    mocker.patch('ezesri.extract.make_request', side_effect=requests.exceptions.RequestException)
    metadata = get_metadata(URL)
    assert metadata == {}

def test_get_metadata_invalid_url():
    """Tests that a non-string URL raises a TypeError."""
    with pytest.raises(TypeError):
        get_metadata(12345)

def test_extract_layer_success(mocker):
    """Tests that a layer is extracted into a GeoDataFrame."""
    # Mock get_metadata to return a valid response
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 1000}
    )
    # Mock the request to return a sample GeoJSON
    mocker.patch('ezesri.extract.make_request').return_value.json.return_value = {
        'objectIds': [1, 2],
        'features': [
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {'id': 1}},
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [1, 1]}, 'properties': {'id': 2}}
        ]
    }
    
    gdf = extract_layer(URL)
    assert not gdf.empty
    assert 'geometry' in gdf.columns
    assert len(gdf) == 2

def test_extract_layer_empty(mocker):
    """Tests extracting an empty layer."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 1000}
    )
    mocker.patch('ezesri.extract.make_request').return_value.json.return_value = {'objectIds': []}
    
    gdf = extract_layer(URL)
    assert gdf.empty

def test_extract_layer_with_bbox(mocker):
    """Tests filtering with a bounding box."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 1000}
    )
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {
        'objectIds': [1],
        'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {'id': 1}}]
    }

    bbox = (-1, -1, 1, 1)
    gdf = extract_layer(URL, bbox=bbox)

    assert not gdf.empty
    assert len(gdf) == 1
    # Check that the bbox was passed to the query
    assert 'geometry' in mock_make_request.call_args_list[0].kwargs['params']
    assert mock_make_request.call_args_list[0].kwargs['params']['geometry'] == '-1,-1,1,1'


def test_bbox_uses_requested_spatial_rel(mocker):
    """The bbox branch honours spatial_rel instead of hardcoding intersects."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 1000}
    )
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {'objectIds': []}

    extract_layer(URL, bbox=(-1, -1, 1, 1), spatial_rel='esriSpatialRelWithin')

    params = mock_make_request.call_args_list[0].kwargs['params']
    assert params['spatialRel'] == 'esriSpatialRelWithin'


def test_geometry_filter_is_converted_to_esri_json(mocker):
    """A GeoJSON geometry is converted to an Esri JSON string, not passed raw."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 1000}
    )
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {'objectIds': []}

    geometry = {"type": "Polygon", "coordinates": [[[0, 0], [0, 1], [1, 1], [0, 0]]]}
    extract_layer(URL, geometry=geometry)

    params = mock_make_request.call_args_list[0].kwargs['params']
    assert isinstance(params['geometry'], str)
    assert 'rings' in json.loads(params['geometry'])
    assert params['geometryType'] == 'esriGeometryPolygon'


def test_geometry_type_is_inferred(mocker):
    """geometryType follows the input rather than defaulting to polygon."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPoint', 'maxRecordCount': 1000}
    )
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {'objectIds': []}

    extract_layer(URL, geometry={"type": "LineString", "coordinates": [[0, 0], [1, 1]]})

    params = mock_make_request.call_args_list[0].kwargs['params']
    assert params['geometryType'] == 'esriGeometryPolyline'


def test_none_where_becomes_1_equals_1(mocker):
    """A None where clause would be dropped by requests, so it is normalised."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPolygon', 'maxRecordCount': 1000}
    )
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {'objectIds': []}

    extract_layer(URL, where=None)

    assert mock_make_request.call_args_list[0].kwargs['params']['where'] == '1=1'


def test_out_sr_is_applied(mocker):
    """out_sr sets both the query outSR and the resulting CRS."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPoint', 'maxRecordCount': 1000}
    )
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {
        'objectIds': [1],
        'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {'id': 1}}]
    }

    gdf = extract_layer(URL, out_sr=3857)

    assert gdf.crs.to_epsg() == 3857
    # The batch fetch posts its params as form data
    batch_call = mock_make_request.call_args_list[-1]
    assert batch_call.kwargs['data']['outSR'] == '3857'


def test_get_count_returns_server_count(mocker):
    """get_count reads the server's count without downloading features."""
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {'count': 4321}

    assert get_count(URL) == 4321
    assert mock_make_request.call_args.kwargs['params']['returnCountOnly'] == 'true'


def test_get_count_handles_error(mocker):
    """A server error yields None rather than raising."""
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {'error': {'message': 'nope'}}

    assert get_count(URL) is None


def test_warns_when_object_ids_are_truncated(mocker, capsys):
    """A short objectIds list against a larger count is reported, not swallowed."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPoint', 'maxRecordCount': 1000}
    )
    mocker.patch('ezesri.extract.get_count', return_value=5000)
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {
        'objectIds': [1],
        'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {'id': 1}}]
    }

    extract_layer(URL)

    output = capsys.readouterr().out
    assert 'incomplete' in output


def test_warns_on_exceeded_transfer_limit(mocker, capsys):
    """exceededTransferLimit on the ID query is surfaced to the user."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'geometryType': 'esriGeometryPoint', 'maxRecordCount': 1000}
    )
    mocker.patch('ezesri.extract.get_count', return_value=None)
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.return_value = {
        'objectIds': [1],
        'exceededTransferLimit': True,
        'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {'id': 1}}]
    }

    extract_layer(URL)

    assert 'exceededTransferLimit' in capsys.readouterr().out
