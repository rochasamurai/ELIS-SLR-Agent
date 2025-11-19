"""
core_harvest.py
Harvests metadata from the CORE API (v3).
Reads queries from config/elis_search_queries.yml (protocol-aligned).

Environment Variables:
- CORE_API_KEY: Your CORE API key (required)

Outputs:
- JSON array in json_jsonl/ELIS_Appendix_A_Search_rows.json

Usage:
- Called by CI/CD workflow to retrieve search results for configured queries
"""

import requests
import json
import os
import yaml
import time
from pathlib import Path


def get_credentials():
    """Get and validate CORE API credentials."""
    api_key = os.getenv("CORE_API_KEY")

    if not api_key:
        raise EnvironmentError("Missing CORE_API_KEY environment variable")

    return api_key


def get_headers():
    """Build CORE API headers with credentials."""
    api_key = get_credentials()
    return {
        "Authorization": f"Bearer {api_key}",
    }


def core_search(query: str, limit: int = 100, max_results: int = 100):
    """
    Send a query to CORE API and retrieve up to max_results.

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

    while len(results) < max_results:
        params = {
            "q": query,
            "limit": min(limit, max_results - len(results)),
            "offset": offset,
        }

        try:
            r = requests.get(url, headers=get_headers(), params=params, timeout=30)

            if r.status_code != 200:
                print(f"Error {r.status_code}: {r.text[:200]}")
                break

            data = r.json()
            works = data.get("results", [])

            if not works:
                break

            results.extend(works)
            offset += len(works)

            # Check if we've reached the end
            total_hits = data.get("totalHits", 0)
            if offset >= total_hits:
                break

            # Rate limiting - be polite
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

    return results


def transform_core_entry(entry):
    """
    Transform raw CORE entry to match the schema used by other sources.
    """
    # Extract authors
    authors_list = entry.get("authors", [])
    if isinstance(authors_list, list):
        authors = ", ".join(
            [
                a.get("name", "")
                for a in authors_list
                if isinstance(a, dict) and a.get("name")
            ]
        )
    else:
        authors = ""

    # Extract year
    year = str(entry.get("yearPublished", ""))

    return {
        "source": "CORE",
        "title": entry.get("title", ""),
        "authors": authors,
        "year": year,
        "doi": entry.get("doi", ""),
        "abstract": entry.get("abstract", ""),
        "url": entry.get("downloadUrl", "")
        or entry.get("links", [{}])[0].get("url", ""),
        "core_id": entry.get("id", ""),
        "raw_metadata": entry,
    }


def load_config(config_path: str = "config/elis_search_queries.yml"):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_core_queries(config):
    """Extract enabled queries for CORE from config."""
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "core" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        # Remove quotes for CORE search
        core_queries = [q.replace('"', "") for q in topic_queries]
        queries.extend(core_queries)

    return queries


if __name__ == "__main__":
    # Load configuration
    print("Loading configuration from config/elis_search_queries.yml")
    config = load_config()

    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 100)

    # Get CORE queries
    queries = get_core_queries(config)

    if not queries:
        print("⚠️  No CORE queries found in config (check sources and enabled flags)")
        exit(0)

    print(f"Found {len(queries)} queries for CORE")

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
        print(f"\n[{i}/{len(queries)}] Querying CORE: {query}")

        try:
            raw_results = core_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_core_entry(entry)
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

    print("\n✅ CORE harvest complete")
    print(f"✅ New results added: {new_count}")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to {output_path}")
