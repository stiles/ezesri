"""
ArcGIS Online Harvester - Proof of Concept

Explore the ArcGIS Online portal search API to discover public Feature/Map services
and evaluate what kind of data is available for a potential directory.

Usage:
    python harvester/explore.py
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# ArcGIS Online portal search endpoint
PORTAL_SEARCH_URL = "https://www.arcgis.com/sharing/rest/search"

# Output directory for sample results
OUTPUT_DIR = Path(__file__).parent / "sample_output"


def search_portal(
    query: str,
    num: int = 100,
    start: int = 1,
    sort_field: str = "numViews",
    sort_order: str = "desc"
) -> dict:
    """
    Search the ArcGIS Online portal for public items.
    
    Args:
        query: Portal search query string (e.g., 'type:"Feature Service" AND access:public')
        num: Number of results per page (max 100)
        start: Starting result index (1-based)
        sort_field: Field to sort by (numViews, created, modified, title)
        sort_order: Sort order (asc, desc)
    
    Returns:
        Raw JSON response from the portal search API
    """
    params = {
        "q": query,
        "num": min(num, 100),
        "start": start,
        "sortField": sort_field,
        "sortOrder": sort_order,
        "f": "json"
    }
    
    response = requests.get(PORTAL_SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def search_all(query: str, max_results: int = 500) -> list[dict]:
    """
    Search portal with automatic pagination to get more results.
    
    Args:
        query: Portal search query string
        max_results: Maximum total results to fetch
    
    Returns:
        List of all result items
    """
    all_results = []
    start = 1
    
    while len(all_results) < max_results:
        data = search_portal(query, num=100, start=start)
        results = data.get("results", [])
        
        if not results:
            break
            
        all_results.extend(results)
        
        # Check if there are more results
        next_start = data.get("nextStart", -1)
        if next_start == -1 or next_start <= start:
            break
        start = next_start
    
    return all_results[:max_results]


def get_service_metadata(service_url: str, timeout: int = 15) -> Optional[dict]:
    """
    Fetch metadata from an Esri REST service endpoint.
    
    Args:
        service_url: URL to the FeatureServer or MapServer
        timeout: Request timeout in seconds
    
    Returns:
        Service metadata dict or None if failed
    """
    try:
        # Clean URL and add JSON format
        url = service_url.rstrip("/")
        if not url.endswith("?f=pjson"):
            url = f"{url}?f=pjson"
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        # Check for error response
        if "error" in data:
            return None
            
        return data
    except Exception:
        return None


def enrich_result(item: dict) -> dict:
    """
    Enrich a portal search result with service-level metadata.
    
    Args:
        item: Portal search result item
    
    Returns:
        Enriched item with service metadata
    """
    enriched = {
        "id": item.get("id"),
        "title": item.get("title"),
        "snippet": item.get("snippet"),
        "description": item.get("description"),
        "url": item.get("url"),
        "owner": item.get("owner"),
        "orgId": item.get("orgId"),
        "created": item.get("created"),
        "modified": item.get("modified"),
        "numViews": item.get("numViews"),
        "numRatings": item.get("numRatings"),
        "avgRating": item.get("avgRating"),
        "type": item.get("type"),
        "tags": item.get("tags", []),
        "categories": item.get("categories", []),
        "extent": item.get("extent"),
        "spatialReference": item.get("spatialReference"),
        "accessInformation": item.get("accessInformation"),
        "licenseInfo": item.get("licenseInfo"),
    }
    
    # Fetch service metadata if URL exists
    service_url = item.get("url")
    if service_url:
        service_meta = get_service_metadata(service_url)
        if service_meta:
            enriched["service"] = {
                "serviceDescription": service_meta.get("serviceDescription"),
                "description": service_meta.get("description"),
                "capabilities": service_meta.get("capabilities"),
                "maxRecordCount": service_meta.get("maxRecordCount"),
                "supportedQueryFormats": service_meta.get("supportedQueryFormats"),
                "supportsQuery": service_meta.get("supportsQuery"),
                "layers": [
                    {
                        "id": layer.get("id"),
                        "name": layer.get("name"),
                        "type": layer.get("type"),
                        "geometryType": layer.get("geometryType"),
                    }
                    for layer in service_meta.get("layers", [])
                ],
                "tables": [
                    {
                        "id": table.get("id"),
                        "name": table.get("name"),
                    }
                    for table in service_meta.get("tables", [])
                ],
                "fullExtent": service_meta.get("fullExtent"),
                "spatialReference": service_meta.get("spatialReference"),
            }
    
    return enriched


def enrich_results_parallel(items: list[dict], max_workers: int = 10) -> list[dict]:
    """
    Enrich multiple results in parallel.
    
    Args:
        items: List of portal search result items
        max_workers: Number of parallel threads
    
    Returns:
        List of enriched items
    """
    enriched = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(enrich_result, item): item for item in items}
        for future in as_completed(futures):
            try:
                result = future.result()
                enriched.append(result)
            except Exception as e:
                print(f"Error enriching item: {e}")
    
    return enriched


def summarize_results(items: list[dict]) -> dict:
    """
    Generate summary statistics for a set of results.
    
    Args:
        items: List of (enriched) result items
    
    Returns:
        Summary statistics dict
    """
    total = len(items)
    with_url = sum(1 for item in items if item.get("url"))
    with_service = sum(1 for item in items if item.get("service"))
    
    # Count by type
    types = {}
    for item in items:
        t = item.get("type", "Unknown")
        types[t] = types.get(t, 0) + 1
    
    # Count layers
    total_layers = sum(
        len(item.get("service", {}).get("layers", []))
        for item in items
    )
    
    # Services with Query capability
    query_capable = sum(
        1 for item in items
        if item.get("service", {}).get("capabilities")
        and "Query" in item.get("service", {}).get("capabilities", "")
    )
    
    # Tag frequency
    all_tags = []
    for item in items:
        all_tags.extend(item.get("tags", []))
    tag_counts = {}
    for tag in all_tags:
        tag_lower = tag.lower()
        tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return {
        "total_results": total,
        "with_url": with_url,
        "with_service_metadata": with_service,
        "query_capable": query_capable,
        "total_layers": total_layers,
        "by_type": types,
        "top_tags": dict(top_tags),
    }


def save_results(data: dict | list, filename: str) -> Path:
    """
    Save results to a JSON file in the output directory.
    
    Args:
        data: Data to save
        filename: Output filename (will be placed in sample_output/)
    
    Returns:
        Path to saved file
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    
    return output_path


