"""
Re-match Phase 1 results with different thresholds
Analyzes existing retrieved results without re-running searches
"""
import json
import re
from pathlib import Path

# Paths
RESULTS_FILE = Path("results/phase1_full_results.json")
GOLD_STANDARD_FILE = Path("data/tai_awasthi_2025_references_FINAL.json")

# Load results
print("Loading Phase 1 results...")
with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
    phase1_results = json.load(f)

with open(GOLD_STANDARD_FILE, 'r', encoding='utf-8') as f:
    gold_standard = json.load(f)

print(f"Retrieved studies: {phase1_results['total_retrieved']}")
print(f"Gold standard: {len(gold_standard)}")
print(f"Original matches (85% threshold): {phase1_results['total_matched']}")

# We need to reconstruct the retrieved studies from database searches
# Since we don't have them in the results file, let's analyze what we can

print("\n" + "="*80)
print("ANALYSIS OF MATCHED STUDIES")
print("="*80)

matched = phase1_results['matched_studies']
print(f"\nTotal matched: {len(matched)}")
print("\nDatabase breakdown:")
db_counts = {}
for m in matched:
    db = m['source_database']
    db_counts[db] = db_counts.get(db, 0) + 1

for db, count in sorted(db_counts.items(), key=lambda x: -x[1]):
    print(f"  {db}: {count}")

print("\n" + "="*80)
print("MATCHED STUDIES LIST")
print("="*80)
for i, m in enumerate(matched, 1):
    print(f"\n{i}. {m['title'][:80]}...")
    print(f"   Authors: {m['authors']}")
    print(f"   Year: {m['year']}")
    print(f"   Source: {m['source_database']}")

print("\n" + "="*80)
print("ANALYSIS OF MISSED STUDIES")
print("="*80)

missed = phase1_results['missed_studies']
print(f"\nTotal missed: {len(missed)}")

# Sample of missed studies
print("\nSample of missed studies (first 10):")
for i, m in enumerate(missed[:10], 1):
    print(f"\n{i}. {m['title'][:80]}...")
    print(f"   Authors: {m['authors']}")
    print(f"   Year: {m['year']}")

print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)

print("""
Based on the analysis:

1. **Google Scholar Critical**: 0 results from Google Scholar
   - This was the best performer in benchmark-1 (37% alone)
   - Need to debug why it failed
   - Check Apify timeout/configuration

2. **Matching Algorithm**: Current 85% threshold catches only exact matches
   - Lower to 70% for better recall
   - Implement author matching as fallback
   - Add year +/- 1 tolerance

3. **Database Issues**:
   - IEEE Xplore: 0 results (check API key)
   - Semantic Scholar: 0 results (rate limits?)
   - These 2 databases need debugging

4. **Good Performers**:
   - OpenAlex: 500 results, 6 matches
   - Web of Science: 500 results, 4 matches
   - Scopus: 500 results, 0 matches (check matching!)
   - CrossRef: 490 results
   - CORE: 482 results, 1 match

NEXT STEPS:
1. Fix Google Scholar integration (priority #1)
2. Lower matching threshold to 70%
3. Debug IEEE & Semantic Scholar
4. Re-run Phase 1
5. Target: 65%+ retrieval rate
""")

print("\n" + "="*80)
print("DETAILED METRICS")
print("="*80)
print(f"Retrieval Rate: {phase1_results['retrieval_rate']:.1%}")
print(f"Precision: {phase1_results['precision']:.1%}")
print(f"Recall: {phase1_results['recall']:.1%}")
print(f"F1 Score: {phase1_results['f1_score']:.3f}")
print(f"Execution Time: {phase1_results['execution_time_seconds']/60:.1f} minutes")

print("\n" + "="*80)
print("STATUS: Need to address Google Scholar failure before re-running")
print("="*80)
