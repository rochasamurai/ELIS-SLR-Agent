# ELIS Benchmark Test - Darmawan (2021)

## Purpose
Validate ELIS SLR Agent retrieval capabilities against a published semi-systematic review as recommended by supervisor.

## Benchmark Standard

**Paper:**
Darmawan, I. (2021). E-voting adoption in many countries: A literature review. *Asian Journal of Comparative Politics, 6*(4), 482-504.
https://doi.org/10.1177/20578911211040584

**Key Details:**
- **Studies:** 78 journal articles (2005-2020)
- **Databases:** Google Scholar, ACM Digital Library, Science Direct, J-STOR
- **Focus:** E-voting adoption research
- **Inclusion:** Scopus-indexed journals only, English language

## Test Objectives

### Primary (Essential)
✅ **Retrieval Rate:** Retrieve ≥70% of Darmawan's 78 studies (target: 75-80%)

### Secondary (Nice to Have)
- Validate search strategy effectiveness
- Compare database coverage (Google Scholar vs. Scopus/WoS)
- Identify additional relevant studies missed by Darmawan

### Tertiary
- Establish ELIS credibility before full systematic review
- Demonstrate to supervisor that ELIS works as intended

## Configuration

See `benchmarks/config/benchmark_config.yaml` for complete parameters.

**Search Terms:**
```
("e-voting" OR "electronic voting" OR "internet voting" OR 
 "online voting" OR "i-voting" OR "remote voting")
AND
("adoption" OR "implementation" OR "deployment" OR "acceptance" 
 OR "intention to use" OR "diffusion")
AND
("election" OR "voting" OR "electoral" OR "ballot")
```

**Date Range:** 2005-01-01 to 2020-12-31

**Databases:** Scopus, Web of Science, IEEE Xplore, Semantic Scholar, OpenAlex, CrossRef, CORE

## Running the Test
```bash
python benchmarks/scripts/run_benchmark.py
```

## Expected Outcomes

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Retrieval Rate** | ≥70% (55+ of 78 studies) | Demonstrates ELIS finds published studies |
| **Precision** | ≥75% | ELIS results are relevant |
| **Additional Studies** | 40-90 studies | ELIS broader database coverage |

## Scope Differences

**Darmawan (2021):**
- Focus: E-voting **adoption** only (narrower)
- Databases: Google Scholar (broad but inconsistent coverage)
- Filter: Scopus-indexed journals

**ELIS:**
- Focus: Electoral **integrity strategies** (broader)
- Databases: Systematic coverage (Scopus, WoS, IEEE, etc.)
- Filter: Peer-reviewed, reproducible criteria

**Expected Overlap:** 70-80% due to scope difference

## Success Criteria

✅ **PASS:** Retrieval rate ≥70%
❌ **FAIL:** Retrieval rate <70%

## Notes

- Benchmark validates ELIS technical capability, not scope alignment
- Lower overlap expected due to different research questions
- ELIS expected to find additional studies = positive outcome
- Results will be documented in `docs/BENCHMARK_VALIDATION_REPORT.md`

## Timeline

1. Extract 78 references from Darmawan PDF → CSV
2. Configure ELIS with benchmark parameters
3. Run search across 7 databases
4. Match results against Darmawan's 78 studies
5. Calculate metrics and generate report
6. Share with supervisor

**Status:** In progress
**Branch:** `benchmark/darmawan-2021`
