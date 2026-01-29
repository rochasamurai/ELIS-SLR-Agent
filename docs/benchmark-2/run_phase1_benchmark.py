"""
Run Full Phase 1 Benchmark - All 8 Databases
Executes benchmark across all available ELIS databases
"""
import yaml
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import re

# Paths
REPO_ROOT = Path.cwd().parents[1]
CONFIG_DIR = REPO_ROOT / "config"
SCRIPTS_DIR = REPO_ROOT / "scripts"
OUTPUT_FILE = REPO_ROOT / "json_jsonl" / "ELIS_Appendix_A_Search_rows.json"
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Database to script mapping (8 databases - ELIS Protocol latest)
DATABASE_SCRIPTS = {
    "Scopus": "scopus_harvest.py",
    "Web of Science": "wos_harvest.py",
    "IEEE Xplore": "ieee_harvest.py",
    "Semantic Scholar": "semanticscholar_harvest.py",
    "OpenAlex": "openalex_harvest.py",
    "CrossRef": "crossref_harvest.py",
    "CORE": "core_harvest.py",
    "Google Scholar": "google_scholar_harvest.py"
}

# Simple fuzzy matching functions
def normalize_text(text):
    """Normalize text for comparison"""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
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
    gold_doi = str(gold_study.get('doi', '') or '').strip().lower()
    retrieved_doi = str(retrieved_study.get('doi', '') or '').strip().lower()
    if gold_doi and retrieved_doi and gold_doi == retrieved_doi:
        return True
    
    # Title similarity
    title_sim = calculate_similarity(
        gold_study.get('title', '') or '',
        retrieved_study.get('title', '') or ''
    )
    
    if title_sim >= threshold:
        return True
    
    return False

def deduplicate(studies):
    """Remove duplicate studies by normalized title"""
    seen = set()
    unique = []
    for study in studies:
        norm_title = normalize_text(study.get('title', ''))
        if norm_title and norm_title not in seen:
            seen.add(norm_title)
            unique.append(study)
    return unique

def search_database(db_name, script_name, query, start_year, end_year):
    """Search a single database"""
    print(f"\n{'='*80}")
    print(f"SEARCHING: {db_name}")
    print(f"{'='*80}")
    
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"  ✗ Script not found: {script_name}")
        return []
    
    # Map database name to ELIS source identifier
    source_mapping = {
        "Scopus": "scopus",
        "Web of Science": "web_of_science",
        "IEEE Xplore": "ieee_xplore",
        "Semantic Scholar": "semantic_scholar",
        "OpenAlex": "openalex",
        "CrossRef": "crossref",
        "CORE": "core",
        "Google Scholar": "google_scholar"
    }
    
    source_id = source_mapping.get(db_name, db_name.lower().replace(" ", "_"))
    
    # Create ELIS config
    elis_config = {
        'global': {
            'year_from': start_year,
            'year_to': end_year,
            'languages': ['en'],
            'max_results_per_source': 500,
            'job_result_cap': 0
        },
        'topics': [{
            'id': f'benchmark_{source_id}',
            'enabled': True,
            'description': f'Benchmark query for {db_name}',
            'queries': [query],
            'include_preprints': False,
            'sources': [source_id]
        }]
    }
    
    # Write config
    with open(CONFIG_DIR / "elis_search_queries.yml", 'w', encoding='utf-8') as f:
        yaml.dump(elis_config, f, default_flow_style=False)
    
    # Clear previous results
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()
    
    # Run harvest script
    print(f"  Running: {script_name}")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"  ✗ ERROR: Return code {result.returncode}")
            if result.stderr:
                print(f"  STDERR: {result.stderr[:500]}")
            return []
        
        # Read results
        if not OUTPUT_FILE.exists():
            print(f"  ⚠ No output file generated")
            return []
        
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Add source database to each result
        for r in results:
            r['source_database'] = db_name
        
        print(f"  ✓ Retrieved: {len(results)} results")
        return results
        
    except subprocess.TimeoutExpired:
        print(f"  ✗ TIMEOUT: Exceeded 5 minutes")
        return []
    except Exception as e:
        print(f"  ✗ ERROR: {type(e).__name__}: {e}")
        return []

# Main execution
print("="*80)
print("BENCHMARK 2 - PHASE 1 FULL EXECUTION")
print("="*80)
print(f"\nPaper: Tai & Awasthi (2025) - Agile Government")

