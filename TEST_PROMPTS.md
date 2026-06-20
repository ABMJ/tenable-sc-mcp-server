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

### CPE Filter Tests (v1.2.1)
- [CPE Filter Tests](#cpe-filter-tests)
  - [Test 1: Basic CPE - Windows 10](#test-1-basic-cpe---windows-10)
  - [Test 2: Basic CPE - Linux](#test-2-basic-cpe---linux)
  - [Test 3: Basic CPE - Cisco](#test-3-basic-cpe---cisco)
  - [Test 4: Regex CPE - Windows 10 OR 11](#test-4-regex-cpe---windows-10-or-11)
  - [Test 5: Regex CPE - Cisco IOS OR ASA](#test-5-regex-cpe---cisco-ios-or-asa)
  - [Test 6: Regex CPE - Windows Server 2016-2019](#test-6-regex-cpe---windows-server-2016-2019)
  - [Test 7: CPE Documentation Access](#test-7-cpe-documentation-access)

### 🧪 v1.3.0.1 Testing (THIS SESSION - REQUIRED)
- [v1.3.0.1 Session Testing](#-v1301-session-testing-required) - **9 Tests Total**
  - [Test 1: Multi-OS IP Listing](#test-1-multi-os-ip-listing-tsc_list_ips)
  - [Test 2: Multi-OS CVE Search](#test-2-multi-os-cve-search-tsc_list_vulns_by_cve)
  - [Test 3: OS Filter Validation Error](#test-3-os-filter-validation-error-per-ip-tool)
  - [Test 4: Per-IP Vulnerability Summary](#test-4-per-ip-vulnerability-summary-regression-test)
  - [Test 5: Per-IP Vulnerability Details](#test-5-per-ip-vulnerability-details-regression-test)
  - [Test 6: Plugin Family Discovery](#test-6-plugin-family-discovery-tsc_list_plugin_families)
  - [Test 7: Family Filter by Name](#test-7-plugin-family-filter-by-name-smart-lookup)
  - [Test 8: Family Filter by ID](#test-8-plugin-family-filter-by-id-direct)
  - [Test 9: Invalid Family Name](#test-9-invalid-plugin-family-name-error-handling)

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

---

## 🧪 v1.3.0.1 Session Testing (REQUIRED)

**What was fixed:**
- OS filter parameter alias (`os` now works alongside `os_name`, `operating_system`, `os_exact`)
- Multi-query execution for OS filtering (one query per OS variant, with deduplication)
- AttributeError fix in `get_operating_systems()` (now uses `server.tsc_analyze`)

**Container:** `tenable-sc-mcp:latest` (built from develop branch)

---

### Test 1: Multi-OS IP Listing

**Run this:**
```
use tenable-sc to list IPs with os "Windows 10" in repository Default
```

**Check for:**
- Returns ~36 Windows 10 IPs (not all 882 from repository)
- Response includes `by_os_variant` breakdown
- Response includes `deduplication_stats`

**Expected tokens:** ~700-1,500

---

### Test 2: Multi-OS CVE Search

**Run this:**
```
use tenable-sc to find all assets with CVE-2021-44228 and os "Windows 10"
```

**Check for:**
- Returns only Windows 10 IPs with Log4Shell
- Response includes `by_os_variant` breakdown
- Response includes `deduplication_stats`

**Expected tokens:** ~800-1,500

---

### Test 3: Per-IP Vulnerability Summary (Regression)

**Run this:**
```
use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical
```

**Check for:**
- Returns vulnerability counts by severity
- No errors (OS filter validation was removed in v1.3.0.2)

**Expected tokens:** ~700

---

### Test 4: Per-IP Vulnerability Details (Regression)

**Run this:**
```
use tenable-sc to list detailed vulnerabilities for IP 10.1.20.10 with severity critical, show first 10
```

**Check for:**
- Returns 10 detailed vulnerability records
- Pagination works correctly

**Expected tokens:** ~5,000 for 50 records

---

### Test 5: Plugin Family Discovery

**Run this:**
```
use tenable-sc to list all plugin families
```

**Check for:**
- Returns list of plugin families with IDs
- Cache hit on repeat calls (24-hour TTL)

**Expected tokens:** ~800-1,200

---

### Test 6: Plugin Family Filter by Name

**Run this:**
```
use tenable-sc to find vulnerabilities in plugin family "Windows" for CVE-2021-44228
```

**Check for:**
- Automatic lookup of family ID from name
- Results filtered to Windows family only

**Expected tokens:** Varies by results

---

### Test 7: Plugin Family Filter by ID

**Run this:**
```
use tenable-sc to list IPs with vulnerabilities in plugin family ID 20 in repository Default
```

**Check for:**
- Direct pass-through of family ID
- Filter applied correctly

**Expected tokens:** Varies by results

---

### Test 8: Invalid Plugin Family Name

**Run this:**
```
use tenable-sc to find vulnerabilities in plugin family "InvalidFamilyXYZ123"
```

**Check for:**
- Error message indicating family not found
- Suggestion to use tsc_list_plugin_families

**Expected tokens:** Minimal (error response)

---

## Test Results

| # | Test | Status | Notes |
|---|------|--------|-------|
| 1 | Multi-OS IP Listing | ✅ PASS | 36 IPs, ~719 tokens |
| 2 | Multi-OS CVE Search | ⬜ | |
| 3 | Per-IP Summary | ⬜ | |
| 4 | Per-IP Details | ⬜ | |
| 5 | Plugin Family Discovery | ⬜ | |
| 6 | Family Filter by Name | ⬜ | |
| 7 | Family Filter by ID | ⬜ | |
| 8 | Invalid Family Name | ⬜ | |

**Legend:** ✅ PASS | ❌ FAIL | ⚠️ PARTIAL | ⬜ NOT TESTED

---
