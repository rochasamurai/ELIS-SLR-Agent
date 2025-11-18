"""
wos_harvest.py
Harvests metadata from the Clarivate Web of Science Starter API.
Reads queries from config/elis_search_queries.yml (protocol-aligned).

Environment Variables:
- WEB_OF_SCIENCE_API_KEY: Your Clarivate API key

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
    """Get and validate Web of Science API credentials."""
    api_key = os.getenv("WEB_OF_SCIENCE_API_KEY")

    if not api_key:
        raise EnvironmentError("Missing WEB_OF_SCIENCE_API_KEY environment variable")

    return api_key


def get_headers():
    """Build Web of Science API headers with credentials."""
    api_key = get_credentials()
    return {
        "X-ApiKey": api_key,
        "Accept": "application/json",
    }


def wos_search(query: str, limit: int = 50, max_results: int = 100):
    """
    Send a query to Web of Science API and retrieve up to max_results.

    Args:
        query (str): WoS query string (e.g., "TS=(electronic voting)")
        limit (int): Number of records per request (max 50 for Starter API)
        max_results (int): Total number of results to retrieve

    Returns:
        list: List of metadata entries returned by WoS
    """
    url = "https://api.clarivate.com/apis/wos-starter/v1/documents"
    results = []
    page = 1

    while len(results) < max_results:
        params = {
            "q": query,
            "limit": min(limit, max_results - len(results)),
            "page": page,
        }

        r = requests.get(url, headers=get_headers(), params=params, timeout=30)

        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text}")
            break

        data = r.json()
        hits = data.get("hits", [])

        if not hits:
            break

        results.extend(hits)
        page += 1

        # Check if we've reached the last page
        metadata = data.get("metadata", {})
        total = metadata.get("total", 0)
        if len(results) >= total:
            break

    return results


def transform_wos_entry(entry):
    """
    Transform raw WoS entry to match the schema used by other sources.
    """
    # Extract authors from author field
    authors_list = entry.get("author", [])
    authors = ", ".join(
        [a.get("display_name", "") for a in authors_list if a.get("display_name")]
    )

    # Extract publication year
    pub_info = entry.get("source", {})
    year = str(pub_info.get("published_biblio_year", ""))

    return {
        "source": "Web of Science",
        "title": entry.get("title", ""),
        "authors": authors,
        "year": year,
        "doi": entry.get("doi", ""),
        "abstract": entry.get("abstract", {}).get("text", ""),
        "url": f"https://doi.org/{entry.get('doi', '')}" if entry.get("doi") else "",
        "wos_id": entry.get("uid", ""),
        "raw_metadata": entry,
    }


def load_config(config_path: str = "config/elis_search_queries.yml"):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_wos_queries(config):
    """Extract enabled queries for Web of Science from config."""
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "web_of_science" not in sources:
            continue

        # WoS uses different query syntax - wrap in TS=(...)
        topic_queries = topic.get("queries", [])
        # Convert queries to WoS syntax
        wos_queries = [f"TS=({q})" for q in topic_queries]
        queries.extend(wos_queries)

    return queries


if __name__ == "__main__":
    # Load configuration
    print("Loading configuration from config/elis_search_queries.yml")
    config = load_config()

    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 100)

    # Get WoS queries
    queries = get_wos_queries(config)

    if not queries:
        print(
            "⚠️  No Web of Science queries found in config (check sources and enabled flags)"
        )
        exit(0)

    print(f"Found {len(queries)} queries for Web of Science")

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
        print(f"\n[{i}/{len(queries)}] Querying Web of Science: {query}")

        try:
            raw_results = wos_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_wos_entry(entry)
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

    print("\n✅ Web of Science harvest complete")
    print(f"✅ New results added: {new_count}")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to {output_path}")
