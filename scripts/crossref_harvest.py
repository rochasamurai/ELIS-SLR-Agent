"""
crossref_harvest.py
Harvests metadata from the CrossRef API.

CONFIGURATION MODES:
1. NEW (Recommended): --search-config config/searches/electoral_integrity_search.yml
   - Uses dedicated search configuration files
   - Supports tier-based max_results (testing/pilot/benchmark/production/exhaustive)
   - Project-specific settings

2. LEGACY (Backwards Compatible): Reads from config/elis_search_queries.yml
   - Maintains compatibility with existing workflows
   - Uses global max_results_per_source setting

Environment Variables:
- ELIS_CONTACT: Email for polite pool (faster rate limits — optional but recommended)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage Examples:
  # New config format with tier
  python scripts/crossref_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # New config format (uses default tier)
  python scripts/crossref_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Legacy format (backwards compatible)
  python scripts/crossref_harvest.py

  # Override max_results regardless of config
  python scripts/crossref_harvest.py --max-results 500
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
# SEARCH (pagination via offset, mailto polite-pool conditional)
# ---------------------------------------------------------------------------


def crossref_search(query: str, rows: int = 100, max_results: int = 1000):
    """
    Send a query to CrossRef API and paginate up to max_results.

    CrossRef API notes:
    - Response body: message.items (not top-level results)
    - rows per call: max 1000
    - Pagination via offset
    - mailto param enables polite pool (dedicated server, higher limits)

    Args:
        query (str): Search query string
        rows (int): Number of records per request (max 1000)
        max_results (int): Total number of results to retrieve

    Returns:
        list: List of work entries returned by CrossRef
    """
    url = "https://api.crossref.org/works"
    results = []
    offset = 0
    retry_count = 0
    max_retries = 5

    # Get contact email for polite pool — optional, no fallback
    mailto = os.getenv("ELIS_CONTACT")
    if not mailto:
        print(
            "[WARNING] ELIS_CONTACT not set. Polite pool recommended for better rate limits."
        )

    while len(results) < max_results:
        params = {
            "query": query,
            "rows": min(rows, max_results - len(results)),
            "offset": offset,
        }
        # Only add mailto if ELIS_CONTACT is set (for polite pool access)
        if mailto:
            params["mailto"] = mailto

        try:
            r = requests.get(url, params=params, timeout=30)

            if r.status_code == 429:
                retry_count += 1
                if retry_count > max_retries:
                    print(
                        f"  [ERROR] Max retries ({max_retries}) exceeded due to rate limiting. Stopping."
                    )
                    break
                # Rate limited — back off and retry with exponential backoff
                wait_time = 5 * retry_count
                print(
                    f"  [WARNING] Rate limited (429). Waiting {wait_time}s before retry ({retry_count}/{max_retries})..."
                )
                time.sleep(wait_time)
                continue

            if r.status_code != 200:
                print(f"  Error {r.status_code}: {r.text[:200]}")
                break

            # Reset retry count after successful request
            retry_count = 0

            data = r.json()
            message = data.get("message", {})
            items = message.get("items", [])

            if not items:
                break

            results.extend(items)
            offset += len(items)

            # Check if we've reached the end
            total_results = message.get("total-results", 0)
            if offset >= total_results:
                print(f"  Retrieved all {total_results} available results")
                break

            # Rate limiting — be polite
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            break

    return results


# ---------------------------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------------------------


def transform_crossref_entry(entry):
    """
    Transform raw CrossRef entry to match the schema used by other sources.

    CrossRef-specific handling:
    - title is a list — take first element
    - DOI key is uppercase "DOI"
    - Year extracted from published-print or published-online date-parts
    """
    # Extract title (CrossRef returns as a list)
    title_list = entry.get("title", [])
    title = title_list[0] if title_list else ""

    # Extract authors (as array for schema compliance)
    authors_list = entry.get("author", [])
    authors = [
        f"{a.get('given', '')} {a.get('family', '')}".strip()
        for a in authors_list
        if a.get("family")
    ]

    # Extract year from published-print (preferred) or published-online (as integer)
    year = None
    published = entry.get("published-print") or entry.get("published-online")
    if published:
        date_parts = published.get("date-parts", [[]])
        if date_parts and date_parts[0]:
            try:
                year = int(date_parts[0][0])
            except (ValueError, TypeError):
                year = None

    # Extract abstract
    abstract = entry.get("abstract", "") or ""

    return {
        "source": "CrossRef",
        "title": title or "",
        "authors": authors,
        "year": year,
        "doi": entry.get("DOI", "") or "",  # CrossRef uses uppercase DOI
        "abstract": abstract,
        "url": entry.get("URL", "") or "",
        "crossref_type": entry.get("type", "") or "",
        "publisher": entry.get("publisher", "") or "",
        "raw_metadata": entry,
    }


# ---------------------------------------------------------------------------
# CONFIG LOADING — LEGACY
# ---------------------------------------------------------------------------


def load_config(config_path: str):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_crossref_queries_legacy(config):
    """
    Extract enabled queries for CrossRef from legacy config format.

    Args:
        config: Legacy config dict from config/elis_search_queries.yml

    Returns:
        list: List of CrossRef queries (quotes stripped — not supported)
    """
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "crossref" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        # Remove quotes — CrossRef query param does not support them
        crossref_queries = [q.replace('"', "") for q in topic_queries]
        queries.extend(crossref_queries)

    return queries


# ---------------------------------------------------------------------------
# CONFIG LOADING — NEW (tier-based)
# ---------------------------------------------------------------------------


def get_crossref_config_new(config, tier=None):
    """
    Extract CrossRef configuration from new search config format.

    Args:
        config: New search config dict from config/searches/*.yml
        tier: Optional tier override (testing/pilot/benchmark/production/exhaustive)

    Returns:
        tuple: (queries, max_results)
    """
    # Find CrossRef database configuration
    databases = config.get("databases", [])
    cr_config = None

    for db in databases:
        if db.get("name") == "CrossRef" and db.get("enabled", False):
            cr_config = db
            break

    if not cr_config:
        print("[WARNING] CrossRef not enabled in search configuration")
        return [], 0

    # Get query — prefer simplified alternative if available (works better with CrossRef)
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
        cr_query = simplified_query
        print("Using simplified alternative query for CrossRef:")
        print(f"  Query: {cr_query}")
    else:
        # Fall back to using boolean_string with quotes stripped
        query_string = query_config.get("boolean_string", "")
        if not query_string:
            print("[WARNING] No query found in search configuration")
            return [], 0

        # Apply wrapper if defined, otherwise use raw query (quotes stripped)
        query_wrapper = cr_config.get("query_wrapper", "{query}")
        cr_query = query_wrapper.replace("{query}", query_string).replace('"', "")
        print("Query for CrossRef (quotes stripped):")
        print(f"  Query: {cr_query[:100]}{'...' if len(cr_query) > 100 else ''}")

    # Determine max_results based on tier
    max_results_config = cr_config.get("max_results")

    if isinstance(max_results_config, dict):
        # Tier-based system
        if tier:
            max_results = max_results_config.get(tier)
            if max_results is None:
                print(
                    f"[WARNING] Unknown tier '{tier}', available tiers: {list(max_results_config.keys())}"
                )
                tier = cr_config.get("max_results_default", "testing")
                max_results = max_results_config.get(tier, 1000)
                print(f"   Using default tier: {tier}")
        else:
            # Use default tier
            tier = cr_config.get("max_results_default", "testing")
            max_results = max_results_config.get(tier, 1000)
            print(f"Using default tier: {tier} (max_results: {max_results})")
    else:
        # Single value (backwards compatible)
        max_results = max_results_config or 1000

    return [cr_query], max_results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Harvest metadata from CrossRef API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use new search config with production tier
  python scripts/crossref_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # Use new search config with default tier
  python scripts/crossref_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Use legacy config (backwards compatible)
  python scripts/crossref_harvest.py

  # Override max_results
  python scripts/crossref_harvest.py --search-config config/searches/electoral_integrity_search.yml --max-results 500
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
        queries, max_results = get_crossref_config_new(config, tier=args.tier)
        config_mode = "NEW"
    else:
        # LEGACY CONFIG FORMAT
        print("Loading configuration from config/elis_search_queries.yml (legacy mode)")
        config = load_config("config/elis_search_queries.yml")
        queries = get_crossref_queries_legacy(config)
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
        print("[WARNING] No CrossRef queries found in config")
        print("   Check that CrossRef is enabled and queries are defined")
        exit(1)  # Exit with error code - missing queries indicates misconfiguration

    print(f"\n{'='*80}")
    print(f"CROSSREF HARVEST - {config_mode} CONFIG")
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

    # Track existing DOIs and normalised titles to avoid duplicates.
    # CrossRef has no secondary native ID — normalised title is the fallback
    # to catch entries that arrive without a DOI.
    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    existing_titles = {
        r.get("title", "").lower().strip() for r in existing_results if r.get("title")
    }
    new_count = 0

    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying CrossRef:")
        print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        try:
            raw_results = crossref_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_crossref_entry(entry)
                doi = transformed.get("doi")
                title = transformed.get("title", "").lower().strip()

                # Add if unique (check DOI first, then normalised title)
                is_duplicate = False
                if doi and doi in existing_dois:
                    is_duplicate = True
                elif title and title in existing_titles:
                    is_duplicate = True

                if not is_duplicate:
                    existing_results.append(transformed)
                    if doi:
                        existing_dois.add(doi)
                    if title:
                        existing_titles.add(title)
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
    print("[OK] CrossRef harvest complete")
    print(f"{'='*80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {args.output}")
    print(f"{'='*80}\n")
