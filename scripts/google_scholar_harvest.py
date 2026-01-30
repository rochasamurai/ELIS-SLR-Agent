"""
google_scholar_harvest.py
Harvests metadata from Google Scholar via Apify API.
Enhanced with comprehensive diagnostics and retry logic.

Environment Variables:
- APIFY_API_TOKEN: Your Apify API token (required)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json
"""

import os
import json
import time
import yaml
import requests
from pathlib import Path
from datetime import datetime


def get_credentials():
    """Get and validate Apify API credentials."""
    api_token = os.getenv("APIFY_API_TOKEN")
    
    if not api_token:
        raise EnvironmentError("Missing APIFY_API_TOKEN environment variable")
    
    return api_token


def check_apify_account_status(api_token):
    """Check Apify account status and credits."""
    try:
        url = "https://api.apify.com/v2/users/me"
        params = {"token": api_token}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        user_data = response.json()
        user_info = user_data.get("data", {})
        
        print("📊 APIFY ACCOUNT STATUS:")
        print(f"   User ID: {user_info.get('id', 'N/A')}")
        print(f"   Username: {user_info.get('username', 'N/A')}")
        print(f"   Credits: ${user_info.get('usageCredits', {}).get('remaining', 'N/A'):.2f}")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not check account status: {e}")
        return False


def google_scholar_search(query: str, max_items: int = 200, start_year: int = None, end_year: int = None, retry_count: int = 0, max_retries: int = 2):
    """
    Search Google Scholar via Apify scraper with enhanced diagnostics.
    """
    api_token = get_credentials()
    
    # Check account status
    if retry_count == 0:  # Only check on first attempt
        check_apify_account_status(api_token)
    
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
    
    if start_year:
        payload["newerThan"] = start_year
    if end_year:
        payload["olderThan"] = end_year
    
    print(f"\n🔍 GOOGLE SCHOLAR SEARCH (Attempt {retry_count + 1}/{max_retries + 1})")
    print(f"   Query: {query}")
    print(f"   Max items: {max_items}")
    if start_year:
        print(f"   Start year: {start_year}")
    if end_year:
        print(f"   End year: {end_year}")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Start the run
        print("\n  📤 Starting Apify run...")
        response = requests.post(start_url, params=params, json=payload, timeout=30)
        response.raise_for_status()
        
        run_info = response.json()
        run_data = run_info.get("data", {})
        run_id = run_data.get("id")
        dataset_id = run_data.get("defaultDatasetId")
        status = run_data.get("status")
        
        print(f"  ✓ Run created successfully")
        print(f"    Run ID: {run_id}")
        print(f"    Dataset ID: {dataset_id}")
        print(f"    Initial status: {status}")
        print(f"    Run URL: https://console.apify.com/actors/runs/{run_id}")
        
        # 2. POLL FOR COMPLETION
        max_wait = 600  # 10 minutes max
        check_interval = 10  # Check every 10 seconds
        waited = 0
        status_retry_count = 0
        max_status_retries = 3
        
        print("\n  ⏳ Polling for completion...")
        
        while waited < max_wait:
            time.sleep(check_interval)
            waited += check_interval
            
            # Check run status
            status_url = f"https://api.apify.com/v2/acts/marco.gullo~google-scholar-scraper/runs/{run_id}"
            
            try:
                status_resp = requests.get(status_url, params=params, timeout=30)
                status_resp.raise_for_status()
                status_retry_count = 0  # Reset on success
                
            except requests.exceptions.HTTPError as e:
                status_retry_count += 1
                print(f"  ⚠️  Status check error (attempt {status_retry_count}/{max_status_retries}): {e}")
                
                if status_retry_count >= max_status_retries:
                    print(f"  ❌ Max status check retries reached")
                    
                    # Try to abort the run
                    try:
                        abort_url = f"https://api.apify.com/v2/acts/marco.gullo~google-scholar-scraper/runs/{run_id}/abort"
                        requests.post(abort_url, params=params, timeout=10)
                        print(f"  🛑 Run aborted")
                    except:
                        pass
                    
                    # Retry the entire search if we haven't exceeded max retries
                    if retry_count < max_retries:
                        print(f"\n  🔄 Retrying entire search...")
                        time.sleep(30)  # Wait before retry
                        return google_scholar_search(query, max_items, start_year, end_year, retry_count + 1, max_retries)
                    else:
                        return []
                
                time.sleep(5)
                continue
            
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️  Network error: {e}")
                status_retry_count += 1
                if status_retry_count >= max_status_retries:
                    if retry_count < max_retries:
                        print(f"\n  🔄 Retrying entire search...")
                        time.sleep(30)
                        return google_scholar_search(query, max_items, start_year, end_year, retry_count + 1, max_retries)
                    else:
                        return []
                time.sleep(5)
                continue
            
            status_data = status_resp.json()
            status_info = status_data.get("data", {})
            status = status_info.get("status")
            stats = status_info.get("stats", {})
            
            # Show progress
            compute_units = stats.get("computeUnits", 0)
            if waited % 30 == 0 or status not in ["RUNNING", "READY"]:  # Every 30s or on status change
                print(f"    [{waited}s] Status: {status} | Compute units: {compute_units:.4f}")
            
            if status == "SUCCEEDED":
                print(f"\n  ✅ Run completed successfully after {waited}s")
                print(f"     Total compute units: {compute_units:.4f}")
                print(f"     Estimated cost: ${compute_units * 0.25:.4f}")
                break
            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                error_msg = status_info.get("statusMessage", "No error message")
                print(f"\n  ❌ Run {status}")
                print(f"     Error: {error_msg}")
                print(f"     Compute units used: {compute_units:.4f}")
                
                # Retry if we haven't exceeded max retries
                if retry_count < max_retries:
                    print(f"\n  🔄 Retrying entire search...")
                    time.sleep(30)
                    return google_scholar_search(query, max_items, start_year, end_year, retry_count + 1, max_retries)
                else:
                    return []
        
        if status != "SUCCEEDED":
            print(f"\n  ⏰ Timeout after {max_wait}s (status: {status})")
            
            # Try to abort the run
            try:
                abort_url = f"https://api.apify.com/v2/acts/marco.gullo~google-scholar-scraper/runs/{run_id}/abort"
                requests.post(abort_url, params=params, timeout=10)
                print(f"  🛑 Run aborted")
            except:
                pass
            
            # Retry if we haven't exceeded max retries
            if retry_count < max_retries:
                print(f"\n  🔄 Retrying entire search...")
                time.sleep(30)
                return google_scholar_search(query, max_items, start_year, end_year, retry_count + 1, max_retries)
            else:
                return []
        
        # 3. GET RESULTS FROM DATASET
        print(f"\n  📥 Retrieving results from dataset...")
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        
        dataset_resp = requests.get(dataset_url, params=params, timeout=30)
        dataset_resp.raise_for_status()
        
        results = dataset_resp.json()
        
        print(f"  ✅ Retrieved {len(results)} results from Google Scholar")
        
        if len(results) == 0:
            print(f"  ⚠️  WARNING: 0 results returned (query may be too restrictive)")
        
        return results
        
    except requests.exceptions.Timeout:
        print(f"  ❌ Request timeout")
        if retry_count < max_retries:
            print(f"\n  🔄 Retrying...")
            time.sleep(30)
            return google_scholar_search(query, max_items, start_year, end_year, retry_count + 1, max_retries)
        return []
        
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ HTTP Error: {e}")
        print(f"     Response: {e.response.text if e.response else 'No response'}")
        if retry_count < max_retries:
            print(f"\n  🔄 Retrying...")
            time.sleep(30)
            return google_scholar_search(query, max_items, start_year, end_year, retry_count + 1, max_retries)
        return []
        
    except Exception as e:
        print(f"  ❌ Unexpected error: {type(e).__name__}: {e}")
        if retry_count < max_retries:
            print(f"\n  🔄 Retrying...")
            time.sleep(30)
            return google_scholar_search(query, max_items, start_year, end_year, retry_count + 1, max_retries)
        return []


