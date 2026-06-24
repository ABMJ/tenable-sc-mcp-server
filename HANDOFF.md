# Tenable.sc MCP Server - Handoff Document

**Last Updated:** 2026-06-24  
**Project Status:** ✅ v1.3.0.1 Released  
**Next Session Priority:** Tool 6 - Missing Patches (Windows)  
**Current Version:** 1.3.0.1

---

## 📋 Quick Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Current Version** | ✅ v1.3.0.1 | OS filtering & plugin family validation fixed |
| **Completed Tools** | 7/27 (26%) | Core IP profiling + vulnerability lookup + 2 helper tools |
| **Filter Count** | 74 filters | Universal filter framework (centralized in COMMON_FILTERS) |
| **Next Tool** | Tool 6 | Missing Patches (Windows) - MS bulletin tracking |
| **Pending Tools** | Tools 6-27 | See TOOLS_ROADMAP.md for complete specifications |

### v1.3.0.1 Highlights (Current Release)

- ✅ **OS Filtering**: Word-boundary matching, 74 filters, 4 OS aliases
- ✅ **Plugin Family**: Smart name→ID resolution, 123 families
- ✅ **Helper Tools**: `tsc_list_operating_systems`, `tsc_list_plugin_families`
- ✅ **Testing**: 8/8 tests passed
- ✅ **Documentation**: CHANGELOG.md, TEST_PROMPTS.md, filter reference updated

---

## 🎯 Next Priority: Tool 6 - Missing Patches (Windows)

**Tool Name:** `tsc_list_missing_patches_windows`  
**Estimated Time:** 2-3 hours  
**Token Budget:** 2,000-4,000 tokens  
**Cache TTL:** 240s (4 minutes)  
**Module:** `src/tenable_sc_mcp/tools/scanning.py`

### What This Tool Does

Provides MS bulletin-based patch gap analysis for Windows systems. Helps security teams:
- Identify missing Microsoft patches across Windows endpoints
- Prioritize patches by severity (critical/important/moderate)
- Track patch compliance by bulletin ID
- Generate remediation plans grouped by bulletin or IP

### Why This Tool Is Important

1. **Patch Management:** Windows patch compliance is critical for security
2. **MS Bulletin Tracking:** IT teams need bulletin-level visibility (not just CVE)
3. **Remediation Planning:** Grouping by bulletin helps batch deployments
4. **Compliance Reporting:** Required for many security frameworks (PCI, NIST, CIS)

### Implementation Plan

**Step 1: Create Tool Function (45 min)**

Location: `src/tenable_sc_mcp/tools/scanning.py` (new file)

```python
@mcp.tool()
def tsc_list_missing_patches_windows(
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    List missing Microsoft patches on Windows systems.
    
    Returns MS bulletin-based patch gap analysis with affected IPs,
    severity ratings, and KB article references. Use this for patch
    compliance reporting and remediation planning.
    
    Filters:
        severity: Patch severity (critical/important/moderate/low)
        release_date: Patch release date range (epoch or YYYY-MM-DD)
        bulletin_id: Specific MS bulletin ID (e.g., "MS17-010")
        repository: Repository name or ID
        ip: Specific IP address
        
    Cache: 240s TTL (patches don't change frequently)
    Token Budget: 2,000-4,000 tokens
    
    Example:
        >>> tsc_list_missing_patches_windows(filters={"severity": "critical"})
        {
            "ok": True,
            "total_bulletins": 15,
            "bulletins": [
                {
                    "bulletin_id": "MS17-010",
                    "severity": "Critical",
                    "title": "Security Update for Windows SMB Server",
                    "release_date": "2017-03-14",
                    "affected_ips": 45,
                    "kb_articles": ["KB4013389", "KB4012598"]
                }
            ]
        }
    """
    client = _client()
    cache = _get_cache()
    
    # Parse filters
    filter_dict = filters or {}
    filter_list = build_filters(**filter_dict)
    
    # Generate cache key
    cache_key = generate_cache_key(
        "analysis_missing_patches_windows",
        params=filter_dict
    )
    
    # Check cache
    if cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    
    # Build analysis query
    query = {
        "tool": "msupdate",
        "type": "vuln",
        "filters": filter_list,
    }
    
    # Execute query
    response = client.analyze(query)
    
    # Transform response to user-friendly format
    result = {
        "ok": True,
        "total_bulletins": len(response.get("results", [])),
        "bulletins": _format_bulletin_results(response),
    }
    
    # Cache result
    if cache:
        cache.set(cache_key, result, ttl_seconds=240)
    
    return result
```

