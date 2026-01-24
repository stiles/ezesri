"""
Generate a markdown directory from harvested ArcGIS services.

Reads JSON files from sample_output/ and produces a clean markdown catalog.

Usage:
    python harvester/generate_directory.py
"""

import json
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "sample_output"
DIRECTORY_FILE = Path(__file__).parent / "directory.md"
CATALOG_JSON_FILE = Path(__file__).parent / "catalog.json"


US_STATES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
    "pennsylvania", "rhode island", "south carolina", "south dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west virginia", "wisconsin", "wyoming", "district of columbia"
}

US_STATE_ABBREVS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC"
}

ABBREV_TO_STATE = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
}

# Known owner -> place mappings for common data publishers
KNOWN_OWNERS = {
    # Federal / National (USA)
    "esri_livefeeds2": "Esri (USA)",
    "esri_landscape2": "Esri (USA)",
    "NIFC_Authoritative": "NIFC (USA)",
    "Esri_US_Federal_Data": "Federal (USA)",
    "Federal_User_Community": "Federal (USA)",
    "USDOT_BTS": "USDOT (USA)",
    "matthew.osborn_TSG": "US Dept of State",
    
    # State agencies
    "MichiganDNR": "Michigan",
    "mdimapdatacatalog": "Maryland",
    "NJDEPBGIS": "New Jersey",
    "NJOGIS": "New Jersey",
    "Services_VCGI": "Vermont",
    "Province.Of.British.Columbia": "British Columbia, CA",
    "Manitoba_Government": "Manitoba, CA",
    
    # Major cities - USA
    "City_of_Minneapolis": "Minneapolis, MN",
    "Minneapolis": "Minneapolis, MN",
    "NashvilleOpenData": "Nashville, TN",
    "SPDGIS_Admin": "Seattle, WA",
    "RaleighGIS": "Raleigh, NC",
    "DCGISopendata": "Washington, DC",
    "CityofSaintPaul": "Saint Paul, MN",
    "JohnsCreekGA": "Johns Creek, GA",
    "tlattibeaudiere": "Miami Gardens, FL",
    "CDAUG_JerseyCity": "Jersey City, NJ",
    "ksolomon_interdev_marco": "Marco Island, FL",
    
    # Counties - USA
    "WakeCountyGovernment": "Wake County, NC",
    "WeldCounty": "Weld County, CO",
    "GIS_DakotaCounty": "Dakota County, MN",
    "JeffersonCountyMO": "Jefferson County, MO",
    "waukco": "Waukesha County, WI",
    "scgarc": "Sampson County, NC",
    "joellogan": "Jackson County, GA",
    "OA_EOC_GIS_Unit": "Los Angeles County, CA",
    "preynolds43": "Stanly County, NC",
    "tpenegar": "Chowan County, NC",
    
    # Texas
    "patrick.corley_mark_43": "Denton County, TX",
    "elise.austin_mark43": "Elk Grove, CA",
    
    # International
    "TorontoPoliceService": "Toronto, ON",
    "brisbaneopendata": "Brisbane, AU",
    "BrisbaneCityCouncil": "Brisbane, AU",
    "FingalAdmin": "Fingal County, IE",
    "canterburymaps": "Canterbury, NZ",
    
    # Utilities
    "PGE_PublicData": "PG&E (California)",
}

# Title translations for non-English service names
TITLE_TRANSLATIONS = {
    "Deutschland_Bundesländergrenzen_2018": "German State Boundaries (2018)",
    "Bundesländergrenzen_2018": "German State Boundaries (2018)",
    "全国市区町村界データ（簡易版）": "Japan Municipal Boundaries (Simplified)",
    "全国市区町村界データ2016": "Japan Municipal Boundaries (2016)",
    "Cercos Sanitarios Estratégicos": "Strategic Health Zones (Spain)",
}


