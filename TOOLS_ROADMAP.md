# Tenable.sc Convenience Tools - Roadmap & User Guide

**Status**: Week 1 - 60% Complete (3 tools operational, 21 remaining)  
**Last Updated**: 2026-06-06 14:30

---

## 🎯 Quick Status

**Completed**: 3/24 tools (12.5%)  
**Current Phase**: Week 1 Session 1.3 (Bug Fix) - Complete  
**Next Session**: Week 1 Session 1.4 - Implement `tsc_list_ips`

**Validated Performance:**
- Cache hit rate: 57%+ achieved
- Token savings: 58-90% confirmed
- Response time: <1ms cached, 1-3s fresh

---

## 📅 WEEK 1 - CORE FOUNDATION

### ✅ **Session 1.1: Tool 1 - IP Profile** (COMPLETE)

#### `tsc_profile_ip_efficient`

**Status**: ✅ Production Ready | **Token Savings**: 83-90% | **Cache TTL**: 180-300s

**What It Does:**
Multi-query efficient IP profiling using 6 optimized queries. Returns host identity, vulnerability summary, scan info, software, services, and asset groups.

**Usage:**
```
use tenable-sc to profile IP 10.1.20.10 efficiently, then show me cache stats
```

**Returns:**
- Host Identity: Hostname, NetBIOS, MAC, ACR score
- Vulnerability Summary: Counts by severity
- Last Scan: Name, policy, timestamp, credential status
- Software: Top 50 packages
- Services: Active services with ports
- Asset Groups: Membership (up to 46)

**Token Efficiency**: ~2,500 tokens (vs ~15,000 raw) = 83% reduction

**Best For**: Initial assessment, audits, asset inventory, credential validation

---

### ✅ **Session 1.2: Tool 2 - Vulnerability Lists** (COMPLETE)

#### `tsc_list_vulns_by_ip_summary`

**Status**: ✅ Production Ready | **Token Savings**: 88-92% | **Cache TTL**: 180s

**What It Does:**
Lightweight vulnerability counts by severity for quick overview.

**Usage:**
```
use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical, then show me cache stats
```

**Returns:**
- Total vulnerability count
- Breakdown by severity
- Applied filter summary

**Filters (10):** severity, exploit_available, first_seen, last_seen, family, vpr_score, plugin_id, cve, port, protocol

**Token Efficiency**: ~700 tokens (vs ~6,000 raw) = 88% reduction

**Best For**: Quick checks, dashboards, scope determination

---

#### `tsc_list_vulns_by_ip_full`

**Status**: ✅ Production Ready (Fixed 2026-06-06) | **Token Savings**: 58-75% | **Cache TTL**: 180s | **Pagination**: 10-200

**What It Does:**
Complete vulnerability details for deep investigation and remediation.

**Usage:**
```
use tenable-sc to list all critical vulnerabilities for IP 10.1.20.10 using tsc_list_vulns_by_ip_full, show first 10 records, then show me cache stats
```

**Returns (per vuln):**
- Plugin ID, name, severity
- Family, port, protocol
- CVSS v3, VPR, EPSS scores
- Exploit availability/frameworks
- CVE IDs
- First/last seen timestamps
- Synopsis, solution (200 chars)

**Filters (15):** All from summary PLUS cvss_v3_base_score, epss_score, patch_published, vuln_published, mitigated_status

**Pagination:** Default 0-50, max 0-200 per query

**Token Efficiency**: ~5,000 tokens for 50 records (vs ~12,000 raw) = 58% reduction

**Best For**: Remediation planning, detailed investigation, compliance reporting

**Bug Fix Note**: Fixed undefined variable issue 2026-06-06. Handles nested/flat API responses.

---

### ✅ **Session 1.3: Bug Fix & Testing** (COMPLETE)

**Activities:**
- Fixed undefined variable `response` in tsc_list_vulns_by_ip_full (line 1201-1205)
- Added `response_data` variable tracking
- Tested all 3 tools successfully
- Validated cache performance (0% → 57% hit rate)
- Confirmed token savings (58-90%)
- Updated documentation

**Deliverables:**
- Bug fix committed and deployed
- TEST_PROMPTS.md updated with cache monitoring
- week1_session_3_2026-06-06_1415.md session summary
- All tools production ready

---

### ⏳ **Session 1.4: Tool 3 - IP Listing** (NEXT)

#### `tsc_list_ips`

**Status**: ⏳ Next to implement | **Token Budget**: 500-1,000 | **Cache TTL**: 300s | **Estimated**: 2h

**Purpose:**
List IPs with comprehensive filtering - subnet, asset groups, tags, repositories, ALL 55+ analysis filters.

**Planned Features:**
- Subnet/CIDR range filtering
- Asset group membership
- Tag filtering (Category:Value format)
- Repository ID filtering
- Asset criticality filtering
- Last seen date ranges
- All 55+ analysis filters supported

