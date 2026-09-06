import click
import json
from . import (
    get_metadata,
    get_count,
    get_codebook,
    extract_layer,
    bulk_export,
    summarize_metadata,
)
import geopandas as gpd
import warnings
from .utils import (
    truncate_field_names,
    has_filegdb_write_support,
    drop_empty_geometries,
    unique_geometry_types,
    write_ndjson,
    geojson_to_esri_geometry,
)
import os


def _parse_bbox(bbox):
    """Parses a 'xmin,ymin,xmax,ymax' string into a tuple of floats."""
    if not bbox:
        return None
    try:
        bbox_tuple = tuple(map(float, bbox.split(',')))
    except ValueError:
        raise click.UsageError("Bbox must be in 'xmin,ymin,xmax,ymax' format.")
    if len(bbox_tuple) != 4:
        raise click.UsageError("Bbox must be in 'xmin,ymin,xmax,ymax' format.")
    return bbox_tuple


def _parse_geometry(geometry):
    """
    Loads a GeoJSON geometry from a file path or a raw string.

    Validates that it converts to Esri JSON so the user gets an immediate error
    rather than a failure mid-download.
    """
    if not geometry:
        return None

    try:
        if os.path.exists(geometry):
            with open(geometry, 'r') as f:
                geometry_filter = json.load(f)
        else:
            geometry_filter = json.loads(geometry)
    except (json.JSONDecodeError, IOError) as e:
        raise click.UsageError(
            f"Invalid geometry input. Must be a valid GeoJSON file or string. Error: {e}"
        )

    try:
        geojson_to_esri_geometry(geometry_filter)
    except ValueError as e:
        raise click.UsageError(f"Invalid geometry input: {e}")

    return geometry_filter


@click.group()
@click.version_option(package_name='ezesri')
def cli():
    """A command-line interface for extracting data from Esri REST endpoints."""
    pass

@cli.command()
@click.argument('url')
@click.option('--json', 'as_json', is_flag=True, help="Output the raw JSON metadata.")
def metadata(url, as_json):
    """
    Fetches and prints the metadata for a given Esri layer URL.

    By default, it displays a summarized, human-readable output.
    Use the --json flag to get the raw JSON.
    """
    click.echo("Fetching metadata...")
    data = get_metadata(url)
    
    if not data:
        click.echo("Could not fetch metadata.", err=True)
        return

    if as_json:
        click.echo(json.dumps(data, indent=2))
    else:
        summary = summarize_metadata(data)
        click.echo(summary)

