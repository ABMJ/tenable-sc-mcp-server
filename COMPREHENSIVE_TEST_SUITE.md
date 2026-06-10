# Comprehensive Test Suite - Tenable.sc MCP Server v1.2.0

**Instructions for Claude Code:**
1. Execute each test prompt below ONCE (first run will be cache miss)
2. After ALL tests complete, generate TWO files:
   - `test_results.md` - Full markdown dump with all prompts and responses (easy to parse)
   - `test_results.html` - Collapsible HTML for visual review
3. The HTML must have:
   - One collapsible section per test
   - Click header to expand/collapse
   - Show the prompt and response when expanded
   - No extra buttons or functions needed - just click to toggle

---

# TOOL 1 TESTS (5 tests)

## Test 1.1: Basic IP Profile
```
I am testing tsc_profile_ip_efficient to profile IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Hostname: [name], OS: [os], Vulnerabilities: C:[count] H:[count] M:[count] L:[count] I:[count]
```

## Test 1.2: Different IP Profile
```
I am testing tsc_profile_ip_efficient to profile IP 10.1.0.101. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Hostname: [name], OS: [os], Vulnerabilities: C:[count] H:[count] M:[count] L:[count] I:[count]
```

## Test 1.3: Private IP Range
```
I am testing tsc_profile_ip_efficient to profile IP 192.168.5.20. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Hostname: [name], OS: [os], Vulnerabilities: C:[count] H:[count] M:[count] L:[count] I:[count]
```

## Test 1.4: Invalid IP (Error Handling)
```
I am testing tsc_profile_ip_efficient to profile IP 999.999.999.999. Please format your response as:

✅/❌ TEST STATUS: [Should FAIL with validation error]
📊 CACHE: N/A
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [validation error message]
📦 RESULT: Error: [error message]
```

## Test 1.5: High-Risk Asset
```
I am testing tsc_profile_ip_efficient to profile IP 10.1.0.5. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Hostname: [name], OS: [os], ACR: [score], Vulnerabilities: C:[count] H:[count] M:[count] L:[count] I:[count]
```

---

# TOOL 2A TESTS (10 tests)

## Test 2a.1: Basic Vulnerability Summary
```
I am testing tsc_list_vulns_by_ip_summary to get vulnerability summary for IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Total: [count], Critical: [count], High: [count], Medium: [count], Low: [count], Info: [count]
```

## Test 2a.2: Filter by Critical Severity
```
I am testing tsc_list_vulns_by_ip_summary to get critical vulnerability summary for IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about filter effectiveness]
📦 RESULT: Total: [count], Critical: [count], High: [count], Medium: [count], Low: [count], Info: [count]
```

## Test 2a.3: Filter by Exploit Available
```
I am testing tsc_list_vulns_by_ip_summary to find vulnerabilities with exploits available on IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about exploit filtering]
📦 RESULT: Total exploitable: [count], By severity: C:[x] H:[x] M:[x] L:[x] I:[x]
```

## Test 2a.4: Multiple Filters (Critical + Exploitable)
```
I am testing tsc_list_vulns_by_ip_summary to find critical vulnerabilities with exploits available on IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about multi-filter effectiveness]
📦 RESULT: Total: [count], Critical: [count], High: [count], Medium: [count], Low: [count], Info: [count]
```

## Test 2a.5: Filter by VPR Score
```
I am testing tsc_list_vulns_by_ip_summary to find high-priority vulnerabilities with VPR 8-10 on IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about VPR filtering]
📦 RESULT: Total high-priority: [count], By severity: C:[x] H:[x] M:[x] L:[x] I:[x]
```

## Test 2a.6: Advanced Multi-Filter (VPR + Critical + Exploit)
```
I am testing tsc_list_vulns_by_ip_summary to find critical vulnerabilities with VPR 8-10 and exploits available on IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about advanced filtering]
📦 RESULT: Total: [count], Critical: [count], High: [count], Medium: [count], Low: [count], Info: [count]
```

