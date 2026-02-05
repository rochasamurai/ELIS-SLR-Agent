"""Full benchmark integration - with matching"""

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
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


# Simple fuzzy matching
def normalize_text(text):
    """Normalize text for comparison"""
    if not text:
        return ""
    import re

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_similarity(str1, str2):
    """Token-based similarity"""
    norm1 = normalize_text(str1)
    norm2 = normalize_text(str2)

    if norm1 == norm2:
        return 1.0

    tokens1 = set(norm1.split())
    tokens2 = set(norm2.split())

    if not tokens1 or not tokens2:
        return 0.0

    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)

    return intersection / union if union > 0 else 0.0


def match_study(gold_study, retrieved_study, threshold=0.85):
    """Check if studies match"""
    # DOI match
    gold_doi = str(gold_study.get("doi", "") or "").strip().lower()
    retrieved_doi = str(retrieved_study.get("doi", "") or "").strip().lower()
    if gold_doi and retrieved_doi and gold_doi == retrieved_doi:
        return True

    # Title similarity
    title_sim = calculate_similarity(
        gold_study.get("title", "") or "", retrieved_study.get("title", "") or ""
    )

    if title_sim >= threshold:
        return True

    return False


# Load benchmark config
print("=" * 80)
print("BENCHMARK 2 - FULL INTEGRATION TEST")
print("=" * 80)

with open("configs/benchmark_2_config.yaml", "r", encoding="utf-8") as f:
    bench_config = yaml.safe_load(f)

with open("data/tai_awasthi_2025_references_FINAL.json", "r", encoding="utf-8") as f:
    gold_standard = json.load(f)

print(f"\nBenchmark: {bench_config['benchmark']['name']}")
print(f"Gold standard: {len(gold_standard)} studies")
print(f"Database: OpenAlex (test)")

# Create ELIS config
query = bench_config["search_strategy"]["query_string"].strip()
start_year = int(bench_config["search_strategy"]["date_range"]["start"].split("-")[0])
end_year = int(bench_config["search_strategy"]["date_range"]["end"].split("-")[0])

elis_config = {
    "global": {
        "year_from": start_year,
        "year_to": end_year,
        "languages": ["en"],
        "max_results_per_source": 200,  # Increased for better coverage
        "job_result_cap": 0,
    },
    "topics": [
        {
            "id": "benchmark_tai_awasthi",
            "enabled": True,
            "description": "Benchmark query for Tai & Awasthi (2025)",
            "queries": [query],
            "include_preprints": False,
            "sources": ["openalex"],
        }
    ],
}

# Write config
with open(CONFIG_DIR / "elis_search_queries.yml", "w", encoding="utf-8") as f:
    yaml.dump(elis_config, f, default_flow_style=False)

# Clear previous results
if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()

# Run harvest
print("\n" + "-" * 80)
print("SEARCHING OPENALEX...")
print("-" * 80)

start_time = datetime.now()

result = subprocess.run(
    [sys.executable, str(SCRIPTS_DIR / "openalex_harvest.py")],
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    timeout=120,
)

if result.returncode != 0:
    print(f"ERROR: {result.stderr}")
    sys.exit(1)

# Read results
with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    retrieved = json.load(f)

print(f"Retrieved: {len(retrieved)} results")

# Match against gold standard
print("\n" + "-" * 80)
print("MATCHING AGAINST GOLD STANDARD...")
print("-" * 80)

matched = []
missed = []

for gold in gold_standard:
    found = False
    for retr in retrieved:
        if match_study(gold, retr):
            matched.append(
                {
                    "gold_id": gold["reference_id"],
                    "title": gold["title"],
                    "year": gold["year"],
                    "matched_title": retr["title"],
                }
            )
            found = True
            break

    if not found:
        missed.append(
            {
                "gold_id": gold["reference_id"],
                "title": gold["title"],
                "year": gold["year"],
            }
        )

# Calculate metrics
end_time = datetime.now()
execution_time = (end_time - start_time).total_seconds()

retrieval_rate = len(matched) / len(gold_standard)
precision = len(matched) / len(retrieved) if retrieved else 0
recall = retrieval_rate
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"\nMatched: {len(matched)}/{len(gold_standard)} ({retrieval_rate:.1%})")
print(f"Precision: {precision:.1%}")
print(f"Recall: {recall:.1%}")
print(f"F1 Score: {f1:.3f}")
print(f"Time: {execution_time:.1f}s")

# Save results
result_data = {
    "benchmark_id": "TAI_AWASTHI_2025",
    "phase": "TEST_OPENALEX",
    "execution_date": start_time.isoformat(),
    "database": "OpenAlex",
    "total_gold_standard": len(gold_standard),
    "total_retrieved": len(retrieved),
    "total_matched": len(matched),
    "retrieval_rate": retrieval_rate,
    "precision": precision,
    "recall": recall,
    "f1_score": f1,
    "execution_time_seconds": execution_time,
    "matched_studies": matched,
    "missed_studies": missed,
}

# Save JSON
with open(RESULTS_DIR / "test_openalex_results.json", "w", encoding="utf-8") as f:
    json.dump(result_data, f, indent=2)

print("\n" + "=" * 80)
print(f"✓ TEST COMPLETE - Results saved to {RESULTS_DIR}/test_openalex_results.json")
print("=" * 80)
print(f"\nStatus: {'✓ SUCCESS' if retrieval_rate >= 0.50 else '✗ BELOW MINIMUM (50%)'}")
