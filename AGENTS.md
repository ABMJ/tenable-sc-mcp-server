# Agent Instructions - Tenable.sc MCP Server

**Python 3.11+ MCP server. Docker-first deployment. Currently on `develop` branch.**

---

## Essential Commands

```bash
# Local dev with venv
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]

# Run MCP server (stdio mode)
tenable-sc-mcp --transport stdio

# Quality checks (must pass before commit)
ruff check src tests    # lint
mypy src                # type check
pytest -q               # unit tests

# Docker build + run (production mode)
docker build --no-cache -t tenable-sc-mcp:latest .  # CRITICAL: --no-cache required when code changes
docker-compose up -d    # includes Redis cache

# Check container health
docker compose logs tenable-sc-mcp
docker ps --filter "name=redis"
```

---

## Architecture Essentials

### Project Structure
```
src/tenable_sc_mcp/
├── server.py               # FastMCP registration, entry point
├── client.py               # TenableScClient (REST API wrapper)
├── cache.py                # Redis/in-memory caching layer
├── convenience_tools.py    # COMMON_FILTERS dict, build_filters(), shared utils
├── catalog.py              # Resource discovery
├── tools/                  # Domain-specific tool modules
│   ├── ip_profiling.py
│   ├── vulnerability_lookup.py
│   └── asset_discovery.py
└── resources/              # MCP resources (auto-generated docs)
    └── filter_reference.py

tests/
├── test_cache.py
├── test_catalog.py
└── integration/
```

### Dependencies & Execution
- **Package manager**: pip + venv (no Poetry, no uv runtime despite lockfile)
- **Entry point**: `tenable-sc-mcp` CLI installed via `project.scripts` in pyproject.toml
- **Transport modes**: `stdio` (local), `streamable-http` (remote Docker)
- **Required env**: `TSC_URL`, `TSC_ACCESS_KEY`, `TSC_SECRET_KEY` (see `.env.example`)

---

## Tool Development Pattern (MANDATORY)

### The Critical Rule: Unified Filters Dict

**ALL new tools with filter support MUST use this exact pattern:**

```python
@mcp.tool()
def tsc_tool_name(
    required_param: str,
    filters: dict[str, Any] | None = None,  # ✅ Single filter dict
) -> dict[str, Any]:
    """
    [Description]
    
    Args:
        required_param: ...
        filters: Optional filter parameters. Reference: tenable-sc://filters/reference
            Common filters:
                asset_criticality: ACR range (e.g., "7-10")
                severity: critical/high/medium/low/info
                exploit_available: Yes/No
    """
    filter_dict = filters or {}
    filter_list = build_filters(**filter_dict)  # ✅ Unpack dict
    # ... use filter_list in API query
```

**Never:**
- ❌ Explicit filter parameters (`asset_criticality: str | None`, `severity: str | None`)
- ❌ Manual filter mapping inside tool function
- ❌ Duplicate filter logic across files

**Single source of truth:**  
`COMMON_FILTERS` dict in `convenience_tools.py` (74 filters)

---

## Key Constraints

### Scoring Filters
**Range format required:** `"7-10"` NOT `">7"` or `">=7"`

Applies to: `asset_criticality`, `vpr_score`, `aes_score`, `cvss_v3_base_score`, `epss_score`

Example: `filters={"asset_criticality": "8-10", "vpr_score": "7-10"}`

### Caching
- **Backend**: Redis (production), in-memory (fallback)
- **TTLs**: 60s-300s based on data volatility
- **Key pattern**: `tool_name:param_hash` (pagination params excluded)
- **Cache control**: `tsc_cache_stats()`, `tsc_cache_clear()`

### Error Handling
- Return `{"ok": False, "error": "...", "hint": "..."}` for failures
- Log warnings (not errors) for unknown filter params
- Never expose raw API errors to users

---

## Git Workflow

### Branch Strategy
```
main (production, protected)
  └── develop (integration)
       ├── feature/tool-name
       ├── bugfix/issue-desc
       └── docs/doc-updates
```

