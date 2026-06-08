# Tenable.sc Convenience Tools - Roadmap & User Guide

**Status**: Week 1 - Session 1.5 Complete (4 tools operational, Tool 4 fully validated)  
**Last Updated**: 2026-06-08 (Session 1.5 - Tool 4 Complete)

---

## 🎯 Quick Status

**Completed**: 4/25 tools (16%) + Modular Architecture  
**Current Phase**: Week 1 Session 1.5 (Tool 4) - ✅ Complete & Validated  
**Next Session**: Week 1 Session 1.6 - Implement Tool 5 (`tsc_list_vulns_by_cve`) in `tools/vulnerability_lookup.py`

**Validated Performance (Tool 4 - New):**
- Cache hit rate: Working correctly (120s TTL)
- Token efficiency: 400-3,700 tokens (payload-dependent)
- Response time: <1s cached, 1-3s fresh
- All 4 test scenarios: ✅ PASSING

---

## 📋 DOCUMENT PURPOSE

This document serves **two critical functions**:

1. **PART 1: USER GUIDE** - Professional documentation for completed tools (Tools 1, 2a, 2b, 4) with:
   - Clear "When to Use" scenarios for each tool
   - Practical usage examples with natural language commands
   - Complete descriptions of what data you get back
   - Performance metrics and best practices
   - Suitable for non-technical users and security teams

2. **PART 2: DEVELOPMENT ROADMAP** - Detailed specifications for pending tools (Tools 5-26) organized by Week/Session with:
   - Clear purpose and use cases
   - Token budgets and cache TTL targets
   - Module assignments and technical implementation notes
   - Designed for LLM-assisted development sessions

**For New Development Sessions**: Review this document + latest `week1_session_X_handoff.md` file to resume immediately.

---

# 📚 PART 1: USER GUIDE (COMPLETED TOOLS)

## ✅ Tool 1: `tsc_profile_ip_efficient` - Complete IP Security Profile

**Status**: ✅ Production Ready | **Token Savings**: 83-90% | **Cache**: 180-300s | **Module**: `tools/ip_profiling.py`

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
profile IP 10.1.20.10

# Full example with context
use tenable-sc to profile IP 10.1.20.10 efficiently, then show me cache stats
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
- **Speed**: <1 second if cached, 1-3 seconds fresh query
- **Data Freshness**: Vulnerability data refreshes every 3 minutes, static data every 5 minutes

