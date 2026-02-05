"""
google_scholar_harvest.py
Harvests metadata from Google Scholar via Apify API using official Python client.
Uses easyapi/google-scholar-scraper actor.

CONFIGURATION MODES:
1. NEW (Recommended): --search-config config/searches/electoral_integrity_search.yml
   - Uses dedicated search configuration files
   - Supports tier-based max_results (testing/pilot/benchmark/production/exhaustive)
   - Project-specific settings

2. LEGACY (Backwards Compatible): Reads from config/elis_search_queries.yml
   - Maintains compatibility with existing workflows
   - Uses global max_results_per_source setting

NOTE — Apify-specific constraints:
- No direct pagination control (actor handles internally)
- EasyAPI free tier hard-caps at 10 results per run regardless of maxItems
- Year filtering not supported by the EasyAPI actor
- DOI not provided by EasyAPI — dedup uses normalised title + google_scholar_id

Environment Variables:
- APIFY_API_TOKEN: Your Apify API token (required)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage Examples:
  # New config format with tier
  python scripts/google_scholar_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # New config format (uses default tier)
  python scripts/google_scholar_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Legacy format (backwards compatible)
  python scripts/google_scholar_harvest.py

  # Override max_results regardless of config
  python scripts/google_scholar_harvest.py --max-results 500
"""

import os
import json
import yaml
import argparse
import hashlib
import time
import random
import traceback
from pathlib import Path
from datetime import datetime
from apify_client import ApifyClient


# ---------------------------------------------------------------------------
# CREDENTIALS
# ---------------------------------------------------------------------------


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

        print("[INFO] APIFY ACCOUNT STATUS:")
        print(f"   User ID: {user.get('id', 'N/A')}")
        print(f"   Username: {user.get('username', 'N/A')}")

        # Credits might be in different structure
        usage = user.get("usageCredits", {})
        if isinstance(usage, dict):
            remaining = usage.get("remaining", "N/A")
            print(f"   Credits: ${remaining}")

        return True
    except Exception as e:
        print(f"[WARNING] Could not check account status: {e}")
        return False


# ---------------------------------------------------------------------------
# QUERY PREPARATION
# ---------------------------------------------------------------------------


def prepare_google_scholar_query(original_query):
    """
    Convert complex Boolean query to simple format for Google Scholar.
    EasyAPI actor works best with simple keyword queries — Boolean operators
    and parentheses are stripped.
    """
    simple_query = original_query.replace('"', "").replace("(", "").replace(")", "")
    simple_query = simple_query.replace(" AND ", " ").replace(" OR ", " ")
    simple_query = " ".join(simple_query.split())  # Normalize whitespace

    return simple_query.strip()


# ---------------------------------------------------------------------------
# SEARCH (Apify actor — no direct pagination, recursive retry)
# ---------------------------------------------------------------------------


