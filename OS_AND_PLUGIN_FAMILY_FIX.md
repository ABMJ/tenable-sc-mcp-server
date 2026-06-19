# v1.3.0 Implementation Plan - OS Filtering & Plugin Family Fix

**Version:** v1.3.0  
**Created:** 2026-06-18  
**Status:** Ready for Implementation  
**Estimated Time:** 6-8 hours total  
**Breaking Changes:** Plugin family filter (v1.2.1 → v1.3.0)

---

## 🎯 Executive Summary

This release solves two critical issues discovered through user testing and API analysis:

1. **CPE False Positives** - Regex patterns cause unintended matches (e.g., Windows 10 pattern matches Server 2019)
2. **Plugin Family Filter Broken** - Current code uses family NAME but API requires numeric ID

**Solution Strategy:**
- Add `operatingSystem` filter for exact OS matching (zero false positives)
- Implement smart OS lookup: User requests "Windows 10" → Tool queries listos → Filters exact names → Returns precise results
- Fix plugin family filter with smart name→ID lookup
- Create two helper tools for filter value discovery
- **NO HARDCODING** - All logic centralized in convenience_tools.py following design principles

**Impact:** Eliminates false positives, improves UX, maintains backward compatibility

---

## 📊 Key Findings from API Analysis

### Finding #1: Operating System Exact Matching

**API Discovery Tool:** `listos` (analysis tool)

**Request:**
```json
{
  "query": {
    "type": "vuln",
    "tool": "listos",
    "sourceType": "cumulative",
    "startOffset": 0,
    "endOffset": 50
  }
}
```

**Response:** Returns list of exact OS names with counts
```json
{
  "results": [
    {"name": "Microsoft Windows 10 Pro Build 19045", "count": 7},
    {"name": "Microsoft Windows Server 2019 Standard Build 17763", "count": 15},
    {"name": "Oracle Linux Server 8.9", "count": 32}
  ]
}
```

**Filter Usage in API:**
```json
{
  "filterName": "operatingSystem",
  "operator": "=",
  "value": "'Microsoft Windows 10 Pro Build 19045'"  // Single quotes inside string
}
```

**Key Insight:** This provides EXACT matching - no regex, no false positives!

---

### Finding #2: Plugin Family Requires Numeric IDs

**API Discovery Endpoint:** `GET /rest/pluginFamily?fields=name`

**Response:** Returns ID + name pairs
```json
{
  "response": [
    {"id": "20", "name": "Windows"},
    {"id": "10", "name": "Windows : Microsoft Bulletins"},
    {"id": "30", "name": "General"},
    {"id": "1000007", "name": "Generic"},
    {"id": "2000004", "name": "Cross Site Scripting"}
  ]
}
```

**Filter Usage in API:**
```json
{
  "filterName": "family",
  "operator": "=",
  "value": [{"id": "20"}, {"id": "10"}, {"id": "29"}]  // Array of ID objects
}
```

**Current Bug:** Code maps `family="Windows"` but API needs `family=[{"id": "20"}]`

**ID Ranges:**
- Standard families: `1-74` (Windows=20, General=30)
- Extended families: `1000001-1000034` (Generic=1000007, Cloud=1000031)
- WAS families: `2000001-2000014` (XSS=2000004, Injection=2000009)

---

## 🏗️ Architecture Design

### Smart OS Filtering Workflow

**User Request:** "Show me all Windows 10 hosts"

**Implementation Flow:**
```
1. User Query: filters={"os_name": "Windows 10"}  (partial match accepted)
2. Tool calls: tsc_analyze(tool="listos") → Get all OS names
3. Smart Filter: Match "Windows 10" against listos results
   - "Microsoft Windows 10 Pro Build 19045" ✅ Match
   - "Microsoft Windows 10 Enterprise" ✅ Match
   - "Microsoft Windows Server 2019" ❌ No match
4. Loop: For each matched OS name:
   - Query: filters=[{"filterName": "operatingSystem", "operator": "=", "value": "'...'"}]
   - Call: tsc_analyze(tool="sumip", filters=[...])
5. Aggregate: Deduplicate IPs across multiple OS queries
6. Return: Unified result set with zero false positives
```

**Benefits:**
- ✅ User-friendly: Accepts partial name "Windows 10"
- ✅ Accurate: Uses exact API matches
- ✅ Intelligent: Handles multiple OS variants automatically
- ✅ Fast: Caches listos results (300s TTL)

---

### Smart Plugin Family Lookup Workflow

**User Request:** `filters={"family": "Windows"}`

**Implementation Flow:**
```
1. Parse Filter: Detect family parameter value
2. Check Type:
   - If numeric (e.g., "20") → Use directly
   - If string (e.g., "Windows") → Lookup required
3. Lookup Cache:
   - Key: "plugin_family_map"
   - TTL: 600s (10 min - static data)
   - If MISS: Call GET /rest/pluginFamily?fields=name
4. Name→ID Resolution:
   - Input: "Windows"
   - Search: Case-insensitive partial match
   - Found: [{"id": "20", "name": "Windows"}]
   - Output: "20"
5. API Format Conversion:
   - Single: "20" → [{"id": "20"}]
   - Multiple: ["20", "10"] → [{"id": "20"}, {"id": "10"}]
6. Build Filter: {"filterName": "family", "operator": "=", "value": [{"id": "20"}]}
```

