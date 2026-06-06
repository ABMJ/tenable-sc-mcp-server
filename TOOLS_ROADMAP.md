# Tenable.sc Convenience Tools - Complete Roadmap & User Guide

**Status**: Week 1 - 60% Complete (3 tools operational, 21 remaining)  
**Version**: 3.0 (Combined Roadmap + User Guide)  
**Last Updated**: 2026-06-06 14:30

---

## 🎯 Quick Status

**Completed Tools**: 3/24 (12.5%)  
**Current Phase**: Week 1 (Core Foundation)  
**Next Session**: Week 1 Session 1.4 - Implement `tsc_list_ips`

**Production Ready Tools:**
- ✅ Tool 1: `tsc_profile_ip_efficient` - IP profiling (83-90% token savings)
- ✅ Tool 2a: `tsc_list_vulns_by_ip_summary` - Vulnerability summary (88-92% savings)
- ✅ Tool 2b: `tsc_list_vulns_by_ip_full` - Full vulnerability details (58-75% savings)

**Validated Performance:**
- Cache hit rate: 57%+ achieved
- Token savings: 58-90% confirmed
- Response time: <1ms cached, 1-3s fresh
- Zero errors in production testing

---

## 📋 Complete Tool Inventory (24 Tools)

### ✅ **COMPLETED TOOLS - USER GUIDE**

---

#### **Tool 1: `tsc_profile_ip_efficient`** ✅ Production Ready

**Status**: Operational | **Token Savings**: 83-90% | **Cache TTL**: 180-300s

**What It Does:**
Multi-query efficient IP profiling using 6 optimized queries. Returns comprehensive security profile including host identity, vulnerability summary, scan information, software inventory, services, and asset group membership.

**Usage:**
```
use tenable-sc to profile IP 10.1.20.10 efficiently, then show me cache stats
```

**Returns:**
- **Host Identity**: Hostname, NetBIOS, MAC address, ACR score
- **Vulnerability Summary**: Counts by severity (critical/high/medium/low/info)
- **Last Scan Info**: Scan name, policy, timestamp, credential status, duration
- **Software**: Top 50 installed packages
- **Services**: Active services with ports/protocols
- **Asset Groups**: Group membership (up to 46 groups)

**Token Efficiency**: ~2,500 tokens (vs ~15,000 raw API) = 83% reduction

**Best For**: Initial assessment, quarterly audits, asset inventory, credential validation

---

#### **Tool 2a: `tsc_list_vulns_by_ip_summary`** ✅ Production Ready

**Status**: Operational | **Token Savings**: 88-92% | **Cache TTL**: 180s

**What It Does:**
Lightweight vulnerability counts by severity for quick overview. Aggregates data without detailed records.

**Usage:**
```
use tenable-sc to get vulnerability summary for IP 10.1.20.10 with severity critical, then show me cache stats
```

**Returns:**
- Total vulnerability count
- Breakdown by severity level
- Applied filter summary

**Supported Filters (10):**
- `severity` (critical/high/medium/low/info or 0-4)
- `exploit_available` (Yes/No)
- `first_seen` / `last_seen` (epoch timestamp)
- `family` (plugin family name)
- `vpr_score` (e.g., ">=7.0")
- `plugin_id`, `cve`, `port`, `protocol`

**Token Efficiency**: ~700 tokens (vs ~6,000 raw) = 88% reduction

**Best For**: Quick checks, dashboards, scope determination, high-level reporting

---

#### **Tool 2b: `tsc_list_vulns_by_ip_full`** ✅ Production Ready (Fixed 2026-06-06)

**Status**: Operational | **Token Savings**: 58-75% | **Cache TTL**: 180s | **Pagination**: 10-200 records

**What It Does:**
Complete vulnerability details with all fields for deep investigation and remediation planning.

**Usage:**
```
use tenable-sc to list all critical vulnerabilities for IP 10.1.20.10 using tsc_list_vulns_by_ip_full, show first 10 records, then show me cache stats
```

**Returns (per vulnerability):**
- Plugin ID, name, severity (name + numeric)
- Plugin family
- Port and protocol
- CVSS v3 base score
- VPR score (Vulnerability Priority Rating)
- EPSS score (Exploit Prediction)
- Exploit availability and frameworks
- CVE IDs
- First/last seen timestamps
- Synopsis (200 chars)
- Solution (200 chars)