def google_scholar_search(
    client,
    query: str,
    max_items: int = 1000,
    start_year: int = None,
    end_year: int = None,
    retry_count: int = 0,
    max_retries: int = 2,
):
    """
    Search Google Scholar via Apify using easyapi/google-scholar-scraper actor.

    Apify-specific notes:
    - Actor is called via client.actor().call() — runs asynchronously, blocks until done
    - Results retrieved from the run's default dataset after completion
    - Free tier hard-caps at 10 results regardless of maxItems
    - maxItems minimum is 100 (actor requirement)
    - Year filtering not available in EasyAPI actor
    - Recursive retry with random 30-60s back-off on failure or 0 results

    Args:
        client: ApifyClient instance
        query (str): Original search query (will be simplified)
        max_items (int): Requested result count (actor may return fewer)
        start_year (int): Not supported by EasyAPI — logged as warning only
        end_year (int): Not supported by EasyAPI — logged as warning only
        retry_count (int): Current retry attempt (internal)
        max_retries (int): Maximum retry attempts

    Returns:
        list: List of Google Scholar result dicts
    """
    # Add delay between retry attempts
    if retry_count > 0:
        delay = random.uniform(30, 60)
        print(f"\n  [WAIT] Waiting {delay:.0f} seconds before retry...")
        time.sleep(delay)

    # Simplify query for EasyAPI
    search_query = prepare_google_scholar_query(query)

    print(
        f"\n[SEARCH] GOOGLE SCHOLAR SEARCH (Attempt {retry_count + 1}/{max_retries + 1})"
    )
    print("   Actor: easyapi/google-scholar-scraper")
    print(f"   Original: {query[:100]}{'...' if len(query) > 100 else ''}")
    print(
        f"   Simplified: {search_query[:100]}{'...' if len(search_query) > 100 else ''}"
    )
    print(f"   Max items: {max_items}")
    print(f"   Timestamp: {datetime.now().isoformat()}")

    # Prepare input — EasyAPI requires minimum 100 for maxItems
    run_input = {
        "query": search_query,
        "maxItems": max(100, max_items),
    }

    # Year filtering not available in EasyAPI actor
    if start_year or end_year:
        print("   [WARNING] Year filtering not supported by EasyAPI actor")

    try:
        print("\n  Starting Apify run...")

        # Run the actor and wait for it to finish
        run = client.actor("easyapi/google-scholar-scraper").call(run_input=run_input)

        print("  [OK] Run completed")
        print(f"    Run ID: {run.get('id')}")
        print(f"    Status: {run.get('status')}")
        print(f"    Run URL: https://console.apify.com/actors/runs/{run.get('id')}")

        # Get build/run stats
        stats = run.get("stats", {})
        compute_units = stats.get("computeUnits", 0)
        print(f"    Compute units: {compute_units:.4f}")
        print(f"    Estimated cost: ${compute_units * 0.25:.4f}")

        # Check if run succeeded
        status = run.get("status")
        if status != "SUCCEEDED":
            print(f"  [WARNING] Run status: {status}")
            if retry_count < max_retries:
                return google_scholar_search(
                    client,
                    query,
                    max_items,
                    start_year,
                    end_year,
                    retry_count + 1,
                    max_retries,
                )
            return []

        # Fetch results from dataset
        print("\n  Retrieving results from dataset...")
        dataset_id = run.get("defaultDatasetId")

        dataset_client = client.dataset(dataset_id)
        results = list(dataset_client.iterate_items())

        print(f"  [OK] Retrieved {len(results)} results from Google Scholar")

        if len(results) == 0:
            print("  [WARNING] WARNING: 0 results")
            if retry_count < max_retries:
                print("\n  Retrying...")
                return google_scholar_search(
                    client,
                    query,
                    max_items,
                    start_year,
                    end_year,
                    retry_count + 1,
                    max_retries,
                )
            else:
                print("  [ERROR] All retries exhausted")
        elif len(results) == 10:
            print("  [NOTE] Note: Free tier limited to 10 results")
            print("      Upgrade Apify account for up to 5000 results")

        return results

    except Exception as e:
        print(f"  [ERROR] Error: {type(e).__name__}: {e}")

        if retry_count < max_retries:
            print("\n  Retrying...")
            return google_scholar_search(
                client,
                query,
                max_items,
                start_year,
                end_year,
                retry_count + 1,
                max_retries,
            )

        return []


# ---------------------------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------------------------


def transform_google_scholar_entry(entry):
    """
    Transform EasyAPI Google Scholar result to standard format.

    EasyAPI-specific field mapping:
    - snippet -> abstract (EasyAPI uses 'snippet' not 'abstract')
    - link -> url
    - pdf_link -> pdf_url
    - result_id -> google_scholar_id (fallback: hash of title+link)
    - DOI: not provided by EasyAPI - set to None
    """
    # Ensure citation_count is always an integer (API may return None)
    citation_count = entry.get("citations")
    citation_count = citation_count if citation_count is not None else 0

    # Extract authors (as array for schema compliance)
    # EasyAPI returns authors as comma-separated string
    authors_str = entry.get("authors", "") or ""
    authors = (
        [a.strip() for a in authors_str.split(",") if a.strip()] if authors_str else []
    )

    # Extract year (as integer for schema compliance)
    year_raw = entry.get("year")
    year = None
    if year_raw:
        try:
            year = int(year_raw)
        except (ValueError, TypeError):
            year = None

    # Extract or generate google_scholar_id
    # EasyAPI may not provide result_id, so generate a stable hash from title+link
    gs_id = entry.get("result_id", "") or ""
    if not gs_id:
        title = entry.get("title", "") or ""
        link = entry.get("link", "") or ""
        if title or link:
            gs_id = "gs_" + hashlib.md5((title + link).encode()).hexdigest()[:12]

    return {
        "source": "Google Scholar",
        "title": entry.get("title", "") or "",
        "authors": authors,
        "year": year,
        "doi": None,  # EasyAPI does not provide DOI
        "abstract": entry.get("snippet", "") or "",  # EasyAPI uses 'snippet'
        "url": entry.get("link", "") or "",
        "pdf_url": entry.get("pdf_link") or "",
        "citation_count": citation_count,
        "google_scholar_id": gs_id,
        "raw_metadata": entry,
    }


