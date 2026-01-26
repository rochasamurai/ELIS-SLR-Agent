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


def google_scholar_search(query: str, max_items: int = 200, 
                         newer_than: int = None, older_than: int = None) -> List[Dict]:
    """
    Search Google Scholar via Apify scraper.
    
    Args:
        query: Search query string
        max_items: Maximum number of results (default 200)
        newer_than: Only articles from this year onwards
        older_than: Only articles up to this year
        
    Returns:
        List of article dictionaries
    """
    
    # Get API token from environment
    api_token = os.environ.get('APIFY_API_TOKEN')
    if not api_token:
        raise ValueError("APIFY_API_TOKEN environment variable not set")
    
    # Prepare API request
    url = "https://api.apify.com/v2/acts/marco.gullo~google-scholar-scraper/run-sync-get-dataset-items"
    
    params = {
        'token': api_token
    }
    
    payload = {
        'keyword': query,
        'maxItems': max_items,
        'filter': 'all',
        'sortBy': 'relevance',
        'articleType': 'any',
        'proxyOptions': {
            'useApifyProxy': True
        }
    }
    
    # Add year filters if provided
    if newer_than:
        payload['newerThan'] = newer_than
    if older_than:
        payload['olderThan'] = older_than
    
    print(f"\n🔍 Searching Google Scholar via Apify...")
    print(f"   Query: {query}")
    print(f"   Max items: {max_items}")
    if newer_than:
        print(f"   Newer than: {newer_than}")
    if older_than:
        print(f"   Older than: {older_than}")
    
    try:
        # Make API request (this waits for completion and returns results)
        response = requests.post(url, params=params, json=payload, timeout=300)
        response.raise_for_status()
        
        results = response.json()
        
        print(f"  ✓ Found {len(results)} results from Google Scholar")
        return results
        
    except requests.exceptions.Timeout:
        print(f"  ⚠️ Request timeout (Google Scholar search took >5 minutes)")
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
    - full_attribution (contains authors)
    - year (need to extract)
    - snippet (abstract)
    - displayed_link
    - pdf_link
    - url
    - cited_by_count
    - related_articles_link
    """
    
    # Extract year from various possible locations
    year = None
    full_attr = entry.get('full_attribution', '')
    
    # Try to extract year from full_attribution (e.g., "Author - Journal, 2020 - publisher")
    import re
    year_match = re.search(r'\b(19|20)\d{2}\b', full_attr)
    if year_match:
        year = int(year_match.group(0))
    
    # Extract authors from full_attribution
    # Format is typically: "Author1, Author2 - Journal, Year - Publisher"
    authors = []
    if full_attr:
        # Take everything before the first dash
        author_part = full_attr.split(' - ')[0] if ' - ' in full_attr else full_attr
        authors = [author_part]  # Simplified, could parse more
    
    # Extract venue/journal
    venue = ''
    if ' - ' in full_attr:
        parts = full_attr.split(' - ')
        if len(parts) >= 2:
            venue = parts[1].split(',')[0].strip()
    
    return {
        'id': entry.get('id', 'unknown'),
        'title': entry.get('title', ''),
        'authors': authors,
        'year': year,
        'venue': venue,
        'abstract': entry.get('snippet', ''),
        'doi': None,  # Google Scholar doesn't always provide DOI
        'url': entry.get('url', ''),
        'pdf_url': entry.get('pdf_link'),
        'cited_by_count': entry.get('cited_by_count', 0),
        'source_id': entry.get('id', ''),
        'full_attribution': full_attr
    }


def main():
    """Test the Google Scholar harvester."""
    
    # Test query
    query = 'e-voting OR "electronic voting" adoption'
    
    print("="*70)
    print("Testing Google Scholar Harvester (Apify)")
    print("="*70)
    
    # Search
    results = google_scholar_search(query, max_items=50, newer_than=2005, older_than=2020)
    
    # Transform
    transformed = [transform_google_scholar_entry(r) for r in results]
    
    print(f"\n✓ Transformed {len(transformed)} results")
    
    # Show sample
    if transformed:
        print("\nSample result:")
        print(json.dumps(transformed[0], indent=2))
    
    print("\n" + "="*70)
    print("Test complete")
    print("="*70)


if __name__ == '__main__':
    main()
    