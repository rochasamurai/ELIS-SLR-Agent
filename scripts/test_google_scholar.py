"""
Test Google Scholar harvest script with benchmark-2 query
"""
import yaml
import sys
from pathlib import Path

# Ensure we can import from scripts
sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("GOOGLE SCHOLAR TEST - Benchmark 2 Query")
print("="*80)

# 1. Create test config
print("\n1. Creating test ELIS config...")
test_config = {
    'global': {
        'year_from': 2002,
        'year_to': 2023,
        'languages': ['en'],
        'max_results_per_source': 50,  # Limited for test
        'job_result_cap': 0
    },
    'topics': [{
        'id': 'benchmark_test_gs',
        'enabled': True,
        'description': 'Test Google Scholar with benchmark-2 query',
        'queries': ['("agile" AND "government") OR ("agile" AND "governance") OR ("agile" AND "public")'],
        'include_preprints': False,
        'sources': ['google_scholar']
    }]
}

# Write test config
config_path = Path("../config/elis_search_queries.yml")
with open(config_path, 'w', encoding='utf-8') as f:
    yaml.dump(test_config, f, default_flow_style=False)
print(f"   ✓ Config written to {config_path}")

# 2. Clear previous results
output_path = Path("../json_jsonl/ELIS_Appendix_A_Search_rows.json")
if output_path.exists():
    output_path.unlink()
    print("   ✓ Cleared previous results")

# 3. Run Google Scholar harvest
print("\n2. Running Google Scholar harvest...")
print("   This will take 5-10 minutes...")
print("-"*80)

import subprocess  # noqa: E402
result = subprocess.run(
    [sys.executable, "google_scholar_harvest.py"],
    cwd=str(Path(__file__).parent),
    capture_output=True,
    text=True,
    timeout=720  # 12 minute timeout
)

# 4. Display output
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# 5. Check results
print("\n" + "="*80)
print("TEST RESULTS")
print("="*80)

if result.returncode == 0:
    print("✓ Script completed successfully")
    
    if output_path.exists():
        import json
        with open(output_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        print(f"✓ Retrieved: {len(results)} results")
        
        if results:
            print("\nSample result:")
            sample = results[0]
            print(f"   Title: {sample.get('title', 'N/A')[:80]}...")
            print(f"   Authors: {sample.get('authors', 'N/A')[:50]}...")
            print(f"   Year: {sample.get('year', 'N/A')}")
            print(f"   Source: {sample.get('source', 'N/A')}")
        
        if len(results) > 0:
            print("\n" + "="*80)
            print("✅ GOOGLE SCHOLAR TEST PASSED")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("⚠️  GOOGLE SCHOLAR RETURNED 0 RESULTS")
            print("="*80)
    else:
        print("❌ No output file generated")
else:
    print(f"❌ Script failed with return code {result.returncode}")

print("\nTest complete.")