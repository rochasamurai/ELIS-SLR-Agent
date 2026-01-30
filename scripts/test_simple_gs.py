from apify_client import ApifyClient
import os

client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

# ULTRA SIMPLE - just one word
run_input = {
    "keyword": "agile",
    "maxItems": 10,
    "proxyOptions": {"useApifyProxy": True}
}

print("Testing with single word: 'agile'")
run = client.actor("marco.gullo/google-scholar-scraper").call(run_input=run_input)
dataset = client.dataset(run['defaultDatasetId'])
results = list(dataset.iterate_items())
print(f"Results: {len(results)}")
if results:
    print(f"First result: {results[0].get('title', 'N/A')}")
    