## Test 2a.7: Filter by AES Score
```
I am testing tsc_list_vulns_by_ip_summary to find vulnerabilities on assets with AES 600-1000 for IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about AES filtering]
📦 RESULT: Total: [count], By severity: C:[x] H:[x] M:[x] L:[x] I:[x]
```

## Test 2a.8: Complex Filter (CVSS + Exploit + Port 443)
```
I am testing tsc_list_vulns_by_ip_summary to find vulnerabilities with CVSS v3 7-10, exploits available, on port 443 for IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about complex filtering]
📦 RESULT: Total: [count], By severity: C:[x] H:[x] M:[x] L:[x] I:[x]
```

## Test 2a.9: Filter by Plugin Family (Windows)
```
I am testing tsc_list_vulns_by_ip_summary to find Windows vulnerabilities on IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about family filtering]
📦 RESULT: Total Windows vulns: [count], By severity: C:[x] H:[x] M:[x] L:[x] I:[x]
```

## Test 2a.10: Ultra-Complex Filter (Windows + VPR + CVSS + Exploit)
```
I am testing tsc_list_vulns_by_ip_summary to find Windows vulnerabilities with VPR 8-10, CVSS v3 7-10, and exploits available on IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about ultra-complex filtering]
📦 RESULT: Total: [count], By severity: C:[x] H:[x] M:[x] L:[x] I:[x]
```

---

# TOOL 2B TESTS (12 tests)

## Test 2b.1: Basic Vulnerability Details
```
I am testing tsc_list_vulns_by_ip_full to list vulnerabilities for IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Returned [x] of [total] records, First 3 plugins: [list plugin IDs]
```

## Test 2b.2: Filter by Critical Severity
```
I am testing tsc_list_vulns_by_ip_full to list critical vulnerabilities for IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about filtering]
📦 RESULT: Returned [x] critical vulns, First 3 plugins: [list]
```

## Test 2b.3: Filter by Exploit Available
```
I am testing tsc_list_vulns_by_ip_full to find vulnerabilities with exploits available on IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about exploit filtering]
📦 RESULT: Returned [x] exploitable vulns, First 3 plugins: [list]
```

## Test 2b.4: Multiple Filters (Critical + Exploit + Port 443)
```
I am testing tsc_list_vulns_by_ip_full to find critical vulnerabilities with exploits on port 443 for IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about multi-filter]
📦 RESULT: Returned [x] matching vulns, Plugins: [list]
```

## Test 2b.5: Filter by CVSS v3 Score
```
I am testing tsc_list_vulns_by_ip_full to find vulnerabilities with CVSS v3 7-10 on IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about CVSS filtering]
📦 RESULT: Returned [x] high-CVSS vulns, Average CVSS: [avg], Plugins: [list]
```

## Test 2b.6: Filter by VPR Score
```
I am testing tsc_list_vulns_by_ip_full to find vulnerabilities with VPR 8-10 on IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about VPR filtering]
📦 RESULT: Returned [x] high-priority vulns, Plugins: [list]
```

## Test 2b.7: Pagination Test
```
I am testing tsc_list_vulns_by_ip_full to list vulnerabilities for IP 10.1.20.10, show records 10-20. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about pagination]
📦 RESULT: Returned records 10-20, Plugins: [list]
```

## Test 2b.8: Advanced Filter (VPR + CVSS + Exploit)
```
I am testing tsc_list_vulns_by_ip_full to find vulnerabilities with VPR 7-10, CVSS v3 7-10, and exploits available on IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about advanced scoring]
📦 RESULT: Returned [x] high-risk vulns, Plugins: [list]
```

## Test 2b.9: Filter by Plugin Family (Windows)
```
I am testing tsc_list_vulns_by_ip_full to find Windows vulnerabilities on IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about family filtering]
📦 RESULT: Returned [x] Windows vulns, Plugins: [list]
```

