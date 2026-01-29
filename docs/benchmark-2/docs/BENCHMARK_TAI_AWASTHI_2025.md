# ELIS Benchmark: Tai & Awasthi (2025)

**Benchmark ID:** `TAI_AWASTHI_2025`  
**Status:** PENDING API ACCESS  
**Created:** 2026-01-29  
**Last Updated:** 2026-01-29

---

## Overview

This benchmark evaluates ELIS SLR Agent's performance against a systematic literature review on agile government in the public sector published in Government Information Quarterly (GIQ) in 2025.

### Key Characteristics
- **Paper Title:** An exploration of agile government in the public sector: A systematic literature review at macro, meso, and micro levels of analysis
- **Authors:** Kuang-Ting Tai, Pallavi Awasthi
- **Journal:** Government Information Quarterly, Volume 42 (2025)
- **DOI:** 10.1016/j.giq.2025.102082
- **Publication Date:** Available online 1 October 2025
- **Methodology:** PRISMA 2020
- **Final Study Count:** 55 articles

---

## Source Information

### Paper Metadata

```yaml
paper:
  title: "An exploration of agile government in the public sector: A systematic literature review at macro, meso, and micro levels of analysis"
  authors:
    - name: "Kuang-Ting Tai"
      affiliation: "Nova Southeastern University"
      email: "ktai@nova.edu"
      role: "Corresponding author"
    - name: "Pallavi Awasthi"
      affiliation: "Nova Southeastern University"
      email: "pawasthi@nova.edu"
  
  publication:
    journal: "Government Information Quarterly"
    volume: 42
    year: 2025
    doi: "10.1016/j.giq.2025.102082"
    publisher: "Elsevier Inc."
    available_online: "2025-10-01"
    received: "2024-06-22"
    revised: "2025-09-23"
    accepted: "2025-09-23"
  
  keywords:
    - "Agile"
    - "Agility"
    - "Agile management"
    - "Agile governance"
    - "PRISMA"
    - "Systematic literature review"
```

---

## Search Strategy (from Paper)

### Databases Used

**Source:** Section 2.1 "Identification and search strategy", page 3

The paper conducted searches across **three major social science databases**:

1. **Web of Science**
2. **EBSCOhost**
3. **ProQuest Social Science Premium**

### Search Period

- **Coverage:** All available years up to May 2023
- **Last Search Date:** May 2023

### Search Query

**Source:** Section 2.1, page 3

Three keyword combinations were applied to **titles, abstracts, and author-identified keywords**:

```
("agile" AND "government")
OR
("agile" AND "governance")
OR
("agile" AND "public")
```

**Search Fields:**
- Title
- Abstract
- Author-identified keywords

**Logic:** Articles were included if **any** of these combinations appeared in the searchable fields.

### Inclusion Criteria

**Source:** Section 2.2 "Screening and eligibility", page 3

1. **Language:** English-language publications only
2. **Peer Review:** Only peer-reviewed articles
3. **Content:** Substantive discussion of agile in public sector context
4. **Accessibility:** Articles must be accessible for full-text review

### Exclusion Criteria

1. Non-English publications
2. Non-peer-reviewed sources
3. Articles without substantive agile discussion
4. Inaccessible full texts

---

## PRISMA Flow

**Source:** Figure 1, page 3

### Search Results

1. **Initial Retrieval:**
   - Web of Science: Not specified
   - EBSCOhost: Not specified
   - ProQuest Social Science Premium: Not specified
   - **Combined Total:** 1,102 records

2. **After Duplicate Removal:**
   - **Unique Records:** 675 articles

3. **After Title/Abstract Screening:**
   - **Eligible for Full-Text Review:** Not specified exactly
   - **Excluded:** Records not meeting initial criteria

4. **After Full-Text Review:**
   - **Final Included Studies:** **55 articles**

### Study Characteristics

**Source:** Section 3 "Results", pages 3-14

**Publication Years:**
- Range: 2002-2023
- Peak publication period: 2018-2023 (post-digital transformation era)

**Journal Distribution:**
- 47% published in public management and administration journals
- 29% in information science and technology journals
- 24% in interdisciplinary and other fields

**Geographic Focus:**
- United States: Largest representation
- European countries: Significant presence
- Australia, Canada, New Zealand: Notable contributions
- Other regions: Limited representation

