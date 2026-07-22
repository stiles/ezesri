import pytest
from ezesri import get_metadata, extract_layer, EsriLayerError, DEFAULT_MAX_BATCH_SIZE
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


def test_extract_layer_pages_object_ids_past_transfer_limit(mocker):
    """Pages returnIdsOnly when the server sets exceededTransferLimit."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={
            'geometryType': 'esriGeometryPolygon',
            'maxRecordCount': 2,
            'objectIdField': 'OBJECTID',
        },
    )

    oid_page_1 = {
        'objectIds': [1, 2, 3],
        'exceededTransferLimit': True,
    }
    oid_page_2 = {
        'objectIds': [4, 5],
        'exceededTransferLimit': False,
    }
    feature_responses = [
        {'features': [
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {'id': 1}},
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [1, 1]}, 'properties': {'id': 2}},
        ]},
        {'features': [
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [2, 2]}, 'properties': {'id': 3}},
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [3, 3]}, 'properties': {'id': 4}},
        ]},
        {'features': [
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [4, 4]}, 'properties': {'id': 5}},
        ]},
    ]

    responses = [oid_page_1, oid_page_2, *feature_responses]
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.side_effect = responses

    gdf = extract_layer(URL)

    assert len(gdf) == 5
    first_oid_params = mock_make_request.call_args_list[0].kwargs['params']
    second_oid_params = mock_make_request.call_args_list[1].kwargs['params']
    assert first_oid_params['orderByFields'] == 'OBJECTID ASC'
    assert 'resultOffset' not in first_oid_params
    assert second_oid_params['resultOffset'] == 3


def test_extract_layer_raises_on_metadata_error(mocker):
    """Esri error JSON in metadata must raise, not return an empty DataFrame."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={'error': {'code': 500, 'message': 'Service not started'}},
    )

    with pytest.raises(EsriLayerError, match='Service not started') as exc_info:
        extract_layer(URL)

    assert exc_info.value.code == 500


def test_extract_layer_caps_batch_size_to_default(mocker):
    """Advertised maxRecordCount above the default cap is not used as batch size."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={
            'geometryType': 'esriGeometryPolygon',
            'maxRecordCount': 50000,
            'objectIdField': 'OBJECTID',
        },
    )
    object_ids = list(range(1, DEFAULT_MAX_BATCH_SIZE + 3))
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.side_effect = [
        {'objectIds': object_ids},
        {'features': [
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {'id': i}}
            for i in object_ids[:DEFAULT_MAX_BATCH_SIZE]
        ]},
        {'features': [
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {'id': i}}
            for i in object_ids[DEFAULT_MAX_BATCH_SIZE:]
        ]},
    ]

    gdf = extract_layer(URL)

    assert len(gdf) == len(object_ids)
    feature_calls = [
        call for call in mock_make_request.call_args_list
        if call.kwargs.get('method') == 'post'
    ]
    first_batch_ids = feature_calls[0].kwargs['data']['objectIds'].split(',')
    assert len(first_batch_ids) == DEFAULT_MAX_BATCH_SIZE


def test_extract_layer_shrinks_batch_on_failure(mocker):
    """Failed oversized batches are retried at half size."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={
            'geometryType': 'esriGeometryPolygon',
            'maxRecordCount': 4,
            'objectIdField': 'OBJECTID',
        },
    )
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.side_effect = [
        {'objectIds': [1, 2, 3, 4]},
        {'error': {'code': 500, 'message': 'Unable to complete operation'}},
        {'features': [
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [0, 0]}, 'properties': {'id': 1}},
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [1, 1]}, 'properties': {'id': 2}},
        ]},
        {'features': [
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [2, 2]}, 'properties': {'id': 3}},
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [3, 3]}, 'properties': {'id': 4}},
        ]},
    ]

    gdf = extract_layer(URL, batch_size=4)

    assert len(gdf) == 4
    feature_calls = [
        call for call in mock_make_request.call_args_list
        if call.kwargs.get('method') == 'post'
    ]
    assert len(feature_calls) == 3
    assert len(feature_calls[0].kwargs['data']['objectIds'].split(',')) == 4
    assert len(feature_calls[1].kwargs['data']['objectIds'].split(',')) == 2


def test_extract_layer_raises_when_single_feature_batch_fails(mocker):
    """If even a batch of one fails, raise instead of returning a partial frame."""
    mocker.patch(
        'ezesri.extract.get_metadata',
        return_value={
            'geometryType': 'esriGeometryPolygon',
            'maxRecordCount': 2,
            'objectIdField': 'OBJECTID',
        },
    )
    mock_make_request = mocker.patch('ezesri.extract.make_request')
    mock_make_request.return_value.json.side_effect = [
        {'objectIds': [1, 2]},
        {'error': {'code': 500, 'message': 'boom'}},
        {'error': {'code': 500, 'message': 'boom'}},
        {'error': {'code': 500, 'message': 'boom'}},
    ]

    with pytest.raises(EsriLayerError, match='batch size 1'):
        extract_layer(URL, batch_size=2)
