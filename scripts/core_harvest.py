"""
core_harvest.py
Harvests metadata from the CORE API (v3).

CONFIGURATION MODES:
1. NEW (Recommended): --search-config config/searches/electoral_integrity_search.yml
   - Uses dedicated search configuration files
   - Supports tier-based max_results (testing/pilot/benchmark/production/exhaustive)
   - Project-specific settings

2. LEGACY (Backwards Compatible): Reads from config/elis_search_queries.yml
   - Maintains compatibility with existing workflows
   - Uses global max_results_per_source setting

Environment Variables:
- CORE_API_KEY: Your CORE API key (required)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage Examples:
  # New config format with tier
  python scripts/core_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # New config format (uses default tier)
  python scripts/core_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Legacy format (backwards compatible)
  python scripts/core_harvest.py

  # Override max_results regardless of config
  python scripts/core_harvest.py --max-results 500
"""

import requests
import json
import os
import yaml
import argparse
import time
import traceback
from pathlib import Path


# ---------------------------------------------------------------------------
# CREDENTIALS
# ---------------------------------------------------------------------------

def get_credentials():
    """Get and validate CORE API credentials."""
    api_key = os.getenv("CORE_API_KEY")

    if not api_key:
        raise EnvironmentError("Missing CORE_API_KEY environment variable")

    return api_key


def get_headers():
    """Build CORE API headers with Bearer token."""
    api_key = get_credentials()
    return {
        "Authorization": f"Bearer {api_key}",
    }


# ---------------------------------------------------------------------------
# SEARCH (pagination via offset)
# ---------------------------------------------------------------------------

def core_search(query: str, limit: int = 100, max_results: int = 1000):
    """
    Send a query to CORE API v3 and paginate up to max_results.

    CORE API notes:
    - Auth: Bearer token in Authorization header
    - Results in data.results, total available in data.totalHits
    - limit per call: max 100
    - Pagination via offset
    - CORE can be slow / intermittently unavailable — retry on 429 and 503

    Args:
        query (str): Search query string
        limit (int): Number of records per request (max 100)
        max_results (int): Total number of results to retrieve

    Returns:
        list: List of work entries returned by CORE
    """
    url = "https://api.core.ac.uk/v3/search/works"
    results = []
    offset = 0
    retry_count = 0
    max_retries = 5
    printed_rate_limits = False

    # Cache headers once before the loop (avoids repeated get_credentials calls)
    headers = get_headers()

    while len(results) < max_results:
        params = {
            "q": query,
            "limit": min(limit, max_results - len(results)),
            "offset": offset,
        }

        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)

            # Log CORE rate limit headers when available (print once per run)
            rl_remaining = r.headers.get("X-RateLimitRemaining")
            rl_retry_after = r.headers.get("X-RateLimit-Retry-After")
            rl_limit = r.headers.get("X-RateLimit-Limit")
            if (rl_remaining or rl_retry_after or rl_limit) and not printed_rate_limits:
                print("  Rate limits:",
                      f"remaining={rl_remaining}" if rl_remaining is not None else "remaining=?",
                      f"retry_after={rl_retry_after}" if rl_retry_after is not None else "retry_after=?",
                      f"limit={rl_limit}" if rl_limit is not None else "limit=?")
                printed_rate_limits = True

            # Warn if remaining quota is low
            if rl_remaining is not None:
                try:
                    remaining_int = int(rl_remaining)
                    if remaining_int <= 5:
                        print(f"  WARNING: Low rate limit remaining ({remaining_int})")
                except (ValueError, TypeError):
                    pass

            if r.status_code in (429, 500, 503):
                retry_count += 1
                if retry_count > max_retries:
                    print(f"  Max retries ({max_retries}) exceeded due to transient server errors. Stopping.")
                    break
                # Rate limited or service unavailable - back off and retry with exponential backoff
                wait_time = 5 * retry_count
                # If we hit a rate limit, honor Retry-After when provided
                if r.status_code == 429 and rl_retry_after:
                    try:
                        wait_time = max(wait_time, int(rl_retry_after))
                    except (ValueError, TypeError):
                        pass
                print(f"  HTTP {r.status_code}. Waiting {wait_time}s before retry ({retry_count}/{max_retries})...")
                time.sleep(wait_time)
                continue

            if r.status_code != 200:
                print(f"  Error {r.status_code}: {r.text[:200]}")
                break

            # Reset retry count after successful request
            retry_count = 0

            payload = r.json()
            # CORE responses can be either top-level or nested under "data"
            if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
                data = payload.get("data")
            else:
                data = payload if isinstance(payload, dict) else {}

            works = data.get("results", [])

            if not works:
                break

            results.extend(works)
            offset += len(works)

            # Check if we've reached the end
            total_hits = data.get("totalHits", data.get("total", 0))
            if offset >= total_hits:
                print(f"  Retrieved all {total_hits} available results")
                break

            # Rate limiting — be polite
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            break

    return results


