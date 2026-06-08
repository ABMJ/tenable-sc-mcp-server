# Test Prompts for Tenable.sc MCP Server

Use these prompts to test the tools and verify functionality. **Always append cache performance and token utilization checks to your queries.**

---

## 📑 Table of Contents

### Completed Tools (Week 1)
- [Tool 1: IP Profile (tsc_profile_ip_efficient)](#tool-1-ip-profile-tsc_profile_ip_efficient)
- [Tool 2: Vulnerability Lists](#tool-2-vulnerability-lists-tsc_list_vulns_by_ip)
  - [Summary View (Efficient)](#summary-view-efficient)
  - [Full Details View](#full-details-view)
  - [Pagination Test](#pagination-test)
- [Tool 4: IP Discovery & Listing (tsc_list_ips)](#tool-4-ip-discovery--listing-tsc_list_ips)
  - [Test 1: List all IPs in Repository](#test-1-list-all-ips-in-repository)
  - [Test 2: List IPs in Asset Group](#test-2-list-ips-in-asset-group)
  - [Test 3: Reverse Lookup (Find IP Membership)](#test-3-reverse-lookup-find-ip-membership)
  - [Test 4: Filtered List with Details](#test-4-filtered-list-with-details)

### Generic/Core Tools
- [Tool 3: Cache Performance (tsc_cache_stats)](#tool-3-cache-performance-tsc_cache_stats)

### Visual Test Prompt Style Guide
- [Test Prompt Format and Best Practices](#visual-test-prompt-style-guide)

---

## Tool 1: IP Profile (tsc_profile_ip_efficient)

### Basic Profile Test
```
I am testing tsc_profile_ip_efficient to profile IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Hostname: [name], OS: [os], Vulnerabilities: C:[count] H:[count] M:[count] L:[count] I:[count]
```

**Expected Output:**
- Hostname and OS information
- Vulnerability counts by severity (Critical/High/Medium/Low/Info)
- Last scan timestamp and authentication status
- ACR score
- Installed software and services
- Asset group memberships
- Cache hit rate and token metrics

**Token Efficiency:** ~2,500 tokens (vs ~15,000 raw API) = 83% reduction

---

## Tool 2: Vulnerability Lists (tsc_list_vulns_by_ip)

### Summary View (Efficient)
```
I am testing tsc_list_vulns_by_ip_summary to get vulnerability summary for IP 10.1.20.10 with severity critical. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Total: [count], Critical: [count], High: [count], Medium: [count], Low: [count], Info: [count]
```

**Expected Output:**
- Total vulnerability count
- Breakdown by severity (Critical/High/Medium/Low/Info)
- Applied filters summary
- Compact aggregated format
- Cache hit rate and token savings

**Token Efficiency:** ~700 tokens (vs ~6,000 raw) = 88% reduction

---

### Full Details View (Tool 2 - Primary Test)
```
I am testing tsc_list_vulns_by_ip_full to list all critical vulnerabilities for IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Returned [count] records of [total] total, First 3 plugins: [list]
```

**Expected Output:**
- 10 detailed vulnerability records
- Plugin ID, name, severity, family
- CVSS v3/VPR/EPSS scores
- CVE IDs and exploit availability
- Port/protocol information
- First seen/last seen timestamps
- Synopsis and solution (200 chars each)
- Pagination info (10 of X total)
- Cache hit rate and token metrics

**Token Efficiency:** ~5,000 tokens for 50 records (vs ~12,000 raw) = 58% reduction

---

### Filtered Search with Exploits
```
I am testing tsc_list_vulns_by_ip_full to find all vulnerabilities on 10.1.20.10 with available exploits. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about filter effectiveness]
📦 RESULT: Found [count] exploitable vulns, Frameworks: [list]
```

**Expected Output:**
- Only vulnerabilities with exploit_available=Yes
- Exploit frameworks (Metasploit, ExploitDB, etc.)
- Full vulnerability details
- Prioritized by severity
- Cache performance metrics

---

## Tool 4: IP Listing (tsc_list_ips)

### Test 1: List IPs by Repository Name
```
I am testing tsc_list_ips to list all IPs in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS] 
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Total IPs: [count], First 5: [list]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked (MISS on first run, HIT on repeat)
- 🔢 Specific token count
- 📦 Total IPs: ~854, sample of first 5 IPs
- Repository: "Default"

**Token Efficiency:** ~3,400 tokens on MISS, ~3,700 on HIT (cache saves API time, not significant tokens due to large payload)

---

### Test 2: List IPs by Asset Group Name
```
I am testing tsc_list_ips to list all IPs in asset group "Windows Hosts". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used  
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Total IPs: [count], First 5: [list]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked
- 🔢 Specific token count
- 📦 Total IPs: ~174, sample of first 5 IPs
- Asset group: "Windows Hosts"

**Token Efficiency:** ~1,000-1,200 tokens (smaller result set = fewer tokens)

---

### Test 3: Reverse Lookup (Find IP Membership)
```
I am testing tsc_list_ips to find which repositories and asset groups contain IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]  
📦 RESULT: Repositories: [list], Asset Groups: [list]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked
- 🔢 Specific token count
- 📦 Repositories: ["Default"], Asset Groups: ~6 groups (filtered by total > 0)
- IP: 10.1.20.10

**Use Case:** Answer "Where does this IP show up?" for asset management

**Token Efficiency:** ~400-700 tokens (minimal payload)

---

### Test 4: Filtered IP List with Full Details
```
I am testing tsc_list_ips to list IPs in repository "Default" with asset criticality > 7 and full details. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Total IPs with ACR > 7: [count], First 3 with DNS and ACR: [list]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked  
- 🔢 Specific token count
- 📦 Total IPs: ~37 (ACR 8-10 range)
- First 3 IPs with full details:
  - IP, DNS name, ACR score (0-10 range)
  - OS, MAC, UUID included
- Applied filters: asset_criticality > 7 (converted to 7.1-10 range)

**Available Filters:** All 55+ analysis filters supported (severity, exploit_available, vpr_score, cvss_v3_base_score, first_seen, last_seen, etc.)

**Token Efficiency:** ~2,300-2,400 tokens with full details (still efficient vs raw API)

---

### Test 5: Verify Cache HIT Behavior (Repeat Test 1)
```
I am testing tsc_list_ips cache behavior by repeating Test 1 (repository "Default"). Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [MUST BE HIT]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner comparing to first query]
📦 RESULT: Confirm total IPs matches Test 1

If cache shows MISS instead of HIT, provide ERROR DETAILS. Do not suggest code or fixes.
```
- Membership counts
- Cache status: **MISS** on first run, **HIT** on repeat
- Specific token count for this query
- One-liner summary of cache performance and token usage

**Use Case:** Answer "Where does this IP show up?" for asset management

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

---

## Tool 4: IP Listing (tsc_list_ips)

**Status**: ✅ Production Ready | **Week 1 Session 1.5** | **Token Savings**: 94% | **Cache TTL**: 300s

### Basic IP Listing by Asset Group
```
use tenable-sc to list all IPs in asset group "Windows Hosts", then show me cache stats and token usage for this request
```

**Expected Output:**
- List of IP addresses in the asset group
- Total IP count
- Cache hit rate
- Token efficiency metrics

**Token Efficiency:** ~500-1,000 tokens (vs ~9,000 raw) = 94% reduction

---

### IP Listing by Repository
```
use tenable-sc to list all IPs in repository "Default", then show me cache stats and token usage for this request
```

**Expected Output:**
- List of IP addresses in the repository
- Total IP count
- Repository name confirmation
- Cache performance

---

### Filtered Listing (ACR Filter)
```
use tenable-sc to list all IPs in asset group "Windows Hosts" with ACR > 8, then show me cache stats and token usage for this request
```

**Expected Output:**
- Filtered IP list (only IPs with ACR score > 8)
- Total count after filtering
- Applied filters summary
- Cache stats

---

### Multi-Filter Query
```
use tenable-sc to list all IPs in repository "Default" with critical severity and exploit available, then show me cache stats and token usage for this request
```

**Expected Output:**
- IPs matching all filter criteria
- Filters applied summary
- Token savings vs raw API
- Cache performance

---

### Reverse Lookup (IP Membership)
```
use tenable-sc to find which repository or asset group contains IP 10.1.20.10, then show me cache stats and token usage for this request
```

**Expected Output:**
- List of repositories containing the IP
- List of asset groups containing the IP
- Membership counts
- Cache hit rate

---

### Detailed Listing (With Metadata)
```
use tenable-sc to list all IPs in asset group "Production Servers" with details including DNS, MAC, UUID, ACR, and OS, then show me cache stats and token usage for this request
```

**Expected Output:**
- IP addresses with full metadata:
  - DNS name
  - MAC address
  - UUID
  - ACR score
  - Operating system
  - Repository membership
- Cache performance
- Token utilization

---

### Cache Performance Test (Run 3 Times)

**Query 1 (Cache Miss):**
```
use tenable-sc to list all IPs in asset group "Windows Hosts", then show me cache stats and token usage for this request
```
Expected: 0% hit rate (first query)

**Query 2 (Cache Hit):**
```
use tenable-sc to list all IPs in asset group "Windows Hosts", then show me cache stats and token usage for this request
```
Expected: 50% hit rate (cache hit on repeated query)

**Query 3 (Cache Hit):**
```
use tenable-sc to list all IPs in asset group "Windows Hosts", then show me cache stats and token usage for this request
```
Expected: 66%+ hit rate (hit rate improving)

---

### Error Handling Tests

**Missing Parameters:**
```
use tenable-sc to list IPs (no parameters)
```
**Expected:** Error message: "Must provide either 'repository', 'asset_group', or 'ip' parameter"

**Both Repository and Asset Group:**
```
use tenable-sc to list IPs in repository "Default" and asset group "Windows Hosts"
```
**Expected:** Error message: "Provide only ONE of: repository, asset_group (not both)"

**Invalid IP for Reverse Lookup:**
```
use tenable-sc to find which asset groups contain IP 999.999.999.999
```
**Expected:** Error message: "Invalid IP address format"

---

## Complete Tool 4 Test Sequence

Execute these in order for comprehensive testing:

```
1. use tenable-sc to list all IPs in asset group "Windows Hosts", then show me cache stats and token usage for this request

2. use tenable-sc to list all IPs in asset group "Windows Hosts", then show me cache stats and token usage for this request (repeat for cache hit)

3. use tenable-sc to list all IPs in asset group "Windows Hosts" with ACR > 8, then show me cache stats and token usage for this request

4. use tenable-sc to find which repository or asset group contains IP 10.1.20.10, then show me cache stats and token usage for this request

5. use tenable-sc to list all IPs in repository "Default" with details, then show me cache stats and token usage for this request

6. use tenable-sc to show me cache statistics and explain the hit rate improvement
```

**Expected Results:**
- All queries work correctly
- Cache hit rate improves with repeated queries (0% → 50% → 66%+)
- Token savings validated (~94% reduction)
- All use cases covered (basic listing, filtering, reverse lookup, detailed metadata)
- No errors or failures
