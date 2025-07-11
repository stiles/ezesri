import ezesri

# URL for LA County 2020 Census Tracts
URL = "https://public.gis.lacounty.gov/public/rest/services/LACounty_Dynamic/Demographics/MapServer/14"

def main():
    """
    Example script to demonstrate ezesri usage.
    """
    print(f"Fetching metadata from: {URL}")
    metadata = ezesri.get_metadata(URL)
    
    if metadata:
        print(f"Layer name: {metadata.get('name')}")
        print(f"Description: {metadata.get('description')}")
        print("-" * 30)

    print("Extracting layer to GeoDataFrame...")
    gdf = ezesri.extract_layer(URL)

    if not gdf.empty:
        print("Successfully created GeoDataFrame.")
        print("GeoDataFrame Info:")
        gdf.info()
        print("\nFirst 5 rows:")
        print(gdf.head())
    else:
        print("Failed to create GeoDataFrame.")

if __name__ == "__main__":
    main() 