"""
sciencedirect_harvest.py
Harvests metadata from the Elsevier ScienceDirect Search API V2.

CONFIGURATION MODES:
1. NEW (Recommended): --search-config config/searches/electoral_integrity_search.yml
2. LEGACY (Backwards Compatible): Reads from config/elis_search_queries.yml

Environment Variables:
- SCIENCEDIRECT_API_KEY: Your Elsevier API key
- SCIENCEDIRECT_INST_TOKEN: Institutional token for full access

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json
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
    """Get and validate ScienceDirect API credentials."""
    api_key = os.getenv("SCIENCEDIRECT_API_KEY")
    inst_token = os.getenv("SCIENCEDIRECT_INST_TOKEN")

    if not api_key or not inst_token:
        raise EnvironmentError(
            "Missing SCIENCEDIRECT_API_KEY or SCIENCEDIRECT_INST_TOKEN environment variables"
        )

    return api_key, inst_token


def get_headers():
    """Build ScienceDirect API headers with credentials."""
    api_key, inst_token = get_credentials()
    return {
        "X-ELS-APIKey": api_key,
        "X-ELS-Insttoken": inst_token,
        "Accept": "application/json",
    }


def sciencedirect_search(query: str, count: int = 25, max_results: int = 100):
    """
    Send a query to ScienceDirect Search API and retrieve up to max_results.

    Args:
        query (str): Boolean query string.
        count (int): Number of records per request (10/25/50/100).
        max_results (int): Total number of results to retrieve.

    Returns:
        list: List of metadata entries returned by ScienceDirect.
    """
    url = "https://api.elsevier.com/content/search/sciencedirect"
    results = []
    start = 0
    retry_count = 0
    max_retries = 5

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
                wait_time = 5 * retry_count
                print(
                    f"  Rate limited (429). Waiting {wait_time}s before retry ({retry_count}/{max_retries})..."
                )
                time.sleep(wait_time)
                continue

            if r.status_code != 200:
                print(f"  Error {r.status_code}: {r.text[:200]}")
                break

            retry_count = 0

            data = r.json()
            entries = data.get("search-results", {}).get("entry", [])

            if not entries:
                break

            results.extend(entries)
            start += count

            total_results = int(
                data.get("search-results", {}).get("opensearch:totalResults", 0)
            )
            if len(results) >= total_results:
                print(f"  Retrieved all {total_results} available results")
                break

            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
            break

    return results


def transform_sciencedirect_entry(entry):
    """
    Transform raw ScienceDirect entry to match the schema used by other sources.
    """
    # Best-effort identifier
    scidir_id = entry.get("dc:identifier", "") or entry.get("pii", "") or ""

    creator = entry.get("dc:creator", "") or ""
    authors = [creator] if creator else []

    year = None
    cover_date = entry.get("prism:coverDate", "")
    if cover_date and len(cover_date) >= 4:
        try:
            year = int(cover_date[:4])
        except (ValueError, TypeError):
            year = None

    return {
        "source": "ScienceDirect",
        "title": entry.get("dc:title", "") or "",
        "authors": authors,
        "year": year,
        "doi": entry.get("prism:doi", "") or "",
        "abstract": entry.get("dc:description", "") or "",
        "url": entry.get("prism:url", "") or "",
        "sciencedirect_id": scidir_id,
        "raw_metadata": entry,
    }


def load_config(config_path: str):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_sciencedirect_queries_legacy(config):
    """
    Extract enabled queries for ScienceDirect from legacy config format.
    """
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "sciencedirect" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        queries.extend(topic_queries)

    return queries


def get_sciencedirect_config_new(config, tier=None):
    """
    Extract ScienceDirect configuration from new search config format.
    """
    databases = config.get("databases", [])
    sd_config = None

    for db in databases:
        if db.get("name") == "ScienceDirect" and db.get("enabled", False):
            sd_config = db
            break

    if not sd_config:
        print("[WARNING] ScienceDirect not enabled in search configuration")
        return [], 0

    query_config = config.get("query", {})
    query_string = query_config.get("boolean_string", "")
    if not query_string:
        print("[WARNING] No query found in search configuration")
        return [], 0

    query_wrapper = sd_config.get("query_wrapper", "{query}")
    sd_query = query_wrapper.replace("{query}", query_string)
    print("Query for ScienceDirect:")
    print(f"  Query: {sd_query[:100]}{'...' if len(sd_query) > 100 else ''}")

    max_results_config = sd_config.get("max_results")

    if isinstance(max_results_config, dict):
        if tier:
            max_results = max_results_config.get(tier)
            if max_results is None:
                print(
                    f"[WARNING] Unknown tier '{tier}', available tiers: {list(max_results_config.keys())}"
                )
                tier = sd_config.get("max_results_default", "production")
                max_results = max_results_config.get(tier, 1000)
                print(f"   Using default tier: {tier}")
        else:
            tier = sd_config.get("max_results_default", "production")
            max_results = max_results_config.get(tier, 1000)
            print(f"Using default tier: {tier} (max_results: {max_results})")
    else:
        max_results = max_results_config or 1000

    return [sd_query], max_results


def parse_args():
    parser = argparse.ArgumentParser(
        description="Harvest metadata from ScienceDirect Search API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--search-config", type=str)
    parser.add_argument(
        "--tier",
        type=str,
        choices=["testing", "pilot", "benchmark", "production", "exhaustive"],
    )
    parser.add_argument("--max-results", type=int)
    parser.add_argument(
        "--output", type=str, default="json_jsonl/ELIS_Appendix_A_Search_rows.json"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.search_config:
        print(f"Loading search configuration from {args.search_config}")
        config = load_config(args.search_config)
        queries, max_results = get_sciencedirect_config_new(config, tier=args.tier)
        config_mode = "NEW"
    else:
        print("Loading configuration from config/elis_search_queries.yml (legacy mode)")
        config = load_config("config/elis_search_queries.yml")
        queries = get_sciencedirect_queries_legacy(config)
        max_results = config.get("global", {}).get("max_results_per_source", 100)
        config_mode = "LEGACY"
        print(
            "[WARNING] Using legacy config format. Consider using --search-config for new projects."
        )

    if args.max_results:
        print(f"Overriding max_results: {max_results} -> {args.max_results}")
        max_results = args.max_results

    if not queries:
        print("[WARNING] No ScienceDirect queries found in config")
        print("   Check that ScienceDirect is enabled and queries are defined")
        exit(1)

    print(f"\n{'='*80}")
    print(f"SCIENCEDIRECT HARVEST - {config_mode} CONFIG")
    print(f"{'='*80}")
    print(f"Queries: {len(queries)}")
    print(f"Max results per query: {max_results}")
    print(f"Output: {args.output}")
    print(f"{'='*80}\n")

    output_path = Path(args.output)

    existing_results = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing_results = json.load(f)
        print(f"Loaded {len(existing_results)} existing results")

    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    existing_sd_ids = {
        r.get("sciencedirect_id") for r in existing_results if r.get("sciencedirect_id")
    }
    new_count = 0

    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying ScienceDirect:")
        print(f"  Query: {query[:100]}{'...' if len(query) > 100 else ''}")

        try:
            raw_results = sciencedirect_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            for entry in raw_results:
                transformed = transform_sciencedirect_entry(entry)
                doi = transformed.get("doi")
                sd_id = transformed.get("sciencedirect_id")

                is_duplicate = False
                if doi and doi in existing_dois:
                    is_duplicate = True
                if sd_id and sd_id in existing_sd_ids:
                    is_duplicate = True

                if not is_duplicate:
                    existing_results.append(transformed)
                    if doi:
                        existing_dois.add(doi)
                    if sd_id:
                        existing_sd_ids.add(sd_id)
                    new_count += 1

        except Exception as e:
            print(f"  Error processing query: {e}")
            traceback.print_exc()
            continue

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print("[OK] ScienceDirect harvest complete")
    print(f"{'='*80}")
    print(f"New results added: {new_count}")
    print(f"Total records in dataset: {len(existing_results)}")
    print(f"Saved to: {output_path}")
    print(f"{'='*80}\n")