**Analysis Levels:**
- **Micro Level** (Project Management): 42% of studies
- **Meso Level** (Organizational Management): 31% of studies
- **Macro Level** (Governance Structure): 27% of studies

---

## ELIS Database Assessment

### ELIS Confirmed Database Access

**Source:** ELIS Protocol v2.0 draft-08.1, Section 3.2

ELIS has programmatic API access to **8 databases**:

1. ✅ **Scopus** – Multidisciplinary database
2. ✅ **Web of Science** – High-impact journal indexing
3. ✅ **IEEE Xplore** – Technical literature
4. ✅ **Semantic Scholar** – AI-enhanced (200M+ papers)
5. ✅ **OpenAlex** – Open bibliographic database (250M+ works)
6. ✅ **CrossRef** – DOI registration agency (130M+ records)
7. ✅ **CORE** – Open access aggregator (300M+ papers)
8. ✅ **Google Scholar** – Via Apify API

### Database Overlap Analysis

**Tai & Awasthi (2025) Databases:**
- Web of Science ✅
- EBSCOhost ❌ (API access pending)
- ProQuest Social Science Premium ❌ (API access pending)

**Confirmed Overlap:** **1 out of 3 databases (33%)**

**Status:**
- ✅ Web of Science: CONFIRMED MATCH
- ⏳ EBSCOhost: PENDING Imperial College API access
- ⏳ ProQuest Social Science Premium: PENDING Imperial College API access

### Supplementary Coverage Analysis

While ELIS has only 1 direct database match, it has access to **complementary databases** that may contain overlapping content:

| ELIS Database | Coverage Relevance | Expected Contribution |
|---------------|-------------------|----------------------|
| **Scopus** | High overlap with WoS | May recover 40-60% of WoS-indexed studies |
| **Web of Science** | Direct match | Primary source for validation |
| **OpenAlex** | Comprehensive aggregator | May contain EBSCOhost/ProQuest content |
| **CrossRef** | Publisher metadata | DOI-based retrieval for known studies |
| **Google Scholar** | Broadest coverage | Likely contains most public studies |
| **Semantic Scholar** | CS/interdisciplinary | Good for digital government topics |

**Estimated Total Coverage:** 60-75% (pending API access for EBSCOhost and ProQuest)

---

## Expected Performance

### Baseline Predictions (Before API Access)

**With Current Database Access (Web of Science only):**

| Metric | Conservative | Realistic | Optimistic |
|--------|-------------|-----------|------------|
| **Direct Retrieval** | 30% | 45% | 60% |
| **Via Supplementary DBs** | +15% | +20% | +25% |
| **Total Expected** | 45% | 65% | 85% |

**Rationale:**
- Web of Science alone may index 40-50% of the 55 studies
- Scopus overlap with WoS typically provides additional 15-25% coverage
- Google Scholar and OpenAlex provide broad safety net
- CrossRef enables DOI-based verification

### Updated Predictions (With Full API Access)

**If EBSCOhost and ProQuest APIs are obtained:**

| Metric | Conservative | Realistic | Optimistic |
|--------|-------------|-----------|------------|
| **Direct Database Match** | 60% | 75% | 85% |
| **Via Supplementary DBs** | +10% | +15% | +10% |
| **Total Expected** | 70% | 90% | 95% |

**Success Criteria:**
- ✅ **Minimum Acceptable:** 50% retrieval rate
- ✅ **Target Performance:** 65% retrieval rate
- ⭐ **Excellent Performance:** 75%+ retrieval rate

---

## Benchmark Configuration

### Search Query Translation

**Original Paper Query:**
```
("agile" AND "government") OR
("agile" AND "governance") OR
("agile" AND "public")
```

**ELIS Query (Structured):**
```yaml
search_query:
  boolean_logic: OR
  groups:
    - terms: ["agile", "government"]
      operator: AND
    - terms: ["agile", "governance"]
      operator: AND
    - terms: ["agile", "public"]
      operator: AND
  
  fields:
    - title
    - abstract
    - keywords
  
  filters:
    language: "en"
    peer_reviewed: true
    date_start: "2002-01-01"
    date_end: "2023-05-31"
```

### Matching Strategy

**Method:** Fuzzy keyword matching with title similarity

