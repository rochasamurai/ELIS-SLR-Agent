"""
wos_preflight.py
Test Web of Science Starter API access
"""

import os
import requests

WOS_API_KEY = os.getenv("WEB_OF_SCIENCE_API_KEY")

if not WOS_API_KEY:
    raise EnvironmentError("Missing WEB_OF_SCIENCE_API_KEY environment variable")

# Test endpoint
url = "https://api.clarivate.com/apis/wos-starter/v1/documents"

headers = {
    "X-ApiKey": WOS_API_KEY,
    "Accept": "application/json",
}

# Simple test query
params = {
    "q": "TS=(electronic voting)",
    "limit": 1,
}

print("Testing Web of Science API access...")
print(f"Endpoint: {url}")

response = requests.get(url, headers=headers, params=params, timeout=30)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    print("✅ API Access Successful!")
    data = response.json()
    print(f"Results found: {data.get('metadata', {}).get('total', 0)}")
else:
    print("❌ API Access Failed")
    print(f"Response: {response.text}")