def extract_place(item: dict) -> str:
    """
    Extract a place/organization name from the item.
    
    Priority:
    1. Known owner mapping
    2. Tags containing location names (states, counties, cities)
    3. accessInformation © attribution
    4. Owner name patterns
    5. Cleaned owner name fallback
    """
    owner = item.get("owner", "")
    tags = item.get("tags", [])
    access_info = item.get("accessInformation", "") or ""
    
    # 1. Check known owners first
    if owner in KNOWN_OWNERS:
        return KNOWN_OWNERS[owner]
    
    # 2. Scan tags for location info (best signal)
    location_from_tags = _extract_location_from_tags(tags)
    if location_from_tags:
        return location_from_tags
    
    # 3. Check accessInformation for © attribution
    location_from_access = _extract_location_from_attribution(access_info)
    if location_from_access:
        return location_from_access
    
    # 4. Parse owner name patterns
    location_from_owner = _extract_location_from_owner(owner)
    if location_from_owner:
        return location_from_owner
    
    # 5. Fall back to cleaned owner name
    if owner:
        cleaned = re.sub(r"(?:GIS|OpenData|_admin|Admin|Data|_)$", "", owner, flags=re.IGNORECASE)
        cleaned = re.sub(r"[_.]", " ", cleaned).strip()
        if cleaned:
            return cleaned
    
    return "Unknown"


def _extract_location_from_tags(tags: list) -> str | None:
    """Extract location from tags, prioritizing specific locations over states."""
    if not tags:
        return None
    
    counties = []
    cities = []
    states = []
    
    for tag in tags:
        if not tag:
            continue
        tag_clean = tag.strip()
        tag_lower = tag_clean.lower()
        
        # Skip generic/unhelpful tags
        if tag_lower in ["open data", "opendata", "arcgis", "gis", "data", "boundaries", 
                         "parcels", "parcel", "zoning", "government", "police", "crime",
                         "military", "environment", "updated", ""]:
            continue
        
        # Check for county pattern
        if "county" in tag_lower:
            counties.append(tag_clean)
            continue
        
        # Check for "City of X" pattern
        city_match = re.match(r"city of (.+)", tag_lower)
        if city_match:
            cities.append(tag_clean.title())
            continue
        
        # Check if it's a US state name
        if tag_lower in US_STATES:
            states.append(tag_clean.title())
            continue
        
        # Check if it's a state abbreviation
        if tag_clean.upper() in US_STATE_ABBREVS:
            states.append(ABBREV_TO_STATE.get(tag_clean.upper(), tag_clean))
            continue
        
        # Check for city-like proper nouns (capitalized, not generic)
        if tag_clean[0].isupper() and len(tag_clean) > 2 and " " not in tag_clean:
            # Could be a city name
            cities.append(tag_clean)
    
    # Return most specific location found
    if counties:
        return counties[0]
    if cities:
        # Try to pair city with state if available
        if states:
            return f"{cities[0]}, {_abbreviate_state(states[0])}"
        return cities[0]
    if states:
        return states[0]
    
    return None


def _abbreviate_state(state_name: str) -> str:
    """Convert full state name to abbreviation."""
    for abbrev, name in ABBREV_TO_STATE.items():
        if name.lower() == state_name.lower():
            return abbrev
    return state_name


