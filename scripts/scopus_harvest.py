"""
scopus_harvest.py
Harvests metadata from the Elsevier Scopus API using institutional token and API key.

CONFIGURATION MODES:
1. NEW (Recommended): --search-config config/searches/electoral_integrity_search.yml
   - Uses dedicated search configuration files
   - Supports tier-based max_results (testing/pilot/benchmark/production/exhaustive)
   - Project-specific settings

2. LEGACY (Backwards Compatible): Reads from config/elis_search_queries.yml
   - Maintains compatibility with existing workflows
   - Uses global max_results_per_source setting

Environment Variables:
- SCOPUS_API_KEY: Your Elsevier API key
- SCOPUS_INST_TOKEN: Institutional token for full access

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage Examples:
  # New config format with tier
  python scripts/scopus_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # New config format (uses default tier)
  python scripts/scopus_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Legacy format (backwards compatible)
  python scripts/scopus_harvest.py

  # Override max_results regardless of config
  python scripts/scopus_harvest.py --max-results 500
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
    """Get and validate Scopus API credentials."""
    api_key = os.getenv("SCOPUS_API_KEY")
    inst_token = os.getenv("SCOPUS_INST_TOKEN")

    if not api_key or not inst_token:
        raise EnvironmentError(
            "Missing SCOPUS_API_KEY or SCOPUS_INST_TOKEN environment variables"
        )

    return api_key, inst_token


def get_headers():
    """Build Scopus API headers with credentials."""
    api_key, inst_token = get_credentials()
    return {
        "X-ELS-APIKey": api_key,
        "X-ELS-Insttoken": inst_token,
        "Accept": "application/json",
    }


def scopus_search(query: str, count: int = 25, max_results: int = 100):
    """
    Send a query to Scopus API and retrieve up to max_results.

    Args:
        query (str): Scopus query string (should include TITLE-ABS-KEY wrapper).
        count (int): Number of records per request (max 25).
        max_results (int): Total number of results to retrieve.

    Returns:
        list: List of metadata entries returned by Scopus.
    """
    url = "https://api.elsevier.com/content/search/scopus"
    results = []
    start = 0
    retry_count = 0
    max_retries = 5

    # Cache headers once before the loop (avoids repeated get_credentials calls)
    headers = get_headers()

    while start < max_results:
        params = {"query": query, "count": count, "start": start}

        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)

            if r.status_code == 429:
                retry_count += 1
                if retry_count > max_retries:
                    print(
                        f"  Max retries ({max_retries}) exceeded due to rate limiting. Stopping."
                    )
                    break
                # Rate limited - back off and retry with exponential backoff
                wait_time = 5 * retry_count
                print(
                    f"  Rate limited (429). Waiting {wait_time}s before retry ({retry_count}/{max_retries})..."
                )
                time.sleep(wait_time)
                continue

            if r.status_code != 200:
                print(f"  Error {r.status_code}: {r.text[:200]}")
                break

            # Reset retry count after successful request
            retry_count = 0

            data = r.json()
            entries = data.get("search-results", {}).get("entry", [])

            if not entries:
                break

            results.extend(entries)
            start += count

            # Stop if we've retrieved all available results
            total_results = int(
                data.get("search-results", {}).get("opensearch:totalResults", 0)
            )
            if len(results) >= total_results:
                print(f"  Retrieved all {total_results} available results")
                break

            # Rate limiting - be polite
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            break

    return results


def transform_scopus_entry(entry):
    """
    Transform raw Scopus entry to match the schema used by other sources.
    """
    # Extract scopus_id safely
    dc_identifier = entry.get("dc:identifier", "") or ""
    scopus_id = dc_identifier.replace("SCOPUS_ID:", "") if dc_identifier else ""

    # Authors: Scopus search API returns dc:creator as string (first author only)
    # Convert to array for schema compliance
    creator = entry.get("dc:creator", "") or ""
    authors = [creator] if creator else []

    # Year: Extract from prism:coverDate (e.g., "2026-01-01") and convert to integer
    year = None
    cover_date = entry.get("prism:coverDate", "")
    if cover_date and len(cover_date) >= 4:
        try:
            year = int(cover_date[:4])
        except (ValueError, TypeError):
            year = None

    return {
        "source": "Scopus",
        "title": entry.get("dc:title", "") or "",
        "authors": authors,
        "year": year,
        "doi": entry.get("prism:doi", "") or "",
        "abstract": entry.get("dc:description", "") or "",
        "url": entry.get("prism:url", "") or "",
        "scopus_id": scopus_id,
        "raw_metadata": entry,
    }


def load_config(config_path: str):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_scopus_queries_legacy(config):
    """
    Extract enabled queries for Scopus from legacy config format.

    Args:
        config: Legacy config dict from config/elis_search_queries.yml

    Returns:
        list: List of Scopus queries wrapped in TITLE-ABS-KEY()
    """
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "scopus" not in sources:
            continue

        # Scopus requires TITLE-ABS-KEY() wrapper for proper field searching
        topic_queries = topic.get("queries", [])
        # Wrap each query in TITLE-ABS-KEY() to search title, abstract, and keywords
        scopus_queries = [f"TITLE-ABS-KEY({q})" for q in topic_queries]
        queries.extend(scopus_queries)

    return queries


def get_scopus_config_new(config, tier=None):
    """
    Extract Scopus configuration from new search config format.

    Args:
        config: New search config dict from config/searches/*.yml
        tier: Optional tier override (testing/pilot/benchmark/production/exhaustive)

    Returns:
        tuple: (queries, max_results)
    """
    # Find Scopus database configuration
    databases = config.get("databases", [])
    scopus_config = None

    for db in databases:
        if db.get("name") == "Scopus" and db.get("enabled", False):
            scopus_config = db
            break

    if not scopus_config:
        print("[WARNING] Scopus not enabled in search configuration")
        return [], 0

    # Get query - Scopus supports boolean syntax, so use boolean_string directly
    query_config = config.get("query", {})
    query_string = query_config.get("boolean_string", "")
    if not query_string:
        print("[WARNING] No query found in search configuration")
        return [], 0

    # Apply Scopus-specific wrapper (TITLE-ABS-KEY for searching title, abstract, keywords)
    query_wrapper = scopus_config.get("query_wrapper", "TITLE-ABS-KEY({query})")
    scopus_query = query_wrapper.replace("{query}", query_string)
    print(f"Query for Scopus:")
    print(f"  Query: {scopus_query[:100]}{'...' if len(scopus_query) > 100 else ''}")

    # Determine max_results based on tier
    max_results_config = scopus_config.get("max_results")

    if isinstance(max_results_config, dict):
        # Tier-based system
        if tier:
            max_results = max_results_config.get(tier)
            if max_results is None:
                print(
                    f"[WARNING] Unknown tier '{tier}', available tiers: {list(max_results_config.keys())}"
                )
                tier = scopus_config.get("max_results_default", "production")
                max_results = max_results_config.get(tier, 1000)
                print(f"   Using default tier: {tier}")
        else:
            # Use default tier
            tier = scopus_config.get("max_results_default", "production")
            max_results = max_results_config.get(tier, 1000)
            print(f"Using default tier: {tier} (max_results: {max_results})")
    else:
        # Single value (backwards compatible)
        max_results = max_results_config or 1000

    return [scopus_query], max_results


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Harvest metadata from Scopus API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use new search config with production tier
  python scripts/scopus_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # Use new search config with default tier
  python scripts/scopus_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Use legacy config (backwards compatible)
  python scripts/scopus_harvest.py

  # Override max_results
  python scripts/scopus_harvest.py --search-config config/searches/electoral_integrity_search.yml --max-results 500
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


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()

    # Determine configuration mode
    if args.search_config:
        # NEW CONFIG FORMAT
        print(f"Loading search configuration from {args.search_config}")
        config = load_config(args.search_config)
        queries, max_results = get_scopus_config_new(config, tier=args.tier)
        config_mode = "NEW"
    else:
        # LEGACY CONFIG FORMAT
        print("Loading configuration from config/elis_search_queries.yml (legacy mode)")
        config = load_config("config/elis_search_queries.yml")
        queries = get_scopus_queries_legacy(config)
        max_results = config.get("global", {}).get("max_results_per_source", 100)
        config_mode = "LEGACY"
        print(
            f"[WARNING] Using legacy config format. Consider using --search-config for new projects."
        )

    # Apply max_results override if provided
    if args.max_results:
        print(f"Overriding max_results: {max_results} -> {args.max_results}")
        max_results = args.max_results

    # Validate queries
    if not queries:
        print("[WARNING] No Scopus queries found in config")
        print("   Check that Scopus is enabled and queries are defined")
        exit(1)  # Exit with error code - missing queries indicates misconfiguration

    print(f"\n{'='*80}")
    print(f"SCOPUS HARVEST - {config_mode} CONFIG")
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

    # Track existing DOIs and Scopus IDs to avoid duplicates
    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    existing_scopus_ids = {
        r.get("scopus_id") for r in existing_results if r.get("scopus_id")
    }
    new_count = 0

    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying Scopus:")
        print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        try:
            raw_results = scopus_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_scopus_entry(entry)
                doi = transformed.get("doi")
                scopus_id = transformed.get("scopus_id")

                # Add if unique (check both DOI and Scopus ID)
                is_duplicate = False
                if doi and doi in existing_dois:
                    is_duplicate = True
                if scopus_id and scopus_id in existing_scopus_ids:
                    is_duplicate = True

                if not is_duplicate:
                    existing_results.append(transformed)
                    if doi:
                        existing_dois.add(doi)
                    if scopus_id:
                        existing_scopus_ids.add(scopus_id)
                    new_count += 1

        except Exception as e:
            print(f"  Error processing query: {e}")
            traceback.print_exc()
            continue

    # Save combined results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print("[OK] Scopus harvest complete")
    print(f"{'='*80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {output_path}")
    print(f"{'='*80}\n")
