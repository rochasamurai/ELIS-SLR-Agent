# ELIS Search Configurations

This directory contains search configuration files for systematic literature reviews (SLRs) conducted using the ELIS SLR Agent.

## Overview

Each search configuration file defines all parameters needed to execute database searches for a specific SLR project, including:

- Search queries (Boolean strings)
- Target databases and their specific syntax
- Date ranges and filters
- Output specifications
- Validation rules

## Available Search Configurations

### 1. Tai & Awasthi 2025 (Benchmark 2)
**File:** `tai_awasthi_2025_search.yml`

- **Purpose:** Benchmark validation - replicate published SLR methodology
- **Topic:** Agile government in the public sector
- **Research Questions:**
  - RQ1: How has agility been conceptualized in the public sector?
  - RQ2: How has agile government been implemented, and what challenges exist?
  - RQ3: What impacts of agile government have been reported?
- **Query:** `("agile" AND "government") OR ("agile" AND "governance") OR ("agile" AND "public")`
- **Databases:** 8 ELIS databases (1/3 match with original paper)
- **Date Range:** 2002-2023
- **Status:** Active (Phase 1 execution)
- **Version:** 1.1.0

### 2. Electoral Integrity (ELIS Native Project)
**File:** `electoral_integrity_search.yml`

- **Purpose:** Primary ELIS research project
- **Topic:** Electoral integrity strategies and evaluation frameworks
- **Research Questions:**
  - PRQ: What strategies have improved electoral integrity/auditability since 1990?
  - MSQ: What empirical designs/frameworks assess electoral integrity strategies?
- **Query:** Multi-component (Electoral Systems AND Integrity AND (Strategies OR Evaluation))
- **Databases:** All 8 ELIS databases
- **Date Range:** 1990-2024
- **Status:** Active (Production)
- **Version:** 2.0.0

## File Structure

Each search configuration follows this standard structure:
```yaml
# Metadata
search_id: "unique_identifier"
project_name: "Descriptive name"
created_date: "YYYY-MM-DD"
status: "active|archived|draft"
version: "X.Y.Z"

# Query
query:
  boolean_string: "..."
  search_fields: [...]
  
# Date Range
date_range:
  start_year: YYYY
  end_year: YYYY

# Databases (ELIS Protocol order)
databases:
  - name: "Scopus"
  - name: "Web of Science"
  - name: "IEEE Xplore"
  - name: "Semantic Scholar"
  - name: "OpenAlex"
  - name: "CrossRef"
  - name: "CORE"
  - name: "Google Scholar"

# Filters
filters:
  language: [...]
  document_types: [...]
  peer_reviewed: true|false

# Output
output:
  directory: "..."
  primary_file: "..."

# Execution
execution:
  retry: {...}
  timeout: {...}
  logging: {...}

# Validation
validation:
  minimum_results: {...}
  expected_range: {...}
```

## How to Use

### For Benchmark Runs

Use the `--search-config` parameter:
```bash
python docs/benchmark-2/run_phase1_benchmark.py \
  --search-config config/searches/tai_awasthi_2025_search.yml
```

### For Production Searches

Reference the config in your workflow:
```yaml
- name: Run Electoral Integrity Search
  run: |
    python scripts/run_slr_search.py \
      --config config/searches/electoral_integrity_search.yml
```

### Programmatic Access
```python
import yaml

# Load search configuration
with open('config/searches/electoral_integrity_search.yml') as f:
    search_config = yaml.safe_load(f)

# Access parameters
query = search_config['query']['boolean_string']
databases = search_config['databases']
max_results = databases[0]['max_results']
```

## Database-Specific Query Syntax

Each database requires specific query formatting. The order below follows **ELIS Protocol 2025 v2.0 Section 3.2.1**:

| Database | Syntax | Example |
|----------|--------|---------|
| **1. Scopus** | `TITLE-ABS-KEY(query)` | `TITLE-ABS-KEY("e-voting" AND "security")` |
| **2. Web of Science** | `TS=(query)` | `TS=("e-voting" AND "security")` |
| **3. IEEE Xplore** | Generic | `querytext=e-voting AND security` |
| **4. Semantic Scholar** | Natural language | `query=e-voting security` |
| **5. OpenAlex** | `default.search:query` | `filter=default.search:e-voting security` |
| **6. CrossRef** | Generic | `query=e-voting AND security` |
| **7. CORE** | Generic | `q=e-voting AND security` |
| **8. Google Scholar** | Simple keywords | `e-voting security trust` |

