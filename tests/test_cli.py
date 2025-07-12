import pytest
from click.testing import CliRunner
from ezesri.cli import cli
import json
import geopandas as gpd

def test_metadata_command_summary(mocker):
    """Tests the metadata command with summarized output."""
    mock_get_metadata = mocker.patch('ezesri.cli.get_metadata', return_value={'name': 'Test Layer'})
    mock_summarize_metadata = mocker.patch('ezesri.cli.summarize_metadata', return_value='Summary')
    
    runner = CliRunner()
    result = runner.invoke(cli, ['metadata', 'fake_url'])
    
    assert result.exit_code == 0
    assert 'Summary' in result.output
    mock_get_metadata.assert_called_once_with('fake_url')
    mock_summarize_metadata.assert_called_once()

def test_metadata_command_json(mocker):
    """Tests the metadata command with JSON output."""
    mock_get_metadata = mocker.patch('ezesri.cli.get_metadata', return_value={'name': 'Test Layer'})
    
    runner = CliRunner()
    result = runner.invoke(cli, ['metadata', 'fake_url', '--json'])
    
    assert result.exit_code == 0
    # The output contains a status message, so we parse the JSON from the end
    json_output = result.output.split('\n', 1)[1]
    assert json.loads(json_output) == {'name': 'Test Layer'}
    mock_get_metadata.assert_called_once_with('fake_url')

def test_fetch_command_with_output(mocker):
    """Tests the fetch command with an output file."""
    # Return a dummy GeoDataFrame to simulate a successful extraction
    mock_gdf = gpd.GeoDataFrame([{'geometry': None}])
    mock_extract = mocker.patch('ezesri.cli.extract_layer', return_value=mock_gdf)
    
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['fetch', 'fake_url', '--out', 'output.geojson', '--format', 'geojson'])
        
        assert result.exit_code == 0
        assert "Successfully saved layer to output.geojson" in result.output
        mock_extract.assert_called_once()

def test_fetch_command_with_service_url_error(mocker):
    """Tests that the fetch command fails with a service URL."""
    runner = CliRunner()
    result = runner.invoke(cli, ['fetch', 'http://test.com/featureserver'])
    
    assert result.exit_code == 0 # The command exits gracefully
    assert "Error: This looks like a service URL" in result.output

def test_bulk_fetch_command(mocker):
    """Tests the bulk-fetch command."""
    mock_bulk_export = mocker.patch('ezesri.cli.bulk_export')
    
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['bulk-fetch', 'fake_service_url', 'output_dir'])
        
        assert result.exit_code == 0
        assert "Starting bulk export" in result.output
        mock_bulk_export.assert_called_once_with('fake_service_url', 'output_dir', output_format='geojson') 