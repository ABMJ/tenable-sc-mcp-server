# Tenable.sc Convenience Tools - Complete Execution Plan

**Status**: ✅ Design Complete - Ready for Implementation  
**Version**: 2.0 (Comprehensive Plan)  
**Last Updated**: 2026-06-06

---

## 🎯 Executive Summary

**Goal**: Build 24 high-value convenience tools that reduce token usage by 90%+ through intelligent caching, query optimization, and purpose-built interfaces.

**Impact**:
- **Token Reduction**: 90-94% per query (e.g., 29,670 → 1,500 tokens)
- **Performance**: 10-20x faster responses via aggressive caching
- **User Experience**: Simple, focused tools vs complex raw API queries
- **Cost Savings**: Massive reduction in Claude API costs

**Timeline**: 3 weeks (15 implementation sessions)

**Design Philosophy**:
1. **Token Efficiency First** - Every tool targets 75-94% token reduction
2. **Cache-Friendly** - Smart TTLs based on data volatility
3. **Filter-Rich** - All 55+ analysis filters available across tools
4. **User-Friendly** - Input validation with helpful error messages
5. **Dual-Mode Options** - Summary + Full variants for large datasets

---

## 📋 Complete Tool Inventory (24 Tools)

### **Category 1: IP Management & Discovery (8 tools)**

| # | Tool Name | Description | Token Budget | Cache TTL |
|---|-----------|-------------|--------------|-----------|
| 1 | `tsc_list_ips` | List IPs with filters (subnet, asset, tag, repo, **ALL 55+ analysis filters**) | 500-1,000 | 300s |
| 2 | `tsc_list_ips_by_repo` | List all IPs in a repo or asset group | 500-1,000 | 300s |
| 3 | `tsc_profile_ip_efficient` | Multi-query IP profile (plugin 19506 + assets + software + services) | 2,000-3,000 | 180s |
| 4 | `tsc_profile_ip_comprehensive` | Single-query IP profile (vulnipdetail for everything) | 8,000-12,000 | 180s |
| 5 | `tsc_get_os_by_ip` | Get OS details per IP/asset | 500-1,000 | 300s |
| 6 | `tsc_list_software` | List installed software with **ALL filters** | 2,000-4,000 | 300s |
| 7 | `tsc_list_services` | List running services with **ALL filters** | 2,000-4,000 | 300s |
| 8 | `tsc_list_ports` | List open ports on IP/asset with ALL filters | 1,500-3,000 | 240s |

### **Category 2: Vulnerability Analysis (4 tools)**

| # | Tool Name | Description | Token Budget | Cache TTL |
|---|-----------|-------------|--------------|-----------|
| 9 | `tsc_list_vulns_by_ip_summary` | Vuln counts by severity (summary mode) | 500-1,000 | 180s |
| 10 | `tsc_list_vulns_by_ip_full` | Full vuln details with **ALL 55+ filters** | 4,000-8,000 | 180s |
| 11 | `tsc_list_ips_by_vuln` | List IPs affected by a vulnerability (full filtering) | 2,000-4,000 | 240s |
| 12 | `tsc_list_missing_patches_windows` | Missing MS patches by bulletin | 2,000-4,000 | 240s |

### **Category 3: Compliance (1 tool)**

| # | Tool Name | Description | Token Budget | Cache TTL |
|---|-----------|-------------|--------------|-----------|
| 13 | `tsc_compliance_status_by_ip` | Summary + failed checks with remediation | 3,000-5,000 | 300s |

### **Category 4: Risk & Asset Intelligence (3 tools)**

| # | Tool Name | Description | Token Budget | Cache TTL |
|---|-----------|-------------|--------------|-----------|
| 14 | `tsc_list_acr_by_ip` | ACR scores per IP | 1,000-2,000 | 300s |
| 15 | `tsc_list_ips_by_acr_range` | IPs within ACR value/range | 1,000-2,000 | 300s |
| 16 | `tsc_asset_group_membership` | List all asset groups an IP belongs to | 500-1,000 | 600s |

### **Category 5: Scan Operations (1 tool)**

| # | Tool Name | Description | Token Budget | Cache TTL |
|---|-----------|-------------|--------------|-----------|
| 17 | `tsc_scan_status` | Scan status with filters (time, launcher, status) | 1,500-3,000 | 60s |

### **Category 6: Admin Tools (5 tools)**