def transform_google_scholar_entry(entry):
    """Transform Apify Google Scholar result to standard format."""
    authors_str = entry.get("authors", "")
    
    return {
        "source": "Google Scholar",
        "title": entry.get("title", ""),
        "authors": authors_str,
        "year": str(entry.get("year", "")),
        "doi": None,
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
        gs_queries = [q.replace('"', '') for q in topic_queries]
        queries.extend(gs_queries)
    
    return queries


if __name__ == "__main__":
    print("="*80)
    print("GOOGLE SCHOLAR HARVEST - ENHANCED DIAGNOSTICS")
    print("="*80)
    print(f"Start time: {datetime.now().isoformat()}")
    
    # Load configuration
    print("\n📋 Loading configuration...")
    config = load_config()
    
    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 200)
    year_from = global_config.get("year_from")
    year_to = global_config.get("year_to")
    
    print(f"   Max results per source: {max_results}")
    print(f"   Year range: {year_from}-{year_to}")
    
    # Get Google Scholar queries
    queries = get_google_scholar_queries(config)
    
    if not queries:
        print("\n⚠️  No Google Scholar queries found in config")
        print("   Check that:")
        print("   - Topic is enabled: true")
        print("   - Sources includes: google_scholar")
        exit(0)
    
    print(f"\n✓ Found {len(queries)} queries for Google Scholar")
    
    # Define output path
    output_path = Path("json_jsonl/ELIS_Appendix_A_Search_rows.json")
    
    # Load existing results if file exists
    existing_results = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing_results = json.load(f)
        print(f"   Loaded {len(existing_results)} existing results")
    
    # Track existing titles to avoid duplicates
    existing_titles = {r.get("title", "").lower().strip() for r in existing_results if r.get("title")}
    new_count = 0
    
    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY {i}/{len(queries)}")
        print(f"{'='*80}")
        
        try:
            raw_results = google_scholar_search(
                query, 
                max_items=max_results,
                start_year=year_from,
                end_year=year_to
            )
            
            print(f"\n📊 Processing {len(raw_results)} results...")
            
            # Transform and add results
            for entry in raw_results:
                transformed = transform_google_scholar_entry(entry)
                title = transformed.get("title", "").lower().strip()
                
                if title and title not in existing_titles:
                    existing_results.append(transformed)
                    existing_titles.add(title)
                    new_count += 1
        
        except Exception as e:
            print(f"\n❌ Fatal error processing query: {e}")
            continue
    
    # Save combined results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("HARVEST COMPLETE")
    print(f"{'='*80}")
    print(f"✅ New results added: {new_count}")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to: {output_path}")
    print(f"⏱️  End time: {datetime.now().isoformat()}")
    