def _extract_location_from_attribution(access_info: str) -> str | None:
    """Extract location from © attribution text."""
    if not access_info:
        return None
    
    # Look for "© City of X" or "© X County" patterns
    patterns = [
        r"©\s*(?:The\s+)?City\s+(?:of\s+)?([A-Za-z\s]+?)(?:\s+\d{4}|\s*$|,)",
        r"©\s*(?:The\s+)?County\s+of\s+([A-Za-z\s]+?)(?:\s+\d{4}|\s*$|,)",
        r"©\s*([A-Za-z\s]+?)\s+County(?:\s+\d{4}|\s*$|,)",
        r"©\s*([A-Za-z\s]+?)\s+(?:City|Government|Council)(?:\s+\d{4}|\s*$|,)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, access_info, re.IGNORECASE)
        if match:
            place = match.group(1).strip()
            if place and len(place) > 2:
                # Check if it's a county pattern
                if "county of" in pattern.lower():
                    return f"{place} County"
                return place.title()
    
    return None


def _extract_location_from_owner(owner: str) -> str | None:
    """Extract location from owner name patterns."""
    if not owner:
        return None
    
    patterns = [
        # "CityOfBoston" or "City_of_Boston" -> "Boston"
        (r"(?:CityOf|City_of_|CityOf_)([A-Za-z]+)", None),
        # "BostonGIS" or "Boston_GIS" -> "Boston"
        (r"^([A-Za-z]+?)(?:_)?(?:GIS|OpenData|Data|Maps|Open)(?:_Admin)?$", None),
        # "CountyOfRiverside" -> "Riverside County"
        (r"(?:CountyOf|County_of_)([A-Za-z]+)", "County"),
        # "RiversideCounty" -> "Riverside County"
        (r"^([A-Za-z]+)County$", "County"),
        # State DOT patterns "TXDOT" -> "Texas"
        (r"^([A-Z]{2})(?:DOT|DEQ|DNR|DEM|DEP|DEC)$", "state"),
    ]
    
    for pattern, suffix in patterns:
        match = re.search(pattern, owner, re.IGNORECASE)
        if match:
            place = match.group(1)
            if suffix == "County":
                return f"{place} County"
            if suffix == "state":
                # Convert state abbreviation to full name
                return ABBREV_TO_STATE.get(place.upper(), place)
            return place
    
    return None


def extract_subject(item: dict) -> str:
    """
    Extract a short subject/topic description.
    Translates known non-English titles to English.
    """
    title = item.get("title", "")
    snippet = item.get("snippet", "")
    
    # Check for known translations first
    if title in TITLE_TRANSLATIONS:
        return TITLE_TRANSLATIONS[title]
    
    # Also check with underscores removed
    title_normalized = title.replace(" ", "_")
    if title_normalized in TITLE_TRANSLATIONS:
        return TITLE_TRANSLATIONS[title_normalized]
    
    # Use title, truncated if needed
    if title:
        # Remove common prefixes/suffixes
        subject = re.sub(r"(?:_view|_public|_open_data)$", "", title, flags=re.IGNORECASE)
        subject = subject.replace("_", " ")
        # Truncate long titles
        if len(subject) > 60:
            subject = subject[:57] + "..."
        return subject
    
    if snippet:
        # First sentence of snippet
        first_sentence = snippet.split(".")[0]
        if len(first_sentence) > 60:
            return first_sentence[:57] + "..."
        return first_sentence
    
    return "Unnamed service"


def load_results() -> dict[str, list[dict]]:
    """
    Load all JSON result files from sample_output.
    
    Returns dict mapping category name to list of items.
    """
    results = {}
    
    for json_file in OUTPUT_DIR.glob("*.json"):
        # Skip combined files
        if "combined" in json_file.name:
            continue
        
        # Extract category from filename (e.g., "parcels_20260124_082214.json" -> "parcels")
        category = json_file.stem.rsplit("_", 2)[0]
        
        with open(json_file) as f:
            data = json.load(f)
        
        items = data.get("items", [])
        
        # If we already have this category, keep the newer one (or merge)
        if category not in results or len(items) > len(results[category]):
            results[category] = items
    
    return results


def dedupe_by_url(items: list[dict]) -> list[dict]:
    """Remove duplicate items based on URL."""
    seen_urls = set()
    unique = []
    for item in items:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(item)
    return unique


def generate_markdown(results: dict[str, list[dict]]) -> str:
    """
    Generate markdown content from categorized results.
    """
    lines = []
    
    # Header
    lines.append("# Esri Public Services Directory")
    lines.append("")
    lines.append(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")
    
    # Summary stats
    total_services = sum(len(items) for items in results.values())
    total_layers = sum(
        len(item.get("service", {}).get("layers", []))
        for items in results.values()
        for item in items
    )
    total_views = sum(
        item.get("numViews", 0)
        for items in results.values()
        for item in items
    )
    
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Categories | {len(results)} |")
    lines.append(f"| Services | {total_services:,} |")
    lines.append(f"| Total layers | {total_layers:,} |")
    lines.append(f"| Combined views | {total_views:,} |")
    lines.append("")
    
    # Category breakdown
    lines.append("### By category")
    lines.append("")
    lines.append("| Category | Services | Layers |")
    lines.append("|----------|----------|--------|")
    
    for category, items in sorted(results.items()):
        layer_count = sum(
            len(item.get("service", {}).get("layers", []))
            for item in items
        )
        display_name = category.replace("_", " ").title()
        lines.append(f"| {display_name} | {len(items)} | {layer_count} |")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Services by category
    for category, items in sorted(results.items()):
        display_name = category.replace("_", " ").title()
        lines.append(f"## {display_name}")
        lines.append("")
        
        # Sort by views (most popular first)
        sorted_items = sorted(items, key=lambda x: x.get("numViews", 0), reverse=True)
        
        # Dedupe
        sorted_items = dedupe_by_url(sorted_items)
        
        lines.append("| Place | Subject | Link |")
        lines.append("|-------|---------|------|")
        
        for item in sorted_items:
            place = extract_place(item)
            subject = extract_subject(item)
            url = item.get("url", "")
            
            # Escape pipes in text
            place = place.replace("|", "\\|")
            subject = subject.replace("|", "\\|")
            
            if url:
                lines.append(f"| {place} | {subject} | [Service]({url}) |")
            else:
                lines.append(f"| {place} | {subject} | N/A |")
        
        lines.append("")
    
    return "\n".join(lines)


def generate_catalog_json(results: dict[str, list[dict]]) -> dict:
    """
    Generate a JSON catalog structure for the web app.
    
    Returns a dict with summary stats and flattened services list.
    """
    # Build flattened services list with enriched metadata
    services = []
    seen_urls = set()
    
    for category, items in results.items():
        category_display = category.replace("_", " ").title()
        
        for item in items:
            url = item.get("url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Get service metadata
            service_meta = item.get("service", {})
            layers = service_meta.get("layers", [])
            
            services.append({
                "id": item.get("id", ""),
                "title": extract_subject(item),
                "place": extract_place(item),
                "category": category_display,
                "categoryKey": category,
                "url": url,
                "description": item.get("snippet") or item.get("description") or "",
                "owner": item.get("owner", ""),
                "numViews": item.get("numViews", 0),
                "tags": [t for t in item.get("tags", []) if t],
                "layers": [
                    {"id": l.get("id"), "name": l.get("name"), "type": l.get("geometryType")}
                    for l in layers
                ],
                "layerCount": len(layers),
                "capabilities": service_meta.get("capabilities", ""),
                "maxRecordCount": service_meta.get("maxRecordCount"),
            })
    
    # Sort by views
    services.sort(key=lambda x: x.get("numViews", 0), reverse=True)
    
    # Compute summary stats
    total_layers = sum(s["layerCount"] for s in services)
    total_views = sum(s["numViews"] for s in services)
    categories = sorted(set(s["categoryKey"] for s in services))
    
    category_stats = []
    for cat in categories:
        cat_services = [s for s in services if s["categoryKey"] == cat]
        category_stats.append({
            "key": cat,
            "name": cat.replace("_", " ").title(),
            "count": len(cat_services),
            "layers": sum(s["layerCount"] for s in cat_services),
        })
    
    return {
        "generated": datetime.now().isoformat(),
        "summary": {
            "totalServices": len(services),
            "totalLayers": total_layers,
            "totalViews": total_views,
            "categoryCount": len(categories),
        },
        "categories": category_stats,
        "services": services,
    }


def main():
    """Generate the directory markdown and JSON catalog files."""
    print("Loading harvested results...")
    results = load_results()
    
    if not results:
        print("No results found in sample_output/")
        return
    
    print(f"Found {len(results)} categories:")
    for cat, items in results.items():
        print(f"  - {cat}: {len(items)} services")
    
    # Generate markdown
    print("\nGenerating markdown...")
    markdown = generate_markdown(results)
    
    with open(DIRECTORY_FILE, "w") as f:
        f.write(markdown)
    
    print(f"Markdown saved to: {DIRECTORY_FILE}")
    
    # Generate JSON catalog
    print("\nGenerating JSON catalog...")
    catalog = generate_catalog_json(results)
    
    with open(CATALOG_JSON_FILE, "w") as f:
        json.dump(catalog, f, indent=2)
    
    print(f"JSON catalog saved to: {CATALOG_JSON_FILE}")
    print(f"  - {catalog['summary']['totalServices']} services")
    print(f"  - {catalog['summary']['totalLayers']} layers")
    print(f"  - {catalog['summary']['categoryCount']} categories")


if __name__ == "__main__":
    main()
