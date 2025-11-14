"""
scopus_harvest.py
Harvests metadata from the Elsevier Scopus API using institutional token and API key.
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
from pathlib import Path

# Retrieve credentials from environment
SCOPUS_API_KEY = os.getenv("SCOPUS_API_KEY")
SCOPUS_INST_TOKEN = os.getenv("SCOPUS_INST_TOKEN")

# Set Scopus API headers
HEADERS = {
    "X-ELS-APIKey": SCOPUS_API_KEY,
    "X-ELS-Insttoken": SCOPUS_INST_TOKEN,
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
        r = requests.get(url, headers=HEADERS, params=params)
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
        "year": entry.get("prism:coverDate", "")[:4] if entry.get("prism:coverDate") else "",
        "doi": entry.get("prism:doi", ""),
        "abstract": entry.get("dc:description", ""),
        "url": entry.get("prism:url", ""),
        "scopus_id": entry.get("dc:identifier", "").replace("SCOPUS_ID:", ""),
        "raw_metadata": entry
    }


if __name__ == "__main__":
    # Define output path (matches workflow expectation)
    output_path = Path("json_jsonl/ELIS_Appendix_A_Search_rows.json")
    
    # Load existing results if file exists
    existing_results = []
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing_results = json.load(f)
        print(f"Loaded {len(existing_results)} existing results")
    
    # Placeholder: future version will load dynamic config from config/elis_search_queries.yml
    query = "electronic voting AND transparency"
    print(f"Querying Scopus: {query}")
    
    # Fetch Scopus results
    raw_results = scopus_search(query, max_results=50)
    print(f"Retrieved {len(raw_results)} results from Scopus")
    
    # Transform to standard format
    scopus_results = [transform_scopus_entry(entry) for entry in raw_results]
    
    # Merge with existing results (avoid duplicates by DOI)
    existing_dois = {r.get("doi") for r in existing_results if r.get("doi")}
    new_count = 0
    
    for result in scopus_results:
        doi = result.get("doi")
        if not doi or doi not in existing_dois:
            existing_results.append(result)
            if doi:
                existing_dois.add(doi)
            new_count += 1
    
    # Save combined results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Scopus harvest complete: {new_count} new results added")
    print(f"✅ Total records in dataset: {len(existing_results)}")
    print(f"✅ Saved to {output_path}")
    