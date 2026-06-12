# Tenable.sc MCP Server - Design Principles & Architecture Guidelines

**Version**: 1.2.1  
**Last Updated**: 2026-06-12  
**Status**: Living Document - Core Principles Established

---

## 📑 Table of Contents

- [Overview](#overview)
- [Core Design Principles](#core-design-principles)
  - [1. Centralized Filter Management](#1-centralized-filter-management-mandatory)
  - [2. Self-Documenting APIs](#2-self-documenting-apis)
  - [3. Token Optimization](#3-token-optimization)
  - [4. Intelligent Caching](#4-intelligent-caching)
  - [5. Fail-Safe Error Handling](#5-fail-safe-error-handling)
- [Tool Development Standards](#tool-development-standards)
- [Architecture Patterns](#architecture-patterns)
- [Testing & Validation](#testing--validation)
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

## Version History

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
