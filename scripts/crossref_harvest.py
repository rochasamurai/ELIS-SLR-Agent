"""
crossref_harvest.py
Harvests metadata from the CrossRef API.
Reads queries from config/elis_search_queries.yml (protocol-aligned).

Environment Variables:
- ELIS_CONTACT: Email for polite pool (faster rate limits)

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


def crossref_search(query: str, rows: int = 100, max_results: int = 100):
    """
    Send a query to CrossRef API and retrieve up to max_results.

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

    # Get contact email for polite pool
    mailto = os.getenv("ELIS_CONTACT", "elis@samurai.com.br")

    while len(results) < max_results:
        params = {
            "query": query,
            "rows": min(rows, max_results - len(results)),
            "offset": offset,
            "mailto": mailto,
        }

        r = requests.get(url, params=params, timeout=30)

        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text}")
            break

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
            break

        # Rate limiting - be polite
        time.sleep(0.5)

    return results


def transform_crossref_entry(entry):
    """
    Transform raw CrossRef entry to match the schema used by other sources.
    """
    # Extract title
    title_list = entry.get("title", [])
    title = title_list[0] if title_list else ""

    # Extract authors
    authors_list = entry.get("author", [])
    authors = ", ".join(
        [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in authors_list
            if a.get("family")
        ]
    )

    # Extract year
    year = ""
    published = entry.get("published-print") or entry.get("published-online")
    if published:
        date_parts = published.get("date-parts", [[]])
        if date_parts and date_parts[0]:
            year = str(date_parts[0][0])

    # Extract abstract
    abstract = entry.get("abstract", "")

    return {
        "source": "CrossRef",
        "title": title,
        "authors": authors,
        "year": year,
        "doi": entry.get("DOI", ""),
        "abstract": abstract,
        "url": entry.get("URL", ""),
        "crossref_type": entry.get("type", ""),
        "publisher": entry.get("publisher", ""),
        "raw_metadata": entry,
    }


def load_config(config_path: str = "config/elis_search_queries.yml"):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_crossref_queries(config):
    """Extract enabled queries for CrossRef from config."""
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "crossref" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        # Remove quotes for CrossRef search
        crossref_queries = [q.replace('"', "") for q in topic_queries]
        queries.extend(crossref_queries)

    return queries


if __name__ == "__main__":
    # Load configuration
    print("Loading configuration from config/elis_search_queries.yml")
    config = load_config()

    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 100)

    # Get CrossRef queries
    queries = get_crossref_queries(config)

    if not queries:
        print(
            "⚠️  No CrossRef queries found in config (check sources and enabled flags)"
        )
        exit(0)

    print(f"Found {len(queries)} queries for CrossRef")

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
        print(f"\n[{i}/{len(queries)}] Querying CrossRef: {query}")

        try:
            raw_results = crossref_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_crossref_entry(entry)
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

    print("\n✅ CrossRef harvest complete")
    print(f"✅ New results added: {new_count}")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to {output_path}")
