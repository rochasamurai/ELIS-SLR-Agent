"""
core_preflight.py
Test CORE API access
"""

import os
import requests

# CORE API - requires API key
CORE_API_KEY = os.getenv("CORE_API_KEY")

if not CORE_API_KEY:
    print("⚠️  CORE_API_KEY not set - trying without key (limited access)")

# Test endpoint (v3 API)
url = "https://api.core.ac.uk/v3/search/works"

headers = {}
if CORE_API_KEY:
    headers["Authorization"] = f"Bearer {CORE_API_KEY}"

params = {
    "q": "electronic voting",
    "limit": 1,
}

print("Testing CORE API access...")
print(f"Endpoint: {url}")
print(f"API Key: {'Provided' if CORE_API_KEY else 'Not provided (limited access)'}")

response = requests.get(url, headers=headers, params=params, timeout=30)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    print("✅ API Access Successful!")
    data = response.json()

    total_hits = data.get("totalHits", 0)
    print(f"Results found: {total_hits}")

    results = data.get("results", [])
    if results:
        work = results[0]
        print("\nSample result:")
        print(f"  Title: {work.get('title', 'N/A')}")
        print(f"  Year: {work.get('yearPublished', 'N/A')}")
        print(f"  DOI: {work.get('doi', 'N/A')}")
else:
    print("❌ API Access Failed")
    print(f"Response: {response.text}")