**Supported Filters (15):**
All from summary tool PLUS:
- `cvss_v3_base_score`, `epss_score`
- `patch_published`, `vuln_published`
- `mitigated_status`

**Pagination:**
- Default: 0-50 records
- Maximum: 0-200 per query
- Use `start_offset` and `end_offset`

**Token Efficiency**: ~5,000 tokens for 50 records (vs ~12,000 raw) = 58% reduction

**Best For**: Remediation planning, detailed investigation, compliance reporting, SIEM/ticketing export

**Bug Fix Note**: Fixed undefined variable issue on 2026-06-06. Now properly handles both nested and flat API responses.

---

### ⏳ **PLANNED TOOLS - IMPLEMENTATION ROADMAP**

---

### **Category 1: IP Management & Discovery (5 remaining)**

#### **Tool 3: `tsc_list_ips`** ⏳ Week 1 Session 1.4

**Status**: Next to implement  
**Token Budget**: 500-1,000 | **Cache TTL**: 300s

**Purpose**: List IPs with comprehensive filtering (subnet, asset, tag, repository, ALL 55+ analysis filters)

**Planned Filters:**
- Subnet/CIDR ranges
- Asset groups
- Tags (Category:Value format)
- Repository IDs
- Asset criticality
- Last seen date ranges
- All 55+ analysis filters

**Use Cases:**
- IP discovery and inventory
- Subnet enumeration
- Asset group membership queries
- Tag-based filtering

---

#### **Tool 4: `tsc_list_ips_by_repo`** ⏳ Week 2 Session 2.7

**Token Budget**: 500-1,000 | **Cache TTL**: 300s

**Purpose**: List all IPs in a repository or asset group

---

#### **Tool 5: `tsc_profile_ip_comprehensive`** ⏳ Week 3 Session 3.1

**Token Budget**: 8,000-12,000 | **Cache TTL**: 180s

**Purpose**: Single-query comprehensive IP profile (alternative to efficient mode)

---

#### **Tool 6: `tsc_get_os_by_ip`** ⏳ Week 2 Session 2.7

**Token Budget**: 500-1,000 | **Cache TTL**: 300s

**Purpose**: Get OS details per IP/asset

---

#### **Tool 7: `tsc_list_software`** ⏳ Week 2 Session 2.4

**Token Budget**: 2,000-4,000 | **Cache TTL**: 300s

**Purpose**: List installed software with full filtering

---

#### **Tool 8: `tsc_list_services`** ⏳ Week 2 Session 2.4

**Token Budget**: 2,000-4,000 | **Cache TTL**: 300s

**Purpose**: List running services with full filtering

---

#### **Tool 9: `tsc_list_ports`** ⏳ Week 2 Session 2.3

**Token Budget**: 1,500-3,000 | **Cache TTL**: 240s

**Purpose**: List open ports with combined scanner + vulnerability data

**Port Scanner Plugin IDs:**
- 0: "Open Port"
- 11219: "Nessus SYN scanner"
- 14272: "Netstat Portscanner (SSH)"
- 10335: "Netstat Portscanner (WMI)"
- 22964: "Service Detection"

---

### **Category 2: Vulnerability Analysis (2 remaining)**

#### **Tool 10: `tsc_list_ips_by_vuln`** ⏳ Week 2 Session 2.6

**Token Budget**: 2,000-4,000 | **Cache TTL**: 240s

**Purpose**: Reverse lookup - list IPs affected by a specific vulnerability (plugin ID or CVE)

---

#### **Tool 11: `tsc_list_missing_patches_windows`** ⏳ Week 1 Session 1.5

**Status**: Next after `tsc_list_ips`  
**Token Budget**: 2,000-4,000 | **Cache TTL**: 240s

**Purpose**: MS bulletin-based patch gap analysis for Windows systems

**Use Cases:**
- Patch compliance reporting
- MS bulletin tracking
- Windows update verification
- Remediation prioritization

---

### **Category 3: Compliance (1 tool)**

#### **Tool 12: `tsc_compliance_status_by_ip`** ⏳ Week 2 Session 2.1

**Token Budget**: 3,000-5,000 | **Cache TTL**: 300s

**Purpose**: Summary + failed compliance checks with remediation guidance

---

### **Category 4: Risk & Asset Intelligence (3 tools)**

#### **Tool 13: `tsc_list_acr_by_ip`** ⏳ Week 3 Session 3.2

