# ELIS Benchmark 2: Tai & Awasthi (2025)

**Benchmark ID:** `TAI_AWASTHI_2025`  
**Status:** PENDING API ACCESS  
**Created:** 2026-01-29  
**Last Updated:** 2026-01-29

---

## Overview

This benchmark validates the ELIS SLR Agent's retrieval capabilities against a systematic literature review on agile government in the public sector published in *Government Information Quarterly*.

### Paper Details

**Citation:**
> Tai, K.T., & Awasthi, P. (2025). An exploration of agile government in the public sector: A systematic literature review at macro, meso, and micro levels of analysis. *Government Information Quarterly, 42*, 102082. https://doi.org/10.1016/j.giq.2025.102082

**Key Characteristics:**
- **Total Studies:** 55 articles
- **Time Period:** 2002-2023 (search until May 2023)
- **Methodology:** PRISMA 2020
- **Databases Used:** Web of Science, EBSCOhost, ProQuest Social Science Premium
- **Focus:** Agile practices across micro (project), meso (organizational), and macro (governance) levels

---

## Folder Structure

```
benchmark-2/
├── README.md                          # This file
├── docs/
│   ├── BENCHMARK_TAI_AWASTHI_2025.md # Complete benchmark documentation
│   └── An_exploration_of_agile_government_in_the_public_sector.pdf
├── data/
│   └── tai_awasthi_2025_references_FINAL.csv  # 55 gold standard references
├── results/
│   └── (benchmark execution results will be stored here)
└── configs/
    └── (benchmark configuration files will be stored here)
```

---

## Current Status

### Blocking Items

⏳ **PENDING:**
- EBSCOhost API access (request submitted to Imperial College IT support)
- ProQuest Social Science Premium API access (request submitted to Imperial College IT support)

### Completed Items

✅ **DONE:**
- Full benchmark documentation created
- Reference list extraction completed (all 55 studies)
- Database overlap analysis performed
- Search strategy documented
- Validation methodology designed

---

## Database Coverage Analysis

### Paper's Databases vs. ELIS Access

| Database | Paper Uses | ELIS Has Access | Status |
|----------|-----------|-----------------|---------|
| **Web of Science** | ✅ | ✅ | **CONFIRMED MATCH** |
| **EBSCOhost** | ✅ | ⏳ | PENDING API access |
| **ProQuest Social Science Premium** | ✅ | ⏳ | PENDING API access |

**Current Database Overlap:** 1/3 (33%)

### ELIS Supplementary Databases

While ELIS only has 1 direct database match, it has access to complementary databases that may provide overlapping coverage:

- ✅ Scopus (high overlap with Web of Science)
- ✅ OpenAlex (comprehensive aggregator, may contain EBSCOhost/ProQuest content)
- ✅ CrossRef (DOI-based verification)
- ✅ Google Scholar (broadest coverage)
- ✅ Semantic Scholar (CS/interdisciplinary)
- ✅ IEEE Xplore (technical literature)
- ✅ CORE (open access aggregator)

---

## Expected Performance

### Baseline Scenario (Web of Science Only)

| Metric | Conservative | Realistic | Optimistic |
|--------|-------------|-----------|------------|
| **Direct Retrieval** | 30% | 45% | 60% |
| **Via Supplementary DBs** | +15% | +20% | +25% |
| **Total Expected** | **45%** | **65%** | **85%** |

### Full Access Scenario (All 3 Databases)

| Metric | Conservative | Realistic | Optimistic |
|--------|-------------|-----------|------------|
| **Direct Database Match** | 60% | 75% | 85% |
| **Via Supplementary DBs** | +10% | +15% | +10% |
| **Total Expected** | **70%** | **90%** | **95%** |

**Success Criteria:**
- ✅ Minimum Acceptable: ≥50% retrieval rate
- ✅ Target Performance: ≥65% retrieval rate
- ⭐ Excellent Performance: ≥75% retrieval rate

---

## Comparison with Benchmark 1

### Key Differences

| Dimension | Benchmark 1 (Darmawan 2021) | Benchmark 2 (Tai & Awasthi 2025) |
|-----------|----------------------------|----------------------------------|
| **Topic** | E-voting adoption | Agile government practices |
| **Journal** | Asian Journal of Comparative Politics | Government Information Quarterly |
| **Study Count** | 78 studies | 55 studies |
| **Time Period** | 2005-2020 | 2002-2023 |
| **Database Overlap** | 0/4 direct matches | 1/3 direct matches (WoS) |
| **Retrieval Rate** | 66.67% (52/78) | TBD |
| **Cost** | $0.50 | TBD |
| **Runtime** | 22 minutes | TBD |

