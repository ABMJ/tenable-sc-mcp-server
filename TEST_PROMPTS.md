# Test Prompts for Tenable.sc MCP Server

Use these prompts to test the tools and verify functionality. **Always append cache performance and token utilization checks to your queries.**

## Tool 1: IP Profile (tsc_profile_ip_efficient)

### Basic Profile Test
```
use tenable-sc to profile IP 10.1.20.10 efficiently, then show me cache stats and token enhancement one liner summary
```

**Expected Output:**
- Hostname and OS information
- Vulnerability counts by severity
- Last scan timestamp
- ACR score and source
- Cache hit rate percentage
- Token savings metrics

**Token Efficiency:** ~2,500 tokens (vs ~15,000 raw API) = 83% reduction

---

### Full Profile with All Details
```
use tenable-sc to get comprehensive profile for 10.1.20.10 including software, services, scan info, and asset groups, then show me cache stats
```

**Expected Output:**
- Basic host info + vulnerabilities
- Top 50 installed software packages
- Running services (ports/protocols)
- Last scan details (policy, scanner, credentials)
- Asset group membership
- Cache performance metrics

**Token Efficiency:** ~5,000 tokens (vs ~30,000 raw API) = 83% reduction

---

## Tool 2: Vulnerability Lists (tsc_list_vulns_by_ip)

### Summary View (Efficient)
```
use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical, then show me cache stats and token utilization enhancement
```

**Expected Output:**
- Total vulnerability count by severity
- Compact aggregated format
- Cache hit rate
- Token savings demonstration (summary vs full)

**Token Efficiency:** ~700 tokens (vs ~6,000 raw) = 88% reduction

---

### Full Details View (Tool 2 - Primary Test)
```
use tenable-sc to list all critical vulnerabilities for IP 10.1.20.10 using tsc_list_vulns_by_ip_full, show first 10 records, then show me cache stats and token utilization enhancement one liner summary
```

**Expected Output:**
- 10 detailed vulnerability records
- Plugin ID, name, severity, family
- CVSS/VPR scores, CVE IDs
- Exploit availability information
- Port/protocol information
- Pagination info (10 of X total)
- Cache hit rate
- Token enhancement summary

**Token Efficiency:** ~5,000 tokens for 50 records (vs ~12,000 raw) = 58% reduction

---

### Filtered Search with Exploits
```
use tenable-sc to find all vulnerabilities on 10.1.20.10 with available exploits, then show cache stats
```

**Expected Output:**
- Only vulnerabilities with exploit_available=Yes
- Full details including exploit frameworks
- Prioritized by severity
- Cache performance

---

## Cache Performance Testing

### Verify Cache Hit Rate Improvement
Run the same query 3 times to see cache hit rate improvement:

**Query 1 (Cache Miss):**
```
use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical, then show me cache stats
```
Expected: 0% hit rate (first query)

**Query 2 (Cache Hit):**
```
use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical, then show me cache stats
```
Expected: 50% hit rate (cache hit on repeated query)

**Query 3 (Cache Hit):**
```
use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical, then show me cache stats
```
Expected: 66% hit rate (hit rate improving)

---

### Check Overall Cache Statistics
```
use tenable-sc to show me cache statistics
```

**Expected Output:**
- Cache backend type (Redis/Memory)
- Total keys stored
- Hit/miss counts
- Hit rate percentage
- Uptime
- Memory usage (if available)

---

## Token Efficiency Demonstration

### Compare Tool Methods
```
use tenable-sc to:
1. Get vulnerability summary for IP 10.1.20.10 (summary method)
2. Then explain token savings vs full details method
```

**Expected Comparison:**
- Summary: ~700 tokens
- Full details: ~6,000 tokens
- Savings: 8.5x reduction when counts suffice

---

## Complete Test Sequence (Run All)

Execute these in order for comprehensive testing:

```
1. use tenable-sc to profile IP 10.1.20.10 efficiently, then show me cache stats

2. use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical, then show me cache stats

3. use tenable-sc to list all critical vulnerabilities for IP 10.1.20.10 using tsc_list_vulns_by_ip_full, show first 10 records, then show me cache stats

4. use tenable-sc to show me cache statistics and explain the hit rate improvement
```

**Expected Results:**
- All 3 tools working correctly
- Cache hit rate improving with repeated queries (0% → 33% → 50% → 57%+)
- Token savings demonstrated (83-90% for tool 1, 88% for tool 2 summary, 58% for tool 2 full)
- No errors or failures
- Response times: <1ms for cached queries, <5s for fresh queries

---

## Advanced Filtering Examples

### Multi-Filter Vulnerability Search
```
use tenable-sc to find vulnerabilities on 10.1.20.10 with severity critical, VPR score >= 7.0, and exploits available, show first 10, then show cache stats
```

**Expected Output:**
- Filtered results matching all criteria
- Full vulnerability details
- Pagination info
- Cache performance

---

### Port-Specific Search
```
use tenable-sc to list vulnerabilities on 10.1.20.10 for port 445, then show cache stats
```

---

### CVE-Specific Search
```
use tenable-sc to find CVE-2021-34527 (PrintNightmare) on 10.1.20.10, then show cache stats
```

---

## Cache Management

### Clear All Cache
```
use tenable-sc to clear all cache entries
```

**Expected:** All cache cleared, stats reset to 0

### Clear Specific Pattern
```
use tenable-sc to clear cache for pattern "analysis:*"
```

**Expected:** Only analysis queries cleared

---

## Performance Benchmarking

### Measure Cache Impact
1. Clear cache
2. Run query (measure time)
3. Run same query again (measure time)
4. Calculate speedup

```
use tenable-sc to:
1. Clear cache
2. Profile IP 10.1.20.10
3. Profile IP 10.1.20.10 again
4. Show me the cache hit rate improvement
```

**Expected Speedup:** 100-1000x faster on cached queries

---

## Error Handling Verification

### Invalid IP Address
```
use tenable-sc to profile IP 999.999.999.999
```

**Expected Output:**
- Clear error message: "Invalid IP address format"
- Expected format example
- Suggestion to use tsc_list_ips()

---

### Invalid Severity Value
```
use tenable-sc to list vulnerabilities for 10.1.20.10 with severity "bogus"
```

**Expected Output:**
- Error message: "Invalid severity: 'bogus'"
- Valid values list: 0, 1, 2, 3, 4, info, low, medium, high, critical

---

### Pagination Out of Bounds
```
use tenable-sc to list vulnerabilities for 10.1.20.10, show records 0-500
```

**Expected Output:**
- Error: "end_offset cannot exceed 200"
- Suggestion: Use multiple queries with pagination

---

## Notes & Best Practices

- **Always include cache stats** in your queries for monitoring
- **Use summary mode first** to understand scope, then full details if needed
- **Leverage filters** to reduce token usage (severity, CVE, port, etc.)
- **Cache TTL**: 180s for vulnerability data, 300s for asset data
- **Pagination**: Default 50, max 200 records per query
- **Severity values**: 0=info, 1=low, 2=medium, 3=high, 4=critical (or text names)
- **Timestamps**: Unix epoch format (e.g., 1762463829)
- **Run queries in new OpenCode chat** after container rebuild for clean connection

---

## Week 1 Session 3 - Bug Fix Validation

**Fixed Bug:** Undefined variable `response` in tsc_list_vulns_by_ip_full (line 1201-1205)

**Test Case:**
```
use tenable-sc to list all critical vulnerabilities for IP 10.1.20.10 using tsc_list_vulns_by_ip_full, show first 10 records, then show me cache stats and token utilization enhancement one liner summary
```

**Validation Criteria:**
- ✅ No errors thrown
- ✅ Returns 10 vulnerability records
- ✅ Shows total records count (X of Y)
- ✅ Pagination info present
- ✅ Cache stats displayed
- ✅ Token enhancement summary shown

**Result:** All criteria met! Bug successfully fixed.