@cli.command()
@click.argument('url')
@click.option('--out', '-o', '--output', help="Output file path (e.g., 'data.geojson').")
@click.option('--format', '-f', '--fmt', type=click.Choice(['geojson', 'shapefile', 'csv', 'gdb', 'gpkg', 'geoparquet', 'parquet', 'ndjson'], case_sensitive=False), help="Output format.")
@click.option('--where', '-w', default='1=1', help="SQL WHERE clause for filtering (e.g., \"State = 'CA'\").")
@click.option('--bbox', help="Bounding box filter in 'xmin,ymin,xmax,ymax' format (WGS84).")
@click.option('--geometry', help="Path to a GeoJSON file or a raw GeoJSON string for spatial filtering.")
@click.option('--spatial-rel', default='esriSpatialRelIntersects', type=click.Choice(['esriSpatialRelIntersects', 'esriSpatialRelContains', 'esriSpatialRelWithin']), help="Spatial relationship for filtering.")
@click.option('--out-sr', default=4326, type=int, help="WKID of the output spatial reference. Defaults to 4326 (WGS84).")
@click.option('--raw-codes', is_flag=True, help="Keep Esri coded values instead of decoding them to their labels.")
@click.option('--raw-dates', is_flag=True, help="Keep Esri date fields as raw epoch milliseconds.")
@click.option('--codebook', help="Write a JSON codebook of coded values and date fields to this path.")
def fetch(url, out, format, where, bbox, geometry, spatial_rel, out_sr, raw_codes, raw_dates, codebook):
    """
    Extracts a layer and saves it to a file or prints it to the console.

    Coded values are decoded to their labels and date fields are converted to
    timestamps by default. Use --raw-codes and --raw-dates to opt out.
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

    if bbox and geometry:
        raise click.UsageError("Cannot use both --bbox and --geometry at the same time.")

    bbox_tuple = _parse_bbox(bbox)
    geometry_filter = _parse_geometry(geometry)

    click.echo(f"Fetching layer from {url}...")
    gdf = extract_layer(
        url,
        where=where,
        bbox=bbox_tuple,
        geometry=geometry_filter,
        spatial_rel=spatial_rel,
        out_sr=out_sr,
        decode_domains=not raw_codes,
        parse_dates=not raw_dates,
    )

    if codebook:
        book = get_codebook(url)
        if book:
            with open(codebook, 'w', encoding='utf-8') as f:
                json.dump(book, f, indent=2, default=str)
            click.echo(f"Wrote codebook to {codebook}")
        else:
            click.echo("Could not build a codebook for this layer.", err=True)

    if gdf.empty:
        click.echo("Could not extract layer or layer is empty.", err=True)
        return

    is_spatial = isinstance(gdf, gpd.GeoDataFrame)
    if not is_spatial:
        click.echo("Note: This layer is non-spatial and contains no geometry.")

    if out or format in ['ndjson']:
        try:
            if not is_spatial and format in ['geojson', 'shapefile', 'gdb', 'gpkg', 'geoparquet']:
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
            elif format == 'parquet':
                # Write non-spatial parquet (drop geometry if present)
                df_to_save = gdf.drop(columns='geometry', errors='ignore')
                try:
                    df_to_save.to_parquet(out)
                except Exception as e:
                    raise click.UsageError(f"Writing Parquet requires pyarrow or fastparquet. Error: {e}")
                click.echo(f"Successfully saved Parquet to {out}")
            elif format == 'geoparquet':
                if not is_spatial:
                    raise click.UsageError("GeoParquet requires spatial data. Use '--format parquet' for tables.")
                cleaned_gdf, dropped = drop_empty_geometries(gdf)
                if dropped:
                    click.echo(f"Warning: Dropped {dropped} features with null/empty geometry before writing.")
                try:
                    cleaned_gdf.to_parquet(out)
                except Exception as e:
                    raise click.UsageError(f"Writing GeoParquet requires geopandas with pyarrow. Error: {e}")
                click.echo(f"Successfully saved GeoParquet to {out}")
            elif format == 'ndjson':
                # Allow stdout when out is not provided or '-'
                target = out or "-"
                cleaned_df, dropped = (drop_empty_geometries(gdf) if is_spatial else (gdf, 0))
                if dropped:
                    click.echo(f"Warning: Dropped {dropped} features with null/empty geometry before writing.")
                write_ndjson(cleaned_df, target)
                if target != "-":
                    click.echo(f"Successfully saved NDJSON to {target}")
            elif format == 'gpkg':
                if not out.lower().endswith('.gpkg'):
                    raise click.UsageError("Output for GPKG format must be a path ending in .gpkg")
                layer_name = os.path.splitext(os.path.basename(out))[0]
                cleaned_gdf, dropped = drop_empty_geometries(gdf)
                if dropped:
                    click.echo(f"Warning: Dropped {dropped} features with null/empty geometry before writing.")
                cleaned_gdf.to_file(out, driver='GPKG', layer=layer_name)
                click.echo(f"Successfully saved layer '{layer_name}' to {out}")
            elif format == 'gdb':
                # Assumes the output path 'out' ends with .gdb
                if not out.lower().endswith('.gdb'):
                    raise click.UsageError("Output for GDB format must be a path ending in .gdb")
                supported, msg = has_filegdb_write_support()
                if not supported:
                    raise click.UsageError(msg + " Tip: Use '--format gpkg' with a .gpkg output path for a similar container.")
                # Clean null/empty geometries to avoid common driver errors
                cleaned_gdf, dropped = drop_empty_geometries(gdf)
                if dropped:
                    click.echo(f"Warning: Dropped {dropped} features with null/empty geometry before writing.")
                # Enforce consistent geometry types (FileGDB often fails on mixed types)
                geom_types = unique_geometry_types(cleaned_gdf)
                if len(geom_types) > 1:
                    raise click.UsageError(
                        f"Mixed geometry types detected: {geom_types}. FileGDB writes generally require a single "
                        "geometry type per layer. Consider filtering or converting geometries, or use GeoPackage/GeoJSON."
                    )
                # Layer name is inferred from the output file name, without extension
                layer_name = os.path.splitext(os.path.basename(out))[0]
                cleaned_gdf.to_file(out, driver='FileGDB', layer=layer_name)
                click.echo(f"Successfully saved layer '{layer_name}' to {out}")
        except Exception as e:
            click.echo(f"Error saving file: {e}", err=True)
    else:
        # Default behavior: print to console
        click.echo(gdf.to_string())

@cli.command()
@click.argument('url')
@click.option('--where', '-w', default='1=1', help="SQL WHERE clause for filtering (e.g., \"State = 'CA'\").")
@click.option('--bbox', help="Bounding box filter in 'xmin,ymin,xmax,ymax' format (WGS84).")
@click.option('--geometry', help="Path to a GeoJSON file or a raw GeoJSON string for spatial filtering.")
@click.option('--spatial-rel', default='esriSpatialRelIntersects', type=click.Choice(['esriSpatialRelIntersects', 'esriSpatialRelContains', 'esriSpatialRelWithin']), help="Spatial relationship for filtering.")
def count(url, where, bbox, geometry, spatial_rel):
    """
    Reports how many features match a query, without downloading them.
    """
    bbox_tuple = _parse_bbox(bbox)
    geometry_filter = _parse_geometry(geometry)

    result = get_count(
        url,
        where=where,
        bbox=bbox_tuple,
        geometry=geometry_filter,
        spatial_rel=spatial_rel,
    )

    if result is None:
        click.echo("Could not get a feature count for this layer.", err=True)
        raise SystemExit(1)

    click.echo(f"{result:,} features match this query.")


@cli.command('bulk-fetch')
@click.argument('url')
@click.argument('output-dir')
@click.option('--format', '-f', '--fmt', type=click.Choice(['geojson', 'shapefile', 'csv', 'gdb', 'gpkg', 'geoparquet', 'parquet', 'ndjson'], case_sensitive=False), default='geojson', help="Output format for all layers.")
@click.option('--workers', '-w', type=int, default=1, help="Number of parallel workers to export layers.")
@click.option('--rate', type=float, default=0.0, help="Global max requests per second (0 to disable).")
@click.option('--where', default='1=1', help="SQL WHERE clause applied to every layer.")
@click.option('--bbox', help="Bounding box filter in 'xmin,ymin,xmax,ymax' format (WGS84).")
@click.option('--geometry', help="Path to a GeoJSON file or a raw GeoJSON string for spatial filtering.")
@click.option('--spatial-rel', default='esriSpatialRelIntersects', type=click.Choice(['esriSpatialRelIntersects', 'esriSpatialRelContains', 'esriSpatialRelWithin']), help="Spatial relationship for filtering.")
@click.option('--out-sr', default=4326, type=int, help="WKID of the output spatial reference. Defaults to 4326 (WGS84).")
@click.option('--raw-codes', is_flag=True, help="Keep Esri coded values instead of decoding them to their labels.")
@click.option('--raw-dates', is_flag=True, help="Keep Esri date fields as raw epoch milliseconds.")
@click.option('--codebooks', is_flag=True, help="Write a <layer>.codebook.json next to each layer's output.")
def bulk_fetch(url, output_dir, format, workers, rate, where, bbox, geometry, spatial_rel, out_sr, raw_codes, raw_dates, codebooks):
    """
    Fetches all layers from a service and saves them to a directory.

    Coded values are decoded to their labels and date fields are converted to
    timestamps by default. Use --raw-codes and --raw-dates to opt out.
    """
    bbox_tuple = _parse_bbox(bbox)
    geometry_filter = _parse_geometry(geometry)

    click.echo(f"Starting bulk export from {url} to {output_dir}...")
    if workers > 1:
        click.echo(f"Using {workers} workers...")
    if rate and rate > 0:
        click.echo(f"Applying global rate limit: {rate} req/s")

    bulk_export(
        url,
        output_dir,
        output_format=format,
        workers=workers,
        rate=rate,
        where=where,
        bbox=bbox_tuple,
        geometry=geometry_filter,
        spatial_rel=spatial_rel,
        out_sr=out_sr,
        decode_domains=not raw_codes,
        parse_dates=not raw_dates,
        write_codebook=codebooks,
    )
    click.echo("Bulk export complete.")


@cli.command()
@click.argument('url')
@click.option('--out', '-o', help="Write the codebook to this path instead of stdout.")
def codebook(url, out):
    """
    Prints a codebook of a layer's coded values and date fields.
    """
    book = get_codebook(url)

    if not book:
        click.echo("Could not build a codebook for this layer.", err=True)
        raise SystemExit(1)

    text = json.dumps(book, indent=2, default=str)

    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(text)
        click.echo(f"Wrote codebook to {out}")
    else:
        click.echo(text)