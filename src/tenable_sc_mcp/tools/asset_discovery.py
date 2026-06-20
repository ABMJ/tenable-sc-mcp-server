"""
Asset discovery and IP listing tools for Tenable.sc MCP Server.

Provides efficient IP enumeration with flexible filtering, asset group/repository
scoping, and optional metadata inclusion.
"""

from __future__ import annotations

from typing import Any

from ..convenience_tools import (
    validate_ip,
    build_filters,
    resolve_repository_name,
    resolve_asset_group_name,
)
from ..server import _client


def register_tools(mcp):
    """Register asset discovery tools with the MCP server."""
    
    @mcp.tool()
    def tsc_list_ips(
        repository: str | None = None,
        asset_group: str | None = None,
        ip: str | None = None,
        include_details: bool = False,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        List IP addresses in repositories or asset groups. Use this when you need to:
        - Enumerate all IPs in a specific repository or asset group
        - Find which repositories/asset groups contain a specific IP (reverse lookup)
        - Filter IPs by asset criticality, vulnerabilities, or other criteria
        - Get detailed IP metadata (hostname, MAC, OS, ACR score)
        
        WHEN TO USE THIS TOOL:
        - User asks "list IPs in X" or "what IPs are in X"
        - User asks "which asset group contains IP X" or "where is IP X"
        - User asks "show me high-risk IPs" (use asset_criticality filter)
        - User asks "list IPs with critical vulnerabilities" (use severity filter)
        - User needs IP inventory or asset discovery
        
        DO NOT USE for single IP profiling - use tsc_profile_ip_efficient instead.
        
        Key Features:
        - Automatic name-to-ID resolution for repositories and asset groups
        - 55+ filters: asset criticality (ACR), severity, exploits, VPR, CVSS, port, protocol, etc.
        - Reverse lookup mode: Find all repositories/asset groups containing an IP
        - Optional detailed metadata: DNS name, MAC address, OS, UUID, ACR score
        - Smart caching (120s TTL) for fast repeated queries
        - Token efficient: 400-3,700 tokens depending on dataset size
        
        Args:
            repository: Repository name or ID (e.g., "Default", "9", "PCI Assets")
            asset_group: Asset group name or ID (e.g., "Windows Hosts", "3")
            ip: Specific IP for reverse lookup (find membership in repos/groups)
            include_details: Return full metadata per IP (DNS, MAC, UUID, ACR, AES, OS)
            filters: Optional dict of filter parameters for narrowing results
                
                Scoring Filters (use RANGE format, NOT operators):
                    asset_criticality: ACR range (e.g., "7-10", "8-10"). DO NOT use ">7"
                    vpr_score: VPR range (e.g., "7-10", "8-10")
                    aes_score: AES range (e.g., "600-1000", "700-1000"). Scale: 0-1000
                    cvss_v3_base_score: CVSS v3 range (e.g., "7-10")
                    cvss_v4_base_score: CVSS v4 range (e.g., "7-10")
                    base_cvss_score: CVSS v2 range (e.g., "7-10")
                    epss_score: EPSS range (e.g., "0.5-1.0"). Scale: 0-1
                
                Other Filters:
                    uuid: Asset UUID filter
                    dns_name: DNS name filter (hostname)
                    first_seen: First seen timestamp (epoch)
                    last_seen: Last seen timestamp (epoch)
                    severity: Vulnerability severity (0-4 or info/low/medium/high/critical)
                    aes_severity: AES-based severity (info/low/medium/high/critical)
                    exploit_available: Exploit availability (Yes/No)
                    plugin_id: Specific plugin ID
                    family: Plugin family name
                    port: Port number
                    protocol: Protocol (TCP/UDP)
                
                IMPORTANT - Scoring Filter Format:
                - Use RANGE format: "min-max" (e.g., "7-10", "600-1000")
                - DO NOT use operators: ">7", ">=7", "<5", "<=5"
                - Why? Tenable.sc backend only supports inclusive ranges
            
        Returns:
            Success response with:
            - ok: True
            - total_ips: Number of IPs found
            - ips: List of IP addresses (or detailed objects if include_details=True)
            - repository/asset_group: Scope confirmation
            - filters_applied: Summary of applied filters (if any)
            
            For reverse lookup (ip parameter):
            - ok: True
            - ip: The queried IP
            - repositories: List of repository names containing this IP
            - asset_groups: List of asset group names containing this IP
            - found: Boolean indicating if IP exists
        
        Examples:
            >>> tsc_list_ips(repository="Default")
            {"ok": True, "repository": "Default", "total_ips": 413, "ips": ["10.1.20.10", ...]}
            
            >>> tsc_list_ips(asset_group="Windows Hosts", filters={"asset_criticality": "8-10"})
            {"ok": True, "asset_group": "Windows Hosts", "filters_applied": {"asset_criticality": "8-10"}, "total_ips": 12, "ips": [...]}
            
            >>> tsc_list_ips(repository="Default", filters={"asset_criticality": "7-10", "aes_score": "600-1000"})
            {"ok": True, "repository": "Default", "filters_applied": {"asset_criticality": "7-10", "aes_score": "600-1000"}, "total_ips": 54, "ips": [...]}
            
            >>> tsc_list_ips(ip="10.10.10.10")
            {
                "ok": True,
                "ip": "10.10.10.10",
                "repositories": ["Default", "PCI Assets"],
                "asset_groups": ["Windows Hosts", "Production Servers"]
            }
            
            >>> tsc_list_ips(repository="Default", include_details=True)
            {
                "ok": True,
                "repository": "Default",
                "total_ips": 156,
                "ips": [
                    {
                        "ip": "10.1.20.10",
                        "dns_name": "webserver01.domain.com",
                        "mac": "00:50:56:12:34:56",
                        "uuid": "abc123...",
                        "acr_score": 8.5,
                        "aes_score": 650,
                        "os": "Windows Server 2019"
                    }
                ]
            }
        """
        # Import server functions
        from .. import server
        
        # Validate inputs
        if ip:
            # Reverse lookup mode: find which asset groups/repos contain this IP
            valid, error = validate_ip(ip)
            if not valid:
                return {"ok": False, "error": error}
            
            return _find_ip_membership(ip)
        
        # Regular mode: list IPs in asset group or repository
        if not repository and not asset_group:
            return {
                "ok": False,
                "error": "Must provide either 'repository', 'asset_group', or 'ip' parameter",
                "hint": "Examples: repository='Default', asset_group='Windows Hosts', or ip='10.10.10.10'"
            }
        
        if repository and asset_group:
            return {
                "ok": False,
                "error": "Provide only ONE of: repository, asset_group (not both)",
                "hint": "Choose either repository='Default' OR asset_group='Windows Hosts'"
            }
        
        try:
            # Build base filters from provided parameters
            filter_list = []
            
            # Handle repository filter
            if repository:
                # Repository can be name or ID - try both approaches
                if repository.isdigit():
                    # Direct repository ID
                    filter_list.append({
                        "filterName": "repository",
                        "operator": "=",
                        "value": [{"id": repository}]
                    })
                else:
                    # Repository name - use repositoryIDs filter with resolved ID
                    repo_id = resolve_repository_name(repository)
                    if not repo_id:
                        return {
                            "ok": False,
                            "error": f"Repository not found: '{repository}'",
                            "hint": "Use tsc_resource_action(action='list', resource='repository') to see available repositories"
                        }
                    filter_list.append({
                        "filterName": "repository",
                        "operator": "=",
                        "value": [{"id": repo_id}]
                    })
            
            # Handle asset group filter
            if asset_group:
                # Asset group can be name or ID
                if asset_group.isdigit():
                    # Direct asset group ID - need to look up name
                    asset_group_id = asset_group
                    asset_group_name = asset_group  # Will try to resolve below
                else:
                    # Asset group name - need to look up ID
                    asset_group_name = asset_group
                    asset_group_id = resolve_asset_group_name(asset_group)
                    if not asset_group_id:
                        return {
                            "ok": False,
                            "error": f"Asset group not found: '{asset_group}'",
                            "hint": "Use tsc_resource_action(action='list', resource='asset') to see available asset groups"
                        }
                
                # Tenable.sc API expects asset filter with BOTH id and name (as strings, not array)
                # Format: {"id": "3", "name": "Windows Hosts"} - NOT [{"id": 3}]
                filter_list.append({
                    "filterName": "asset",
                    "operator": "=",
                    "value": {"id": str(asset_group_id), "name": asset_group_name}
                })
            
            # Extract filter dict
            filter_dict = filters or {}
            
            # Add additional filters from dict (v1.3.0.2: no longer returns OS names)
            # Note: Scoring filters must be in range format (e.g., "7-10", "600-1000").
            # Operators like ">7" will raise ValueError with helpful message.
            # v1.3.0.2: OS filters now use CPE partial matching (single query, efficient!)
            additional_filters, os_names_to_query = build_filters(client=_client(), **filter_dict)
            filter_list.extend(additional_filters)
            
            # Execute single query (v1.3.0.2: OS filter uses CPE, no multi-query needed)
            import json
            import logging
            logger = logging.getLogger(__name__)
            logger.debug("Filters being sent to Tenable.sc API:")
            logger.debug(json.dumps(filter_list, indent=2))
            
            query = {
                "type": "vuln",
                "query": {
                    "type": "vuln",
                    "tool": "sumip",
                    "filters": filter_list
                },
                "sourceType": "cumulative"
            }
            
            tsc_analyze = server.tsc_analyze
            result = tsc_analyze(query)
            
            if not result.get("ok"):
                return result
            
            # Extract IP data from response
            api_response = result.get("response", {})
            if isinstance(api_response, dict) and "response" in api_response:
                ip_data = api_response.get("response", {}).get("results", [])
            else:
                ip_data = api_response.get("results", [])
            
            # Format output based on include_details flag
            if include_details:
                # Return full metadata using correct field names from sumip response
                formatted_ips = []
                for item in ip_data:
                    ip_entry = {
                        "ip": item.get("ip"),
                        "dns_name": item.get("dnsName", ""),
                        "netbios_name": item.get("netbiosName", ""),
                        "mac_address": item.get("macAddress", ""),
                        "uuid": item.get("uuid", ""),
                        "os": item.get("operatingSystem", item.get("osCPE", "")),
                        "acr_score": item.get("acrScore", "0"),              # Asset Criticality Rating (0-10)
                        "aes_score": item.get("assetExposureScore", "0"),    # Asset Exposure Score (0-1000)
                        "repository": item.get("repository", {}).get("name", ""),
                    }
                    formatted_ips.append(ip_entry)
            else:
                # Return just IP addresses (minimal)
                formatted_ips = [item.get("ip") for item in ip_data if item.get("ip")]
            
            # Build response
            response = {
                "ok": True,
                "total_ips": len(formatted_ips),
                "ips": formatted_ips
            }
            
            # Add scope info
            if repository:
                response["repository"] = repository
            if asset_group:
                response["asset_group"] = asset_group
            
            # Track ALL applied filters dynamically
            # List all filter parameters from function signature (not scope/control params)
            filter_params = [
                'asset_criticality', 'uuid', 'dns_name', 
                'first_seen', 'last_seen',
                'vpr_score', 'aes_score', 'cvss_v3_base_score', 'cvss_v4_base_score', 
                'base_cvss_score', 'epss_score',
                'severity', 'aes_severity', 'exploit_available',
                'plugin_id', 'family', 'port', 'protocol'
            ]
            
            filters_applied = {
                param: locals()[param]
                for param in filter_params
                if locals().get(param) is not None
            }
            
            if filters_applied:
                response["filters_applied"] = filters_applied
            
            return response
        
        except Exception as exc:
            return {
                "ok": False,
                "error": f"Failed to list IPs: {exc}",
                "hint": "Verify repository/asset group name is correct. Use tsc_list('repository') or tsc_list('asset') to see available options."
            }




def _find_ip_membership(ip: str) -> dict[str, Any]:
    """
    Find which asset groups and repositories contain a specific IP (reverse lookup).
    
    Args:
        ip: IP address to lookup
    
    Returns:
        Dictionary with repositories and asset_groups lists
    """
    try:
        # Import server for API access
        from .. import server
        
        # Query 1: Get repository membership using sumip
        repo_query = {
            "type": "vuln",
            "query": {
                "type": "vuln",
                "tool": "sumip",
                "filters": [
                    {"filterName": "ip", "operator": "=", "value": ip}
                ]
            },
            "sourceType": "cumulative"
        }
        
        tsc_analyze = server.tsc_analyze
        repo_result = tsc_analyze(repo_query)
        
        repositories = []
        if repo_result.get("ok"):
            # Extract repository data
            api_response = repo_result.get("response", {})
            if isinstance(api_response, dict) and "response" in api_response:
                ip_data = api_response.get("response", {}).get("results", [])
            else:
                ip_data = api_response.get("results", [])
            
            # Extract unique repository names
            for item in ip_data:
                repo_info = item.get("repository", {})
                if repo_info and isinstance(repo_info, dict):
                    repo_name = repo_info.get("name")
                    if repo_name and repo_name not in repositories:
                        repositories.append(repo_name)
        
        # Query 2: Get asset group membership using sumasset (required for asset groups!)
        asset_query = {
            "type": "vuln",
            "query": {
                "type": "vuln",
                "tool": "sumasset",
                "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
            },
            "sourceType": "cumulative"
        }
        
        asset_result = tsc_analyze(asset_query)
        
        asset_groups = []
        if asset_result.get("ok"):
            # Extract asset group data
            api_response = asset_result.get("response", {})
            if isinstance(api_response, dict) and "response" in api_response:
                asset_data = api_response.get("response", {}).get("results", [])
            else:
                asset_data = asset_result.get("results", [])
            
            # Extract unique asset group names where IP is actually present
            # sumasset returns ALL asset groups, need to filter by total > 0
            for asset in asset_data:
                # Check if this asset group actually contains the IP (total > 0)
                total_count = asset.get("total", 0)
                
                # Convert to int if it's a string
                if isinstance(total_count, str):
                    try:
                        total_count = int(total_count)
                    except ValueError:
                        total_count = 0
                
                # Only include asset groups where the IP is actually present
                if total_count > 0 and "asset" in asset:
                    asset_info = asset.get("asset", {})
                    if isinstance(asset_info, dict) and asset_info.get("name"):
                        asset_name = asset_info.get("name")
                        if asset_name and asset_name not in asset_groups:
                            asset_groups.append(asset_name)
        
        # Check if IP was found
        found = len(repositories) > 0 or len(asset_groups) > 0
        
        return {
            "ok": True,
            "ip": ip,
            "found": found,
            "repositories": repositories,
            "asset_groups": asset_groups
        }
    
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed to lookup IP membership: {exc}"
        }
    
    
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
            # Validate parameters
            if limit < 1 or limit > 200:
                return {
                    "ok": False,
                    "error": "limit must be between 1 and 200"
                }
            
            if start_offset < 0:
                return {
                    "ok": False,
                    "error": "start_offset must be >= 0"
                }
            
            if sort_by not in ("count", "name"):
                return {
                    "ok": False,
                    "error": f"Invalid sort_by: {sort_by}. Use 'count' or 'name'"
                }
            
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
            
            # Call analysis API (uses existing caching in tsc_analyze)
            from ..server import tsc_analyze
            result = tsc_analyze(query)
            
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


# Export for testing
__all__ = ["register_tools"]