**Output:**
List of IPs with:
- IP address
- Hostname
- Operating system
- Last seen timestamp
- ACR score
- Repository membership

**Use Cases:**
- IP discovery and inventory
- Subnet enumeration
- Asset group membership queries
- Tag-based asset identification
- Repository content listing

**Implementation Notes:**
- Use `sumip` or `iplist` analysis tool
- Support CIDR notation (e.g., "10.1.20.0/24")
- Validate IP format and CIDR ranges
- Cache TTL: 300s (5 minutes)
- Token budget: 500-1,000 tokens

---

### ⏳ **Session 1.5: Tool 4 - Missing Patches**

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

---

### ⏳ **Session 1.6: Tool 5 - Scan Status**

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

---

## 📅 WEEK 2 - EXTENDED FEATURES (8 TOOLS)

### ⏳ **Session 2.1: Tool 6 - Compliance Status**

#### `tsc_compliance_status_by_ip`

**Token Budget**: 3,000-5,000 | **Cache TTL**: 300s | **Estimated**: 3h

**Purpose:** Summary + failed compliance checks with remediation guidance

---

### ⏳ **Session 2.2: Tool 7 - Resources Status (Admin)**

#### `tsc_resources_status`

**Token Budget**: 1,500-3,000 | **Cache TTL**: 60s/600s | **Estimated**: 3h | **Admin Only**

**Purpose:** Nessus/NNM/WAS/Proxy status with force_refresh flag

---

### ⏳ **Session 2.3: Tool 8 - Open Ports**

#### `tsc_list_ports`

**Token Budget**: 1,500-3,000 | **Cache TTL**: 240s | **Estimated**: 2h

**Purpose:** List open ports with combined scanner + vulnerability data

**Port Scanner Plugin IDs:**
- 0: Open Port
- 11219: Nessus SYN scanner
- 14272: Netstat Portscanner (SSH)
- 10335: Netstat Portscanner (WMI)
- 22964: Service Detection

---

### ⏳ **Session 2.4: Tools 9-10 - Software & Services**

#### `tsc_list_software`

**Token Budget**: 2,000-4,000 | **Cache TTL**: 300s | **Estimated**: 1.5h

**Purpose:** List installed software with full filtering

---

#### `tsc_list_services`

**Token Budget**: 2,000-4,000 | **Cache TTL**: 300s | **Estimated**: 1.5h

**Purpose:** List running services with full filtering

---

### ⏳ **Session 2.5: Tool 11 - Credential Audit**

#### `tsc_credential_audit`

**Token Budget**: 2,000-3,000 | **Cache TTL**: 240s | **Estimated**: 2h

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

### ⏳ **Session 2.6: Tool 12 - IPs by Vulnerability**

#### `tsc_list_ips_by_vuln`

**Token Budget**: 2,000-4,000 | **Cache TTL**: 240s | **Estimated**: 2h

**Purpose:** Reverse lookup - list IPs affected by specific vulnerability (plugin ID or CVE)

---

### ⏳ **Session 2.7: Tools 13-14 - IP by Repo & OS Detection**

#### `tsc_list_ips_by_repo`

**Token Budget**: 500-1,000 | **Cache TTL**: 300s | **Estimated**: 1h

**Purpose:** List all IPs in a repository or asset group

---

#### `tsc_get_os_by_ip`

**Token Budget**: 500-1,000 | **Cache TTL**: 300s | **Estimated**: 1h

**Purpose:** Get OS details per IP/asset

---

## 📅 WEEK 3 - COMPLETION & POLISH (11 TOOLS)

### ⏳ **Session 3.1: Tool 15 - Comprehensive IP Profile**

#### `tsc_profile_ip_comprehensive`

**Token Budget**: 8,000-12,000 | **Cache TTL**: 180s | **Estimated**: 2h

**Purpose:** Single-query comprehensive IP profile (alternative to efficient mode)

---

### ⏳ **Session 3.2: Tools 16-17 - ACR Risk Scoring**

#### `tsc_list_acr_by_ip`

**Token Budget**: 1,000-2,000 | **Cache TTL**: 300s | **Estimated**: 1h

**Purpose:** ACR (Asset Criticality Rating) scores per IP

---

#### `tsc_list_ips_by_acr_range`

**Token Budget**: 1,000-2,000 | **Cache TTL**: 300s | **Estimated**: 1h

**Purpose:** List IPs within ACR value/range

---

### ⏳ **Session 3.3: Tools 18-19 - Asset Intelligence**

#### `tsc_asset_group_membership`

**Token Budget**: 500-1,000 | **Cache TTL**: 600s | **Estimated**: 1h

**Purpose:** List all asset groups an IP belongs to

---

#### `tsc_top_vulnerable_assets`

**Token Budget**: 1,000-2,000 | **Cache TTL**: 180s | **Estimated**: 1h

**Purpose:** Most vulnerable IPs ranked by severity count

---

### ⏳ **Session 3.4: Tools 20-21 - Admin Monitoring (Part 1)**

