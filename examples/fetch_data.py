import os
import ezesri
import geopandas as gpd

def main():
    """
    An example script that fetches and prepares all the data needed for the
    Palm Springs pool analysis.
    """
    # --- 1. Define URLs and output paths ---
    palm_springs_boundary_url = "https://services.arcgis.com/f48yV21HSEYeCYMI/arcgis/rest/services/City_of_PS_Boundary/FeatureServer/0/query?where=1=1&f=geojson&outSR=4326"
    parcels_url = "https://gis.countyofriverside.us/arcgis/rest/services/mmc/mmc_mSrvc_v12_prod/MapServer/8"
    address_points_url = "https://gis.countyofriverside.us/arcgis/rest/services/mmc/mmc_mSrvc_v12_prod/MapServer/4"
    
    output_dir = "examples/data"
    merged_parcels_path = os.path.join(output_dir, "parcels_with_class_codes.geojson")

    # --- 2. Create output directory if it doesn't exist ---
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- 3. Fetch Palm Springs boundary ---
    print("Fetching Palm Springs boundary...")
    palm_springs_boundary_gdf = gpd.read_file(palm_springs_boundary_url)

    # --- 4. Fetch parcels within the boundary ---
    print("Fetching parcels in Palm Springs...")
    parcels_in_palm_springs = ezesri.extract.extract_layer(
        parcels_url,
        bbox=palm_springs_boundary_gdf.total_bounds,
    )
    print(f"Found {len(parcels_in_palm_springs)} parcels.")

    # --- 5. Fetch address points within the boundary ---
    print("Fetching address points in Palm Springs...")
    address_points = ezesri.extract.extract_layer(
        address_points_url,
        bbox=palm_springs_boundary_gdf.total_bounds,
    )
    print(f"Found {len(address_points)} address points.")

    # --- 6. Merge parcels and address points ---
    print("Merging parcels and address points...")
    # Ensure APN columns are of the same type for merging
    parcels_in_palm_springs['APN'] = parcels_in_palm_springs['APN'].astype(str)
    address_points['APN'] = address_points['APN'].astype(str)
    
    merged_parcels = parcels_in_palm_springs.merge(
        address_points[['APN', 'CLASS_CODE', 'ADDRESS_TYPE']],
        on='APN',
        how='left'
    )
    print(f"Merged data has {len(merged_parcels)} records.")

    # --- 7. Save the merged data ---
    print(f"Saving merged data to {merged_parcels_path}...")
    merged_parcels.to_file(merged_parcels_path, driver="GeoJSON")
    print("Data acquisition and preparation complete.")

if __name__ == "__main__":
    main() 