**Token Budget**: 1,000-2,000 | **Cache TTL**: 300s

**Purpose**: ACR (Asset Criticality Rating) scores per IP

---

#### **Tool 14: `tsc_list_ips_by_acr_range`** ⏳ Week 3 Session 3.2

**Token Budget**: 1,000-2,000 | **Cache TTL**: 300s

**Purpose**: List IPs within ACR value/range

---

#### **Tool 15: `tsc_asset_group_membership`** ⏳ Week 3 Session 3.3

**Token Budget**: 500-1,000 | **Cache TTL**: 600s

**Purpose**: List all asset groups an IP belongs to

---

### **Category 5: Scan Operations (1 tool)**

#### **Tool 16: `tsc_scan_status`** ⏳ Week 1 Session 1.6

**Status**: Final Week 1 tool  
**Token Budget**: 1,500-3,000 | **Cache TTL**: 60s

**Purpose**: Real-time scan monitoring with filters (time, launcher, status)

**Use Cases:**
- Monitor active scans
- Track scan completion
- Identify stuck/failed scans
- Scan performance analysis

---

### **Category 6: Admin Tools (5 tools)**

#### **Tool 17: `tsc_plugin_update_status`** ⏳ Week 3 Session 3.4

**Token Budget**: 500-1,000 | **Cache TTL**: 600s | **Admin Only**

**Purpose**: Plugin feed status monitoring

---

#### **Tool 18: `tsc_license_usage`** ⏳ Week 3 Session 3.4

**Token Budget**: 500-1,000 | **Cache TTL**: 1800s | **Admin Only**

**Purpose**: License usage statistics

---

#### **Tool 19: `tsc_repo_config_usage`** ⏳ Week 3 Session 3.5

**Token Budget**: 1,500-2,500 | **Cache TTL**: 1800s | **Admin Only**

**Purpose**: Repository configuration and utilization

---

#### **Tool 20: `tsc_resources_status`** ⏳ Week 2 Session 2.2

**Token Budget**: 1,500-3,000 | **Cache TTL**: 60s/600s | **Admin Only**

**Purpose**: Nessus/NNM/WAS/Proxy status with force_refresh flag

---

#### **Tool 21: `tsc_repo_utilization`** ⏳ Week 3 Session 3.5

**Token Budget**: 1,000-2,000 | **Cache TTL**: 1800s | **Admin Only**

**Purpose**: Repository capacity and trending

---

### **Category 7: Advanced Analysis (2 tools)**

#### **Tool 22: `tsc_credential_audit`** ⏳ Week 2 Session 2.5

**Token Budget**: 2,000-3,000 | **Cache TTL**: 240s

**Purpose**: Credential success/failure audit per IP using plugin 19506 + auth plugins

**Authentication Plugin IDs:**
- 19506: "Nessus Scan Information" (master scan metadata)
- 21745: "Authentication Failure - Local Checks Not Run"
- 10394: "Microsoft Windows SMB Log In Possible"
- 10396: "SSH Authorization Successful"
- 102094: "SSH Commands Not Available"
- 24786: "Nessus Windows Scan Not Performed with Admin Privileges"

**Strategy**: Query plugin 19506 + auth failure plugins to correlate credential success/failure per protocol.

---

#### **Tool 23: `tsc_top_vulnerable_assets`** ⏳ Week 3 Session 3.3

**Token Budget**: 1,000-2,000 | **Cache TTL**: 180s

**Purpose**: Most vulnerable IPs ranked by severity count

---

## 📅 Implementation Timeline

### **Week 1 - Core Foundation** (60% Complete)

| Session | Tool(s) | Status | Hours |
|---------|---------|--------|-------|
| **1.1** | `tsc_profile_ip_efficient` | ✅ Complete | 3h |
| **1.2** | `tsc_list_vulns_by_ip_summary` + `_full` | ✅ Complete | 3h |
| **1.3** | Bug fix & testing (Tool 2) | ✅ Complete | 1h |
| **1.4** | `tsc_list_ips` | ⏳ **NEXT** | 2h |
| **1.5** | `tsc_list_missing_patches_windows` | ⏳ Pending | 2h |
| **1.6** | `tsc_scan_status` | ⏳ Pending | 2h |

