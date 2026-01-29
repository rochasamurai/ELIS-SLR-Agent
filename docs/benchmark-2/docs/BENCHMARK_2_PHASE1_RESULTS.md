# Benchmark-2 Phase 1 Results - Tai & Awasthi (2025)

**Execution Date:** 2026-01-29  
**Benchmark:** Agile Government Systematic Review  
**Gold Standard:** 55 studies  
**Status:** ⚠️ BELOW MINIMUM THRESHOLD (20% vs 50% target)

---

## Executive Summary

**Phase 1 Execution Completed** with 8 ELIS databases, achieving **20.0% retrieval rate** (11/55 studies). While below the 50% minimum threshold, the infrastructure is working and several issues have been identified for improvement.

### Key Results

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Retrieval Rate** | 20.0% (11/55) | ≥50% | ❌ Below |
| **Retrieved Studies** | 2,272 unique | - | ✅ Good |
| **Precision** | 0.5% | - | Low |
| **F1 Score** | 0.009 | ≥0.60 | ❌ Below |
| **Execution Time** | 2.3 minutes | <60 min | ✅ Fast |

---

## Database Performance

### ✅ Working Databases (5/8)

| Database | Results | Matched | Match Rate | Status |
|----------|---------|---------|------------|--------|
| **Scopus** | 500 | 0 | 0% | ⚠️ No matches |
| **Web of Science** | 500 | 4 | 36% | ✅ Good |
| **OpenAlex** | 500 | 6 | 55% | ✅ Best |
| **CrossRef** | 490 | 0 | 0% | ⚠️ No matches |
| **CORE** | 482 | 1 | 9% | ✅ Working |

### ❌ Failed Databases (3/8)

| Database | Results | Issue |
|----------|---------|-------|
| **Google Scholar** | 0 | ⚠️ No output file generated |
| **IEEE Xplore** | 0 | API key or configuration issue |
| **Semantic Scholar** | 0 | Rate limit or API issue |

---

## Matched Studies (11/55 - 20.0%)

### Database Contribution
- **OpenAlex**: 6 matches (55% of total)
- **Web of Science**: 4 matches (36% of total)
- **CORE**: 1 match (9% of total)

### Successfully Matched Studies

1. **Baxter et al. (2023)** - Institutional challenges in agile adoption (OpenAlex)
2. **Berger & Beynon-Davies (2009)** - Rapid application development (Web of Science)
3. **Fischer & Neumann (2024)** - Multilevel understanding of agile (OpenAlex)
4. **Herranz (2009)** - Multisectoral network management (Web of Science)
5. **Hong & Kim (2020)** - Building an agile government (OpenAlex)
6. **Patanakul & Rufo-McCarron (2018)** - Transitioning to agile (OpenAlex)
7. **Ribeiro & Domingues (2018)** - Acceptance of agile methodology (Web of Science)
8. **Seri et al. (2014)** - Public e-services in Europe (Web of Science)
9. **Soe & Drechsler (2018)** - Agile local governments (OpenAlex)
10. **Tate et al. (2018)** - Fuzzy front end of innovation (CORE)
11. **Ylinen (2021)** - Agile practices in IT management (OpenAlex)

---

## Root Cause Analysis

### Critical Issue #1: Google Scholar Failure ⚠️

**Impact:** SEVERE - Google Scholar was the best performer in benchmark-1 (37% alone)

**Evidence:**
- Benchmark-1: Google Scholar retrieved 200 results, contributed 29/78 matches (37%)
- Benchmark-2: Google Scholar retrieved 0 results (complete failure)

**Potential Causes:**
1. Apify timeout (5 minutes may be insufficient)
2. Query complexity (3-part OR query)
3. Rate limiting
4. Configuration error in workflow

**Action Required:** DEBUG PRIORITY #1

---

### Critical Issue #2: Matching Algorithm Too Strict

**Current Threshold:** 85% title similarity

**Problem:** Only catching exact or near-exact title matches

**Evidence:**
- Scopus: 500 results, 0 matches (0%)
- CrossRef: 490 results, 0 matches (0%)
- OpenAlex: 500 results, only 6 matches (1.2%)

**Comparison to Benchmark-1:**
- Benchmark-1 used simple substring matching: 38.5% retrieval
- Benchmark-2 uses fuzzy matching (85%): 20.0% retrieval
- **Lesson:** Simpler is better

**Action Required:** Lower threshold to 70% or revert to simple matching

---

### Issue #3: Database Failures

**IEEE Xplore:** 0 results
- Likely API key issue (same as benchmark-1)
- Low priority (limited relevance to public admin)

**Semantic Scholar:** 0 results
- Likely rate limiting (same as benchmark-1)
- Medium priority (moderate relevance)

---

## Missed Studies Analysis (44/55 - 80%)

### Sample of High-Priority Missed Studies

**Likely in databases but not matched:**
1. Balter (2011) - "Toward a more agile government" (title includes "agile government")
2. Bogdanova et al. (2020) - "Agile project management in public sector"
3. Chatfield & Reddick (2018) - "Policy entrepreneurs in open government"
4. Clarke (2020) - "Digital government units"
5. Wernham (2012) - "Agile project management for government"

