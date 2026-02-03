# Google Scholar Integration Notes

## Current Status (2026-01-30)

**Actor:** `easyapi/google-scholar-scraper`  
**Status:** ✅ Working (switched from marco.gullo due to rate limiting)  
**Results:** 10 per query (free tier)  
**Cost:** $0.0001 per run

---

## Implementation Details

### Actor Configuration
```python
client.actor("easyapi/google-scholar-scraper").call({
    "query": "simplified keyword query",
    "maxItems": 100  # Free tier returns max 10
})
```

### Limitations
1. **Free Tier:** 10 results per query (vs 100-500 needed)
2. **No Year Filtering:** Cannot filter by publication year (2002-2023)
3. **Query Format:** Works best with simple keywords (no complex Boolean)
4. **Field Mapping:** Different output structure than marco.gullo

### Output Mapping
```python
{
    "title": entry.get("title"),
    "authors": entry.get("authors"),
    "year": entry.get("year"),
    "abstract": entry.get("snippet"),  # Note: 'snippet' not 'abstract'
    "url": entry.get("link"),
    "pdf_url": entry.get("pdf_link"),
    "citation_count": entry.get("citations"),
    "google_scholar_id": entry.get("result_id")
}
```

---

## Integration History

### Timeline

**2026-01-29:** Initial integration with `marco.gullo/google-scholar-scraper`
- ✅ Successful test runs (50-500 results)
- ✅ Proper configuration reading
- ✅ Timeout handling (12 min for GS, 5 min for others)

**2026-01-30 Morning:** Rate limiting issues discovered
- ❌ All queries returning 0 results
- ❌ HTTP 429 errors (Too Many Requests)
- ❌ ~10 test runs triggered Google Scholar blocking

**2026-01-30 Afternoon:** Alternative actor evaluation
- ✅ Tested `easyapi/google-scholar-scraper` - **WORKS**
- ❌ Tested `marco.gullo` with delays - Still blocked
- ⚠️ Evaluated `primeparse` - Too new (1 user, untested)

**2026-01-30 16:19:** Production switch to EasyAPI
- ✅ 10 results retrieved successfully
- ✅ No rate limiting
- ✅ Low cost ($0.0001 per run)

---

## Rate Limiting Investigation

### Root Cause
Google Scholar detected multiple rapid requests from marco.gullo actor's proxy pool and blocked those specific Apify proxy IPs.

### Evidence
- Simple query "agile" (should return 1000s) → 0 results
- HTTP 429 status code on all requests
- Apify run status: SUCCEEDED but 0 data
- Pattern: 10+ retries across 3 query strategies

### Solution
Switch to `easyapi/google-scholar-scraper` which uses a different proxy pool that wasn't blocked.

---

## Comparison: Tested Actors

| Actor | Status | Results | Free Tier | Cost | Notes |
|-------|--------|---------|-----------|------|-------|
| **marco.gullo** | ❌ Rate Limited | 0 (429 errors) | Yes | Free | Currently blocked |
| **easyapi** | ✅ Working | 10 (free), up to 5000 (paid) | 10 results | $10/1000 | **PRODUCTION** |
| **primeparse** | ⚠️ Untested | Up to 50 | Unknown | Pay per use | Too new (1 user) |

---

## Upgrade Path

### To Get Full Results (100-500+)

**Option 1: Upgrade Apify Account**
1. Go to https://apify.com/pricing
2. Choose paid plan (~$49/month or pay-as-you-go)
3. Estimated cost: $10-20 for typical Phase 1 usage
4. No code changes needed

**Option 2: Wait for Rate Limit Reset**
1. Wait 24 hours for marco.gullo proxy IPs to reset
2. Switch back to `marco.gullo/google-scholar-scraper`
3. Risk: May get rate limited again with heavy usage

**Option 3: Accept Free Tier Limitation**
1. Keep current setup (10 results per query)
2. Document limitation in benchmark report
3. Still provides value for Phase 1 validation

---

## Current Production Configuration

**Script:** `scripts/google_scholar_harvest.py`  
**Actor:** `easyapi/google-scholar-scraper`  
**Query Simplification:** Removes Boolean operators, keeps keywords only  
**Retry Logic:** 3 attempts with 30-60s delays  
**Deduplication:** By title (case-insensitive)

**Example Query Transformation:**
```
Input:  ("agile" AND "government") OR ("agile" AND "governance") OR ("agile" AND "public")
Output: agile government agile governance agile public
```

---

## Lessons Learned

1. **Rate Limiting is Real:** Even with Apify proxy, Google Scholar aggressively blocks
2. **Multiple Actors Available:** Having alternatives prevents complete blocking
3. **Free Tiers Have Limits:** 10 results sufficient for testing, not production
4. **Simple Queries Work Better:** Complex Boolean queries may trigger scrutiny
5. **Delays Help But Not Enough:** 45-90s delays didn't prevent blocking on same proxy pool

---

## Recommendations

### Short Term (Phase 1)
- ✅ Use EasyAPI with free tier (10 results)
- ✅ Document limitation in benchmark report
- ✅ Proceed with 6 working databases

### Long Term (Production)
- 💰 Upgrade Apify account for full results
- 🔄 Rotate between multiple actors to avoid blocking
- ⏰ Add longer delays (5-10 minutes) between queries
- 📊 Monitor Apify usage and costs

---

## Support & Resources

**Apify Console:** https://console.apify.com  
**EasyAPI Actor:** https://apify.com/easyapi/google-scholar-scraper  
**Pricing:** https://apify.com/pricing  
**Support:** https://apify.com/contact

---

**Last Updated:** 2026-01-30  
**Status:** ✅ Production Ready (Free Tier)  
**Next Review:** After Phase 1 results analysis
