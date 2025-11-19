"""
crossref_preflight.py
Test CrossRef API access
"""

import requests

# CrossRef API - no key required, polite requests recommended
url = "https://api.crossref.org/works"

params = {
    "query": "electronic voting",
    "rows": 1,
    "mailto": "elis@samurai.com.br",  # Polite pool
}

print("Testing CrossRef API access...")
print(f"Endpoint: {url}")
print("Note: No API key required (open access)")

response = requests.get(url, params=params, timeout=30)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    print("✅ API Access Successful!")
    data = response.json()

    message = data.get("message", {})
    total_results = message.get("total-results", 0)
    print(f"Results found: {total_results}")

    items = message.get("items", [])
    if items:
        work = items[0]
        print("\nSample result:")
        print(
            f"  Title: {work.get('title', ['N/A'])[0] if work.get('title') else 'N/A'}"
        )
        print(f"  DOI: {work.get('DOI', 'N/A')}")
        print(
            f"  Published: {work.get('published-print', {}).get('date-parts', [[None]])[0][0] if work.get('published-print') else 'N/A'}"
        )
else:
    print("❌ API Access Failed")
    print(f"Response: {response.text}")