```python
matching_algorithm = {
    "primary": "title_fuzzy_match",
    "threshold": 0.85,
    "fallback": "doi_exact_match",
    "secondary": "author_year_title_match",
    "verification": "manual_review"
}
```

**Matching Criteria:**
1. **Exact DOI match** (if DOI available) → 100% confidence
2. **Title similarity ≥85%** + Author match → 95% confidence
3. **Title similarity ≥85%** + Year match → 85% confidence
4. **Title similarity 70-84%** → Flag for manual review
5. **Title similarity <70%** → Exclude

---

## Reference List Extraction

### Status: TO BE COMPLETED

**Action Required:**
1. Extract all 55 references from pages 16-17 of the PDF
2. Parse into structured format with:
   - Authors
   - Year
   - Title
   - Journal/Source
   - DOI (if available)
   - Volume/Issue/Pages

### Expected Format

```csv
reference_id,authors,year,title,journal,volume,issue,pages,doi
1,"Aleinikova et al.",2020,"Project management technologies in public administration","Journal of Management Information and Decision Sciences",23,,"510-522",
2,"Androniceanu, A.",2024,"Generative artificial intelligence, present and perspectives in public administration","Administration & Public Management Review",43,,"105-119",
...
```

---

## Validation Methodology

### Phase 1: Automated Retrieval

1. **Execute ELIS Search**
   - Run queries across all 8 ELIS databases
   - Apply date filter: 2002-01-01 to 2023-05-31
   - Apply language filter: English only
   - Apply peer-review filter

2. **Deduplication**
   - Remove exact DOI duplicates
   - Remove title duplicates (≥95% similarity)
   - Flag near-duplicates (85-95% similarity) for review

3. **Matching Against Gold Standard**
   - Load 55 gold standard references
   - Apply matching algorithm
   - Calculate retrieval metrics

### Phase 2: Manual Verification

1. **Review High-Confidence Matches**
   - Verify all matches with ≥95% confidence
   - Spot-check 20% of 85-95% confidence matches

2. **Investigate Misses**
   - For each unretrieved study, document:
     - Which databases should have indexed it
     - Why ELIS didn't retrieve it
     - Whether it's a database coverage issue or query issue

3. **False Positive Analysis**
   - Review ELIS retrievals not in gold standard
   - Determine if they should have been included
   - Document query precision issues

### Phase 3: Results Analysis

**Metrics to Calculate:**

```python
metrics = {
    "retrieval_rate": "Retrieved / 55",
    "precision": "True Positives / (True Positives + False Positives)",
    "recall": "Retrieved / 55",  # Same as retrieval rate
    "f1_score": "2 * (Precision * Recall) / (Precision + Recall)",
    "database_contribution": "Studies per database",
    "cost_per_study": "Total API cost / Retrieved studies",
    "execution_time": "Total minutes"
}
```

**Expected Outputs:**
1. Quantitative performance report
2. Database-by-database contribution analysis
3. Query effectiveness assessment
4. Recommendations for protocol refinement

---

## Comparison with Darmawan Benchmark

### Comparative Analysis Framework

| Dimension | Darmawan (2021) | Tai & Awasthi (2025) |
|-----------|-----------------|----------------------|
| **Topic Domain** | Agile development in government digital services | Agile government (macro/meso/micro) |
| **Journal** | Asian Journal of Comparative Politics | Government Information Quarterly |
| **Study Count** | 78 studies | 55 studies |
| **Database Overlap** | 0/4 direct matches | 1/3 direct matches (WoS) |
| **Retrieval Rate** | 66.67% (52/78) | TBD |
| **Cost** | $0.50 | TBD |
| **Runtime** | 22 minutes | TBD |

### Expected Insights

**Hypotheses:**
1. **H1:** Retrieval rate will be higher due to better database overlap (WoS confirmed)
2. **H2:** Precision will be higher due to narrower topic scope
3. **H3:** Runtime will be similar (~20-30 minutes)
4. **H4:** Cost will be comparable ($0.40-$0.60)

**Cross-Benchmark Questions:**
- Does WoS access significantly improve retrieval?
- How does Scopus compare to WoS for GIQ coverage?
- Is Google Scholar consistently the top performer?
- Do different topic focuses affect retrieval patterns?

---

## Dependencies and Prerequisites

### Critical Path Items

