# ELIS Benchmark 2 - Integration Guide

## Overview

This guide explains how to integrate the Benchmark 2 testing script with the actual ELIS SLR Agent to run real database searches instead of simulations.

---

## Current Status

✅ **COMPLETED:**
- Configuration file created (`configs/benchmark_2_config.yaml`)
- Test script created (`benchmark_2_runner.py`)
- Matching algorithm implemented and tested
- Simulation successfully validates the matching logic (40% retrieval in simulation)

⏳ **PENDING:**
- Integration with actual ELIS SLR Agent API
- EBSCOhost API access
- ProQuest API access

---

## Integration Steps

### Step 1: Locate ELIS SLR Agent

The benchmark script needs to call the ELIS SLR Agent's search functionality. You need to:

1. Find the ELIS SLR Agent main module (likely in `src/` or `elis_agent/`)
2. Identify the search API/function that executes database queries
3. Understand the expected input/output format

**Example ELIS Agent structure (adjust based on actual codebase):**
```python
from elis_agent import ELISAgent

# Initialize agent
agent = ELISAgent(config_file="config.yaml")

# Execute search
results = agent.search(
    databases=["Scopus", "Web of Science"],
    query="(agile AND government)",
    date_start="2002-01-01",
    date_end="2023-05-31",
    filters={
        "language": "English",
        "peer_reviewed": True
    }
)
```

### Step 2: Replace Simulation Function

In `benchmark_2_runner.py`, find the `simulate_database_search()` method (around line 159):

**CURRENT (Simulation):**
```python
def simulate_database_search(self, database: str, query: str) -> List[Dict]:
    """
    SIMULATION: Returns mock results for testing
    """
    print(f"  [SIMULATION] Searching {database}...")
    # ... simulation code ...
```

**REPLACE WITH (Production):**
```python
def execute_database_search(self, database: str, query: str) -> List[Dict]:
    """
    PRODUCTION: Calls actual ELIS SLR Agent
    """
    print(f"  Searching {database}...")
    
    # Import ELIS agent
    from elis_agent import ELISAgent
    
    # Initialize if not already done
    if not hasattr(self, 'agent'):
        self.agent = ELISAgent(config_file="../config.yaml")
    
    # Extract date range from config
    date_start = self.config['search_strategy']['date_range']['start']
    date_end = self.config['search_strategy']['date_range']['end']
    
    # Execute search
    results = self.agent.search(
        database=database,
        query=query,
        date_start=date_start,
        date_end=date_end,
        filters={
            "language": "English",
            "peer_reviewed": True
        }
    )
    
    # Convert ELIS results to benchmark format
    formatted_results = []
    for result in results:
        formatted_results.append({
            'title': result.get('title', ''),
            'authors': result.get('authors', ''),
            'year': result.get('year', ''),
            'journal': result.get('journal', ''),
            'doi': result.get('doi', ''),
            'source_database': database
        })
    
    print(f"  Found: {len(formatted_results)} results")
    return formatted_results
```

### Step 3: Update Method Call

In the `execute_phase1()` method, replace:

```python
results = self.simulate_database_search(db, query)
```

With:

```python
results = self.execute_database_search(db, query)
```

### Step 4: Test with Single Database First

Before running all databases, test with just one:

```python
# In execute_phase1(), temporarily modify:
phase1_dbs = ["Web of Science"]  # Test with just WoS first

# Run test
python3 benchmark_2_runner.py
```

### Step 5: Verify Results Format

After the first test run, verify the output format matches expectations:

```python
# Check a sample result
print(json.dumps(unique_retrieved[0], indent=2))

# Expected format:
{
  "title": "Study title here",
  "authors": "Author1, Author2",
  "year": "2020",
  "journal": "Journal Name",
  "doi": "10.1234/example",
  "source_database": "Web of Science"
}
```

### Step 6: Full Execution

Once verified, run with all Phase 1 databases:

```python
phase1_dbs = [
    "Scopus", 
    "Web of Science", 
    "OpenAlex", 
    "CrossRef", 
    "Google Scholar", 
    "Semantic Scholar", 
    "CORE"
]
```

