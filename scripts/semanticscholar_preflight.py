"""
semanticscholar_preflight.py
Test Semantic Scholar API access
"""

import os
import requests

# Semantic Scholar API key is optional but recommended
S2_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

# Test endpoint
url = "https://api.semanticscholar.org/graph/v1/paper/search"

headers = {}
if S2_API_KEY:
    headers["x-api-key"] = S2_API_KEY

params = {
    "query": "electronic voting",
    "limit": 1,
    "fields": "title,authors,year,abstract,citationCount",
}

print("Testing Semantic Scholar API access...")
print(f"Endpoint: {url}")
print(f"API Key: {'Provided' if S2_API_KEY else 'Not provided (using public access)'}")

response = requests.get(url, headers=headers, params=params, timeout=30)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    print("✅ API Access Successful!")
    data = response.json()
    total = data.get("total", 0)
    print(f"Results found: {total}")

    if data.get("data"):
        paper = data["data"][0]
        print("\nSample result:")
        print(f"  Title: {paper.get('title', 'N/A')}")
        print(f"  Year: {paper.get('year', 'N/A')}")
        print(f"  Citations: {paper.get('citationCount', 0)}")
else:
    print("❌ API Access Failed")
    print(f"Response: {response.text}")
