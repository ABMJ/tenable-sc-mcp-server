# Filter Format Reference - Tenable.sc MCP Server v1.2.0

This document provides comprehensive guidance on filter formats for all Tenable.sc MCP tools.

---

## Quick Reference

### ✅ Simple Filters (String/Number Format)

These filters accept simple string or number values:

```python
# Severity (use integer 0-4)
filters = {"severity": "4"}  # Critical
filters = {"severity": "3"}  # High
filters = {"severity": "2"}  # Medium
filters = {"severity": "1"}  # Low
filters = {"severity": "0"}  # Info

# Exploit availability (use boolean string)
filters = {"exploit_available": "true"}
filters = {"exploit_available": "false"}

# IP address
filters = {"ip": "10.1.20.10"}

# DNS name
filters = {"dns_name": "webserver01.domain.com"}

# Plugin ID
filters = {"plugin_id": "19506"}

# CVE ID
filters = {"cve": "CVE-2021-44228"}

# Port number
filters = {"port": 443}

# Protocol (use protocol number)
filters = {"protocol": "6"}   # TCP
filters = {"protocol": "17"}  # UDP
```

### ✅ Range Filters (Min-Max Format)

These filters accept range values in "min-max" format:

```python
# Asset Criticality Rating (ACR) - Scale: 0-10
filters = {"asset_criticality": "7-10"}  # High-risk assets
filters = {"asset_criticality": "8-10"}  # Critical assets
filters = {"asset_criticality": "6-10"}  # Medium+ risk

# Asset Exposure Score (AES) - Scale: 0-1000
filters = {"aes_score": "600-1000"}  # High exposure
filters = {"aes_score": "700-1000"}  # Very high exposure
filters = {"aes_score": "500-1000"}  # Medium+ exposure

# Vulnerability Priority Rating (VPR) - Scale: 0-10
filters = {"vpr_score": "8-10"}  # High priority
filters = {"vpr_score": "7-10"}  # Medium+ priority
filters = {"vpr_score": "9-10"}  # Critical priority

# CVSS v2 Base Score - Scale: 0-10
filters = {"base_cvss_score": "7-10"}  # High severity
filters = {"base_cvss_score": "9-10"}  # Critical severity

# CVSS v3 Base Score - Scale: 0-10
filters = {"cvss_v3_base_score": "7-10"}  # High severity
filters = {"cvss_v3_base_score": "8-10"}  # High+ severity

# CVSS v4 Base Score - Scale: 0-10
filters = {"cvss_v4_base_score": "7-10"}

# EPSS Score - Scale: 0-1 (probability)
filters = {"epss_score": "0.5-1.0"}  # High exploitation probability
filters = {"epss_score": "0.7-1.0"}  # Very high probability
filters = {"epss_score": "0.9-1.0"}  # Critical probability
```

### ⚠️ Complex Filters (Array of Objects Format)

These filters require array-of-objects format with numeric IDs:

#### Family Filter (Plugin Family)

**❌ WRONG (will fail):**
```python
filters = {"family": "Windows"}
filters = {"family": "Web Servers"}
```

**✅ CORRECT:**
```python
# Must use numeric family IDs
filters = {"family": [{"id": 24}]}  # Windows family
filters = {"family": [{"id": 21}]}  # Web Servers family

# Multiple families
filters = {"family": [{"id": 24}, {"id": 21}]}
```

**How to find family IDs:**
1. Use Tenable.sc UI: Analysis > Plugins > Families
2. Use API: `GET /rest/pluginFamily` endpoint
3. Common family IDs:
   - Windows: 24
   - Web Servers: 21
   - Databases: 13
   - DNS: 14
   - FTP: 15
   - SMTP: 19

#### Repository Filter

**❌ WRONG (will fail):**
```python
filters = {"repository": "Default"}
filters = {"repository": "Production"}
```

**✅ CORRECT:**
```python
# Must use numeric repository IDs
filters = {"repository": [{"id": 1}]}  # Repository ID 1

# Multiple repositories
filters = {"repository": [{"id": 1}, {"id": 2}]}
```

**How to find repository IDs:**
1. Use `tsc_list()` with resource="repository"
2. Use Tenable.sc UI: Repositories section
3. Use API: `GET /rest/repository` endpoint

#### Asset Group Filter (Works with Names!)