**Week 1 Milestones:**
- 🟡 5 core tools operational (3 done, 2 pending)
- ✅ Universal filter framework tested
- ✅ Input validation implemented
- ✅ Cache strategies validated (57%+ hit rate)
- ✅ Token savings confirmed (58-90% reduction)

---

### **Week 2 - Extended Features** (8 Tools)

| Session | Tool(s) | Hours |
|---------|---------|-------|
| **2.1** | `tsc_compliance_status_by_ip` | 3h |
| **2.2** | `tsc_resources_status` (admin) | 3h |
| **2.3** | `tsc_list_ports` | 2h |
| **2.4** | `tsc_list_software` + `tsc_list_services` | 3h |
| **2.5** | `tsc_credential_audit` | 2h |
| **2.6** | `tsc_list_ips_by_vuln` | 2h |
| **2.7** | `tsc_list_ips_by_repo` + `tsc_get_os_by_ip` | 2h |

**Week 2 Milestones:**
- 13 tools total (5 from Week 1 + 8 new)
- Admin tools functional
- Compliance reporting operational
- Cache hit rates > 80%

---

### **Week 3 - Completion & Polish** (11 Tools + Testing)

| Session | Tool(s) | Hours |
|---------|---------|-------|
| **3.1** | `tsc_profile_ip_comprehensive` | 2h |
| **3.2** | `tsc_list_acr_by_ip` + `tsc_list_ips_by_acr_range` | 2h |
| **3.3** | `tsc_asset_group_membership` + `tsc_top_vulnerable_assets` | 2h |
| **3.4** | `tsc_plugin_update_status` + `tsc_license_usage` | 2h |
| **3.5** | `tsc_repo_config_usage` + `tsc_repo_utilization` | 2h |
| **3.6** | Comprehensive testing | 3h |
| **3.7** | Documentation + benchmarking | 2h |
| **3.8** | User acceptance + refinements | 3h |

**Week 3 Milestones:**
- All 24 tools completed
- Test coverage > 90%
- Documentation complete
- Performance benchmarks published

---

## 🔧 Technical Architecture

### Universal Filter Framework (55+ Filters)

All tools support the complete set of Tenable.sc analysis filters:

**Asset Identification (8 filters):**
`asset_id`, `asset`, `asset_criticality`, `ip`, `uuid`, `dns_name`, `repository`, `repository_ids`

**Vulnerability Info (10 filters):**
`plugin_id`, `plugin_name`, `plugin_text`, `plugin_type`, `family`, `family_id`, `severity`, `port`, `protocol`, `data_format`

**CVE/Compliance (8 filters):**
`cve_id`, `cve`, `cce_id`, `iavm_id`, `ms_bulletin_id`, `xref`, `cpe`, `stig_severity`

**Scoring (9 filters):**
`base_cvss_score`, `cvss_v3_base_score`, `cvss_v4_base_score`, `vpr_score`, `epss_score`, `cvss_vector`, `cvss_v3_vector`, `cvss_v4_vector`

**Threat Context (2 filters):**
`exploit_available`, `exploit_frameworks`

**Temporal (10 filters):**
`first_seen`, `last_seen`, `last_mitigated`, `days_mitigated`, `vuln_published`, `patch_published`, `plugin_published`, `plugin_modified`

**Risk Management (4 filters):**
`accept_risk_status`, `recast_risk_status`, `mitigated_status`, `responsible_user`

**Policy/Audit (4 filters):**
`policy`, `policy_id`, `audit_file`, `audit_file_id`, `benchmark_name`

**WAS-specific (1 filter):**
`was_vuln`

---

### Cache Strategy

**Smart TTLs by Data Volatility:**
- **Static (24h)**: Plugins, plugin families
- **Semi-static (30m)**: Repositories, policies, credentials, users
- **Dynamic (10m)**: Assets, queries
- **Real-time (1-5m)**: Scans, scan results, analysis queries

**Analysis Tool-Specific TTLs:**
- **300s (5 min)**: sumip, sumasset, iplist, listsoftware, listservices
- **180s (3 min)**: vulndetails, vulnipdetail, vulnipsummary
- **240s (4 min)**: listvuln, sumport, sumprotocol
- **60s (1 min)**: listening, event

**Pagination Normalization:** ✅ Implemented
- Pagination params removed from cache keys
- Different pagination shares same cache entry
- Validated: 94% token reduction on repeats

---

### Dual-Mode Tools (Summary + Full)

