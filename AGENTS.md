# Agent Instructions - Tenable.sc MCP Server

**Python 3.11+ MCP server. Docker-first deployment. Currently on `develop` branch.**

> **📐 CRITICAL REFERENCE**: Before making ANY code changes, consult **DESIGN_PRINCIPLES.md** for mandatory architecture patterns:
> - Centralized Filter Management (filters dict pattern)
> - Smart Lookup & Helper Tool patterns
> - Caching strategy, error handling, git workflow
> - This document contains the authoritative "why" and "how" for all development decisions.

---

## Critical Gotchas

### Docker: Must rebuild with `--no-cache`
```bash
docker build --no-cache -t tenable-sc-mcp:latest .
```
Layer caching prevents code changes from appearing. Always use `--no-cache` when src/ changes.

### Filters: Range format, NOT operators
```python
# ✅ Correct
filters={"asset_criticality": "7-10", "vpr_score": "8-10"}

# ❌ Wrong - will fail
filters={"asset_criticality": ">7", "vpr_score": ">=8"}
```
Applies to: `asset_criticality`, `vpr_score`, `aes_score`, `cvss_v3_base_score`, `epss_score`

### Single source of truth: COMMON_FILTERS dict
Location: `src/tenable_sc_mcp/convenience_tools.py:110`

**Never** add filter parameters to tool signatures. **Never** duplicate filter logic.
All 74 filters live in this dict. Add new filters here only.

---

## Tool Development Pattern (MANDATORY)

```python
@mcp.tool()
def tsc_tool_name(
    required_param: str,
    filters: dict[str, Any] | None = None,  # ✅ Only way to accept filters
) -> dict[str, Any]:
    filter_dict = filters or {}
    filter_list = build_filters(**filter_dict)  # ✅ Unpack, don't map manually
    # Use filter_list in query
```

Reference: `tenable-sc://filters/reference` (MCP resource, auto-generated from COMMON_FILTERS)

---

## Git Workflow

**Branch from `develop`, NOT `main`:**
```bash
git checkout develop && git pull
git checkout -b feature/tool-name
```

**Before committing:**
```bash
ruff check src tests && mypy src && pytest -q  # All must pass
```

**Commit format:**
```
<type>(<scope>): <subject>
```
Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Release flow:** `develop` → `release/vX.Y.Z` → `main` (tag) → back-merge to `develop`

---

## Dev Commands

```bash
# Local dev
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
tenable-sc-mcp --transport stdio

# Docker (production)
docker build --no-cache -t tenable-sc-mcp:latest .
docker-compose up -d
docker compose logs tenable-sc-mcp

# Tests
pytest -q                    # All tests
pytest tests/test_file.py    # Single file
pytest -k test_name          # Single test

# Quality gates (must pass)
ruff check src tests
mypy src
pytest -q
```

---

## Project Structure

```
src/tenable_sc_mcp/
├── server.py               # FastMCP entry point, tool registration
├── client.py               # TenableScClient (REST wrapper)
├── cache.py                # Redis/memory cache layer
├── convenience_tools.py    # COMMON_FILTERS (line 110), build_filters (line 764)
├── tools/                  # Domain-specific tool modules
│   ├── ip_profiling.py
│   ├── vulnerability_lookup.py
│   ├── asset_discovery.py
│   └── admin/plugins.py
└── resources/              # MCP resources (auto-generated docs)
```

---

## Environment Variables

Required in `.env` (Docker Compose reads automatically):
```bash
TSC_URL=https://sc.example.com
TSC_ACCESS_KEY=your-key
TSC_SECRET_KEY=your-secret
TSC_VERIFY_SSL=true
TSC_CACHE_BACKEND=redis          # or "memory"
TSC_CACHE_REDIS_HOST=redis
```

---

## Package Manager Quirks

- **Lockfile uses uv**, but **execution uses pip + venv** (no Poetry, no uv runtime)
- **Entry point**: `tenable-sc-mcp` installed via `pyproject.toml` scripts
- **Install:** `pip install -e .` (editable) or `pip install -e .[dev]` (with test tools)

---

## Caching

- **Backend**: Redis (production), in-memory (fallback)
- **TTLs**: 60s-300s by data type
- **Key pattern**: `tool_name:param_hash` (pagination excluded from hash)
- **Control**: `tsc_cache_stats()`, `tsc_cache_clear(pattern=None)`

---

## Common Mistakes

1. **Branching from `main`** → Use `develop`
2. **Operators in scoring filters** → Use range format `"7-10"`
3. **Explicit filter params in tools** → Use `filters: dict` only
4. **Docker rebuild without `--no-cache`** → Code won't update
5. **Editing filter logic in tools** → Add to `COMMON_FILTERS` dict instead

---

## Documentation

**For development:**
- DESIGN_PRINCIPLES.md - Architecture patterns (read this first)
- FILTER_FORMAT_REFERENCE.md - All 74 filters
- TOOLS_ROADMAP.md - Pending features

**For users:**
- USER_GUIDE.md - Tool examples
- TEST_PROMPTS.md - Test queries

---

**Last Updated**: 2026-06-24