## Test 2b.10: Complex Filter (Windows + VPR + CVSS + Exploit)
```
I am testing tsc_list_vulns_by_ip_full to find Windows vulnerabilities with VPR 8-10, CVSS v3 7-10, and exploits available on IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about complex targeting]
📦 RESULT: Returned [x] high-risk Windows vulns, Plugins: [list]
```

## Test 2b.11: Filter by Protocol (TCP)
```
I am testing tsc_list_vulns_by_ip_full to find TCP vulnerabilities on IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about protocol filtering]
📦 RESULT: Returned [x] TCP vulns, Plugins: [list]
```

## Test 2b.12: Ultra-Complex Filter (Windows + VPR + CVSS + Exploit + TCP + Low Complexity)
```
I am testing tsc_list_vulns_by_ip_full to find Windows vulnerabilities that have VPR > 8, CVSS v3 > 7, are exploitable, can be exploited via network (TCP protocol), and have low exploit complexity on IP 10.1.20.10, show first 10 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about enterprise-grade filtering]
📦 RESULT: Returned [x] critically exposed Windows vulns, Plugins: [list]
```

---

# TOOL 4 TESTS (18 tests)

## Test 4.1: List All IPs in Repository
```
I am testing tsc_list_ips to list all IPs in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about performance]
📦 RESULT: Total IPs: [count], First 5: [list]
```

## Test 4.2: List IPs in Asset Group
```
I am testing tsc_list_ips to list all IPs in asset group "Windows Hosts". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about asset group query]
📦 RESULT: Total IPs: [count], First 5: [list]
```

## Test 4.3: Filter by ACR 8-10
```
I am testing tsc_list_ips to find high-risk assets with ACR 8-10 in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about ACR filtering]
📦 RESULT: Total high-risk IPs: [count], First 5: [list]
```

## Test 4.4: Filter by ACR 7-10 + Critical Severity
```
I am testing tsc_list_ips to find critical assets (ACR 7-10) with critical vulnerabilities in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about multi-filter]
📦 RESULT: Total matching IPs: [count], First 5: [list]
```

## Test 4.5: Filter by AES 600-1000
```
I am testing tsc_list_ips to find assets with high exposure (AES 600-1000) in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about AES filtering]
📦 RESULT: Total high-exposure IPs: [count], First 5: [list]
```

## Test 4.6: Filter by ACR + VPR + Exploit
```
I am testing tsc_list_ips to find critical assets (ACR 7-10) with exploitable high-priority vulnerabilities (VPR 8-10) in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about risk-based filtering]
📦 RESULT: Total high-risk assets: [count], First 5: [list]
```

## Test 4.7: Filter by ACR + AES + Critical + Exploit
```
I am testing tsc_list_ips to find assets with ACR 6-10, AES 500-1000, critical vulnerabilities, and exploits available in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about complex risk scoring]
📦 RESULT: Total matching assets: [count], First 5: [list]
```

## Test 4.8: Filter by VPR + Port 443 + TCP
```
I am testing tsc_list_ips to find assets with high-priority TCP vulnerabilities (VPR 7-10) on port 443 in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about network filtering]
📦 RESULT: Total assets with high-risk HTTPS vulns: [count], First 5: [list]
```

## Test 4.9: Advanced Filter (ACR + VPR + CVSS + Exploit + TCP)
```
I am testing tsc_list_ips to find critical assets (ACR 6-10) with network-exploitable vulnerabilities (VPR 8-10, CVSS v3 7-10, exploits available, TCP protocol) in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about advanced risk filtering]
📦 RESULT: Total critically exposed assets: [count], First 5: [list]
```

## Test 4.10: Reverse IP Lookup
```
I am testing tsc_list_ips to find which repositories and asset groups contain IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about reverse lookup]
📦 RESULT: Repositories: [list], Asset Groups: [list]
```