---

## Expected Results

### Phase 1 (Current Databases Only)

**Databases:** Scopus, WoS, OpenAlex, CrossRef, Google Scholar, Semantic Scholar, CORE

**Expected Metrics:**
- Retrieval Rate: 45-85%
- Precision: 70-90%
- Runtime: 15-30 minutes
- Cost: $0.40-$0.80

**Database Overlap with Paper:**
- Direct match: Web of Science (1/3)
- Supplementary coverage via Scopus, OpenAlex, Google Scholar

### Phase 2 (After API Access)

**Additional Databases:** EBSCOhost, ProQuest Social Science Premium

**Expected Metrics:**
- Retrieval Rate: 70-95%
- Precision: 75-90%
- Runtime: 20-35 minutes
- Cost: $0.60-$1.20

**Database Overlap with Paper:**
- Direct match: All 3 databases (Web of Science, EBSCOhost, ProQuest)

---

## Configuration Reference

### Query String

From `configs/benchmark_2_config.yaml`:

```yaml
query_string: |
  ("agile" AND "government") OR 
  ("agile" AND "governance") OR 
  ("agile" AND "public")
```

### Search Fields

- Title
- Abstract
- Keywords (author-identified)

### Date Range

- Start: 2002-01-01
- End: 2023-05-31

### Filters

- Language: English
- Peer-reviewed: Yes
- Document type: Article

---

## Matching Algorithm

The benchmark uses a **fuzzy keyword hybrid** matching approach:

### Priority 1: Exact DOI Match
```python
if gold_doi == retrieved_doi:
    return True  # 100% confidence
```

### Priority 2: Title + Author Match
```python
if title_similarity >= 0.85 and author_overlap:
    return True  # 95% confidence
```

### Priority 3: Title + Year Match
```python
if title_similarity >= 0.85 and same_year:
    return True  # 85% confidence
```

### Thresholds
- Title similarity threshold: 0.85 (85%)
- Manual review range: 0.70-0.85

---

## Output Files

After execution, the following files will be generated in `results/`:

1. **benchmark_2_phase1_results.json** - Complete results in JSON format
2. **benchmark_2_phase1_report.md** - Human-readable markdown report
3. **benchmark_2_matched_studies.json** - List of successfully matched studies
4. **benchmark_2_missed_studies.json** - List of studies not found

---

## Troubleshooting

### Issue: Low Retrieval Rate (<40%)

**Possible causes:**
- Query syntax not compatible with database
- Date filters too restrictive
- Missing search fields (e.g., keywords not supported)

**Solution:**
- Review database API documentation
- Test query manually in database interface
- Adjust search fields in configuration

### Issue: High False Positive Rate

**Possible causes:**
- Query too broad (e.g., "agile" AND "public" matches many irrelevant studies)
- Missing filters (e.g., not filtering by peer-review status)

**Solution:**
- Add additional filters
- Review matched studies manually
- Adjust matching threshold

### Issue: API Rate Limits

**Possible causes:**
- Too many rapid requests
- Exceeding database quotas

**Solution:**
- Implement rate limiting (sleep between requests)
- Batch requests
- Use caching for repeated queries

---

## Next Steps After Integration

1. **Run Phase 1** with available databases
2. **Analyze results** - Compare with expected performance
3. **Document findings** - Create detailed report
4. **Wait for API access** - Monitor EBSCOhost and ProQuest requests
5. **Run Phase 2** - Re-execute with full database coverage
6. **Compare phases** - Analyze improvement from additional databases

---

## Contact

For questions about integration:
- Review ELIS SLR Agent documentation
- Check `src/` directory for agent implementation
- Consult with development team

For questions about benchmark configuration:
- See `configs/benchmark_2_config.yaml`
- Review this integration guide
- Check `docs/BENCHMARK_TAI_AWASTHI_2025.md`

---

**Last Updated:** 2026-01-29  
**Status:** Ready for integration with ELIS Agent
