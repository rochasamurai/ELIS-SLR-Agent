"""
ieee_harvest.py
Harvests metadata from the IEEE Xplore API using the official Python 3 SDK.

CONFIGURATION MODES:
1. NEW (Recommended): --search-config config/searches/electoral_integrity_search.yml
   - Uses dedicated search configuration files
   - Supports tier-based max_results (testing/pilot/benchmark/production/exhaustive)
   - Project-specific settings

2. LEGACY (Backwards Compatible): Reads from config/elis_search_queries.yml
   - Maintains compatibility with existing workflows
   - Uses global max_results_per_source setting

Environment Variables:
- IEEE_EXPLORE_API_KEY: Your IEEE Xplore API key (required)

Dependencies:
- xploreapi/xploreapi.py  (IEEE official SDK — must be in repo)
- pycurl, certifi          (SDK requirements; added to workflow pip install)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage Examples:
  # New config format with tier
  python scripts/ieee_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # New config format (uses default tier)
  python scripts/ieee_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Legacy format (backwards compatible)
  python scripts/ieee_harvest.py

  # Override max_results regardless of config
  python scripts/ieee_harvest.py --max-results 500
"""

import json
import os
import sys
import yaml
import argparse
import time
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
# SDK IMPORT  — works whether script is run from repo root or scripts/
# ---------------------------------------------------------------------------
# Add repo root to path so that xploreapi/ is importable regardless of cwd
_repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_repo_root))
from xploreapi.xploreapi import XPLORE


# ---------------------------------------------------------------------------
# CREDENTIALS
# ---------------------------------------------------------------------------


def get_credentials():
    """Get and validate IEEE Xplore API credentials."""
    api_key = os.getenv("IEEE_EXPLORE_API_KEY")

    if not api_key:
        raise EnvironmentError("Missing IEEE_EXPLORE_API_KEY environment variable")

    return api_key


# ---------------------------------------------------------------------------
# SEARCH (with pagination loop using official SDK)
# ---------------------------------------------------------------------------


def ieee_search(query: str, max_results: int = 1000):
    """
    Send a query to IEEE Xplore via the official SDK and paginate up to max_results.

    The SDK uses pycurl + urllib.parse.quote_plus internally, which is the
    encoding that IEEE's API expects.  Using requests.get(params=...) encodes
    differently and triggers 403 "Developer Inactive" on CI runners.

    IEEE API constraints:
    - max_records per call: 200
    - Pagination via start_record (1-based)
    - Response JSON: articles array; empty array = no more results

    Args:
        query (str): IEEE query string (boolean syntax)
        max_results (int): Total number of results to retrieve

    Returns:
        list: List of article dicts returned by IEEE
    """
    api_key = get_credentials()
    results = []
    start_record = 1  # IEEE is 1-based
    retry_count = 0
    max_retries = 5

    print(f"  SDK endpoint: {XPLORE.endPoint}")
    print(f"  Query:        {query[:120]}{'...' if len(query) > 120 else ''}")
    print(f"  Max:          {max_results}")

    while len(results) < max_results:
        page_size = min(200, max_results - len(results))

        # Instantiate a fresh SDK object per page (it accumulates state)
        xplore = XPLORE(api_key)
        xplore.booleanText(query)
        xplore.maximumResults(page_size)
        xplore.startingResult(start_record)
        xplore.dataFormat("object")  # return parsed JSON dict, not raw string

        try:
            data = xplore.callAPI()

            # SDK returns parsed dict when dataFormat is "object"
            if not isinstance(data, dict):
                print(f"  Unexpected response type: {type(data)}")
                print(f"  Raw (first 300 chars): {str(data)[:300]}")
                break

            # Check for error response
            if "error" in data:
                error_msg = data.get("error", {})
                print(f"  API error: {error_msg}")
                retry_count += 1
                if retry_count > max_retries:
                    print(f"  Max retries ({max_retries}) exceeded. Stopping.")
                    break
                wait_time = 5 * retry_count
                print(
                    f"  Waiting {wait_time}s before retry ({retry_count}/{max_retries})..."
                )
                time.sleep(wait_time)
                continue

            # Reset retry count after successful request
            retry_count = 0

            articles = data.get("articles", [])

            if not articles:
                print(f"  No articles in response. Keys: {list(data.keys())}")
                break

            results.extend(articles)
            print(
                f"  Page {start_record}: {len(articles)} articles (running total: {len(results)})"
            )

            # Advance start_record for next page
            start_record += len(articles)

            # Rate limiting - 10 calls/sec allowed, but be polite
            time.sleep(0.5)

        except Exception as e:
            print(f"  SDK call failed: {e}")
            traceback.print_exc()
            retry_count += 1
            if retry_count > max_retries:
                print(f"  Max retries ({max_retries}) exceeded. Stopping.")
                break
            wait_time = 5 * retry_count
            print(
                f"  Waiting {wait_time}s before retry ({retry_count}/{max_retries})..."
            )
            time.sleep(wait_time)
            continue

    return results


