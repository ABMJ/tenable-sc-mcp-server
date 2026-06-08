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


def register_tools(mcp):
    """Register asset discovery tools with the MCP server."""
    
    @mcp.tool()
    def tsc_list_ips(
        repository: str | None = None,
        asset_group: str | None = None,
        ip: str | None = None,
        include_details: bool = False,
        # Asset filters
        asset_criticality: str | None = None,
        uuid: str | None = None,
        dns_name: str | None = None,
        # Temporal filters
        first_seen: str | None = None,
        last_seen: str | None = None,
        # Scoring filters (all support operators: >, >=, <, <=, =)
        vpr_score: str | None = None,
        aes_score: str | None = None,
        cvss_v3_base_score: str | None = None,
        cvss_v4_base_score: str | None = None,
        base_cvss_score: str | None = None,
        epss_score: str | None = None,
        # Vulnerability filters
        severity: str | None = None,
        aes_severity: str | None = None,
        exploit_available: str | None = None,
        # Other common filters
        plugin_id: str | None = None,
        family: str | None = None,
        port: int | None = None,
        protocol: str | None = None,
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
            include_details: Return full metadata per IP (DNS, MAC, UUID, ACR, OS)
            
            # Advanced Filters (55+ supported):
            asset_criticality: ACR filter (e.g., ">8", ">=7.5")
            uuid: Asset UUID filter
            dns_name: DNS name filter (hostname)
            first_seen: First seen timestamp (epoch)
            last_seen: Last seen timestamp (epoch)
            vpr_score: VPR score filter (e.g., ">=7.0")
            cvss_v3_base_score: CVSS v3 base score filter
            severity: Vulnerability severity (0-4 or info/low/medium/high/critical)
            exploit_available: Exploit availability (Yes/No)
            plugin_id: Specific plugin ID
            family: Plugin family name
            port: Port number
            protocol: Protocol (TCP/UDP)
            
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
            
            >>> tsc_list_ips(asset_group="Windows Hosts", asset_criticality=">8")
            {"ok": True, "asset_group": "Windows Hosts", "filters_applied": {"asset_criticality": ">8"}, "total_ips": 12, "ips": [...]}
            
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
            filters = []
            
            # Handle repository filter
            if repository:
                # Repository can be name or ID - try both approaches
                if repository.isdigit():
                    # Direct repository ID
                    filters.append({
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
                    filters.append({
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
                filters.append({
                    "filterName": "asset",
                    "operator": "=",
                    "value": {"id": str(asset_group_id), "name": asset_group_name}
                })
            
            # Add additional filters from parameters
            # Note: build_filters() automatically converts scoring filter operators (>, >=, <, <=)
            # to range format required by Tenable.sc API (e.g., ">7" becomes "7.1-10")
            additional_filters = build_filters(
                asset_criticality=asset_criticality,
                uuid=uuid,
                dns_name=dns_name,
                first_seen=first_seen,
                last_seen=last_seen,
                vpr_score=vpr_score,
                aes_score=aes_score,
                cvss_v3_base_score=cvss_v3_base_score,
                cvss_v4_base_score=cvss_v4_base_score,
                base_cvss_score=base_cvss_score,
                epss_score=epss_score,
                severity=severity,
                aes_severity=aes_severity,
                exploit_available=exploit_available,
                plugin_id=plugin_id,
                family=family,
                port=port,
                protocol=protocol,
            )
            filters.extend(additional_filters)
            
            # Build query for sumip analysis tool with proper nested structure
            # Tenable.sc API requires: {"type": "vuln", "query": {...}, "sourceType": "cumulative"}
            query = {
                "type": "vuln",
                "query": {
                    "type": "vuln",
                    "tool": "sumip",
                    "filters": filters
                },
                "sourceType": "cumulative"
            }
            
            # Call tsc_analyze (handles caching)
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
                        "acr_score": item.get("acrScore", "0"),  # Asset Criticality Rating (0-10)
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
            
            # Add filter info if any filters were applied
            filters_applied = {}
            if asset_criticality:
                filters_applied["asset_criticality"] = asset_criticality
            if severity:
                filters_applied["severity"] = severity
            if exploit_available:
                filters_applied["exploit_available"] = exploit_available
            if vpr_score:
                filters_applied["vpr_score"] = vpr_score
            if last_seen:
                filters_applied["last_seen"] = last_seen
            
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


# Export for testing
__all__ = ["register_tools"]
