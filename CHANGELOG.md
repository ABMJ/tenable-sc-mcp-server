# Changelog

All notable changes to the Tenable.sc MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.1] - 2026-06-24

### Added
- **Tool 6: `tsc_list_missing_patches`** - Patch gap analysis tool for comprehensive patch management
  - Universal mode (Plugin 66334): All OS types + third-party software (Chrome, Office, VMware, etc.)
  - Windows mode (Plugin 38153): Windows KB articles and legacy MS bulletins
  - Supports all 74+ universal filters (repository, asset_criticality, severity, etc.)
  - Smart parsing: Extracts KB IDs, third-party software, vulnerability counts
  - Repository name auto-resolution (e.g., "Default" → ID 9)
  - Token efficient: 700-20,000 tokens depending on scope
  - Cache: 240s (4 minute) TTL
  - Pagination: Returns up to 50 IPs per query
  - Empty result validation: Distinguishes "no patches" vs "IP/repo doesn't exist"

### Fixed
- **Patch Management Tool**: 6 critical bugs fixed during implementation
  - Filter name mapping: `pluginID` → `plugin_id` (COMMON_FILTERS compatibility)
  - Response parsing: Handle double-nested `response.response.results` structure
  - Query structure: Nested query object format matching Tenable.sc UI exactly
  - Pagination: Added required `startOffset`/`endOffset`/`vulnTool` parameters
  - Error handling: API failure detection and helpful error messages
  - Validation: Empty result messaging with troubleshooting guidance

### Changed
- Updated USER_GUIDE.md with comprehensive Tool 6 documentation (Section 8)
- Updated TEST_PROMPTS.md with 6 test scenarios for Tool 6 (lines 477-666)
- Changed test prompts from "Production" to "Default" repository (more common)
- Added single-IP filters to test prompts for token efficiency in large environments

### Documentation
- Added TEST_RESULTS_TOOL6_SESSION.md with comprehensive test results
  - All 6 Tool 6 tests documented (5 PASS, 1 expected fail)
  - Verification of 6 other tools (all working)
  - 45+ tests executed, 95% pass rate, 119K tokens total
  - Known limitations and troubleshooting guidance
- Updated version references across documentation from v1.3.0.1 → v1.3.1

---

## [1.3.0.1] - 2026-06-20

### Changed
- Updated USER_GUIDE.md with improved Tool 5 examples and filter documentation
- Updated MCP registry metadata with complete tool descriptions
- Optimized AGENTS.md to reduce verbosity while preserving design principles reference

### Removed
- Removed obsolete documentation files (old roadmap documents)
- Removed all v1.4.0 multi-client references (deferred to future release)

---

## [1.3.0] - 2026-06-18

### Added
- **Tool 5: `tsc_list_vulns_by_cve`** - CVE search across infrastructure
  - Emergency outbreak response capability
  - Returns unique affected IPs with severity counts
  - Supports 50+ analysis filters
  - Token efficient: ~800-1,500 tokens (85% reduction vs raw API)
  - Cache: 240s (4 minute) TTL
  - Pagination: Default 200 records per request

- **Tool 6: `tsc_list_operating_systems`** - OS name discovery
  - Lists all detected operating system names from Tenable.sc
  - Essential for using `operating_system` filter correctly
  - Cache: 300s (5 minute) TTL
  - Token efficient: ~500-1,000 tokens

- **Tool 7: `tsc_list_plugin_families`** - Plugin family discovery
  - Lists all 123 plugin families with IDs and names
  - Smart name→ID resolution for `family` filter
  - Cache: 86400s (24 hour) TTL
  - Token efficient: ~3,000-4,000 tokens

### Fixed
- Tool 5: Repository filter name-to-ID resolution working correctly
- Tool 5: Empty result validation distinguishes "no CVE found" vs "IP doesn't exist"

---

## [1.2.0] - 2026-06-15

### Added
- **Tool 4: `tsc_list_ips`** - IP discovery and asset enumeration
  - List IPs by repository, asset group, or reverse lookup (find IP membership)
  - Optional detailed metadata: DNS name, MAC, UUID, ACR, AES, OS
  - Supports 55+ filters: asset_criticality, severity, exploit_available, VPR, CVSS, port, protocol
  - Smart caching with 120s TTL
  - Token efficient: 400-3,700 tokens depending on dataset size

### Changed
- Centralized filter management: All tools now use `COMMON_FILTERS` dict pattern
- Improved error handling across all tools with helpful validation messages

---

## [1.1.0] - 2026-06-10

### Added
- **Tool 2a: `tsc_list_vulns_by_ip_summary`** - Quick vulnerability count
  - Aggregated counts by severity
  - Token efficient: ~700 tokens (88% reduction vs full details)
  - Cache: 180s (3 minute) TTL

- **Tool 2b: `tsc_list_vulns_by_ip_full`** - Detailed vulnerability records
  - Complete vulnerability records with all metadata
  - Supports pagination (10-200 records per request)
  - Token efficient: ~5,000 tokens for 50 records (58% reduction)
  - Cache: 180s (3 minute) TTL

### Changed
- Split vulnerability lookup into two tools (summary vs full) for better token efficiency

---

## [1.0.0] - 2026-06-05

### Added
- **Initial Release**: Production-ready Tenable.sc MCP Server
- **Tool 1: `tsc_profile_ip_efficient`** - Complete IP security profile
  - Combines 6 optimized queries with separate caching
  - Token efficient: ~2,500 tokens (83% reduction vs unoptimized)
  - Cache: 180s for vulnerability data, 300s for static data
  - Includes: vulnerability summary, OS, software, services, scan status, asset groups

### Infrastructure
- Docker-first deployment with Docker Compose
- Redis caching layer with in-memory fallback
- FastMCP framework integration
- Comprehensive error handling and validation
- 21+ unit tests with pytest
- Code quality gates: ruff, mypy, pytest
- Python 3.11+ support

### Documentation
- USER_GUIDE.md with comprehensive examples
- TEST_PROMPTS.md with test scenarios
- DESIGN_PRINCIPLES.md with architecture patterns
- FILTER_FORMAT_REFERENCE.md with all 74 filters
- AGENTS.md with development workflow

---

## Legend

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
