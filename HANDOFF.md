# Tenable.sc MCP Server - Handoff Document

**Last Updated:** 2026-06-24  
**Project Status:** ✅ Tool 7 Complete (Ready for v1.4.0 Release)  
**Next Session Priority:** Tool 8 - Compliance Summary  
**Current Version:** 1.3.1 (develop branch has Tool 7, not yet released)

---

## 📋 Quick Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Current Version** | ✅ v1.3.1 | Released to main (Tool 6 complete) |
| **Develop Branch** | ✅ Tool 7 Complete | Ready to merge to main as v1.4.0 |
| **Completed Tools** | 9/27 (33%) | Core tools + scan monitoring |
| **Filter Count** | 74 filters | Universal filter framework (centralized in COMMON_FILTERS) |
| **Next Tool** | Tool 8 | Compliance Summary - sumseverity API with compliance filters |
| **Pending Tools** | Tools 8-27 | See TOOLS_ROADMAP.md for complete specifications |

### Tool 7 Status (On Develop Branch)

- ✅ **Implementation**: `src/tenable_sc_mcp/tools/scanning.py` (377 lines, 13K)
- ✅ **Tests**: Helper function tests passing, integration tests present
- ✅ **Documentation**: USER_GUIDE.md Section 9, TEST_PROMPTS.md Tool 7, TOOLS_ROADMAP.md updated
- ✅ **Merged**: Feature branch merged to develop (commit `b309539`)
- ⏳ **Release**: Ready to merge develop → main as v1.4.0

---

## 🎯 Next Priority: Tool 8 - Compliance Summary

**Tool Name:** `tsc_compliance_summary`  
**Estimated Time:** 3-4 hours  
**Token Budget:** 700-1,500 tokens  
**Cache TTL:** 180s (3 minutes)  
**Module:** `src/tenable_sc_mcp/tools/compliance.py` (new file)

### What This Tool Does

Provides compliance audit summary using Tenable.sc's sumseverity analysis tool with `pluginType=compliance` filter. Translates severity levels to audit outcomes:
- **High severity** → Failed audit tests
- **Medium severity** → Manual verification needed
- **Info severity** → Passed audit tests

Aggregates compliance results across all audit files (CIS, PCI, HIPAA, custom policies) to give overall compliance posture.

### Why This Tool Is Important

1. **Executive Dashboard:** Quick compliance percentage across infrastructure
2. **Risk Prioritization:** Focus remediation on failed checks (High severity)
3. **Audit Readiness:** Track manual verification items (Medium severity)
4. **Trend Analysis:** Monitor compliance improvement over time
5. **Asset Scoping:** Filter by ACR, IP, or criticality for targeted reporting

### Key API Insights

1. **Analysis Tool:** Uses `sumseverity` with `pluginType=compliance` filter
2. **Severity Mapping:**
   - Critical/Low: Rarely used for compliance
   - High: Failed audit tests (remediation required)
   - Medium: Manual verification needed (human review)
   - Info: Passed audit tests (compliant)
3. **Query Structure:** Requires nested format:
   ```json
   {
     "type": "vuln",
     "query": {
       "type": "vuln",
       "tool": "sumseverity",
       "filters": [...]
     },
     "sourceType": "cumulative"
   }
   ```
4. **Response Format:** Returns severity counts in nested structure:
   - `response.response.results[]` (double-nested!)

### Implementation Plan

**Step 1: Create Core Function (1.5h)**

Location: `src/tenable_sc_mcp/tools/compliance.py` (new file)

Key features:
- Extract core logic to `_get_compliance_summary_core()` for testability
- Use `build_filters(client=_client(), **filter_dict)` for smart lookups
- Mandatory `plugin_type=compliance` filter
- Parse nested response structure
- Calculate compliance percentage: `(passed / (passed + failed)) * 100`

**Step 2: Testing (1h)**

Create simple integration tests:
- Global compliance summary (no filters)
- Compliance by asset criticality (ACR filter)
- Empty result handling

**Note:** Repository filter has API limitations (requires array with IDs) - document as known limitation.

**Step 3: Documentation (0.5-1h)**

- USER_GUIDE.md Section 10
- TEST_PROMPTS.md with 5 test scenarios
- TOOLS_ROADMAP.md progress update (10/27)

### Known Challenges

1. **Repository Filter:** API expects `[{id: 9}]` format, not string name
   - Workaround: Use IP or asset_criticality filters instead
   - Document as limitation for now

2. **Audit File Identification:** Cannot determine which audit file was run
   - Tool aggregates across ALL audit files
   - No way to filter by specific audit policy

3. **Response Nesting:** API returns `response.response.results` (double-nested)
   - Need careful parsing to extract results

### Reference Materials

- TOOLS_ROADMAP.md: Full Tool 8 specification
- DESIGN_PRINCIPLES.md: Filter patterns and caching strategy
- Tool 6 (`patch_management.py`): Similar analysis tool pattern
    params = {
        "fields": "id,name,status,totalIPs,completedIPs,completedChecks,totalChecks,startTime,finishTime,scanDuration,importStatus,importStart,importFinish,importDuration,errorDetails,importErrorDetails,scan,repository,initiator",
        "startTime": str(start_epoch),
        "endTime": str(end_epoch)
    }
    
        return (now - 2592000, now)
    else:
        # Default to 24h
        return (now - 86400, now)

