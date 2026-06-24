# Tenable.sc MCP Server - Handoff Document

**Last Updated:** 2026-06-24  
**Project Status:** ✅ v1.3.1 Released (Tool 6 Complete)  
**Next Session Priority:** Tool 7 - Scan Status Monitoring  
**Current Version:** 1.3.1

---

## 📋 Quick Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Current Version** | ✅ v1.3.1 | Tool 6 complete, mypy 100% clean (0 errors) |
| **Completed Tools** | 8/27 (30%) | Core IP profiling + vulnerability lookup + patch management + 2 helper tools |
| **Filter Count** | 74 filters | Universal filter framework (centralized in COMMON_FILTERS) |
| **Next Tool** | Tool 7 | Scan Status Monitoring - scanResult API integration |
| **Pending Tools** | Tools 7-27 | See TOOLS_ROADMAP.md for complete specifications |

### v1.3.1 Highlights (Current Release)

- ✅ **Tool 6**: `tsc_list_missing_patches` - Universal & Windows modes, 21/21 tests passed
- ✅ **Type Safety**: Mypy 100% clean (31 errors → 0 errors) with zero behavioral changes
- ✅ **Docker Deployment**: Verified v1.3.1 running with Tool 6 code (14,552 bytes patch_management.py)
- ✅ **Documentation**: CHANGELOG.md (full history), USER_GUIDE.md Section 8, MCP registry entry
- ✅ **GitHub PR**: PR #8 merged to develop (15 commits)

---


## 🎯 Next Priority: Tool 7 - Scan Status Monitoring

## 🎯 Next Priority: Tool 7 - Scan Status Monitoring

**Tool Name:** `tsc_scan_status`  
**Estimated Time:** 2.5-3 hours  
**Token Budget:** 2,000-4,000 tokens  
**Cache TTL:** 60s (real-time data)  
**Module:** `src/tenable_sc_mcp/tools/scanning.py` (new file)

### What This Tool Does

Provides real-time scan execution monitoring using Tenable.sc scanResult API. Tracks:
- **Scan Status**: Running, Completed, Error, Stopped, Paused, Partial
- **Import Status**: Finished, Running, Error (critical for data availability)
- **Progress Tracking**: IPs scanned, plugins executed, percent complete
- **Performance Metrics**: IPs/hour, estimated completion time
- **Error Detection**: Scan failures, import issues, stuck scans

Helps operations teams:
- Monitor active scan progress in real-time
- Identify scans with import issues (completed but data not available)
- Calculate scan performance metrics
- Track historical scan results with filtering

### Why This Tool Is Important

1. **Import Status Visibility:** Scan can complete but import still running - data not available yet
2. **Progress Estimation:** Calculate remaining time based on IPs/hour scan rate
3. **Error Detection:** Identify failed scans and import errors quickly
4. **Performance Tracking:** Monitor scan efficiency and scanner load

### Key API Insights (from Official Docs)

1. **Time Filtering Confusion:**
   - `startTime`/`endTime` params search against `createdTime`, NOT `finishTime`
   - Must use `timeCompareField` param to search by finishTime
   - Default: Last 30 days of created results

2. **Progress Field Limitation:**
   - `progress` field ONLY available on GET /{id}, NOT on list
   - Must query each scan individually for detailed progress
   - List view has: completedIPs, completedChecks, totalChecks only

3. **Import vs Scan Status:**
   - `status` = scan execution status
   - `importStatus` = result import status
   - Both must be tracked separately!

4. **String Booleans:**
   - `running`, `downloadAvailable` are strings: "true" or "false" (NOT booleans)

### Implementation Plan

**Step 1: Create Tool Function (1.5h)**

Location: `src/tenable_sc_mcp/tools/scanning.py` (new file)

