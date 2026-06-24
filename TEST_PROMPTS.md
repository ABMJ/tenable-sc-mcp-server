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
- [Tool 6: Missing Patches (tsc_list_missing_patches)](#tool-6-missing-patches-tsc_list_missing_patches)
  - [Test 1: Universal Patches (Single IP)](#test-1-universal-patches-single-ip)
  - [Test 2: Universal Patches with Repository Filter](#test-2-universal-patches-with-repository-filter)
  - [Test 3: Universal Patches (High-Criticality Assets)](#test-3-universal-patches-high-criticality-assets-only)
  - [Test 4: Windows KB Mode (Single IP)](#test-4-windows-kb-mode-single-ip)
  - [Test 5: Windows KB with Repository Filter](#test-5-windows-kb-with-repository-filter)
  - [Test 6: Cache HIT Behavior](#test-6-verify-cache-hit-behavior-repeat-test-1)

### CPE Filter Tests (v1.2.1)
- [CPE Filter Tests](#cpe-filter-tests)
  - [Test 1: Basic CPE - Windows 10](#test-1-basic-cpe---windows-10)
  - [Test 2: Basic CPE - Linux](#test-2-basic-cpe---linux)
  - [Test 3: Basic CPE - Cisco](#test-3-basic-cpe---cisco)
  - [Test 4: Regex CPE - Windows 10 OR 11](#test-4-regex-cpe---windows-10-or-11)
  - [Test 5: Regex CPE - Cisco IOS OR ASA](#test-5-regex-cpe---cisco-ios-or-asa)
  - [Test 6: Regex CPE - Windows Server 2016-2019](#test-6-regex-cpe---windows-server-2016-2019)
  - [Test 7: CPE Documentation Access](#test-7-cpe-documentation-access)

### Operating System & Plugin Family Tests (v1.3.0)
- [Operating System Filter Tests](#operating-system-filter-tests-v130)
  - [Test 1: Discover Available Operating Systems](#test-1-discover-available-operating-systems)
  - [Test 2: Exact Windows 10 Match](#test-2-exact-windows-10-match-zero-false-positives)
  - [Test 3: Exact Server 2019 Match](#test-3-exact-server-2019-match-no-windows-10)
  - [Test 4: Smart OS Lookup (Partial Match)](#test-4-smart-os-lookup-partial-match)
  - [Test 5: Exact Linux Match](#test-5-exact-linux-match)
  - [Test 6: Compare CPE vs Operating System](#test-6-compare-cpe-vs-operating-system-false-positive-check)
- [Plugin Family Filter Tests](#plugin-family-filter-tests-v130)
  - [Test 1: Discover Plugin Families](#test-1-discover-plugin-families)
  - [Test 2: Family Filter by Name](#test-2-family-filter-by-name-smart-lookup)
  - [Test 3: Family Filter by ID](#test-3-family-filter-by-id-direct-pass-through)
  - [Test 4: Multiple Families (Mixed)](#test-4-multiple-families-mixed-name-and-id)
  - [Test 5: Invalid Family Name](#test-5-invalid-family-name-error-handling)
  - [Test 6: Search Plugin Families](#test-6-search-plugin-families-discovery-helper)
- [New Tools (v1.3.0)](#quick-reference-new-tools-v130)

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
📦 RESULT: Total unique IPs: [count], First 3 affected IPs with severity counts: [list with critical/high/medium/low/info counts]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked (MISS on first run, HIT on repeat)
- 🔢 Specific token count (target: 800-1,500 tokens)
- 📦 Total unique IPs count (no duplicate records)
- First 3 affected IPs with hostname, severity counts (critical/high/medium/low/info), ACR/AES scores
- Note about using tsc_list_vulns_by_ip_full for detailed remediation

**Token Efficiency:** ~800-1,500 tokens (vs ~10,000 raw API) = 85% reduction

---

### Test 2: CVE with Advanced Filtering (Critical Assets)
```
I am testing tsc_list_vulns_by_cve to find CVE-2017-0144 (EternalBlue) on critical assets with ACR > 7. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about filtering effectiveness]
📦 RESULT: Total critical IPs with CVE: [count], Filters applied: asset_criticality="7-10", First 3 IPs with ACR scores and severity counts: [list]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked
- 🔢 Specific token count
- 📦 Filtered results showing only IPs with ACR 7-10
- Each affected IP showing ACR score and severity counts
- Filters applied summary

**Use Case:** Answer "Do we have critical assets with this CVE?" for risk prioritization

---

### Test 3: CVE Pagination (Large Result Sets)
```
I am testing tsc_list_vulns_by_cve pagination with a CVE that affects many IPs. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about pagination]
📦 RESULT: Total IPs: [count], Returned IPs: [count], Start offset: 0, End offset: 200, More available: [Yes/No]

If failed, provide ERROR DETAILS with enough information for the developer to fix. Do not suggest code or fixes.
```

**Expected Output:**
- ✅ **PASS** with visual confirmation
- 📊 Cache status clearly marked
- 🔢 Token count for first page
- 📦 Pagination metadata showing total_ips, returned_ips, more_available flag
- If more_available is true, instructions on how to fetch next page

**Use Case:** Handle large CVE outbreaks affecting hundreds of assets

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
- 📦 ok: true, summary.total_ips: 0, affected_ips: []
- User-friendly message explaining CVE not found

**Use Case:** Verify patch deployment - if CVE returns 0 IPs after patching, remediation was successful

---

### Test 5: Verify Cache HIT Behavior (Repeat Test 1)
```
I am testing tsc_list_vulns_by_cve cache behavior by repeating Test 1 (CVE-2021-44228). Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [MUST BE HIT]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner comparing to first query]
📦 RESULT: Confirm total IPs matches Test 1, Cache TTL: 240s (4 minutes)

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

## Tool 6: Missing Patches (tsc_list_missing_patches)

**Purpose:** Universal patch gap analysis across all operating systems with Microsoft KB tracking and third-party software updates.

**Modes:**
- **universal** (plugin 66334): All OS types + third-party software (Chrome, Office, VMware, etc.)
- **windows** (plugin 38153): Windows KB articles and legacy MS bulletins

**Use Cases:**
- Compliance reporting (PCI, NIST, CIS)
- Remediation planning grouped by IP or patch
- Microsoft KB tracking with superseded relationships
- Third-party software update monitoring

---

### Test 1: Universal Patches (Single IP)
```
I am testing tsc_list_missing_patches in universal mode for IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: IP: [ip], Hostname: [hostname], OS: [os], Total patches: [count] ([X] Microsoft KBs, [Y] third-party)
```

**Expected Output:**
- Single IP patch status
- Microsoft KB article numbers with vulnerability counts
- Third-party software updates (Google Chrome, VMware Tools, Office, etc.)
- Hostname, OS, and repository information
- Total patch count breakdown
- Cache performance and token metrics

**Token Efficiency:** ~500-1,500 tokens for single IP (vs 3,000-5,000 for wide-open query)

**Note:** Use `filters={"ip": "10.1.20.10"}` to scope to a single IP. Querying all 1000+ IPs without filters is inefficient.

---

### Test 2: Universal Patches with Repository Filter
```
I am testing tsc_list_missing_patches in universal mode filtered by repository "Default" for IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Repository: [name], Affected IPs: [count], Total patches for 10.1.20.10: [count] ([X] Microsoft KBs, [Y] third-party)
```

**Expected Output:**
- Only IPs from specified repository
- Patch data for single IP
- Repository name confirmed in results
- Single IP scope for token efficiency

**Note:** Use `filters={"ip": "10.1.20.10", "repository": "Default"}` to scope to Default repository

---

### Test 3: Universal Patches (High-Criticality Assets Only)
```
I am testing tsc_list_missing_patches in universal mode with asset_criticality filter "8-10" for IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: IP: [ip], ACR Score: [score], Total patches: [count] ([X] Microsoft KBs, [Y] third-party)
```

**Expected Output:**
- Only high-criticality assets (ACR 8-10)
- Patch data for critical system
- Filter confirmation in response
- Useful for prioritizing remediation efforts

**Filter Format:** Must use range format `"8-10"` (NOT `">8"`)

**Note:** Use `filters={"ip": "10.1.20.10", "asset_criticality": "8-10"}` for single critical asset

---

### Test 4: Windows KB Mode (Single IP)
```
I am testing tsc_list_missing_patches in windows mode for IP 10.1.20.10 to get Windows KB articles. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: IP: [ip], Hostname: [hostname], OS: [os], Missing KBs: [count], Sample KBs: [list 2-3 KB IDs]
```

**Expected Output:**
- Windows-specific KB article numbers
- Support.microsoft.com URLs for each KB
- Legacy MS bulletin IDs (MS16-087, MS17-010, etc.) if present
- Hostname and OS information
- Total missing KB count

**Token Efficiency:** ~500-1,000 tokens for single IP

**Note:** Use `filters={"ip": "10.1.20.10"}` to scope to a single Windows IP.

---

### Test 5: Windows KB with Repository Filter
```
I am testing tsc_list_missing_patches in windows mode filtered by repository "Default" for IP 10.1.20.10 to focus on Windows patches. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: IP: [ip], Repository: [name], Missing KBs: [count], Most critical KB: [KB ID with highest vuln count]
```

**Expected Output:**
- Only Windows systems in specified repository
- KB article tracking for Default repository
- Repository scoping confirmed
- Useful for compliance audits and remediation planning

**Note:** Use `filters={"ip": "10.1.20.10", "repository": "Default"}` to scope to Default repository

---

### Test 6: Verify Cache HIT Behavior (Repeat Test 1)
```
I am repeating Test 1 (universal patches for IP 10.1.20.10) to verify cache HIT. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [expected HIT]
🔢 TOKENS: [count] tokens used (should be ~50-200 vs ~500-1,500 on MISS)
📝 SUMMARY: Cache HIT reduced token usage by [X]%
📦 RESULT: Data matches Test 1 results exactly
```

**Expected Behavior:**
- Cache HIT (240s TTL)
- Token usage 85-95% lower than Test 1
- Identical results to Test 1
- Response time < 1s

**Cache TTL:** 240 seconds (4 minutes) for patch data

---

### Summary for Tool 6

**Key Features:**
- Universal patch tracking (all OS types)
- Windows-specific KB article mode
- Third-party software update tracking
- Microsoft KB with vulnerability counts
- Legacy MS bulletin support
- Repository and asset criticality filtering
- 240s cache TTL for patch data

**Token Efficiency:**
- Single IP query: ~500-1,500 tokens (recommended for testing)
- Repository-scoped: ~2,000-5,000 tokens (moderate result sets)
- Wide-open query: ~5,000-20,000+ tokens (NOT recommended for large environments)
- Cache HIT: ~50-200 tokens (90-95% reduction)

**Best Practices:**
- **Always use IP or repository filters** for large environments (1000+ assets)
- Use `filters={"ip": "x.x.x.x"}` for single-host queries
- Use `universal` mode for comprehensive patch coverage
- Use `windows` mode for Windows-specific KB tracking
- Apply `repository` filter to scope by network segment
- Use `asset_criticality` filter to prioritize critical assets
- Use range format for scoring filters: `"8-10"` NOT `">8"`
- Run queries twice to verify cache performance

**Common Use Cases:**
1. Single-host audit: Get patch status for specific IP with `ip` filter
2. Compliance reporting: List patches for repository with `repository` filter
3. Remediation planning: Identify critical systems with `asset_criticality` filter
4. KB tracking: Monitor Windows update deployment status with `windows` mode
5. Third-party updates: Track Chrome, Office, VMware Tool versions with `universal` mode

**Performance Warning:**
- Querying all patches without filters in environments with 1000+ IPs can consume 10,000-20,000+ tokens
- Always scope queries with `ip`, `repository`, or `asset_criticality` filters

---

## CPE Filter Tests

**Feature Added:** v1.2.1  
**Purpose:** Validate OS/Platform filtering with smart operator auto-detection  
**Operators:** `~=` (contains), `=` (exact), `pcre` (regex)

---

### Test 1: Basic CPE - Windows 10
```
I am testing tsc_list_ips with CPE filter to find Windows 10 systems. Please format your response as:

use tenable-sc to list IPs in repository Default with cpe filter "microsoft:windows_10" and severity critical, show first 10 results

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about CPE operator detection and results]
📦 RESULT: Total IPs: [count], Operator Used: [~=/=/pcre], First 5 IPs: [list]
```

**Expected Result:**
- ✅ Uses `~=` operator (auto-detected)
- ✅ Returns Windows 10 IPs with critical vulns
- ✅ No API errors
- ⚠️ May include Server 2016/2019 (share Windows 10 codebase)

---

### Test 2: Basic CPE - Linux
```
I am testing tsc_list_ips with CPE filter to find Linux systems with high risk scores. Please format your response as:

use tenable-sc to list IPs with cpe "linux" where VPR score is 8-10 and ACR is 7-10 in repository Default

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about results and filter combination]
📦 RESULT: Total IPs: [count], Operator Used: [~=/=/pcre], Distros Found: [list]
```

**Expected Result:**
- ✅ Uses `~=` operator
- ✅ Returns all Linux distros (CentOS, Ubuntu, Oracle)
- ✅ All have VPR ≥ 8 and ACR ≥ 7
- ℹ️ May return zero results if dataset lacks high-risk Linux systems

---

### Test 3: Basic CPE - Cisco
```
I am testing tsc_list_ips with CPE filter to find Cisco devices with exploitable critical vulnerabilities. Please format your response as:

use tenable-sc to list IPs with cpe "cisco" where exploit_available is true and severity is critical in repository Default

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about Cisco devices and exploit status]
📦 RESULT: Total IPs: [count], Operator Used: [~=/=/pcre], Device Types: [IOS/ASA/NX-OS list]
```

**Expected Result:**
- ✅ Uses `~=` operator
- ✅ Returns all Cisco devices with exploitable critical vulns
- ✅ Boolean filter `exploit_available` works correctly

---

### Test 4: Regex CPE - Windows 10 OR 11
```
I am testing tsc_list_ips with regex CPE pattern for Windows 10 or 11. Please format your response as:

use tenable-sc to list IPs with cpe ".*windows.*(10|11).*" in repository Default, show first 10 results

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about regex detection and any false positives]
📦 RESULT: Total IPs: [count], Operator Used: [pcre], Win10: [count], Win11: [count], False Positives: [if any]
```

**Expected Result:**
- ✅ Uses `pcre` operator (auto-detected from regex)
- ✅ Returns Windows 10 and Windows 11
- ⚠️ **Known Issue:** May include Server 2016/2019 (version "10.0.17763")
- ℹ️ False positives expected - pattern too broad (documented)

**Note:** For exact matching, use `os_type` filter in v1.2.2+

---

### Test 5: Regex CPE - Cisco IOS OR ASA
```
I am testing tsc_list_ips with regex CPE pattern to find Cisco IOS or ASA devices only. Please format your response as:

use tenable-sc to list IPs with cpe ".*cisco.*(ios|asa).*" where severity is critical in repository Default

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about selective Cisco matching]
📦 RESULT: Total IPs: [count], Operator Used: [pcre], IOS: [count], ASA: [count], NX-OS Excluded: [yes/no]
```

**Expected Result:**
- ✅ Uses `pcre` operator
- ✅ Returns ONLY Cisco IOS and ASA devices
- ✅ Correctly excludes Nexus (NX-OS) devices
- ✅ Severity filter applied

---

### Test 6: Regex CPE - Windows Server 2016-2019
```
I am testing tsc_list_ips with regex CPE pattern for Windows Server year range. Please format your response as:

use tenable-sc to list IPs with cpe ".*windows_server_201[6-9].*" where ACR is 8-10 in repository Default

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about year range matching and exclusions]
📦 RESULT: Total IPs: [count], Operator Used: [pcre], 2016: [c], 2017: [c], 2018: [c], 2019: [c]
```

**Expected Result:**
- ✅ Uses `pcre` operator (auto-detected)
- ✅ Returns Server 2016, 2017, 2018, 2019 only
- ✅ Correctly excludes Server 2012 and 2022
- ⚠️ **Known Issue:** May include Windows 10 systems (substring "10" matches)
- ℹ️ May return zero results if no high-ACR Server systems in dataset

**Note:** For improved pattern, use `.*:windows_server_201[6-9]:.*` (colon boundaries)

---

### Test 7: CPE Documentation Access
```
I am testing MCP resource access for CPE filter documentation. Please format your response as:

fetch the MCP resource tenable-sc://filters/format-reference and show me the CPE filtering section with the three operators and auto-detection details

✅/❌ TEST STATUS: [PASS/FAIL]
📦 RESULT: [Summary of what CPE documentation was found]
```

**Expected Result:**
- ✅ Shows v1.2.1 docs
- ✅ Explains three operators: `~=`, `=`, `pcre`
- ✅ Shows auto-detection rules with examples
- ✅ Includes regex reference table
- ℹ️ May reference `tenable-sc://filters/reference` for compact version

**Alternative:** Try `tenable-sc://filters/reference` if format-reference not found

---

## Operating System Filter Tests (v1.3.0)

**Feature Added:** v1.3.0  
**Purpose:** Validate exact OS matching with zero false positives (solves CPE regex issues)  
**API Field:** `operatingSystem`  
**Operator:** `=` (exact match)  
**Discovery Tool:** `tsc_list_operating_systems`

---

### Test 1: Discover Available Operating Systems

```
I am testing tsc_list_operating_systems to discover all OS names in the environment. Please format your response as:

use tenable-sc to list all operating systems, limit to 20 results

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about OS discovery]
📦 RESULT: Total OS: [count], First 5 OS names with counts: [list]
```

**Expected Result:**
- ✅ Returns list of exact OS names with asset counts
- ✅ Sorted by count (descending) by default
- ✅ Token budget: ~1,500-2,000 tokens
- ✅ Cache TTL: 300s (5 min)
- ℹ️ Use these exact names in operating_system filter

**Link:** [Tool 6a: tsc_list_operating_systems](#tool-6a-tsc_list_operating_systems)

---

### Test 2: Exact Windows 10 Match (Zero False Positives)

```
I am testing tsc_list_ips with exact operating_system filter for Windows 10. Please format your response as:

use tenable-sc to list IPs in repository Default with operating_system "Microsoft Windows 10 Pro Build 19045"

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about exact match accuracy]
📦 RESULT: Total IPs: [count], All are Build 19045: [Yes/No], No Server editions: [Confirmed/Failed]
```

**Expected Result:**
- ✅ Returns ONLY Windows 10 Pro Build 19045
- ✅ Excludes all Windows Server editions (2016, 2019, 2022)
- ✅ Excludes other Windows 10 builds (18363, 19044, etc.)
- ✅ Zero false positives confirmed
- ⚠️ May return 0 results if exact build not in dataset

**Link:** [Tool 4: tsc_list_ips](#tool-4-ip-listing-tsc_list_ips)

---

### Test 3: Exact Server 2019 Match (No Windows 10)

```
I am testing tsc_list_ips with exact operating_system filter for Server 2019. Please format your response as:

use tenable-sc to list IPs with operating_system "Microsoft Windows Server 2019 Standard Build 17763" where severity is critical

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about exclusion of Windows 10]
📦 RESULT: Total IPs: [count], All are Server 2019: [Yes/No], No Win10 mixed in: [Confirmed/Failed]
```

**Expected Result:**
- ✅ Returns ONLY Server 2019 Standard Build 17763
- ✅ Excludes all Windows 10 editions
- ✅ Combined with severity filter works correctly
- ✅ Confirms v1.2.1 false positive issue resolved

**Link:** [Tool 4: tsc_list_ips](#tool-4-ip-listing-tsc_list_ips)

---

### Test 4: Smart OS Lookup (Partial Match)

```
I am testing smart OS lookup with partial name "Windows 10". Please format your response as:

use tenable-sc to list IPs with os_name "Windows 10" in repository Default, show first 10

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about smart matching]
📦 RESULT: OS variants matched: [list], Total IPs: [count], No false positives: [Confirmed/Failed]
```

**Expected Result:**
- ✅ Tool queries listos to find all "Windows 10" OS names
- ✅ Matches: "Windows 10 Pro Build 19045", "Windows 10 Enterprise", etc.
- ✅ Excludes: "Windows Server 2019", "Windows 11", etc.
- ✅ Aggregates IPs across all matched OS variants
- ✅ Zero false positives (no Server editions)

**Link:** [Tool 4: tsc_list_ips](#tool-4-ip-listing-tsc_list_ips)

---

### Test 5: Exact Linux Match

```
I am testing exact operating_system filter with Oracle Linux. Please format your response as:

use tenable-sc to list IPs with os_exact "Oracle Linux Server 8.9" where ACR is 7-10

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about Linux precision]
📦 RESULT: Total IPs: [count], All Oracle 8.9: [Yes/No], No other versions: [Confirmed/Failed]
```

**Expected Result:**
- ✅ Returns ONLY Oracle Linux Server 8.9
- ✅ Excludes Oracle 8.4, 8.7, 9.0, etc.
- ✅ Combined with ACR filter works correctly
- ⚠️ May return 0 results if specific version not in dataset

**Link:** [Tool 4: tsc_list_ips](#tool-4-ip-listing-tsc_list_ips)

---

### Test 6: Compare CPE vs Operating System (False Positive Check)

```
I am testing to compare CPE regex false positives with exact operating_system matching. Please format your response as:

First query: use tenable-sc to list IPs with cpe ".*windows.*(10|11).*" in Default
Second query: use tenable-sc to list IPs with os_name "Windows 10" in Default

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS for both queries]
🔢 TOKENS: CPE: [count], OS: [count]
📝 SUMMARY: [comparison of false positives between methods]
📦 RESULT: CPE Total: [count] (includes Server: [Y/N]), OS Total: [count] (Server excluded: [Y/N])
```

**Expected Result:**
- ⚠️ CPE query includes Server 2016/2019 (false positives)
- ✅ operating_system query excludes all Server editions (zero false positives)
- ✅ Demonstrates v1.3.0 improvement over v1.2.1
- ℹ️ Confirms exact matching superiority

**Links:**
- [CPE Test 4](#test-4-regex-cpe---windows-10-or-11)
- [OS Test 4](#test-4-smart-os-lookup-partial-match)

---

## Plugin Family Filter Tests (v1.3.0)

**Feature Fixed:** v1.3.0  
**Breaking Change:** Now uses numeric IDs (v1.2.1 was broken)  
**API Field:** `family`  
**Format:** Array of ID objects: `[{"id": "20"}]`  
**Discovery Tool:** `tsc_list_plugin_families`

---

### Test 1: Discover Plugin Families

```
I am testing tsc_list_plugin_families to discover all available plugin families. Please format your response as:

use tenable-sc to list all plugin families

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about family discovery]
📦 RESULT: Total families: [count], First 10 families with IDs: [list]
```

**Expected Result:**
- ✅ Returns all plugin families (150+ total)
- ✅ Shows both ID and name for each family
- ✅ Token budget: ~800-1,200 tokens
- ✅ Cache TTL: 600s (10 min - static data)
- ℹ️ Use these IDs OR names in family filter

**Link:** [Tool 6b: tsc_list_plugin_families](#tool-6b-tsc_list_plugin_families)

---

### Test 2: Family Filter by Name (Smart Lookup)

```
I am testing family filter with smart name lookup. Please format your response as:

use tenable-sc to list vulnerabilities for IP 10.1.20.10 with family "Windows", show first 10

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about name→ID conversion]
📦 RESULT: Family ID used: [20], Total vulns: [count], All Windows family: [Yes/No]
```

**Expected Result:**
- ✅ Tool converts "Windows" → ID "20"
- ✅ API receives: `[{"id": "20"}]`
- ✅ Returns only Windows plugin family vulnerabilities
- ✅ Family cache used (600s TTL)
- ℹ️ Smart lookup working as designed

**Link:** [Tool 2b: tsc_list_vulns_by_ip_full](#full-details-view-tool-2---primary-test)

---

### Test 3: Family Filter by ID (Direct Pass-Through)

```
I am testing family filter with direct ID (no lookup). Please format your response as:

use tenable-sc to list vulnerabilities for IP 10.1.20.10 with family "30", show first 10

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about ID pass-through]
📦 RESULT: Family ID used: [30], Total vulns: [count], All General family: [Yes/No]
```

**Expected Result:**
- ✅ Tool recognizes numeric ID, uses directly
- ✅ API receives: `[{"id": "30"}]`
- ✅ No cache lookup needed (already ID)
- ✅ Returns only General plugin family vulnerabilities

**Link:** [Tool 2b: tsc_list_vulns_by_ip_full](#full-details-view-tool-2---primary-test)

---

### Test 4: Multiple Families (Mixed Name and ID)

```
I am testing family filter with multiple families (mixed name and ID). Please format your response as:

use tenable-sc to list vulnerabilities for IP 10.1.20.10 with family ["Windows", "30", "SCADA"], show first 20

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about mixed conversion]
📦 RESULT: Family IDs used: [20, 30, 36], Total vulns: [count], Breakdown by family: [counts]
```

**Expected Result:**
- ✅ Converts "Windows" → 20, "30" → 30, "SCADA" → 36
- ✅ API receives: `[{"id": "20"}, {"id": "30"}, {"id": "36"}]`
- ✅ Returns vulnerabilities from all three families
- ✅ Demonstrates smart mixed-mode handling

**Link:** [Tool 2b: tsc_list_vulns_by_ip_full](#full-details-view-tool-2---primary-test)

---

### Test 5: Invalid Family Name (Error Handling)

```
I am testing family filter error handling with invalid name. Please format your response as:

use tenable-sc to list vulnerabilities for IP 10.1.20.10 with family "NonexistentFamily"

✅/❌ TEST STATUS: [PASS if gracefully handled, FAIL if error]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about error handling]
📦 RESULT: Warning logged: [Yes/No], Query proceeded without family filter: [Yes/No]
```

**Expected Result:**
- ✅ Tool logs WARNING about unknown family name
- ✅ Filter is skipped (not applied)
- ✅ Query proceeds with other filters
- ✅ Returns all vulnerabilities (family filter omitted)
- ℹ️ Graceful degradation, not hard error

**Link:** [Tool 2b: tsc_list_vulns_by_ip_full](#full-details-view-tool-2---primary-test)

---

### Test 6: Search Plugin Families (Discovery Helper)

```
I am testing plugin family search functionality. Please format your response as:

use tenable-sc to list plugin families with search term "Windows"

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about search results]
📦 RESULT: Families matching "Windows": [list with IDs]
```

**Expected Result:**
- ✅ Returns filtered list of families matching "Windows"
- ✅ Expected: Windows (20), Windows : Microsoft Bulletins (10), Windows : User management (29)
- ✅ Case-insensitive partial match working
- ℹ️ Helpful for discovering exact family names before filtering

**Link:** [Tool 6b: tsc_list_plugin_families](#tool-6b-tsc_list_plugin_families)

---

## Quick Reference: New Tools (v1.3.0)

### Tool 6a: tsc_list_operating_systems

**Purpose:** Discover available OS names for exact matching

**Usage:**
```
use tenable-sc to list all operating systems, limit 20
use tenable-sc to list operating systems sorted by name
```

**Returns:** OS names with counts, pagination support

**Token Budget:** ~1,500-2,000 tokens  
**Cache TTL:** 300s (5 min)  
**Module:** `tools/asset_discovery.py`

---

### Tool 6b: tsc_list_plugin_families

**Purpose:** Discover plugin family IDs and names

**Usage:**
```
use tenable-sc to list all plugin families
use tenable-sc to list plugin families with search "Windows"
```

**Returns:** Family IDs with names

**Token Budget:** ~800-1,200 tokens  
**Cache TTL:** 600s (10 min)  
**Module:** `tools/admin/plugins.py`

---