**Step 2: Add Helper Function (15 min)**

```python
def _format_bulletin_results(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Transform raw API response to bulletin summary format."""
    bulletins = []
    for item in response.get("results", []):
        bulletins.append({
            "bulletin_id": item.get("msid"),
            "severity": item.get("severity", {}).get("name"),
            "title": item.get("name"),
            "release_date": item.get("publishedDate"),
            "affected_ips": item.get("ipCount", 0),
            "kb_articles": item.get("kbArticles", []),
        })
    return bulletins
```

**Step 3: Register Tool (5 min)**

Add to `src/tenable_sc_mcp/server.py`:
```python
from tenable_sc_mcp.tools.scanning import tsc_list_missing_patches_windows
```

**Step 4: Add Filter Support (30 min)**

Filters are already centralized in `COMMON_FILTERS` dict (`convenience_tools.py:110`).
The `build_filters()` function handles all 74 existing filters automatically.

For bulletin-specific filters, verify these exist:
- `severity` - Already exists (severity filter)
- `release_date` - Check if exists, add if missing
- `bulletin_id` - Add new filter for MS bulletin ID

**Step 5: Testing (45 min)**

Create `tests/test_missing_patches.py`:
```python
def test_missing_patches_basic():
    """Test basic missing patches query."""
    result = tsc_list_missing_patches_windows()
    assert result["ok"] is True
    assert "bulletins" in result

def test_missing_patches_severity_filter():
    """Test severity filter."""
    result = tsc_list_missing_patches_windows(filters={"severity": "critical"})
    assert result["ok"] is True
    assert all(b["severity"] == "Critical" for b in result["bulletins"])

def test_missing_patches_cached():
    """Test cache hit on second call."""
    result1 = tsc_list_missing_patches_windows()
    result2 = tsc_list_missing_patches_windows()
    assert result1 == result2
```

**Step 6: Documentation (15 min)**

1. Add to `TEST_PROMPTS.md` - "Show me critical missing Windows patches"
2. Update `TOOLS_ROADMAP.md` - Mark Tool 6 as ✅ Complete
3. Add entry to `CHANGELOG.md` for next release

---

## 📚 Key Documentation Files

**MUST READ BEFORE CODING:**
- `DESIGN_PRINCIPLES.md` - **CRITICAL**: Centralized filter management, smart lookup patterns, caching strategy
- `TOOLS_ROADMAP.md` - Complete specifications for Tools 6-27
- `FILTER_FORMAT_REFERENCE.md` - All 74 filters with examples

**User Documentation:**
- `README.md` - Quick start and feature overview
- `TEST_PROMPTS.md` - Comprehensive test prompts for all tools
- `USER_GUIDE.md` - Detailed guide for completed tools (1-7)
- `CHANGELOG.md` - Version history and release notes

**Developer Documentation:**
- `HANDOFF.md` - Session handoff notes (this file)
- `AGENTS.md` - Development environment setup, git workflow, common mistakes

**MCP Resources (exposed to LLM):**
- `tenable-sc://filters/reference` - Interactive filter documentation
- `tenable-sc://resources/catalog` - Available API resources
- `tenable-sc://server/info` - Server configuration and OpenAPI metadata

---

## 🔧 Development Environment

**Current Setup:**
```bash
Branch: develop
Version: 1.3.0.1
Python: 3.12
Package Manager: uv (lockfile) + pip (runtime)
Container: Docker + docker-compose
```

**Quick Start:**
```bash
# Activate venv
source .venv/bin/activate

# Install in editable mode
pip install -e .[dev]

# Run quality checks
ruff check src tests
mypy src
pytest -q

# Docker rebuild (ALWAYS use --no-cache for code changes)
docker build --no-cache -t tenable-sc-mcp:latest .
docker-compose up -d

# Check logs
docker compose logs tenable-sc-mcp -f
```

---

## 🎯 Critical Development Patterns

**Read DESIGN_PRINCIPLES.md BEFORE making changes!**

### 1. Centralized Filter Management

