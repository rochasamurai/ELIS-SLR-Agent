"""
ieee_preflight.py
Test IEEE Xplore API access
"""

import os
import requests

IEEE_API_KEY = os.getenv("IEEE_API_KEY")

if not IEEE_API_KEY:
    raise EnvironmentError("Missing IEEE_API_KEY environment variable")

# Test endpoint
url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

params = {
    "apikey": IEEE_API_KEY,
    "querytext": "electronic voting",
    "max_records": 1,
}

print("Testing IEEE Xplore API access...")
print(f"Endpoint: {url}")

response = requests.get(url, params=params, timeout=30)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    print("✅ API Access Successful!")
    data = response.json()
    print(f"Results found: {data.get('total_records', 0)}")
else:
    print("❌ API Access Failed")
    print(f"Response: {response.text}")