# ---------------------------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------------------------

def transform_core_entry(entry):
    """
    Transform raw CORE v3 entry to match the schema used by other sources.

    CORE-specific handling:
    - authors is a list of dicts with 'name' key (can also be non-list — guard)
    - year in yearPublished
    - URL: downloadUrl preferred, links[0].url as fallback
    """
    # Extract authors (as array for schema compliance) — guard against non-list values
    authors_list = entry.get("authors", [])
    if isinstance(authors_list, list):
        authors = [
            a.get("name", "")
            for a in authors_list
            if isinstance(a, dict) and a.get("name")
        ]
    else:
        authors = []

    # Extract year (as integer for schema compliance)
    year_raw = entry.get("yearPublished")
    year = None
    if year_raw:
        try:
            year = int(year_raw)
        except (ValueError, TypeError):
            year = None

    # URL: downloadUrl preferred, links[0].url as fallback
    url = entry.get("downloadUrl", "")
    if not url:
        links = entry.get("links", [{}])
        url = links[0].get("url", "") if links else ""

    return {
        "source": "CORE",
        "title": entry.get("title", "") or "",
        "authors": authors,
        "year": year,
        "doi": entry.get("doi", "") or "",
        "abstract": entry.get("abstract", "") or "",
        "url": url or "",
        "core_id": entry.get("id", "") or "",
        "raw_metadata": entry,
    }


# ---------------------------------------------------------------------------
# CONFIG LOADING — LEGACY
# ---------------------------------------------------------------------------

def load_config(config_path: str):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_core_queries_legacy(config):
    """
    Extract enabled queries for CORE from legacy config format.

    Args:
        config: Legacy config dict from config/elis_search_queries.yml

    Returns:
        list: List of CORE queries (quotes stripped)
    """
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "core" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        # Remove quotes — CORE search does not support them
        core_queries = [q.replace('"', "") for q in topic_queries]
        queries.extend(core_queries)

    return queries


# ---------------------------------------------------------------------------
# CONFIG LOADING — NEW (tier-based)
# ---------------------------------------------------------------------------

