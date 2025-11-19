"""
ieee_harvest.py
Harvests metadata from the IEEE Xplore API.
Reads queries from config/elis_search_queries.yml (protocol-aligned).

Environment Variables:
- IEEE_API_KEY: Your IEEE Xplore API key

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
    """Get and validate IEEE API credentials."""
    api_key = os.getenv("IEEE_API_KEY")

    if not api_key:
        raise EnvironmentError("Missing IEEE_API_KEY environment variable")

    return api_key


def ieee_search(query: str, max_records: int = 100):
    """
    Send a query to IEEE Xplore API and retrieve up to max_records.

    Args:
        query (str): IEEE query string
        max_records (int): Total number of results to retrieve (max 200 per call)

    Returns:
        list: List of metadata entries returned by IEEE
    """
    api_key = get_credentials()
    url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

    params = {
        "apikey": api_key,
        "querytext": query,
        "max_records": min(max_records, 200),  # IEEE API max is 200
        "start_record": 1,
    }

    r = requests.get(url, params=params, timeout=30)

    if r.status_code != 200:
        print(f"Error {r.status_code}: {r.text}")
        return []

    data = r.json()
    articles = data.get("articles", [])

    return articles


def transform_ieee_entry(entry):
    """
    Transform raw IEEE entry to match the schema used by other sources.
    """
    # Extract authors
    authors_list = entry.get("authors", {}).get("authors", [])
    authors = ", ".join(
        [a.get("full_name", "") for a in authors_list if a.get("full_name")]
    )

    # Extract publication year
    year = str(entry.get("publication_year", ""))

    return {
        "source": "IEEE Xplore",
        "title": entry.get("title", ""),
        "authors": authors,
        "year": year,
        "doi": entry.get("doi", ""),
        "abstract": entry.get("abstract", ""),
        "url": entry.get("pdf_url", "") or entry.get("html_url", ""),
        "ieee_id": entry.get("article_number", ""),
        "raw_metadata": entry,
    }


def load_config(config_path: str = "config/elis_search_queries.yml"):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_ieee_queries(config):
    """Extract enabled queries for IEEE from config."""
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


if __name__ == "__main__":
    # Load configuration
    print("Loading configuration from config/elis_search_queries.yml")
    config = load_config()

    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 100)

    # Get IEEE queries
    queries = get_ieee_queries(config)

    if not queries:
        print("⚠️  No IEEE queries found in config (check sources and enabled flags)")
        exit(0)

    print(f"Found {len(queries)} queries for IEEE Xplore")

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
        print(f"\n[{i}/{len(queries)}] Querying IEEE Xplore: {query}")

        try:
            raw_results = ieee_search(query, max_records=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_ieee_entry(entry)
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

    print("\n✅ IEEE Xplore harvest complete")
    print(f"✅ New results added: {new_count}")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to {output_path}")