| # | Tool Name | Description | Token Budget | Cache TTL |
|---|-----------|-------------|--------------|-----------|
| 18 | `tsc_plugin_update_status` | Plugin feed status (admin only) | 500-1,000 | 600s |
| 19 | `tsc_license_usage` | License usage stats (admin only) | 500-1,000 | 1800s |
| 20 | `tsc_repo_config_usage` | Repository config and utilization (admin only) | 1,500-2,500 | 1800s |
| 21 | `tsc_resources_status` | Nessus/NNM/WAS/Proxy status with **force_refresh** flag (admin only) | 1,500-3,000 | 60s/600s |
| 22 | `tsc_repo_utilization` | Repository capacity and trending (admin only) | 1,000-2,000 | 1800s |

### **Category 7: Advanced Analysis (2 tools)**

| # | Tool Name | Description | Token Budget | Cache TTL |
|---|-----------|-------------|--------------|-----------|
| 23 | `tsc_credential_audit` | Credential success/failure per IP (plugin 19506 + auth plugins) | 2,000-3,000 | 240s |
| 24 | `tsc_top_vulnerable_assets` | Most vulnerable IPs by severity count | 1,000-2,000 | 180s |

---

## 🔧 Technical Architecture

### 1. Universal Filter Framework (55+ Filters)

All tools support the complete set of Tenable.sc analysis filters:

**Asset Identification (8 filters)**:
- `asset_id`, `asset`, `asset_criticality`, `ip`, `uuid`, `dns_name`, `repository`, `repository_ids`

**Vulnerability Info (10 filters)**:
- `plugin_id`, `plugin_name`, `plugin_text`, `plugin_type`, `family`, `family_id`, `severity`, `port`, `protocol`, `data_format`

**CVE/Compliance (8 filters)**:
- `cve_id`, `cve`, `cce_id`, `iavm_id`, `ms_bulletin_id`, `xref`, `cpe`, `stig_severity`

**Scoring (9 filters)**:
- `base_cvss_score`, `cvss_v3_base_score`, `cvss_v4_base_score`, `vpr_score`, `epss_score`, `cvss_vector`, `cvss_v3_vector`, `cvss_v4_vector`

**Threat Context (2 filters)**:
- `exploit_available`, `exploit_frameworks`

**Temporal (10 filters)**:
- `first_seen`, `last_seen`, `last_mitigated`, `days_mitigated`, `vuln_published`, `patch_published`, `plugin_published`, `plugin_modified`

**Risk Management (4 filters)**:
- `accept_risk_status`, `recast_risk_status`, `mitigated_status`, `responsible_user`

**Policy/Audit (4 filters)**:
- `policy`, `policy_id`, `audit_file`, `audit_file_id`, `benchmark_name`

**WAS-specific (1 filter)**:
- `was_vuln`

### 2. Credential Audit Architecture

**Authentication Plugin IDs**:
```python
AUTH_PLUGINS = {
    19506: "Nessus Scan Information",  # Master scan metadata
    21745: "Authentication Failure - Local Checks Not Run",
    10394: "Microsoft Windows SMB Log In Possible",
    10396: "SSH Authorization Successful",
    102094: "SSH Commands Not Available",
    24786: "Nessus Windows Scan Not Performed with Admin Privileges",
}
```

**Strategy**: Query plugin 19506 + auth failure plugins (21745, 10394, 10396, 102094, 24786) to correlate credential success/failure per protocol.

**Plugin 19506 Parse Fields** (from user sample):
- Nessus version, build, plugin feed version
- Scanner edition, OS, distribution
- Scan type, name, policy (with UUID)
- Scanner IP, port scanner, range
- **Credentialed checks: yes/no** ← Key field
- **Patch management checks** ← Key field
- Scan timing, duration, settings

### 3. Open Ports Tool Architecture

**Port Scanner Plugin IDs**:
```python
PORT_SCANNER_PLUGINS = {
    0: "Open Port",  # Generic port detection
    11219: "Nessus SYN scanner",
    14272: "Netstat Portscanner (SSH)",
    10335: "Netstat Portscanner (WMI)",
    22964: "Service Detection",
}
```

**Strategy**: Combine port scanner results (lightweight, ~500 tokens) + vulnerability aggregation by port to provide complete port list with security context.

### 4. Dual-Mode Tools (Summary + Full)

Tools with potentially large datasets offer two modes:

**Summary Mode** (`_summary` suffix):
- Returns aggregated counts/summaries
- Token budget: 500-1,000
- Use case: Quick overview, dashboards

**Full Mode** (`_full` suffix):
- Returns complete detailed records
- Token budget: 4,000-8,000
- Use case: Deep investigation, reporting
- Includes pagination support

**Example**: 
- `tsc_list_vulns_by_ip_summary` → {critical: 5, high: 23, ...}
- `tsc_list_vulns_by_ip_full` → [{plugin_id, severity, cvss, ...}, ...]

### 5. Input Validation

All tools include pre-validation with helpful error messages:

```python
# Invalid IP example
Input: ip="invalid"
Output: {
  "error": "Invalid IP address format: 'invalid'",
  "expected": "Valid IPv4/IPv6 address (e.g., 10.1.20.10)",
  "suggestion": "Use tsc_list_ips() to find valid IP addresses"
}

# Invalid severity example
Input: severity="bogus"
Output: {
  "error": "Invalid severity: 'bogus'",
  "valid_values": "0, 1, 2, 3, 4, info, low, medium, high, critical"
}
```

### 6. Cache Strategy

**Smart TTLs by Data Volatility**:
- **Static data** (24h): Plugins, plugin families
- **Semi-static** (30m): Repositories, scan policies, credentials, users
- **Dynamic** (10m): Assets, queries
- **Real-time** (1-5m): Scans, scan results, analysis queries

**Analysis Tool-Specific TTLs**:
- **300s (5 min)**: sumip, sumasset, iplist, listsoftware, listservices (slow-changing)
- **180s (3 min)**: vulndetails, vulnipdetail, vulnipsummary (semi-dynamic)
- **240s (4 min)**: listvuln, sumport, sumprotocol (relatively stable)
- **60s (1 min)**: listening, event (real-time)

**Pagination Normalization**: Already implemented ✅
- Pagination params (`startOffset`, `endOffset`) removed from cache keys
- Different pagination shares same cache entry
- Validated working: 94% token reduction on repeat queries

---

## 📅 Implementation Timeline (3 Weeks / 15 Sessions)

### **Phase 1: Week 1 - Core Foundation (5 Tools)**

**Priority**: Highest-value tools with maximum token savings

| Session | Tool(s) | Hours | Deliverables |
|---------|---------|-------|--------------|
| **1.1** | `tsc_profile_ip_efficient` | 3h | Multi-query efficient IP profiling with plugin 19506 parsing |
| **1.2** | `tsc_list_vulns_by_ip_summary` + `_full` | 3h | Dual-mode vuln listing with ALL 55+ filters |
| **1.3** | `tsc_list_ips` | 2h | IP listing with subnet/repo/tag/asset filters |
| **1.4** | `tsc_list_missing_patches_windows` | 2h | MS bulletin-based patch gaps |
| **1.5** | `tsc_scan_status` | 2h | Scan monitoring with time/launcher/status filters |

**Week 1 Milestones**:
- ✅ 5 core tools operational
- ✅ Universal filter framework tested
- ✅ Input validation implemented
- ✅ Cache strategies validated
- ✅ Token savings measured (target: 90%+ reduction)

---

### **Phase 2: Week 2 - Extended Features (8 Tools)**

**Priority**: High-value admin, compliance, and analysis tools

| Session | Tool(s) | Hours | Deliverables |
|---------|---------|-------|--------------|
| **2.1** | `tsc_compliance_status_by_ip` | 3h | Summary + failed checks with remediation |
| **2.2** | `tsc_resources_status` (admin) | 3h | Nessus/NNM/WAS/Proxy status with force_refresh |
| **2.3** | `tsc_list_ports` | 2h | Open ports with combined scanner + vuln data |
| **2.4** | `tsc_list_software` + `tsc_list_services` | 3h | Software/services with full filtering |
| **2.5** | `tsc_credential_audit` | 2h | Auth status per IP (plugin 19506 + auth plugins) |
| **2.6** | `tsc_list_ips_by_vuln` | 2h | Reverse lookup: IPs affected by a vulnerability |
| **2.7** | `tsc_list_ips_by_repo` + `tsc_get_os_by_ip` | 2h | Repo-based IP listing + OS detection |

**Week 2 Milestones**:
- ✅ 13 tools total (5 from Week 1 + 8 new)
- ✅ Admin tools functional
- ✅ Compliance reporting operational
- ✅ Cache hit rates > 80% on repeated queries

