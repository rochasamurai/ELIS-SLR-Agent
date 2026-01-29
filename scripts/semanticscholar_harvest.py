"""
semanticscholar_harvest.py
Harvests metadata from the Semantic Scholar API.
Reads queries from config/elis_search_queries.yml (protocol-aligned).

Environment Variables:
- SEMANTIC_SCHOLAR_API_KEY: Optional API key (increases rate limits)

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
    """Get Semantic Scholar API key (optional)."""
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    return api_key


def get_headers():
    """Build Semantic Scholar API headers."""
    api_key = get_credentials()
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def semanticscholar_search(query: str, limit: int = 100, max_results: int = 100):
    """
    Send a query to Semantic Scholar API and retrieve up to max_results.

    Args:
        query (str): Search query string
        limit (int): Number of records per request (max 100)
        max_results (int): Total number of results to retrieve

    Returns:
        list: List of paper entries returned by Semantic Scholar
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    results = []
    offset = 0

    fields = "title,authors,year,venue,abstract,citationCount,externalIds"

    while len(results) < max_results:
        params = {
            "query": query,
            "limit": min(limit, max_results - len(results)),
            "offset": offset,
            "fields": fields,
        }

        r = requests.get(url, headers=get_headers(), params=params, timeout=30)

        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text}")
            break

        data = r.json()
        papers = data.get("data", [])

        if not papers:
            break

        results.extend(papers)
        offset += len(papers)

        # Rate limiting - be nice to the API
        time.sleep(1)

        # Check if we've reached the end
        total = data.get("total", 0)
        if offset >= total:
            break

    return results


def transform_semanticscholar_entry(entry):
    """
    Transform raw Semantic Scholar entry to match the schema used by other sources.
    """
    # Extract authors
    authors_list = entry.get("authors", [])
    authors = ", ".join([a.get("name", "") for a in authors_list if a.get("name")])

    # Extract year
    year = str(entry.get("year", ""))

    # Get DOI from externalIds or top level
    doi = entry.get("doi", "")
    if not doi:
        external_ids = entry.get("externalIds", {})
        doi = external_ids.get("DOI", "")

    return {
        "source": "Semantic Scholar",
        "title": entry.get("title", ""),
        "authors": authors,
        "year": year,
        "doi": doi,
        "abstract": entry.get("abstract", ""),
        "url": entry.get("url", ""),
        "s2_id": entry.get("paperId", ""),
        "citation_count": entry.get("citationCount", 0),
        "raw_metadata": entry,
    }


def load_config(config_path: str = "config/elis_search_queries.yml"):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_semanticscholar_queries(config):
    """Extract enabled queries for Semantic Scholar from config."""
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


if __name__ == "__main__":
    # Load configuration
    print("Loading configuration from config/elis_search_queries.yml")
    config = load_config()

    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 100)

    # Get Semantic Scholar queries
    queries = get_semanticscholar_queries(config)

    if not queries:
        print(
            "⚠️  No Semantic Scholar queries found in config (check sources and enabled flags)"
        )
        exit(0)

    print(f"Found {len(queries)} queries for Semantic Scholar")

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
        print(f"\n[{i}/{len(queries)}] Querying Semantic Scholar: {query}")

        try:
            raw_results = semanticscholar_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_semanticscholar_entry(entry)
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

    print("\n✅ Semantic Scholar harvest complete")
    print(f"✅ New results added: {new_count}")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to {output_path}")
