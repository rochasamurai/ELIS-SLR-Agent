"""
wos_harvest.py
Harvests metadata from the Clarivate Web of Science Starter API.

CONFIGURATION MODES:
1. NEW (Recommended): --search-config config/searches/electoral_integrity_search.yml
   - Uses dedicated search configuration files
   - Supports tier-based max_results (testing/pilot/benchmark/production/exhaustive)
   - Project-specific settings

2. LEGACY (Backwards Compatible): Reads from config/elis_search_queries.yml
   - Maintains compatibility with existing workflows
   - Uses global max_results_per_source setting

Environment Variables:
- WEB_OF_SCIENCE_API_KEY: Your Clarivate API key

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage Examples:
  # New config format with tier
  python scripts/wos_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # New config format (uses default tier)
  python scripts/wos_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Legacy format (backwards compatible)
  python scripts/wos_harvest.py

  # Override max_results regardless of config
  python scripts/wos_harvest.py --max-results 500
"""

import requests
import json
import os
import yaml
import argparse
import time
import traceback
from pathlib import Path


def get_credentials():
    """Get and validate Web of Science API credentials."""
    api_key = os.getenv("WEB_OF_SCIENCE_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing WEB_OF_SCIENCE_API_KEY environment variable")
    return api_key


def get_headers():
    """Build Web of Science API headers with credentials."""
    api_key = get_credentials()
    return {
        "X-ApiKey": api_key,
        "Accept": "application/json",
    }

def wos_search(query: str, limit: int = 50, max_results: int = 1000):
    """
    Send a query to Web of Science Starter API and retrieve up to max_results.

    Args:
        query (str): WoS query string (should include TS= wrapper for topic search)
        limit (int): Number of records per request (max 50 for Starter API)
        max_results (int): Total number of results to retrieve

    Returns:
        list: List of metadata entries returned by Web of Science
    """
    # Web of Science Starter API endpoint
    url = "https://api.clarivate.com/apis/wos-starter/v1/documents"
    results = []
    page = 1
    retry_count = 0
    max_retries = 5

    # Cache headers once before the loop (avoids repeated get_credentials calls)
    headers = get_headers()

    while len(results) < max_results:
        params = {
            "db": "WOS",
            "q": query,
            "limit": min(limit, max_results - len(results)),
            "page": page,
        }

        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)

            if r.status_code == 429:
                retry_count += 1
                if retry_count > max_retries:
                    print(f"  Max retries ({max_retries}) exceeded due to rate limiting. Stopping.")
                    break
                # Rate limited - back off and retry with exponential backoff
                wait_time = 5 * retry_count
                print(f"  Rate limited (429). Waiting {wait_time}s before retry ({retry_count}/{max_retries})...")
                time.sleep(wait_time)
                continue

            if r.status_code != 200:
                print(f"  Error {r.status_code}: {r.text[:200]}")
                break

            # Reset retry count after successful request
            retry_count = 0

            data = r.json()

            # Starter API returns hits in different structure
            hits = data.get("hits", [])

            if not hits:
                break

            results.extend(hits)

            # Check if there are more results
            metadata = data.get("metadata", {})
            total = metadata.get("total", 0)

            if len(results) >= total:
                print(f"  Retrieved all {total} available results")
                break

            page += 1

            # Rate limiting - be polite
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            break

    return results


def transform_wos_entry(entry):
    """
    Transform raw WoS Starter API entry to match the schema used by other sources.
    """
    # Extract title (directly available)
    title = entry.get("title", "") or ""

    # Extract authors from names.authors structure
    names = entry.get("names", {}) or {}
    authors_data = names.get("authors", [])
    if isinstance(authors_data, list):
        authors = ", ".join([a.get("displayName", "") or a.get("wosStandard", "") or "" for a in authors_data])
    else:
        authors = ""

    # Extract year from source.publishYear
    source_info = entry.get("source", {}) or {}
    year = str(source_info.get("publishYear", "") or "")

    # Extract identifiers
    identifiers = entry.get("identifiers", {}) or {}
    doi = identifiers.get("doi", "") or ""
    uid = entry.get("uid", "") or ""

    # Abstract not available in Starter API basic response
    abstract = ""

    # Extract source title
    source_title = source_info.get("sourceTitle", "") or ""

    return {
        "source": "Web of Science",
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "abstract": abstract,
        "url": f"https://www.webofscience.com/wos/woscc/full-record/{uid}" if uid else "",
        "wos_id": uid,
        "source_title": source_title,
        "raw_metadata": entry,
    }


def load_config(config_path: str):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_wos_queries_legacy(config):
    """
    Extract enabled queries for Web of Science from legacy config format.
    
    Args:
        config: Legacy config dict from config/elis_search_queries.yml
        
    Returns:
        list: List of WoS queries wrapped in TS=()
    """
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "web_of_science" not in sources:
            continue

        # WoS requires TS=() wrapper for topic search
        topic_queries = topic.get("queries", [])
        # Wrap each query in TS=() to search title, abstract, and keywords
        wos_queries = [f"TS=({q})" for q in topic_queries]
        queries.extend(wos_queries)

    return queries


