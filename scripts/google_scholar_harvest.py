"""
google_scholar_harvest.py
Harvests metadata from Google Scholar via Apify API.
Reads queries from config/elis_search_queries.yml (protocol-aligned).

Environment Variables:
- APIFY_API_TOKEN: Your Apify API token (required)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage:
- Called by CI/CD workflow to retrieve search results for configured queries
"""

import os
import json
import time
import yaml
import requests
from pathlib import Path


def get_credentials():
    """Get and validate Apify API credentials."""
    api_token = os.getenv("APIFY_API_TOKEN")
    
    if not api_token:
        raise EnvironmentError("Missing APIFY_API_TOKEN environment variable")
    
    return api_token


def google_scholar_search(query: str, max_items: int = 200, start_year: int = None, end_year: int = None):
    """
    Search Google Scholar via Apify scraper (async with polling).
    
    Args:
        query (str): Search query string
        max_items (int): Maximum number of results to retrieve
        start_year (int): Start year for date filter
        end_year (int): End year for date filter
    
    Returns:
        list: List of search results from Google Scholar
    """
    api_token = get_credentials()
    
    # 1. START THE RUN
    start_url = "https://api.apify.com/v2/acts/marco.gullo~google-scholar-scraper/runs"
    params = {"token": api_token}
    
    payload = {
        "keyword": query,
        "maxItems": max_items,
        "filter": "all",
        "sortBy": "relevance",
        "articleType": "any",
        "proxyOptions": {"useApifyProxy": True},
    }
    
    # Add year filters if provided
    if start_year:
        payload["newerThan"] = start_year
    if end_year:
        payload["olderThan"] = end_year
    
    print(f"\n🔍 Searching Google Scholar via Apify...")
    print(f"   Query: {query}")
    print(f"   Max items: {max_items}")
    if start_year:
        print(f"   Start year: {start_year}")
    if end_year:
        print(f"   End year: {end_year}")
    
    try:
        # Start the run
        print("  Starting Apify run...")
        response = requests.post(start_url, params=params, json=payload, timeout=30)
        response.raise_for_status()
        
        run_info = response.json()
        run_id = run_info["data"]["id"]
        dataset_id = run_info["data"]["defaultDatasetId"]
        
        print(f"  Run started: {run_id}")
        print("  Waiting for completion...")
        
        # 2. POLL FOR COMPLETION
        max_wait = 600  # 10 minutes max (increased for Google Scholar)
        waited = 0
        retry_count = 0
        max_retries = 3
        
        while waited < max_wait:
            time.sleep(10)  # Check every 10 seconds
            waited += 10
            
            # Check run status
            status_url = f"https://api.apify.com/v2/acts/marco.gullo~google-scholar-scraper/runs/{run_id}"
            
            try:
                status_resp = requests.get(status_url, params=params, timeout=30)
                status_resp.raise_for_status()
                retry_count = 0  # Reset on success
                
            except requests.exceptions.HTTPError as e:
                if e.response and e.response.status_code == 502:
                    retry_count += 1
                    print(f"  ⚠️ Apify gateway error (502), retry {retry_count}/{max_retries}...")
                    if retry_count < max_retries:
                        time.sleep(5)
                        continue
                    else:
                        print("  ❌ Max retries reached")
                        return []
                else:
                    print(f"  ❌ HTTP Error: {e}")
                    return []
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️ Request error: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)
                    continue
                else:
                    return []
            
            status_data = status_resp.json()
            status = status_data["data"]["status"]
            
            if status == "SUCCEEDED":
                print(f"  ✓ Run completed after {waited}s")
                break
            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                print(f"  ❌ Run {status}")
                return []
            else:
                print(f"  ⏳ Status: {status} ({waited}s elapsed)")
        
        if status != "SUCCEEDED":
            print("  ⚠️ Timeout waiting for results")
            return []
        
        # 3. GET RESULTS FROM DATASET
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        dataset_resp = requests.get(dataset_url, params=params, timeout=30)
        dataset_resp.raise_for_status()
        
        results = dataset_resp.json()
        print(f"  ✓ Found {len(results)} results from Google Scholar")
        return results
        
    except requests.exceptions.Timeout:
        print("  ⚠️ Request timeout")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ HTTP Error: {e}")
        return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []


def transform_google_scholar_entry(entry):
    """
    Transform Apify Google Scholar result to standard format.
    """
    # Parse authors - Apify returns as string
    authors_str = entry.get("authors", "")
    
    return {
        "source": "Google Scholar",
        "title": entry.get("title", ""),
        "authors": authors_str,
        "year": str(entry.get("year", "")),
        "doi": None,  # Google Scholar doesn't provide DOI directly
        "abstract": entry.get("searchMatch", ""),
        "url": entry.get("link", ""),
        "pdf_url": entry.get("documentLink"),
        "citation_count": entry.get("citations", 0),
        "google_scholar_id": entry.get("cidCode", ""),
        "raw_metadata": entry,
    }


def load_config(config_path: str = "config/elis_search_queries.yml"):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_google_scholar_queries(config):
    """Extract enabled queries for Google Scholar from config."""
    queries = []
    
    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue
        
        sources = topic.get("sources", [])
        if "google_scholar" not in sources:
            continue
        
        topic_queries = topic.get("queries", [])
        # Remove quotes for Google Scholar search
        gs_queries = [q.replace('"', '') for q in topic_queries]
        queries.extend(gs_queries)
    
    return queries


if __name__ == "__main__":
    # Load configuration
    print("Loading configuration from config/elis_search_queries.yml")
    config = load_config()
    
    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 200)
    year_from = global_config.get("year_from")
    year_to = global_config.get("year_to")
    
    # Get Google Scholar queries
    queries = get_google_scholar_queries(config)
    
    if not queries:
        print("⚠️  No Google Scholar queries found in config (check sources and enabled flags)")
        exit(0)
    
    print(f"Found {len(queries)} queries for Google Scholar")
    
    # Define output path
    output_path = Path("json_jsonl/ELIS_Appendix_A_Search_rows.json")
    
    # Load existing results if file exists
    existing_results = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing_results = json.load(f)
        print(f"Loaded {len(existing_results)} existing results")
    
    # Track existing titles to avoid duplicates (Google Scholar doesn't have DOIs)
    existing_titles = {r.get("title", "").lower().strip() for r in existing_results if r.get("title")}
    new_count = 0
    
    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying Google Scholar: {query}")
        
        try:
            raw_results = google_scholar_search(
                query, 
                max_items=max_results,
                start_year=year_from,
                end_year=year_to
            )
            print(f"  Retrieved {len(raw_results)} results")
            
            # Transform and add results
            for entry in raw_results:
                transformed = transform_google_scholar_entry(entry)
                title = transformed.get("title", "").lower().strip()
                
                if title and title not in existing_titles:
                    existing_results.append(transformed)
                    existing_titles.add(title)
                    new_count += 1
        
        except Exception as e:
            print(f"  ❌ Error processing query: {e}")
            continue
    
    # Save combined results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Google Scholar harvest complete")
    print(f"✅ New results added: {new_count}")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to {output_path}")
    