## Test 4.11: Full Details with ACR Filter
```
I am testing tsc_list_ips to list IPs with ACR > 7 and full details in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about full metadata]
📦 RESULT: Total IPs: [count], First 3 with DNS and ACR: [list]
```

## Test 4.12: Filter by Windows + Critical Severity
```
I am testing tsc_list_ips to find assets with critical Windows vulnerabilities in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about family + severity]
📦 RESULT: Total Windows assets with critical vulns: [count], First 5: [list]
```

## Test 4.13: Ultra-Complex Filter (ACR + AES + VPR + CVSS + Exploit + Windows + TCP)
```
I am testing tsc_list_ips to find Windows assets (ACR 6-10, AES 600-1000) with network-exploitable critical vulnerabilities (VPR 8-10, CVSS v3 8-10, exploits available, TCP protocol) in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about ultra-advanced filtering]
📦 RESULT: Total Windows assets at extreme risk: [count], First 5: [list]
```

## Test 4.14: Filter by EPSS 0.5-1.0
```
I am testing tsc_list_ips to find assets with vulnerabilities having high EPSS scores (0.5-1.0) in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about EPSS filtering]
📦 RESULT: Total assets with high-EPSS vulns: [count], First 5: [list]
```

## Test 4.15: All Scoring Metrics (VPR + CVSS + EPSS + ACR + AES)
```
I am testing tsc_list_ips to find assets (ACR 7-10, AES 600-1000) with vulnerabilities scoring high across all metrics (VPR 8-10, CVSS v3 8-10, EPSS 0.7-1.0) in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about comprehensive scoring]
📦 RESULT: Total critically scored assets: [count], First 5: [list]
```

## Test 4.16: Filter by Port Range (Windows + Port 445 + TCP + Exploit)
```
I am testing tsc_list_ips to find Windows assets with exploitable TCP vulnerabilities on port 445 in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about SMB vulnerabilities]
📦 RESULT: Total Windows assets with SMB exploits: [count], First 5: [list]
```

## Test 4.17: Enterprise Filter (ACR + VPR + Exploit + Windows + Network + Low Complexity)
```
I am testing tsc_list_ips to find Windows assets with ACR > 6 that have vulnerabilities with VPR > 8, are exploitable, can be exploited via network (TCP), and have low exploit complexity in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about enterprise-grade filtering]
📦 RESULT: Total easily exploitable Windows assets: [count], First 5: [list]
```

## Test 4.18: Critical Path Filter (All Risk Indicators)
```
I am testing tsc_list_ips to find Windows assets (ACR 6-10, AES 600-1000) with critical vulnerabilities (severity critical, VPR 8-10, CVSS v3 8-10, EPSS 0.7-1.0) that are exploitable via network (TCP protocol, port 445 or 443) and have low exploit complexity in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about critical path analysis]
📦 RESULT: Total Windows assets on critical attack path: [count], First 5: [list]
```

---

# TOOL 5 TESTS (15 tests)

## Test 5.1: Basic CVE Search (Log4Shell)
```
I am testing tsc_list_vulns_by_cve to search for CVE-2021-44228 (Log4Shell). Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about CVE search]
📦 RESULT: Total affected assets: [count], First 5 IPs: [list]
```

## Test 5.2: CVE with ACR Filter (Critical Assets)
```
I am testing tsc_list_vulns_by_cve to find critical assets (ACR 7-10) affected by CVE-2021-44228. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about risk filtering]
📦 RESULT: Critical assets with Log4Shell: [count], First 5 with ACR: [list]
```

## Test 5.3: CVE with ACR + Severity Filter
```
I am testing tsc_list_vulns_by_cve to find critical-severity CVE-2021-44228 on high-risk assets (ACR 8-10). Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about severity + ACR]
📦 RESULT: High-risk critical instances: [count], IPs: [list]
```