---

### **Phase 3: Week 3 - Completion & Polish (11 Tools + Testing)**

**Priority**: Remaining tools, testing, documentation, optimization

| Session | Tool(s) | Hours | Deliverables |
|---------|---------|-------|--------------|
| **3.1** | `tsc_profile_ip_comprehensive` | 2h | Single-query comprehensive IP profile (alternate mode) |
| **3.2** | `tsc_list_acr_by_ip` + `tsc_list_ips_by_acr_range` | 2h | ACR risk scoring tools |
| **3.3** | `tsc_asset_group_membership` + `tsc_top_vulnerable_assets` | 2h | Asset intelligence tools |
| **3.4** | `tsc_plugin_update_status` + `tsc_license_usage` | 2h | Admin monitoring tools |
| **3.5** | `tsc_repo_config_usage` + `tsc_repo_utilization` | 2h | Repository management tools |
| **3.6** | Comprehensive testing | 3h | Unit tests, integration tests, cache validation |
| **3.7** | Documentation + benchmarking | 2h | Update README, API docs, performance benchmarks |
| **3.8** | User acceptance testing + refinements | 3h | User feedback, bug fixes, optimizations |

**Week 3 Milestones**:
- ✅ All 24 tools completed
- ✅ Test coverage > 90%
- ✅ Documentation complete
- ✅ Performance benchmarks published
- ✅ User acceptance complete

---

## 📊 Expected Token Savings (By Tool)

| Tool | Raw API Tokens | Optimized Tokens | Reduction % | Cache TTL |
|------|----------------|------------------|-------------|-----------|
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

**Overall Average**: **~75% token reduction** (first call)  
**With caching**: **~90% effective reduction** (after 2-3 repeated queries)

---

## ✅ Success Criteria

### **Performance Metrics**
- ✅ Average token reduction: ≥75% (first call), ≥90% (cached calls)
- ✅ Cache hit rate: ≥80% on repeated queries
- ✅ Response time: <5s for cached queries, <30s for fresh queries
- ✅ Error rate: <1% (robust validation + error handling)

### **Code Quality**
- ✅ Test coverage: ≥90%
- ✅ All tools support full filter set (55+ filters)
- ✅ Consistent API interface across all tools
- ✅ Input validation with helpful error messages
- ✅ Comprehensive documentation with examples

### **User Experience**
- ✅ Clear, concise output formats
- ✅ Intuitive parameter names
- ✅ Helpful validation errors with suggestions
- ✅ Examples in documentation
- ✅ Summary + full mode options where applicable

---

## 🔧 Implementation Checklist (Per Tool)

For each tool, follow this checklist:

### **1. Design**
- [ ] Define input parameters (common filters + tool-specific)
- [ ] Design output format (JSON structure)
- [ ] Identify underlying analysis tool(s) to use
- [ ] Calculate token budget
- [ ] Determine cache TTL

### **2. Implementation**
- [ ] Write tool function with full docstring
- [ ] Implement universal filter builder
- [ ] Add input validation
- [ ] Implement caching logic
- [ ] Add error handling
- [ ] Format output consistently

### **3. Testing**
- [ ] Write unit tests (valid inputs)
- [ ] Write edge case tests (invalid inputs, empty results)
- [ ] Test caching behavior
- [ ] Measure token usage
- [ ] Validate cache TTL
- [ ] Test with real Tenable.sc data

### **4. Documentation**
- [ ] Update tool docstring with examples
- [ ] Add to README
- [ ] Document filter options
- [ ] Include token savings metrics
- [ ] Add usage examples

---

## 📚 Appendix A: Key Research Findings

### **A.1 Analysis Tool Types by Cache TTL**
- **300s (5 min)**: sumip, sumasset, iplist, listsoftware, listservices
- **180s (3 min)**: vulndetails, vulnipdetail, vulnipsummary, cveipdetail
- **240s (4 min)**: listvuln, sumport, sumprotocol, sumseverity
- **60s (1 min)**: listening, event (real-time)

### **A.2 Pagination Normalization (Already Implemented)**
From user test results:
- **Run 1**: 0 hits, 9 misses → 0% hit rate (expected - first query)
- **Run 2**: 1 hit, 9 misses → 10% hit rate ✅ Cache hit!
- **Run 3**: 2 hits, 9 misses → 18.2% hit rate ✅ Another cache hit!
- **Token savings**: 29,670 → 1,427 tokens (94% reduction) ✅