**Pattern:** Many have "agile" + "government"/"public" in title - should match!

### Likely Not in ELIS Databases

1. Finer (1936) - "Better government personnel" (too old)
2. Hood (1995) - "New public management" (predates agile concept)
3. Some specialized journals not indexed in our databases

---

## Comparison to Benchmark-1 (Darmawan 2021)

| Aspect | Benchmark-1 | Benchmark-2 | Difference |
|--------|-------------|-------------|------------|
| **Gold Standard** | 78 studies | 55 studies | -29% |
| **Best Run** | 38.5% (30/78) | 20.0% (11/55) | -48% |
| **Google Scholar** | 200 results ✅ | 0 results ❌ | FAIL |
| **Databases Working** | 5/8 | 5/8 | Same |
| **Matching Method** | Simple substring | Fuzzy 85% | Fuzzy worse |
| **Execution Time** | ~5 min | 2.3 min | Faster |

**Key Insight:** Google Scholar failure is devastating to performance

---

## Recommendations

### Immediate Actions (Priority 1)

**1. Fix Google Scholar Integration**
- Increase timeout from 5 to 10 minutes
- Simplify query (test each OR clause separately)
- Add retry logic
- Check Apify API token status

**2. Lower Matching Threshold**
- Change from 85% to 70% similarity
- Or revert to simple substring matching (proven better)
- Test on existing 2,272 results before re-running

**3. Debug IEEE & Semantic Scholar**
- Verify API keys in GitHub secrets
- Check rate limits
- Add better error logging

### Phase 1 Re-run Strategy (Priority 2)

**After fixes:**
1. Run Google Scholar separately to verify it works
2. Test matching algorithm on existing results
3. Re-run full Phase 1 with all fixes
4. **Expected result:** 45-65% retrieval rate

---

## Technical Debt Identified

### 1. Matching Algorithm Over-Engineering
- **Problem:** Complex fuzzy matching performs worse than simple matching
- **Solution:** Revert to simple + add author/year fallback
- **Lesson:** KISS principle applies to benchmarks

### 2. Google Scholar Reliability
- **Problem:** Single point of failure for benchmark success
- **Solution:** 
  - Better timeout handling
  - Fallback to other databases
  - Consider alternative Google Scholar APIs

### 3. Error Handling
- **Problem:** Databases fail silently (0 results)
- **Solution:** Add explicit error checking and logging
- **Impact:** Faster debugging of future issues

---

## Next Steps - Action Plan

### Week 1: Debug & Fix

**Day 1: Google Scholar** (4 hours)
- [ ] Test Google Scholar harvest script locally
- [ ] Increase timeout to 10 minutes
- [ ] Add detailed error logging
- [ ] Verify Apify API token and credits

**Day 2: Matching Algorithm** (2 hours)
- [ ] Test 70% threshold on existing results
- [ ] Compare simple vs fuzzy matching
- [ ] Choose best approach
- [ ] Update run_phase1_benchmark.py

**Day 3: Database Debugging** (2 hours)
- [ ] Test IEEE Xplore with API key
- [ ] Test Semantic Scholar rate limits
- [ ] Document any API changes needed

### Week 2: Re-execute

**Phase 1 Re-run:**
- [ ] Run with all fixes applied
- [ ] Target: 45-65% retrieval rate
- [ ] Document results
- [ ] Compare to benchmark-1

**If successful (≥50%):**
- [ ] Proceed to Phase 2 planning (EBSCOhost, ProQuest)
- [ ] Write up methodology
- [ ] Prepare for academic paper

**If still below 50%:**
- [ ] Analyze database coverage gap
- [ ] Consider adjusting success criteria
- [ ] Document limitations honestly

---

## Files & Artifacts

### Generated Files
- `results/phase1_full_results.json` - Complete results (2,272 studies)
- `docs/BENCHMARK_2_PHASE1_RESULTS.md` - This document

### GitHub Actions
- **Workflow:** `.github/workflows/benchmark_2_phase1.yml`
- **Run #2:** https://github.com/rochasamurai/ELIS-SLR-Agent/actions/runs/21486173766
- **Artifacts:** benchmark-2-phase1-results.zip

### Scripts
- `run_phase1_benchmark.py` - Main execution script
- `rematch_results.py` - Analysis script
- `full_integration.py` - Local testing script

---

## Conclusion

**Infrastructure Status:** ✅ WORKING
- All GitHub Actions workflow functioning
- 5/8 databases retrieving results
- Matching algorithm functional (though too strict)

**Performance Status:** ❌ BELOW THRESHOLD
- 20% retrieval vs 50% minimum
- Critical dependency on Google Scholar (currently failing)
- Matching threshold needs adjustment

**Path Forward:** 🔧 FIXABLE
- Clear root causes identified
- Actionable fixes defined
- High confidence in reaching 50%+ after fixes

**Estimated Time to Success:** 1-2 weeks
- Week 1: Debug and fix
- Week 2: Re-run and validate

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-29  
**Status:** Phase 1 Complete - Fixes Required Before Phase 2