# ---------------------------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------------------------


def transform_ieee_entry(entry):
    """
    Transform raw IEEE Xplore entry to match the schema used by other sources.
    """
    # Extract authors (as array for schema compliance)
    authors_data = entry.get("authors", {}) or {}
    authors_list = authors_data.get("authors", []) or []
    authors = [a.get("full_name", "") for a in authors_list if a.get("full_name")]

    # Extract publication year (as integer for schema compliance)
    year_raw = entry.get("publication_year")
    year = None
    if year_raw:
        try:
            year = int(year_raw)
        except (ValueError, TypeError):
            year = None

    return {
        "source": "IEEE Xplore",
        "title": entry.get("title", "") or "",
        "authors": authors,
        "year": year,
        "doi": entry.get("doi", "") or "",
        "abstract": entry.get("abstract", "") or "",
        "url": entry.get("pdf_url", "") or entry.get("html_url", "") or "",
        "ieee_id": entry.get("article_number", "") or "",
        "raw_metadata": entry,
    }


# ---------------------------------------------------------------------------
# CONFIG LOADING — LEGACY
# ---------------------------------------------------------------------------


def load_config(config_path: str):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_ieee_queries_legacy(config):
    """
    Extract enabled queries for IEEE from legacy config format.

    Args:
        config: Legacy config dict from config/elis_search_queries.yml

    Returns:
        list: List of IEEE queries (no wrapper needed — generic syntax)
    """
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "ieee_xplore" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        queries.extend(topic_queries)

    return queries


# ---------------------------------------------------------------------------
# CONFIG LOADING — NEW (tier-based)
# ---------------------------------------------------------------------------


