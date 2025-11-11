"""
scopus_harvest.py

Harvests metadata from the Elsevier Scopus API using institutional token and API key.

Environment Variables:
- SCOPUS_API_KEY: Your Elsevier API key
- SCOPUS_INST_TOKEN: Institutional token for full access

Outputs:
- JSONL file in imports/scopus_sample.jsonl (one JSON object per line)

Usage:
- Called by CI/CD workflow to retrieve search results for configured queries
- Intended to be integrated into elis-agent-search.yml in future iterations
"""

import requests
import json
import os

# Retrieve credentials from environment
SCOPUS_API_KEY = os.getenv("SCOPUS_API_KEY")
SCOPUS_INST_TOKEN = os.getenv("SCOPUS_INST_TOKEN")

# Set Scopus API headers
HEADERS = {
    "X-ELS-APIKey": SCOPUS_API_KEY,
    "X-ELS-Insttoken": SCOPUS_INST_TOKEN,
    "Accept": "application/json"
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
        params = {
            "query": query,
            "count": count,
            "start": start
        }
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

if __name__ == "__main__":
    # Placeholder: future version will load dynamic config from json_jsonl/config/
    query = "electronic voting AND transparency"
    results = scopus_search(query, max_results=50)

    output_path = "imports/scopus_sample.jsonl"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")

    print(f"✅ Scopus harvest complete: {len(results)} results saved to {output_path}")