**Important:** The harvest scripts automatically translate the Boolean query to the correct syntax for each database.

## Creating a New Search Configuration

### Step 1: Copy Template

Use the Electoral Integrity config as a template for comprehensive projects, or Tai & Awasthi for simpler queries:
```bash
cp config/searches/electoral_integrity_search.yml \
   config/searches/your_project_search.yml
```

### Step 2: Update Metadata
```yaml
search_id: "your_project_2026"
project_name: "Your Project Name"
created_date: "2026-01-30"
status: "draft"
version: "1.0.0"
```

### Step 3: Define Your Query

**Simple Query (like Tai & Awasthi):**
```yaml
query:
  boolean_string: |
    ("your term" AND "another term") OR 
    ("your term" AND "third term")
```

**Multi-Component Query (like Electoral Integrity):**
```yaml
query:
  boolean_string: |
    (
      ("concept A" OR "concept B")
      AND
      ("dimension 1" OR "dimension 2")
      AND
      (
        ("focus area 1" OR "focus area 2")
        OR
        ("methodology 1" OR "methodology 2")
      )
    )
```

### Step 4: Configure Databases

**Always follow ELIS Protocol order:** Scopus → WoS → IEEE → Semantic Scholar → OpenAlex → CrossRef → CORE → Google Scholar
```yaml
databases:
  # 1. Scopus
  - name: "Scopus"
    enabled: true
    max_results: 1000
    priority: "CRITICAL"
  
  # 2. Web of Science
  - name: "Web of Science"
    enabled: true
    max_results: 1000
    priority: "CRITICAL"
  
  # ... continue in ELIS Protocol order
```

### Step 5: Set Filters
```yaml
filters:
  language: ["English"]
  document_types: ["article", "conference paper"]
  peer_reviewed: true
```

### Step 6: Validate Configuration
```bash
python scripts/validate_search_config.py \
  config/searches/your_project_search.yml
```

## Best Practices

### Query Design

1. **Use Boolean operators:** AND, OR, NOT (parentheses for grouping)
2. **Include synonyms:** Cover different terminology for same concept
3. **Target 2-4 concept groups:** Not too broad, not too narrow
4. **Test pilot searches:** Verify query captures relevant literature
5. **Document rationale:** Explain how query addresses research questions

### Database Selection

1. **Follow ELIS Protocol order:** Always maintain standard sequence
2. **Enable all relevant databases:** Don't limit coverage unnecessarily
3. **Set appropriate max_results:**
   - Benchmarks: 500-1000 per database
   - Production: 1000-2000 per database
4. **Consider priority levels:**
   - CRITICAL: Must succeed for valid search
   - HIGH: Important but not critical
   - MEDIUM/LOW: Complementary coverage

### Date Ranges

1. **Align with research question:** Topic emergence to present
2. **Consider historical context:** When did field begin?
3. **Balance comprehensiveness vs. relevance:** Older ≠ better
4. **Note limitations:** Some databases don't support year filtering

### Filters

1. **Language:** English is standard, add others if needed
2. **Document types:**
   - Benchmarks: Articles only (match original)
   - Production: Articles + conferences (broader coverage)
3. **Peer review:** Usually true for quality assurance

## Query Design Approaches

### Approach 1: Simple Boolean (Tai & Awasthi)
**When to use:** Established field with clear terminology
```yaml
("term A" AND "context") OR ("term B" AND "context")
```

**Pros:** Simple, replicable, high sensitivity  
**Cons:** Lower precision, requires careful screening

### Approach 2: Multi-Component (Electoral Integrity)
**When to use:** Complex research questions, multiple dimensions
```yaml
(Component 1: Concept) AND (Component 2: Dimension) AND (Component 3: Focus)
```

**Pros:** Addresses multiple RQs, explicit structure  
**Cons:** More complex, requires careful testing