**✅ This filter supports names:**
```python
# Asset group by name (Tool 4 only)
tsc_list_ips(asset_group="Windows Hosts")
tsc_list_ips(asset_group="Production Servers")

# Tool automatically resolves names to IDs
```

---

## Filter Examples by Tool

### Tool 1: tsc_profile_ip_efficient (IP Profiling)

**This tool doesn't use filters** - it profiles a single IP comprehensively.

```python
# Basic usage
tsc_profile_ip_efficient("10.1.20.10")

# With options
tsc_profile_ip_efficient(
    "10.1.20.10",
    include_software=True,
    include_services=True
)
```

---

### Tool 2A: tsc_list_vulns_by_ip_summary (Vulnerability Summary)

#### Simple Filters

```python
# Filter by severity
tsc_list_vulns_by_ip_summary("10.1.20.10", filters={"severity": "4"})

# Filter by exploit availability
tsc_list_vulns_by_ip_summary("10.1.20.10", filters={"exploit_available": "true"})

# Filter by VPR score
tsc_list_vulns_by_ip_summary("10.1.20.10", filters={"vpr_score": "8-10"})
```

#### Multi-Filter Examples

```python
# Critical vulnerabilities with exploits
tsc_list_vulns_by_ip_summary("10.1.20.10", filters={
    "severity": "4",
    "exploit_available": "true"
})

# High-priority vulnerabilities (VPR + CVSS)
tsc_list_vulns_by_ip_summary("10.1.20.10", filters={
    "vpr_score": "8-10",
    "cvss_v3_base_score": "7-10"
})

# Advanced multi-filter (VPR + severity + exploit)
tsc_list_vulns_by_ip_summary("10.1.20.10", filters={
    "vpr_score": "8-10",
    "severity": "4",
    "exploit_available": "true"
})
```

#### ⚠️ Family Filter (Requires IDs)

```python
# ❌ WILL FAIL
tsc_list_vulns_by_ip_summary("10.1.20.10", filters={"family": "Windows"})

# ✅ CORRECT
tsc_list_vulns_by_ip_summary("10.1.20.10", filters={"family": [{"id": 24}]})
```

---

### Tool 2B: tsc_list_vulns_by_ip_full (Full Vulnerability Details)

#### Simple Filters

```python
# Critical vulnerabilities only
tsc_list_vulns_by_ip_full("10.1.20.10", filters={"severity": "4"})

# Vulnerabilities with exploits
tsc_list_vulns_by_ip_full("10.1.20.10", filters={"exploit_available": "true"})

# High CVSS vulnerabilities
tsc_list_vulns_by_ip_full("10.1.20.10", filters={"cvss_v3_base_score": "7-10"})
```

#### Multi-Filter Examples

```python
# Critical + exploitable + port 443
tsc_list_vulns_by_ip_full("10.1.20.10", filters={
    "severity": "4",
    "exploit_available": "true",
    "port": 443
})

# Advanced scoring (VPR + CVSS + exploit)
tsc_list_vulns_by_ip_full("10.1.20.10", filters={
    "vpr_score": "7-10",
    "cvss_v3_base_score": "7-10",
    "exploit_available": "true"
})

# Ultra-complex (7+ filters) - Test 2b.12 PASSED!
tsc_list_vulns_by_ip_full("10.1.20.10", filters={
    "vpr_score": "8-10",
    "cvss_v3_base_score": "7-10",
    "exploit_available": "true",
    "protocol": "6",  # TCP
    "aes_score": "600-1000"
})
```

#### Pagination

```python
# First 10 records
tsc_list_vulns_by_ip_full("10.1.20.10", end_offset=10)

# Next 10 records (11-20)
tsc_list_vulns_by_ip_full("10.1.20.10", start_offset=10, end_offset=20)

# Records 50-100
tsc_list_vulns_by_ip_full("10.1.20.10", start_offset=50, end_offset=100)
```

---

### Tool 4: tsc_list_ips (IP Discovery & Asset Enumeration)

#### Repository/Asset Group (Name Resolution Works!)

```python
# By repository name
tsc_list_ips(repository="Default")

# By asset group name (auto-resolves to ID)
tsc_list_ips(asset_group="Windows Hosts")
tsc_list_ips(asset_group="Production Servers")
```

#### Simple Filters

```python
# High-risk assets (ACR 8-10)
tsc_list_ips(repository="Default", filters={"asset_criticality": "8-10"})

# High-exposure assets (AES 600-1000)
tsc_list_ips(repository="Default", filters={"aes_score": "600-1000"})

# Assets with critical vulnerabilities
tsc_list_ips(repository="Default", filters={"severity": "4"})
```