### Expected Insights

**Hypotheses:**
1. **H1:** Retrieval rate will be higher due to better database overlap (Web of Science confirmed)
2. **H2:** Precision will be higher due to more recent publication (2025 vs 2021)
3. **H3:** Runtime will be similar (~20-30 minutes)
4. **H4:** Cost will be comparable ($0.40-$0.60)

---

## Documentation

### Main Documentation

📄 **`docs/BENCHMARK_TAI_AWASTHI_2025.md`** - Complete benchmark documentation including:
- Full paper metadata and abstract
- Verified search strategy from the paper
- ELIS database access assessment
- Expected performance predictions
- Detailed validation methodology
- Phase-by-phase execution plan
- Comparison framework with Benchmark 1
- Risk assessment
- Timeline and action plan

### Reference Data

📊 **`data/tai_awasthi_2025_references_FINAL.csv`** - Gold standard reference list:
- All 55 studies from the systematic review
- Structured format: reference_id, authors, year, title, journal, volume, issue, pages, DOI
- Ready for automated matching

### Source Paper

📑 **`docs/An_exploration_of_agile_government_in_the_public_sector.pdf`** - Original paper

---

## Execution Workflow

### Prerequisites

**Required:**
- [x] ELIS SLR Agent installed and configured
- [x] Gold standard reference list prepared
- [x] Search strategy documented
- [ ] EBSCOhost API access obtained
- [ ] ProQuest API access obtained

**Optional:**
- [ ] Author contact for search strategy verification
- [ ] Raw search results from authors (for validation)

### Phase 1: Preparation (CURRENT)

- [x] Extract reference list
- [x] Create benchmark documentation
- [x] Design validation methodology
- [ ] Monitor API access requests
- [ ] Configure ELIS queries (pending API access)

### Phase 2: Execution (BLOCKED)

- [ ] Run ELIS searches across all databases
- [ ] Perform deduplication
- [ ] Execute matching algorithm
- [ ] Calculate metrics

### Phase 3: Analysis (BLOCKED)

- [ ] Manual verification of high-confidence matches
- [ ] Investigate missed studies
- [ ] Analyze false positives
- [ ] Compare with Benchmark 1

### Phase 4: Documentation (BLOCKED)

- [ ] Generate results report
- [ ] Create visualization
- [ ] Document lessons learned
- [ ] Update ELIS protocol if needed

---

## Timeline

```
Week 1: API Access & Configuration
├── Day 1-3: Monitor Imperial College API requests
├── Day 4: Configure ELIS queries
└── Day 5: Test API connections

Week 2: Execution
├── Day 1: Execute searches
├── Day 2-3: Matching and deduplication
├── Day 4: Calculate preliminary metrics
└── Day 5: Initial analysis

Week 3: Validation & Documentation
├── Day 1-2: Manual verification
├── Day 3: Comparative analysis with Benchmark 1
├── Day 4: Results documentation
└── Day 5: Final report and recommendations
```

---

## Contact & Support

**Principal Investigator:**
- Name: Carlos Rocha
- Role: Visiting Researcher
- Institution: Imperial College London

**Support Requests:**
- EBSCOhost API: Imperial College IT Support
- ProQuest API: Imperial College IT Support

---

## Related Resources

### Internal Documents
- **Benchmark 1:** `../benchmark-1/` (Darmawan 2021 - E-voting adoption)
- **ELIS Protocol:** ELIS_2025_SLR_Protocol_Electoral_Integrity_Strategies_v2.0_draft-08.1.pdf
- **ELIS Repository:** https://github.com/rochasamurai/ELIS-SLR-Agent

### External Resources
- **PRISMA 2020:** http://www.prisma-statement.org/
- **Web of Science API:** https://developer.clarivate.com/
- **Original Paper DOI:** https://doi.org/10.1016/j.giq.2025.102082

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-29 | Initial benchmark setup and documentation | ELIS Team |

---

**Last Updated:** 2026-01-29  
**Status:** Documentation complete, awaiting API access