### Approach 3: Expanded Keywords
**When to use:** Comprehensive coverage needed
```yaml
query:
  boolean_string: "Core query"
  expanded_keywords:
    category_1: [list of terms]
    category_2: [list of terms]
```

**Pros:** Documents all captured terms  
**Cons:** Very long configuration files

## Validation and Quality Checks

Each configuration includes validation rules:
```yaml
validation:
  minimum_results:
    critical_databases: 200
    other_databases: 50
  
  expected_range:
    minimum: 2000
    maximum: 8000
  
  quality_checks:
    - "No empty abstracts in >80% of results"
    - "DOI present in >60% of results"
```

These ensure search execution meets quality standards.

## Output Files

Search results are saved to:

- **Combined results:** `json_jsonl/ELIS_Appendix_A_Search_rows.json`
- **Project results:** `results/{project_name}/`
- **Archives:** `results/{project_name}/archives/`
- **Reports:** Database contribution, statistics, etc.

## Troubleshooting

### Common Issues

**Issue:** Database returns 0 results
- **Check:** API credentials in environment variables
- **Check:** Query syntax is correct for that database
- **Check:** Database is accessible (not rate limited)
- **Check:** max_results setting isn't too restrictive

**Issue:** Fewer results than expected
- **Check:** max_results setting in config
- **Check:** Date range filters
- **Check:** Query is not too restrictive
- **Verify:** Database-specific syntax is correct

**Issue:** Too many irrelevant results
- **Check:** Query is not too broad
- **Check:** Filters are properly applied
- **Refine:** Add exclusion terms or narrow query
- **Consider:** Multi-component query structure

**Issue:** Database order confusion
- **Solution:** Always follow ELIS Protocol 2025 v2.0 order
- **Reference:** Scopus → WoS → IEEE → Semantic Scholar → OpenAlex → CrossRef → CORE → Google Scholar

### Getting Help

1. Check database-specific documentation
2. Review harvest script logs
3. Validate configuration syntax
4. Compare with working configurations (tai_awasthi or electoral_integrity)

## Version Control

Search configurations use semantic versioning:

- **Major (X.0.0):** Significant query changes, new research focus
- **Minor (x.Y.0):** Database changes, filter updates, documentation
- **Patch (x.y.Z):** Typo fixes, clarifications, no functional changes

**Examples:**
- `1.0.0` → `2.0.0`: Changed from e-voting only to all electoral systems
- `1.0.0` → `1.1.0`: Added query coverage documentation
- `1.1.0` → `1.1.1`: Fixed typo in notes

## Changelog

### 2026-01-30
- ✅ Created Tai & Awasthi 2025 benchmark configuration (v1.1.0)
- ✅ Created Electoral Integrity native project configuration (v2.0.0)
- ✅ Updated README with ELIS Protocol database order
- ✅ Added comprehensive query design guidance
- ✅ Documented research question alignment approaches

## Future Enhancements

Planned improvements:

1. **Configuration validator script** - Automated syntax/schema checking
2. **Query builder tool** - Interactive query construction
3. **Pilot search mode** - Test queries with limited results
4. **Configuration versioning** - Track changes over time
5. **Templates library** - Pre-configured templates for common SLR types
6. **Automated syntax translation** - Test query across all databases

## Related Documentation

- **ELIS Protocol:** `ELIS_2025_SLR_Protocol_Electoral_Integrity_Strategies_2026-01-28_v2.0_draft-08.1.pdf`
- **Harvest Scripts:** `../../scripts/README.md` - Database-specific implementation
- **Benchmark Documentation:** `../../docs/benchmark-2/README.md` - Validation methodology
- **ELIS Main README:** `../../README.md` - Overall project documentation
- **Query Syntax Audit:** `../../docs/QUERY_SYNTAX_AUDIT_AND_FIXES.md` - Database syntax reference

## Contributing

When creating or updating search configurations:

1. ✅ Follow ELIS Protocol database order
2. ✅ Use semantic versioning
3. ✅ Document query rationale
4. ✅ Include expanded keywords for complex queries
5. ✅ Add research question alignment notes
6. ✅ Test with pilot search before production
7. ✅ Update this README with new configurations

---

**Last Updated:** 2026-01-30  
**Maintainer:** ELIS Research Team  
**Status:** Active