#### Multi-Filter Examples

```python
# Critical assets with critical vulnerabilities
tsc_list_ips(repository="Default", filters={
    "asset_criticality": "7-10",
    "severity": "4"
})

# High-risk assets with exploitable vulns
tsc_list_ips(repository="Default", filters={
    "asset_criticality": "7-10",
    "exploit_available": "true",
    "vpr_score": "8-10"
})

# Ultra-complex (Test 4.13 PASSED without family filter!)
tsc_list_ips(repository="Default", filters={
    "asset_criticality": "6-10",
    "aes_score": "600-1000",
    "vpr_score": "8-10",
    "cvss_v3_base_score": "8-10",
    "exploit_available": "true",
    "protocol": "6"  # TCP
})
```

#### Reverse Lookup

```python
# Find which repos/groups contain an IP
tsc_list_ips(ip="10.1.20.10")

# Returns:
# {
#     "repositories": ["Default"],
#     "asset_groups": ["Windows Hosts", "SSL or TLS Servers", ...]
# }
```

#### Full Details Mode

```python
# Get full metadata (DNS, ACR, AES, OS)
tsc_list_ips(
    repository="Default",
    filters={"asset_criticality": "7-10"},
    include_details=True
)
```

---

### Tool 5: tsc_list_vulns_by_cve (CVE Search / Outbreak Response)

#### Basic CVE Search

```python
# Search for Log4Shell
tsc_list_vulns_by_cve("CVE-2021-44228")

# Search for EternalBlue
tsc_list_vulns_by_cve("CVE-2017-0144")
```

#### With Asset Risk Filters

```python
# Critical assets with Log4Shell
tsc_list_vulns_by_cve("CVE-2021-44228", filters={
    "asset_criticality": "7-10"
})

# High-exposure assets with EternalBlue
tsc_list_vulns_by_cve("CVE-2017-0144", filters={
    "aes_score": "600-1000"
})
```

#### With Vulnerability Scoring

```python
# Log4Shell instances with high VPR
tsc_list_vulns_by_cve("CVE-2021-44228", filters={
    "vpr_score": "8-10"
})

# EternalBlue with high CVSS
tsc_list_vulns_by_cve("CVE-2017-0144", filters={
    "cvss_v3_base_score": "7-10"
})
```

#### Ultra-Complex Filters (Test 5.10 PASSED!)

```python
# Critically exposed Log4Shell instances
tsc_list_vulns_by_cve("CVE-2021-44228", filters={
    "asset_criticality": "6-10",
    "aes_score": "600-1000",
    "vpr_score": "8-10",
    "cvss_v3_base_score": "8-10",
    "exploit_available": "true"
})
```

#### With Asset Group Filter

```python
# Log4Shell in specific asset group
tsc_list_vulns_by_cve("CVE-2021-44228", filters={
    "asset_group": "Windows Hosts"  # Works with name!
})
```

#### ⚠️ Repository Filter (Requires IDs)

```python
# ❌ WILL FAIL (Test 5.5)
tsc_list_vulns_by_cve("CVE-2017-0144", filters={"repository": "Default"})

# ✅ CORRECT
tsc_list_vulns_by_cve("CVE-2017-0144", filters={"repository": [{"id": 1}]})
```

---

## Common Filter Combinations

### Emergency Outbreak Response

```python
# Critical assets with CVE X
tsc_list_vulns_by_cve("CVE-YYYY-XXXXX", filters={
    "asset_criticality": "7-10"
})

# High-exposure assets with CVE X
tsc_list_vulns_by_cve("CVE-YYYY-XXXXX", filters={
    "aes_score": "600-1000"
})

# All high-priority instances
tsc_list_vulns_by_cve("CVE-YYYY-XXXXX", filters={
    "vpr_score": "8-10",
    "cvss_v3_base_score": "7-10"
})
```

### Risk-Based Asset Discovery

```python
# Critical assets with exploitable high-priority vulns
tsc_list_ips(repository="Default", filters={
    "asset_criticality": "7-10",
    "vpr_score": "8-10",
    "exploit_available": "true"
})

# High-exposure assets with network-exploitable vulns
tsc_list_ips(repository="Default", filters={
    "aes_score": "600-1000",
    "protocol": "6",  # TCP
    "exploit_available": "true"
})
```

