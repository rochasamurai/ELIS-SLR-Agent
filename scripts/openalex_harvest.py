"""
openalex_harvest.py
Harvests metadata from the OpenAlex API.
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


def openalex_search(query: str, per_page: int = 100, max_results: int = 100):
    """
    Send a query to OpenAlex API and retrieve up to max_results.

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

    # Get contact email for polite pool
    mailto = os.getenv("ELIS_CONTACT")
    if not mailto:
      print("⚠️  Warning: ELIS_CONTACT not set. Using polite pool recommended for better rate limits.")
      mailto = None

    while len(results) < max_results:
        params = {
            # Use default.search to search across title, abstract, and fulltext
            # This matches Tai & Awasthi's methodology (title, abstract, keywords)
            "filter": f"default.search:{query}",
            "per_page": min(per_page, max_results - len(results)),
            "page": page,        
        }
        # Only add mailto if ELIS_CONTACT is set (for polite pool access)
        if mailto:
            params["mailto"] = mailto

        r = requests.get(url, params=params, timeout=30)

        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text}")
            break

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
            break

        # Rate limiting - be polite
        time.sleep(0.1)

    return results


def transform_openalex_entry(entry):
    """
    Transform raw OpenAlex entry to match the schema used by other sources.
    """
    # Extract authors
    authorships = entry.get("authorships", [])
    authors = ", ".join(
        [
            a.get("author", {}).get("display_name", "")
            for a in authorships
            if a.get("author", {}).get("display_name")
        ]
    )

    # Extract year
    year = str(entry.get("publication_year", ""))

    # Extract DOI
    doi = entry.get("doi", "")
    if doi and doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")

    # Extract abstract (inverted index format)
    abstract_inverted = entry.get("abstract_inverted_index", {})
    abstract = ""
    if abstract_inverted:
        # Reconstruct abstract from inverted index
        words = {}
        for word, positions in abstract_inverted.items():
            for pos in positions:
                words[pos] = word
        abstract = " ".join([words[i] for i in sorted(words.keys())])

    return {
        "source": "OpenAlex",
        "title": entry.get("title", ""),
        "authors": authors,
        "year": year,
        "doi": doi,
        "abstract": abstract,
        "url": entry.get("doi", "") or entry.get("id", ""),
        "openalex_id": entry.get("id", ""),
        "citation_count": entry.get("cited_by_count", 0),
        "raw_metadata": entry,
    }


def load_config(config_path: str = "config/elis_search_queries.yml"):
    """Load search configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_openalex_queries(config):
    """Extract enabled queries for OpenAlex from config."""
    queries = []

    for topic in config.get("topics", []):
        if not topic.get("enabled", False):
            continue

        sources = topic.get("sources", [])
        if "openalex" not in sources:
            continue

        topic_queries = topic.get("queries", [])
        # Remove quotes for OpenAlex search
        openalex_queries = [q.replace('"', "") for q in topic_queries]
        queries.extend(openalex_queries)

    return queries


if __name__ == "__main__":
    # Load configuration
    print("Loading configuration from config/elis_search_queries.yml")
    config = load_config()

    # Extract global settings
    global_config = config.get("global", {})
    max_results = global_config.get("max_results_per_source", 100)

    # Get OpenAlex queries
    queries = get_openalex_queries(config)

    if not queries:
        print(
            "⚠️  No OpenAlex queries found in config (check sources and enabled flags)"
        )
        exit(0)

    print(f"Found {len(queries)} queries for OpenAlex")

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
        print(f"\n[{i}/{len(queries)}] Querying OpenAlex: {query}")

        try:
            raw_results = openalex_search(query, max_results=max_results)
            print(f"  Retrieved {len(raw_results)} results")

            # Transform and add results
            for entry in raw_results:
                transformed = transform_openalex_entry(entry)
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

    print("\n✅ OpenAlex harvest complete")
    print(f"✅ New results added: {new_count}")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to {output_path}")
