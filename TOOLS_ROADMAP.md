# Tenable.sc Convenience Tools - Development Roadmap

**Status**: 9/27 tools complete (33%)  
**Last Updated**: 2026-06-24  
**Next Priority**: Tool 8 (Compliance Summary)

---

## 📋 Document Purpose

This document provides **detailed specifications for upcoming tools** (Tools 7-27) organized by implementation priority.

**For Completed Tools:** See USER_GUIDE.md for full documentation on Tools 1-9

**For New Development Sessions:** 
1. Review HANDOFF.md for current status and next priorities
2. Review DESIGN_PRINCIPLES.md for mandatory patterns
3. Start with Tool 8 (Compliance Summary)

---

# 🗓️ UPCOMING TOOLS

---

## Tool 8: Compliance Summary (NEXT PRIORITY)

### `tsc_compliance_summary`

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

## Tool 9: Compliance Details

### `tsc_compliance_details`

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

## Tool 10: Asset Details

### `tsc_asset_details`

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

## Tool 11: Asset Search

### `tsc_search_assets`

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

## Tool 12: Software Inventory

### `tsc_list_software`

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

## Tool 13: Service Inventory

### `tsc_list_services`

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

## Tool 14: Vulnerability Trends

### `tsc_vulnerability_trends`

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

## Tool 15: Risk Scoring

### `tsc_risk_score_summary`

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

## Tool 16: Exploit Intelligence

### `tsc_list_exploitable_vulns`

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

## Tool 17: Remediation Planning

### `tsc_remediation_summary`

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


## Tool 18: User Management

### `tsc_list_users`

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
User account listing and role/permission summary.

**Module**: `tools/admin/user_management.py`

---

## Tool 19: Repository Management

### `tsc_list_repositories`

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
Repository listing with asset counts and scanner assignments.

**Module**: `tools/admin/repository_management.py`

---

## Tool 20: Asset Group Management

### `tsc_list_asset_groups`

**Status**: ⏳ Pending | **Token Budget**: 2,000-4,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
Asset group listing with definitions and member counts.

**Module**: `tools/admin/asset_group_management.py`

---

## Tool 21: Scanner Status

### `tsc_list_scanners`

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 120s | **Estimated**: 2h

**Purpose:**
Scanner health monitoring and assignment tracking.

**Module**: `tools/scanning.py`

---

## Tool 22: Plugin Search

### `tsc_search_plugins`

**Status**: ⏳ Pending | **Token Budget**: 2,500-5,000 | **Cache TTL**: 86400s (24h) | **Estimated**: 3h

**Purpose:**
Plugin database search by ID, name, CVE, or keyword.

**Module**: `tools/admin/plugins.py`

---

## Tool 23: Alert Management

### `tsc_list_alerts`

**Status**: ⏳ Pending | **Token Budget**: 2,000-4,000 | **Cache TTL**: 180s | **Estimated**: 2h

**Purpose:**
Active alert listing and configuration review.

**Module**: `tools/admin/alert_management.py`

---

## Tool 24: Query Management

### `tsc_list_queries`

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
Saved query listing and execution.

**Module**: `tools/analysis/query_management.py`

---

## Tool 25: Dashboard Summary

### `tsc_dashboard_summary`

**Status**: ⏳ Pending | **Token Budget**: 3,000-6,000 | **Cache TTL**: 180s | **Estimated**: 3h

**Purpose:**
High-level security posture dashboard (vuln counts, top risks, trends).

**Module**: `tools/analysis/dashboard.py`

---

## Tool 26: Report Generation

### `tsc_generate_report`

**Status**: ⏳ Pending | **Token Budget**: 2,000-4,000 | **Cache TTL**: N/A | **Estimated**: 3h

**Purpose:**
On-demand report generation with customizable templates.

**Module**: `tools/reporting.py`

---

## Tool 27: Export Data

### `tsc_export_data`

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