# Predefined query configurations to explore
SAMPLE_QUERIES = {
    "open_data_features": {
        "query": 'type:"Feature Service" AND access:public AND (tags:"open data" OR tags:"opendata")',
        "description": "Public Feature Services tagged as open data"
    },
    "parcels": {
        "query": 'type:"Feature Service" AND access:public AND (title:parcel OR tags:parcel)',
        "description": "Parcel-related Feature Services"
    },
    "zoning": {
        "query": 'type:"Feature Service" AND access:public AND (title:zoning OR tags:zoning)',
        "description": "Zoning-related Feature Services"
    },
    "boundaries": {
        "query": 'type:"Feature Service" AND access:public AND (tags:boundaries OR tags:boundary)',
        "description": "Boundary/administrative Feature Services"
    },
    "elections": {
        "query": 'type:"Feature Service" AND access:public AND (tags:election OR tags:voting OR title:precinct)',
        "description": "Election/voting related Feature Services"
    },
    "infrastructure": {
        "query": 'type:"Feature Service" AND access:public AND (tags:infrastructure OR tags:utilities)',
        "description": "Infrastructure and utilities Feature Services"
    },
    "environment": {
        "query": 'type:"Feature Service" AND access:public AND (tags:environment OR tags:environmental)',
        "description": "Environmental Feature Services"
    },
    "government": {
        "query": 'type:"Feature Service" AND access:public AND (tags:government OR tags:municipal OR tags:"local government")',
        "description": "General government Feature Services"
    },
    "crime": {
        "query": 'type:"Feature Service" AND access:public AND (tags:crime OR tags:police OR title:crime OR title:"public safety")',
        "description": "Crime and public safety Feature Services"
    },
    "law_enforcement": {
        "query": 'type:"Feature Service" AND access:public AND (tags:"law enforcement" OR tags:sheriff OR tags:incidents)',
        "description": "Law enforcement Feature Services"
    },
    "military": {
        "query": 'type:"Feature Service" AND access:public AND (tags:military OR tags:defense OR tags:DoD OR title:"military")',
        "description": "Military and defense Feature Services"
    },
    "aviation": {
        "query": 'type:"Feature Service" AND access:public AND (tags:aviation OR tags:airport OR tags:airspace OR title:airport)',
        "description": "Aviation and airports Feature Services"
    },
    "utilities": {
        "query": 'type:"Feature Service" AND access:public AND (tags:utilities OR tags:utility OR tags:water OR tags:sewer OR tags:stormwater)',
        "description": "Utilities Feature Services"
    },
    "transportation": {
        "query": 'type:"Feature Service" AND access:public AND (tags:transportation OR tags:transit OR tags:rail OR tags:"bus routes")',
        "description": "Transportation and transit Feature Services"
    },
    "health": {
        "query": 'type:"Feature Service" AND access:public AND (tags:health OR tags:hospital OR tags:clinic OR title:hospital)',
        "description": "Health and medical Feature Services"
    },
    "education": {
        "query": 'type:"Feature Service" AND access:public AND (tags:education OR tags:schools OR tags:"school district" OR title:school)',
        "description": "Education and schools Feature Services"
    },
    "demographics": {
        "query": 'type:"Feature Service" AND access:public AND (tags:census OR tags:demographics OR tags:population)',
        "description": "Demographics and census Feature Services"
    },
    "emergency": {
        "query": 'type:"Feature Service" AND access:public AND (tags:"fire station" OR tags:EMS OR tags:"emergency services" OR title:"fire station")',
        "description": "Emergency services Feature Services"
    },
    "addresses": {
        "query": 'type:"Feature Service" AND access:public AND (tags:addresses OR tags:"address points" OR title:"address points")',
        "description": "Address points Feature Services"
    },
    "permits": {
        "query": 'type:"Feature Service" AND access:public AND (tags:permits OR tags:"building permits" OR title:permits)',
        "description": "Permits and licensing Feature Services"
    },
}