**BLOCKING:**
- ⏳ **EBSCOhost API Access** – Pending Imperial College support
  - Status: Request submitted to Imperial College IT support
  - Expected resolution: TBD
  - Impact: Required for 100% database parity

- ⏳ **ProQuest Social Science Premium API Access** – Pending Imperial College support
  - Status: Request submitted to Imperial College IT support
  - Expected resolution: TBD
  - Impact: Required for 100% database parity

**REQUIRED:**
- ✅ **Web of Science API Access** – Already available in ELIS
- ✅ **Tai & Awasthi (2025) PDF** – Available
- ⏳ **Reference List Extraction** – To be completed
- ⏳ **Reference List Parsing** – To be completed

**OPTIONAL:**
- 📋 **Author Contact** – Verify search strategy details
- 📋 **Raw Search Results** – Request from authors for validation

### Timeline

```
Week 1: API Access & Reference Extraction
├── Day 1-2: Monitor Imperial College API access requests
├── Day 3-4: Extract and parse 55 references
└── Day 5: Validate reference list completeness

Week 2: Benchmark Execution
├── Day 1: Configure ELIS queries
├── Day 2-3: Execute searches (with available APIs)
├── Day 4: Perform matching and analysis
└── Day 5: Generate preliminary results

Week 3: Validation & Documentation
├── Day 1-2: Manual verification of matches
├── Day 3: False positive/negative analysis
├── Day 4: Comparative analysis with Darmawan
└── Day 5: Final report and recommendations
```

---

## Risk Assessment

### High-Priority Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **EBSCOhost API not obtained** | Medium | High | Proceed with partial benchmark; document coverage gap |
| **ProQuest API not obtained** | Medium | High | Proceed with partial benchmark; document coverage gap |
| **Reference extraction errors** | Low | High | Manual verification of all 55 references |
| **Database downtime during test** | Low | Medium | Schedule backup execution windows |
| **Query translation issues** | Medium | Medium | Validate query logic before full execution |

### Low-Priority Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **API rate limits** | Low | Low | Implement exponential backoff |
| **Cost overruns** | Low | Low | Monitor API costs in real-time |
| **Runtime exceeds expectations** | Medium | Low | Optimize queries; use parallel execution |

---

## Success Criteria

### Tier 1: Minimum Viable Benchmark

✅ **Required for Success:**
- Retrieval rate ≥50%
- Precision ≥70%
- Complete execution without errors
- Documented methodology
- Comparison with Darmawan benchmark

### Tier 2: Good Performance

⭐ **Target Metrics:**
- Retrieval rate ≥65%
- Precision ≥80%
- Cost <$1.00
- Runtime <30 minutes
- Database-level contribution analysis

### Tier 3: Excellent Performance

🏆 **Stretch Goals:**
- Retrieval rate ≥75%
- Precision ≥85%
- Cost <$0.60
- Runtime <25 minutes
- Actionable recommendations for protocol improvement

---

## Open Questions

### Methodological Questions

1. **Database Coverage:**
   - Q: What percentage of the 55 studies are indexed in Web of Science?
   - Action: Analyze database overlap after API access

2. **Query Precision:**
   - Q: Does the broad query ("agile" AND "public") introduce too many false positives?
   - Action: Test precision with subset validation

3. **Temporal Bias:**
   - Q: Does ELIS perform differently for older (2002-2010) vs. newer (2018-2023) studies?
   - Action: Segment analysis by publication year

### Technical Questions

1. **API Integration:**
   - Q: How to optimize EBSCOhost/ProQuest queries for maximum recall?
   - Action: Consult API documentation when access is obtained

2. **Matching Algorithm:**
   - Q: Should we adjust fuzzy matching threshold for interdisciplinary studies?
   - Action: Sensitivity analysis on matching parameters

3. **Cost Optimization:**
   - Q: Can we reduce API calls without sacrificing retrieval rate?
   - Action: Analyze database contribution before full execution

---

## Next Steps

### Immediate Actions (Priority 1)

1. ✅ **Document Benchmark** – COMPLETED
2. ⏳ **Monitor API Access Requests** – IN PROGRESS
   - Check Imperial College IT support for EBSCOhost access
   - Check Imperial College IT support for ProQuest access
3. ⏳ **Extract Reference List** – PENDING
   - Parse pages 16-17 of PDF
   - Create structured CSV with all 55 references
