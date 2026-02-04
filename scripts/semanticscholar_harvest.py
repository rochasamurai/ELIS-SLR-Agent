"""
semanticscholar_harvest.py
Harvests metadata from the Semantic Scholar API.

CONFIGURATION MODES:
1. NEW (Recommended): --search-config config/searches/electoral_integrity_search.yml
   - Uses dedicated search configuration files
   - Supports tier-based max_results (testing/pilot/benchmark/production/exhaustive)
   - Project-specific settings

2. LEGACY (Backwards Compatible): Reads from config/elis_search_queries.yml
   - Maintains compatibility with existing workflows
   - Uses global max_results_per_source setting

Environment Variables:
- SEMANTIC_SCHOLAR_API_KEY: Optional API key (increases rate limits from 1 req/s to 100 req/s)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage Examples:
  # New config format with tier
  python scripts/semanticscholar_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # New config format (uses default tier)
  python scripts/semanticscholar_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Legacy format (backwards compatible)
  python scripts/semanticscholar_harvest.py

  # Override max_results regardless of config
  python scripts/semanticscholar_harvest.py --max-results 500
"""

import requests
import json
import os
import yaml
import argparse
import time
import re
import traceback
from pathlib import Path


# ---------------------------------------------------------------------------
# QUERY SIMPLIFICATION
# ---------------------------------------------------------------------------

def simplify_boolean_query(boolean_query: str) -> str:
    """
    Convert boolean query syntax to keyword-based query for Semantic Scholar.
    
    Semantic Scholar API does NOT support boolean operators (AND/OR/NOT).
    It uses keyword-based search, ranking papers by relevance.
    
    This function:
    - Removes boolean operators (AND, OR, NOT)
    - Removes quotes and parentheses
    - Extracts meaningful keywords
    - Limits query length to 500 chars
    
    Args:
        boolean_query: Query with boolean syntax like:
                      '("electoral system" OR "voting system") AND ("integrity" OR "security")'
    
    Returns:
        Simplified keyword query: 'electoral system voting system integrity security'
    """
    # Remove boolean operators
    query = re.sub(r'\bAND\b|\bOR\b|\bNOT\b', ' ', boolean_query, flags=re.IGNORECASE)
    
    # Remove quotes and parentheses
    query = re.sub(r'[()\"]+', ' ', query)
    
    # Clean up whitespace and newlines
    query = ' '.join(query.split())
    
    # Limit length (Semantic Scholar has query length limits)
    # Truncate at word boundary to avoid cutting words mid-way
    if len(query) > 500:
        query = query[:500].rsplit(' ', 1)[0]

    return query.strip()


# ---------------------------------------------------------------------------
# CREDENTIALS (API key is optional — increases rate limit if present)
# ---------------------------------------------------------------------------

def get_credentials():
    """Get Semantic Scholar API key (optional)."""
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if not api_key:
        print("[WARNING] SEMANTIC_SCHOLAR_API_KEY not set. Rate limited to 1 req/s (100 req/s with key).")
    return api_key


def get_headers():
    """Build Semantic Scholar API headers."""
    api_key = get_credentials()
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    return headers


# ---------------------------------------------------------------------------
# SEARCH (pagination via offset — already looped, kept as-is)
# ---------------------------------------------------------------------------