def calculate_progress(result: dict) -> dict:
    """Calculate scan progress metrics."""
    completed = int(result.get("completedIPs", 0))
    total = int(result.get("totalIPs", 1))
    percent = (completed / total * 100) if total > 0 else 0
    
    # Time estimation
    start = int(result.get("startTime", 0))
    now = int(time.time())
    elapsed = now - start if start > 0 else 0
    
    ips_per_hour = (completed / elapsed * 3600) if elapsed > 0 else 0
    remaining_ips = total - completed
    estimated_seconds = (remaining_ips / ips_per_hour * 3600) if ips_per_hour > 0 else 0
    
    return {
        "ips_completed": completed,
        "ips_total": total,
        "percent": round(percent, 1),
        "checks_completed": int(result.get("completedChecks", 0)),
        "checks_total": int(result.get("totalChecks", 0)),
        "ips_per_hour": round(ips_per_hour, 1) if ips_per_hour > 0 else None,
        "estimated_remaining_seconds": int(estimated_seconds) if estimated_seconds > 0 else None
    }

def check_import_status(result: dict) -> dict:
    """Check for import issues."""
    scan_status = result.get("status", "")
    import_status = result.get("importStatus", "")
    
    # Key insight: scan can be completed but import still running
    if scan_status == "Completed" and import_status == "Running":
        import_start = int(result.get("importStart", 0))
        elapsed = int(time.time()) - import_start if import_start > 0 else 0
        
        return {
            "alert": True,
            "message": "Scan completed but import still processing",
            "import_elapsed_seconds": elapsed,
            "import_elapsed_formatted": format_duration(elapsed)
        }
    elif import_status == "Error":
        return {
            "alert": True,
            "message": "Import failed",
            "error_details": result.get("importErrorDetails", "Unknown error")
        }
    
    return {"alert": False}

def format_timing(result: dict) -> dict:
    """Format timing information."""
    start = int(result.get("startTime", 0))
    finish = int(result.get("finishTime", -1))
    duration = int(result.get("scanDuration", 0))
    
    timing = {}
    
    if start > 0:
        timing["started"] = datetime.fromtimestamp(start).isoformat()
    
    if finish > 0:
        timing["finished"] = datetime.fromtimestamp(finish).isoformat()
        timing["duration"] = format_duration(duration)
    elif start > 0:
        elapsed = int(time.time()) - start
        timing["elapsed"] = format_duration(elapsed)
    
    return timing

def format_duration(seconds: int) -> str:
    """Format seconds to human-readable duration."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
```

**Step 3: Register Tool (10 min)**

Add to `src/tenable_sc_mcp/server.py`:
```python
from tenable_sc_mcp.tools.scanning import register_tools as register_scanning_tools
register_scanning_tools(mcp)
```

**Step 4: Testing (0.5h)**

Create `tests/test_scanning.py`:
```python
def test_scan_status_running():
    """Test listing running scans."""
    result = tsc_scan_status(status="running")
    assert result["ok"] is True
    assert "scan_results" in result

def test_scan_status_time_range():
    """Test time range filtering."""
    result = tsc_scan_status(time_range="7d")
    assert result["ok"] is True
    assert result["filters_applied"]["time_range"] == "7d"

def test_parse_time_range():
    """Test time range parsing."""
    start, end = parse_time_range("24h")
    assert end - start == 86400

def test_calculate_progress():
    """Test progress calculation."""
    result = {
        "completedIPs": "50",
        "totalIPs": "100",
        "startTime": str(int(time.time()) - 3600)
    }
    progress = calculate_progress(result)
    assert progress["percent"] == 50.0
    assert progress["ips_per_hour"] > 0
```

**Step 5: Documentation (30 min)**

1. Add to `USER_GUIDE.md`: New Section 9 - Scan Status Monitoring
2. Add to `TEST_PROMPTS.md`: "Show me all running scans", "Did last night's scans complete?"
3. Update `TOOLS_ROADMAP.md`: Mark Tool 7 as ✅ Complete
4. Update `CHANGELOG.md`: Add v1.4.0 entry

### Response Structure

```json
{
    "ok": true,
    "total_results": 15,
    "active_scans": 3,
    "completed_scans": 10,
    "failed_scans": 2,
    "scan_results": [
        {
            "id": "123",
            "name": "Weekly PCI Scan",
            "status": "Running",
            "progress": {
                "ips_completed": 450,
                "ips_total": 500,
                "percent": 90.0,
                "checks_completed": 125000,
                "checks_total": 135000,
                "ips_per_hour": 200.0,
                "estimated_remaining_seconds": 900
            },
            "timing": {
                "started": "2026-06-24T10:00:00",
                "elapsed": "2h 15m"
            },
            "import_status": "No Results",
            "import_info": {"alert": false},
            "scan": {"id": "45", "name": "PCI Quarterly"},
            "repository": {"id": "9", "name": "Production"},
            "initiator": {"username": "scheduler"}
        }
    ]
}
```

### Use Cases Covered

1. ✅ "Show me all running scans"
2. ✅ "Did last night's scans complete?"
3. ✅ "Why can't I see scan data?" (import status check)
4. ✅ "How long until PCI scan finishes?"
5. ✅ "Which scans failed this week?"
6. ✅ "What's the scanning rate?" (IPs/hour)

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
3. **Review Tool 7 Spec Above** - Complete implementation plan with API insights
4. **Create Feature Branch** - `git checkout -b feature/tool-7-scan-status`
5. **Implement Tool 7** - Follow the implementation plan above (2.5-3 hours)
6. **Test Thoroughly** - Run quality checks and pytest
7. **Update Documentation** - USER_GUIDE.md, TEST_PROMPTS.md, TOOLS_ROADMAP.md, CHANGELOG.md
8. **Commit and Push** - Follow git workflow

---

**For next session:** Start with Tool 7 implementation following the plan above. All architecture patterns are established, Tool 6 is complete and deployed, mypy is 100% clean, and the codebase is ready for new tools.