4. ⏳ **Validate Reference Extraction** – PENDING
   - Manual verification of all entries
   - Cross-check with paper's reported study count

### Secondary Actions (Priority 2)

5. ⏳ **Configure ELIS Queries** – PENDING API access
   - Translate paper's search strategy to ELIS format
   - Test query logic with sample searches
6. ⏳ **Prepare Validation Scripts** – PENDING
   - Develop matching algorithm
   - Create analysis pipeline
7. ⏳ **Design Comparison Framework** – PENDING
   - Align with Darmawan benchmark structure
   - Identify cross-benchmark metrics

### Future Actions (Priority 3)

8. 📋 **Execute Benchmark** – BLOCKED by API access
9. 📋 **Analyze Results** – BLOCKED by execution
10. 📋 **Document Findings** – BLOCKED by analysis

---

## Appendices

### Appendix A: Paper Abstract

**Source:** Page 1

> "Originating from private sector software development, agile has permeated the public sector, fostering innovative reforms not just in project management but also in organizational management and collaborative governance. Despite its widespread adoption, there exists a paucity of research delving into the intricacies of agile practices, particularly for the potential conflicts and interactions with the traditional waterfall-based approaches. Employing the Preferred Reporting Items for Systematic reviews and Meta-Analyses (PRISMA) method, this systematic review aims to address three fundamental research questions concerning the conceptualization, implementation, and impacts of agile government. To deepen theoretical insight and practical application, our study classifies agile into three distinct levels: Micro (project management), Meso (organizational management), and Macro (governance structure). Our analysis uncovers substantial variations in agile practices across these levels, reflecting a deliberate strategy aimed at harmonizing with existing bureaucratic systems. This study concludes by offering policy implications and delineating avenues for future research endeavors."

### Appendix B: Research Questions

**Source:** Section 1, page 2

The systematic review addresses three fundamental research questions:

1. **RQ1: Conceptualization**
   - How is agile conceptualized and applied across different levels (micro, meso, macro) in the public sector?

2. **RQ2: Implementation**
   - What are the key challenges and enabling factors in implementing agile practices in public sector organizations?

3. **RQ3: Impact**
   - What impacts have agile practices demonstrated in public sector contexts, and how do these vary across different implementation levels?

### Appendix C: Analysis Framework

**Source:** Section 2.3, pages 3-4

The paper employs a **multi-level analysis framework**:

**Micro Level (Project Management):**
- Agile methodologies for IT projects
- Scrum, Kanban, and hybrid approaches
- Project delivery and stakeholder engagement

**Meso Level (Organizational Management):**
- Organizational agility and adaptability
- Internal process transformation
- Cross-functional team collaboration

**Macro Level (Governance Structure):**
- Agile governance frameworks
- Policy agility and regulatory adaptation
- Multi-stakeholder collaboration and co-creation

### Appendix D: Key Findings Summary

**Source:** Section 3-5, pages 4-14

**Main Findings:**

1. **Conceptual Diversity:**
   - Agile is interpreted differently across levels
   - Micro-level: Primarily technical/methodological
   - Meso-level: Organizational culture and structure
   - Macro-level: Governance philosophy and stakeholder engagement

2. **Implementation Challenges:**
   - Bureaucratic resistance to change
   - Regulatory and legal constraints
   - Resource limitations
   - Skills gap and training needs
   - Cultural misalignment with agile values

3. **Success Factors:**
   - Executive leadership support
   - Clear communication and training
   - Incremental adoption strategies
   - Hybrid approaches (agile + waterfall)
   - Stakeholder engagement

4. **Observed Impacts:**
   - Improved project delivery times (micro)
   - Enhanced organizational responsiveness (meso)
   - Better citizen engagement (macro)
   - Mixed results on cost savings
   - Challenges in measuring outcomes

---

## Document Control

**Version:** 1.0  
**Status:** Draft  
**Author:** ELIS Research Team  
**Reviewers:** TBD  
**Approval:** Pending  

**Change Log:**

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-29 | 1.0 | Initial benchmark documentation | ELIS Team |

**Related Documents:**
- BENCHMARK_DARMAWAN_2021.md
- BENCHMARK_DOCUMENTATION_REGISTRY.md
- ELIS_2025_SLR_Protocol_Electoral_Integrity_Strategies_2026-01-28_v2.0_draft-08.1.pdf

---

**END OF DOCUMENT**
