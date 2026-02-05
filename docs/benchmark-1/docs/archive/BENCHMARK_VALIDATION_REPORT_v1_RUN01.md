# ELIS Benchmark Validation Report

**Date:** 2026-01-26 13:35:41  
**Status:** ❌ FAIL

## Benchmark Standard

**Paper:** Darmawan, I. (2021). E-voting adoption in many countries: A literature review.  
**Journal:** Asian Journal of Comparative Politics, 6(4), 482-504  
**DOI:** 10.1177/20578911211040584  
**Studies:** 78 (2005-2020)  
**Databases Used by Darmawan:** Google Scholar, ACM Digital Library, Science Direct, J-STOR

## ELIS Configuration

**Search Terms:**
```
("e-voting" OR "electronic voting" OR "internet voting" OR 
 "online voting" OR "i-voting" OR "remote voting")
AND ("adoption" OR "implementation" OR "deployment" OR "acceptance" 
 OR "intention to use" OR "diffusion")
AND ("election" OR "voting" OR "electoral" OR "ballot")

```

**Databases:** scopus, web_of_science, semantic_scholar, openalex, crossref, ieee_xplore, core  
**Date Range:** 2005-01-01 to 2020-12-31  
**Filters:** English language, peer-reviewed journal articles

## Validation Results

### Summary Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Retrieval Rate** | 9.0% (7/78) | ≥70.0% | ❌ |
| **Precision** | 7.1% | ≥75.0% | ❌ |
| **Recall** | 9.0% | ≥70.0% | ❌ |
| **ELIS Total Results** | 99 | - | - |
| **Additional Studies** | 92 | - | ℹ️ |

### Interpretation

**Matched Studies:** 7/78 studies from Darmawan's benchmark were successfully retrieved by ELIS.

**Missed Studies:** 71 studies from Darmawan were not found by ELIS. See detailed list below.

**Additional Studies:** ELIS found 92 additional studies not in Darmawan's review, likely due to:
- Broader database coverage (Scopus, Web of Science vs. Google Scholar)
- Systematic search methodology
- Different search string optimization

## Validation Outcome

### ❌ VALIDATION FAILED

ELIS retrieved only **9.0%** of Darmawan's studies, below the minimum threshold of 70.0%.

**Action Required:** 
1. Review search string optimization
2. Check database API configurations
3. Analyze missed studies for patterns
4. Refine screening rules
5. Re-run benchmark test


## Detailed Analysis

### Missed Studies (71 studies)

| ID | Year | Authors | Title |
|---|------|---------|-------|
| 1 | 2005 | Xenakis and Machintosh | Trust analysis of the UK e-voting pilots... |
| 4 | 2005 | Roseman Jr. and Stephenson | The effect of voting technology on voter turnout: Do compute... |
| 5 | 2005 | Oostven and van de Besselaar | Trust, identity, and the effects of voting technologies on v... |
| 6 | 2005 | Houston, Yao, Okoli and Watson | Will remote electronic voting systems increase participation... |
| 7 | 2006 | Choi | Deliberative democracy, rational participation and e-voting ... |
| 8 | 2007 | Smith | Securing e-voting as a legitimate option for e-governance... |
| 9 | 2007 | Dee | Technology and voter intent: Evidence from the California re... |
| 10 | 2007 | Card and Moretti | Does voting technology affect election outcomes? Touch-scree... |
| 11 | 2007 | Yao and Murphy | Remote electronic voting systems: An exploration of voters' ... |
| 12 | 2008 | De Jong, van Hoof, and Goosselt | Voters' perceptions of voting technology: Paper ballots vers... |

*...and 61 more. See `data/benchmark/missed_studies.csv` for complete list.*


### Sample Matched Studies (7 of 7)

| ID | Year | Authors | Title |
|---|------|---------|-------|
| 2 | 2005 | Schaupp and Carter | E-voting: From apathy to adoption... |
| 3 | 2005 | Garner and Spolaore | Why chads? Determinants of voting equipment use in the Unite... |
| 33 | 2013 | Salimonu, Osman, Shittu and Jimoh | Adoption of e-voting system in Nigeria: A conceptual framewo... |
| 43 | 2016 | Alomari | E-voting adoption in a developing country... |
| 47 | 2016 | Dolatabadi | Towards a comprehensive conceptualisation of e-voting adopti... |
| 66 | 2020 | Zhu, Azizah and Hsiao | Examining multi-dimensional trust of technology in citizens'... |
| 74 | 2020 | Mensah | Impact of performance expectancy, effort expectancy, and cit... |


## Next Steps

1. Analyze missed studies for common patterns
2. Optimize search strings based on findings
3. Verify database API connectivity
4. Re-run benchmark test
5. Iterate until validation passes


---

**Report Generated:** 2026-01-26 13:35:41  
**Script:** `benchmarks/scripts/run_benchmark.py`  
**Configuration:** `benchmarks/config/benchmark_config.yaml`  
**Gold Standard:** `data/benchmark/darmawan_2021_references.json`