# Load config and gold standard
with open('configs/benchmark_2_config.yaml', 'r', encoding='utf-8') as f:
    bench_config = yaml.safe_load(f)

with open('data/tai_awasthi_2025_references_FINAL.json', 'r', encoding='utf-8') as f:
    gold_standard = json.load(f)

print(f"Gold standard: {len(gold_standard)} studies")
print(f"Databases: 8 (Phase 1 - All ELIS databases)")

# Get search parameters
query = bench_config['search_strategy']['query_string'].strip()
start_year = int(bench_config['search_strategy']['date_range']['start'].split('-')[0])
end_year = int(bench_config['search_strategy']['date_range']['end'].split('-')[0])

print(f"\nQuery: {query[:80]}...")
print(f"Date range: {start_year}-{end_year}")

# Execute searches
start_time = datetime.now()
all_results = []
db_contribution = {}

databases = list(DATABASE_SCRIPTS.keys())

for db_name in databases:
    script_name = DATABASE_SCRIPTS[db_name]
    results = search_database(db_name, script_name, query, start_year, end_year)
    all_results.extend(results)
    db_contribution[db_name] = len(results)

# Deduplication
print(f"\n{'='*80}")
print("DEDUPLICATION")
print("="*80)
print(f"Total retrieved (with duplicates): {len(all_results)}")
unique_results = deduplicate(all_results)
print(f"After deduplication: {len(unique_results)}")

# Matching
print(f"\n{'='*80}")
print("MATCHING AGAINST GOLD STANDARD")
print("="*80)

matched = []
missed = []

for gold in gold_standard:
    found = False
    for retr in unique_results:
        if match_study(gold, retr):
            matched.append({
                'gold_id': gold['reference_id'],
                'title': gold['title'],
                'authors': gold['authors'],
                'year': gold['year'],
                'matched_title': retr['title'],
                'source_database': retr.get('source_database', 'Unknown')
            })
            found = True
            break
    
    if not found:
        missed.append({
            'gold_id': gold['reference_id'],
            'title': gold['title'],
            'authors': gold['authors'],
            'year': gold['year']
        })

# Calculate metrics
end_time = datetime.now()
execution_time = (end_time - start_time).total_seconds()

retrieval_rate = len(matched) / len(gold_standard)
precision = len(matched) / len(unique_results) if unique_results else 0
recall = retrieval_rate
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"\nMatched: {len(matched)}/{len(gold_standard)} ({retrieval_rate:.1%})")
print(f"Precision: {precision:.1%}")
print(f"Recall: {recall:.1%}")
print(f"F1 Score: {f1:.3f}")
print(f"Execution time: {execution_time/60:.1f} minutes")

# Database contribution analysis
print(f"\n{'='*80}")
print("DATABASE CONTRIBUTION")
print("="*80)
for db, count in sorted(db_contribution.items(), key=lambda x: -x[1]):
    print(f"  {db}: {count} results")

# Save results
result_data = {
    'benchmark_id': 'TAI_AWASTHI_2025',
    'phase': 'PHASE_1',
    'execution_date': start_time.isoformat(),
    'databases_used': databases,
    'total_gold_standard': len(gold_standard),
    'total_retrieved': len(unique_results),
    'total_matched': len(matched),
    'retrieval_rate': retrieval_rate,
    'precision': precision,
    'recall': recall,
    'f1_score': f1,
    'execution_time_seconds': execution_time,
    'database_contribution': db_contribution,
    'matched_studies': matched,
    'missed_studies': missed
}

# Save JSON
results_file = RESULTS_DIR / "phase1_full_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(result_data, f, indent=2)

print(f"\n{'='*80}")
print("PHASE 1 COMPLETE")
print("="*80)
print(f"Results saved: {results_file}")

# Status assessment
if retrieval_rate >= 0.75:
    status = "✓ EXCELLENT"
elif retrieval_rate >= 0.65:
    status = "✓ TARGET ACHIEVED"
elif retrieval_rate >= 0.50:
    status = "✓ MINIMUM ACHIEVED"
else:
    status = "✗ BELOW MINIMUM"

print(f"\nStatus: {status}")
print(f"Retrieval Rate: {retrieval_rate:.1%}")
