#!/usr/bin/env python3
"""
Google Scholar Harvester via Apify

Uses Apify's Google Scholar Scraper to access Google Scholar data.
Requires APIFY_API_TOKEN environment variable.

Author: Carlos Rocha
Date: 2026-01-26
"""

import os
import sys
import json
import time
import requests
from typing import List, Dict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def google_scholar_search(
    query: str, max_items: int = 200, newer_than: int = None, older_than: int = None
) -> List[Dict]:
    """
    Search Google Scholar via Apify scraper (async with polling).
    """

    # Get API token from environment
    api_token = os.environ.get("APIFY_API_TOKEN")
    if not api_token:
        raise ValueError("APIFY_API_TOKEN environment variable not set")

    # 1. START THE RUN
    start_url = "https://api.apify.com/v2/acts/marco.gullo~google-scholar-scraper/runs"

    params = {"token": api_token}

    payload = {
        "keyword": query,
        "maxItems": max_items,
        "filter": "all",
        "sortBy": "relevance",
        "articleType": "any",
        "proxyOptions": {"useApifyProxy": True},
    }

    if newer_than:
        payload["newerThan"] = newer_than
    if older_than:
        payload["olderThan"] = older_than

    print("\n🔍 Searching Google Scholar via Apify...")
    print(f"   Query: {query}")
    print(f"   Max items: {max_items}")
    if newer_than:
        print(f"   Newer than: {newer_than}")
    if older_than:
        print(f"   Older than: {older_than}")

    try:
        # Start the run
        print("  Starting Apify run...")
        response = requests.post(start_url, params=params, json=payload, timeout=30)
        response.raise_for_status()

        run_info = response.json()
        run_id = run_info["data"]["id"]
        dataset_id = run_info["data"]["defaultDatasetId"]

        print(f"  Run started: {run_id}")
        print("  Waiting for completion...")

        # 2. POLL FOR COMPLETION
        max_wait = 420  # 7 minutes max (Google Scholar can be slow)
        waited = 0
        retry_count = 0
        max_retries = 3

        while waited < max_wait:
            time.sleep(10)  # Check every 10 seconds
            waited += 10

            # Check run status
            status_url = f"https://api.apify.com/v2/acts/marco.gullo~google-scholar-scraper/runs/{run_id}"

            try:
                status_resp = requests.get(status_url, params=params, timeout=30)
                status_resp.raise_for_status()

                # Reset retry count on successful request
                retry_count = 0

            except requests.exceptions.HTTPError as e:
                if e.response and e.response.status_code == 502:
                    retry_count += 1
                    print(
                        f"  ⚠️ Apify gateway error (502), retry {retry_count}/{max_retries}..."
                    )
                    if retry_count < max_retries:
                        time.sleep(5)  # Wait a bit longer before retry
                        continue
                    else:
                        print("  ❌ Max retries reached, giving up")
                        return []
                else:
                    print(f"  ❌ HTTP Error: {e}")
                    return []
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️ Request error: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)
                    continue
                else:
                    return []

            status_data = status_resp.json()
            status = status_data["data"]["status"]

            if status == "SUCCEEDED":
                print(f"  ✓ Run completed after {waited}s")
                break
            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                print(f"  ❌ Run {status}")
                return []
            else:
                print(f"  ⏳ Status: {status} ({waited}s elapsed)")

        if status != "SUCCEEDED":
            print("  ⚠️ Timeout waiting for results")
            return []

        # 3. GET RESULTS FROM DATASET
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        dataset_resp = requests.get(dataset_url, params=params, timeout=30)
        dataset_resp.raise_for_status()

        results = dataset_resp.json()

        # DEBUG: Print first result structure
        # if results:
        #     print("\n📋 DEBUG - Raw API response (first item):")
        #     import json
        #     print(json.dumps(results[0], indent=2))

        print(f"  ✓ Found {len(results)} results from Google Scholar")
        return results

    except requests.exceptions.Timeout:
        print("  ⚠️ Request timeout")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ HTTP Error: {e}")
        print(f"  Response: {e.response.text if e.response else 'No response'}")
        return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return []


def transform_google_scholar_entry(entry: Dict) -> Dict:
    """
    Transform Apify Google Scholar result to standard format.

    Apify returns:
    - title
    - authors (string, not list)
    - year (integer)
    - publication
    - searchMatch (snippet/abstract)
    - link
    - documentLink (PDF)
    - citations (count)
    - fullAttribution
    """

    # Parse authors - Apify returns as string
    authors_str = entry.get("authors", "")
    authors = [authors_str] if authors_str else []

    return {
        "id": entry.get("cidCode", "unknown"),
        "title": entry.get("title", ""),
        "authors": authors,
        "year": entry.get("year"),
        "venue": entry.get("publication", ""),
        "abstract": entry.get("searchMatch", ""),
        "doi": None,  # Google Scholar doesn't provide DOI directly
        "url": entry.get("link", ""),
        "pdf_url": entry.get("documentLink"),
        "cited_by_count": entry.get("citations", 0),
        "source_id": entry.get("cidCode", ""),
        "full_attribution": entry.get("fullAttribution", ""),
    }


def main():
    """Test the Google Scholar harvester."""

    # Test query
    query = 'e-voting OR "electronic voting" adoption'

    print("=" * 70)
    print("Testing Google Scholar Harvester (Apify)")
    print("=" * 70)

    # Search
    results = google_scholar_search(
        query, max_items=50, newer_than=2005, older_than=2020
    )

    # Transform
    transformed = [transform_google_scholar_entry(r) for r in results]

    print(f"\n✓ Transformed {len(transformed)} results")

    # Show sample
    if transformed:
        print("\nSample result:")
        print(json.dumps(transformed[0], indent=2))

    print("\n" + "=" * 70)
    print("Test complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
