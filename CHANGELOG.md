# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0.1] - 2026-06-20

### Fixed
- **Critical: Windows 11 false positives in OS filtering** - Fixed token-based matching to use word boundaries for numeric version tokens (e.g., "Windows 10" no longer matches "Windows 11")
- **Critical: Multi-OS entries excluded from results** - Fixed server exclusion logic to include ambiguous multi-OS detections (e.g., "Microsoft Windows 7, Microsoft Windows Server 2008 R2, Microsoft Windows 10, ...")
- **Critical: Plugin family validation broken** - Fixed `get_plugin_families()` and `resolve_plugin_family_id()` to use correct `client.request()` API calls instead of non-existent `client.get()` method
- **Critical: Invalid plugin families silently ignored** - Added proper validation that raises `ValueError` for invalid family names, preventing unfiltered results from leaking

### Changed
- **Architecture: Simplified OS filtering** - Removed OS filter support from `tsc_list_vulns_by_cve` (~150 lines removed). LLM now orchestrates multi-step workflows (CVE query → profile IPs → filter by OS) for better flexibility and transparency
- **Docker: Build process** - Developers must now use `docker-compose build --no-cache` when debugging Python code changes to avoid Docker layer caching issues

### Added
- **Tool: tsc_list_operating_systems** - Discover valid OS names from Tenable.sc for filtering (300s cache TTL)
- **Tool: tsc_list_plugin_families** - Discover valid plugin families with IDs for filtering (24h cache TTL)
- **Filter aliases:** Added 4 OS filter aliases (operating_system, os_name, os_exact, os) - all support smart matching with word-boundary awareness

### Technical Details
- 6 helper functions added to `convenience_tools.py` for OS/family smart lookup
- `build_filters()` now returns tuple `(filters_list, os_names_list)` for multi-query execution
- Multi-query OS filtering: Execute N separate API calls (one per matched OS) instead of single query with OR logic
- Smart OS matching: Token-based algorithm with word-boundary matching for numeric versions against live `listos` API data
- Plugin family validation: Name→ID resolution with case-insensitive lookup and partial matching
- Response format includes per-OS variant breakdown and deduplication stats

### Test Results (8/8 Passed)
1. ✅ OS filtering with multi-OS entries (11 variants, 35 IPs)
2. ✅ CVE search regression (20 IPs with Log4Shell)
3. ✅ Vulnerability summary by IP (78 critical vulns)
4. ✅ Detailed vulnerability records (10/78 with pagination)
5. ✅ Plugin family listing (123 families)
6. ✅ Family filter "Misc." + CVE (16 IPs)
7. ✅ Family filter by ID 20 (164 IPs)
8. ✅ Invalid family error handling (proper error message)

### Files Changed
- `src/tenable_sc_mcp/convenience_tools.py` - 674 lines added (OS/family helpers, build_filters tuple return)
- `src/tenable_sc_mcp/tools/asset_discovery.py` - Multi-query OS filtering, deduplication
- `src/tenable_sc_mcp/tools/admin/plugins.py` - New tsc_list_plugin_families tool
- `src/tenable_sc_mcp/tools/vulnerability_lookup.py` - OS filter removed from tsc_list_vulns_by_cve
- `TEST_PROMPTS.md` - Updated with 8 comprehensive test prompts

### Migration Notes
- OS filtering in `tsc_list_vulns_by_cve` now returns error directing users to multi-step workflow
- Plugin family filter now validates input - invalid families will raise clear error instead of silently returning unfiltered results
- Docker containers must be rebuilt with `--no-cache` flag when testing Python code changes

---

## [1.2.1] - 2026-06-12

### Features
- **Smart CPE/OS Filtering** - Auto-detects operators (contains/exact/regex) based on input pattern
- Added `cpe` and `os_cpe` filter parameters (71 total filters)
- Zero-configuration operator detection for intuitive filtering

### Bug Fixes
- Fixed MCP resource documentation generation (brace escaping)
- Resource `tenable-sc://filters/reference` now loads correctly

### Documentation
- Added comprehensive regex pitfall guidance
- Enhanced FILTER_FORMAT_REFERENCE.md with best practices
- Updated branch protection instructions for GitHub Rulesets

### Technical Details
- Token efficiency maintained: 58-92% reduction vs raw API
- All 5 tools functional with CPE support
- Severity string conversion verified working

---

## [1.2.0] - 2026-06-10

### Changed
- Unified filters dict pattern across all tools

---

## [0.1.0] - 2026-04-30

### Added
- Initial release of Tenable Security Center MCP Server
- Core API client with authentication
- Basic vulnerability and asset discovery tools
- MCP server implementation with stdio transport
