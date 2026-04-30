# Changelog

All notable changes to this project are documented in this file.

## Unreleased

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