def run_exploration(
    query_key: str = "open_data_features",
    max_results: int = 50,
    enrich: bool = True
) -> dict:
    """
    Run a complete exploration for a given query.
    
    Args:
        query_key: Key from SAMPLE_QUERIES or a custom query string
        max_results: Maximum results to fetch
        enrich: Whether to fetch service-level metadata (slower but richer)
    
    Returns:
        Exploration results with items and summary
    """
    # Get query config
    if query_key in SAMPLE_QUERIES:
        config = SAMPLE_QUERIES[query_key]
        query = config["query"]
        description = config["description"]
    else:
        query = query_key
        description = "Custom query"
    
    print(f"\n{'='*60}")
    print(f"Query: {description}")
    print(f"{'='*60}")
    print(f"Search string: {query}")
    print(f"Max results: {max_results}")
    print()
    
    # Search
    print("Searching ArcGIS Online portal...")
    items = search_all(query, max_results=max_results)
    print(f"Found {len(items)} results")
    
    # Enrich with service metadata
    if enrich and items:
        print(f"Enriching results with service metadata (this may take a moment)...")
        items = enrich_results_parallel(items)
        print("Done enriching")
    
    # Generate summary
    summary = summarize_results(items)
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Total results: {summary['total_results']}")
    print(f"  With URL: {summary['with_url']}")
    print(f"  With service metadata: {summary['with_service_metadata']}")
    print(f"  Query-capable: {summary['query_capable']}")
    print(f"  Total layers: {summary['total_layers']}")
    print(f"\n  By type: {summary['by_type']}")
    print(f"\n  Top tags: {list(summary['top_tags'].keys())[:10]}")
    
    return {
        "query": query,
        "description": description,
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "items": items,
    }


def main():
    """Run exploration on multiple queries and save results."""
    
    print("ArcGIS Online Harvester - Proof of Concept")
    print("=" * 60)
    
    # Run a few different queries to see what's out there
    queries_to_run = ["open_data_features", "parcels", "zoning"]
    
    all_results = {}
    
    for query_key in queries_to_run:
        results = run_exploration(query_key, max_results=50, enrich=True)
        all_results[query_key] = results
        
        # Save individual results
        filename = f"{query_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = save_results(results, filename)
        print(f"\nSaved to: {path}")
    
    # Save combined results
    combined_path = save_results(
        all_results,
        f"combined_exploration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    print(f"\nCombined results saved to: {combined_path}")
    
    # Print some interesting examples
    print("\n" + "=" * 60)
    print("Sample services discovered:")
    print("=" * 60)
    
    for query_key, results in all_results.items():
        print(f"\n--- {results['description']} ---")
        for item in results["items"][:3]:
            print(f"\n  Title: {item.get('title')}")
            print(f"  Owner: {item.get('owner')}")
            print(f"  URL: {item.get('url')}")
            print(f"  Views: {item.get('numViews')}")
            if item.get("service"):
                layers = item["service"].get("layers", [])
                print(f"  Layers: {len(layers)}")
                if layers:
                    print(f"    - {', '.join(l['name'] for l in layers[:3])}")


if __name__ == "__main__":
    main()
