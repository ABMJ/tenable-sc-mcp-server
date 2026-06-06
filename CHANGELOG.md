# Changelog

All notable changes to this project are documented in this file.

## v0.2.0 - 2026-06-06

### Added
- Smart TTL optimization for analysis queries based on query type
- Dynamic cache lifetime: IP/asset queries (5 min), vulnerability queries (3 min), real-time (1 min)
- Comprehensive test coverage for smart TTL functionality

### Changed
- Increased base TTLs for better cache hit rates:
  - `asset`: 300s → 600s (10 minutes)
  - `scanResult`: 60s → 300s (5 minutes)
  - `analysis`: Now uses smart TTL (120-300s based on query type)
- Updated CACHING_DEEP_DIVE.md with smart TTL architecture
- Archived historical session documentation to docs/archive/
- Cleaned up documentation structure

### Fixed
- Critical caching bug: POST /analysis queries now properly cached
- Expected cache hit rate improvement: 16% → 60-80%

## Unreleased

- Added explicit "not officially supported by Tenable" disclaimers across governance and support docs.
- Added architecture overview section to README.
- Added milestone-aligned roadmap in `docs/roadmap.md`.
- Added CI workflow for linting, type checks, and tests on push/PR.
- Added community and governance docs: `SECURITY.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, and PR template.
- Added Dependabot configuration for Python and GitHub Actions updates.
- Added minimal pytest suite and release checklist under `docs/releasing.md`.
- Added README badges and compatibility/support policy details.

## v0.1.0 - 2026-04-30

- Initial public release of `tenable-sc-mcp`.
- Added generic Tenable.sc MCP tooling including `tsc_catalog`, `tsc_resource_docs`, `tsc_current_user`, `tsc_resource_action`, and `tsc_request`.
- Added compatibility aliases (`tsc_list`, `tsc_get`, `tsc_create`, `tsc_update`, `tsc_delete`) for existing clients.
- Added deployment guidance for local, Docker, Docker Compose, and remote MCP usage.