### Current Branch: `develop`
**All feature work merges to `develop` first, not `main`.**

### Standard Feature Flow
```bash
# 1. Start from develop
git checkout develop && git pull

# 2. Create feature branch
git checkout -b feature/new-tool

# 3. Develop + test
ruff check . && mypy src && pytest -q

# 4. Commit with convention
git commit -m "feat(tools): Add tsc_new_tool"

# 5. Push and PR to develop
git push -u origin feature/new-tool
gh pr create --base develop
```

### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `test`: Tests added/updated
- `chore`: Build/tooling

**Format:** `<type>(<scope>): <subject>`  
**Example:** `feat(tools): Add OS listing tool`

### Release Flow (develop → main)
1. Create `release/vX.Y.Z` from `develop`
2. Bump version in `pyproject.toml`
3. Final testing (no new features)
4. PR to `main` → merge → tag
5. Merge back to `develop` (critical!)

---

## Testing Requirements

**Before committing:**
```bash
ruff check src tests  # Must pass
mypy src             # Must pass
pytest -q            # Must pass (>80% coverage preferred)
```

**Test structure:**
- Unit tests: `tests/test_*.py`
- Integration: `tests/integration/` (requires Tenable.sc instance)

---

## Common Mistakes to Avoid

1. **Using explicit filter parameters instead of `filters: dict`**
   - Old pattern (deprecated): `def tool(ip: str, severity: str | None)`
   - Correct: `def tool(ip: str, filters: dict[str, Any] | None)`

2. **Using operators in scoring filters**
   - Wrong: `{"asset_criticality": ">7"}`
   - Correct: `{"asset_criticality": "7-10"}`

3. **Branching from `main` instead of `develop`**
   - Feature branches MUST start from `develop`

4. **Not running quality checks before commit**
   - CI will fail if ruff/mypy/pytest don't pass locally

5. **Editing filter logic in tools directly**
   - Add filters to `COMMON_FILTERS` dict, not individual tools

6. **Forgetting `--no-cache` on Docker rebuild**
   - Code changes won't appear without it due to layer caching

---

## Key Documentation

- **DESIGN_PRINCIPLES.md**: Mandatory patterns for all tools
- **FILTER_FORMAT_REFERENCE.md**: Complete filter reference (74 filters)
- **ARCHITECTURE.md**: System design and component interaction
- **USER_GUIDE.md**: Tool usage examples and best practices (7 tools documented)
- **TOOLS_ROADMAP.md**: Pending Tools 6-27 specifications
- **HANDOFF.md**: Next session priorities (v1.4.0 focus)
- **CACHING_DEEP_DIVE.md**: Cache behavior and tuning

**MCP Resource for LLMs:** `tenable-sc://filters/reference` (auto-generated filter docs)

---

## Environment Setup

**Required `.env` file:**
```bash
TSC_URL=https://your-sc-server.com
TSC_ACCESS_KEY=your-access-key
TSC_SECRET_KEY=your-secret-key
TSC_VERIFY_SSL=true
TSC_CACHE_ENABLED=true
TSC_CACHE_BACKEND=redis  # or "memory"
TSC_CACHE_REDIS_HOST=redis
TSC_CACHE_REDIS_PORT=6379
```

**Docker Compose reads `.env` automatically.**

---

## Quick Reference

| Task | Command |
|------|---------|
| Install dev deps | `pip install -e .[dev]` |
| Run server (local) | `tenable-sc-mcp --transport stdio` |
| Run server (remote) | `tenable-sc-mcp --transport streamable-http --port 8000` |
| Lint | `ruff check .` |
| Type check | `mypy src` |
| Test | `pytest -q` |
| Docker build | `docker build --no-cache -t tenable-sc-mcp:latest .` |
| Docker run | `docker-compose up -d` |
| View logs | `docker compose logs tenable-sc-mcp` |
| Git feature start | `git checkout develop && git checkout -b feature/name` |
| Git commit | `git commit -m "feat(scope): description"` |

---

**Last Updated**: 2026-06-21 (aligned with v1.3.0.1)
