# Test Prompts for Tenable.sc MCP Server

Use these prompts to test the tools and verify functionality. **Always append cache performance and token utilization checks to your queries.**

---

## 📑 Table of Contents

### Completed Tools (Week 1)
- [Tool 1: IP Profile (tsc_profile_ip_efficient)](#tool-1-ip-profile-tsc_profile_ip_efficient)
- [Tool 2: Vulnerability Lists (tsc_list_vulns_by_ip)](#tool-2-vulnerability-lists-tsc_list_vulns_by_ip)
  - [Summary View (Efficient)](#summary-view-efficient)
  - [Full Details View](#full-details-view-tool-2---primary-test)
  - [Filtered Search with Exploits](#filtered-search-with-exploits)
- [Tool 4: IP Listing (tsc_list_ips)](#tool-4-ip-listing-tsc_list_ips)
  - [Test 1: List IPs by Repository Name](#test-1-list-ips-by-repository-name)
  - [Test 2: List IPs by Asset Group Name](#test-2-list-ips-by-asset-group-name)
  - [Test 3: Reverse Lookup](#test-3-reverse-lookup-find-ip-membership)
  - [Test 4: Filtered List with Details](#test-4-filtered-ip-list-with-full-details)
  - [Test 5: Cache HIT Behavior](#test-5-verify-cache-hit-behavior-repeat-test-1)
- [Tool 5: CVE Search (tsc_list_vulns_by_cve)](#tool-5-cve-search-tsc_list_vulns_by_cve)
  - [Test 1: Basic CVE Search](#test-1-basic-cve-search)
  - [Test 2: CVE with Advanced Filtering](#test-2-cve-with-advanced-filtering-critical-assets)
  - [Test 3: CVE with Full Plugin Output](#test-3-cve-with-full-plugin-output)
  - [Test 4: Non-Existent CVE](#test-4-non-existent-cve-error-handling)
  - [Test 5: Cache HIT Behavior](#test-5-verify-cache-hit-behavior-repeat-test-1-1)

### Testing & Performance
- [Cache Performance Testing](#cache-performance-testing)
- [Token Efficiency Demonstration](#token-efficiency-demonstration)
- [Complete Test Sequence](#complete-test-sequence-run-all)
- [Advanced Filtering Examples](#advanced-filtering-examples)
- [Cache Management](#cache-management)
- [Performance Benchmarking](#performance-benchmarking)
- [Error Handling Verification](#error-handling-verification)

### Reference
- [Visual Test Prompt Style Guide](#visual-test-prompt-style-guide)
- [Notes & Best Practices](#notes--best-practices)

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

## Tool 5: CVE Search (tsc_list_vulns_by_cve)

### Test 1: Basic CVE Search
```
I am testing tsc_list_vulns_by_cve to search for CVE-2021-44228 (Log4Shell) across the infrastructure. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Total affected assets: [count], Plugin ID: [id], Plugin Name: [name], First 3 affected IPs: [list]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked (MISS on first run, HIT on repeat)
- 🔢 Specific token count (target: 1,000-2,000 tokens)
- 📦 Total affected assets count
- Plugin ID and name for this CVE
- First 3 affected IPs with hostname, severity, port, protocol
- Remediation summary with steps, references, vendor advisories

**Token Efficiency:** ~1,000-2,000 tokens (vs ~10,000 raw API) = 85% reduction

---

### Test 2: CVE with Advanced Filtering (Critical Assets)
```
I am testing tsc_list_vulns_by_cve to find CVE-2017-0144 (EternalBlue) on critical assets with ACR > 7. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about filtering effectiveness]
📦 RESULT: Total critical assets with CVE: [count], Filters applied: asset_criticality="7-10", First 3 IPs with ACR scores: [list]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked
- 🔢 Specific token count
- 📦 Filtered results showing only assets with ACR 7-10
- Each affected IP showing ACR score
- Filters applied summary

**Use Case:** Answer "Do we have critical assets with this CVE?" for risk prioritization

---

### Test 3: CVE with Full Plugin Output
```
I am testing tsc_list_vulns_by_cve to get CVE-2021-26855 (ProxyLogon) with full plugin output. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about full output size]
📦 RESULT: Total assets: [count], Full output present: [Yes/No], Output size: [chars/lines]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked
- 🔢 Token count (higher due to full output)
- 📦 Full plugin output included (may be 500+ lines)
- plugin_output_available: true
- Complete remediation details from plugin text

**Use Case:** Detailed remediation planning requiring complete plugin context

---

### Test 4: Non-Existent CVE (Error Handling)
```
I am testing tsc_list_vulns_by_cve error handling with non-existent CVE-9999-99999. Please format your response as:

✅/❌ TEST STATUS: [PASS if gracefully handled, FAIL if error]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about error handling]
📦 RESULT: Expected message: "No assets found with CVE-9999-99999"

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** (graceful handling, not an error)
- 📊 Cache status
- 🔢 Minimal token count
- 📦 ok: true, total_affected_assets: 0
- User-friendly message explaining CVE not found

**Use Case:** Verify patch deployment - if CVE returns 0 assets after patching, remediation was successful

---

### Test 5: Verify Cache HIT Behavior (Repeat Test 1)
```
I am testing tsc_list_vulns_by_cve cache behavior by repeating Test 1 (CVE-2021-44228). Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [MUST BE HIT]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner comparing to first query]
📦 RESULT: Confirm total assets matches Test 1, Cache TTL: 240s (4 minutes)

If cache shows MISS instead of HIT, provide ERROR DETAILS. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with cache HIT
- 📊 Cache: HIT (within 240s window)
- 🔢 Same or similar token count
- 📦 Results match first query exactly
- Response time: <1s (vs 2-4s on MISS)

**Cache Behavior:** 240s (4 min) TTL balances freshness vs performance for emergency outbreak response

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


---

## Visual Test Prompt Style Guide

### Standard Format

All test prompts should use this visual format for consistency:

```
I am testing [tool_name] to [action]. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: [brief summary of returned data]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

### Benefits

- **Visual Icons** (✅/❌/📊/🔢/📝/📦) - Easy to scan for pass/fail at a glance
- **Structured Sections** - Consistent across all tests, machine-parseable
- **Cache Tracking** - Always report HIT/MISS for performance validation
- **Token Metrics** - Track token usage per query
- **Actionable Errors** - Clear debugging information without suggested fixes

### Example

```
I am testing tsc_list_ips to list all IPs in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Total IPs: [count], First 5: [list]
```

---

## Notes & Best Practices

### Cache Behavior
- First query of any unique dataset will be a **MISS**
- Repeated queries (within TTL window) will be a **HIT**
- Different filters create different cache keys (new MISS)
- Cache TTLs: 120-300s depending on tool

### Token Optimization
- Use summary tools first (`tsc_list_vulns_by_ip_summary`) before full details
- Apply filters to reduce payload size
- Pagination helps manage large datasets
- Cache hits use minimal tokens (~50-100 vs thousands on MISS)

### Testing Tips
- Run each query twice to verify cache HIT behavior
- Check `tsc_cache_stats` to monitor overall hit rate
- Test error handling with invalid inputs
- Validate filters work correctly with real data
- Compare token usage: first query (MISS) vs repeat (HIT)

---