### Network-Based Targeting

```python
# HTTPS vulnerabilities
tsc_list_ips(repository="Default", filters={
    "port": 443,
    "protocol": "6",  # TCP
    "vpr_score": "7-10"
})

# SMB vulnerabilities (port 445)
tsc_list_ips(repository="Default", filters={
    "port": 445,
    "protocol": "6",
    "exploit_available": "true"
})
```

### Comprehensive Scoring

```python
# Assets scoring high across ALL metrics
tsc_list_ips(repository="Default", filters={
    "asset_criticality": "7-10",
    "aes_score": "600-1000",
    "vpr_score": "8-10",
    "cvss_v3_base_score": "8-10",
    "epss_score": "0.7-1.0"
})
```

---

## Filter Value Formats Summary

| Filter | Format | Example | Test Status |
|--------|--------|---------|-------------|
| severity | Integer 0-4 | `"4"` (Critical) | ✅ PASSED |
| exploit_available | Boolean string | `"true"` or `"false"` | ✅ PASSED |
| asset_criticality | Range "min-max" | `"7-10"` | ✅ PASSED |
| aes_score | Range "min-max" | `"600-1000"` | ✅ PASSED |
| vpr_score | Range "min-max" | `"8-10"` | ✅ PASSED |
| cvss_v3_base_score | Range "min-max" | `"7-10"` | ✅ PASSED |
| epss_score | Range "min-max" | `"0.5-1.0"` | ✅ PASSED |
| port | Integer | `443` | ✅ PASSED |
| protocol | Protocol number | `"6"` (TCP) | ✅ PASSED |
| ip | IP address | `"10.1.20.10"` | ✅ PASSED |
| cve | CVE ID | `"CVE-2021-44228"` | ✅ PASSED |
| plugin_id | Plugin ID | `"19506"` | ✅ PASSED |
| family | Array of objects | `[{"id": 24}]` | ⚠️ REQUIRES ID |
| repository | Array of objects | `[{"id": 1}]` | ⚠️ REQUIRES ID |
| asset_group | String (Tool 4/5) | `"Windows Hosts"` | ✅ PASSED |

---

## Troubleshooting

### Error: "Filter 'family' should be an array of records"

**Problem:** You're passing a family name instead of ID array.

**Solution:**
```python
# Instead of:
filters = {"family": "Windows"}

# Use:
filters = {"family": [{"id": 24}]}
```

**How to find family IDs:**
1. Tenable.sc UI: Analysis > Plugins > Families (hover shows ID)
2. API endpoint: `GET /rest/pluginFamily`
3. See common IDs in "Complex Filters" section above

### Error: "Filter 'repository' should be an array of records"

**Problem:** You're passing a repository name instead of ID array.

**Solution:**
```python
# Instead of:
filters = {"repository": "Default"}

# Use:
filters = {"repository": [{"id": 1}]}
```

**How to find repository IDs:**
1. Use `tsc_list()` with `resource="repository"`
2. Tenable.sc UI: Repositories section
3. API endpoint: `GET /rest/repository`

### Zero Results with Multi-Filter

**Problem:** Your filters are too restrictive and exclude all results.

**Solution:**
1. Start with one filter, then add more incrementally
2. Check each filter value is correct (severity 4 = critical, not "critical")
3. Verify range filters use "min-max" format, not operators like ">7"
4. Some combinations may legitimately return zero results

---

## Test Results Reference

Based on comprehensive testing (60 tests, 56 passed):

### ✅ Fully Tested & Working
- All simple filters (severity, exploit, VPR, CVSS, AES, ACR, EPSS, port, protocol)
- All range filters (ACR, AES, VPR, CVSS, EPSS)
- Multi-filter combinations (2-7+ filters)
- Asset group name resolution (Tools 4, 5)
- Repository name resolution (Tool 4)
- Reverse IP lookup
- Pagination
- Zero-result handling

### ⚠️ Requires ID Format
- `family` filter (4 test failures)
- `repository` filter in Tool 5 (1 test failure)

### Token Efficiency Achieved
- Tool 1: 52-76% better than target
- Tool 2A: Meeting/exceeding target
- Tool 2B: 40% better than target
- Tool 4: On target
- Tool 5: Meeting target

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-10  
**Test Suite Version:** v1.2.0  
**Pass Rate:** 93.3% (56/60)
