# Tenable.sc MCP Server - Development Roadmap

**Current Version**: v1.2.2  
**Last Updated**: 2026-06-19  
**Next Release**: v1.3.0 (OS Filtering & Plugin Family Fix) or v1.4.0 (Multi-Client API Keys)

---

## 📑 Table of Contents

- [Overview](#overview)
- [Completed Tools](#completed-tools)
- [Planned Releases](#planned-releases)
  - [v1.3.0: OS Filtering & Plugin Family Fix](#v130-os-filtering--plugin-family-fix)
  - [v1.4.0: Multi-Client API Key Support](#v140-multi-client-api-key-support)
  - [Tool 6: Missing Patches](#tool-6-missing-patches)
  - [Tool 7: Scan Status](#tool-7-scan-status)
- [Future Tools (Week 2-3)](#future-tools-week-2-3)
- [Technical Architecture](#technical-architecture)

---

## Overview

This roadmap tracks planned features and tools for the Tenable.sc MCP Server. For documentation on **completed tools**, see **[USER_GUIDE.md](USER_GUIDE.md)**.

### Current Status

**Completed**: 5/25 tools (20%) + v1.2.2 Release  
**In Progress**: v1.3.0 and v1.4.0 planning complete  
**Next Priority**: v1.3.0 or v1.4.0 (independent features, either can go first)

### Completed Tools (See USER_GUIDE.md)

1. ✅ **tsc_profile_ip_efficient** - Complete IP Security Profile
2. ✅ **tsc_list_vulns_by_ip_summary** - Quick Vulnerability Count  
3. ✅ **tsc_list_vulns_by_ip_full** - Detailed Vulnerability Records
4. ✅ **tsc_list_ips** - IP Discovery & Asset Enumeration
5. ✅ **tsc_list_vulns_by_cve** - CVE Search Across Infrastructure

### Architecture Highlights

- ✅ **Unified Filters**: 71+ filters work consistently across all tools
- ✅ **Token Optimization**: 83-90% reduction in LLM token usage
- ✅ **Smart Caching**: Independent TTLs (60s-300s) per data type
- ✅ **Production Ready**: Comprehensive error handling and testing

---

## Planned Releases

### v1.3.0: OS Filtering & Plugin Family Fix

**Status**: 📋 Ready for Implementation  
**Estimated Time**: 6-8 hours  
**Priority**: High  
**Implementation Plan**: See **[OS_AND_PLUGIN_FAMILY_FIX.md](.private/OS_AND_PLUGIN_FAMILY_FIX.md)** (comprehensive 1,612-line guide)

**Summary**: Fix two critical issues discovered through user testing and API analysis.

#### Problem 1: CPE False Positives

**Issue**: Regex patterns cause unintended matches
- Example: `.*windows.*(10|11).*` incorrectly matches Windows Server 2019

**Solution**: Add `operating_system` filter for exact OS matching
- Uses Tenable.sc `listos` analysis tool for discovery
- Smart lookup: User requests "Windows 10" → Tool queries exact names → Zero false positives

#### Problem 2: Plugin Family Filter Broken

**Issue**: Current code uses family NAME but API requires numeric ID
- Example: `family="Windows"` fails, needs `family=[{"id": "20"}]`

**Solution**: Smart name→ID lookup with cache
- Fetch family mappings from `/rest/pluginFamily`
- Cache for 10 minutes (static data)
- Support both numeric IDs and friendly names

#### Implementation Phases

1. **Phase 1 (2-3h)**: Core filter infrastructure
   - Add 3 OS filter aliases to COMMON_FILTERS
   - Implement 6 helper functions in convenience_tools.py
   - Add listos discovery and family lookup

2. **Phase 2 (2-3h)**: OS filtering tools
   - Add `tsc_list_os_names` discovery tool
   - Update existing tools with OS filters
   - Test with multiple OS variants

3. **Phase 3 (1-2h)**: Plugin family fix
   - Add `tsc_list_plugin_families` discovery tool
   - Fix family filter implementation
   - Update all tools with family support

4. **Phase 4 (1h)**: Testing & documentation
   - 10+ test cases for OS and family filters
   - Update FILTER_FORMAT_REFERENCE.md
   - User guide examples

#### Breaking Changes

- ⚠️ Plugin family filter behavior changes (v1.2.x was broken, v1.3.0 fixes it)
- ✅ OS filtering is new functionality (no breaking changes)

#### Deliverables

- [ ] `tsc_list_os_names` tool (OS discovery)
- [ ] `tsc_list_plugin_families` tool (family discovery)
- [ ] Updated COMMON_FILTERS with OS aliases
- [ ] Smart OS and family lookup functions
- [ ] All existing tools work with new filters
- [ ] 10+ test cases
- [ ] Documentation updates
- [ ] Version bumped to 1.3.0

---

### v1.4.0: Multi-Client API Key Support

**Status**: 📋 Ready for Implementation  
**Estimated Time**: 4-5 hours  
**Priority**: High  
**Implementation Plan**: See **[MULTI_CLIENT_API_KEYS.md](MULTI_CLIENT_API_KEYS.md)** (comprehensive 1,200+-line guide)

**Summary**: Transform MCP server from single-tenant to multi-tenant architecture.

#### Current Problem

- MCP server loads ONE set of API keys from `.env` at startup
- ALL clients share the SAME credentials
- No per-client RBAC enforcement
- Cannot support multiple users with different permission levels

#### Solution Architecture

- Add FastMCP `Context` parameter to all 15+ tools
- Store per-session `TenableScClient` instances with separate credentials
- Add `initialize_credentials` tool for clients to provide API keys
- Implement per-client cache isolation to prevent data leakage
- Support BOTH legacy `.env` mode and new per-client mode (backward compatible)

#### Implementation Phases

1. **Phase 1 (2h)**: Core Session Management
   - Add session storage with thread-safe locks
   - Implement `_client_for_session(session_id)` function
   - Add `initialize_credentials` tool
   - Per-session cache initialization

2. **Phase 2 (1.5h)**: Update All Tools
   - Add `Context` parameter to all tools
   - Update core API tools
   - Update convenience tools
   - Update cache access to use session-specific cache

3. **Phase 3 (1h)**: Testing & Validation
   - Unit tests for session management
   - Integration tests with multiple clients
   - Cache isolation verification
   - Backward compatibility tests

4. **Phase 4 (1h)**: Documentation
   - Update README with multi-client usage
   - Update DESIGN_PRINCIPLES
   - Migration guide

#### New Tool: `initialize_credentials`

**Purpose**: Allow clients to provide their own API credentials

**Parameters**:
- `ctx: Context` - MCP context (automatically provided)
- `base_url: str` - Tenable.sc URL
- `access_key: str` - API access key
- `secret_key: str` - API secret key
- `verify_ssl: bool = True`
- `cache_enabled: bool = True`
- `cache_backend: str = "memory"`

**Returns**: Session confirmation with ID and cache config

#### Benefits

- ✅ Each client isolated with own credentials
- ✅ Tenable.sc RBAC enforced per-client
- ✅ No shared cache data between clients
- ✅ Support multiple concurrent users
- ✅ Credentials never stored on disk
- ✅ Backward compatible with existing deployments

#### Breaking Changes

- None (backward compatible with `.env` mode)

#### Deliverables

- [ ] Session management implemented
- [ ] All 15+ tools updated with Context parameter
- [ ] `initialize_credentials` tool added
- [ ] Per-session cache working
- [ ] Session cleanup on disconnect
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Version bumped to 1.4.0

---

### Tool 6: Missing Patches

**Status**: ⏳ Pending | **Token Budget**: 2,000-4,000 | **Cache TTL**: 240s | **Estimated**: 2h  
**Module**: `tools/scanning.py`

#### `tsc_list_missing_patches_windows`

**Purpose**: MS bulletin-based patch gap analysis for Windows systems

**Planned Features**:
- List missing MS patches by bulletin ID
- Filter by severity (critical/important/moderate)
- Filter by release date
- Group by bulletin or by IP
- Include affected IPs per bulletin

**Use Cases**:
- Patch compliance reporting
- MS bulletin tracking
- Windows update verification
- Remediation prioritization

**Dependencies**:
- ⚠️ Requires v1.3.0 plugin family fix to be completed first

---

### Tool 7: Scan Status

**Status**: ⏳ Pending | **Token Budget**: 1,500-3,000 | **Cache TTL**: 60s | **Estimated**: 2h  
**Module**: `tools/scanning.py`

#### `tsc_scan_status`

**Purpose**: Real-time scan monitoring with filters (time, launcher, status)

**Planned Features**:
- List active/completed/failed scans
- Filter by scan status (running/completed/error)
- Filter by time range (last 24h, 7d, 30d)
- Filter by scanner/launcher
- Show scan progress percentage
- Display scan targets and results summary

**Use Cases**:
- Monitor active scans
- Troubleshoot scan failures
- Capacity planning
- Scan scheduling validation

**Dependencies**:
- ⚠️ Requires v1.3.0 plugin family fix to be completed first

---

## Future Tools (Week 2-3)

### Week 2: Essential Queries (10 tools)

**1. Tool 6: `tsc_list_missing_patches_windows`**
- **Purpose**: MS bulletin-based patch gap analysis for Windows systems
- **Token Budget**: 2,000-4,000 | **Module**: `tools/scanning.py`

**2. Tool 7: `tsc_scan_status`**
- **Purpose**: Real-time scan monitoring with filters (time, launcher, status)
- **Token Budget**: 1,500-3,000 | **Module**: `tools/scanning.py`

**3. Tool 8: `tsc_compliance_status_by_ip`**
- **Purpose**: Summary + failed compliance checks with remediation guidance (PCI-DSS, NIST, CIS, ISO 27001, HIPAA)
- **Token Budget**: 3,000-5,000 | **Module**: `tools/compliance.py`

**4. Tool 9: `tsc_resources_status`** (Admin Only)
- **Purpose**: Nessus/NNM/WAS/Proxy status with force_refresh flag
- **Token Budget**: 1,500-3,000 | **Module**: `tools/admin/resources.py`

**5. Tool 10: `tsc_list_ports`**
- **Purpose**: List open ports with combined scanner + vulnerability data
- **Token Budget**: 1,500-3,000 | **Module**: `tools/network.py`

**6. Tool 11: `tsc_list_software`**
- **Purpose**: List installed software with full filtering (performance optimization vs IP profile)
- **Token Budget**: 2,000-4,000 | **Module**: `tools/inventory.py`

**7. Tool 12: `tsc_list_services`**
- **Purpose**: List running services with full filtering (performance optimization vs IP profile)
- **Token Budget**: 2,000-4,000 | **Module**: `tools/inventory.py`

**8. Tool 13: `tsc_credential_audit`**
- **Purpose**: Credential success/failure audit per IP using plugin 19506 + auth plugins
- **Token Budget**: 2,000-4,000 | **Module**: `tools/scanning.py`

**9. Tool 14: `tsc_list_ips_by_vuln`**
- **Purpose**: Reverse lookup - list IPs affected by specific vulnerability (plugin ID or CVE)
- **Token Budget**: 2,000-4,000 | **Module**: `tools/vulnerability_lookup.py`

**10. Tool 15: `tsc_list_cves_by_ip`**
- **Purpose**: List all CVEs affecting a specific IP
- **Token Budget**: 2,000-4,000 | **Module**: `tools/vulnerability_lookup.py`

### Week 3: Advanced Features (15 tools)

**11. Tool 16: `tsc_list_scan_results`**
- **Purpose**: Detailed scan result analysis
- **Token Budget**: 3,000-5,000 | **Module**: `tools/scanning.py`

**12. Tool 17: `tsc_list_ips_by_repo`**
- **Purpose**: List all IPs in a repository or asset group (performance optimization)
- **Token Budget**: 1,500-3,000 | **Module**: `tools/asset_discovery.py`

**13. Tool 18: `tsc_get_os_by_ip`**
- **Purpose**: Get OS details per IP/asset (performance optimization vs IP profile)
- **Token Budget**: 1,000-2,000 | **Module**: `tools/asset_discovery.py`

**14. Tool 19: `tsc_profile_ips_bulk`**
- **Purpose**: Bulk IP profiling for multiple IPs at once
- **Token Budget**: 5,000-10,000 | **Module**: `tools/ip_profiling.py`

**15. Tool 20: `tsc_list_acr_by_ip`**
- **Purpose**: ACR (Asset Criticality Rating) scores per IP
- **Token Budget**: 1,500-3,000 | **Module**: `tools/asset_discovery.py`

**16. Tool 21: `tsc_list_ips_by_acr_range`**
- **Purpose**: List IPs within ACR value/range (e.g., score >= 8)
- **Token Budget**: 2,000-4,000 | **Module**: `tools/asset_discovery.py`

**17. Tool 22: `tsc_asset_group_membership`**
- **Purpose**: List all asset groups an IP belongs to (performance optimization vs IP profile)
- **Token Budget**: 1,000-2,000 | **Module**: `tools/asset_discovery.py`

**18. Tool 23: `tsc_top_vulnerable_assets`**
- **Purpose**: Most vulnerable IPs ranked by severity count
- **Token Budget**: 2,000-4,000 | **Module**: `tools/vulnerability_lookup.py`

**19. Tool 24: `tsc_plugin_update_status`** (Admin Only)
- **Purpose**: Plugin feed status monitoring
- **Token Budget**: 1,000-2,000 | **Module**: `tools/admin/resources.py`

**20. Tool 25: `tsc_license_usage`** (Admin Only)
- **Purpose**: License usage statistics
- **Token Budget**: 1,000-2,000 | **Module**: `tools/admin/resources.py`

**21. Tool 26: `tsc_repo_status`** (Admin Only)
- **Purpose**: Combined repository tool - config + utilization + capacity + trending
- **Token Budget**: 2,000-4,000 | **Module**: `tools/admin/resources.py`

**Total Planned**: 26 tools (5 completed + 21 remaining)

---

## Technical Architecture

### Design Principles

All new tools must follow these mandatory patterns (see DESIGN_PRINCIPLES.md):

1. **Unified Filters Dict**: Single `filters` parameter accepts all 71+ filters
2. **Token Optimization**: Target 80%+ reduction vs raw API
3. **Smart Caching**: Independent TTLs based on data volatility
4. **Error Handling**: Comprehensive with helpful messages
5. **Documentation**: Detailed docstrings with examples

### Filter Architecture

**71+ Universal Filters** work across all tools:
- Scoring filters (ACR, VPR, AES, CVSS, EPSS) - use range format "min-max"
- Vulnerability filters (severity, exploit, family, CVE)
- Asset filters (repository, IP, hostname, OS)
- Network filters (port, protocol)
- Temporal filters (first_seen, last_seen)

**See**: [FILTER_FORMAT_REFERENCE.md](FILTER_FORMAT_REFERENCE.md) for complete reference

### Module Structure

```
src/tenable_sc_mcp/
├── server.py               # FastMCP server, tool registration
├── convenience_tools.py    # Shared helpers, COMMON_FILTERS, discovery tools
├── client.py               # Tenable.sc API client
├── cache.py                # Caching layer (Memory/Redis)
├── catalog.py              # MCP resources
├── tools/
│   ├── ip_profiling.py    # Tool 1
│   ├── vulnerability_lookup.py  # Tools 2a, 2b, 5
│   ├── asset_discovery.py # Tool 4
│   └── [future tools]
└── resources/
    └── filter_reference.py # Filter documentation
```

### Development Workflow

For new development sessions:

1. **Read Documentation**:
   - HANDOFF.md - Current status and next priorities
   - DESIGN_PRINCIPLES.md - Mandatory patterns and architecture
   - Relevant implementation plan (OS_AND_PLUGIN_FAMILY_FIX.md or MULTI_CLIENT_API_KEYS.md)

2. **Review Code**:
   - Existing tools for patterns
   - COMMON_FILTERS for filter reference
   - convenience_tools.py for shared functions

3. **Implement**:
   - Follow v1.2.0+ unified filters pattern
   - Add to appropriate module
   - Register in server.py
   - Write tests

4. **Document**:
   - Update USER_GUIDE.md when complete
   - Update FILTER_FORMAT_REFERENCE.md if new filters
   - Update HANDOFF.md with session notes

---

## Version History

| Version | Release Date | Key Features |
|---------|-------------|--------------|
| v1.2.2 | 2026-06-19 | Repository cleanup, branch protection |
| v1.2.1 | 2026-06-12 | CPE/OS filtering with smart operators |
| v1.2.0 | 2026-06-10 | Unified filters architecture |
| v1.1.0 | 2026-05-15 | Tools 2a, 2b, 4 added |
| v1.0.0 | 2026-05-01 | Initial release, Tool 1 |
| **v1.3.0** | **TBD** | **OS filtering & plugin family fix** |
| **v1.4.0** | **TBD** | **Multi-client API key support** |

---

## Contributing

For development guidelines, see:
- **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Architecture and patterns
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[HANDOFF.md](HANDOFF.md)** - Current development status

---

**Document Version**: 2.0  
**Maintained By**: ABMJ  
**License**: GPL-3.0