## Test 5.4: Basic CVE Search (EternalBlue)
```
I am testing tsc_list_vulns_by_cve to search for CVE-2017-0144 (EternalBlue). Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about CVE search]
📦 RESULT: Total affected assets: [count], First 5 IPs: [list]
```

## Test 5.5: CVE with ACR + Repository Filter
```
I am testing tsc_list_vulns_by_cve to find CVE-2017-0144 on critical assets (ACR 8-10) in repository "Default". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about scoped search]
📦 RESULT: Critical assets with EternalBlue: [count], IPs: [list]
```

## Test 5.6: CVE with Asset Group Filter
```
I am testing tsc_list_vulns_by_cve to find CVE-2021-44228 in asset group "Windows Hosts". Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about group filtering]
📦 RESULT: Windows Hosts with Log4Shell: [count], First 5: [list]
```

## Test 5.7: CVE with ACR + AES + Severity
```
I am testing tsc_list_vulns_by_cve to find critical-severity CVE-2021-44228 on assets with ACR 6-10 and AES 500-1000. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about risk scoring]
📦 RESULT: High-risk assets with critical Log4Shell: [count], First 5: [list]
```

## Test 5.8: CVE with Port + Protocol Filter
```
I am testing tsc_list_vulns_by_cve to find CVE-2021-44228 instances on TCP port 443. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about network filtering]
📦 RESULT: HTTPS-exposed Log4Shell instances: [count], First 5: [list]
```

## Test 5.9: CVE with ACR + VPR + Exploit + TCP
```
I am testing tsc_list_vulns_by_cve to find CVE-2017-0144 on critical assets (ACR 7-10) with VPR 8-10, exploits available, on TCP protocol. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about threat prioritization]
📦 RESULT: High-priority EternalBlue targets: [count], IPs: [list]
```

## Test 5.10: CVE with Ultra-Complex Filter (ACR + AES + VPR + CVSS + Exploit)
```
I am testing tsc_list_vulns_by_cve to find CVE-2021-44228 on assets with ACR 6-10, AES 600-1000, where vulnerability has VPR 8-10, CVSS v3 8-10, and exploits available. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about enterprise risk]
📦 RESULT: Critically exposed Log4Shell instances: [count], First 5: [list]
```

## Test 5.11: CVE Not Found (Error Handling)
```
I am testing tsc_list_vulns_by_cve to search for CVE-2099-99999 (non-existent). Please format your response as:

✅/❌ TEST STATUS: [Should PASS with 0 results]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about graceful handling]
📦 RESULT: Total affected assets: 0, Message: [message]
```

## Test 5.12: CVE with Pagination
```
I am testing tsc_list_vulns_by_cve to search for CVE-2021-44228, fetch first 50 records. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about pagination]
📦 RESULT: Returned [x] of [total] assets, First 5: [list]
```

## Test 5.13: CVE with Windows + VPR + Exploit + Port 445
```
I am testing tsc_list_vulns_by_cve to find CVE-2017-0144 (EternalBlue) on Windows assets with VPR 8-10, exploits available, on TCP port 445. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about SMB targeting]
📦 RESULT: Windows assets with high-priority SMB exploit: [count], First 5: [list]
```

## Test 5.14: CVE with All Scoring Metrics (VPR + CVSS + EPSS + ACR + AES)
```
I am testing tsc_list_vulns_by_cve to find CVE-2021-44228 on assets (ACR 7-10, AES 600-1000) with vulnerability scoring high across all metrics (VPR 8-10, CVSS v3 8-10, EPSS 0.7-1.0). Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about comprehensive scoring]
📦 RESULT: Critically scored Log4Shell instances: [count], First 5: [list]
```

## Test 5.15: CVE Critical Path (Windows + All Risk + Network + Low Complexity)
```
I am testing tsc_list_vulns_by_cve to find CVE-2021-44228 on Windows assets (ACR 6-10, AES 600-1000) where vulnerability has VPR > 8, CVSS v3 > 7, EPSS > 0.7, is exploitable, can be exploited via network (TCP), and has low exploit complexity. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about critical attack path]
📦 RESULT: Windows assets on Log4Shell critical path: [count], First 5: [list]
```