def get_ieee_config_new(config, tier=None):
    """
    Extract IEEE configuration from new search config format.

    Args:
        config: New search config dict from config/searches/*.yml
        tier: Optional tier override (testing/pilot/benchmark/production/exhaustive)

    Returns:
        tuple: (queries, max_results)
    """
    # Find IEEE Xplore database configuration
    databases = config.get("databases", [])
    ieee_config = None

    for db in databases:
        if db.get("name") == "IEEE Xplore" and db.get("enabled", False):
            ieee_config = db
            break

    if not ieee_config:
        print("[WARNING] IEEE Xplore not enabled in search configuration")
        return [], 0

    # Get query — IEEE uses generic syntax, no wrapper required
    query_string = config.get("query", {}).get("boolean_string", "")
    if not query_string:
        print("[WARNING] No query found in search configuration")
        return [], 0

    # Apply wrapper if one is defined in config, otherwise use raw query
    query_wrapper = ieee_config.get("query_wrapper", "{query}")
    ieee_query = query_wrapper.replace("{query}", query_string)

    # Determine max_results based on tier
    max_results_config = ieee_config.get("max_results")

    if isinstance(max_results_config, dict):
        # Tier-based system
        if tier:
            max_results = max_results_config.get(tier)
            if max_results is None:
                print(
                    f"[WARNING] Unknown tier '{tier}', available tiers: {list(max_results_config.keys())}"
                )
                tier = ieee_config.get("max_results_default", "production")
                max_results = max_results_config.get(tier, 1000)
                print(f"   Using default tier: {tier}")
        else:
            # Use default tier
            tier = ieee_config.get("max_results_default", "production")
            max_results = max_results_config.get(tier, 1000)
            print(f"Using default tier: {tier} (max_results: {max_results})")
    else:
        # Single value (backwards compatible)
        max_results = max_results_config or 1000

    return [ieee_query], max_results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Harvest metadata from IEEE Xplore API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use new search config with production tier
  python scripts/ieee_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # Use new search config with default tier
  python scripts/ieee_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Use legacy config (backwards compatible)
  python scripts/ieee_harvest.py

  # Override max_results
  python scripts/ieee_harvest.py --search-config config/searches/electoral_integrity_search.yml --max-results 500
        """,
    )

    parser.add_argument(
        "--search-config",
        type=str,
        help="Path to search configuration file (e.g., config/searches/electoral_integrity_search.yml)",
    )

    parser.add_argument(
        "--tier",
        type=str,
        choices=["testing", "pilot", "benchmark", "production", "exhaustive"],
        help="Max results tier to use (testing/pilot/benchmark/production/exhaustive)",
    )

    parser.add_argument(
        "--max-results",
        type=int,
        help="Override max_results regardless of config or tier",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="json_jsonl/ELIS_Appendix_A_Search_rows.json",
        help="Output file path (default: json_jsonl/ELIS_Appendix_A_Search_rows.json)",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()

    # Determine configuration mode
    if args.search_config:
        # NEW CONFIG FORMAT
        print(f"Loading search configuration from {args.search_config}")
        config = load_config(args.search_config)
        queries, max_results = get_ieee_config_new(config, tier=args.tier)
        config_mode = "NEW"
    else:
        # LEGACY CONFIG FORMAT
        print("Loading configuration from config/elis_search_queries.yml (legacy mode)")
        config = load_config("config/elis_search_queries.yml")
        queries = get_ieee_queries_legacy(config)
        max_results = config.get("global", {}).get("max_results_per_source", 1000)
        config_mode = "LEGACY"
        print(
            "[WARNING] Using legacy config format. Consider using --search-config for new projects."
        )

    # Apply max_results override if provided
    if args.max_results:
        print(f"Overriding max_results: {max_results} -> {args.max_results}")
        max_results = args.max_results

    # Validate queries
    if not queries:
        print("[WARNING] No IEEE Xplore queries found in config")
        print("   Check that IEEE Xplore is enabled and queries are defined")
        exit(1)  # Exit with error code - missing queries indicates misconfiguration

    print(f"\n{'='*80}")
    print(f"IEEE XPLORE HARVEST - {config_mode} CONFIG")
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

    # Track existing DOIs and IEEE IDs to avoid duplicates
    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    existing_ieee_ids = {r.get("ieee_id") for r in existing_results if r.get("ieee_id")}
    new_count = 0

    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying IEEE Xplore:")
        print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        try:
            raw_results = ieee_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_ieee_entry(entry)
                doi = transformed.get("doi")
                ieee_id = transformed.get("ieee_id")

                # Add if unique (check both DOI and IEEE article_number)
                is_duplicate = False
                if doi and doi in existing_dois:
                    is_duplicate = True
                if ieee_id and ieee_id in existing_ieee_ids:
                    is_duplicate = True

                if not is_duplicate:
                    existing_results.append(transformed)
                    if doi:
                        existing_dois.add(doi)
                    if ieee_id:
                        existing_ieee_ids.add(ieee_id)
                    new_count += 1

        except Exception as e:
            print(f"  [ERROR] Error processing query: {e}")
            traceback.print_exc()
            continue

    # Save combined results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print("[OK] IEEE Xplore harvest complete")
    print(f"{'='*80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {args.output}")
    print(f"{'='*80}\n")