def get_wos_config_new(config, tier=None):
    """
    Extract Web of Science configuration from new search config format.
    
    Args:
        config: New search config dict from config/searches/*.yml
        tier: Optional tier override (testing/pilot/benchmark/production/exhaustive)
        
    Returns:
        tuple: (queries, max_results)
    """
    # Find Web of Science database configuration
    databases = config.get("databases", [])
    wos_config = None
    
    for db in databases:
        if db.get("name") == "Web of Science" and db.get("enabled", False):
            wos_config = db
            break
    
    if not wos_config:
        print("⚠️  Web of Science not enabled in search configuration")
        return [], 0
    
    # Get query and wrap in TS=()
    query_string = config.get("query", {}).get("boolean_string", "")
    if not query_string:
        print("⚠️  No query found in search configuration")
        return [], 0
    
    # Apply WoS-specific wrapper
    query_wrapper = wos_config.get("query_wrapper", "TS=({query})")
    wos_query = query_wrapper.replace("{query}", query_string)
    
    # Determine max_results based on tier
    max_results_config = wos_config.get("max_results")
    
    if isinstance(max_results_config, dict):
        # Tier-based system
        if tier:
            max_results = max_results_config.get(tier)
            if max_results is None:
                print(f"⚠️  Unknown tier '{tier}', available tiers: {list(max_results_config.keys())}")
                tier = wos_config.get("max_results_default", "production")
                max_results = max_results_config.get(tier, 1000)
                print(f"   Using default tier: {tier}")
        else:
            # Use default tier
            tier = wos_config.get("max_results_default", "production")
            max_results = max_results_config.get(tier, 1000)
            print(f"Using default tier: {tier} (max_results: {max_results})")
    else:
        # Single value (backwards compatible)
        max_results = max_results_config or 1000
    
    return [wos_query], max_results


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Harvest metadata from Web of Science API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use new search config with production tier
  python scripts/wos_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # Use new search config with default tier
  python scripts/wos_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Use legacy config (backwards compatible)
  python scripts/wos_harvest.py

  # Override max_results
  python scripts/wos_harvest.py --search-config config/searches/electoral_integrity_search.yml --max-results 500
        """
    )
    
    parser.add_argument(
        "--search-config",
        type=str,
        help="Path to search configuration file (e.g., config/searches/electoral_integrity_search.yml)"
    )
    
    parser.add_argument(
        "--tier",
        type=str,
        choices=["testing", "pilot", "benchmark", "production", "exhaustive"],
        help="Max results tier to use (testing/pilot/benchmark/production/exhaustive)"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        help="Override max_results regardless of config or tier"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="json_jsonl/ELIS_Appendix_A_Search_rows.json",
        help="Output file path (default: json_jsonl/ELIS_Appendix_A_Search_rows.json)"
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()
    
    # Determine configuration mode
    if args.search_config:
        # NEW CONFIG FORMAT
        print(f"Loading search configuration from {args.search_config}")
        config = load_config(args.search_config)
        queries, max_results = get_wos_config_new(config, tier=args.tier)
        config_mode = "NEW"
    else:
        # LEGACY CONFIG FORMAT
        print("Loading configuration from config/elis_search_queries.yml (legacy mode)")
        config = load_config("config/elis_search_queries.yml")
        queries = get_wos_queries_legacy(config)
        max_results = config.get("global", {}).get("max_results_per_source", 100)
        config_mode = "LEGACY"
        print(f"⚠️  Using legacy config format. Consider using --search-config for new projects.")
    
    # Apply max_results override if provided
    if args.max_results:
        print(f"Overriding max_results: {max_results} -> {args.max_results}")
        max_results = args.max_results

    # Validate queries
    if not queries:
        print("⚠️  No Web of Science queries found in config")
        print("   Check that Web of Science is enabled and queries are defined")
        exit(1)  # Exit with error code - missing queries indicates misconfiguration
    
    print(f"\n{'='*80}")
    print(f"WEB OF SCIENCE HARVEST - {config_mode} CONFIG")
    print(f"{'='*80}")
    print(f"Queries: {len(queries)}")
    print(f"Max results per query: {max_results}")
    print(f"Output: {args.output}")
    print(f"{'='*80}\n")

    # Define output path
    output_path = Path(args.output)

    # Load existing results if file exists
    existing_results = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing_results = json.load(f)
        print(f"Loaded {len(existing_results)} existing results")

    # Track existing DOIs and WoS IDs to avoid duplicates
    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    existing_wos_ids = {r.get("wos_id") for r in existing_results if r.get("wos_id")}
    new_count = 0

    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying Web of Science:")
        print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        try:
            raw_results = wos_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_wos_entry(entry)
                doi = transformed.get("doi")
                wos_id = transformed.get("wos_id")

                # Add if unique (check both DOI and WoS ID)
                is_duplicate = False
                if doi and doi in existing_dois:
                    is_duplicate = True
                if wos_id and wos_id in existing_wos_ids:
                    is_duplicate = True
                
                if not is_duplicate:
                    existing_results.append(transformed)
                    if doi:
                        existing_dois.add(doi)
                    if wos_id:
                        existing_wos_ids.add(wos_id)
                    new_count += 1

        except Exception as e:
            print(f"  ❌ Error processing query: {e}")
            traceback.print_exc()
            continue

    # Save combined results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print("✅ Web of Science harvest complete")
    print(f"{'='*80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {output_path}")
    print(f"{'='*80}\n")
    