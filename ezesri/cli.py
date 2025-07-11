import click
import json
from . import get_metadata, extract_layer, bulk_export
import geopandas as gpd
import warnings
from .utils import truncate_field_names

@click.group()
def cli():
    """A command-line interface for extracting data from Esri REST endpoints."""
    pass

@cli.command()
@click.argument('url')
def metadata(url):
    """
    Fetches and prints the metadata for a given Esri layer URL.
    """
    click.echo("Fetching metadata...")
    data = get_metadata(url)
    if data:
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo("Could not fetch metadata.", err=True)

@cli.command()
@click.argument('url')
@click.option('--out', '-o', help="Output file path (e.g., 'data.geojson').")
@click.option('--format', '-f', type=click.Choice(['geojson', 'shapefile', 'csv'], case_sensitive=False), help="Output format.")
@click.option('--bbox', help="Bounding box filter in 'xmin,ymin,xmax,ymax' format.")
def fetch(url, out, format, bbox):
    """
    Extracts a layer and saves it to a file or prints it to the console.
    """
    normalized_url = url.strip().rstrip('/')
    if normalized_url.lower().endswith(('/mapserver', '/featureserver')):
        click.echo(
            "Error: This looks like a service URL. "
            "To download all layers from this service, use the 'bulk-fetch' command.",
            err=True
        )
        return

    if out and not format:
        raise click.UsageError("The --format option must be provided when specifying an output file.")

    bbox_tuple = None
    if bbox:
        try:
            bbox_tuple = tuple(map(float, bbox.split(',')))
            if len(bbox_tuple) != 4:
                raise ValueError
        except ValueError:
            raise click.UsageError("Bbox must be in 'xmin,ymin,xmax,ymax' format.")

    click.echo(f"Fetching layer from {url}...")
    gdf = extract_layer(url, bbox=bbox_tuple)

    if gdf.empty:
        click.echo("Could not extract layer or layer is empty.", err=True)
        return

    is_spatial = isinstance(gdf, gpd.GeoDataFrame)
    if not is_spatial:
        click.echo("Note: This layer is non-spatial and contains no geometry.")

    if out:
        try:
            if not is_spatial and format in ['geojson', 'shapefile']:
                raise click.UsageError(f"Cannot save non-spatial layer as {format}. Try '--format csv'.")

            if format == 'geojson':
                gdf.to_file(out, driver='GeoJSON')
                click.echo(f"Successfully saved layer to {out}")
            elif format == 'shapefile':
                # Use the 'fiona' engine to avoid warnings about truncated field names.
                gdf.to_file(out, engine='fiona')
                click.echo(f"Successfully saved shapefile to {out}")
            elif format == 'csv':
                # For CSV, we drop the geometry if it exists.
                df_to_save = gdf.drop(columns='geometry', errors='ignore')
                df_to_save.to_csv(out, index=False)
                click.echo(f"Successfully saved CSV to {out} (geometry column was dropped).")
        except Exception as e:
            click.echo(f"Error saving file: {e}", err=True)
    else:
        # Default behavior: print to console
        click.echo(gdf.to_string())

@cli.command('bulk-fetch')
@click.argument('url')
@click.argument('output-dir')
@click.option('--format', '-f', type=click.Choice(['geojson', 'shapefile', 'csv'], case_sensitive=False), default='geojson', help="Output format for all layers.")
def bulk_fetch(url, output_dir, format):
    """
    Fetches all layers from a service and saves them to a directory.
    """
    click.echo(f"Starting bulk export from {url} to {output_dir}...")
    bulk_export(url, output_dir, output_format=format)
    click.echo("Bulk export complete.") 