---

# OUTPUT FILE TEMPLATES

After running ALL tests above, generate TWO files:

## FILE 1: test_results.md

Simple markdown dump for easy parsing:

```markdown
# Test Results - Tenable.sc MCP v1.2.0

## Test 1.1: Basic IP Profile

**PROMPT:**
```
I am testing tsc_profile_ip_efficient to profile IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Hostname: [name], OS: [os], Vulnerabilities: C:[count] H:[count] M:[count] L:[count] I:[count]
```

**RESPONSE:**
```
[PASTE ACTUAL RESPONSE HERE]
```

---

## Test 1.2: Different IP Profile

**PROMPT:**
```
[prompt text]
```

**RESPONSE:**
```
[response text]
```

---

[REPEAT FOR ALL 60 TESTS]
```

## FILE 2: test_results.html

Collapsible HTML for visual review:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Results - Tenable.sc MCP v1.2.0</title>
    <style>
        body { font-family: monospace; margin: 20px; background: #1e1e1e; color: #d4d4d4; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #4ec9b0; border-bottom: 2px solid #4ec9b0; padding-bottom: 10px; }
        .test { margin: 10px 0; border: 1px solid #3c3c3c; }
        .header { padding: 10px; background: #252526; cursor: pointer; }
        .header:hover { background: #2d2d30; }
        .content { padding: 15px; background: #1e1e1e; display: none; }
        .content.show { display: block; }
        pre { background: #252526; padding: 10px; border-left: 3px solid #4ec9b0; overflow-x: auto; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Test Results - Tenable.sc MCP v1.2.0</h1>
        
        <!-- Test 1.1 -->
        <div class="test">
            <div class="header" onclick="this.nextElementSibling.classList.toggle('show')">
                ▶ Test 1.1: Basic IP Profile
            </div>
            <div class="content">
                <strong>PROMPT:</strong>
                <pre>I am testing tsc_profile_ip_efficient to profile IP 10.1.20.10. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Hostname: [name], OS: [os], Vulnerabilities: C:[count] H:[count] M:[count] L:[count] I:[count]</pre>
                
                <strong>RESPONSE:</strong>
                <pre>[PASTE ACTUAL RESPONSE HERE]</pre>
            </div>
        </div>
        
        <!-- Test 1.2 -->
        <div class="test">
            <div class="header" onclick="this.nextElementSibling.classList.toggle('show')">
                ▶ Test 1.2: Different IP Profile
            </div>
            <div class="content">
                <strong>PROMPT:</strong>
                <pre>I am testing tsc_profile_ip_efficient to profile IP 10.1.0.101. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: Hostname: [name], OS: [os], Vulnerabilities: C:[count] H:[count] M:[count] L:[count] I:[count]</pre>
                
                <strong>RESPONSE:</strong>
                <pre>[PASTE ACTUAL RESPONSE HERE]</pre>
            </div>
        </div>
        
        <!-- REPEAT FOR ALL 60 TESTS - copy this pattern for each test, replacing:
             - Test number (1.1, 1.2, 2a.1, etc.)
             - Test name in header
             - Prompt text
             - Response text
        -->
        
    </div>
</body>
</html>
```

**IMPORTANT:** 
- Generate BOTH `test_results.md` (full dump) and `test_results.html` (collapsible)
- In HTML: Create ONE collapsible section per test (60 total sections)
- Include the ACTUAL prompt text in each section
- Include the ACTUAL response from the MCP server
- Click header to expand/collapse - no extra buttons needed

---

**Total Tests:** 60 tests
- Tool 1: 5 tests
- Tool 2a: 10 tests
- Tool 2b: 12 tests
- Tool 4: 18 tests
- Tool 5: 15 tests

**Expected Runtime:** 20-30 minutes
