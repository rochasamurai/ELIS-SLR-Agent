"""
scopus_harvest.py
Harvests metadata from the Elsevier Scopus API using institutional token and API key.
Reads queries from config/elis_search_queries.yml (protocol-aligned).

Environment Variables:
- SCOPUS_API_KEY: Your Elsevier API key
- SCOPUS_INST_TOKEN: Institutional token for full access

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage:
- Called by CI/CD workflow to retrieve search results for configured queries
"""

import requests
import json
import os
import yaml
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
        query (str): Scopus query string.
        count (int): Number of records per request (max 25).
        max_results (int): Total number of results to retrieve.

    Returns:
        list: List of metadata entries returned by Scopus.
    """
    url = "https://api.elsevier.com/content/search/scopus"
    results = []
    start = 0

    while start < max_results:
        params = {"query": query, "count": count, "start": start}
        r = requests.get(url, headers=get_headers(), params=params, timeout=30)

        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text}")
            break

        data = r.json()
        entries = data.get("search-results", {}).get("entry", [])

        if not entries:
            break

        results.extend(entries)
        start += count

    return results


def transform_scopus_entry(entry):
    """
    Transform raw Scopus entry to match the schema used by other sources.
    """
    return {
        "source": "Scopus",
        "title": entry.get("dc:title", ""),
        "authors": entry.get("dc:creator", ""),
        "year": (
            entry.get("prism:coverDate", "")[:4] if entry.get("prism:coverDate") else ""
        ),
        "doi": entry.get("prism:doi", ""),
        "abstract": entry.get("dc:description", ""),
        "url": entry.get("prism:url", ""),
        "scopus_id": entry.get("dc:identifier", "").replace("SCOPUS_ID:", ""),
        "raw_metadata": entry,
    }


def load_config(config_path: str = "config/elis_search_queries.yml"):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_scopus_queries(config):
    """Extract enabled queries for Scopus from config."""
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "scopus" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        queries.extend(topic_queries)

    return queries


if __name__ == "__main__":
    # Load configuration
    print("Loading configuration from config/elis_search_queries.yml")
    config = load_config()

    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 100)

    # Get Scopus queries
    queries = get_scopus_queries(config)

    if not queries:
        print("⚠️  No Scopus queries found in config (check sources and enabled flags)")
        exit(0)

    print(f"Found {len(queries)} queries for Scopus")

    # Define output path
    output_path = Path("json_jsonl/ELIS_Appendix_A_Search_rows.json")

    # Load existing results if file exists
    existing_results = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing_results = json.load(f)
        print(f"Loaded {len(existing_results)} existing results")

    # Track existing DOIs to avoid duplicates
    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    new_count = 0

    # Execute each query
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Querying Scopus: {query}")

        try:
            raw_results = scopus_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_scopus_entry(entry)
                doi = transformed.get("doi")

                if not doi or doi not in existing_dois:
                    existing_results.append(transformed)
                    if doi:
                        existing_dois.add(doi)
                    new_count += 1

        except Exception as e:
            print(f"  ❌ Error processing query: {e}")
            continue

    # Save combined results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)

    print("\n✅ Scopus harvest complete")
    print(f"✅ New results added: {new_count}")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to {output_path}")
