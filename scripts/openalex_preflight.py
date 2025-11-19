"""
openalex_preflight.py
Test OpenAlex API access
"""

import requests

# OpenAlex API - no key required, polite pool recommended
url = "https://api.openalex.org/works"

params = {
    "filter": "title.search:electronic voting",
    "per_page": 1,
    "mailto": "elis@samurai.com.br",  # Polite pool - faster rate limits
}

print("Testing OpenAlex API access...")
print(f"Endpoint: {url}")
print("Note: No API key required (open access)")

response = requests.get(url, params=params, timeout=30)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    print("✅ API Access Successful!")
    data = response.json()

    meta = data.get("meta", {})
    count = meta.get("count", 0)
    print(f"Results found: {count}")

    results = data.get("results", [])
    if results:
        work = results[0]
        print("\nSample result:")
        print(f"  Title: {work.get('title', 'N/A')}")
        print(f"  Year: {work.get('publication_year', 'N/A')}")
        print(f"  Citations: {work.get('cited_by_count', 0)}")
else:
    print("❌ API Access Failed")
    print(f"Response: {response.text}")