**Single source of truth:** `src/tenable_sc_mcp/convenience_tools.py:110`

```python
COMMON_FILTERS = {
    "severity": {
        "api_key": "severity",
        "type": "severity",
        "description": "Vulnerability severity (0-4 or info/low/medium/high/critical)",
    },
    # ... 73 more filters
}
```

**NEVER add filter parameters to tool signatures!**
```python
# ❌ WRONG - Don't add explicit filter params
def tsc_tool(severity: str = None, exploit: bool = None):
    pass

# ✅ CORRECT - Use filters dict only
def tsc_tool(filters: dict[str, Any] | None = None):
    filter_dict = filters or {}
    filter_list = build_filters(**filter_dict)  # Unpack dict
```

### 2. Smart Lookup Pattern

For human-friendly parameters (names instead of IDs):
```python
# User provides name, tool resolves to ID
repository_id = resolve_repository_name(repository_name)
```

### 3. Caching Strategy

```python
# Generate cache key (excludes pagination)
cache_key = generate_cache_key("tool_name", params=filter_dict)

# Check cache
cached = cache.get(cache_key)
if cached:
    return cached

# Execute query
result = client.analyze(query)

# Cache with appropriate TTL
cache.set(cache_key, result, ttl_seconds=240)
```

TTL Guidelines:
- Real-time data (scan status): 60s
- Semi-dynamic (vulnerabilities): 180s
- Slow-changing (patches, asset info): 240-300s
- Static (plugin families, OS list): 86400s (24h)

### 4. Scoring Filters - Range Format

**CRITICAL:** Scoring filters use RANGE format, NOT operators!

```python
# ✅ CORRECT
filters = {
    "asset_criticality": "7-10",    # Range format
    "vpr_score": "8-10",
    "cvss_v3_base_score": "7.0-10.0"
}

# ❌ WRONG - Backend doesn't support operators
filters = {
    "asset_criticality": ">7",      # Will fail
    "vpr_score": ">=8"              # Will fail
}
```

---

## 🚀 Git Workflow

**ALWAYS branch from develop:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/tool-6-missing-patches
```

**Before committing:**
```bash
ruff check src tests && mypy src && pytest -q
```

**Commit format:**
```
feat(tools): Add tsc_list_missing_patches_windows

- MS bulletin-based patch gap analysis
- Severity and date range filtering
- Grouped by bulletin with affected IP counts
- 240s cache TTL
- Token budget: 2,000-4,000

Implements Tool 6 from TOOLS_ROADMAP.md
```

**Release flow:**
```
develop → release/vX.Y.Z → main (tag) → back-merge to develop
```

---

## 📊 Project Statistics

- **Total Tools:** 7 implemented, 20 planned (27 total)
- **Total Filters:** 74 (universal across all tools)
- **Token Efficiency:** 83-90% reduction vs raw API
- **Cache Strategy:** Per-tool TTLs (60s-24h depending on data volatility)
- **Test Coverage:** 8 test cases for v1.3.0.1 (all passing)

---

## 🚨 Common Mistakes (From AGENTS.md)

1. **Branching from main** → Use `develop`
2. **Operators in scoring filters** → Use range format `"7-10"`
3. **Explicit filter params in tools** → Use `filters: dict` only
4. **Docker rebuild without `--no-cache`** → Code won't update
5. **Editing filter logic in tools** → Add to `COMMON_FILTERS` dict instead
6. **Forgetting to unpack filters dict** → Use `build_filters(**filter_dict)`

---

## 🎯 Next Steps for New Session

1. **Read This Document** - Understand current state and next priority
2. **Read DESIGN_PRINCIPLES.md** - Mandatory architecture patterns
3. **Read TOOLS_ROADMAP.md Lines 134-173** - Tool 6 complete specification
4. **Create Feature Branch** - `git checkout -b feature/tool-6-missing-patches`
5. **Implement Tool 6** - Follow the implementation plan above (2-3 hours)
6. **Test Thoroughly** - Run quality checks and pytest
7. **Update Documentation** - TEST_PROMPTS.md, TOOLS_ROADMAP.md, CHANGELOG.md
8. **Commit and Push** - Follow git workflow

---

**For next session:** Start with Tool 6 implementation following the plan above. All architecture patterns are established, filters are centralized, and the codebase is ready for new tools.
