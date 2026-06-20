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
        Cache TTL: 86400s (24 hours - static data, rarely changes)
        
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
            from ...server import _client
            client = _client()
            
            # Cache key
            cache_key = "plugin_families_all"
            
            # Try cache first
            try:
                if hasattr(client, 'cache') and client.cache:
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
                        
                        # Cache for 24 hours (static data)
                        client.cache.set(cache_key, families, ttl=86400)
                        logger.debug(f"Cached {len(families)} plugin families (TTL: 86400s / 24h)")
                else:
                    # No cache - direct API call
                    result = client.get("pluginFamily", params={"fields": "name"})
                    
                    if not result.get("ok"):
                        return {
                            "ok": False,
                            "error": "Failed to fetch plugin families",
                            "details": result.get("error")
                        }
                    
                    families = result.get("response", [])
            
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
