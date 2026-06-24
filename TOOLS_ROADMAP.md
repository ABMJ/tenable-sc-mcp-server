# Tenable.sc Convenience Tools - Development Roadmap

**Status**: v1.3.0.1 Complete (OS Filtering & Plugin Family Validation)  
**Last Updated**: 2026-06-24  
**Next Priority**: Tool 6 (Missing Patches)

---

## 📑 Table of Contents

### Quick Navigation
- [🎯 Quick Status](#-quick-status)
- [📋 Document Purpose](#-document-purpose)

### Tool Development
- [📅 Week 1 - Core Foundation (Tools 6-7)](#-week-1---core-foundation-tools-6-7)
- [📅 Week 2 - Essential Queries (Tools 8-17)](#-week-2---essential-queries-tools-8-17)
- [📅 Week 3 - Advanced Features (Tools 18-27)](#-week-3---advanced-features-tools-18-27)

### Technical Reference
- [🔧 Technical Architecture](#-technical-architecture)
- [💡 Best Practices](#-best-practices)

---

## 🎯 Quick Status

**Completed**: 7/27 tools (26%) - v1.3.0.1 includes OS filtering fixes + 2 helper tools  
**Current Phase**: v1.3.0.1 Released (OS filtering & plugin family validation)  
**Next Priority**: Tool 6 (Missing Patches)

**v1.3.0.1 Architecture (RELEASED - 2026-06-20):**
- ✅ OS filtering with word-boundary matching (74 total filters)
- ✅ Plugin family validation with smart name→ID resolution
- ✅ Added `tsc_list_operating_systems` helper tool (300s cache)
- ✅ Added `tsc_list_plugin_families` helper tool (24h cache)
- ✅ Multi-OS entry support (11 Windows 10 variants including ambiguous detections)
- ✅ All critical bugs from v1.2.1 resolved

**Completed Tools:**
1. ✅ `tsc_profile_ip_efficient` - Complete IP security profile
2. ✅ `tsc_list_vulns_by_ip_summary` - Quick vulnerability count
3. ✅ `tsc_list_vulns_by_ip_full` - Detailed vulnerability records
4. ✅ `tsc_list_ips` - IP discovery & asset enumeration
5. ✅ `tsc_list_vulns_by_cve` - CVE search across infrastructure
6. ✅ `tsc_list_operating_systems` - OS name discovery helper
7. ✅ `tsc_list_plugin_families` - Plugin family discovery helper

**See:** USER_GUIDE.md for complete documentation on completed tools

---

## 📋 Document Purpose

This document provides **detailed specifications for pending tools** (Tools 8-27) organized by implementation priority:

- Clear purpose and use cases for each tool
- Token budgets and cache TTL targets
- Module assignments and technical implementation notes
- Follows v1.2.0+ unified filters dict pattern (see DESIGN_PRINCIPLES.md)
- Designed for LLM-assisted development sessions

**For User Documentation:** See USER_GUIDE.md for completed tools (Tools 1-7)

**For New Development Sessions:** 
1. Review HANDOFF.md for current status and next priorities
2. Review DESIGN_PRINCIPLES.md for mandatory patterns
3. Start with Tool 6 (Missing Patches)

---

# 🗓️ DEVELOPMENT ROADMAP (PENDING TOOLS)

---

## 📅 WEEK 1 - CORE FOUNDATION (TOOLS 6-7)

### ⏳ Tool 6: Missing Patches

#### `tsc_list_missing_patches`

**Status**: ⏳ Pending | **Token Budget**: 2,000-5,000 | **Cache TTL**: 240s | **Estimated**: 3-4h

**Purpose:**
Universal patch gap analysis across all operating systems (Windows, Linux, macOS) with KB article tracking.

**Key Plugins:**
- **Plugin 66334** ("Patch Report") - Universal, all OS, includes third-party software
- **Plugin 38153** ("Microsoft Windows Summary of Missing Patches") - Windows KB-specific

**Planned Features:**
- List missing patches for Windows, Linux, macOS, and Unix
- Track Microsoft KB articles with superseded KB relationships
- Include third-party software patches (Chrome, VMware, Nessus Agent, etc.)
- Filter by IP, repository, or other standard filters
- Group patches by IP address
- Extract KB numbers and support URLs

**Use Cases:**
- Patch compliance reporting across entire infrastructure
- Windows KB tracking for Patch Tuesday validation
- Third-party software update verification
- Remediation prioritization

**Module**: `tools/patch_management.py` (new file)

**Implementation Notes:**
- Query plugin 66334 (universal) OR plugin 38153 (Windows KB only)
- Use `vulndetails` analysis tool to get full plugin output
- Parse `pluginText` field (HTML-escaped text) to extract KB numbers
- HTML unescape required: `&lt;` → `<`, `&gt;` → `>`
- Regex patterns:
  - KB articles: `KB\d+`
  - Legacy MS bulletins: `MS\d{2}-\d+`
  - Third-party software: `\[ (.+?) \]`
- Cache TTL: 240s (patches change during Patch Tuesday)
- Support both modes: universal (66334) or Windows-only (38153)

**Data Structure (Plugin 66334 - Universal):**
```
<plugin_output>
. You need to take the following 42 actions :

+ Install the following Microsoft patches :
- KB5025279 (85 vulnerabilities)The following KBs would be covered: 
KB5022872, KB5022874, KB5021291, ...

[ Google Chrome < 113.0.5672.63 Multiple Vulnerabilities ]
+ Action to take : Upgrade to Google Chrome version 113.0.5672.63 or later.
+ Impact : Taking this action will resolve the following 71 different vulnerabilities :
CVE-2023-2468, CVE-2023-2467, ...
</plugin_output>
```

**Data Structure (Plugin 38153 - Windows KB):**
```
<plugin_output>The patches for the following bulletins or KBs are missing on the remote host :

 - MS16-087 ( http://technet.microsoft.com/en-us/security/bulletin/ms16-087 )
 - KB4025252 ( https://support.microsoft.com/en-us/help/4025252 )
 - KB4025337 ( https://support.microsoft.com/en-us/help/4025337 )
 ...
</plugin_output>
```

**Query Structure:**
```python
# Mode 1: Universal patches (all OS + third-party)
query = {
    "tool": "vulndetails",
    "type": "vuln",
    "filters": [
        {"filterName": "pluginID", "operator": "=", "value": "66334"},
        # Additional user filters (ip, repository, etc.)
    ]
}

# Mode 2: Windows KB only
query = {
    "tool": "vulndetails",
    "type": "vuln",
    "filters": [
        {"filterName": "pluginID", "operator": "=", "value": "38153"},
        # Additional user filters
    ]
}
```

**Parsing Implementation:**
```python
import re
from html import unescape

def parse_patch_report(plugin_text: str, plugin_id: str) -> dict:
    """Parse patch report from plugin 66334 or 38153."""
    text = unescape(plugin_text)
    text = re.sub(r'</?plugin_output>', '', text)
    
    if plugin_id == "66334":
        return parse_plugin_66334(text)
    else:  # 38153
        return parse_plugin_38153(text)

def parse_plugin_66334(text: str) -> dict:
    """Parse universal patch report (all OS)."""
    patches = []
    
    # Extract Microsoft KB patches
    kb_pattern = r'- (KB\d+)(?: \((\d+) vulnerabilities\))?'
    for match in re.finditer(kb_pattern, text):
        kb_id = match.group(1)
        vuln_count = int(match.group(2)) if match.group(2) else None
        patches.append({
            "type": "microsoft_kb",
            "kb_id": kb_id,
            "vulnerability_count": vuln_count
        })
    
    # Extract third-party software
    software_pattern = r'\[ (.+?) \]'
    for match in re.finditer(software_pattern, text):
        patches.append({
            "type": "third_party",
            "software": match.group(1)
        })
    
    return {"patches": patches}

def parse_plugin_38153(text: str) -> dict:
    """Parse Windows KB summary."""
    kb_list = []
    
    # Extract KB articles
    kb_pattern = r'(KB\d+)'
    for match in re.finditer(kb_pattern, text):
        kb_id = match.group(1)
        kb_list.append({
            "kb_id": kb_id,
            "url": f"https://support.microsoft.com/en-us/help/{kb_id}"
        })
    
    # Extract legacy MS bulletins
    ms_pattern = r'(MS\d{2}-\d+)'
    for match in re.finditer(ms_pattern, text):
        kb_list.append({
            "bulletin_id": match.group(1)
        })
    
    return {"missing_kbs": kb_list}
```

**Example Usage:**
```python
# Universal patch report (all OS)
result = tsc_list_missing_patches(
    mode="universal",
    filters={"ip": "10.1.20.10"}
)

# Windows KB only
result = tsc_list_missing_patches(
    mode="windows",
    filters={"repository": "Production"}
)
```

**Output Format:**
```json
{
  "ok": true,
  "mode": "universal",
  "total_affected_ips": 15,
  "patches_by_ip": [
    {
      "ip": "10.1.20.10",
      "hostname": "win7-office2010.labnet.local",
      "os": "Microsoft Windows 7 Professional Service Pack 1",
      "repository": "Default",
      "total_missing_patches": 42,
      "microsoft_kbs": [
        {
          "kb_id": "KB5025279",
          "vulnerability_count": 85,
          "supersedes": ["KB5022872", "KB5022874"]
        }
      ],
      "third_party": [
        {
          "software": "Google Chrome < 113.0.5672.63",
          "cve_count": 71
        }
      ]
    }
  ]
}
```

**Complexity Notes:**
- **MEDIUM complexity** (not easy) due to text parsing requirements
- HTML unescaping needed for plugin output
- Two different text formats to handle
- Regex extraction for KB numbers and software names
- Need to associate patches with IPs
- Estimated 3-4 hours (was originally estimated at 2h)

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
- Troubleshoot failed scans
- Track scan performance
- Validate scan completion

**Module**: `tools/scanning.py`

**Implementation Notes:**
- Use `/rest/scanResult` with `usable` or `manageable` fields
- Short cache TTL (60s) for real-time updates
- Support status filters: running, completed, error, stopped
- Calculate progress from `completedIPs` / `totalIPs`
- Include scanner name and launcher username

**Example Usage:**
```python
filters = {
    "status": "running",
    "time_range": "24h"
}
result = tsc_scan_status(filters=filters)
```

---

## 📅 WEEK 2 - ESSENTIAL QUERIES (TOOLS 8-17)

### Session 2.1: Tool 8 - Compliance Summary

#### `tsc_compliance_summary`

**Status**: ⏳ Pending | **Token Budget**: 2,500-5,000 | **Cache TTL**: 180s | **Estimated**: 3h

**Purpose:**
Compliance posture overview across policies (PCI, HIPAA, CIS, custom).

**Planned Features:**
- List compliance results by policy
- Filter by audit file/policy name
- Show pass/fail/error counts
- Include compliance percentage
- Support repository/asset group scoping

**Use Cases:**
- Compliance reporting
- Audit preparation
- Policy effectiveness tracking
- Remediation prioritization

**Module**: `tools/compliance.py`

---

### Session 2.2: Tool 9 - Compliance Details

#### `tsc_compliance_details`

**Status**: ⏳ Pending | **Token Budget**: 4,000-8,000 | **Cache TTL**: 180s | **Estimated**: 3h

**Purpose:**
Detailed compliance results per check with affected assets.

**Planned Features:**
- List failed checks with descriptions
- Include affected IP addresses per check
- Filter by severity/check status
- Support pagination for large result sets
- Include remediation guidance

**Use Cases:**
- Drill-down from summary to specifics
- Generate remediation work orders
- Track specific control compliance
- Validate remediation completion

**Module**: `tools/compliance.py`

---

### Session 2.3: Tool 10 - Asset Details

#### `tsc_asset_details`

**Status**: ⏳ Pending | **Token Budget**: 2,000-4,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
Comprehensive asset metadata (OS, tags, tracking method, last scan).

**Planned Features:**
- Get asset details by IP or UUID
- Include OS, DNS name, MAC address
- Show asset tags and criticality
- Display tracking method and discovery info
- Include last scan date and scanner

**Use Cases:**
- Asset inventory queries
- Validate asset configuration
- Troubleshoot missing assets
- Verify asset tagging

**Module**: `tools/assets/asset_lookup.py`

---

### Session 2.4: Tool 11 - Asset Search

#### `tsc_search_assets`

**Status**: ⏳ Pending | **Token Budget**: 3,000-6,000 | **Cache TTL**: 180s | **Estimated**: 3h

**Purpose:**
Flexible asset search with multi-field filtering and text search.

**Planned Features:**
- Search by hostname, IP range, OS, tags
- Support wildcard and regex patterns
- Filter by asset criticality and exposure
- Include vulnerability summary per asset
- Support pagination and sorting

**Use Cases:**
- Find assets by partial hostname
- Locate assets by tag or criticality
- Discover assets by OS or software
- Build custom asset reports

**Module**: `tools/assets/asset_discovery.py`

---

### Session 2.5: Tool 12 - Software Inventory

#### `tsc_list_software`

**Status**: ⏳ Pending | **Token Budget**: 3,500-7,000 | **Cache TTL**: 300s | **Estimated**: 3h

**Purpose:**
Installed software inventory across all or filtered assets.

**Planned Features:**
- List installed software by name/vendor
- Filter by version or installation date
- Group by software or by IP
- Include installation count per software
- Support CPE-based searches

**Use Cases:**
- License compliance tracking
- Vulnerability surface mapping
- EOL software discovery
- Software standardization audits

**Module**: `tools/assets/asset_discovery.py`

---

### Session 2.6: Tool 13 - Service Inventory

#### `tsc_list_services`

**Status**: ⏳ Pending | **Token Budget**: 2,500-5,000 | **Cache TTL**: 240s | **Estimated**: 2h

**Purpose:**
Network services inventory with port/protocol/banner details.

**Planned Features:**
- List open ports/services across assets
- Filter by port, protocol, service name
- Include banner/version information
- Group by service or by IP
- Show service exposure (internal/external)

**Use Cases:**
- Attack surface mapping
- Unauthorized service detection
- Port/service standardization
- Network segmentation validation

**Module**: `tools/assets/asset_discovery.py`

---

### Session 2.7: Tool 14 - Vulnerability Trends

#### `tsc_vulnerability_trends`

**Status**: ⏳ Pending | **Token Budget**: 3,000-6,000 | **Cache TTL**: 300s | **Estimated**: 3h

**Purpose:**
Historical vulnerability counts over time (trend analysis).

**Planned Features:**
- Show vulnerability count changes over time
- Group by severity or repository
- Support custom date ranges
- Include new/fixed/persistent vuln counts
- Generate sparkline-ready data

**Use Cases:**
- Track remediation progress
- Report security posture trends
- Validate patch management effectiveness
- Executive dashboards

**Module**: `tools/vulnerabilities/vulnerability_analysis.py`

---

### Session 2.8: Tool 15 - Risk Scoring

#### `tsc_risk_score_summary`

**Status**: ⏳ Pending | **Token Budget**: 2,500-5,000 | **Cache TTL**: 180s | **Estimated**: 2h

**Purpose:**
Asset and vulnerability risk scoring (VPR, CVSS, AES, ACR).

**Planned Features:**
- List assets by risk score (VPR/AES/ACR)
- Filter by score thresholds
- Include vulnerability contribution to risk
- Support repository/asset group scoping
- Show risk distribution by severity

**Use Cases:**
- Risk-based prioritization
- Critical asset identification
- Security ROI tracking
- Executive risk reporting

**Module**: `tools/vulnerabilities/vulnerability_analysis.py`

---

### Session 2.9: Tool 16 - Exploit Intelligence

#### `tsc_list_exploitable_vulns`

**Status**: ⏳ Pending | **Token Budget**: 3,500-7,000 | **Cache TTL**: 240s | **Estimated**: 3h

**Purpose:**
Vulnerabilities with known exploits (Metasploit, Exploit-DB, in-the-wild).

**Planned Features:**
- List exploitable vulnerabilities across infrastructure
- Filter by exploit type (public/weaponized/active)
- Include exploit framework references
- Show affected asset counts per vuln
- Support EPSS score filtering

**Use Cases:**
- Emergency patching prioritization
- Threat-informed defense
- Red team scoping
- Vulnerability prioritization

**Module**: `tools/vulnerabilities/vulnerability_analysis.py`

---

### Session 2.10: Tool 17 - Remediation Planning

#### `tsc_remediation_summary`

**Status**: ⏳ Pending | **Token Budget**: 4,000-8,000 | **Cache TTL**: 300s | **Estimated**: 3h

**Purpose:**
Remediation guidance aggregated by solution/patch.

**Planned Features:**
- Group vulnerabilities by common remediation
- Show asset count per remediation action
- Include patch/update URLs
- Prioritize by risk reduction potential
- Support filtering by severity/VPR

**Use Cases:**
- Patch Tuesday planning
- Remediation work order generation
- Risk reduction forecasting
- Effort-based prioritization

**Module**: `tools/vulnerabilities/vulnerability_analysis.py`

---

## 📅 WEEK 3 - ADVANCED FEATURES (TOOLS 18-27)

### Session 3.1: Tool 18 - User Management

#### `tsc_list_users`

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
User account listing and role/permission summary.

**Module**: `tools/admin/user_management.py`

---

### Session 3.2: Tool 19 - Repository Management

#### `tsc_list_repositories`

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
Repository listing with asset counts and scanner assignments.

**Module**: `tools/admin/repository_management.py`

---

### Session 3.3: Tool 20 - Asset Group Management

#### `tsc_list_asset_groups`

**Status**: ⏳ Pending | **Token Budget**: 2,000-4,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
Asset group listing with definitions and member counts.

**Module**: `tools/admin/asset_group_management.py`

---

### Session 3.4: Tool 21 - Scanner Status

#### `tsc_list_scanners`

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 120s | **Estimated**: 2h

**Purpose:**
Scanner health monitoring and assignment tracking.

**Module**: `tools/scanning.py`

---

### Session 3.5: Tool 22 - Plugin Search

#### `tsc_search_plugins`

**Status**: ⏳ Pending | **Token Budget**: 2,500-5,000 | **Cache TTL**: 86400s (24h) | **Estimated**: 3h

**Purpose:**
Plugin database search by ID, name, CVE, or keyword.

**Module**: `tools/admin/plugins.py`

---

### Session 3.6: Tool 23 - Alert Management

#### `tsc_list_alerts`

**Status**: ⏳ Pending | **Token Budget**: 2,000-4,000 | **Cache TTL**: 180s | **Estimated**: 2h

**Purpose:**
Active alert listing and configuration review.

**Module**: `tools/admin/alert_management.py`

---

### Session 3.7: Tool 24 - Query Management

#### `tsc_list_queries`

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
Saved query listing and execution.

**Module**: `tools/analysis/query_management.py`

---

### Session 3.8: Tool 25 - Dashboard Summary

#### `tsc_dashboard_summary`

**Status**: ⏳ Pending | **Token Budget**: 3,000-6,000 | **Cache TTL**: 180s | **Estimated**: 3h

**Purpose:**
High-level security posture dashboard (vuln counts, top risks, trends).

**Module**: `tools/analysis/dashboard.py`

---

### Session 3.9: Tool 26 - Report Generation

#### `tsc_generate_report`

**Status**: ⏳ Pending | **Token Budget**: 2,000-4,000 | **Cache TTL**: N/A | **Estimated**: 3h

**Purpose:**
On-demand report generation with customizable templates.

**Module**: `tools/reporting.py`

---

### Session 3.10: Tool 27 - Export Data

#### `tsc_export_data`

**Status**: ⏳ Pending | **Token Budget**: 2,500-5,000 | **Cache TTL**: N/A | **Estimated**: 3h

**Purpose:**
Data export in CSV/JSON formats for external analysis.

**Module**: `tools/reporting.py`

---

## 🔧 Technical Architecture

### Universal Patterns (Apply to All Tools)

**1. Unified Filters Dict:**
```python
filters = {
    "severity": "critical",
    "asset_criticality": "7-10",  # RANGE format for scores
    "exploit_available": "Yes",
    "repository": "Production"
}
```

**2. Smart Lookups (No Hardcoding):**
- OS names: Fetch from `listos` API (300s cache)
- Plugin families: Fetch from `/rest/pluginFamily` (24h cache)
- All lookups use live API data

**3. Token Optimization:**
- Target: 80-90% reduction vs raw API responses
- Use `keys_only` for list operations
- Deduplicate results (by IP or IP:plugin_id:port)
- Paginate large result sets

**4. Cache Strategy:**
- Static data (plugins, families): 24h
- Semi-static (OS names, users): 5-10min
- Dynamic (scans, vulnerabilities): 60-180s
- Real-time (scan status): 30-60s

**5. Error Handling:**
- Validate filter parameters before API calls
- Raise clear errors for invalid inputs
- Include helpful error messages with guidance
- Never return unfiltered results on filter failure

### Module Organization

```
src/tenable_sc_mcp/tools/
├── admin/
│   ├── plugins.py (Tools 7, 22)
│   ├── user_management.py (Tool 18)
│   ├── repository_management.py (Tool 19)
│   ├── asset_group_management.py (Tool 20)
│   └── alert_management.py (Tool 23)
├── assets/
│   ├── asset_discovery.py (Tools 4, 6, 11, 12, 13)
│   └── asset_lookup.py (Tools 1, 10)
├── vulnerabilities/
│   ├── vulnerability_lookup.py (Tools 2a, 2b, 5)
│   └── vulnerability_analysis.py (Tools 14, 15, 16, 17)
├── compliance/
│   └── compliance.py (Tools 8, 9)
├── scanning.py (Tools 7, 21)
├── analysis/
│   ├── query_management.py (Tool 24)
│   └── dashboard.py (Tool 25)
└── reporting.py (Tools 26, 27)
```

---

## 💡 Best Practices

### 1. Development Workflow

1. **Plan First**: Review tool specification in this document
2. **Design Filters**: Identify which filters from COMMON_FILTERS apply
3. **Prototype**: Start with basic API call, validate response structure
4. **Optimize**: Add caching, deduplication, token reduction
5. **Test**: Create 3-5 test cases covering common use cases
6. **Document**: Update USER_GUIDE.md with examples and use cases

### 2. Filter Design

- **Use RANGE format for scores**: `"7-10"` NOT `">7"`
- **Support multiple filter combinations**: AND logic by default
- **Validate inputs**: Check filter values before API calls
- **Use smart lookups**: OS names, plugin families, etc.
- **Document filter behavior**: Clear examples in docstrings

### 3. Token Efficiency

- **Target 80-90% reduction**: Compare token count to raw API
- **Use keys_only parameter**: When full details not needed
- **Deduplicate results**: By IP or unique identifier
- **Paginate large results**: Default 50-200 records
- **Cache aggressively**: But respect data volatility

### 4. Testing

- **Test with real API**: No mocks for integration tests
- **Cover edge cases**: Empty results, invalid filters, large datasets
- **Measure token usage**: Include in test output
- **Validate cache behavior**: HIT/MISS testing
- **Document test results**: Add to TEST_PROMPTS.md

### 5. Documentation

- **Clear "When to Use" section**: Help users choose right tool
- **Practical examples**: Natural language prompts
- **Performance metrics**: Token counts, response times
- **Troubleshooting**: Common issues and solutions
- **Update USER_GUIDE.md**: As tools are completed

---

## 📊 Progress Tracking

**Overall Progress**: 7/27 tools (26%)

**Week 1**: 5/7 tools complete (71%)
- ✅ Tool 1: `tsc_profile_ip_efficient`
- ✅ Tool 2a: `tsc_list_vulns_by_ip_summary`
- ✅ Tool 2b: `tsc_list_vulns_by_ip_full`
- ✅ Tool 4: `tsc_list_ips`
- ✅ Tool 5: `tsc_list_vulns_by_cve`
- ⏳ Tool 6: Missing patches (pending)
- ⏳ Tool 7: Scan status (pending)

**Helper Tools**: 2/2 complete (100%)
- ✅ `tsc_list_operating_systems`
- ✅ `tsc_list_plugin_families`

**Week 2**: 0/10 tools (0%)
**Week 3**: 0/10 tools (0%)

---

**Next Steps:**
1. Start Tool 6 (Missing Patches) - See HANDOFF.md for implementation plan
2. Continue with Week 1 remaining tools (Tool 7)
3. Proceed to Week 2 essential queries (Tools 8-17)
4. Begin Week 2 essential queries
