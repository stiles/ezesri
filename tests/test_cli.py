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

        args, kwargs = mock_bulk_export.call_args
        assert args == ('fake_service_url', 'output_dir')
        # Check the defaults that matter, not the whole signature
        assert kwargs['output_format'] == 'geojson'
        assert kwargs['where'] == '1=1'
        assert kwargs['bbox'] is None
        assert kwargs['out_sr'] == 4326
        assert kwargs['decode_domains'] is True
        assert kwargs['parse_dates'] is True


def test_bulk_fetch_passes_filters(mocker):
    """Bulk-fetch forwards its filters to bulk_export."""
    mock_bulk_export = mocker.patch('ezesri.cli.bulk_export')

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, [
            'bulk-fetch', 'fake_service_url', 'output_dir',
            '--where', "STATE = 'CA'",
            '--bbox', '-1,-1,1,1',
            '--out-sr', '3857',
        ])

        assert result.exit_code == 0
        kwargs = mock_bulk_export.call_args.kwargs
        assert kwargs['where'] == "STATE = 'CA'"
        assert kwargs['bbox'] == (-1.0, -1.0, 1.0, 1.0)
        assert kwargs['out_sr'] == 3857


def test_fetch_defaults_where_to_1_equals_1(mocker):
    """Omitting --where sends '1=1', not None, which requests would drop."""
    mock_extract = mocker.patch('ezesri.cli.extract_layer', return_value=gpd.GeoDataFrame())

    runner = CliRunner()
    runner.invoke(cli, ['fetch', 'fake_url'])

    assert mock_extract.call_args.kwargs['where'] == '1=1'


def test_fetch_passes_out_sr(mocker):
    """The --out-sr flag reaches extract_layer."""
    mock_extract = mocker.patch('ezesri.cli.extract_layer', return_value=gpd.GeoDataFrame())

    runner = CliRunner()
    runner.invoke(cli, ['fetch', 'fake_url', '--out-sr', '3857'])

    assert mock_extract.call_args.kwargs['out_sr'] == 3857


def test_fetch_rejects_invalid_geometry():
    """An unsupported GeoJSON type is caught before any download starts."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        'fetch', 'fake_url',
        '--geometry', '{"type": "GeometryCollection", "geometries": []}',
    ])

    assert result.exit_code != 0
    assert "Invalid geometry input" in result.output


def test_count_command(mocker):
    """The count command reports the server's feature count."""
    mocker.patch('ezesri.cli.get_count', return_value=1234)

    runner = CliRunner()
    result = runner.invoke(cli, ['count', 'fake_url'])

    assert result.exit_code == 0
    assert "1,234 features" in result.output


def test_fetch_decodes_by_default(mocker):
    """Decoding is on unless the user opts out."""
    mock_extract = mocker.patch('ezesri.cli.extract_layer', return_value=gpd.GeoDataFrame())

    runner = CliRunner()
    runner.invoke(cli, ['fetch', 'fake_url'])

    assert mock_extract.call_args.kwargs['decode_domains'] is True
    assert mock_extract.call_args.kwargs['parse_dates'] is True


def test_fetch_raw_flags_opt_out(mocker):
    """--raw-codes and --raw-dates turn decoding off."""
    mock_extract = mocker.patch('ezesri.cli.extract_layer', return_value=gpd.GeoDataFrame())

    runner = CliRunner()
    runner.invoke(cli, ['fetch', 'fake_url', '--raw-codes', '--raw-dates'])

    assert mock_extract.call_args.kwargs['decode_domains'] is False
    assert mock_extract.call_args.kwargs['parse_dates'] is False


def test_fetch_writes_codebook(mocker, tmp_path):
    """--codebook writes the sidecar file."""
    mocker.patch('ezesri.cli.extract_layer', return_value=gpd.GeoDataFrame())
    mocker.patch('ezesri.cli.get_codebook', return_value={'layer': 'Permits', 'fields': {}})

    target = tmp_path / "codebook.json"
    runner = CliRunner()
    result = runner.invoke(cli, ['fetch', 'fake_url', '--codebook', str(target)])

    assert result.exit_code == 0
    assert json.loads(target.read_text())['layer'] == 'Permits'


def test_codebook_command(mocker):
    """The codebook command prints JSON to stdout."""
    mocker.patch('ezesri.cli.get_codebook', return_value={'layer': 'Permits', 'fields': {}})

    runner = CliRunner()
    result = runner.invoke(cli, ['codebook', 'fake_url'])

    assert result.exit_code == 0
    assert json.loads(result.output)['layer'] == 'Permits'


def test_codebook_command_failure(mocker):
    """An unavailable codebook exits non-zero."""
    mocker.patch('ezesri.cli.get_codebook', return_value={})

    runner = CliRunner()
    result = runner.invoke(cli, ['codebook', 'fake_url'])

    assert result.exit_code != 0


def test_count_command_failure(mocker):
    """The count command exits non-zero when no count is available."""
    mocker.patch('ezesri.cli.get_count', return_value=None)

    runner = CliRunner()
    result = runner.invoke(cli, ['count', 'fake_url'])

    assert result.exit_code != 0 