```python
from typing import Any
import time
from datetime import datetime

@mcp.tool()
def tsc_scan_status(
    scan_id: int | None = None,           # Specific scan result ID
    status: str | None = None,            # running/completed/error/stopped/paused
    time_range: str | None = "24h",       # 24h/7d/30d
    include_progress: bool = False,       # Detailed progress (per-scan query)
    filters: dict[str, Any] | None = None # Additional filters
) -> dict[str, Any]:
    """
    Monitor scan execution status with progress tracking.
    
    Tracks scan status, import status, and performance metrics.
    
    Args:
        scan_id: Specific scan result ID for detailed view
        status: Filter by status (running/completed/error/stopped/paused)
        time_range: Time range filter (24h/7d/30d)
        include_progress: Get detailed progress (requires per-scan query)
        filters: Additional filters (start_time, end_time, etc.)
    
    Returns:
        Scan status with progress, timing, and import status
    
    Example:
        >>> tsc_scan_status(status="running")
        {
            "ok": True,
            "active_scans": 3,
            "scan_results": [...]
        }
    """
    client = _client()
    cache = _get_cache()
    
    # Parse time range
    start_epoch, end_epoch = parse_time_range(time_range)
    
    # Build query parameters
    params = {
        "fields": "id,name,status,totalIPs,completedIPs,completedChecks,totalChecks,startTime,finishTime,scanDuration,importStatus,importStart,importFinish,importDuration,errorDetails,importErrorDetails,scan,repository,initiator",
        "startTime": str(start_epoch),
        "endTime": str(end_epoch)
    }
    
    # Add status filter
    if status:
        if status == "running":
            params["running"] = "true"
        elif status == "completed":
            params["completed"] = "true"
    
    # Apply custom filters
    filter_dict = filters or {}
    if "time_compare_field" in filter_dict:
        params["timeCompareField"] = filter_dict["time_compare_field"]
    
    # Generate cache key
    cache_key = generate_cache_key("scan_status", params=params)
    
    # Check cache
    if cache and not scan_id:  # Don't cache specific scan queries
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    # Query API
    if scan_id:
        # Single scan with detailed progress
        response = client.get(f"/rest/scanResult/{scan_id}", params={
            "fields": params["fields"] + ",progress"
        })
        results = [response.get("response", {})]
    else:
        # List all matching scans
        response = client.get("/rest/scanResult", params=params)
        results = response.get("response", {}).get("usable", [])
    
    # Process results
    scan_results = []
    active_scans = 0
    completed_scans = 0
    failed_scans = 0
    
    for result in results:
        status_val = result.get("status", "")
        
        # Count by status
        if status_val == "Running":
            active_scans += 1
        elif status_val == "Completed":
            completed_scans += 1
        elif status_val in ["Error", "Stopped"]:
            failed_scans += 1
        
        # Calculate progress
        progress = calculate_progress(result)
        
        # Check import status
        import_info = check_import_status(result)
        
        # Format timing
        timing = format_timing(result)
        
        scan_results.append({
            "id": result.get("id"),
            "name": result.get("name"),
            "status": status_val,
            "progress": progress,
            "timing": timing,
            "import_status": result.get("importStatus"),
            "import_info": import_info,
            "scan": result.get("scan", {}),
            "repository": result.get("repository", {}),
            "initiator": result.get("initiator", {})
        })
    
    result_data = {
        "ok": True,
        "total_results": len(scan_results),
        "active_scans": active_scans,
        "completed_scans": completed_scans,
        "failed_scans": failed_scans,
        "scan_results": scan_results,
        "filters_applied": {
            "time_range": time_range,
            "status": status or "all"
        }
    }
    
    # Cache result
    if cache and not scan_id:
        cache.set(cache_key, result_data, ttl_seconds=60)
    
    return result_data
```

**Step 2: Add Helper Functions (0.5h)**

```python
def parse_time_range(time_range: str) -> tuple[int, int]:
    """Parse time range to epoch timestamps."""
    now = int(time.time())
    
    if time_range == "24h":
        return (now - 86400, now)
    elif time_range == "7d":
        return (now - 604800, now)
    elif time_range == "30d":
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