def get_core_config_new(config, tier=None):
    """
    Extract CORE configuration from new search config format.

    Args:
        config: New search config dict from config/searches/*.yml
        tier: Optional tier override (testing/pilot/benchmark/production/exhaustive)

    Returns:
        tuple: (queries, max_results)
    """
    # Find CORE database configuration
    databases = config.get("databases", [])
    core_config = None

    for db in databases:
        if db.get("name") == "CORE" and db.get("enabled", False):
            core_config = db
            break

    if not core_config:
        print("[WARNING] CORE not enabled in search configuration")
        return [], 0

    # Get query - prefer simplified alternative if available (works better with CORE)
    query_config = config.get("query", {})
    alternative_queries = query_config.get("alternative_queries", [])

    # Look for simplified query in alternatives
    simplified_query = None
    for alt in alternative_queries:
        if isinstance(alt, dict) and "simplified" in alt:
            simplified_query = alt["simplified"].strip()
            break

    if simplified_query:
        # Use the curated simplified query directly
        core_query = simplified_query
        print(f"Using simplified alternative query for CORE:")
        print(f"  Query: {core_query}")
    else:
        # Fall back to using boolean_string with quotes stripped
        query_string = query_config.get("boolean_string", "")
        if not query_string:
            print("[WARNING] No query found in search configuration")
            return [], 0

        # Apply wrapper if defined, otherwise use raw query (quotes stripped)
        query_wrapper = core_config.get("query_wrapper", "{query}")
        core_query = query_wrapper.replace("{query}", query_string).replace('"', "")
        print(f"Query for CORE (quotes stripped):")
        print(f"  Query: {core_query[:100]}{'...' if len(core_query) > 100 else ''}")

    # Determine max_results based on tier
    max_results_config = core_config.get("max_results")

    if isinstance(max_results_config, dict):
        # Tier-based system
        if tier:
            max_results = max_results_config.get(tier)
            if max_results is None:
                print(f"[WARNING] Unknown tier '{tier}', available tiers: {list(max_results_config.keys())}")
                tier = core_config.get("max_results_default", "production")
                max_results = max_results_config.get(tier, 1000)
                print(f"   Using default tier: {tier}")
        else:
            # Use default tier
            tier = core_config.get("max_results_default", "production")
            max_results = max_results_config.get(tier, 1000)
            print(f"Using default tier: {tier} (max_results: {max_results})")
    else:
        # Single value (backwards compatible)
        max_results = max_results_config or 1000

    return [core_query], max_results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Harvest metadata from CORE API v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use new search config with production tier
  python scripts/core_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # Use new search config with default tier
  python scripts/core_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Use legacy config (backwards compatible)
  python scripts/core_harvest.py

  # Override max_results
  python scripts/core_harvest.py --search-config config/searches/electoral_integrity_search.yml --max-results 500
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
        queries, max_results = get_core_config_new(config, tier=args.tier)
        config_mode = "NEW"
    else:
        # LEGACY CONFIG FORMAT
        print("Loading configuration from config/elis_search_queries.yml (legacy mode)")
        config = load_config("config/elis_search_queries.yml")
        queries = get_core_queries_legacy(config)
        max_results = config.get("global", {}).get("max_results_per_source", 1000)
        config_mode = "LEGACY"
        print("[WARNING] Using legacy config format. Consider using --search-config for new projects.")

    # Apply max_results override if provided
    if args.max_results:
        print(f"Overriding max_results: {max_results} -> {args.max_results}")
        max_results = args.max_results

    # Validate queries
    if not queries:
        print("[WARNING] No CORE queries found in config")
        print("   Check that CORE is enabled and queries are defined")
        exit(1)  # Exit with error code - missing queries indicates misconfiguration

    print(f"\n{'='*80}")
    print(f"CORE HARVEST - {config_mode} CONFIG")
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

    # Track existing DOIs and CORE IDs to avoid duplicates
    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    existing_core_ids = {r.get("core_id") for r in existing_results if r.get("core_id")}
    new_count = 0

    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying CORE:")
        print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        try:
            raw_results = core_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_core_entry(entry)
                doi = transformed.get("doi")
                core_id = transformed.get("core_id")

                # Add if unique (check both DOI and CORE ID)
                is_duplicate = False
                if doi and doi in existing_dois:
                    is_duplicate = True
                if core_id and core_id in existing_core_ids:
                    is_duplicate = True

                if not is_duplicate:
                    existing_results.append(transformed)
                    if doi:
                        existing_dois.add(doi)
                    if core_id:
                        existing_core_ids.add(core_id)
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
    print("[OK] CORE harvest complete")
    print(f"{'='*80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {args.output}")
    print(f"{'='*80}\n")
