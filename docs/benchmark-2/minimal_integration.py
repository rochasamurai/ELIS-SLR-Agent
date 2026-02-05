"""Minimal working integration - Test with OpenAlex"""

import yaml
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path.cwd().parents[1]
CONFIG_DIR = REPO_ROOT / "config"
SCRIPTS_DIR = REPO_ROOT / "scripts"
OUTPUT_FILE = REPO_ROOT / "json_jsonl" / "ELIS_Appendix_A_Search_rows.json"

print("=" * 80)
print("MINIMAL BENCHMARK INTEGRATION TEST")
print("=" * 80)
print(f"\nRepo root: {REPO_ROOT}")
print(f"Config dir: {CONFIG_DIR}")
print(f"Scripts dir: {SCRIPTS_DIR}")

# Load benchmark config
print("\n1. Loading benchmark config...")
with open("configs/benchmark_2_config.yaml", "r", encoding="utf-8") as f:
    bench_config = yaml.safe_load(f)
print(f"   ✓ Loaded: {bench_config['benchmark']['id']}")

# Create simple ELIS config for OpenAlex
print("\n2. Creating ELIS config for OpenAlex...")
query = bench_config["search_strategy"]["query_string"].strip()
start_year = int(bench_config["search_strategy"]["date_range"]["start"].split("-")[0])
end_year = int(bench_config["search_strategy"]["date_range"]["end"].split("-")[0])

elis_config = {
    "global": {
        "year_from": start_year,
        "year_to": end_year,
        "languages": ["en"],
        "max_results_per_source": 100,
        "job_result_cap": 0,
    },
    "topics": [
        {
            "id": "benchmark_test",
            "enabled": True,
            "description": "Benchmark test query",
            "queries": [query],
            "include_preprints": False,
            "sources": ["openalex"],
        }
    ],
}

# Write ELIS config
elis_config_file = CONFIG_DIR / "elis_search_queries.yml"
print(f"   Writing to: {elis_config_file}")
with open(elis_config_file, "w", encoding="utf-8") as f:
    yaml.dump(elis_config, f, default_flow_style=False)
print("   ✓ Config written")

# Clear previous results
if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()
    print(f"   ✓ Cleared previous results")

# Run OpenAlex harvest
print("\n3. Running OpenAlex harvest script...")
script_path = SCRIPTS_DIR / "openalex_harvest.py"
print(f"   Script: {script_path}")

try:
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"   ✗ ERROR: Return code {result.returncode}")
        print(f"   STDERR: {result.stderr}")
        sys.exit(1)

    print("   ✓ Script completed")

except subprocess.TimeoutExpired:
    print("   ✗ TIMEOUT")
    sys.exit(1)

# Read results
print("\n4. Reading results...")
if not OUTPUT_FILE.exists():
    print("   ✗ No output file generated")
    sys.exit(1)

with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

print(f"   ✓ Retrieved: {len(results)} results")

# Show sample
if results:
    print(f"\n5. Sample result:")
    sample = results[0]
    print(f"   Title: {sample.get('title', 'N/A')[:80]}...")
    print(f"   Authors: {sample.get('authors', 'N/A')[:50]}...")
    print(f"   Year: {sample.get('year', 'N/A')}")

print("\n" + "=" * 80)
print("✓ MINIMAL INTEGRATION TEST SUCCESSFUL")
print("=" * 80)