# ---------------------------------------------------------------------------
# CONFIG LOADING — LEGACY
# ---------------------------------------------------------------------------


def load_config(config_path: str):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_google_scholar_queries_legacy(config):
    """
    Extract enabled queries for Google Scholar from legacy config format.

    Note: queries are NOT quote-stripped here — prepare_google_scholar_query()
    handles all Boolean simplification at search time.

    Args:
        config: Legacy config dict from config/elis_search_queries.yml

    Returns:
        list: List of raw Google Scholar queries
    """
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


# ---------------------------------------------------------------------------
# CONFIG LOADING — NEW (tier-based)
# ---------------------------------------------------------------------------


def get_google_scholar_config_new(config, tier=None):
    """
    Extract Google Scholar configuration from new search config format.

    Args:
        config: New search config dict from config/searches/*.yml
        tier: Optional tier override (testing/pilot/benchmark/production/exhaustive)

    Returns:
        tuple: (queries, max_results)
    """
    # Find Google Scholar database configuration
    databases = config.get("databases", [])
    gs_config = None

    for db in databases:
        if db.get("name") in ("Google Scholar", "GoogleScholar") and db.get(
            "enabled", False
        ):
            gs_config = db
            break

    if not gs_config:
        print("[WARNING] Google Scholar not enabled in search configuration")
        return [], 0

    # Get query — do NOT strip quotes here; prepare_google_scholar_query()
    # handles Boolean simplification at search time
    query_string = config.get("query", {}).get("boolean_string", "")
    if not query_string:
        print("[WARNING] No query found in search configuration")
        return [], 0

    # Apply wrapper if defined, otherwise use raw query
    query_wrapper = gs_config.get("query_wrapper", "{query}")
    gs_query = query_wrapper.replace("{query}", query_string)

    # Determine max_results based on tier
    max_results_config = gs_config.get("max_results")

    if isinstance(max_results_config, dict):
        # Tier-based system
        if tier:
            max_results = max_results_config.get(tier)
            if max_results is None:
                print(
                    f"[WARNING] Unknown tier '{tier}', available tiers: {list(max_results_config.keys())}"
                )
                tier = gs_config.get("max_results_default", "testing")
                max_results = max_results_config.get(tier, 1000)
                print(f"   Using default tier: {tier}")
        else:
            # Use default tier
            tier = gs_config.get("max_results_default", "testing")
            max_results = max_results_config.get(tier, 1000)
            print(f"Using default tier: {tier} (max_results: {max_results})")
    else:
        # Single value (backwards compatible)
        max_results = max_results_config or 1000

    return [gs_query], max_results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Harvest metadata from Google Scholar via Apify",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use new search config with production tier
  python scripts/google_scholar_harvest.py --search-config config/searches/electoral_integrity_search.yml --tier production

  # Use new search config with default tier
  python scripts/google_scholar_harvest.py --search-config config/searches/tai_awasthi_2025_search.yml

  # Use legacy config (backwards compatible)
  python scripts/google_scholar_harvest.py

  # Override max_results
  python scripts/google_scholar_harvest.py --search-config config/searches/electoral_integrity_search.yml --max-results 500

