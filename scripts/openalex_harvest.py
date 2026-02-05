"""
openalex_harvest.py
Harvests metadata from the OpenAlex API.

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
  python scripts/openalex_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # New config format (uses default tier)
  python scripts/openalex_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Legacy format (backwards compatible)
  python scripts/openalex_harvest.py

  # Override max_results regardless of config
  python scripts/openalex_harvest.py --max-results 500
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
# SEARCH (pagination via page, mailto polite-pool conditional)
# ---------------------------------------------------------------------------


def openalex_search(query: str, per_page: int = 100, max_results: int = 1000):
    """
    Send a query to OpenAlex API and paginate up to max_results.

    OpenAlex API notes:
    - Uses default.search filter to search across title, abstract, and fulltext
      (matches Tai & Awasthi methodology: title, abstract, keywords)
    - per_page max: 200
    - Pagination via page parameter (1-based)
    - mailto param enables polite pool (10x rate limit)

    Args:
        query (str): Search query string
        per_page (int): Number of records per request (max 200)
        max_results (int): Total number of results to retrieve

    Returns:
        list: List of work entries returned by OpenAlex
    """
    url = "https://api.openalex.org/works"
    results = []
    page = 1
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
            # default.search searches across title, abstract, and fulltext
            "filter": f"default.search:{query}",
            "per_page": min(per_page, max_results - len(results)),
            "page": page,
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
            works = data.get("results", [])

            if not works:
                break

            results.extend(works)
            page += 1

            # Check if we've reached the last page
            meta = data.get("meta", {})
            count = meta.get("count", 0)
            if len(results) >= count:
                print(f"  Retrieved all {count} available results")
                break

            # Rate limiting — be polite
            time.sleep(0.1)

        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            break

    return results


# ---------------------------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------------------------


def transform_openalex_entry(entry):
    """
    Transform raw OpenAlex entry to match the schema used by other sources.

    OpenAlex-specific handling:
    - DOI arrives as full URL (https://doi.org/...) — strip prefix
    - Abstract stored as inverted index — reconstruct word order
    """
    # Extract authors (as array for schema compliance)
    authorships = entry.get("authorships", [])
    authors = [
        a.get("author", {}).get("display_name", "")
        for a in authorships
        if a.get("author", {}).get("display_name")
    ]

    # Extract year (as integer for schema compliance)
    year_raw = entry.get("publication_year")
    year = None
    if year_raw:
        try:
            year = int(year_raw)
        except (ValueError, TypeError):
            year = None

    # Extract DOI — strip URL prefix if present
    doi = entry.get("doi", "") or ""
    if doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")

    # Reconstruct abstract from inverted index
    abstract_inverted = entry.get("abstract_inverted_index", {})
    abstract = ""
    if abstract_inverted:
        words = {}
        for word, positions in abstract_inverted.items():
            for pos in positions:
                words[pos] = word
        abstract = " ".join([words[i] for i in sorted(words.keys())])

    # Ensure citation_count is always an integer (API may return None)
    citation_count = entry.get("cited_by_count")
    citation_count = citation_count if citation_count is not None else 0

    return {
        "source": "OpenAlex",
        "title": entry.get("title", "") or "",
        "authors": authors,
        "year": year,
        "doi": doi,
        "abstract": abstract,
        "url": entry.get("doi", "") or entry.get("id", "") or "",
        "openalex_id": entry.get("id", "") or "",
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


def get_openalex_queries_legacy(config):
    """
    Extract enabled queries for OpenAlex from legacy config format.

    Args:
        config: Legacy config dict from config/elis_search_queries.yml

    Returns:
        list: List of OpenAlex queries (quotes stripped — not supported by default.search)
    """
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "openalex" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        # Remove quotes — OpenAlex default.search does not support them
        openalex_queries = [q.replace('"', "") for q in topic_queries]
        queries.extend(openalex_queries)

    return queries


# ---------------------------------------------------------------------------
# CONFIG LOADING — NEW (tier-based)
# ---------------------------------------------------------------------------


def get_openalex_config_new(config, tier=None):
    """
    Extract OpenAlex configuration from new search config format.

    Args:
        config: New search config dict from config/searches/*.yml
        tier: Optional tier override (testing/pilot/benchmark/production/exhaustive)

    Returns:
        tuple: (queries, max_results)
    """
    # Find OpenAlex database configuration
    databases = config.get("databases", [])
    oa_config = None

    for db in databases:
        if db.get("name") == "OpenAlex" and db.get("enabled", False):
            oa_config = db
            break

    if not oa_config:
        print("[WARNING] OpenAlex not enabled in search configuration")
        return [], 0

    # Get query — prefer simplified alternative if available (works better with default.search)
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
        oa_query = simplified_query
        print("Using simplified alternative query for OpenAlex:")
        print(f"  Query: {oa_query}")
    else:
        # Fall back to using boolean_string with quotes stripped
        query_string = query_config.get("boolean_string", "")
        if not query_string:
            print("[WARNING] No query found in search configuration")
            return [], 0

        # Apply wrapper if defined, otherwise use raw query (quotes stripped)
        query_wrapper = oa_config.get("query_wrapper", "{query}")
        oa_query = query_wrapper.replace("{query}", query_string).replace('"', "")
        print("Query for OpenAlex (quotes stripped):")
        print(f"  Query: {oa_query[:100]}{'...' if len(oa_query) > 100 else ''}")

    # Determine max_results based on tier
    max_results_config = oa_config.get("max_results")

    if isinstance(max_results_config, dict):
        # Tier-based system
        if tier:
            max_results = max_results_config.get(tier)
            if max_results is None:
                print(
                    f"[WARNING] Unknown tier '{tier}', available tiers: {list(max_results_config.keys())}"
                )
                tier = oa_config.get("max_results_default", "production")
                max_results = max_results_config.get(tier, 1000)
                print(f"   Using default tier: {tier}")
        else:
            # Use default tier
            tier = oa_config.get("max_results_default", "production")
            max_results = max_results_config.get(tier, 1000)
            print(f"Using default tier: {tier} (max_results: {max_results})")
    else:
        # Single value (backwards compatible)
        max_results = max_results_config or 1000

    return [oa_query], max_results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Harvest metadata from OpenAlex API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use new search config with production tier
  python scripts/openalex_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # Use new search config with default tier
  python scripts/openalex_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Use legacy config (backwards compatible)
  python scripts/openalex_harvest.py

  # Override max_results
  python scripts/openalex_harvest.py --search-config config/searches/electoral_integrity_search.yml --max-results 500
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
        queries, max_results = get_openalex_config_new(config, tier=args.tier)
        config_mode = "NEW"
    else:
        # LEGACY CONFIG FORMAT
        print("Loading configuration from config/elis_search_queries.yml (legacy mode)")
        config = load_config("config/elis_search_queries.yml")
        queries = get_openalex_queries_legacy(config)
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
        print("[WARNING] No OpenAlex queries found in config")
        print("   Check that OpenAlex is enabled and queries are defined")
        exit(1)  # Exit with error code - missing queries indicates misconfiguration

    print(f"\n{'='*80}")
    print(f"OPENALEX HARVEST - {config_mode} CONFIG")
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

    # Track existing DOIs and OpenAlex IDs to avoid duplicates
    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    existing_oa_ids = {
        r.get("openalex_id") for r in existing_results if r.get("openalex_id")
    }
    new_count = 0

    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying OpenAlex:")
        print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        try:
            raw_results = openalex_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_openalex_entry(entry)
                doi = transformed.get("doi")
                oa_id = transformed.get("openalex_id")

                # Add if unique (check both DOI and OpenAlex ID)
                is_duplicate = False
                if doi and doi in existing_dois:
                    is_duplicate = True
                if oa_id and oa_id in existing_oa_ids:
                    is_duplicate = True

                if not is_duplicate:
                    existing_results.append(transformed)
                    if doi:
                        existing_dois.add(doi)
                    if oa_id:
                        existing_oa_ids.add(oa_id)
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
    print("[OK] OpenAlex harvest complete")
    print(f"{'='*80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {args.output}")
    print(f"{'='*80}\n")
