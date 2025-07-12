import pytest
from ezesri import get_metadata, extract_layer
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