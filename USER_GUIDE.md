# Tenable.sc MCP Server - User Guide

**Version**: v1.3.1  
**Last Updated**: 2026-06-24  
**Status**: 8 Production-Ready Tools

---

## 📑 Table of Contents

### Overview
- [Introduction](#introduction)
- [Quick Start](#quick-start)

### Available Tools
1. [tsc_profile_ip_efficient](#1-tsc_profile_ip_efficient---complete-ip-security-profile) - Complete IP Security Profile
2. [tsc_list_vulns_by_ip_summary](#2a-tsc_list_vulns_by_ip_summary---quick-vulnerability-count) - Quick Vulnerability Count
3. [tsc_list_vulns_by_ip_full](#2b-tsc_list_vulns_by_ip_full---detailed-vulnerability-records) - Detailed Vulnerability Records
4. [tsc_list_ips](#4-tsc_list_ips---ip-discovery--asset-enumeration) - IP Discovery & Asset Enumeration
5. [tsc_list_vulns_by_cve](#5-tsc_list_vulns_by_cve---cve-search-across-infrastructure) - CVE Search Across Infrastructure
6. [tsc_list_operating_systems](#6-tsc_list_operating_systems---os-name-discovery) - OS Name Discovery
7. [tsc_list_plugin_families](#7-tsc_list_plugin_families---plugin-family-discovery) - Plugin Family Discovery
8. [tsc_list_missing_patches](#8-tsc_list_missing_patches---patch-gap-analysis) - Patch Gap Analysis

### Reference
- [Universal Filter Framework](#universal-filter-framework)
- [Performance & Caching](#performance--caching)
- [Best Practices](#best-practices)

---

## Introduction

The Tenable.sc MCP Server provides AI-powered tools for security vulnerability management and asset discovery. These tools are optimized for use with Claude Desktop and other MCP-compatible AI assistants.

### What You Can Do

- **Incident Response**: Instantly profile suspicious IPs with complete security context
- **Vulnerability Management**: Search for specific CVEs across your entire infrastructure
- **Asset Discovery**: Find and enumerate IPs by repository, asset group, or criticality
- **Risk Assessment**: Get vulnerability counts and details filtered by severity, VPR, or EPSS scores
- **Compliance**: Track patching status and credential-based scanning coverage
- **Patch Management**: Identify missing patches and security updates across all operating systems

### Key Features

- ✅ **Token Efficient**: 83-90% reduction in LLM token usage vs raw API calls
- ✅ **Smart Caching**: Intelligent TTLs (60s-300s) for frequently accessed data
- ✅ **Unified Filters**: 74+ filters work consistently across all tools
- ✅ **Natural Language**: Use conversational commands with your AI assistant
- ✅ **Production Ready**: Battle-tested with comprehensive error handling

---

## Quick Start

### Example Conversation

```
You: Profile IP 10.1.20.10

Claude: I'll get a complete security profile for 10.1.20.10...
[Returns: Host identity, vulnerability summary, last scan info, 
 installed software, running services, asset groups]

You: List all critical IPs in the Default repository

Claude: Finding IPs with ACR 7-10 in Default repository...
[Returns: List of high-risk IP addresses]

You: Do we have CVE-2021-44228 (Log4Shell)?

Claude: Searching for CVE-2021-44228 across infrastructure...
[Returns: Affected IPs with severity counts and remediation details]
```

### Common Tasks

| Task | Command Example |
|------|----------------|
| **Profile a host** | "Profile IP 10.1.20.10" |
| **Find critical assets** | "List IPs with ACR > 7 in Production" |
| **Check CVE exposure** | "Do we have CVE-2021-44228?" |
| **Vulnerability details** | "Show vulnerabilities for 192.168.1.100" |
| **Asset discovery** | "List all Windows hosts in Default repository" |
| **Patch gap analysis** | "What patches are missing on 10.1.20.10?" |

---

## 1. `tsc_profile_ip_efficient` - Complete IP Security Profile

**Status**: ✅ Production Ready | **Token Savings**: 83-90% | **Cache**: 180-300s  
**Module**: `tools/ip_profiling.py`

### What This Tool Does

Gets a complete security assessment for a single IP address in one command. Combines host identity, vulnerability counts, scan status, installed software, running services, and asset group membership.

### When to Use This Tool

- **Incident Response**: "Tell me everything about this suspicious IP"
- **Asset Audit**: "What's the security posture of our database server at 10.1.20.10?"
- **Credential Validation**: "Was this server scanned with credentials?"
- **Compliance Check**: "Show me the scan status and vulnerabilities for this critical host"
- **Before Patching**: "What software and services are running before I patch?"

### How to Use

```bash
# Simple profile
Profile IP 10.1.20.10

# Full example with context
Use tenable-sc to profile IP 10.1.20.10 efficiently
```

### What You Get Back

- **Host Identity**: Hostname, DNS name, NetBIOS name, MAC address, ACR score
- **Vulnerability Summary**: Count of vulnerabilities by severity (Critical/High/Medium/Low/Info)
- **Last Scan Info**: Scan name, policy used, timestamp, authentication status
- **Installed Software**: Up to 50 most important packages/applications
- **Running Services**: Active services with port numbers
- **Asset Groups**: All asset group memberships (up to 46 groups)

### Performance

- **Tokens Used**: ~2,500 tokens (vs ~15,000 without optimization) = **83% reduction**
- **API Calls**: 6 optimized queries with independent caching
- **Cache TTL**: 180s for vulnerabilities, 300s for static data
- **Response Time**: <1s cached, 1-3s fresh

### Example Output

```json
{
  "ok": true,
  "ip": "10.1.20.10",
  "summary": {
    "hostname": "webserver01.domain.com",
    "os": "Windows Server 2019",
    "last_scan": "2026-06-19T10:30:00Z",
    "vulnerabilities": {
      "critical": 5,
      "high": 23,
      "medium": 87,
      "low": 12,
      "info": 45
    }
  },
  "data": {
    "basic_info": {...},
    "vulnerability_summary": {...},
    "last_scan": {...},
    "installed_software": [...],
    "running_services": [...],
    "asset_groups": [...]
  }
}
```

### Optional Parameters

```python
# Disable specific sections for faster response
tsc_profile_ip_efficient(
    "10.1.20.10",
    include_software=False,      # Skip software list
    include_services=False,      # Skip services list
    include_scan_info=False,     # Skip scan metadata
    include_asset_groups=False   # Skip asset group membership
)
```

### Best Practices

1. **Use for investigation**: Perfect for incident response and asset audits
2. **Check authentication**: Look for "credentialed": true in scan_info
3. **Monitor ACR scores**: Assets with ACR 7-10 need immediate attention
4. **Cache awareness**: Data is cached for 3-5 minutes, suitable for real-time investigation

---

## 2a. `tsc_list_vulns_by_ip_summary` - Quick Vulnerability Count

**Status**: ✅ Production Ready | **Token Savings**: 88% | **Cache**: 180s  
**Module**: `tools/vulnerability_lookup.py`

### What This Tool Does

Get vulnerability counts by severity for an IP address without pulling full vulnerability records. Perfect for quick scoping and dashboard metrics.

### When to Use This Tool

- **Quick Check**: "How many vulnerabilities does IP X have?"
- **Severity Breakdown**: "Show me the vulnerability summary for 10.1.20.10"
- **Dashboard Metrics**: Get counts for multiple IPs quickly
- **Scope Before Details**: Check if it's worth pulling full vulnerability records
- **Triage**: Quickly assess risk level before detailed investigation

### How to Use

```bash
# Basic usage
How many vulnerabilities does 10.1.20.10 have?

# With filters
Show vulnerability summary for 192.168.1.100, only critical and high severity
```

### What You Get Back

```json
{
  "ok": true,
  "ip": "10.1.20.10",
  "summary": {
    "total": 183,
    "by_severity": {
      "critical": 15,
      "high": 45,
      "medium": 123,
      "low": 0,
      "info": 0
    }
  }
}
```

### Performance

- **Tokens Used**: ~700 tokens (vs ~6,000 for full details) = **88% reduction**
- **API Calls**: 1 optimized query
- **Cache TTL**: 180s (3 minutes)
- **Response Time**: <1s cached, 1-2s fresh

### Filtering Options

```python
# Filter by severity
tsc_list_vulns_by_ip_summary(
    "10.1.20.10",
    filters={"severity": "critical"}  # Only critical vulns
)

# Filter by exploit availability
tsc_list_vulns_by_ip_summary(
    "10.1.20.10",
    filters={"exploit_available": "Yes"}  # Only exploitable
)

# Multiple filters
tsc_list_vulns_by_ip_summary(
    "10.1.20.10",
    filters={
        "severity": "high",
        "vpr_score": "7-10",
        "exploit_available": "Yes"
    }
)
```

### Best Practices

1. **Use before full scan**: Check counts before pulling all vulnerability records
2. **Quick triage**: Identify high-risk hosts without downloading full data
3. **Combine with filters**: Get precise counts for specific vulnerability types
4. **Cache aware**: Summary data cached for 3 minutes

---

## 2b. `tsc_list_vulns_by_ip_full` - Detailed Vulnerability Records

**Status**: ✅ Production Ready | **Token Savings**: 58% | **Cache**: 180s  
**Module**: `tools/vulnerability_lookup.py`

### What This Tool Does

Get complete vulnerability records for an IP address with full details including plugin information, scoring (CVSS/VPR/EPSS), exploit availability, patch dates, and remediation guidance.

### When to Use This Tool

- **Detailed Investigation**: "Show me all vulnerabilities for IP X with full details"
- **Remediation Planning**: Get solution text and patch information
- **Export Data**: Pull vulnerability records for reporting or ticketing
- **Compliance**: Generate detailed vulnerability reports
- **Risk Analysis**: Review CVSS, VPR, EPSS scores for prioritization

### How to Use

```bash
# Basic usage
Show detailed vulnerabilities for 10.1.20.10

# With pagination
Show first 10 critical vulnerabilities for 192.168.1.100

# With filters
List high severity vulnerabilities with exploits available for 10.1.20.10
```

### What You Get Back

Complete vulnerability records with:
- Plugin ID and name
- Severity (0-4 scale and text)
- CVSS v2/v3/v4 scores
- VPR score (Vulnerability Priority Rating)
- EPSS score (Exploit Prediction Scoring System)
- Exploit availability
- Patch publication date
- Vulnerability publication date
- Solution text
- Synopsis and description
- References (CVE, BID, etc.)
- Plugin output
- Port and protocol
- First seen / Last seen dates
- Mitigation status

### Performance

- **Tokens Used**: ~5,000 tokens for 50 records (vs ~12,000 unfiltered) = **58% reduction**
- **API Calls**: 1 paginated query
- **Cache TTL**: 180s (3 minutes)
- **Response Time**: <1s cached, 2-4s fresh
- **Pagination**: 10-200 records per request (default: 50)

### Pagination

```python
# Get first 50 vulnerabilities
tsc_list_vulns_by_ip_full("10.1.20.10")

# Get next 50 (records 50-100)
tsc_list_vulns_by_ip_full("10.1.20.10", start_offset=50, end_offset=100)

# Get first 10 only
tsc_list_vulns_by_ip_full("10.1.20.10", end_offset=10)
```

### Filtering Options

```python
# Critical vulnerabilities only
tsc_list_vulns_by_ip_full(
    "10.1.20.10",
    filters={"severity": "critical"}
)

# High VPR scores
tsc_list_vulns_by_ip_full(
    "10.1.20.10",
    filters={"vpr_score": "7-10"}
)

# Exploitable vulnerabilities
tsc_list_vulns_by_ip_full(
    "10.1.20.10",
    filters={"exploit_available": "Yes"}
)

# Specific CVE
tsc_list_vulns_by_ip_full(
    "10.1.20.10",
    filters={"cve": "CVE-2021-44228"}
)

# Multiple filters
tsc_list_vulns_by_ip_full(
    "10.1.20.10",
    filters={
        "severity": "high",
        "exploit_available": "Yes",
        "vpr_score": "8-10",
        "port": 443,
        "protocol": "TCP"
    },
    end_offset=20  # First 20 results
)
```

### Best Practices

1. **Use summary first**: Call `tsc_list_vulns_by_ip_summary` to check counts before pulling full records
2. **Apply filters**: Narrow results with severity, VPR, or exploit filters
3. **Pagination**: Request small batches (10-50 records) for faster response
4. **Cache timing**: Data cached for 3 minutes, suitable for investigation workflows

---

## 4. `tsc_list_ips` - IP Discovery & Asset Enumeration

**Status**: ✅ Production Ready | **Token Savings**: 85% | **Cache**: 120s  
**Module**: `tools/asset_discovery.py`

### What This Tool Does

List IP addresses in repositories or asset groups with optional filtering by asset criticality, vulnerabilities, or other criteria. Includes reverse lookup to find where an IP exists.

### When to Use This Tool

- **Asset Discovery**: "List all IPs in Production repository"
- **Critical Assets**: "Show me all IPs with ACR score > 7"
- **Reverse Lookup**: "Which asset groups contain IP 10.1.20.10?"
- **Inventory**: "How many Windows hosts are in Default repository?"
- **Risk Profiling**: "List IPs with critical vulnerabilities"

### How to Use

```bash
# List IPs in repository
List IPs in Default repository

# Filter by criticality
Show me critical assets (ACR > 7) in Production

# Reverse lookup
Which asset groups contain IP 10.1.20.10?

# With detailed metadata
List IPs in Production with full details (hostname, MAC, ACR, OS)
```

### What You Get Back

**Basic Mode** (default):
- List of IP addresses

**Detailed Mode** (`include_details=True`):
- IP address
- DNS hostname
- MAC address
- UUID
- ACR score (Asset Criticality Rating)
- AES score (Asset Exposure Score)
- Operating System
- Repository name

**Reverse Lookup Mode** (`ip` parameter):
- IP address
- List of repositories containing this IP
- List of asset groups containing this IP
- Found status

### Performance

- **Tokens Used**: ~400-3,700 tokens depending on dataset size = **85% reduction**
- **API Calls**: 1-2 optimized queries (1 for list, 2 for reverse lookup)
- **Cache TTL**: 120s (2 minutes)
- **Response Time**: <1s cached, 2-4s fresh

### Filtering Options

```python
# By repository
tsc_list_ips(repository="Default")

# By asset group
tsc_list_ips(asset_group="Windows Hosts")

# By asset criticality (ACR)
tsc_list_ips(
    repository="Default",
    filters={"asset_criticality": "8-10"}  # Critical assets only
)

# By severity
tsc_list_ips(
    repository="Production",
    filters={"severity": "critical"}  # Assets with critical vulns
)

# Multiple filters
tsc_list_ips(
    repository="Default",
    filters={
        "asset_criticality": "7-10",
        "aes_score": "600-1000",
        "severity": "high",
        "exploit_available": "Yes"
    }
)

# Reverse lookup
tsc_list_ips(ip="10.1.20.10")  # Find where this IP exists

# With detailed metadata
tsc_list_ips(repository="Default", include_details=True)
```

### Example Output

**Basic List:**
```json
{
  "ok": true,
  "repository": "Default",
  "total_ips": 413,
  "ips": ["10.1.20.10", "10.1.20.11", "10.1.20.12", ...]
}
```

**Detailed List:**
```json
{
  "ok": true,
  "repository": "Default",
  "total_ips": 156,
  "ips": [
    {
      "ip": "10.1.20.10",
      "dns_name": "webserver01.domain.com",
      "mac": "00:50:56:12:34:56",
      "uuid": "abc123...",
      "acr_score": 8.5,
      "aes_score": 650,
      "os": "Windows Server 2019"
    }
  ]
}
```

**Reverse Lookup:**
```json
{
  "ok": true,
  "ip": "10.1.20.10",
  "repositories": ["Default", "PCI Assets"],
  "asset_groups": ["Windows Hosts", "Production Servers"],
  "found": true
}
```

### Best Practices

1. **Start simple**: List IPs without filters to understand scope
2. **Use filters**: Narrow to critical assets with ACR or severity filters
3. **Reverse lookup**: Find asset membership before making changes
4. **Detailed mode**: Use sparingly (more tokens) when you need metadata
5. **Cache timing**: IP lists cached for 2 minutes

### Scoring Filter Format

⚠️ **IMPORTANT**: Scoring filters use RANGE format, not operators.

```python
# ✅ Correct (range format)
filters={"asset_criticality": "7-10"}
filters={"vpr_score": "8-10"}
filters={"aes_score": "600-1000"}

# ❌ Incorrect (operators not supported)
filters={"asset_criticality": ">7"}
filters={"vpr_score": ">=8"}
```

**Why?** Tenable.sc backend only supports inclusive ranges for scoring filters.

---

## 5. `tsc_list_vulns_by_cve` - CVE Search Across Infrastructure

**Status**: ✅ Production Ready | **Token Savings**: 85% | **Cache**: 240s  
**Module**: `tools/vulnerability_lookup.py`

### What This Tool Does

Search for a specific CVE across your entire infrastructure. Returns list of unique affected IPs with severity counts. Perfect for emergency outbreak response and CVE-based asset discovery.

### When to Use This Tool

- **Outbreak Response**: "Do we have CVE-2021-44228 (Log4Shell)?"
- **CVE Investigation**: "List all hosts with CVE-X"
- **Impact Scoping**: "How many assets are affected by CVE-Y?"
- **Patch Verification**: "Verify remediation for CVE after patching"
- **Security Bulletins**: "Check exposure to recently disclosed vulnerability"

### How to Use

```bash
# Basic CVE search
Do we have CVE-2021-44228?

# With filters
List critical assets with CVE-2021-44228 (ACR > 7)

# Check specific repository
Search for CVE-2017-0144 in Production repository
```

### What You Get Back

For each affected IP:
- IP address
- Hostname
- Total vulnerability count
- Severity breakdown (Critical/High/Medium/Low/Info counts)
- ACR score (Asset Criticality Rating)
- AES score (Asset Exposure Score)
- Repository name

### Performance

- **Tokens Used**: ~800-1,500 tokens (vs ~10,000 raw API) = **85% reduction**
- **API Calls**: 1 optimized query with in-memory deduplication
- **Cache TTL**: 240s (4 minutes)
- **Response Time**: <1s cached, 2-4s fresh
- **Pagination**: Default 200 records per request (covers 90% of use cases)

### Filtering Options

```python
# Basic search
tsc_list_vulns_by_cve("CVE-2021-44228")

# Critical assets only
tsc_list_vulns_by_cve(
    "CVE-2021-44228",
    filters={"asset_criticality": "7-10"}
)

# Specific repository
tsc_list_vulns_by_cve(
    "CVE-2021-44228",
    filters={"repository": "Production"}
)

# Multiple filters
tsc_list_vulns_by_cve(
    "CVE-2021-44228",
    filters={
        "repository": "Production",
        "asset_criticality": "7-10",
        "exploit_available": "Yes"
    }
)

# Pagination for large results
tsc_list_vulns_by_cve(
    "CVE-2021-44228",
    start_offset=200,
    end_offset=400  # Next page
)
```

### Example Output

```json
{
  "ok": true,
  "cve": "CVE-2021-44228",
  "summary": {
    "total_ips": 20,
    "returned_ips": 20,
    "start_offset": 0,
    "end_offset": 200,
    "more_available": false
  },
  "affected_ips": [
    {
      "ip": "192.168.5.20",
      "hostname": "webserver01.domain.com",
      "total_vulns": 2,
      "severity_critical": 0,
      "severity_high": 2,
      "severity_medium": 0,
      "severity_low": 0,
      "severity_info": 0,
      "acr_score": "8.5",
      "aes_score": 585,
      "repository": "Default"
    }
  ],
  "note": "For detailed remediation, use tsc_list_vulns_by_ip_full with cve filter"
}
```

### Best Practices

1. **Emergency response**: Use this as first step in outbreak investigation
2. **Follow up**: After identifying IPs, use `tsc_list_vulns_by_ip_full` for remediation details
3. **Apply filters**: Narrow to critical assets or specific repositories
4. **Pagination**: Check `more_available` flag, fetch additional pages if needed
5. **Cache timing**: CVE searches cached for 4 minutes

### For Detailed Remediation

This tool returns summary counts. For full remediation details:

```python
# Step 1: Find affected IPs
result = tsc_list_vulns_by_cve("CVE-2021-44228")

# Step 2: Get remediation for each IP
for ip_data in result["affected_ips"]:
    details = tsc_list_vulns_by_ip_full(
        ip_data["ip"],
        filters={"cve": "CVE-2021-44228"}
    )
    # details contains solution text, plugin output, etc.
```

---

## 6. `tsc_list_operating_systems` - OS Name Discovery

**Status**: ✅ Production Ready | **Token Savings**: 80%+ | **Cache**: 300s  
**Module**: `tools/assets/asset_discovery.py`

### What This Tool Does

Discovers all valid operating system names from the Tenable.sc listos API. Use this to find exact OS names for filtering with the `operating_system` filter.

### When to Use This Tool

- **Before OS Filtering**: "What OS names are available for filtering?"
- **Asset Discovery Planning**: "Show me all Windows variants in the system"
- **Filter Validation**: "Is 'Windows Server 2019' a valid OS name?"
- **Inventory Analysis**: "List all Linux distributions detected"

### How to Use It

#### Basic Discovery
```
You: What operating systems are available?

Claude: [Lists all OS names detected, e.g., "Windows 10", "Windows Server 2019", 
         "Ubuntu 20.04", "CentOS Linux 7", etc.]
```

#### Find Specific OS Variants
```
You: Show me all Windows operating systems

Claude: [Filters list to Windows variants only]
```

### What You Get Back

```json
{
  "ok": true,
  "total": 156,
  "operating_systems": [
    "Windows 10",
    "Windows Server 2019",
    "Windows 11",
    "Ubuntu 20.04",
    "CentOS Linux 7",
    ...
  ],
  "cache_status": "HIT"
}
```

### Key Features

- **Live API Data**: Always reflects current Tenable.sc detection results
- **Fast Caching**: 300s (5 minute) cache for quick repeated queries
- **Use with Filters**: Get exact names for `operating_system` filter
- **Token Efficient**: Compact list format, ~500-1,000 tokens

### Pro Tips

1. **Use before filtering**: Get exact OS name, then use in `tsc_list_ips`
2. **Case sensitive**: Use exact name as returned (e.g., "Windows 10" not "windows 10")
3. **Handles variants**: Returns all detected variants (e.g., 11 Windows 10 variants)

### Example Workflow

```python
# Step 1: Discover OS names
os_list = tsc_list_operating_systems()

# Step 2: Find IPs with specific OS
ips = tsc_list_ips(
    repository="Default",
    filters={"operating_system": "Windows 10"}  # Use exact name from step 1
)
```

---

## 7. `tsc_list_plugin_families` - Plugin Family Discovery

**Status**: ✅ Production Ready | **Token Savings**: 85%+ | **Cache**: 86400s (24h)  
**Module**: `tools/admin/plugins.py`

### What This Tool Does

Lists all 123 plugin families with their numeric IDs and names. Essential for using the `family` filter correctly, as Tenable.sc requires numeric family IDs internally.

### When to Use This Tool

- **Before Family Filtering**: "What plugin families are available?"
- **Find Family ID**: "What's the ID for the Windows plugin family?"
- **Discover Categories**: "List all compliance plugin families"
- **Validate Filters**: "Does the 'Database' family exist?"

### How to Use It

#### List All Families
```
You: What plugin families are available?

Claude: [Lists 123 families with IDs, e.g., 
         "Windows (ID: 20)", "Red Hat Local Security Checks (ID: 21)", etc.]
```

#### Search for Specific Family
```
You: What's the ID for the Windows plugin family?

Claude: Windows plugin family has ID 20
```

### What You Get Back

```json
{
  "ok": true,
  "total": 123,
  "plugin_families": [
    {
      "id": "20",
      "name": "Windows"
    },
    {
      "id": "21",
      "name": "Red Hat Local Security Checks"
    },
    {
      "id": "23",
      "name": "Misc."
    },
    ...
  ],
  "cache_status": "HIT"
}
```

### Key Features

- **Smart Name→ID Resolution**: Tools auto-resolve family names to IDs
- **Long Cache**: 24-hour cache (families rarely change)
- **123 Total Families**: Standard (75) + Extended (34) + WAS (14)
- **Token Efficient**: ~3,000-4,000 tokens for full list

### Pro Tips

1. **Use names directly**: Tools accept "Windows" and auto-resolve to ID 20
2. **Check Misc. family**: Many plugins are in "Misc." (ID 23), including Log4Shell
3. **Case matters**: Use exact name (e.g., "Windows" not "windows")
4. **Validation**: Invalid families raise helpful errors

### Example Workflow

```python
# Step 1: Discover family names
families = tsc_list_plugin_families()

# Step 2: Filter vulnerabilities by family
vulns = tsc_list_vulns_by_ip_full(
    "10.1.20.10",
    filters={"family": "Windows"}  # Auto-resolves to ID 20
)

# Or filter IPs with vulnerabilities in specific family
ips = tsc_list_ips(
    repository="Default",
    filters={
        "family": "Windows",
        "severity": "critical"
    }
)
```

---

## 8. `tsc_list_missing_patches` - Patch Gap Analysis

**Status**: ✅ Production Ready | **Token Savings**: 60-70% | **Cache**: 240s (4m)  
**Module**: `tools/patch_management.py`

### What This Tool Does

Lists missing patches and security updates across all operating systems by analyzing Tenable plugin output. Supports two modes:
- **Universal Mode** (Plugin 66334): All OS types + third-party software (Chrome, Office, VMware, etc.)
- **Windows Mode** (Plugin 38153): Windows KB articles and legacy MS bulletins

### When to Use This Tool

- **Patch Compliance**: "What patches are missing on our production servers?"
- **Vulnerability Remediation**: "Which Microsoft KBs will fix these vulnerabilities?"
- **Incident Response**: "Is this server missing critical patches?"
- **Asset Audit**: "Show me all IPs with missing patches in Default repository"
- **Risk Prioritization**: "Which critical assets have the most missing patches?"

### How to Use It

#### Basic Single-IP Query (Universal Mode)
```
You: What patches are missing on 10.1.20.10?

Claude: Analyzing missing patches for 10.1.20.10 using universal mode...
[Returns: 41 patches - 37 Microsoft KBs + 4 third-party updates]
```

#### Repository-Wide Analysis
```
You: List missing patches across Default repository

Claude: Analyzing all IPs in Default repository...
[Returns: Up to 50 IPs with patch counts and details]
```

#### Windows KB-Specific Query
```
You: Show missing Windows updates for 192.168.5.20

Claude: Analyzing Windows patches for 192.168.5.20...
[Returns: Missing KB articles with vulnerability counts and URLs]
```

#### Filter by Asset Criticality
```
You: Show missing patches for critical assets (ACR 8-10)

Claude: Finding high-risk IPs with missing patches...
[Returns: Critical assets sorted by patch count]
```

### What You Get Back

#### Universal Mode Response
```json
{
  "ok": true,
  "mode": "universal",
  "total_affected_ips": 1,
  "patches_by_ip": [
    {
      "ip": "10.1.20.10",
      "hostname": "win7-office2010.labnet.local",
      "os": "Microsoft Windows 7 Professional Service Pack 1",
      "repository": "Default",
      "total_missing_patches": 41,
      "microsoft_kbs": [
        {
          "kb_id": "KB5025279",
          "vulnerability_count": 85
        },
        {
          "kb_id": "KB5026361",
          "vulnerability_count": 12
        }
      ],
      "third_party": [
        {
          "software": "Google Chrome < 113.0.5672.63"
        },
        {
          "software": "VMware Tools 10.x / 11.x < 12.2.0"
        }
      ]
    }
  ],
  "cache_status": "HIT"
}
```

#### Windows Mode Response
```json
{
  "ok": true,
  "mode": "windows",
  "total_affected_ips": 1,
  "patches_by_ip": [
    {
      "ip": "192.168.5.20",
      "hostname": "bg520-1.demo.io",
      "os": "Windows 10",
      "repository": "Default",
      "total_missing_kbs": 23,
      "missing_kbs": [
        {
          "kb_id": "KB4025252",
          "url": "https://support.microsoft.com/kb/4025252"
        },
        {
          "bulletin_id": "MS16-087",
          "type": "legacy_ms_bulletin"
        }
      ]
    }
  ]
}
```

### Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `mode` | string | `"universal"` (default) or `"windows"` | No |
| `filters` | dict | Filter parameters (see below) | No |

### Supported Filters

All 74+ universal filters are supported. Common examples:

#### Asset Filters
```python
filters = {
    "ip": "10.1.20.10",              # Specific IP
    "repository": "Default",          # Repository name (auto-resolves to ID)
    "asset_criticality": "8-10",      # High-risk assets only
    "dns_name": "webserver01"         # Hostname filter
}
```

#### Vulnerability Filters
```python
filters = {
    "severity": "critical",           # critical/high/medium/low/info
    "operating_system": "Windows 10", # OS filter
    "first_seen": "1704067200",       # Unix timestamp
    "last_seen": "1735689600"         # Unix timestamp
}
```

### Key Features

- **Two Detection Modes**: Universal (all OS) or Windows-specific
- **Smart Parsing**: Extracts KB IDs, third-party software, vulnerability counts
- **Repository Name Resolution**: Auto-converts "Default" → ID 9
- **Token Efficient**: 700-20,000 tokens depending on result size
- **Fast Caching**: 240s (4 minute) cache for quick repeated queries
- **Pagination**: Returns up to 50 results per query

### Pro Tips

1. **Single-IP queries recommended**: In 1000+ IP environments, scope queries to specific IPs/repositories to avoid token explosion
2. **Use filters to narrow scope**: Apply `asset_criticality` or `repository` filters to focus on high-risk assets
3. **Check scan policy**: Tool requires plugin output to be stored (scan policy setting)
4. **Repository name resolution**: Use repository name directly ("Default"), no need to look up ID
5. **Empty results validation**: Tool distinguishes "no patches found" vs "IP/repo doesn't exist"

### Example Workflows

#### Workflow 1: Single Server Audit
```python
# Step 1: Profile the server
profile = tsc_profile_ip_efficient("10.1.20.10")

# Step 2: Get missing patches
patches = tsc_list_missing_patches(
    mode="universal",
    filters={"ip": "10.1.20.10"}
)

# Step 3: Get full vulnerability details
vulns = tsc_list_vulns_by_ip_full(
    "10.1.20.10",
    filters={"severity": "critical"}
)
```

#### Workflow 2: Repository-Wide Compliance
```python
# Step 1: Find all IPs in repository
ips = tsc_list_ips(repository="Default")

# Step 2: Get missing patches for repository
patches = tsc_list_missing_patches(
    mode="universal",
    filters={"repository": "Default"}
)

# Step 3: Filter to critical assets only
critical_patches = tsc_list_missing_patches(
    mode="universal",
    filters={
        "repository": "Default",
        "asset_criticality": "8-10"
    }
)
```

#### Workflow 3: Windows Patch Management
```python
# Step 1: Find all Windows 10 hosts
win10_ips = tsc_list_ips(
    repository="Default",
    filters={"operating_system": "Windows 10"}
)

# Step 2: Get missing Windows updates
patches = tsc_list_missing_patches(
    mode="windows",
    filters={
        "repository": "Default",
        "operating_system": "Windows 10"
    }
)
```

### Known Limitations

1. **Pagination**: Returns max 50 results per query
   - Workaround: Use IP or repository filters to scope queries
2. **Plugin Output Required**: Tool requires `pluginText` field to be stored
   - If scan policy has "Store plugin output" disabled, returns 0 results
3. **Repository Name Resolution**: Repository must exist in system
   - Tool provides list of available repositories when name not found

### Performance Benchmarks

| Query Type | Token Usage | Cache | Response Time |
|------------|-------------|-------|---------------|
| Single IP | 700-1,200 | 240s | <1s cached, 2s fresh |
| Repository (50 IPs) | 15,000-20,000 | 240s | <1s cached, 3-5s fresh |
| High ACR (10-30 IPs) | 5,000-10,000 | 240s | <1s cached, 2-4s fresh |

### Troubleshooting

**Problem**: Tool returns 0 results for known vulnerable IP  
**Solution**: Check scan policy has "Store plugin output" enabled

**Problem**: Repository not found error  
**Solution**: Use `tsc_list_domains()` or check error message for available repositories

**Problem**: Token usage too high (>50,000 tokens)  
**Solution**: Add `ip` or `repository` filter to scope query, avoid wide-open queries in large environments

---

## Universal Filter Framework

All tools support 74+ filters via the `filters` dict parameter. Filters are consistent across all tools.

### Common Filters

#### Scoring Filters (Range Format)
```python
filters = {
    "asset_criticality": "7-10",     # ACR range (0-10)
    "vpr_score": "8-10",             # VPR range (0-10)
    "aes_score": "600-1000",         # AES range (0-1000)
    "cvss_v3_base_score": "7-10",    # CVSS v3 range
    "epss_score": "0.5-1.0"          # EPSS range (0-1)
}
```

⚠️ **Important**: Use range format `"min-max"`, NOT operators like `">7"` or `">=8"`.

#### Vulnerability Filters
```python
filters = {
    "severity": "critical",           # critical/high/medium/low/info
    "exploit_available": "Yes",       # Yes/No
    "family": "Windows",              # Plugin family
    "plugin_id": "156013",           # Specific plugin
    "cve": "CVE-2021-44228"          # CVE ID
}
```

#### Asset Filters
```python
filters = {
    "repository": "Production",       # Repository name or ID
    "ip": "10.1.20.10",              # Specific IP
    "dns_name": "webserver01"        # Hostname
}
```

#### Network Filters
```python
filters = {
    "port": 443,                      # Port number
    "protocol": "TCP"                 # TCP/UDP
}
```

#### Temporal Filters (Unix timestamps)
```python
filters = {
    "first_seen": "1704067200",      # First detection
    "last_seen": "1735689600"        # Last detection
}
```

### Complete Filter Reference

For complete list of all 74+ filters, see: [FILTER_FORMAT_REFERENCE.md](FILTER_FORMAT_REFERENCE.md)

### Filter Examples

**Critical assets with exploitable vulns:**
```python
tsc_list_ips(
    repository="Production",
    filters={
        "asset_criticality": "7-10",
        "severity": "high",
        "exploit_available": "Yes"
    }
)
```

**Windows hosts with specific CVE:**
```python
tsc_list_vulns_by_cve(
    "CVE-2021-44228",
    filters={
        "operating_system": "Windows",
        "repository": "Production"
    }
)
```

**High VPR vulnerabilities with patches:**
```python
tsc_list_vulns_by_ip_full(
    "10.1.20.10",
    filters={
        "vpr_score": "8-10",
        "patch_available": "Yes"
    }
)
```

---

## Performance & Caching

### Token Efficiency

All tools are optimized to minimize LLM token usage:

| Tool | Token Usage | Savings | vs Raw API |
|------|-------------|---------|------------|
| tsc_profile_ip_efficient | ~2,500 | 83% | ~15,000 |
| tsc_list_vulns_by_ip_summary | ~700 | 88% | ~6,000 |
| tsc_list_vulns_by_ip_full | ~5,000 | 58% | ~12,000 |
| tsc_list_ips | ~400-3,700 | 85% | ~5,000-25,000 |
| tsc_list_vulns_by_cve | ~800-1,500 | 85% | ~10,000 |

### Cache Strategy

Intelligent caching reduces API calls and improves response times:

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Vulnerability data | 180s (3 min) | Changes frequently during scans |
| IP lists | 120s (2 min) | Moderate change rate |
| CVE searches | 240s (4 min) | Relatively stable |
| Host software/services | 300s (5 min) | Rarely changes |
| Static metadata | 300s (5 min) | Infrequent updates |

### Response Times

| Scenario | Response Time | Notes |
|----------|---------------|-------|
| Cache hit | <1s | Instant response from cache |
| Fresh query (simple) | 1-2s | Single API call |
| Fresh query (complex) | 2-4s | Multiple API calls |
| Large dataset | 3-5s | Pagination or aggregation |

---

## Best Practices

### 1. Start with Summary Tools

Use lightweight summary tools before pulling full details:

```bash
# ✅ Efficient workflow
1. tsc_list_vulns_by_ip_summary → Get counts
2. If counts are high → tsc_list_vulns_by_ip_full → Get details

# ❌ Inefficient workflow
1. tsc_list_vulns_by_ip_full → Always pulls full records (wasteful)
```

### 2. Apply Filters Early

Narrow results with filters to reduce token usage:

```python
# ✅ Good: Filter for critical vulns only
tsc_list_vulns_by_ip_full(
    "10.1.20.10",
    filters={"severity": "critical"},
    end_offset=10
)

# ❌ Wasteful: Pull all 500 vulnerabilities
tsc_list_vulns_by_ip_full("10.1.20.10")
```

### 3. Use Pagination

Request small batches for faster responses:

```python
# ✅ Good: Request first 20 results
tsc_list_vulns_by_ip_full("10.1.20.10", end_offset=20)

# ❌ Slower: Request 200 results at once
tsc_list_vulns_by_ip_full("10.1.20.10", end_offset=200)
```

### 4. Leverage Caching

Be aware of cache TTLs for your workflow:

- **Real-time investigation** (1-5 min): Cache is fresh, responses are instant
- **Continuous monitoring** (>5 min): Cache expires, fresh data fetched
- **Reporting** (periodic): Cache ensures consistent data within TTL window

### 5. Natural Language

Use conversational commands with your AI assistant:

```bash
# ✅ Natural language (Claude understands)
"Profile IP 10.1.20.10"
"Show me critical vulnerabilities for 192.168.1.100"
"Do we have CVE-2021-44228?"

# ❌ No need for technical syntax
tsc_profile_ip_efficient("10.1.20.10")
```

### 6. Combine Tools

Use multiple tools together for comprehensive analysis:

```bash
# Workflow example
1. "Do we have CVE-2021-44228?"
   → tsc_list_vulns_by_cve identifies affected IPs

2. "Profile IP 10.1.20.10"
   → tsc_profile_ip_efficient gets host details

3. "Show vulnerabilities for 10.1.20.10"
   → tsc_list_vulns_by_ip_full gets remediation details
```

### 7. Scoring Filter Format

Always use range format for scoring filters:

```python
# ✅ Correct
filters={"asset_criticality": "7-10"}
filters={"vpr_score": "8-10"}
filters={"aes_score": "600-1000"}

# ❌ Incorrect (not supported)
filters={"asset_criticality": ">7"}
filters={"vpr_score": ">=8"}
```

---

## Support & Documentation

### Additional Resources

- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Architecture and design decisions
- **[FILTER_FORMAT_REFERENCE.md](FILTER_FORMAT_REFERENCE.md)** - Complete filter reference (74+ filters)
- **[TOOLS_ROADMAP.md](TOOLS_ROADMAP.md)** - Future features and development roadmap
- **[README.md](README.md)** - Installation and setup instructions

### Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/ABMJ/tenable-sc-mcp-server/issues)
- **Documentation**: All tools have detailed docstrings with examples
- **MCP Resources**: Use `tenable-sc://filters/reference` for filter documentation

### Version Information

- **Current Version**: v1.3.0.1
- **Last Updated**: 2026-06-20
- **API Version**: Tenable.sc REST API 5.x+
- **MCP Protocol**: 1.0+

---

**Document Version**: 1.0  
**Status**: Production Ready  
**Maintained By**: ABMJ  
**License**: GPL-3.0
