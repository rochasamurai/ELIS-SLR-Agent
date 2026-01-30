"""
Test simple Google Scholar query with EasyAPI actor.
Tests if the alternative actor can bypass rate limits.
"""
from apify_client import ApifyClient
import os

# Initialize client
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

print("="*80)
print("TESTING EASYAPI GOOGLE SCHOLAR ACTOR")
print("="*80)

# Test 1: Ultra simple query
print("\nTest 1: Single word query")
print("-"*80)

run_input = {
    "query": "agile",
    "maxItems": 100  # EasyAPI requires minimum 100
}

print(f"Actor: easyapi/google-scholar-scraper")
print(f"Query: {run_input['query']}")
print(f"Max items: {run_input['maxItems']}")
print("\nStarting run...")

try:
    run = client.actor("easyapi/google-scholar-scraper").call(run_input=run_input)
    
    print(f"\n✓ Run completed")
    print(f"  Run ID: {run['id']}")
    print(f"  Status: {run['status']}")
    print(f"  Run URL: https://console.apify.com/actors/runs/{run['id']}")
    
    # Get results
    dataset = client.dataset(run['defaultDatasetId'])
    results = list(dataset.iterate_items())
    
    print(f"\n📊 RESULTS:")
    print(f"  Total: {len(results)}")
    
    if results:
        print(f"\n✅ SUCCESS! Retrieved {len(results)} results")
        print(f"\nFirst result sample:")
        first = results[0]
        print(f"  Title: {first.get('title', 'N/A')[:80]}...")
        print(f"  Authors: {first.get('authors', 'N/A')[:60]}...")
        print(f"  Year: {first.get('year', 'N/A')}")
        print(f"  Citations: {first.get('citations', 'N/A')}")
    else:
        print(f"\n❌ FAILED: 0 results (possibly rate limited)")
        
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)