#### `tsc_plugin_update_status`

**Token Budget**: 500-1,000 | **Cache TTL**: 600s | **Estimated**: 1h | **Admin Only**

**Purpose:** Plugin feed status monitoring

---

#### `tsc_license_usage`

**Token Budget**: 500-1,000 | **Cache TTL**: 1800s | **Estimated**: 1h | **Admin Only**

**Purpose:** License usage statistics

---

### ⏳ **Session 3.5: Tools 22-23 - Admin Monitoring (Part 2)**

#### `tsc_repo_config_usage`

**Token Budget**: 1,500-2,500 | **Cache TTL**: 1800s | **Estimated**: 1h | **Admin Only**

**Purpose:** Repository configuration and utilization

---

#### `tsc_repo_utilization`

**Token Budget**: 1,000-2,000 | **Cache TTL**: 1800s | **Estimated**: 1h | **Admin Only**

**Purpose:** Repository capacity and trending

---

### ⏳ **Session 3.6: Comprehensive Testing**

**Activities:** Unit tests, integration tests, cache validation  
**Estimated**: 3h

---

### ⏳ **Session 3.7: Documentation & Benchmarking**

**Activities:** Update README, API docs, performance benchmarks  
**Estimated**: 2h

---

### ⏳ **Session 3.8: User Acceptance & Refinements**

**Activities:** User feedback, bug fixes, optimizations  
**Estimated**: 3h

---

## 🔧 Technical Architecture

### Universal Filter Framework (55+ Filters)

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

### Cache Strategy

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

### Dual-Mode Tools

**Summary Mode** (_summary): Aggregated counts, 500-1,000 tokens, for dashboards
**Full Mode** (_full): Complete records, 4,000-8,000 tokens, for investigation (with pagination)

---

## 📊 Expected Token Savings

| Tool | Raw API | Optimized | Reduction | Cache TTL |
|------|---------|-----------|-----------|-----------|
| tsc_profile_ip_efficient | 15,000 | 2,500 | 83% | 180s |
| tsc_list_vulns_by_ip_summary | 6,000 | 700 | 88% | 180s |
| tsc_list_vulns_by_ip_full | 12,000 | 5,000 | 58% | 180s |
| tsc_list_ips | 9,000 | 500 | 94% | 300s |
| tsc_list_missing_patches_windows | 8,000 | 3,000 | 62% | 240s |
| tsc_scan_status | 5,000 | 1,500 | 70% | 60s |
| tsc_compliance_status_by_ip | 10,000 | 4,000 | 60% | 300s |
| tsc_list_ports | 7,000 | 2,000 | 71% | 240s |
| tsc_list_software | 8,000 | 3,000 | 62% | 300s |
| tsc_list_services | 8,000 | 3,000 | 62% | 300s |
| tsc_credential_audit | 6,000 | 2,500 | 58% | 240s |
| tsc_list_ips_by_vuln | 7,000 | 2,500 | 64% | 240s |
| Admin tools (avg) | 3,000 | 800 | 73% | 600-1800s |

**Average:** 75% first call, 90% with caching

---

## 🎯 Usage Best Practices

1. **Always Monitor Cache**: Append `then show me cache stats` to queries
2. **Use Summary First**: Get scope with summary, then full details if needed
3. **Apply Filters Early**: Filter in query, not after fetch
4. **Use Pagination**: 10-20 initial, 50-100 for reports, max 200
5. **Leverage Cache**: Run identical queries within TTL (180-300s)
6. **New Chat After Rebuild**: Start fresh OpenCode chat after container rebuild

---

## 🚀 For Next Session

**To Resume Development:**
```
Review TOOLS_ROADMAP.md and week1_session_3_2026-06-06_1415.md, 
then implement Week 1 Session 1.4: tsc_list_ips tool
```

**Next Task Details:**
- Tool: `tsc_list_ips`
- Session: Week 1 Session 1.4
- Time: 2 hours
- Token budget: 500-1,000
- Cache TTL: 300s
- Key filters: subnet/CIDR, asset groups, tags, repository IDs, asset criticality

**Implementation Context:**
- Codebase: `src/tenable_sc_mcp/server.py` (lines 547-1227 contain Tools 1-2)
- Universal filter builder: `src/tenable_sc_mcp/convenience_tools.py`
- Test prompts: `TEST_PROMPTS.md`
- All validation/error patterns established

---

## 📚 Documentation

- **Test Queries**: TEST_PROMPTS.md
- **Caching Details**: CACHING_DEEP_DIVE.md
- **Latest Session**: week1_session_3_2026-06-06_1415.md
- **API Reference**: https://docs.tenable.com/security-center/api/index.htm

---

**Version**: 3.1 (Chronologically Ordered)  
**Last Updated**: 2026-06-06 14:35  
**Status**: Week 1 - 60% Complete (3/5 tools done)  
**Next**: Week 1 Session 1.4 - `tsc_list_ips`
