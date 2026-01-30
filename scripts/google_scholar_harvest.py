"""
google_scholar_harvest.py
Harvests metadata from Google Scholar via Apify API using official Python client.
Uses easyapi/google-scholar-scraper actor (alternative to avoid rate limits).

Environment Variables:
- APIFY_API_TOKEN: Your Apify API token (required)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json
"""

import os
import json
import yaml
import time
import random
from pathlib import Path
from datetime import datetime
from apify_client import ApifyClient


def get_credentials():
    """Get and validate Apify API credentials."""
    api_token = os.getenv("APIFY_API_TOKEN")
    
    if not api_token:
        raise EnvironmentError("Missing APIFY_API_TOKEN environment variable")
    
    return api_token


def check_apify_account_status(client):
    """Check Apify account status and credits."""
    try:
        user = client.user().get()
        
        print("📊 APIFY ACCOUNT STATUS:")
        print(f"   User ID: {user.get('id', 'N/A')}")
        print(f"   Username: {user.get('username', 'N/A')}")
        
        # Credits might be in different structure
        usage = user.get('usageCredits', {})
        if isinstance(usage, dict):
            remaining = usage.get('remaining', 'N/A')
            print(f"   Credits: ${remaining}")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not check account status: {e}")
        return False


def prepare_google_scholar_query(original_query):
    """
    Convert complex Boolean query to simple format for Google Scholar.
    EasyAPI actor works best with simple keyword queries.
    """
    # Remove quotes and Boolean operators, keep just the keywords
    simple_query = original_query.replace('"', '').replace('(', '').replace(')', '')
    simple_query = simple_query.replace(' AND ', ' ').replace(' OR ', ' ')
    simple_query = ' '.join(simple_query.split())  # Normalize whitespace
    
    return simple_query.strip()


def google_scholar_search(client, query: str, max_items: int = 100, start_year: int = None, end_year: int = None, retry_count: int = 0, max_retries: int = 2):
    """
    Search Google Scholar via Apify using easyapi/google-scholar-scraper actor.
    Note: Free tier limited to 10 results, paid tier up to 5000.
    """
    
    # Add delay between retry attempts
    if retry_count > 0:
        delay = random.uniform(30, 60)
        print(f"\n  ⏸️  Waiting {delay:.0f} seconds before retry...")
        time.sleep(delay)
    
    # Simplify query for better results
    search_query = prepare_google_scholar_query(query)
    
    print(f"\n🔍 GOOGLE SCHOLAR SEARCH (Attempt {retry_count + 1}/{max_retries + 1})")
    print(f"   Actor: easyapi/google-scholar-scraper")
    print(f"   Original: {query}")
    print(f"   Simplified: {search_query}")
    print(f"   Max items: {max_items}")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    
    # Prepare input for EasyAPI actor
    # Note: EasyAPI requires minimum 100 for maxItems (free tier gets 10)
    run_input = {
        "query": search_query,
        "maxItems": max(100, max_items)  # Minimum 100 required
    }
    
    # Note: Year filtering not available in EasyAPI actor
    if start_year or end_year:
        print(f"   ⚠️  Year filtering not supported by EasyAPI actor")
    
    try:
        print("\n  📤 Starting Apify run...")
        
        # Run the actor and wait for it to finish
        run = client.actor("easyapi/google-scholar-scraper").call(run_input=run_input)
        
        print(f"  ✓ Run completed")
        print(f"    Run ID: {run.get('id')}")
        print(f"    Status: {run.get('status')}")
        print(f"    Run URL: https://console.apify.com/actors/runs/{run.get('id')}")
        
        # Get build/run stats
        stats = run.get('stats', {})
        compute_units = stats.get('computeUnits', 0)
        print(f"    Compute units: {compute_units:.4f}")
        print(f"    Estimated cost: ${compute_units * 0.25:.4f}")
        
        # Check if run succeeded
        status = run.get('status')
        if status != 'SUCCEEDED':
            print(f"  ⚠️  Run status: {status}")
            if retry_count < max_retries:
                return google_scholar_search(client, query, max_items, start_year, end_year, retry_count + 1, max_retries)
            return []
        
        # Fetch results from dataset
        print(f"\n  📥 Retrieving results from dataset...")
        dataset_id = run.get('defaultDatasetId')
        
        dataset_client = client.dataset(dataset_id)
        results = list(dataset_client.iterate_items())
        
        print(f"  ✅ Retrieved {len(results)} results from Google Scholar")
        
        if len(results) == 0:
            print(f"  ⚠️  WARNING: 0 results")
            
            if retry_count < max_retries:
                print(f"\n  🔄 Retrying...")
                return google_scholar_search(client, query, max_items, start_year, end_year, retry_count + 1, max_retries)
            else:
                print(f"  ❌ All retries exhausted")
        elif len(results) == 10:
            print(f"  ℹ️  Note: Free tier limited to 10 results")
            print(f"      Upgrade Apify account for up to 5000 results")
        
        return results
        
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {e}")
        
        if retry_count < max_retries:
            print(f"\n  🔄 Retrying...")
            return google_scholar_search(client, query, max_items, start_year, end_year, retry_count + 1, max_retries)
        
        return []


def transform_google_scholar_entry(entry):
    """Transform EasyAPI Google Scholar result to standard format."""
    # EasyAPI returns different field names than marco.gullo
    authors_str = entry.get("authors", "")
    
    return {
        "source": "Google Scholar",
        "title": entry.get("title", ""),
        "authors": authors_str,
        "year": str(entry.get("year", "")),
        "doi": None,  # EasyAPI doesn't provide DOI
        "abstract": entry.get("snippet", ""),  # EasyAPI uses 'snippet'
        "url": entry.get("link", ""),
        "pdf_url": entry.get("pdf_link"),
        "citation_count": entry.get("citations", 0),
        "google_scholar_id": entry.get("result_id", ""),
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
        queries.extend(topic_queries)
    
    return queries


if __name__ == "__main__":
    print("="*80)
    print("GOOGLE SCHOLAR HARVEST - EASYAPI ACTOR")
    print("="*80)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Actor: easyapi/google-scholar-scraper (alternative to avoid rate limits)")
    
    # Initialize Apify client
    api_token = get_credentials()
    client = ApifyClient(api_token)
    
    # Check account status
    check_apify_account_status(client)
    
    # Load configuration
    print("\n📋 Loading configuration...")
    config = load_config()
    
    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 200)
    year_from = global_config.get("year_from")
    year_to = global_config.get("year_to")
    
    print(f"   Max results per source: {max_results}")
    print(f"   Year range: {year_from}-{year_to} (filtering not supported by EasyAPI)")
    
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
                client,
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
    
    if new_count > 0 and new_count <= 10:
        print(f"\nℹ️  FREE TIER NOTE:")
        print(f"   EasyAPI free tier limited to 10 results per run")
        print(f"   For full {max_results} results, upgrade at https://apify.com/pricing")
        