NOTE: EasyAPI free tier hard-caps at 10 results regardless of max_results.
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

    print("=" * 80)
    print("GOOGLE SCHOLAR HARVEST - EASYAPI ACTOR")
    print("=" * 80)
    print(f"Start time: {datetime.now().isoformat()}")
    print("Actor: easyapi/google-scholar-scraper")

    # Initialize Apify client
    api_token = get_credentials()
    client = ApifyClient(api_token)

    # Check account status
    check_apify_account_status(client)

    # Determine configuration mode
    if args.search_config:
        # NEW CONFIG FORMAT
        print(f"\nLoading search configuration from {args.search_config}")
        config = load_config(args.search_config)
        queries, max_results = get_google_scholar_config_new(config, tier=args.tier)
        config_mode = "NEW"
    else:
        # LEGACY CONFIG FORMAT
        print(
            "\nLoading configuration from config/elis_search_queries.yml (legacy mode)"
        )
        config = load_config("config/elis_search_queries.yml")
        queries = get_google_scholar_queries_legacy(config)
        max_results = config.get("global", {}).get("max_results_per_source", 1000)
        config_mode = "LEGACY"
        print(
            "[WARNING] Using legacy config format. Consider using --search-config for new projects."
        )

    # Extract year range from config (logged only — not supported by EasyAPI)
    global_config = config.get("global", {})
    year_from = global_config.get("year_from")
    year_to = global_config.get("year_to")

    # Apply max_results override if provided
    if args.max_results:
        print(f"Overriding max_results: {max_results} -> {args.max_results}")
        max_results = args.max_results

    # Validate queries
    if not queries:
        print("\n[WARNING] No Google Scholar queries found in config")
        print("   Check that Google Scholar is enabled and queries are defined")
        exit(1)  # Exit with error code - missing queries indicates misconfiguration

    print(f"\n{'=' * 80}")
    print(f"GOOGLE SCHOLAR HARVEST - {config_mode} CONFIG")
    print(f"{'=' * 80}")
    print(f"Queries: {len(queries)}")
    print(f"Max results per query: {max_results}")
    print(f"Year range: {year_from}-{year_to} (not supported by EasyAPI — logged only)")
    print(f"Output: {args.output}")
    print(f"{'=' * 80}\n")

    # Define output path
    output_path = Path(args.output)

    # Load existing results if file exists
    existing_results = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing_results = json.load(f)
        print(f"Loaded {len(existing_results)} existing results")

    # Track existing titles and Google Scholar IDs to avoid duplicates.
    # DOI is not available from EasyAPI — dual dedup uses normalised title
    # (primary) + google_scholar_id / result_id (secondary).
    existing_titles = {
        r.get("title", "").lower().strip() for r in existing_results if r.get("title")
    }
    existing_gs_ids = {
        r.get("google_scholar_id")
        for r in existing_results
        if r.get("google_scholar_id")
    }
    new_count = 0

    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"QUERY {i}/{len(queries)}")
        print(f"{'=' * 80}")

        try:
            raw_results = google_scholar_search(
                client,
                query,
                max_items=max_results,
                start_year=year_from,
                end_year=year_to,
            )

            print(f"\n[INFO] Processing {len(raw_results)} results...")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_google_scholar_entry(entry)
                title = transformed.get("title", "").lower().strip()
                gs_id = transformed.get("google_scholar_id")

                # Add if unique (check both normalised title and google_scholar_id)
                is_duplicate = False
                if title and title in existing_titles:
                    is_duplicate = True
                if gs_id and gs_id in existing_gs_ids:
                    is_duplicate = True

                if not is_duplicate:
                    existing_results.append(transformed)
                    if title:
                        existing_titles.add(title)
                    if gs_id:
                        existing_gs_ids.add(gs_id)
                    new_count += 1

        except Exception as e:
            print(f"\n[ERROR] Fatal error processing query: {e}")
            traceback.print_exc()
            continue

    # Save combined results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 80}")
    print("[OK] GOOGLE SCHOLAR HARVEST COMPLETE")
    print(f"{'=' * 80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {args.output}")
    print(f"End time: {datetime.now().isoformat()}")
    print(f"{'=' * 80}\n")

    if new_count > 0 and new_count <= 10:
        print("[NOTE] FREE TIER NOTE:")
        print("   EasyAPI free tier limited to 10 results per run")
        print(
            f"   For full {max_results} results, upgrade at https://apify.com/pricing"
        )