def semanticscholar_search(query: str, limit: int = 100, max_results: int = 1000):
    """
    Send a query to Semantic Scholar API and paginate up to max_results.

    Semantic Scholar API constraints:
    - limit per call: max 100
    - Pagination via offset
    - Rate limit: 1 req/s (unauthenticated), 100 req/s (with API key)

    Args:
        query (str): Search query string (keywords, not boolean syntax)
        limit (int): Number of records per request (max 100)
        max_results (int): Total number of results to retrieve

    Returns:
        list: List of paper entries returned by Semantic Scholar
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    results = []
    offset = 0
    retry_count = 0
    max_retries = 5

    # Request all useful fields in one call
    fields = "title,authors,year,venue,abstract,citationCount,externalIds"

    # Cache headers once before the loop (avoids repeated get_credentials calls)
    headers = get_headers()

    # Adjust sleep based on whether we have an API key
    has_key = bool(os.getenv("SEMANTIC_SCHOLAR_API_KEY"))
    sleep_interval = 0.1 if has_key else 1.0

    while len(results) < max_results:
        params = {
            "query": query,
            "limit": min(limit, max_results - len(results)),
            "offset": offset,
            "fields": fields,
        }

        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)

            if r.status_code == 429:
                retry_count += 1
                if retry_count > max_retries:
                    print(f"  [ERROR] Max retries ({max_retries}) exceeded due to rate limiting. Stopping.")
                    break
                # Rate limited — back off and retry with exponential backoff
                wait_time = 5 * retry_count
                print(f"  [WARNING] Rate limited (429). Waiting {wait_time}s before retry ({retry_count}/{max_retries})...")
                time.sleep(wait_time)
                continue

            if r.status_code != 200:
                print(f"  Error {r.status_code}: {r.text[:200]}")
                break

            # Reset retry count after successful request
            retry_count = 0

            data = r.json()
            papers = data.get("data", [])

            if not papers:
                break

            results.extend(papers)
            offset += len(papers)

            # Check if we've reached the end
            total = data.get("total", 0)
            if offset >= total:
                print(f"  Retrieved all {total} available results")
                break

            # Rate limiting
            time.sleep(sleep_interval)

        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            break

    return results


# ---------------------------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------------------------

def transform_semanticscholar_entry(entry):
    """
    Transform raw Semantic Scholar entry to match the schema used by other sources.
    """
    # Extract authors (as array for schema compliance)
    authors_list = entry.get("authors", [])
    authors = [a.get("name", "") for a in authors_list if a.get("name")]

    # Extract year (as integer for schema compliance)
    year_raw = entry.get("year")
    year = None
    if year_raw:
        try:
            year = int(year_raw)
        except (ValueError, TypeError):
            year = None

    # Get DOI from externalIds (preferred) or top level
    external_ids = entry.get("externalIds", {}) or {}
    doi = external_ids.get("DOI", "") or entry.get("doi", "") or ""

    # Ensure citation_count is always an integer (API may return None)
    citation_count = entry.get("citationCount")
    citation_count = citation_count if citation_count is not None else 0

    return {
        "source": "Semantic Scholar",
        "title": entry.get("title", "") or "",
        "authors": authors,
        "year": year,
        "doi": doi,
        "abstract": entry.get("abstract", "") or "",
        "url": entry.get("url", "") or "",
        "s2_id": entry.get("paperId", "") or "",
        "citation_count": citation_count,
        "raw_metadata": entry,
    }


# ---------------------------------------------------------------------------
# CONFIG LOADING — LEGACY
# ---------------------------------------------------------------------------

def load_config(config_path: str):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_semanticscholar_queries_legacy(config):
    """
    Extract enabled queries for Semantic Scholar from legacy config format.

    Args:
        config: Legacy config dict from config/elis_search_queries.yml

    Returns:
        list: List of Semantic Scholar queries (natural language, no wrapper needed)
    """
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "semantic_scholar" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        queries.extend(topic_queries)

    return queries


# ---------------------------------------------------------------------------
# CONFIG LOADING — NEW (tier-based)
# ---------------------------------------------------------------------------

def get_semanticscholar_config_new(config, tier=None):
    """
    Extract Semantic Scholar configuration from new search config format.

    Args:
        config: New search config dict from config/searches/*.yml
        tier: Optional tier override (testing/pilot/benchmark/production/exhaustive)

    Returns:
        tuple: (queries, max_results)
    """
    # Find Semantic Scholar database configuration
    databases = config.get("databases", [])
    s2_config = None

    for db in databases:
        if db.get("name") == "Semantic Scholar" and db.get("enabled", False):
            s2_config = db
            break

    if not s2_config:
        print("[WARNING] Semantic Scholar not enabled in search configuration")
        return [], 0

    # Get query — prefer simplified alternative if available (works better with S2 API)
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
        s2_query_simplified = simplified_query
        print(f"Using simplified alternative query for Semantic Scholar:")
        print(f"  Query: {s2_query_simplified}")
    else:
        # Fall back to simplifying the boolean query
        query_string = query_config.get("boolean_string", "")
        if not query_string:
            print("[WARNING] No query found in search configuration")
            return [], 0

        # Apply wrapper if one is defined in config, otherwise use raw query
        query_wrapper = s2_config.get("query_wrapper", "{query}")
        s2_query = query_wrapper.replace("{query}", query_string)

        # Simplify boolean query to keywords — Semantic Scholar doesn't support boolean syntax
        s2_query_simplified = simplify_boolean_query(s2_query)

        print(f"Query simplified for Semantic Scholar:")
        print(f"  Original: {s2_query[:100]}{'...' if len(s2_query) > 100 else ''}")
        print(f"  Simplified: {s2_query_simplified[:100]}{'...' if len(s2_query_simplified) > 100 else ''}")

    # Determine max_results based on tier
    max_results_config = s2_config.get("max_results")

    if isinstance(max_results_config, dict):
        # Tier-based system
        if tier:
            max_results = max_results_config.get(tier)
            if max_results is None:
                print(f"[WARNING] Unknown tier '{tier}', available tiers: {list(max_results_config.keys())}")
                tier = s2_config.get("max_results_default", "production")
                max_results = max_results_config.get(tier, 1000)
                print(f"   Using default tier: {tier}")
        else:
            # Use default tier
            tier = s2_config.get("max_results_default", "production")
            max_results = max_results_config.get(tier, 1000)
            print(f"Using default tier: {tier} (max_results: {max_results})")
    else:
        # Single value (backwards compatible)
        max_results = max_results_config or 1000

    return [s2_query_simplified], max_results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Harvest metadata from Semantic Scholar API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use new search config with production tier
  python scripts/semanticscholar_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # Use new search config with default tier
  python scripts/semanticscholar_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Use legacy config (backwards compatible)
  python scripts/semanticscholar_harvest.py

  # Override max_results
  python scripts/semanticscholar_harvest.py --search-config config/searches/electoral_integrity_search.yml --max-results 500
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
        queries, max_results = get_semanticscholar_config_new(config, tier=args.tier)
        config_mode = "NEW"
    else:
        # LEGACY CONFIG FORMAT
        print("Loading configuration from config/elis_search_queries.yml (legacy mode)")
        config = load_config("config/elis_search_queries.yml")
        queries = get_semanticscholar_queries_legacy(config)
        max_results = config.get("global", {}).get("max_results_per_source", 1000)
        config_mode = "LEGACY"
        print("[WARNING] Using legacy config format. Consider using --search-config for new projects.")

    # Apply max_results override if provided
    if args.max_results:
        print(f"Overriding max_results: {max_results} -> {args.max_results}")
        max_results = args.max_results

    # Validate queries
    if not queries:
        print("[WARNING] No Semantic Scholar queries found in config")
        print("   Check that Semantic Scholar is enabled and queries are defined")
        exit(1)  # Exit with error code - missing queries indicates misconfiguration

    print(f"\n{'='*80}")
    print(f"SEMANTIC SCHOLAR HARVEST - {config_mode} CONFIG")
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

    # Track existing DOIs and Semantic Scholar paper IDs to avoid duplicates
    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    existing_s2_ids = {r.get("s2_id") for r in existing_results if r.get("s2_id")}
    new_count = 0

    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying Semantic Scholar:")
        print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        try:
            raw_results = semanticscholar_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_semanticscholar_entry(entry)
                doi = transformed.get("doi")
                s2_id = transformed.get("s2_id")

                # Add if unique (check both DOI and Semantic Scholar paperId)
                is_duplicate = False
                if doi and doi in existing_dois:
                    is_duplicate = True
                if s2_id and s2_id in existing_s2_ids:
                    is_duplicate = True

                if not is_duplicate:
                    existing_results.append(transformed)
                    if doi:
                        existing_dois.add(doi)
                    if s2_id:
                        existing_s2_ids.add(s2_id)
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
    print("[OK] Semantic Scholar harvest complete")
    print(f"{'='*80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {args.output}")
    print(f"{'='*80}\n")
