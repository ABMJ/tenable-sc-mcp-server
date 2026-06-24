# Tenable.sc MCP Server - Design Principles & Architecture Guidelines

**Version**: 1.3.0 (planned)  
**Last Updated**: 2026-06-18  
**Status**: Living Document - Added Smart Lookup and Helper Tool Patterns

---

## 📑 Table of Contents

- [Overview](#overview)
- [Core Design Principles](#core-design-principles)
  - [1. Centralized Filter Management](#1-centralized-filter-management-mandatory)
  - [2. Self-Documenting APIs](#2-self-documenting-apis)
  - [3. Token Optimization](#3-token-optimization)
  - [4. Intelligent Caching](#4-intelligent-caching)
  - [5. Fail-Safe Error Handling](#5-fail-safe-error-handling)
  - [6. Smart Lookup Pattern](#6-smart-lookup-pattern-v130)
  - [7. Helper Tool Pattern](#7-helper-tool-pattern-v130)
- [Tool Development Standards](#tool-development-standards)
- [Architecture Patterns](#architecture-patterns)
- [Testing & Validation](#testing--validation)
- [Development Workflow & Contribution Guidelines](#development-workflow--contribution-guidelines)
  - [Branch Strategy](#branch-strategy)
  - [Workflow Patterns](#workflow-patterns)
    - [Pattern 1: Feature Development](#pattern-1-feature-development)
    - [Pattern 2: Release Workflow](#pattern-2-release-workflow)
    - [Pattern 3: Tenable Exchange Listing Updates](#pattern-3-tenable-exchange-listing-updates)
    - [Pattern 4: Hotfix Workflow](#pattern-4-hotfix-workflow)
- [Version History](#version-history)

---

## Overview

This document establishes the **mandatory design principles** and architecture patterns for all tools in the Tenable.sc MCP Server project. These principles ensure consistency, maintainability, and optimal performance across the codebase.

**Purpose:**
- Provide clear guidance for implementing new tools
- Maintain architectural consistency across all 25+ planned tools
- Prevent common pitfalls and anti-patterns
- Enable LLM-assisted development with clear constraints

**Scope:**
- All convenience tools (Tools 1-25+)
- Core API tools and server infrastructure
- Resource management and caching layers

---

## Core Design Principles

### 1. Centralized Filter Management (MANDATORY)

**Status**: 🔴 **CRITICAL - ALL FUTURE TOOLS MUST FOLLOW THIS PATTERN**

#### The Problem

Before v1.2.0, tools used explicit filter parameters in function signatures:

```python
# ❌ OLD PATTERN (DEPRECATED - DO NOT USE)
@mcp.tool()
def tool_name(
    param: str,
    # 55+ explicit filter parameters
    asset_criticality: str | None = None,
    vpr_score: str | None = None,
    aes_score: str | None = None,
    # ... 50+ more parameters
) -> dict:
    # Manual mapping to build_filters()
    filters = build_filters(
        asset_criticality=asset_criticality,
        vpr_score=vpr_score,
        # ... repeat all 55 parameters
    )
```

**Problems with old approach:**
- ❌ 100+ lines of boilerplate per tool
- ❌ Adding a new filter = updating 4 tools × 3 locations = 12+ edits
- ❌ High maintenance burden
- ❌ Prone to inconsistencies and copy-paste errors
- ❌ Does not scale beyond 25 tools

#### The Solution: Unified Filters Dict Pattern

**ALL new tools MUST use this pattern:**

```python
# ✅ CORRECT PATTERN (v1.2.0+)
@mcp.tool()
def tool_name(
    # Tool-specific required parameters
    required_param: str,
    optional_param: int = 0,
    # Unified filters dict - provides access to ALL 55+ filters
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    [Tool description]
    
    Args:
        required_param: Description
        optional_param: Description
        filters: Optional dict of filter parameters for narrowing results.
            For complete filter reference, fetch MCP resource: tenable-sc://filters/reference
            
            Common filters:
                asset_criticality: ACR range (e.g., "7-10", "8-10")
                vpr_score: VPR range (e.g., "7-10")
                severity: critical/high/medium/low/info
                exploit_available: Yes/No
                [... list 8-10 most common filters]
            
            See tenable-sc://filters/reference for all 55+ available filters.
    
    Returns:
        [Return value description]
    """
    # Extract filter dict (default to empty if not provided)
    filter_dict = filters or {}
    
    # Build filters using centralized helper - NO MANUAL MAPPING
    filter_list = build_filters(**filter_dict)
    
    # Use filter_list in API query
    query = {
        "filters": filter_list,
        ...
    }
```

#### Implementation Checklist

**When implementing ANY new tool that supports filters:**

1. ✅ **Function Signature**
   - Add `filters: dict[str, Any] | None = None` parameter
   - Keep tool-specific params separate (e.g., `ip`, `cve_id`, `repository`)
   - NO explicit filter parameters (no `asset_criticality`, `severity`, etc.)

2. ✅ **Docstring**
   - Reference MCP resource: `tenable-sc://filters/reference`
   - List 8-10 most common filters inline (not all 55)
   - Use consistent format (see pattern above)

3. ✅ **Implementation**
   ```python
   filter_dict = filters or {}
   filter_list = build_filters(**filter_dict)
   ```

4. ✅ **No Manual Mapping**
   - NEVER manually list filter parameters in `build_filters()` call
   - Let `**filter_dict` unpack automatically

5. ✅ **Usage Examples**
   - Show filters dict usage in docstring examples
   - Format: `tool_name(..., filters={"severity": "critical", "acr": "8-10"})`

#### Benefits

**For Developers:**
- 5 lines of code instead of 100+
- Add new filter = 1 edit to `COMMON_FILTERS` dict
- Zero duplication across tools
- Consistent pattern everywhere

**For Users:**
- All tools have identical filter interface
- One learning curve for all tools
- Comprehensive filter docs via MCP resource

**For Maintainability:**
- Single source of truth (`COMMON_FILTERS` in `convenience_tools.py`)
- Auto-generated documentation (never out of sync)
- Easy to extend with new filters

#### Single Source of Truth

**Location**: `src/tenable_sc_mcp/convenience_tools.py`

```python
COMMON_FILTERS = {
    # Asset Filters
    "asset_criticality": "assetCriticalityRating",  # ACR (0-10)
    "repository": "repository",
    "asset_group": "asset",
    "ip": "ip",
    "dns_name": "dnsName",
    "uuid": "uuid",
    
    # Vulnerability Filters
    "severity": "severity",
    "exploit_available": "exploitAvailable",
    "family": "family",
    "plugin_id": "pluginID",
    "cve": "cveID",
    
    # Scoring Filters (RANGE format required: "min-max")
    "vpr_score": "vprScore",
    "aes_score": "assetExposureScore",
    "cvss_v3_base_score": "cvssV3BaseScore",
    "epss_score": "epssScore",
    
    # ... 55+ total filters
}
```

**Adding a New Filter:**
1. Add one line to `COMMON_FILTERS` dict
2. Filter automatically available in ALL tools
3. Auto-generated docs update instantly
4. Validation warnings include new filter

**NEVER:**
- ❌ Add filter parameters to tool signatures
- ❌ Create tool-specific filter mappings
- ❌ Duplicate filter logic across files
- ❌ Hard-code filter names in tool implementations

---

### 2. Self-Documenting APIs

**Principle**: Tools must be self-documenting for LLM clients via MCP resources.

#### MCP Resources Layer

**Implemented**: v1.1.0 (2026-06-10)

All filter-capable tools reference:
```
tenable-sc://filters/reference
```

**Features:**
- Auto-generated from `COMMON_FILTERS` dict
- 10,000+ words of comprehensive documentation
- Organized by category (Asset, Vulnerability, Scoring, etc.)
- Includes format requirements and examples
- Common mistakes and troubleshooting

**Auto-Generation Pattern:**
```python
# resources/filter_reference.py
def generate_filter_reference() -> str:
    """Auto-generate filter docs from COMMON_FILTERS."""
    from ..convenience_tools import COMMON_FILTERS
    
    # Build markdown documentation
    docs = []
    for category in FILTER_CATEGORIES:
        docs.append(f"## {category}\n")
        for filter_name, api_name in get_filters_for_category(category):
            docs.append(format_filter_docs(filter_name, api_name))
    
    return "\n".join(docs)
```

**Benefits:**
- Always in sync with code (same source)
- LLM clients can fetch once and cache
- Reduces tool docstring verbosity
- Enables discovery without guessing

---

### 3. Token Optimization

**Target**: 75-92% token reduction vs naive API calls

#### Techniques

1. **Smart Field Selection**
   - Request only required fields from Tenable.sc API
   - Different field sets for summary vs detail tools

2. **Aggressive Caching**
   - 120-300s TTL based on data volatility
   - Separate TTLs for static (hostname) vs dynamic (vulns) data

3. **Pagination**
   - Default page sizes tuned to 90th percentile use cases
   - Tool 1: No pagination (single IP)
   - Tool 2a: No pagination (summary only)
   - Tool 2b: 10-200 records (default: 50)
   - Tool 5: 0-1000 records (default: 200)

4. **Response Formatting**
   - Compact JSON structures
   - Remove null/empty fields
   - Abbreviate common keys

**Token Budgets by Tool Type:**
- IP Profile: ~2,500 tokens (83% savings)
- Summary Queries: ~700 tokens (88% savings)
- Detail Queries: ~5,000 tokens per 50 records (58% savings)
- Discovery Tools: 400-3,700 tokens based on result size

---

### 4. Intelligent Caching

**Backend**: Redis (production) / In-memory (development)

#### Cache TTL Strategy

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Vulnerability data | 180s (3min) | Changes with scans, but not constantly |
| Asset discovery | 120s (2min) | IP lists change with network changes |
| Static metadata | 300s (5min) | Hostnames, MAC addresses rarely change |
| Scan status | 60s (1min) | Actively monitored during scan execution |
| CVE outbreaks | 240s (4min) | Emergency response, fresh but not real-time |

#### Cache Key Pattern

```python
def build_cache_key(tool_name: str, params: dict) -> str:
    """Build consistent cache keys across tools."""
    # Sort params for consistent keys
    sorted_params = sorted(params.items())
    param_str = json.dumps(sorted_params, sort_keys=True)
    param_hash = hashlib.md5(param_str.encode()).hexdigest()[:12]
    return f"{tool_name}:{param_hash}"
```

#### Cache Invalidation

**Write operations clear related cache:**
```python
# Example: Accepting risk on asset invalidates IP profile cache
def accept_asset_risk(ip: str):
    # ... accept risk via API ...
    cache.delete(f"tsc_profile_ip_efficient:*{ip}*")
    cache.delete(f"tsc_list_vulns_by_ip:*{ip}*")
```

---

### 5. Fail-Safe Error Handling

**Principle**: Never expose raw API errors to users. Provide actionable guidance.

#### Error Response Pattern

```python
def tool_implementation():
    try:
        # Validate inputs
        valid, error = validate_input(param)
        if not valid:
            return {
                "ok": False,
                "error": error,
                "hint": "Helpful suggestion for fixing the error"
            }
        
        # API call
        result = api_call()
        
        if not result.get("ok"):
            return {
                "ok": False,
                "error": "User-friendly error message",
                "technical_details": result.get("error"),  # For debugging
                "suggestion": "Try X or check Y"
            }
        
        return {
            "ok": True,
            "data": format_response(result)
        }
    
    except ValueError as e:
        # Known error types - provide helpful guidance
        return {
            "ok": False,
            "error": str(e),
            "hint": "Check X"
        }
    
    except Exception as e:
        # Unknown errors - log and return safe message
        logger.error(f"Unexpected error in tool_name: {e}", exc_info=True)
        return {
            "ok": False,
            "error": "An unexpected error occurred",
            "request_id": generate_request_id(),
            "hint": "Check server logs for details"
        }
```

#### Validation Warnings (Not Errors)

**Filter validation uses warnings:**
```python
# Unknown filters log WARNING but don't block execution
if validate and unknown_params:
    logger.warning(
        f"Unknown filter parameters will be ignored: {unknown_params}. "
        f"For valid filter names, see: tenable-sc://filters/reference"
    )
# Continue execution - don't raise error
```

**Rationale**: Some parameters may be valid but undocumented. Warnings provide guidance without breaking workflows.

---

## Tool Development Standards

### File Organization

```
tools/
├── __init__.py              # Register all tools
├── ip_profiling.py          # Tool 1: IP profiling
├── vulnerability_lookup.py  # Tools 2a, 2b, 5: Vuln queries
├── asset_discovery.py       # Tool 4: IP/asset discovery
├── scanning.py              # Tools 6-7: Scan management (future)
└── [module].py              # Group related tools by domain
```

### Tool Registration Pattern

```python
# tools/[module].py
def register_tools(mcp):
    """Register all tools in this module."""
    
    @mcp.tool()
    def tool_name(...):
        """Tool implementation."""
        pass

# tools/__init__.py
def register_all_tools(mcp):
    """Register all tools from all modules."""
    from .ip_profiling import register_tools as register_ip_profiling
    from .vulnerability_lookup import register_tools as register_vuln_lookup
    from .asset_discovery import register_tools as register_asset_discovery
    
    register_ip_profiling(mcp)
    register_vuln_lookup(mcp)
    register_asset_discovery(mcp)
```

### Naming Conventions

**Tool Names:**
- Prefix: `tsc_` (Tenable Security Center)
- Format: `tsc_verb_noun_modifier`
- Examples:
  - `tsc_profile_ip_efficient`
  - `tsc_list_vulns_by_ip_summary`
  - `tsc_list_missing_patches_windows`

**Function Parameters:**
- Use snake_case
- Match Tenable.sc terminology where possible
- Clear, self-documenting names
- Required params first, optional after, `filters` dict last

### Docstring Template

```python
@mcp.tool()
def tsc_tool_name(
    required_param: str,
    optional_param: int = 0,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    [One-line description]. Use this when you need to:
    - [Primary use case]
    - [Secondary use case]
    - [Additional use case]
    
    WHEN TO USE THIS TOOL:
    - User asks "[natural language query 1]"
    - User asks "[natural language query 2]"
    - [Specific scenario]
    
    DO NOT USE for [alternative tool scenario] - use [other_tool] instead.
    
    [Brief explanation of what the tool does and how it works]
    
    Token Efficiency: ~X tokens (vs ~Y raw API) = Z% reduction
    Cache TTL: Xs (X minutes)
    Response Time: <1s cached, X-Ys fresh
    
    Args:
        required_param: Description
        optional_param: Description
        filters: Optional dict of filter parameters.
            For complete filter reference: tenable-sc://filters/reference
            
            Common filters:
                [List 8-10 most relevant filters with examples]
    
    Returns:
        Dict with:
        - ok: True/False
        - [key fields in response]
    
    Example:
        >>> tsc_tool_name("value", filters={"severity": "critical"})
        {
            "ok": True,
            "result": [...]
        }
    """
```

---

## Architecture Patterns

### Module Structure

```
src/tenable_sc_mcp/
├── server.py               # FastMCP server, tool registration
├── convenience_tools.py    # Shared helpers, COMMON_FILTERS
├── tools/                  # Tool implementations
│   ├── __init__.py
│   ├── [domain]_tools.py
├── resources/              # MCP resources (auto-generated docs)
│   ├── __init__.py
│   ├── filter_reference.py
└── cache/                  # Caching layer
    ├── __init__.py
    └── redis_cache.py
```

### Dependency Flow

```
┌──────────────────────────────────┐
│   MCP Client (OpenCode/Claude)   │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│     FastMCP Server (server.py)   │
│  - Tool registration              │
│  - Resource registration          │
└──────────────┬───────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
┌─────────────┐   ┌───────────────────┐
│   Tools     │   │    Resources      │
│  (domain    │   │  - Filter docs    │
│   modules)  │   │  - Catalog        │
└──────┬──────┘   └───────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│   Convenience Tools Layer          │
│  - COMMON_FILTERS                  │
│  - build_filters()                 │
│  - Validation                      │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│        Cache Layer                 │
│  - Redis (production)              │
│  - In-memory (development)         │
└──────────┬─────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│     Tenable.sc REST API            │
│  - /rest/analysis                  │
│  - /rest/[resource]                │
└────────────────────────────────────┘
```

### Data Flow

**Tool Execution:**
1. MCP client calls tool with parameters
2. Tool validates inputs (fail-safe errors)
3. Tool extracts `filters` dict
4. Tool calls `build_filters(**filters)`
5. `build_filters()` validates and maps to API names
6. Cache layer checks for existing result
7. If cache miss: Query Tenable.sc API
8. Format and cache response
9. Return to MCP client

**Filter Documentation:**
1. MCP client fetches `tenable-sc://filters/reference`
2. Resource handler generates docs from `COMMON_FILTERS`
3. Client caches documentation
4. Client uses correct filter names/formats

---


## Testing & Validation

### Required Tests for New Tools

1. **Unit Tests**
   - Input validation
   - Filter parameter handling
   - Error cases
   - Response formatting

2. **Integration Tests**
   - End-to-end with test Tenable.sc instance
   - Cache hit/miss scenarios
   - Filter combinations

3. **Performance Tests**
   - Token count measurements
   - Cache TTL validation
   - Response time benchmarks

4. **LLM Tests**
   - Natural language prompts
   - Filter discovery via resource
   - Error recovery

### Test Prompt Template

```
I am testing [tool_name] to [use case]. Please format your response as:

✅/❌ TEST STATUS: [PASS/FAIL]
📊 CACHE: [HIT/MISS]
🔢 TOKENS: [count] tokens used
📝 SUMMARY: [one-liner about effectiveness]
📦 RESULT: [key metrics from response]

If failed, provide ERROR DETAILS with enough information for the developer to fix.
```

---

### 6. Smart Lookup Pattern (v1.3.0)

**Status**: ✅ **RECOMMENDED - Enhances UX and prevents false positives**

#### The Problem

Some API filters require exact values (OS names, plugin family IDs) but users naturally provide partial names or keywords:

```python
# User provides natural language
filters = {"operating_system": "Windows 10"}  # Partial match desired

# API requires exact match
"operatingSystem" = "Microsoft Windows 10 Pro Build 19045"  # Exact string
```

**Problems with exact-only matching:**
- ❌ User must know exact OS name format from Tenable.sc
- ❌ Cannot do "all Windows 10" without knowing all builds
- ❌ Poor UX requiring manual discovery step
- ❌ Plugin family names not supported (only IDs work)

#### The Solution: Smart Lookup with Discovery Tools

**Pattern:**
1. User provides natural language input (partial name, keyword)
2. Tool queries discovery endpoint (cached)
3. Tool finds all matching values
4. Tool applies exact filters for each match
5. Tool aggregates results

**Example Implementation (Operating System):**

```python
def handle_operating_system_filter(os_value: str) -> list[dict]:
    """
    Smart OS lookup: partial name → exact matches → zero false positives.
    
    Args:
        os_value: User's partial OS name (e.g., "Windows 10")
    
    Returns:
        List of exact OS filter objects
    """
    # Step 1: Query discovery tool (cached 300s)
    all_os = _query_listos_cached()
    
    # Step 2: Find all matching OS names (case-insensitive partial match)
    matches = [
        os for os in all_os 
        if os_value.lower() in os["name"].lower()
    ]
    
    # Step 3: Build exact filters for each match
    return [
        {
            "filterName": "operatingSystem",
            "operator": "=",
            "value": f"'{match['name']}'"  # Exact match with quotes
        }
        for match in matches
    ]
    
    # Tenable.sc API auto-aggregates results (OR logic)
```

**Example Implementation (Plugin Family):**

```python
def get_plugin_family_id(family_input: str) -> str | None:
    """
    Smart family lookup: name OR ID → always returns valid ID.
    
    Args:
        family_input: Family name ("Windows") or ID ("20")
    
    Returns:
        Plugin family ID string or None if not found
    """
    # Quick check: already an ID?
    if family_input.isdigit():
        return family_input
    
    # Lookup by name (cached 600s - static data)
    families = _query_plugin_families_cached()
    for family in families:
        if family["name"].lower() == family_input.lower():
            return family["id"]
    
    # Graceful degradation
    logger.warning(f"Unknown plugin family: {family_input}")
    return None  # Caller skips this filter
```

#### Key Benefits

✅ **Better UX:** Natural language input, no manual discovery needed  
✅ **Zero False Positives:** Exact matching prevents unintended matches  
✅ **Backward Compatible:** Accepts exact values unchanged  
✅ **Cache-Friendly:** Discovery endpoints cached separately (300s-600s)  
✅ **Graceful Degradation:** Unknown values logged + skipped (not errors)

#### When to Use

**Use Smart Lookup When:**
- API requires exact IDs/names but users provide keywords
- Multiple exact values map to one user intent ("Windows 10" → 5 builds)
- Discovery endpoint available and cacheable
- False positives are unacceptable (security context)

**Don't Use When:**
- Filter already supports partial matching (like `dns_name ~= "web"`)
- Lookup cost exceeds benefit (uncacheable, slow)
- User expects regex-like behavior (use `pcre` instead)

#### Related Patterns

- **Helper Tool Pattern (Principle 7):** Discovery tools as standalone
- **Intelligent Caching (Principle 4):** Longer TTL for static lookup data
- **Fail-Safe Error Handling (Principle 5):** Graceful unknown value handling

**Examples:**
- `tsc_list_ips(filters={"operating_system": "Windows 10"})` → finds all Win10 builds
- `tsc_list_vulns_by_ip_full(filters={"family": "Windows"})` → converts to ID 20

---

### 7. Helper Tool Pattern (v1.3.0)

**Status**: ✅ **RECOMMENDED - Improves discoverability and testability**

#### The Problem

Smart Lookup Pattern (Principle 6) requires discovery endpoints (listos, plugin families) but users don't know:
- What values are available (all OS names, all family names)
- How to spell exact names ("Microsoft Windows Server 2019" vs "Windows Server 2019")
- What IDs map to which names (family ID 20 = "Windows")

**Without helper tools:**
- ❌ Users must guess filter values
- ❌ Smart lookup internals not testable
- ❌ Discovery logic buried in filter handlers (not reusable)

#### The Solution: Standalone Discovery Tools

**Pattern:**
1. Create dedicated MCP tool for discovery endpoint
2. Make tool public and standalone (not just internal helper)
3. Cache results aggressively (static/semi-static data)
4. Smart lookup handlers reuse the same tool internally

**Example Implementation:**

```python
# File: tools/asset_discovery.py

@mcp.tool()
def tsc_list_operating_systems(
    repository: str | None = None,
    sort_by: str = "count",  # count|name
    limit: int = 200,
) -> dict[str, Any]:
    """
    List all operating system names in the environment.
    
    Use this to discover exact OS names before filtering with operating_system.
    
    Returns:
        - ok: True/False
        - operating_systems: List of {"name": str, "count": int}
        - summary: {total, returned, sort_by}
    
    Token Budget: ~1,500-2,000 tokens
    Cache TTL: 300s (5 minutes)
    """
    # Call internal cached helper (shared with smart lookup)
    results = _query_listos_cached(repository=repository)
    
    # Sort and paginate
    if sort_by == "count":
        results.sort(key=lambda x: x["count"], reverse=True)
    else:
        results.sort(key=lambda x: x["name"])
    
    return {
        "ok": True,
        "operating_systems": results[:limit],
        "summary": {
            "total": len(results),
            "returned": min(limit, len(results)),
            "sort_by": sort_by
        }
    }

# Internal helper (shared cache)
@lru_cache(maxsize=128)
def _query_listos_cached(repository: str | None = None) -> list[dict]:
    """Cached listos query - 300s TTL via Redis."""
    # Implementation details...
    pass
```

**Internal Reuse:**

```python
# File: convenience_tools.py

def handle_operating_system_filter(os_value: str) -> list[dict]:
    """Smart OS lookup reuses same cached data as tsc_list_operating_systems."""
    # Use same internal helper (shares cache)
    all_os = _query_listos_cached()
    
    # Find matches and build filters
    matches = [os for os in all_os if os_value.lower() in os["name"].lower()]
    return [build_exact_filter(match) for match in matches]
```

#### Key Benefits

✅ **Discoverable:** Users can find tool via MCP catalog  
✅ **Testable:** Standalone tool = independent testing  
✅ **Reusable:** Same cache/logic for UI and internal lookups  
✅ **Documented:** Explicit token budget and cache TTL  
✅ **Cache-Efficient:** Single cache shared across use cases

#### Implementation Checklist

**For each helper tool:**
1. ✅ Create as public `@mcp.tool()` (not private function)
2. ✅ Add to appropriate module (`asset_discovery.py`, `plugins.py`)
3. ✅ Document token budget + cache TTL in docstring
4. ✅ Implement sorting and pagination
5. ✅ Share cache with internal smart lookup handlers
6. ✅ Add test prompts to `TEST_PROMPTS.md`
7. ✅ Reference in filter documentation

#### When to Use

**Use Helper Tool When:**
- Discovery endpoint returns static/semi-static data (cacheable)
- Users need to know available values before filtering
- Smart lookup pattern (Principle 6) already implemented
- Endpoint useful standalone (not just internal dependency)

**Don't Use When:**
- Data changes too frequently (cache ineffective)
- Discovery query too expensive (>5s response time)
- Only needed internally (pure implementation detail)

#### Examples (v1.3.0)

**Tool 6a: `tsc_list_operating_systems`**
- Discovery: All OS names with counts
- Cache: 300s (semi-static, changes on new scans)
- Token Budget: ~1,500-2,000 tokens
- Used by: `operating_system` filter smart lookup

**Tool 6b: `tsc_list_plugin_families`**
- Discovery: All plugin family IDs + names
- Cache: 600s (static data, rarely changes)
- Token Budget: ~800-1,200 tokens
- Used by: `family` filter smart lookup

**Related Patterns:**
- **Smart Lookup Pattern (Principle 6):** Helper tools enable smart lookups
- **Self-Documenting APIs (Principle 2):** MCP resources reference helpers
- **Intelligent Caching (Principle 4):** Longer TTL for static discovery data

---

## Development Workflow & Contribution Guidelines

**Purpose:** Define how code changes flow from development to production while keeping `main` branch always production-ready.

### Branch Strategy

We use a **GitHub Flow variant** with two permanent branches:

```
main (production-ready, protected)
  └── develop (integration branch)
       ├── feature/tool-name
       ├── bugfix/issue-description
       └── docs/documentation-updates
```

#### Branch Types

| Branch | Purpose | Merges To | Lifetime |
|--------|---------|-----------|----------|
| `main` | Production releases, tagged versions | N/A (protected) | Permanent |
| `develop` | Integration, feature testing | `main` | Permanent |
| `feature/*` | New tools, enhancements | `develop` | 1-5 days |
| `bugfix/*` | Non-critical bug fixes | `develop` | 1-3 days |
| `hotfix/*` | Critical production fixes | `main` + `develop` | Hours |
| `docs/*` | Documentation only | `develop` or `main` | 1-2 days |
| `release/*` | Release preparation | `main` | 1-2 days |

### Workflow Patterns

#### Pattern 1: Feature Development

**Use Case:** Adding new tools, filters, or non-breaking enhancements

```bash
# 1. Branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/os-exact-matching

# 2. Develop with frequent commits
git add src/tenable_sc_mcp/tools/asset_discovery.py
git commit -m "feat(tools): Add tsc_list_operating_systems tool"

# 3. Push and create PR to develop
git push -u origin feature/os-exact-matching
gh pr create --base develop --title "feat: OS exact matching filter"

# 4. After review and approval, merge to develop
# 5. Delete feature branch
git branch -d feature/os-exact-matching
```

**Key Rules:**
- ✅ Always branch from `develop`, never from `main`
- ✅ Keep feature branches short-lived (1-5 days max)
- ✅ Commit early and often
- ✅ Pull from `develop` daily to stay current
- ✅ Run tests locally before pushing

#### Pattern 2: Release Workflow

**Use Case:** Promoting tested features from `develop` to production

```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/vX.Y.Z

# 2. Bump version in pyproject.toml
# Edit: version = "X.Y.Z"
git add pyproject.toml
git commit -m "chore: Bump version to X.Y.Z"

# 3. Final testing and bug fixes ONLY (no new features)
pytest tests/
git commit -m "fix: Edge case in OS matching"

# 4. Create PR to main
gh pr create --base main --title "Release vX.Y.Z" --body "..."

# 5. After approval, merge to main
git checkout main
git merge --no-ff release/vX.Y.Z
git tag -a vX.Y.Z -m "Release vX.Y.Z: <summary>"
git push origin main --tags

# 6. Merge back to develop (critical!)
git checkout develop
git merge --no-ff release/vX.Y.Z
git push origin develop

# 7. Delete release branch
git branch -d release/vX.Y.Z

# 8. Create GitHub release
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file RELEASE_NOTES.md
```

#### Pattern 3: Tenable Exchange Listing Updates

**Use Case:** Updating marketplace listing when adding new tools, resources, or prompts

**File:** `tenable-sc-mcp-server.md` (root directory)

**When to Update:**
- ✅ Adding new MCP tools (Tools 6-26)
- ✅ Adding new MCP resources (e.g., `tenable-sc://new-resource`)
- ✅ Adding MCP prompts (if/when implemented)
- ❌ Bug fixes, refactoring, documentation updates
- ❌ Version bumps, performance improvements
- ❌ Internal code changes

**Rule of Thumb:**
> "Does this change what tools/features users can access?"
> - **Yes** → Update Exchange listing
> - **No** → Don't touch it

**Update Process:**

```bash
# 1. After implementing new tool (e.g., Tool 6)
nano tenable-sc-mcp-server.md

# 2. Add to tools_exposed section (YAML front matter)
tools_exposed:
  # ... existing 15 tools ...
  
  - name: "tsc_list_missing_patches_windows"  # NEW
    description: "MS bulletin-based patch gap analysis for Windows systems"
  - name: "tsc_scan_status"  # NEW
    description: "Real-time scan monitoring with filters"

# 3. Commit and push
git add tenable-sc-mcp-server.md
git commit -m "docs: Update Exchange listing with Tools 6-7"
git push origin main

# 4. Verify on Tenable Exchange (5-10 min sync delay)
# Visit: https://exchange.tenable.com/cyberagents
# Search: "Tenable.sc MCP Server"
```

**Update Schedule (Based on Roadmap):**

| Version | Tools Added | Update Required? |
|---------|-------------|------------------|
| v1.3.0 | None (bug fixes only) | ❌ No |
| v2.0.0 | Tools 6-26 (21 new tools) | ✅ **YES** |

**Exchange File Sections:**

```yaml
# YAML Front Matter (lines 1-53)
tools_exposed:        # Update when adding MCP tools
  - name: "tool_name"
    description: "..."

resources_exposed:    # Update when adding MCP resources
  - name: "resource_uri"
    description: "..."

prompts_exposed: []   # Update when adding MCP prompts

# Markdown Content (lines 55-76)
## What it does       # Update if purpose changes
## How it works       # Update if architecture changes
```

**Tenable May Update:**
- `tier: "unreviewed"` → `tier: "community"` (after review)
- Tag updates for discoverability
- Description typo fixes

**Important Notes:**
1. This file is for **Tenable Exchange marketplace listing** only
2. Don't update for every commit - only when user-facing features change
3. Tenable Exchange syncs every 5-10 minutes after push
4. File must remain in repository root for Exchange integration

**Version Numbering (Semantic Versioning):**
- **Major (x.0.0):** Breaking changes, API incompatibility
- **Minor (1.x.0):** New features, backward compatible  
- **Patch (1.2.x):** Bug fixes only, no new features

#### Pattern 4: Hotfix Workflow

**Use Case:** Critical bug in production requiring immediate fix

```bash
# 1. Branch from main (not develop!)
git checkout main
git pull origin main
git checkout -b hotfix/cache-leak

# 2. Fix with minimal changes
git commit -m "fix: Prevent Redis connection leak"

# 3. Test thoroughly
pytest tests/

# 4. Merge to main immediately
git checkout main
git merge --no-ff hotfix/cache-leak
git tag -a v1.2.2 -m "Hotfix v1.2.2: Cache leak"
git push origin main --tags

# 5. Merge to develop (prevent regression!)
git checkout develop
git merge --no-ff hotfix/cache-leak
git push origin develop

# 6. Delete hotfix branch
git branch -d hotfix/cache-leak

# 7. Create GitHub release
gh release create v1.2.2 --title "v1.2.2 - HOTFIX" --notes "..."
```

### Commit Message Conventions

We follow **Conventional Commits** for semantic, searchable history.

#### Format

```
<type>(<scope>): <subject>

<body> (optional)

<footer> (optional)
```

#### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(tools): Add OS listing tool` |
| `fix` | Bug fix | `fix(cache): Resolve memory leak` |
| `docs` | Documentation only | `docs: Update filter reference` |
| `style` | Code style (no logic change) | `style: Apply black formatting` |
| `refactor` | Code refactoring | `refactor: Extract filter helpers` |
| `perf` | Performance improvement | `perf: Optimize cache lookups` |
| `test` | Tests added/updated | `test: Add OS matching unit tests` |
| `chore` | Build/tooling changes | `chore: Update Docker base image` |
| `ci` | CI/CD changes | `ci: Add GitHub Actions workflow` |

#### Scopes (Optional)

Use component names: `tools`, `filters`, `cache`, `client`, `docs`, `tests`

**Examples:**
```bash
git commit -m "feat(tools): Add user IoE summarization"
git commit -m "fix(filters): Resolve family ID lookup"
git commit -m "docs(readme): Clarify installation steps"
git commit -m "refactor(cache): Use connection pooling"
```

### Pull Request Guidelines

#### PR Template

```markdown
## Description
Brief summary of changes and motivation.

## Type of Change
- [ ] New feature (non-breaking)
- [ ] Bug fix (non-breaking)
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows design principles
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] Commit messages follow conventions
```

#### Review Process

1. **Author** creates PR with clear description
2. **Reviewer** checks:
   - Code follows design principles (filters dict, caching, etc.)
   - Test coverage adequate
   - Documentation updated
   - No security vulnerabilities
   - Token optimization maintained
3. **Approval** required before merge
4. **Merge** via GitHub (squash or merge commit)
5. **Delete branch** after merge

### Branch Protection Rules

**⚠️ IMPORTANT:** GitHub now uses **Rulesets** (not "Branch protection rules").  
For detailed setup instructions, see: **`BRANCH_PROTECTION_SETUP.md`** or **`QUICK_RULESET_SETUP.md`**

#### Main Branch (Production) - Ruleset Configuration

**Quick Setup:** Go to `https://github.com/ABMJ/tenable-sc-mcp-server/settings/rules`

**Ruleset Configuration:**
- **Ruleset Name:** `Protect main branch`
- **Enforcement Status:** Active
- **Target Branches:** Include by pattern → `main`
- **Bypass List:** Empty (no exceptions - maximum protection)

**Rules to Enable:**
- ✅ **Require a pull request before merging**
  - Required approvals: 1 (increase for teams)
  - Dismiss stale pull request approvals when new commits are pushed
  - Require approval of the most recent reviewable push
- ✅ **Block force pushes** (prevents history rewriting)
- ✅ **Restrict deletions** (prevents branch deletion)
- ✅ **Require linear history** (optional - keeps history clean)
- ✅ **Require status checks to pass** (if CI/CD is configured)

**Result:** No one (including you) can push directly to main. All changes require PR + approval.

#### Develop Branch (Integration) - Ruleset Configuration

**Ruleset Configuration:**
- **Ruleset Name:** `Protect develop branch`
- **Enforcement Status:** Active
- **Target Branches:** Include by pattern → `develop`
- **Bypass List:** Empty or maintainer-only (your choice)

**Rules to Enable:**
- ✅ **Require a pull request before merging** (1 approval)
- ✅ **Block force pushes**
- ✅ **Restrict deletions**
- ⚠️ **Status checks** (optional - can be more lenient than main)

**Note:** Develop can be slightly more flexible than main (e.g., allow emergency pushes via bypass list)

**For Complete Step-by-Step Instructions:** See `BRANCH_PROTECTION_SETUP.md` or `QUICK_RULESET_SETUP.md`

### CI/CD Integration (Recommended)

Example GitHub Actions workflow for automated testing:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-extras
      
      - name: Run tests
        run: pytest tests/ --cov
      
      - name: Lint
        run: ruff check .
      
      - name: Type check
        run: mypy src/
```

**Automated Checks:**
- All tests must pass (>80% coverage)
- No linting errors (ruff)
- No type errors (mypy)
- Security scans pass (Dependabot)

### Release Checklist

Before releasing a new version:

- [ ] All features merged to `develop` and tested
- [ ] Create release branch from `develop`
- [ ] Bump version in `pyproject.toml`
- [ ] Update documentation (README, FILTER_REFERENCE, etc.)
- [ ] Run full test suite locally
- [ ] Build and test Docker image
- [ ] Create PR to `main` with comprehensive release notes
- [ ] Get approval and merge to `main`
- [ ] Tag release: `git tag -a v<version> -m "Release v<version>"`
- [ ] Push tags: `git push --tags`
- [ ] Create GitHub Release with detailed notes
- [ ] Merge release branch back to `develop`
- [ ] Delete release branch
- [ ] Announce release (if applicable)

### Best Practices Summary

**DO:**
- ✅ Keep `main` production-ready at all times
- ✅ Use `develop` for integration and testing
- ✅ Create feature branches for all changes
- ✅ Write clear, conventional commit messages
- ✅ Test before pushing
- ✅ Update documentation with code changes
- ✅ Request code reviews for all PRs
- ✅ Tag all releases with semantic versioning
- ✅ Merge release branches back to `develop`

**DON'T:**
- ❌ Commit directly to `main` or `develop`
- ❌ Keep feature branches alive >5 days
- ❌ Merge without code review
- ❌ Push failing tests
- ❌ Skip documentation updates
- ❌ Use force push (except on your own feature branches)
- ❌ Forget to merge hotfixes to both `main` and `develop`

### Repository Visibility & Access Control

**Making Repository Public (Read-Only for Users):**

This repository is designed to be **public for MCP server usage** but **restricted for code development**.

**Goal:** Users can USE the MCP server (via Docker/PyPI), but only maintainers can modify the codebase.

#### GitHub Settings Configuration

**Settings → General → Danger Zone:**
- ✅ **Make repository public** (already done - allows users to view/clone/fork)

**Settings → Collaborators and teams:**
- Only add trusted maintainers as collaborators
- Do NOT accept outside collaborators

**Settings → Pull Requests:**
- ✅ **Allow forking** (recommended - users can customize privately)
- Users who fork can modify for their own use
- With branch protection (Rulesets), only you can approve PRs

**Settings → Features:**
- ✅ **Issues enabled** (for bug reports and feature requests)
- ❌ **Wiki disabled** (use docs/ directory instead)
- ❌ **Projects disabled** (optional - use if helpful)
- ❌ **Discussions disabled** (optional - use Issues instead)

**Create `.github/CODEOWNERS` (auto-assigns you to all PRs):**
```
# All files owned by maintainer
* @ABMJ
```

**Create `.github/PULL_REQUEST_TEMPLATE.md` (clarifies contribution policy):**
```markdown
# ⚠️ Pull Requests Not Accepted

This repository does not accept external pull requests.

**For bug reports:** Open an issue instead  
**For feature requests:** Open an issue for discussion  
**For personal use:** Fork the repository and modify as needed

Maintainer-only repository. External contributions are not accepted at this time.
```

#### How Users Can Use the MCP Server

**Recommended Distribution Methods:**

1. **Docker Hub / GitHub Container Registry (Primary):**
   - Publish Docker images: `ghcr.io/abmj/tenable-sc-mcp:latest`
   - Users install via: `docker pull ghcr.io/abmj/tenable-sc-mcp:latest`
   - No code access needed - pure consumption

2. **GitHub Releases (Recommended):**
   - Tag releases: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
   - Create GitHub Releases with release notes
   - Users can download specific versions

3. **PyPI Package (Optional - Future):**
   - Publish as: `pip install tenable-sc-mcp`
   - Users install without seeing code

4. **Source Installation (Self-Hosting):**
   - Users can clone the public repo
   - Follow README.md installation instructions
   - Clarify: "Read-only - PRs not accepted"

#### Repository Settings Summary

**Current Configuration (Post-Setup):**

```
Repository Status:
  [✅] Public repository (users can view, clone, fork)
  [✅] Main branch protected via Ruleset (requires PR + approval)
  [✅] Develop branch protected via Ruleset (requires PR + approval)
  [✅] Issues enabled (bug reports, feature requests)
  [✅] Forking allowed (users can customize privately)
  [✅] CODEOWNERS file (@ABMJ auto-assigned to PRs)

Result:
  ✅ Users can USE the MCP server (Docker, source install)
  ✅ Users can FORK for personal modifications
  ✅ Users can report ISSUES for bugs/features
  ❌ Users CANNOT push directly to main/develop
  ❌ External PRs require YOUR approval (you control codebase)
```

#### Enforcement Strategy

**Three-Layer Protection:**

1. **Technical:** Branch Rulesets prevent direct pushes (configured above)
2. **Social:** Clear CONTRIBUTING.md stating no external contributions
3. **Process:** Close external PRs politely with standard message

**Example CONTRIBUTING.md:**

```markdown
# Contributing

This is a **maintainer-only** repository.

## For Users

- **Bug Reports:** Open an issue with reproduction steps
- **Feature Requests:** Open an issue for discussion
- **Questions:** Open an issue or check existing documentation

## For Contributors

External pull requests are **not accepted** at this time.

This is a personal/internal project maintained by @ABMJ.

If you find this useful and want to modify it, please fork the repository
and maintain your own version.
```

---

## Version History

### v1.3.0 (2026-06-18) - PLANNED
- ✅ **Smart Lookup Pattern**: Added Principle 6 for natural language filter inputs
- ✅ **Helper Tool Pattern**: Added Principle 7 for discoverable standalone tools
- 🚧 **Operating System Exact Matching**: New `operating_system` filter (zero false positives)
- 🚧 **Plugin Family Fix**: Smart name→ID conversion (fixes v1.2.1 broken behavior)
- 🚧 **Helper Tools**: `tsc_list_operating_systems`, `tsc_list_plugin_families`
- 🚧 **Filter Count**: 71 → 74 filters (added `operating_system`, `os_name`, `os_exact`)
- 📝 **Documentation**: Complete implementation plan in `OS_AND_PLUGIN_FAMILY_FIX.md`

### v1.2.1 (2026-06-12)
- ✅ **CPE/OS Filtering**: Added smart operator detection for `cpe` filter (contains/exact/regex)
- ✅ Added `os_cpe` as alias for `cpe` parameter (71 total filters)
- ✅ Fixed MCP resource documentation generation (brace escaping in examples)
- ✅ Enhanced documentation with regex pitfall guidance and best practices
- ✅ Verified severity string-to-numeric conversion working correctly
- ✅ Design Decision: Auto-detect CPE operators based on value format (no user configuration needed)

### v1.2.0 (2026-06-10)
- ✅ **BREAKING**: Unified filters dict pattern (mandatory for all new tools)
- ✅ Created DESIGN_PRINCIPLES.md
- ✅ Refactored all 4 existing tools to use `filters: dict` pattern
- ✅ Established centralized filter management as core principle

### v1.1.0 (2026-06-10)
- ✅ Added MCP Resources layer for self-documenting APIs
- ✅ Enhanced `build_filters()` with validation warnings
- ✅ Fixed Tool 5 (CVE search) bugs

### v1.0.0 (2026-06-08)
- ✅ Initial implementation of 4 convenience tools
- ✅ Redis caching layer
- ✅ Docker deployment
- ✅ Token optimization patterns

---

## Summary

**Mandatory Patterns:**
1. ✅ Use `filters: dict` parameter (NO explicit filter params)
2. ✅ Call `build_filters(**filter_dict)` (NO manual mapping)
3. ✅ Reference `tenable-sc://filters/reference` in docstrings
4. ✅ Single source of truth: `COMMON_FILTERS` dict
5. ✅ Auto-generated documentation (never manual duplication)

**Forbidden Patterns:**
1. ❌ Explicit filter parameters in tool signatures
2. ❌ Manual parameter mapping to `build_filters()`
3. ❌ Tool-specific filter logic
4. ❌ Hard-coded filter names
5. ❌ Duplicated filter documentation

**When in doubt:** Follow the patterns in Tools 1, 2a, 2b, and 5 (post-v1.2.0 refactor).

---

**Questions?** See:
- `ARCHITECTURE.md` - Complete system architecture
- `TOOLS_ROADMAP.md` - Tool implementation roadmap
- `TEST_PROMPTS.md` - Testing examples
- `convenience_tools.py` - `COMMON_FILTERS` dict and `build_filters()` implementation

**End of Design Principles Document**
