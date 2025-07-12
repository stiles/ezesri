import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def main():
    """
    Creates a map of residential parcels with and without pools in Palm Springs,
    based on inferred residential status.
    """
    # Define file paths
    merged_parcels_path = "examples/data/parcels_with_class_codes.geojson"
    boundary_path = "examples/data/palm_springs_boundary.geojson"
    output_map_path = "examples/data/palm_springs_residential_pool_map.png"
    
    # Check if the required files exist
    if not os.path.exists(merged_parcels_path) or not os.path.exists(boundary_path):
        print("Required geojson files not found. Please run the data fetching and merging script first.")
        return

    # Load the datasets
    print("Loading data...")
    merged_parcels = gpd.read_file(merged_parcels_path)
    boundary = gpd.read_file(boundary_path)

    # Clip the parcels to the boundary
    print("Clipping parcels to the boundary...")
    clipped_parcels = gpd.clip(merged_parcels, boundary)

    # Infer residential status based on available fields
    print("Inferring residential status...")
    clipped_parcels['is_residential'] = (
        (clipped_parcels['BEDROOM_COUNT'] > 0) |
        (clipped_parcels['BATH_COUNT'] > 0)
    )

    residential_parcels = clipped_parcels[clipped_parcels['is_residential']].copy()

    # Report on pool statistics
    total_residential_parcels = len(residential_parcels)
    parcels_with_pools = residential_parcels[residential_parcels['POOL'].str.upper() == 'YES']
    count_with_pools = len(parcels_with_pools)
    percentage_with_pools = (count_with_pools / total_residential_parcels) * 100 if total_residential_parcels > 0 else 0

    print(f"Found {total_residential_parcels} residential parcels.")
    print(f"Found {count_with_pools} residential parcels with pools.")
    print(f"Share of residential parcels with pools: {percentage_with_pools:.2f}%")

    # Create a color column for plotting
    residential_parcels['color'] = '#d3d3d3'  # Light gray
    residential_parcels.loc[residential_parcels['POOL'].str.upper() == 'YES', 'color'] = '#0077be'

    # Create the map
    print("Creating map...")
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))
    
    # Plot residential parcels
    residential_parcels.plot(ax=ax, color=residential_parcels['color'], linewidth=0.1)
    
    # Plot boundary
    boundary.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=1)
    
    # Customize and save the plot
    ax.set_title('Residential parcels with pools in Palm Springs', fontsize=20, pad=20)
    ax.set_axis_off()

    # Add legend
    legend_patches = [
        mpatches.Patch(color='#0077be', label='Has pool'),
        mpatches.Patch(color='#d3d3d3', label='No pool')
    ]
    ax.legend(handles=legend_patches, loc='upper right', fontsize=12, title='Legend')
    
    fig.tight_layout()
    plt.savefig(output_map_path, dpi=300)
    print(f"Map saved to {output_map_path}")

if __name__ == "__main__":
    main() 