### **A.3 Plugin 19506 Sample Output** (User-provided)
```
Information about this scan : 

Nessus version : 10.9.4
Nessus build : 20037
Plugin feed version : 202510060158
Scanner edition used : Nessus
Scanner OS : LINUX
Scanner distribution : es8-x86-64
Scan type : Normal
Scan name : Credentialed Patch Auditing Policy - Windows
Scan policy used : 053f713d-9f27-547b-8660-a084a340f9eb-4479/Credentialed Patch Auditing Policy
Scanner IP : 192.168.40.62
Port scanner(s) : nessus_syn_scanner 
Port range : sc-default
Ping RTT : 149.816 ms
Thorough tests : no
Experimental tests : no
Scan for Unpatched Vulnerabilities : no
Plugin debugging enabled : no
Paranoia level : 1
Report verbosity : 1
Safe checks : yes
Optimize the test : yes
Credentialed checks : no  ← KEY FIELD
Patch management checks : None  ← KEY FIELD
Display superseded patches : yes (supersedence plugin did not launch)
CGI scanning : disabled
Web application tests : disabled
Max hosts : 30
Max checks : 4
Recv timeout : 5
Backports : None
Allow post-scan editing : Yes
Nessus Plugin Signature Checking : Enabled
Audit File Signature Checking : Disabled
Scan Start Date : 2025/10/6 4:15 EDT (UTC -04:00)
Scan duration : 181 sec
Scan for malware : no
```

### **A.4 SSL/TLS Plugin List** (For Future Implementation)

**Version Detection Plugins**:
- 20007: SSL v2/v3 Detection (CRITICAL)
- 104743: TLS 1.0 Detection (MEDIUM)
- 157288: TLS 1.1 Deprecated (MEDIUM)

**Certificate Validation Plugins**:
- 15901: SSL Certificate Expiry (MEDIUM)
- 51192: SSL Certificate Cannot Be Trusted (MEDIUM)
- 10863: SSL Certificate Information (INFO)
- 69551: RSA Keys < 2048 bits (LOW)

**Cipher Weakness Plugins**:
- 26928: Weak Cipher Suites (MEDIUM)
- 42873: Medium Strength Ciphers/SWEET32 (HIGH)
- 65821: RC4 Cipher Support (MEDIUM)
- 21643: Cipher Suite Enumeration (INFO)

**Protocol Vulnerability Plugins**:
- 73412: Heartbleed (HIGH)
- 78479: POODLE (LOW)
- 81606: FREAK (MEDIUM)
- 83875: Logjam (LOW)
- 89058: DROWN (MEDIUM)

---

## 📝 Open Questions / Decisions Needed

### **Q1: Tool Naming Convention**
- **Current**: `tsc_list_vulns_by_ip_full`
- **Alternative**: `tsc_ip_vulnerabilities_full`
- **Decision needed**: User preference?

### **Q2: Output Format Standardization**
- **Option A**: All tools return `{"ok": true, "data": {...}}` structure
- **Option B**: Vary by tool type (some return raw lists, some structured)
- **Decision needed**: User preference?

### **Q3: Pagination Defaults**
- **Default page size**: 50, 100, or 200?
- **Max page size**: 500, 1000?
- **Decision needed**: User preference?

### **Q4: Cache Invalidation Strategy**
- **Option A**: Manual cache clear per tool
- **Option B**: Rely on TTL expiration only
- **Option C**: Both (TTL + manual clear capability)
- **Decision needed**: User preference?

---

## 🚀 Next Actions

### **Immediate**
1. ✅ Review and approve this execution plan
2. ⏳ Resolve open questions (Q1-Q4)
3. ⏳ Commit roadmap to GitHub

### **Week 1, Session 1.1** (Next Implementation Session)
1. ⏳ Implement `tsc_profile_ip_efficient` (first tool)
2. ⏳ Test plugin 19506 parsing with real data
3. ⏳ Validate multi-query caching
4. ⏳ Measure token savings vs. raw API
5. ⏳ Document implementation patterns

---

**Status**: ✅ Design Complete - Ready for Implementation  
**Next Milestone**: Week 1, Session 1.1 - First Tool Implementation  
**Success Metric**: 90%+ token reduction on common queries