**Summary Mode** (`_summary` suffix):
- Aggregated counts/summaries
- Token budget: 500-1,000
- Use: Quick overview, dashboards

**Full Mode** (`_full` suffix):
- Complete detailed records
- Token budget: 4,000-8,000
- Use: Deep investigation, reporting
- Includes pagination

---

## 📊 Expected Token Savings

| Tool | Raw API | Optimized | Reduction | Cache TTL |
|------|---------|-----------|-----------|-----------|
| `tsc_list_ips` | ~9,000 | ~500 | 94% | 300s |
| `tsc_profile_ip_efficient` | ~15,000 | ~2,500 | 83% | 180s |
| `tsc_profile_ip_comprehensive` | ~18,000 | ~10,000 | 44% | 180s |
| `tsc_list_vulns_by_ip_summary` | ~6,000 | ~700 | 88% | 180s |
| `tsc_list_vulns_by_ip_full` | ~12,000 | ~5,000 | 58% | 180s |
| `tsc_list_missing_patches_windows` | ~8,000 | ~3,000 | 62% | 240s |
| `tsc_compliance_status_by_ip` | ~10,000 | ~4,000 | 60% | 300s |
| `tsc_scan_status` | ~5,000 | ~1,500 | 70% | 60s |
| `tsc_list_ports` | ~7,000 | ~2,000 | 71% | 240s |
| `tsc_list_software` | ~8,000 | ~3,000 | 62% | 300s |
| `tsc_list_services` | ~8,000 | ~3,000 | 62% | 300s |
| `tsc_credential_audit` | ~6,000 | ~2,500 | 58% | 240s |
| `tsc_list_ips_by_vuln` | ~7,000 | ~2,500 | 64% | 240s |
| Admin tools (avg) | ~3,000 | ~800 | 73% | 600-1800s |

**Overall Average:** 75% token reduction (first call), 90% with caching

---

## 🎯 Usage Best Practices

### 1. Always Monitor Cache Performance
```
... then show me cache stats
```
Append to every query to track hit rate and token savings.

### 2. Use Summary Before Full
Start with summary to understand scope, then use full details if needed.

**Good:**
```
1. Get summary (78 critical found)
2. Need details? → Use full with limit=10
```

**Wasteful:**
```
1. Get full for all 78 (7,000+ tokens)
2. Realize only needed count
```

### 3. Apply Filters Early
Filter in query, not locally after fetch.

### 4. Use Pagination Wisely
- Start with 10-20 for initial review
- Increase to 50-100 for reports
- Max 200 per query

### 5. Leverage Cache
Run identical queries within TTL window (180-300s) for instant cached responses.

### 6. New Chat After Container Rebuild
Start fresh OpenCode chat after rebuilding containers.

---

## 🚀 For Next Session

**To Resume Development:**
1. Review this file (TOOLS_ROADMAP.md)
2. Review last session: week1_session_3_2026-06-06_1415.md
3. Check Week 1 status: 60% complete (3/5 tools done)
4. Next task: Implement `tsc_list_ips` (Session 1.4)

**Implementation Context:**
- Codebase: `src/tenable_sc_mcp/server.py` (lines 547-1227 contain Tools 1-2)
- Universal filter builder: `src/tenable_sc_mcp/convenience_tools.py`
- Test prompts: `TEST_PROMPTS.md`
- Cache validated: 57%+ hit rate, 58-90% token savings
- All validation and error handling patterns established

**Next Tool Specifications:**
- **Tool Name**: `tsc_list_ips`
- **Purpose**: IP discovery and listing with comprehensive filters
- **Token Budget**: 500-1,000 tokens
- **Cache TTL**: 300s
- **Key Filters**: subnet/CIDR, asset groups, tags, repository IDs, asset criticality
- **Output**: List of IPs with basic metadata (hostname, OS, last seen, ACR)

---

## 📚 Documentation References

- **Test Queries**: TEST_PROMPTS.md
- **Caching Details**: CACHING_DEEP_DIVE.md
- **Latest Session**: week1_session_3_2026-06-06_1415.md
- **API Reference**: https://docs.tenable.com/security-center/api/index.htm

---

**Version**: 3.0 (Combined Roadmap + User Guide)  
**Status**: Week 1 - 60% Complete  
**Next**: Week 1 Session 1.4 - Implement `tsc_list_ips`  
**Last Updated**: 2026-06-06 14:30