**Fallback Behavior:**
- If name not found → Log WARNING, skip filter (don't break query)
- If API call fails → Use cache or return helpful error

---

## 📝 Detailed Implementation Tasks

### Phase 1: Core Filter Infrastructure (2-3 hours)

#### Task 1.1: Update COMMON_FILTERS Dictionary

**File:** `src/tenable_sc_mcp/convenience_tools.py`

**Location:** Find the `COMMON_FILTERS` dictionary (around line 100-250)

**Add to COMMON_FILTERS:**
```python
# Operating System Filters (NEW in v1.3.0)
"operating_system": "operatingSystem",  # Exact OS match - RECOMMENDED
"os_name": "operatingSystem",           # Alias for user-friendliness
"os_exact": "operatingSystem",          # Alias for explicit intent
```

**Update count comment:**
```python
# Total filters: 74 (was 71 in v1.2.1)
```

**DO NOT modify existing `"family": "family"` line** - we'll handle it in build_filters()

**Result:** 71 filters → 74 filters (added 3 OS aliases)

---

#### Task 1.2: Implement Helper Functions in convenience_tools.py

**File:** `src/tenable_sc_mcp/convenience_tools.py`

**Location:** Add these functions BEFORE the `build_filters()` function (around line 450-500)

**Function 1: Fetch Plugin Families with Cache**

```python
def get_plugin_families(client: Any) -> dict[str, str]:
    """
    Fetch plugin families from API with caching.
    Returns dict mapping family name (lowercase) to ID.
    
    Cache Strategy:
        - Key: "plugin_families_map"
        - TTL: 600s (10 min - static data)
        - Structure: {"windows": "20", "general": "30", ...}
    
    Args:
        client: Tenable.sc client instance
    
    Returns:
        Dict mapping family name to ID: {"windows": "20", ...}
    
    Note: This is a helper function - not exposed as MCP tool
    """
    import logging
    logger = logging.getLogger(__name__)
    
    cache_key = "plugin_families_map"
    
    # Try cache first
    try:
        cached = client.cache.get(cache_key)
        if cached:
            logger.debug(f"Plugin families loaded from cache (key: {cache_key})")
            return cached
    except Exception as e:
        logger.warning(f"Cache read failed for plugin families: {e}")
    
    # Cache miss - fetch from API
    try:
        from .client import TenableSecurityCenterClient
        
        # Call GET /rest/pluginFamily?fields=name
        result = client.get("pluginFamily", params={"fields": "name"})
        
        if not result.get("ok"):
            logger.error(f"Failed to fetch plugin families: {result.get('error')}")
            return {}
        
        families = result.get("response", [])
        
        # Build name→ID mapping (lowercase for case-insensitive lookup)
        family_map = {
            family["name"].strip().lower(): family["id"]
            for family in families
            if "id" in family and "name" in family
        }
        
        # Cache for 10 minutes
        try:
            client.cache.set(cache_key, family_map, ttl=600)
            logger.debug(f"Cached {len(family_map)} plugin families (TTL: 600s)")
        except Exception as e:
            logger.warning(f"Cache write failed for plugin families: {e}")
        
        return family_map
    
    except Exception as e:
        logger.error(f"Error fetching plugin families: {e}", exc_info=True)
        return {}


def resolve_plugin_family_id(name_or_id: str, client: Any) -> str | None:
    """
    Convert plugin family name to numeric ID, or pass through if already ID.
    
    Args:
        name_or_id: Family name ("Windows") or ID ("20")
        client: Tenable.sc client
    
    Returns:
        Numeric ID string, or None if not found
    
    Examples:
        "Windows" → "20"
        "20" → "20"
        "windows : microsoft bulletins" → "10"
        "InvalidFamily" → None (logs warning)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    value = str(name_or_id).strip()
    
    # Check if already numeric ID
    if value.isdigit():
        logger.debug(f"Plugin family value is already numeric ID: {value}")
        return value
    
    # Lookup name→ID
    family_map = get_plugin_families(client)
    
    if not family_map:
        logger.warning("Plugin family map is empty - cannot resolve name to ID")
        return None
    
    # Case-insensitive lookup
    value_lower = value.lower()
    
    # Direct match
    if value_lower in family_map:
        family_id = family_map[value_lower]
        logger.debug(f"Resolved plugin family '{value}' → ID '{family_id}'")
        return family_id
    
    # Partial match (fallback)
    for family_name, family_id in family_map.items():
        if value_lower in family_name or family_name in value_lower:
            logger.debug(f"Partial match: plugin family '{value}' → ID '{family_id}' (matched '{family_name}')")
            return family_id
    
    # Not found
    logger.warning(f"Unknown plugin family: '{value}'. Use tsc_list_plugin_families() to discover valid names/IDs.")
    return None


def format_family_filter_value(ids: list[str]) -> list[dict]:
    """
    Convert list of IDs to Tenable.sc API format.
    
    Args:
        ids: ["20", "10", "30"]
    
    Returns:
        [{"id": "20"}, {"id": "10"}, {"id": "30"}]
    """
    return [{"id": str(id_val)} for id_val in ids]
```

---

**Function 2: Fetch Operating Systems with Cache**

```python
def get_operating_systems(client: Any) -> list[dict]:
    """
    Fetch all operating systems from listos tool with caching.
    Returns list of OS entries with name and count.
    
    Cache Strategy:
        - Key: "listos_all_os"
        - TTL: 300s (5 min - semi-static)
        - Structure: [{"name": "...", "count": 123}, ...]
    
    Args:
        client: Tenable.sc client instance
    
    Returns:
        List of OS dicts: [{"name": "Microsoft Windows 10 Pro", "count": 7}, ...]
    
    Note: This is a helper function - not exposed as MCP tool
    """
    import logging
    logger = logging.getLogger(__name__)
    
    cache_key = "listos_all_os"
    
    # Try cache first
    try:
        cached = client.cache.get(cache_key)
        if cached:
            logger.debug(f"Operating systems loaded from cache (key: {cache_key})")
            return cached
    except Exception as e:
        logger.warning(f"Cache read failed for operating systems: {e}")
    
    # Cache miss - fetch from API using listos analysis tool
    try:
        query = {
            "type": "vuln",
            "tool": "listos",
            "sourceType": "cumulative",
            "startOffset": 0,
            "endOffset": 500,  # Get first 500 OS (covers most environments)
            "sortColumn": "count",
            "sortDirection": "desc",
            "filters": []
        }
        
        # Use existing analyze wrapper
        result = client.analyze(query)
        
        if not result.get("ok"):
            logger.error(f"Failed to fetch operating systems: {result.get('error')}")
            return []
        
        response = result.get("response", {})
        os_list = response.get("results", [])
        
        # Cache for 5 minutes
        try:
            client.cache.set(cache_key, os_list, ttl=300)
            logger.debug(f"Cached {len(os_list)} operating systems (TTL: 300s)")
        except Exception as e:
            logger.warning(f"Cache write failed for operating systems: {e}")
        
        return os_list
    
    except Exception as e:
        logger.error(f"Error fetching operating systems: {e}", exc_info=True)
        return []


def match_operating_systems(partial_name: str, client: Any) -> list[str]:
    """
    Match user's partial OS name against available OS names.
    Returns list of exact OS names that match.
    
    Algorithm:
        1. Fetch all OS names from listos (cached)
        2. Normalize: lowercase input and OS names
        3. Split input into tokens: "Windows 10" → ["windows", "10"]
        4. Match if ALL tokens present in OS name
        5. Apply smart exclusion (e.g., "Windows 10" excludes "Server")
    
    Args:
        partial_name: User input like "Windows 10", "Oracle Linux", "CentOS 7"
        client: Tenable.sc client
    
    Returns:
        List of exact OS names: ["Microsoft Windows 10 Pro Build 19045", ...]
    
    Examples:
        "Windows 10" → ["Microsoft Windows 10 Pro Build 19045", 
                        "Microsoft Windows 10 Enterprise"]
        "Server 2019" → ["Microsoft Windows Server 2019 Standard Build 17763"]
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not partial_name:
        return []
    
    # Get all OS names
    os_list = get_operating_systems(client)
    
    if not os_list:
        logger.warning("Operating systems list is empty - cannot match partial name")
        return []
    
    # Normalize input
    user_input = partial_name.strip().lower()
    user_tokens = user_input.split()
    
    matches = []
    
    for os_entry in os_list:
        os_name = os_entry.get("name", "")
        if not os_name:
            continue
        
        os_name_lower = os_name.lower()
        
        # All tokens must be present
        if all(token in os_name_lower for token in user_tokens):
            # Smart exclusion: If searching "Windows 10", exclude "Server" unless explicitly requested
            if "server" in os_name_lower and "server" not in user_input:
                logger.debug(f"Excluding '{os_name}' (contains 'server', not in user input)")
                continue
            
            # Smart exclusion: If searching "Windows Server", exclude non-Server
            if "server" in user_input and "server" not in os_name_lower:
                logger.debug(f"Excluding '{os_name}' (user requested 'server', OS is not server)")
                continue
            
            matches.append(os_name)
            logger.debug(f"Matched OS: '{os_name}' for input '{partial_name}'")
    
    logger.info(f"Found {len(matches)} OS matches for '{partial_name}'")
    
    if not matches:
        logger.warning(f"No operating systems matched '{partial_name}'. Use tsc_list_operating_systems() to discover valid OS names.")
    
    return matches
```

---

#### Task 1.3: Update build_filters() Function

**File:** `src/tenable_sc_mcp/convenience_tools.py`

**Location:** Find the `build_filters()` function (around line 500-650)

**Add at the BEGINNING of build_filters() (after docstring, before filter loop):**

```python
def build_filters(client: Any = None, validate: bool = True, **kwargs) -> list[dict]:
    """
    [Keep existing docstring]
    """
    import logging
    logger = logging.getLogger(__name__)
    
    result = []
    
    # ========================================================================
    # SPECIAL HANDLING: Operating System Filter (v1.3.0)
    # ========================================================================
    # Check for operating_system, os_name, or os_exact parameters
    os_param_keys = ["operating_system", "os_name", "os_exact"]
    os_value = None
    
    for key in os_param_keys:
        if key in kwargs:
            os_value = kwargs.pop(key)  # Remove from kwargs to avoid duplicate processing
            break
    
    if os_value:
        if not client:
            logger.error("Operating system filter requires client instance")
        else:
            # Match partial OS name to exact OS names
            matched_os_names = match_operating_systems(os_value, client)
            
            if matched_os_names:
                # Create exact-match filter for each matched OS
                # Note: Multiple OS filters are OR'd by Tenable.sc API
                for os_name in matched_os_names:
                    result.append({
                        "filterName": "operatingSystem",
                        "operator": "=",
                        "value": f"'{os_name}'"  # Single quotes inside string
                    })
                    logger.debug(f"Added OS filter: {os_name}")
            else:
                logger.warning(f"No operating systems matched '{os_value}' - filter skipped")
    
    # ========================================================================
    # SPECIAL HANDLING: Plugin Family Filter (v1.3.0 FIX)
    # ========================================================================
    if "family" in kwargs:
        if not client:
            logger.error("Plugin family filter requires client instance")
        else:
            family_value = kwargs.pop("family")  # Remove from kwargs
            
            # Handle list or single value
            if isinstance(family_value, list):
                family_values = family_value
            else:
                family_values = [family_value]
            
            # Resolve each name/ID to numeric ID
            family_ids = []
            for value in family_values:
                family_id = resolve_plugin_family_id(value, client)
                if family_id:
                    family_ids.append(family_id)
            
            if family_ids:
                # Format for API: [{"id": "20"}, {"id": "10"}]
                result.append({
                    "filterName": "family",
                    "operator": "=",
                    "value": format_family_filter_value(family_ids)
                })
                logger.debug(f"Added family filter with IDs: {family_ids}")
            else:
                logger.warning(f"No valid plugin family IDs resolved from {family_values} - filter skipped")
    
    # ========================================================================
    # EXISTING FILTER PROCESSING (keep all existing code below)
    # ========================================================================
    # [Rest of existing build_filters() code continues here...]
```

**Important Notes:**
- Add this code at the START of build_filters(), right after parameter setup
- Do NOT modify any existing filter processing logic
- The special handlers remove their keys from kwargs before regular processing
- Keep all existing severity conversion, boolean normalization, range validation code

---

### Phase 2: Helper Tools Implementation (2-3 hours)

#### Task 2.1: Create tsc_list_operating_systems Tool

**File:** `src/tenable_sc_mcp/tools/asset_discovery.py`

**Location:** Add at the END of the file, before the final `register_tools()` function

**Implementation:**

```python
@mcp.tool()
def tsc_list_operating_systems(
    sort_by: str = "count",  # count | name
    limit: int = 50,
    start_offset: int = 0,
) -> dict[str, Any]:
    """
    List all operating systems detected in your environment with asset counts.
    Use this to discover valid OS names for the operating_system filter.
    
    WHEN TO USE THIS TOOL:
    - User asks "what operating systems are in our environment"
    - User needs to find exact OS name for filtering
    - User asks "show me all Windows versions we have"
    - Before using operating_system filter (discover valid values)
    
    This tool wraps the Tenable.sc 'listos' analysis tool and returns
    deduplicated OS names with counts. Use the exact name in your
    operating_system filter for zero false positives.
    
    Token Efficiency: ~1,500-2,000 tokens (vs ~8,000 raw)
    Cache TTL: 300s (5 min - semi-static data)
    
    Args:
        sort_by: Sort order: "count" (default) or "name"
        limit: Max OS entries to return (1-200, default: 50)
        start_offset: Starting record for pagination (default: 0)
    
    Returns:
        Dict with:
        - ok: True/False
        - total_os: Total unique OS detected
        - returned: Number returned in this response
        - operating_systems: List of {name: str, count: int}
        - pagination: {start: int, end: int, more_available: bool}
    
    Example:
        >>> tsc_list_operating_systems(limit=10)
        {
            "ok": True,
            "total_os": 257,
            "returned": 10,
            "operating_systems": [
                {"name": "Linux Kernel 4.8", "count": 56},
                {"name": "Microsoft Windows 10 Pro Build 19045", "count": 7},
                ...
            ],
            "pagination": {"start": 0, "end": 50, "more_available": True}
        }
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Build listos query
        query = {
            "type": "vuln",
            "tool": "listos",
            "sourceType": "cumulative",
            "startOffset": start_offset,
            "endOffset": start_offset + limit,
            "sortColumn": sort_by,
            "sortDirection": "desc",
            "filters": []
        }
        
        # Get client
        from ..client import get_client
        client = get_client()
        
        # Call analysis API (uses existing caching in analyze())
        result = client.analyze(query)
        
        if not result.get("ok"):
            return {
                "ok": False,
                "error": "Failed to query operating systems",
                "details": result.get("error"),
                "hint": "Check Tenable.sc connectivity and permissions"
            }
        
        response = result.get("response", {})
        os_list = response.get("results", [])
        total = int(response.get("totalRecords", 0))
        returned = int(response.get("returnedRecords", 0))
        
        # Format response
        return {
            "ok": True,
            "total_os": total,
            "returned": returned,
            "operating_systems": [
                {
                    "name": os_entry["name"],
                    "count": int(os_entry["count"]),
                    "detection_method": os_entry.get("detectionMethod", "N/A")
                }
                for os_entry in os_list
            ],
            "pagination": {
                "start": start_offset,
                "end": start_offset + limit,
                "more_available": (start_offset + returned) < total
            },
            "usage_tip": (
                "Use exact 'name' values in operating_system filter for precise matching. "
                "Example: filters={'operating_system': 'Microsoft Windows 10 Pro Build 19045'} "
                "or use partial name for smart matching: filters={'os_name': 'Windows 10'}"
            )
        }
    
    except Exception as e:
        logger.error(f"Error in tsc_list_operating_systems: {e}", exc_info=True)
        return {
            "ok": False,
            "error": "Unexpected error listing operating systems",
            "hint": "Check server logs for details"
        }
```

**Update register_tools():**

Add this tool to the registration function at the end of `asset_discovery.py`:

```python
def register_tools(mcp):
    """Register all asset discovery tools."""
    
    @mcp.tool()
    def tsc_list_ips(...):
        # existing code
    
    @mcp.tool()
    def tsc_profile_ip_efficient(...):
        # existing code (if in this file)
    
    # NEW: Register OS discovery tool
    @mcp.tool()
    def tsc_list_operating_systems(...):
        # code from above
```

---

#### Task 2.2: Create tsc_list_plugin_families Tool

**File:** Create NEW file `src/tenable_sc_mcp/tools/admin/plugins.py`

**Full File Contents:**

```python
"""
Admin tools for plugin management.

Provides tools for discovering plugin families and metadata.
"""

from __future__ import annotations
from typing import Any


def register_tools(mcp):
    """Register all plugin management tools."""
    
    @mcp.tool()
    def tsc_list_plugin_families(
        search: str | None = None,
    ) -> dict[str, Any]:
        """
        List all Nessus plugin families with IDs for filtering.
        Use this to discover valid family IDs/names for the family filter.
        
        WHEN TO USE THIS TOOL:
        - User asks "what plugin families are available"
        - User needs family ID for filtering
        - User asks "show me all Windows plugin families"
        - Before using family filter (discover valid IDs)
        
        Plugin families organize Nessus plugins by platform, technology, or
        vulnerability type. Use the 'id' field in your family filter.
        
        Token Efficiency: ~800-1,200 tokens
        Cache TTL: 600s (10 min - static data)
        
        Args:
            search: Optional search term to filter families by name
                    (case-insensitive partial match)
        
        Returns:
            Dict with:
            - ok: True/False
            - total_families: Total count
            - families: List of {id: str, name: str}
            - search_applied: Search term if provided
        
        Example:
            >>> tsc_list_plugin_families(search="Windows")
            {
                "ok": True,
                "total_families": 3,
                "search_applied": "Windows",
                "families": [
                    {"id": "20", "name": "Windows"},
                    {"id": "10", "name": "Windows : Microsoft Bulletins"},
                    {"id": "29", "name": "Windows : User management"}
                ],
                "usage_tip": "Use 'id' in family filter. Smart lookup accepts name or ID."
            }
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            from ...client import get_client
            client = get_client()
            
            # Cache key
            cache_key = "plugin_families_all"
            
            # Try cache first
            try:
                cached = client.cache.get(cache_key)
                if cached:
                    families = cached
                    logger.debug("Plugin families loaded from cache")
                else:
                    # Call API: GET /rest/pluginFamily?fields=name
                    result = client.get("pluginFamily", params={"fields": "name"})
                    
                    if not result.get("ok"):
                        return {
                            "ok": False,
                            "error": "Failed to fetch plugin families",
                            "details": result.get("error"),
                            "hint": "Check Tenable.sc connectivity and permissions"
                        }
                    
                    families = result.get("response", [])
                    
                    # Cache for 10 minutes (static data)
                    client.cache.set(cache_key, families, ttl=600)
                    logger.debug(f"Cached {len(families)} plugin families (TTL: 600s)")
            
            except Exception as e:
                logger.warning(f"Cache operation failed, proceeding with API call: {e}")
                # Fallback to direct API call
                result = client.get("pluginFamily", params={"fields": "name"})
                
                if not result.get("ok"):
                    return {
                        "ok": False,
                        "error": "Failed to fetch plugin families",
                        "details": result.get("error")
                    }
                
                families = result.get("response", [])
            
            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                families = [
                    f for f in families
                    if search_lower in f.get("name", "").lower()
                ]
            
            return {
                "ok": True,
                "total_families": len(families),
                "search_applied": search if search else None,
                "families": [
                    {"id": f["id"], "name": f["name"]}
                    for f in families
                ],
                "id_ranges": {
                    "standard": "1-74 (Platform-specific: Windows, Linux, etc.)",
                    "extended": "1000001-1000034 (Categories: Generic, Cloud, etc.)",
                    "was": "2000001-2000014 (Web App Scanning families)"
                },
                "usage_tip": (
                    "Smart family filter accepts name OR ID. "
                    "Example: filters={'family': 'Windows'} or filters={'family': '20'}"
                )
            }
        
        except Exception as e:
            logger.error(f"Error in tsc_list_plugin_families: {e}", exc_info=True)
            return {
                "ok": False,
                "error": "Unexpected error listing plugin families",
                "hint": "Check server logs for details"
            }
```

---

#### Task 2.3: Update tools/__init__.py

**File:** `src/tenable_sc_mcp/tools/admin/__init__.py`

**Create this file if it doesn't exist:**

```python
"""
Admin tools package.
"""

from __future__ import annotations


def register_all_admin_tools(mcp):
    """Register all admin tools."""
    from .plugins import register_tools as register_plugin_tools
    
    register_plugin_tools(mcp)
```

---

**File:** `src/tenable_sc_mcp/tools/__init__.py`

**Update the register_all_tools() function:**

```python
def register_all_tools(mcp):
    """Register all tools from all modules."""
    from .ip_profiling import register_tools as register_ip_profiling
    from .vulnerability_lookup import register_tools as register_vuln_lookup
    from .asset_discovery import register_tools as register_asset_discovery
    from .admin import register_all_admin_tools  # NEW
    
    register_ip_profiling(mcp)
    register_vuln_lookup(mcp)
    register_asset_discovery(mcp)
    register_all_admin_tools(mcp)  # NEW
```

---

### Phase 3: Documentation Updates (1-2 hours)

#### Task 3.1: Update FILTER_FORMAT_REFERENCE.md

**File:** `FILTER_FORMAT_REFERENCE.md`

**Action:** Replace the CPE section (search for "## CPE" or around lines 299-338)

**New Content:**

```markdown
## Operating System Filtering - Two-Tier Approach (v1.3.0)

### Overview

v1.3.0 introduces exact OS matching to eliminate false positives discovered in v1.2.1 CPE testing.

**Problem Solved:** CPE regex patterns caused unintended matches:
- `.*windows.*(10|11).*` matched Server 2016/2019 (version "10.0.17763")
- Wasted tokens showing 30+ irrelevant results

### Tier 1: Exact Match via operating_system (RECOMMENDED) ⭐

**When to use:** You need precise OS targeting with zero false positives  
**Accuracy:** 100% - Uses exact string match  
**Discovery:** Use `tsc_list_operating_systems()` to find valid OS names

```python
# Step 1: Discover available OS names
result = tsc_list_operating_systems(limit=20)
# Returns: ["Microsoft Windows 10 Pro Build 19045", "Oracle Linux Server 8.9", ...]

# Step 2: Use exact name in filter
tsc_list_ips(
    repository="Default",
    filters={"operating_system": "Microsoft Windows 10 Pro Build 19045"}
)
# Returns: ONLY Build 19045, excludes all other Windows versions
```

**Aliases (all equivalent):**
- `operating_system` - Primary name
- `os_name` - User-friendly alias
- `os_exact` - Explicit intent alias

**Smart Matching (v1.3.0):**
Tools automatically handle partial OS names:
```python
# User provides partial name
filters = {"os_name": "Windows 10"}

# Tool internally:
# 1. Queries listos to get all OS names
# 2. Filters: "Microsoft Windows 10 Pro", "Microsoft Windows 10 Enterprise"
# 3. Creates exact-match filter for each
# 4. Aggregates results
# 5. Returns unified list with zero false positives
```

**Benefits:**
- ✅ Zero false positives
- ✅ No regex expertise needed
- ✅ Natural language query support
- ✅ Multiple OS variants handled automatically

---

### Tier 2: CPE Substring/Regex (Advanced, Use with Caution)

**When to use:** Broad matching across OS variants when exact names unknown  
**Accuracy:** May include related systems (false positives possible)

**Simple Substring (auto-detects ~= operator):**
```python
filters = {"cpe": "microsoft:windows"}  # All Windows variants
filters = {"cpe": "cisco"}              # All Cisco devices
filters = {"cpe": "linux"}              # All Linux distros
```

**Regex Patterns (auto-detects pcre operator):**
```python
# ✅ IMPROVED patterns with boundaries (v1.2.1+)
filters = {"cpe": ".*windows_(10|11).*"}                  # Underscore boundary
filters = {"cpe": ".*windows(?!_server).*(10|11).*"}      # Negative lookahead
filters = {"cpe": ".*:windows_server_201[6-9]:.*"}        # Colon boundaries

# ❌ AVOID these patterns (cause false positives)
filters = {"cpe": ".*windows.*(10|11).*"}                 # Too broad - matches Server 2019
filters = {"cpe": ".*windows_server_201[6-9].*"}          # No boundaries - matches Win 10
```

**Why CPE has false positives:**
- CPE strings include version numbers that can overlap
- Example: Server 2019 = version "10.0.17763" → matches pattern ".*(10|11).*"
- Example: Windows 10 contains "10" → matches pattern ".*201[6-9].*"

**Recommendation:**
Use Tier 1 (operating_system) for 90% of use cases. Only use CPE if you specifically need:
- Broad variant matching across unknown OS versions
- Regex patterns for complex logic
- Compatibility with external CPE databases

---

### Comparison Table

| Feature | Tier 1: operating_system | Tier 2: CPE |
|---------|-------------------------|-------------|
| **Accuracy** | 100% (exact match) | ~70-90% (regex dependent) |
| **False Positives** | Zero | Possible (pattern dependent) |
| **Ease of Use** | Easy (natural language) | Hard (regex expertise) |
| **Discovery Tool** | tsc_list_operating_systems | Manual research |
| **Use Case** | Precise targeting | Broad variant matching |
| **Examples** | "Windows 10 Pro Build 19045" | "all Windows variants" |

---

## Plugin Family Filtering (Fixed in v1.3.0)

**Breaking Change:** v1.2.1 family filter was broken (used name, API needs ID).  
**Fixed in v1.3.0:** Smart name→ID lookup with automatic conversion.

### Discovery Tool

Use `tsc_list_plugin_families()` to discover available families:

```python
# List all families
tsc_list_plugin_families()

# Search specific families
tsc_list_plugin_families(search="Windows")
# Returns: [
#   {"id": "20", "name": "Windows"},
#   {"id": "10", "name": "Windows : Microsoft Bulletins"}
# ]
```

### Usage (Smart Lookup)

The family filter now accepts name OR ID and automatically converts:

```python
# By name (smart lookup)
filters = {"family": "Windows"}  # Converts to ID "20"

# By ID (direct pass-through)
filters = {"family": "20"}  # Uses ID directly

# Multiple families (mixed name and ID)
filters = {"family": ["Windows", "30", "SCADA"]}  # Converts to IDs [20, 30, 36]
```

### Family ID Ranges

- **Standard families:** 1-74 (Windows=20, General=30, CISCO=33)
- **Extended families:** 1000001-1000034 (Generic=1000007, Cloud=1000031)
- **WAS families:** 2000001-2000014 (XSS=2000004, Injection=2000009)

### API Format (Internal)

For reference, the API format (handled automatically):
```json
{
  "filterName": "family",
  "operator": "=",
  "value": [{"id": "20"}, {"id": "10"}]
}
```

You don't need to know this - just provide name or ID in the filter dict.
```

---

#### Task 3.2: Create PLUGIN_FAMILY_INVESTIGATION.md

**File:** Create NEW `PLUGIN_FAMILY_INVESTIGATION.md`

**Content:** [See earlier comprehensive content - 200+ lines documenting the complete investigation]

*Note: I'll create this file with the full content from the plan*

---

#### Task 3.3: Update MCP Filter Reference Resource

**File:** `src/tenable_sc_mcp/resources/filter_reference.py`

**Action:** Update the auto-generated docs to mention new filters

**Find the section that generates filter documentation (around line 100-300)**

**Update the header or intro section:**

```python
def generate_filter_reference() -> str:
    """Generate comprehensive filter reference documentation."""
    
    header = f"""
# Tenable.sc Analysis Filter Reference

**Version:** v1.3.0  
**Last Updated:** {datetime.now().strftime("%Y-%m-%d")}  
**Total Filters:** 74 (NEW: operating_system, os_name, os_exact)

This document provides a complete reference for all 74+ Tenable.sc analysis 
filters available in convenience tools.

## What's New in v1.3.0

- **Operating System Exact Matching:** New `operating_system` filter for zero false positives
- **Plugin Family Fix:** Smart name→ID lookup (was broken in v1.2.1)
- **Helper Tools:** `tsc_list_operating_systems()` and `tsc_list_plugin_families()`
- **Two-Tier OS Filtering:** Exact match (Tier 1) vs CPE regex (Tier 2)

## Quick Start

**Discover Available Values:**
- OS names: Use `tsc_list_operating_systems()` tool
- Plugin families: Use `tsc_list_plugin_families()` tool

**Common Filter Examples:**
```python
# Exact OS matching (NEW - RECOMMENDED)
filters = {{"operating_system": "Microsoft Windows 10 Pro Build 19045"}}
filters = {{"os_name": "Windows 10"}}  # Smart partial matching

# Plugin family (FIXED - name or ID)
filters = {{"family": "Windows"}}  # Auto-converts to ID "20"
filters = {{"family": "20"}}       # Direct ID usage
```

---

"""
```

**Add special documentation for new filters:**

```python
# In the filter categories section, add:

special_filters = """
## Special Filters (v1.3.0)

### Operating System Filters

**New in v1.3.0** - Exact OS matching to eliminate false positives:

- `operating_system`: Exact OS name (RECOMMENDED)
- `os_name`: Alias for operating_system
- `os_exact`: Alias for operating_system

**API Field:** `operatingSystem`  
**Operator:** `=` (exact match)  
**Format:** Exact string from `listos` tool

**Discovery:**
Use `tsc_list_operating_systems()` to find valid OS names.

**Examples:**
- `"Microsoft Windows 10 Pro Build 19045"` - Exact build
- `"Oracle Linux Server 8.9"` - Specific version
- `"Windows 10"` - Smart partial match (finds all Win10 variants)

**Smart Matching:**
Provide partial name and tool automatically:
1. Queries listos for all OS names
2. Matches partial input (e.g., "Windows 10")
3. Creates exact filters for each match
4. Excludes unrelated systems (e.g., Server editions)
5. Returns aggregated results with zero false positives

---

### Plugin Family Filter

**Fixed in v1.3.0** - Was broken in v1.2.1 (used name, API needs ID):

- `family`: Plugin family name OR numeric ID

**API Field:** `family`  
**Format:** Array of ID objects: `[{{"id": "20"}}]`  
**Smart Lookup:** Accepts name or ID, auto-converts

**Discovery:**
Use `tsc_list_plugin_families()` to find family IDs and names.

**Examples:**
- `"Windows"` - Converts to ID "20"
- `"20"` - Uses ID directly
- `["Windows", "30", "SCADA"]` - Multiple families (mixed format)

**ID Ranges:**
- Standard: 1-74 (Windows=20, General=30)
- Extended: 1000001+ (Generic=1000007, Cloud=1000031)
- WAS: 2000001+ (XSS=2000004, Injection=2000009)

"""
```

---

### Phase 4: Design Principles Update

**File:** `DESIGN_PRINCIPLES.md`

**Action:** Add new principle for smart lookup pattern

**Location:** Find the "Core Design Principles" section (around line 40-400)

**Add new section (after caching, before tool development standards):**

```markdown
### 6. Smart Lookup Pattern (Name → ID Resolution)

**Principle**: When API requires numeric IDs but users know friendly names, implement smart lookup with caching.

**Pattern Introduced:** v1.3.0 (Plugin Family, Operating System filters)

#### When to Use

Apply this pattern when:
- API endpoint requires numeric/opaque identifiers
- Users naturally refer to resources by name
- There's a discovery API to fetch ID→name mappings
- The mapping is static or semi-static (cacheable)

#### Implementation Pattern

```python
# 1. Cache Lookup Table (centralized helper)
def get_resource_map(client: Any) -> dict[str, str]:
    """
    Fetch resource name→ID mapping with caching.
    
    Cache Strategy:
        - Key: "resource_map"
        - TTL: Based on volatility (600s for static, 300s for semi-static)
        - Structure: {"name_lowercase": "id"}
    """
    cache_key = "resource_map"
    
    # Try cache first
    cached = client.cache.get(cache_key)
    if cached:
        return cached
    
    # Fetch from API
    result = client.get("resource", params={"fields": "id,name"})
    
    # Build lowercase map for case-insensitive lookup
    resource_map = {
        item["name"].strip().lower(): item["id"]
        for item in result.get("response", [])
    }
    
    # Cache result
    client.cache.set(cache_key, resource_map, ttl=600)
    
    return resource_map


# 2. Smart Resolution Function
def resolve_resource_id(name_or_id: str, client: Any) -> str | None:
    """
    Convert resource name to ID, or pass through if already ID.
    
    Algorithm:
        1. Check if value is numeric → return as-is
        2. Fetch cached name→ID map
        3. Normalize input (lowercase, strip)
        4. Direct lookup
        5. Partial match fallback (optional)
        6. Return ID or None
    """
    value = str(name_or_id).strip()
    
    # Numeric pass-through
    if value.isdigit():
        return value
    
    # Lookup
    resource_map = get_resource_map(client)
    value_lower = value.lower()
    
    # Direct match
    if value_lower in resource_map:
        return resource_map[value_lower]
    
    # Partial match (optional)
    for name, res_id in resource_map.items():
        if value_lower in name or name in value_lower:
            return res_id
    
    # Not found - log warning, don't error
    logger.warning(f"Unknown resource: '{value}'")
    return None


# 3. Integration in build_filters()
def build_filters(client: Any = None, **kwargs) -> list[dict]:
    # Special handling before main loop
    if "resource_filter" in kwargs:
        value = kwargs.pop("resource_filter")
        resource_id = resolve_resource_id(value, client)
        
        if resource_id:
            result.append({
                "filterName": "resourceField",
                "operator": "=",
                "value": format_api_value(resource_id)
            })
        # If None, filter is skipped (graceful degradation)
    
    # Continue with regular filter processing...
```

#### Real-World Examples

**Example 1: Plugin Family Filter (v1.3.0)**
- API requires: `[{"id": "20"}]`
- User provides: `"Windows"` or `"20"`
- Implementation: `resolve_plugin_family_id()` + cache
- Behavior: Name→ID lookup, numeric pass-through

**Example 2: Operating System Filter (v1.3.0)**
- API requires: Exact string `"Microsoft Windows 10 Pro Build 19045"`
- User provides: Partial `"Windows 10"`
- Implementation: `match_operating_systems()` + listos cache
- Behavior: Partial→multiple exact matches, aggregation

#### Benefits

**For Users:**
- ✅ Natural language queries work
- ✅ No need to memorize IDs
- ✅ Helper tools for discovery
- ✅ Backward compatible (IDs still work)

**For Code:**
- ✅ Centralized lookup logic (DRY)
- ✅ Cache minimizes API calls
- ✅ Graceful fallback (missing ID → warning, not error)
- ✅ Testable independently

**For Maintenance:**
- ✅ Single source of truth (cache)
- ✅ Easy to extend to new resources
- ✅ Clear separation: lookup vs filter building

#### Anti-Patterns to Avoid

❌ **Hardcoded ID Mappings**
```python
# BAD - becomes stale
FAMILY_IDS = {"Windows": "20", "General": "30"}
```

❌ **Inline API Calls**
```python
# BAD - no caching, slow
def build_filters(**kwargs):
    if "family" in kwargs:
        families = requests.get("/pluginFamily")  # Every time!
```

❌ **Error on Unknown Name**
```python
# BAD - breaks query
if not resource_id:
    raise ValueError("Unknown resource")  # User can't recover
```

✅ **Correct Approach**
```python
# GOOD - cached, graceful
def resolve_id(name, client):
    cached_map = get_cached_map(client)  # Cache layer
    id = cached_map.get(name.lower())
    if not id:
        logger.warning(f"Unknown: {name}")  # Log, don't error
    return id  # None is OK - filter skipped
```

#### Testing Requirements

When implementing smart lookup:

1. **Cache Hit/Miss:** Test cache behavior (first call, repeat call)
2. **Name Variants:** Test lowercase, uppercase, mixed case
3. **Partial Matching:** Test substring matching (if implemented)
4. **Numeric Pass-Through:** Test direct ID usage
5. **Unknown Values:** Test graceful handling (warning, no error)
6. **Multiple Values:** Test list input handling
7. **Empty/None:** Test edge cases

#### Documentation Requirements

- Document discovery tool in tool docstring
- Reference discovery tool in filter docs
- Provide examples (name and ID usage)
- Explain smart matching behavior (if applicable)
- List ID ranges (if relevant)

---
```

**Add to version history (at end of file):**

```markdown
### v1.3.0 (2026-06-18)
- ✅ **Design Principle #6**: Smart Lookup Pattern (name→ID resolution)
- ✅ **Operating System Exact Matching**: Eliminates CPE false positives
- ✅ **Plugin Family Fix**: Smart name→ID lookup (broken in v1.2.1)
- ✅ **Helper Tools Pattern**: Discovery tools for filter value lookup
- ✅ **NO HARDCODING Rule**: All lookups via cached API calls
- ✅ **Centralized Logic**: Smart matching in convenience_tools.py only
```

---

### Phase 5: Test Cases (Documented Separately)

**See TEST_PROMPTS.md updates** - 11 new test cases with visual formatting

---

## 🎯 Key Architecture Decisions

### Decision 1: Smart OS Lookup vs Direct Exact Match

**Chosen:** Smart lookup (partial name → listos query → multiple exact matches)

**Rationale:**
- User doesn't know exact OS strings ("Microsoft Windows 10 Pro Build 19045")
- Natural language: "show me Windows 10 hosts" should work
- Tool handles discovery and filtering internally
- Zero false positives maintained (uses exact API matches)
- Better UX than forcing user to call listos first

---

### Decision 2: Smart Plugin Family Lookup

**Chosen:** Accept name OR ID, auto-convert to ID

**Rationale:**
- Best UX - user can use friendly names ("Windows")
- Backward compatible - existing IDs still work
- Cache minimizes lookup overhead (600s TTL)
- Graceful degradation on lookup failure (warning, not error)

---

### Decision 3: No Hardcoding - Dynamic Lookup Only

**Chosen:** All lookups via cached API calls, zero hardcoded mappings

**Rationale:**
- Future-proof: New plugin families don't break code
- Accurate: Always reflects current Tenable.sc state
- Maintainable: No manual updates needed
- Testable: Can mock API responses

**Alternatives Rejected:**
- Hardcode plugin family IDs → becomes stale
- Hardcode OS patterns → limited coverage

---

### Decision 4: Centralized Logic in convenience_tools.py

**Chosen:** All smart lookup logic in convenience_tools.py helper functions

**Rationale:**
- Single source of truth
- Reusable across all tools (no duplication)
- Testable independently
- Clear separation: helpers vs tools

**Alternatives Rejected:**
- Implement in each tool → massive duplication
- Implement in client.py → wrong layer (client = API wrapper)

---

## 🔧 Implementation Checklist

### Phase 1: Core Infrastructure ✅
- [ ] Update COMMON_FILTERS dict (add 3 OS aliases)
- [ ] Implement `get_plugin_families()` helper
- [ ] Implement `resolve_plugin_family_id()` helper
- [ ] Implement `format_family_filter_value()` helper
- [ ] Implement `get_operating_systems()` helper
- [ ] Implement `match_operating_systems()` helper
- [ ] Update `build_filters()` with special handling

### Phase 2: Helper Tools ✅
- [ ] Create `tsc_list_operating_systems()` tool
- [ ] Create `src/tenable_sc_mcp/tools/admin/plugins.py`
- [ ] Implement `tsc_list_plugin_families()` tool
- [ ] Create `src/tenable_sc_mcp/tools/admin/__init__.py`
- [ ] Update `src/tenable_sc_mcp/tools/__init__.py` registration

### Phase 3: Documentation ✅
- [ ] Update FILTER_FORMAT_REFERENCE.md (OS two-tier approach)
- [ ] Create PLUGIN_FAMILY_INVESTIGATION.md
- [ ] Update MCP resource filter_reference.py
- [ ] Update DESIGN_PRINCIPLES.md (smart lookup pattern)
- [ ] Append tests to TEST_PROMPTS.md (11 test cases)

### Phase 4: Testing ✅
- [ ] Run all 11 new test cases via MCP client
- [ ] Verify zero false positives (OS filtering)
- [ ] Verify smart lookup (plugin family)
- [ ] Test error handling (invalid inputs)
- [ ] Validate cache performance

### Phase 5: Deployment ✅
- [ ] Rebuild Docker container (no-cache)
- [ ] Verify 74 filters in logs
- [ ] Test helper tools via MCP
- [ ] Update HANDOFF.md
- [ ] Git commit with message

---

## 🚀 Success Criteria

**Implementation Complete When:**
- ✅ 74 filters available (was 71)
- ✅ `operating_system`, `os_name`, `os_exact` working
- ✅ Plugin family filter accepts name or ID
- ✅ `tsc_list_operating_systems()` tool working
- ✅ `tsc_list_plugin_families()` tool working
- ✅ All 11 test cases passing
- ✅ Zero false positives confirmed
- ✅ Documentation updated (5 files)
- ✅ Container rebuilt and deployed
- ✅ Git committed and tagged

**Quality Gates:**
- Code follows design principles (no hardcoding)
- All logic centralized in convenience_tools.py
- Helper tools properly registered
- Cache working (hit rate >50% after warmup)
- Error handling graceful (warnings, not errors)
- Documentation complete and accurate

---

## 📚 Reference Materials

**API Examples:**
- listos query: See "Finding #1" section above
- pluginFamily endpoint: See "Finding #2" section above
- operatingSystem filter: See API analysis section

**Code Locations:**
- COMMON_FILTERS: `src/tenable_sc_mcp/convenience_tools.py` ~line 100
- build_filters(): `src/tenable_sc_mcp/convenience_tools.py` ~line 500
- Tool registration: `src/tenable_sc_mcp/tools/__init__.py`

**Related Documents:**
- HANDOFF.md - Current project state
- DESIGN_PRINCIPLES.md - Mandatory patterns
- TEST_PROMPTS.md - Test case format
- FILTER_FORMAT_REFERENCE.md - User-facing docs

---

**Implementation Status:** 📋 Ready - All tasks documented  
**Estimated Time:** 6-8 hours  
**Next Step:** Start with Phase 1, Task 1.1 (Update COMMON_FILTERS)

---

**End of Implementation Plan**