### Best Use Cases
- Initial security assessment of unknown hosts
- Compliance audits requiring complete host documentation
- Asset inventory verification
- Credential scan validation (checking if authenticated scans are working)
- Pre-patch planning (knowing what's installed before changes)

---

## ✅ Tool 2a: `tsc_list_vulns_by_ip_summary` - Quick Vulnerability Count

**Status**: ✅ Production Ready | **Token Savings**: 88-92% | **Cache**: 180s | **Module**: `tools/vulnerability_lookup.py`

### What This Tool Does
Gets vulnerability counts by severity for an IP address without pulling full details. Perfect for quick checks and determining scope before deeper investigation.

### When to Use This Tool
- **Dashboard Reports**: "How many critical vulnerabilities do we have on this server?"
- **Quick Assessment**: "Is this IP clean or does it have issues?"
- **Scoping**: "How many vulns before I pull full details?" (avoid overloading with data)
- **Executive Summary**: "Give me the vulnerability breakdown for our web server"
- **Triage**: "Which servers have the most critical issues?" (check multiple IPs quickly)

### How to Use
```bash
# Get all vulnerability counts
get vulnerability summary for IP 10.1.20.10

# Filter for specific severity
get critical vulnerability count for IP 10.1.20.10

# Full example with cache
use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical, then show me cache stats
```

### What You Get Back
- **Total Count**: Total number of vulnerabilities found
- **Breakdown by Severity**:
  - Critical: [count]
  - High: [count]
  - Medium: [count]
  - Low: [count]
  - Info: [count]
- **Applied Filters**: Summary of any filters you used

### Available Filters (10)
- `severity`: Critical/High/Medium/Low/Info or 0-4
- `exploit_available`: Yes/No
- `first_seen`: Unix timestamp
- `last_seen`: Unix timestamp
- `family`: Plugin family (e.g., "Windows")
- `vpr_score`: Vulnerability Priority Rating score
- `plugin_id`: Specific Nessus plugin ID
- `cve`: CVE identifier
- `port`: Port number
- `protocol`: TCP/UDP

### Performance
- **Tokens Used**: ~700 tokens (vs ~6,000 with full details) = **88% reduction**
- **Speed**: <1 second cached, 1-2 seconds fresh
- **Data Freshness**: Refreshes every 3 minutes

### Best Use Cases
- Quick security posture checks
- Dashboard metrics and reporting
- Determining scope before pulling full vulnerability details
- Comparing multiple IPs quickly (check 10 IPs in seconds vs minutes)
- Executive briefings requiring summary statistics only

---

## ✅ Tool 2b: `tsc_list_vulns_by_ip_full` - Detailed Vulnerability Records

**Status**: ✅ Production Ready | **Token Savings**: 58-75% | **Cache**: 180s | **Pagination**: 10-200 | **Module**: `tools/vulnerability_lookup.py`

### What This Tool Does
Gets complete vulnerability details with full metadata for an IP address. Returns all the information needed for remediation planning including plugin details, scoring, exploit status, and solution steps.

### When to Use This Tool
- **Remediation Planning**: "What are the details on these critical vulnerabilities so I can fix them?"
- **Ticketing**: "I need full vuln data to create tickets for my team"
- **Investigation**: "Show me everything about the high-risk vulnerabilities on this server"
- **Compliance Reports**: "Give me detailed vulnerability information for our audit"
- **Risk Analysis**: "Which vulnerabilities have public exploits available?"

### How to Use
```bash
# Get all critical vulnerabilities
list all critical vulnerabilities for IP 10.1.20.10

# First 10 records only
use tenable-sc to list all critical vulnerabilities for IP 10.1.20.10 using tsc_list_vulns_by_ip_full, show first 10 records

# With cache stats
use tenable-sc to list all critical vulnerabilities for IP 10.1.20.10 using tsc_list_vulns_by_ip_full, show first 10 records, then show me cache stats

# Filter by multiple criteria
show vulnerabilities for IP 10.1.20.10 with severity high, exploit available, port 443
```

### What You Get Back (Per Vulnerability)
- **Identity**: Plugin ID, plugin name, plugin family
- **Severity**: Severity level (Critical/High/Medium/Low/Info)
- **Risk Scoring**: CVSS v3 score, VPR score, EPSS probability
- **Exploit Status**: Exploit available (Yes/No), exploit frameworks (Metasploit, etc.)
- **CVE IDs**: Associated CVE identifiers
- **Network**: Port number, protocol (TCP/UDP)
- **Timeline**: First seen, last seen timestamps
- **Remediation**: Synopsis (200 chars), solution (200 chars), see_also URLs
- **Patch Info**: Patch publication date, vulnerability publication date
- **Mitigation**: Mitigation status

### Available Filters (15)
**Common Filters (10)**:
- `severity`, `exploit_available`, `first_seen`, `last_seen`, `family`
- `vpr_score`, `plugin_id`, `cve`, `port`, `protocol`

**Additional Filters (5)**:
- `cvss_v3_base_score`: CVSS v3 base score filter
- `epss_score`: EPSS exploitation probability score
- `patch_published`: Filter by patch publication date
- `vuln_published`: Filter by vulnerability publication date
- `mitigated_status`: Filter by mitigation status

### Pagination Controls
- **Default**: Returns records 0-50 (50 records)
- **Maximum**: 200 records per request
- **Parameters**: `start_offset` and `end_offset`
- **Example**: `start_offset=0, end_offset=100` returns first 100 records

### Performance
- **Tokens Used**: ~5,000 tokens for 50 records (vs ~12,000 unfiltered) = **58% reduction**
- **Speed**: <1 second cached, 2-4 seconds fresh
- **Data Freshness**: Refreshes every 3 minutes
- **Best Practice**: Start with 50 records, paginate if needed

### Best Use Cases
- Remediation planning and prioritization
- Creating detailed security tickets for IT teams
- Compliance reporting with full vulnerability documentation
- Risk analysis and exploit mapping
- Investigation of specific vulnerabilities requiring full context

---

## ✅ Tool 4: `tsc_list_ips` - IP Discovery & Asset Enumeration

**Status**: ✅ Production Ready | **Token Range**: 400-3,700 | **Cache**: 120s | **Module**: `tools/asset_discovery.py`

### What This Tool Does
Lists all IP addresses in a repository or asset group with powerful filtering options. Also supports reverse lookup to find which repositories and asset groups contain a specific IP address.

### When to Use This Tool
- **Asset Discovery**: "Show me all IPs in our production network"
- **Scope Building**: "List all IPs in Windows Hosts group for patching"
- **High-Risk Identification**: "Show me all IPs with asset criticality >8"
- **Reverse Lookup**: "Which asset groups contain this suspicious IP?"
- **Subnet Enumeration**: "List all IPs we're actively scanning"
- **CMDB Sync**: "Export all IPs with full metadata for our asset database"

### How to Use

#### Basic IP Listing
```bash
# List IPs in repository
list all IPs in repository "Default"

# List IPs in asset group
list IPs in asset group "Windows Hosts"

# Filter by asset criticality
list IPs in repository "Default" with asset criticality >7

# Get full details
list IPs in asset group "Production Servers" with full details
```

#### Reverse Lookup
```bash
# Find where an IP exists
find which repositories and asset groups contain IP 10.1.20.10

# Using test format with visual icons
I am testing tsc_list_ips to find which repositories and asset groups contain IP 10.1.20.10
```

#### Developer Test Format (Use Visual Icons)
When testing this tool, use the standardized format with visual icons for clear results:

```
I am testing tsc_list_ips to [your test scenario]. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about cache and token performance]
📦 RESULT: [your expected data]
```

### What You Get Back

**Minimal Mode** (default):
- List of IP addresses only
- Total IP count
- Repository or asset group name

**With include_details=True**:
- IP address
- DNS hostname
- NetBIOS name
- MAC address
- Asset UUID
- Operating system
- ACR score (0-10 scale)
- Repository name

**Reverse Lookup Mode** (when using `ip` parameter):
- List of repositories containing the IP
- List of asset groups containing the IP (only groups where IP actually exists)
- Total membership count

### Available Filters (55+)
This tool supports all Tenable.sc analysis filters:
- **Asset Filters**: `asset_criticality` (ACR score >7, >=8, etc.), `uuid`, `dns_name`
- **Time Filters**: `first_seen`, `last_seen` (Unix timestamps)
- **Risk Scoring**: `vpr_score`, `cvss_v3_base_score`
- **Vulnerability Filters**: `severity` (Critical/High/Med/Low), `exploit_available` (Yes/No), `plugin_id`, `family`
- **Network Filters**: `port`, `protocol` (TCP/UDP)
- Plus 45+ additional Tenable.sc analysis filters

**Special Feature**: Asset Criticality operators automatically convert (e.g., `>7` becomes `7.1-10` range to include decimals)

### Performance
- **Tokens Used**: 400-3,700 tokens depending on result size
  - Large datasets (800+ IPs): ~3,500 tokens
  - Medium datasets (100-200 IPs): ~1,200 tokens
  - Reverse lookup: ~500 tokens
  - With full details: ~2,400 tokens
- **Speed**: <1 second cached, 1-3 seconds fresh
- **Data Freshness**: Refreshes every 2 minutes
- **Note**: Token count depends on payload size. Real benefit is cache speed and API rate limit savings.

### Best Use Cases
- Asset discovery and inventory management
- Building scan target lists
- Finding high-risk assets (ACR >8 filters)
- Asset group membership verification
- Reverse lookup to find IP locations
- CMDB synchronization and export
- Subnet enumeration

### Technical Notes for Developers
- Uses `sumip` analysis tool for IP enumeration
- Uses `sumasset` tool for reverse lookup of asset group membership
- Automatic name-to-ID resolution for repositories and asset groups
- Asset filter format: `{"id": "3", "name": "Windows Hosts"}` (object with both ID and name)
- Repository filter format: `[{"id": "9"}]` (array with string ID)
- ACR operator conversion: `>7` → `7.1-10`, `>=7` → `7.0-10` (handles decimals correctly)
- Reverse lookup filters results by `total > 0` to show only actual memberships
- Gracefully handles missing data (returns empty lists, not errors)

### Bugs Fixed in Session 1.5
1. ✅ Added nested `{"query": {...}}` wrapper for API compatibility (HTTP 403 fix)
2. ✅ Fixed asset filter structure to use object format not array
3. ✅ Fixed ACR field mapping to `acrScore` (0-10) instead of `score` (0-4000+)
4. ✅ Fixed ACR operator conversion to include decimal ranges (>7 → 7.1-10 not 8-10)
5. ✅ Fixed reverse lookup to use correct `sumasset` analysis tool
6. ✅ Added filtering to show only asset groups where `total > 0`
7. ✅ Validated all scenarios with real Tenable.sc production data

---

# 🗓️ PART 2: DEVELOPMENT ROADMAP (PENDING TOOLS)

---

## 📅 WEEK 1 - CORE FOUNDATION (2 TOOLS REMAINING)

### ⏳ Session 1.6: Tool 5 - CVE Search (NEW - HIGH PRIORITY) 🆕

#### `tsc_list_vulns_by_cve`

**Status**: ⏳ Pending | **Token Budget**: 1,000-2,000 | **Cache TTL**: 240s | **Estimated**: 2h

**Purpose:**
Search for specific CVE across entire infrastructure. Emergency outbreak response tool.

**Planned Features:**
- Search by CVE ID (e.g., "CVE-2021-44228")
- List all affected IPs
- Show severity per IP
- Include plugin name and plugin ID
- **Summarized remediation steps with references**
- Plugin output excerpts
- **Full plugin output available on request** (may be 500+ lines)

**Output:**
```json
{
  "cve": "CVE-2021-44228",
  "total_affected_ips": 47,
  "plugin_id": "156013",
  "plugin_name": "Apache Log4j < 2.15.0 Remote Code Execution",
  "affected_assets": [
    {
      "ip": "10.1.20.10",
      "hostname": "webserver01",
      "severity": "Critical",
      "port": 8080,
      "protocol": "TCP"
    }
  ],
  "remediation_summary": {
    "steps": ["Upgrade to Log4j 2.17.1 or later", "Apply vendor patches"],
    "references": ["https://logging.apache.org/log4j/2.x/security.html"],
    "vendor_advisories": ["Apache Security Advisory"]
  },
  "plugin_output_available": true
}
```

**Use Cases:**
- Emergency CVE outbreak response (Log4Shell, ProxyLogon, etc.)
- Security bulletin tracking
- Incident response - "Do we have CVE-XXXX-XXXX?"
- Patch verification after remediation

**Implementation Notes:**
- Use `listvuln` analysis tool with `cve` filter
- Cache TTL: 240s (4 minutes) - balance freshness vs performance
- Token budget: 1,000-2,000 tokens
- Parse plugin output for remediation section
- Offer full plugin output via optional parameter `include_full_output=true`
- No limit on number of affected IPs returned
- **Module**: `tools/vulnerability_lookup.py`

---

### ⏳ Session 1.7: Tool 6 - Missing Patches

#### `tsc_list_missing_patches_windows`

**Status**: ⏳ Pending | **Token Budget**: 2,000-4,000 | **Cache TTL**: 240s | **Estimated**: 2h

**Purpose:**
MS bulletin-based patch gap analysis for Windows systems.

**Planned Features:**
- List missing MS patches by bulletin ID
- Filter by severity (critical/important/moderate)
- Filter by release date
- Group by bulletin or by IP
- Include affected IPs per bulletin

**Use Cases:**
- Patch compliance reporting
- MS bulletin tracking
- Windows update verification
- Remediation prioritization
- **Module**: `tools/scanning.py`

---

### ⏳ Session 1.8: Tool 7 - Scan Status

#### `tsc_scan_status`

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 60s | **Estimated**: 2h

**Purpose:**
Real-time scan monitoring with filters (time, launcher, status).

**Planned Features:**
- List active/completed/failed scans
- Filter by scan status (running/completed/error)
- Filter by time range (last 24h, 7d, 30d)
- Filter by scanner/launcher
- Show scan progress percentage
- Include scan duration and target count

**Use Cases:**
- Monitor active scans
- Track scan completion
- Identify stuck/failed scans
- Scan performance analysis

**Implementation Notes:**
- Real-time data - short TTL (60s)
- Use `/scan` endpoint with filters
- Include scan result UUID for drill-down
- **Module**: `tools/scanning.py`

---

## 📅 WEEK 2 - EXTENDED FEATURES (9 TOOLS)

### ⏳ Session 2.1: Tool 8 - Compliance Status

#### `tsc_compliance_status_by_ip`

**Token Budget**: 3,000-5,000 | **Cache TTL**: 300s | **Estimated**: 3h | **Module**: `tools/compliance.py`

**Purpose:** Summary + failed compliance checks with remediation guidance

**Frameworks Supported:** PCI-DSS, NIST, CIS, ISO 27001, HIPAA (generic compliance tool)

---

### ⏳ Session 2.2: Tool 9 - Resources Status (Admin)

#### `tsc_resources_status`

**Token Budget**: 1,500-3,000 | **Cache TTL**: 60s/600s | **Estimated**: 3h | **Admin Only** | **Module**: `tools/admin/resources.py`

**Purpose:** Nessus/NNM/WAS/Proxy status with force_refresh flag

---

### ⏳ Session 2.3: Tool 10 - Open Ports

#### `tsc_list_ports`

**Token Budget**: 1,500-3,000 | **Cache TTL**: 240s | **Estimated**: 2h | **Module**: `tools/network.py`

**Purpose:** List open ports with combined scanner + vulnerability data

**Port Scanner Plugin IDs:**
- 0: Open Port
- 11219: Nessus SYN scanner
- 14272: Netstat Portscanner (SSH)
- 10335: Netstat Portscanner (WMI)
- 22964: Service Detection

---

### ⏳ Session 2.4: Tools 11-12 - Software & Services

#### `tsc_list_software`

**Token Budget**: 2,000-4,000 | **Cache TTL**: 300s | **Estimated**: 1.5h | **Module**: `tools/inventory.py`

**Purpose:** List installed software with full filtering (kept for performance despite overlap with IP profile)

---

#### `tsc_list_services`

**Token Budget**: 2,000-4,000 | **Cache TTL**: 300s | **Estimated**: 1.5h | **Module**: `tools/inventory.py`

**Purpose:** List running services with full filtering (kept for performance despite overlap with IP profile)

---

### ⏳ Session 2.5: Tool 13 - Credential Audit

#### `tsc_credential_audit`

**Token Budget**: 2,000-3,000 | **Cache TTL**: 240s | **Estimated**: 2h | **Module**: `tools/authentication.py`

**Purpose:** Credential success/failure audit per IP using plugin 19506 + auth plugins

**Authentication Plugin IDs:**
- 19506: Nessus Scan Information (master)
- 21745: Authentication Failure - Local Checks Not Run
- 10394: Microsoft Windows SMB Log In Possible
- 10396: SSH Authorization Successful
- 102094: SSH Commands Not Available
- 24786: Nessus Windows Scan Not Performed with Admin Privileges

**Strategy:** Query plugin 19506 + auth failure plugins to correlate success/failure per protocol

---

### ⏳ Session 2.6: Tool 14 - IPs by Vulnerability

#### `tsc_list_ips_by_vuln`

**Token Budget**: 2,000-4,000 | **Cache TTL**: 240s | **Estimated**: 2h | **Module**: `tools/vulnerability_lookup.py`

**Purpose:** Reverse lookup - list IPs affected by specific vulnerability (plugin ID or CVE)

---

### ⏳ Session 2.7: Tool 15 - CVE List per IP (NEW) 🆕

#### `tsc_list_cves_by_ip`

**Status**: ⏳ Pending | **Token Budget**: 800-1,500 | **Cache TTL**: 180s | **Estimated**: 1.5h | **Module**: `tools/vulnerability_lookup.py`

**Purpose:**
Lightweight CVE-only listing for an IP. Complements `tsc_list_vulns_by_ip_full` (which shows all fields).

**Planned Features:**
- List all CVE IDs affecting an IP
- Optional severity filter
- Optional exploit availability filter
- Sorted by severity (descending)

**Output:**
```json
{
  "ip": "10.1.20.10",
  "total_cves": 183,
  "cves": [
    {
      "cve_id": "CVE-2021-44228",
      "severity": "Critical",
      "plugin_id": "156013",
      "exploit_available": "Yes"
    }
  ]
}
```

**Use Cases:**
- "Just show me the CVE IDs for this server"
- Quick CVE inventory check
- Export CVE list for ticketing systems
- Lightweight alternative to full vulnerability details

**Token Efficiency:**
~800-1,500 tokens (vs 5,000+ for full details) = **70-85% reduction**

---

### ⏳ Session 2.8: Tool 16 - Scan Results (NEW) 🆕

#### `tsc_list_scan_results`

**Status**: ⏳ Pending | **Token Budget**: 2,000-3,000 | **Cache TTL**: 180s | **Estimated**: 2h | **Module**: `tools/scanning.py`

**Purpose:**
Filter scan results by date, status, repository. Better operational visibility.

**Planned Features:**
- Filter by scan status (completed/running/error/stopped)
- Filter by date range (last 24h, 7d, 30d, custom)
- Filter by repository
- Filter by scanner
- Show scan duration, target count, findings count
- Include scan result UUID for drill-down

**Output:**
```json
{
  "total_results": 47,
  "results": [
    {
      "scan_name": "Weekly PCI Scan",
      "status": "completed",
      "start_time": "2026-06-05T10:00:00Z",
      "end_time": "2026-06-05T12:30:00Z",
      "duration": "2h 30m",
      "targets": 256,
      "vulnerabilities_found": 1847,
      "repository": "PCI Assets",
      "scanner": "Scanner-01",
      "result_uuid": "abc123..."
    }
  ]
}
```

**Use Cases:**
- "Show all failed scans from last week"
- "Get all scan results for PCI repository"
- Scan audit trail
- Performance analysis (scan duration trends)

---

### ⏳ Session 2.9: Tools 17-18 - IP by Repo & OS Detection

#### `tsc_list_ips_by_repo`

**Token Budget**: 500-1,000 | **Cache TTL**: 300s | **Estimated**: 1h | **Module**: `tools/asset_discovery.py`

**Purpose:** List all IPs in a repository or asset group (kept for performance despite overlap)

---

#### `tsc_get_os_by_ip`

**Token Budget**: 500-1,000 | **Cache TTL**: 300s | **Estimated**: 1h | **Module**: `tools/asset_discovery.py`

**Purpose:** Get OS details per IP/asset (kept for performance despite overlap with IP profile)

---

## 📅 WEEK 3 - COMPLETION & POLISH (7 TOOLS + 3 SESSIONS)

### ⏳ Session 3.1: Tool 19 - Bulk IP Profiling (NEW) 🆕

#### `tsc_profile_ips_bulk`

**Status**: ⏳ Pending | **Token Budget**: 5,000-10,000 | **Cache TTL**: 180s | **Estimated**: 2h | **Module**: `tools/ip_profiling.py`

**Purpose:**
Profile multiple IPs (10-50+) in one efficient query. Better caching, reduced round trips.

**Planned Features:**
- Accept list of IPs (no limit on quantity per user requirement)
- Return same data structure as `tsc_profile_ip_efficient`
- Parallel query execution with shared cache
- Progress indicator for large batches
- Batch optimization for token efficiency

**Output:**
```json
{
  "total_ips": 50,
  "profiles": [
    {
      "ip": "10.1.20.10",
      "hostname": "webserver01",
      "os": "Windows Server 2019",
      "vulnerabilities": {"critical": 5, "high": 23},
      ...
    }
  ],
  "cache_performance": {
    "cache_hits": 43,
    "cache_misses": 7,
    "hit_rate": "86%"
  }
}
```

**Use Cases:**
- After getting IP list, profile them all at once vs one-by-one
- Subnet-wide profiling
- Asset group bulk assessment
- Export for CMDB/asset management systems

**Implementation Notes:**
- No hard limit on IP count (per user requirement: "there should be no limit")
- Smart batching for very large requests (500+ IPs)
- Warn if request >100 IPs (token budget consideration)
- Cache per-IP for maximum hit rates

**Token Efficiency:**
~100 tokens per IP with caching (vs 2,500 per individual call) = **96% reduction** at scale

---

### ⏳ Session 3.2: Tools 20-21 - ACR Risk Scoring

#### `tsc_list_acr_by_ip`

**Token Budget**: 1,000-2,000 | **Cache TTL**: 300s | **Estimated**: 1h | **Module**: `tools/risk_scoring.py`

**Purpose:** ACR (Asset Criticality Rating) scores per IP

---

#### `tsc_list_ips_by_acr_range`

**Token Budget**: 1,000-2,000 | **Cache TTL**: 300s | **Estimated**: 1h | **Module**: `tools/risk_scoring.py`

**Purpose:** List IPs within ACR value/range (e.g., score >= 8)

---

### ⏳ Session 3.3: Tools 22-23 - Asset Intelligence

#### `tsc_asset_group_membership`

**Token Budget**: 500-1,000 | **Cache TTL**: 600s | **Estimated**: 1h | **Module**: `tools/asset_discovery.py`

**Purpose:** List all asset groups an IP belongs to (kept for performance despite overlap with IP profile)

---

#### `tsc_top_vulnerable_assets`

**Token Budget**: 1,000-2,000 | **Cache TTL**: 180s | **Estimated**: 1h | **Module**: `tools/asset_discovery.py`

**Purpose:** Most vulnerable IPs ranked by severity count

---

### ⏳ Session 3.4: Tools 24-25 - Admin Monitoring

#### `tsc_plugin_update_status`

**Token Budget**: 500-1,000 | **Cache TTL**: 600s | **Estimated**: 1h | **Admin Only** | **Module**: `tools/admin/plugins.py`

**Purpose:** Plugin feed status monitoring

---

#### `tsc_license_usage`

**Token Budget**: 500-1,000 | **Cache TTL**: 1800s | **Estimated**: 1h | **Admin Only** | **Module**: `tools/admin/licensing.py`

**Purpose:** License usage statistics

---

### ⏳ Session 3.5: Tool 26 - Repository Status (MERGED) 🔄

#### `tsc_repo_status`

**Token Budget**: 2,000-3,000 | **Cache TTL**: 1800s | **Estimated**: 1.5h | **Admin Only** | **Module**: `tools/admin/repositories.py`

**Purpose:** Combined repository tool - config + utilization + capacity + trending

**Note:** Replaces two separate tools (`tsc_repo_config_usage` + `tsc_repo_utilization`) per user decision Q4

---

### ⏳ Session 3.6: Comprehensive Testing

**Activities:** Unit tests, integration tests, cache validation  
**Estimated**: 3h

---

### ⏳ Session 3.7: Documentation & Benchmarking

**Activities:** Update README, API docs, performance benchmarks  
**Estimated**: 2h

---

### ⏳ Session 3.8: User Acceptance & Refinements

**Activities:** User feedback, bug fixes, optimizations  
**Estimated**: 3h

---

# 🔧 TECHNICAL ARCHITECTURE

## Universal Filter Framework (55+ Filters)

**Asset Identification (8):** asset_id, asset, asset_criticality, ip, uuid, dns_name, repository, repository_ids

**Vulnerability Info (10):** plugin_id, plugin_name, plugin_text, plugin_type, family, family_id, severity, port, protocol, data_format

**CVE/Compliance (8):** cve_id, cve, cce_id, iavm_id, ms_bulletin_id, xref, cpe, stig_severity

**Scoring (9):** base_cvss_score, cvss_v3_base_score, cvss_v4_base_score, vpr_score, epss_score, cvss_vector, cvss_v3_vector, cvss_v4_vector

**Threat Context (2):** exploit_available, exploit_frameworks

**Temporal (10):** first_seen, last_seen, last_mitigated, days_mitigated, vuln_published, patch_published, plugin_published, plugin_modified

**Risk Management (4):** accept_risk_status, recast_risk_status, mitigated_status, responsible_user

**Policy/Audit (4):** policy, policy_id, audit_file, audit_file_id, benchmark_name

**WAS-specific (1):** was_vuln

---

## Cache Strategy

**Smart TTLs by Data Volatility:**
- Static (24h): Plugins, plugin families
- Semi-static (30m): Repositories, policies, credentials, users
- Dynamic (10m): Assets, queries
- Real-time (1-5m): Scans, scan results, analysis queries

**Analysis Tool-Specific:**
- 300s (5 min): sumip, sumasset, iplist, listsoftware, listservices
- 180s (3 min): vulndetails, vulnipdetail, vulnipsummary
- 240s (4 min): listvuln, sumport, sumprotocol
- 60s (1 min): listening, event

**Pagination Normalization:** ✅ Implemented - pagination params removed from cache keys, 94% token reduction on repeats

---

## Dual-Mode Tools

**Summary Mode** (_summary): Aggregated counts, 500-1,000 tokens, for dashboards  
**Full Mode** (_full): Complete records, 4,000-8,000 tokens, for investigation (with pagination)

---

# 📊 EXPECTED TOKEN SAVINGS

| Tool | Raw API | Optimized | Reduction | Cache TTL |
|------|---------|-----------|-----------|-----------|
| tsc_profile_ip_efficient | 15,000 | 2,500 | 83% | 180s |
| tsc_list_vulns_by_ip_summary | 6,000 | 700 | 88% | 180s |
| tsc_list_vulns_by_ip_full | 12,000 | 5,000 | 58% | 180s |
| tsc_list_ips | 9,000 | 500 | 94% | 300s |
| tsc_list_vulns_by_cve | 10,000 | 1,500 | 85% | 240s |
| tsc_list_missing_patches_windows | 8,000 | 3,000 | 62% | 240s |
| tsc_scan_status | 5,000 | 1,500 | 70% | 60s |
| tsc_compliance_status_by_ip | 10,000 | 4,000 | 60% | 300s |
| tsc_list_ports | 7,000 | 2,000 | 71% | 240s |
| tsc_list_software | 8,000 | 3,000 | 62% | 300s |
| tsc_list_services | 8,000 | 3,000 | 62% | 300s |
| tsc_credential_audit | 6,000 | 2,500 | 58% | 240s |
| tsc_list_ips_by_vuln | 7,000 | 2,500 | 64% | 240s |
| tsc_list_cves_by_ip | 5,000 | 1,000 | 80% | 180s |
| tsc_list_scan_results | 6,000 | 2,500 | 58% | 180s |
| tsc_profile_ips_bulk | 2,500/IP | 100/IP | 96% | 180s |
| Admin tools (avg) | 3,000 | 800 | 73% | 600-1800s |

**Average:** 75% first call, 90% with caching

---

# 🎯 USAGE BEST PRACTICES

1. **Always Monitor Cache**: Append `then show me cache stats` to queries
2. **Use Summary First**: Get scope with summary, then full details if needed
3. **Apply Filters Early**: Filter in query, not after fetch
4. **Use Pagination**: 10-20 initial, 50-100 for reports, max 200
5. **Leverage Cache**: Run identical queries within TTL (180-300s)
6. **New Chat After Rebuild**: Start fresh OpenCode chat after container rebuild
7. **Bulk Operations**: Use bulk tools for multi-IP queries (better caching)
8. **CVE Search**: Use `tsc_list_vulns_by_cve` for outbreak response (emergency tool)

---

# 📊 OPTIMIZATION DECISIONS LOG

This roadmap reflects user decisions from 2026-06-06 Session 4:

✅ **Q1: Keep all dedicated single-purpose tools** - Performance focus over avoiding duplication  
❌ **Q2: Remove comprehensive IP profile** - Low ROI (44% vs 83% efficient mode)  
✅ **Q3: Keep both ACR tools** - Both `tsc_list_acr_by_ip` and `tsc_list_ips_by_acr_range`  
🔄 **Q4: Merge repo tools** - Combined into single `tsc_repo_status` tool  
⭐ **Q5: CVE search in Week 1** - High priority, full plugin output on request  
✅ **Q6: Both CVE tools** - Search across infrastructure + list per IP  
❌ **Q7: No plugin family search** - Not needed  
✅ **Q8: Add bulk IP queries** - No limit on IP count  
✅ **Q9: Add scan result filtering** - Better operational visibility  
❌ **Q10: No framework-specific compliance** - Generic tool covers all

**Net Changes:**
- Removed: 3 tools (comprehensive profile, plugin family, merged 2 repo tools)
- Added: 4 tools (CVE search, CVE list per IP, bulk profiling, scan results)
- Final count: **25 tools** (same as original, optimized value mix)

---

# 🚀 FOR NEXT SESSION

**To Resume Development:**
```
Review TOOLS_ROADMAP.md and week1_session5_2026-06-08_handoff.md, 
then implement Week 1 Session 1.6: tsc_list_vulns_by_cve tool
```

**Next Task Details:**
- Tool: `tsc_list_vulns_by_cve` (Tool 5)
- Session: Week 1 Session 1.6
- Time: 2-3 hours
- Token budget: 1,000-2,000
- Cache TTL: 240s
- Key features: CVE search across infrastructure, affected IP list, remediation summary

**Implementation Context:**
- Codebase: `src/tenable_sc_mcp/tools/vulnerability_lookup.py` (add Tool 5 here)
- Tool 4 complete in `tools/asset_discovery.py` (414 lines)
- Universal filter builder: `src/tenable_sc_mcp/convenience_tools.py`
- Test prompts: `TEST_PROMPTS.md`
- All validation/error patterns established

---

# 📚 DOCUMENTATION

- **Test Queries**: TEST_PROMPTS.md
- **Caching Details**: CACHING_DEEP_DIVE.md
- **Latest Session**: week1_session5_2026-06-08_handoff.md
- **API Reference**: https://docs.tenable.com/security-center/api/index.htm

---

**Version**: 4.1 (Session 1.5 Complete)  
**Last Updated**: 2026-06-08 Session 5  
**Status**: Week 1 - 67% Complete (4/6 tools done)  
**Next**: Week 1 Session 1.6 - `tsc_list_vulns_by_cve` (Tool 5)
