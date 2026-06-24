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


## 🎯 Next Priority: Tool 6 - Missing Patches

**Tool Name:** `tsc_list_missing_patches`  
**Estimated Time:** 3-4 hours  
**Token Budget:** 2,000-5,000 tokens  
**Cache TTL:** 240s (4 minutes)  
**Module:** `src/tenable_sc_mcp/tools/patch_management.py` (new file)

### What This Tool Does

Provides universal patch gap analysis across all operating systems (Windows, Linux, macOS) with KB article tracking. Uses Tenable plugins:
- **Plugin 66334** - Universal patch report (all OS + third-party software)
- **Plugin 38153** - Windows KB-specific summary

Helps security teams:
- Identify missing patches across entire infrastructure
- Track Microsoft KB articles with superseded KB relationships
- Monitor third-party software updates (Chrome, VMware Tools, etc.)
- Generate remediation plans grouped by IP or patch

### Why This Tool Is Important

1. **Universal Coverage:** Works on Windows, Linux, macOS, Unix - not just Windows
2. **Third-Party Tracking:** Includes Chrome, Office, VMware, Nessus Agent patches
3. **KB Relationships:** Shows which KBs are superseded by rollups
4. **Compliance Reporting:** Required for PCI, NIST, CIS frameworks

### Implementation Plan

**Step 1: Create Tool Function (1h)**

Location: `src/tenable_sc_mcp/tools/patch_management.py` (new file)

```python
import re
from html import unescape
from typing import Any

@mcp.tool()
def tsc_list_missing_patches(
    mode: str = "universal",  # "universal" or "windows"
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    List missing patches across all operating systems.
    
    Uses Tenable plugins to detect missing patches:
    - Plugin 66334 (universal): All OS + third-party software
    - Plugin 38153 (windows): Windows KB-specific
    
    Args:
        mode: "universal" (plugin 66334) or "windows" (plugin 38153)
        filters: Standard filters (ip, repository, etc.)
    
    Returns:
        Patch gap analysis grouped by IP with KB articles
    
    Example:
        >>> tsc_list_missing_patches(mode="universal", filters={"ip": "10.1.20.10"})
        {
            "ok": True,
            "mode": "universal",
            "total_affected_ips": 1,
            "patches_by_ip": [...]
        }
    """
    client = _client()
    cache = _get_cache()
    
    # Select plugin based on mode
    plugin_id = "66334" if mode == "universal" else "38153"
    
    # Parse filters and add plugin ID filter
    filter_dict = filters or {}
    filter_dict["pluginID"] = plugin_id
    filter_list = build_filters(**filter_dict)
    
    # Generate cache key
    cache_key = generate_cache_key(
        f"missing_patches_{mode}",
        params=filter_dict
    )
    
    # Check cache
    if cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    
    # Query using vulndetails to get plugin output
    query = {
        "tool": "vulndetails",
        "type": "vuln",
        "filters": filter_list,
    }
    
    # Execute query
    response = client.analyze(query)
    
    # Parse plugin text for each IP
    patches_by_ip = []
    for result in response.get("results", []):
        plugin_text = result.get("pluginText", "")
        parsed = parse_patch_report(plugin_text, plugin_id)
        
        patches_by_ip.append({
            "ip": result.get("ip"),
            "hostname": result.get("dnsName"),
            "os": result.get("operatingSystem"),
            "repository": result.get("repository", {}).get("name"),
            **parsed
        })
    
    result = {
        "ok": True,
        "mode": mode,
        "total_affected_ips": len(patches_by_ip),
        "patches_by_ip": patches_by_ip,
    }
    
    # Cache result
    if cache:
        cache.set(cache_key, result, ttl_seconds=240)
    
    return result
```

**Step 2: Add Parsing Functions (1h)**

```python
def parse_patch_report(plugin_text: str, plugin_id: str) -> dict[str, Any]:
    """Parse patch report from plugin text."""
    # HTML unescape
    text = unescape(plugin_text)
    text = re.sub(r'</?plugin_output>', '', text)
    
    if plugin_id == "66334":
        return parse_plugin_66334(text)
    else:  # 38153
        return parse_plugin_38153(text)

def parse_plugin_66334(text: str) -> dict[str, Any]:
    """Parse universal patch report (plugin 66334)."""
    microsoft_kbs = []
    third_party = []
    
    # Extract Microsoft KB patches
    kb_pattern = r'- (KB\d+)(?: \((\d+) vulnerabilities\))?'
    for match in re.finditer(kb_pattern, text):
        kb_id = match.group(1)
        vuln_count = int(match.group(2)) if match.group(2) else None
        microsoft_kbs.append({
            "kb_id": kb_id,
            "vulnerability_count": vuln_count
        })
    
    # Extract third-party software
    software_pattern = r'\[ (.+?) \]'
    for match in re.finditer(software_pattern, text):
        third_party.append({
            "software": match.group(1)
        })
    
    return {
        "total_missing_patches": len(microsoft_kbs) + len(third_party),
        "microsoft_kbs": microsoft_kbs,
        "third_party": third_party
    }

def parse_plugin_38153(text: str) -> dict[str, Any]:
    """Parse Windows KB summary (plugin 38153)."""
    kb_list = []
    
    # Extract KB articles
    kb_pattern = r'(KB\d+)'
    for match in re.finditer(kb_pattern, text):
        kb_id = match.group(1)
        kb_list.append({
            "kb_id": kb_id,
            "url": f"https://support.microsoft.com/en-us/help/{kb_id}"
        })
    
    # Extract legacy MS bulletins
    ms_pattern = r'(MS\d{2}-\d+)'
    for match in re.finditer(ms_pattern, text):
        kb_list.append({
            "bulletin_id": match.group(1)
        })
    
    return {
        "total_missing_kbs": len(kb_list),
        "missing_kbs": kb_list
    }
```

**Step 3: Register Tool (10 min)**

Add to `src/tenable_sc_mcp/server.py`:
```python
from tenable_sc_mcp.tools.patch_management import register_tools as register_patch_tools
register_patch_tools(mcp)
```

**Step 4: Testing (1h)**

Create `tests/test_patch_management.py`:
```python
def test_missing_patches_universal():
    """Test universal patch report (plugin 66334)."""
    result = tsc_list_missing_patches(mode="universal")
    assert result["ok"] is True
    assert "patches_by_ip" in result

def test_missing_patches_windows():
    """Test Windows KB report (plugin 38153)."""
    result = tsc_list_missing_patches(mode="windows")
    assert result["ok"] is True
    assert result["mode"] == "windows"

def test_patch_parsing_66334():
    """Test parsing plugin 66334 output."""
    sample_text = """<plugin_output>
    - KB5025279 (85 vulnerabilities)
    [ Google Chrome < 113.0.5672.63 ]
    </plugin_output>"""
    
    result = parse_plugin_66334(sample_text)
    assert len(result["microsoft_kbs"]) == 1
    assert len(result["third_party"]) == 1
```

**Step 5: Documentation (30 min)**

1. Add to `TEST_PROMPTS.md`: "Show me missing patches for IP 10.1.20.10"
2. Update `TOOLS_ROADMAP.md`: Mark Tool 6 as ✅ Complete
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
