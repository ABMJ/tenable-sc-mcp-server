"""
Patch management and gap analysis tools for Tenable.sc MCP Server.

Provides universal patch tracking across all operating systems (Windows, Linux, macOS)
with Microsoft KB article tracking and third-party software updates.
"""

from __future__ import annotations

import re
from html import unescape
from typing import Any

from ..cache import generate_cache_key
from ..convenience_tools import build_filters
from ..server import _client, _get_cache


def parse_plugin_66334(text: str) -> dict[str, Any]:
    """
    Parse universal patch report from plugin 66334.
    
    Extracts Microsoft KB articles and third-party software patches from
    HTML-escaped plugin output text.
    
    Args:
        text: Unescaped plugin output text
    
    Returns:
        Dict with microsoft_kbs and third_party lists
    
    Example output format:
        - KB5025279 (85 vulnerabilities)
        [ Google Chrome < 113.0.5672.63 ]
        [ VMware Tools 10.x / 11.x < 12.2.0 ]
    """
    microsoft_kbs = []
    third_party = []
    
    # Extract Microsoft KB patches with optional vulnerability counts
    # Pattern: "- KB12345" or "- KB12345 (42 vulnerabilities)"
    kb_pattern = r'-\s+(KB\d+)(?:\s+\((\d+)\s+(?:vulnerability|vulnerabilities)\))?'
    for match in re.finditer(kb_pattern, text, re.IGNORECASE):
        kb_id = match.group(1)
        vuln_count = int(match.group(2)) if match.group(2) else None
        microsoft_kbs.append({
            "kb_id": kb_id,
            "vulnerability_count": vuln_count
        })
    
    # Extract third-party software updates
    # Pattern: "[ Software Name version info ]"
    software_pattern = r'\[\s*(.+?)\s*\]'
    for match in re.finditer(software_pattern, text):
        software_name = match.group(1).strip()
        # Skip empty brackets
        if software_name:
            third_party.append({
                "software": software_name
            })
    
    return {
        "total_missing_patches": len(microsoft_kbs) + len(third_party),
        "microsoft_kbs": microsoft_kbs,
        "third_party": third_party
    }


def parse_plugin_38153(text: str) -> dict[str, Any]:
    """
    Parse Windows KB summary from plugin 38153.
    
    Extracts KB article numbers and legacy MS bulletin IDs from Windows-specific
    patch report.
    
    Args:
        text: Unescaped plugin output text
    
    Returns:
        Dict with missing_kbs list containing KB IDs and URLs
    
    Example output format:
        - MS16-087 ( http://technet.microsoft.com/... )
        - KB4025252 ( https://support.microsoft.com/... )
    """
    kb_list = []
    
    # Extract KB articles (e.g., KB4025252)
    kb_pattern = r'(KB\d+)'
    seen_kbs = set()  # Deduplicate KB numbers
    for match in re.finditer(kb_pattern, text):
        kb_id = match.group(1)
        if kb_id not in seen_kbs:
            seen_kbs.add(kb_id)
            kb_list.append({
                "kb_id": kb_id,
                "url": f"https://support.microsoft.com/en-us/help/{kb_id[2:]}"  # Remove KB prefix
            })
    
    # Extract legacy MS bulletins (e.g., MS16-087)
    ms_pattern = r'(MS\d{2}-\d+)'
    seen_bulletins = set()
    for match in re.finditer(ms_pattern, text):
        bulletin_id = match.group(1)
        if bulletin_id not in seen_bulletins:
            seen_bulletins.add(bulletin_id)
            kb_list.append({
                "bulletin_id": bulletin_id,
                "type": "legacy_ms_bulletin"
            })
    
    return {
        "total_missing_kbs": len(kb_list),
        "missing_kbs": kb_list
    }


def parse_patch_report(plugin_text: str, plugin_id: str) -> dict[str, Any]:
    """
    Parse patch report from plugin output text.
    
    Dispatcher function that calls the appropriate parser based on plugin ID.
    Handles HTML unescaping and plugin_output tag removal.
    
    Args:
        plugin_text: Raw plugin output (may contain HTML entities)
        plugin_id: Plugin ID ("66334" or "38153")
    
    Returns:
        Parsed patch data structure
    """
    # HTML unescape and remove plugin_output tags
    text = unescape(plugin_text)
    text = re.sub(r'</?plugin_output>', '', text)
    
    if plugin_id == "66334":
        return parse_plugin_66334(text)
    else:  # 38153
        return parse_plugin_38153(text)


def register_tools(mcp):
    """Register patch management tools with the MCP server."""
    
    @mcp.tool()
    def tsc_list_missing_patches(
        mode: str = "universal",
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        List missing patches across all operating systems.
        
        Uses Tenable plugins to detect missing patches and security updates:
        - Plugin 66334 (universal): All OS types + third-party software (Chrome, Office, VMware, etc.)
        - Plugin 38153 (windows): Windows KB-specific summary with legacy MS bulletin support
        
        WHEN TO USE THIS TOOL:
        - User asks "what patches are missing on IP X"
        - User asks "list missing Windows updates"
        - User needs patch gap analysis for compliance (PCI, NIST, CIS)
        - User wants to track Microsoft KB articles or third-party updates
        - User needs remediation planning grouped by IP
        
        DO NOT USE for vulnerability details - use tsc_list_vulns_by_ip_full instead.
        DO NOT USE for single vulnerability queries - use tsc_list_vulns_by_cve instead.
        
        Token Efficiency: ~3,000-5,000 tokens depending on patch count
        Cache TTL: 240s (4 minutes)
        Response Time: <1s cached, 2-5s fresh
        
        Args:
            mode: Patch report mode. Options:
                - "universal" (default): Plugin 66334 - All OS + third-party software
                - "windows": Plugin 38153 - Windows KB articles and MS bulletins only
            filters: Optional dict of filter parameters for narrowing results.
                For complete filter reference, fetch MCP resource: tenable-sc://filters/reference
                
                Common filters:
                    ip: Specific IP address (e.g., "10.1.20.10")
                    repository: Repository name or ID
                    asset_criticality: ACR range (e.g., "7-10", "8-10")
                    severity: critical/high/medium/low/info
                    operating_system: OS name (exact or partial match)
                    dns_name: Hostname filter
                    first_seen: First detection date (epoch timestamp)
                    last_seen: Last detection date (epoch timestamp)
                
                See tenable-sc://filters/reference for all 74+ available filters.
        
        Returns:
            Patch gap analysis grouped by IP with patch details
        
        Examples:
            >>> tsc_list_missing_patches(mode="universal")
            {
                "ok": True,
                "mode": "universal",
                "total_affected_ips": 156,
                "patches_by_ip": [...]
            }
            
            >>> tsc_list_missing_patches(mode="universal", filters={"ip": "10.1.20.10"})
            {
                "ok": True,
                "mode": "universal",
                "total_affected_ips": 1,
                "patches_by_ip": [{
                    "ip": "10.1.20.10",
                    "hostname": "webserver01.domain.com",
                    "os": "Windows Server 2019",
                    "repository": "Production",
                    "total_missing_patches": 45,
                    "microsoft_kbs": [
                        {"kb_id": "KB5025279", "vulnerability_count": 85},
                        {"kb_id": "KB5026361", "vulnerability_count": 12}
                    ],
                    "third_party": [
                        {"software": "Google Chrome < 113.0.5672.63"},
                        {"software": "VMware Tools 10.x / 11.x < 12.2.0"}
                    ]
                }]
            }
            
            >>> tsc_list_missing_patches(mode="windows", filters={"repository": "Default"})
            {
                "ok": True,
                "mode": "windows",
                "total_affected_ips": 89,
                "patches_by_ip": [{
                    "ip": "192.168.5.20",
                    "hostname": "bg520-1.demo.io",
                    "os": "Windows 10",
                    "repository": "Default",
                    "total_missing_kbs": 23,
                    "missing_kbs": [
                        {"kb_id": "KB4025252", "url": "https://support.microsoft.com/..."},
                        {"bulletin_id": "MS16-087", "type": "legacy_ms_bulletin"}
                    ]
                }]
            }
        """
        # Import tsc_analyze from server
        from .. import server
        tsc_analyze = server.tsc_analyze
        
        client = _client()
        cache = _get_cache()
        
        # Validate mode parameter
        if mode not in ["universal", "windows"]:
            return {
                "ok": False,
                "error": f"Invalid mode '{mode}'. Must be 'universal' or 'windows'."
            }
        
        # Select plugin based on mode
        plugin_id = "66334" if mode == "universal" else "38153"
        
        # Parse filters and add plugin ID filter
        filter_dict = filters or {}
        filter_dict["plugin_id"] = plugin_id
        
        # Build filters using centralized helper
        try:
            filter_list, os_names_to_query = build_filters(
                client=client,
                **filter_dict
            )
        except Exception as e:
            return {
                "ok": False,
                "error": f"Filter validation failed: {str(e)}"
            }
        
        # Generate cache key (excludes pagination params)
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
        
        try:
            # Execute query
            response = tsc_analyze(query)
        except Exception as e:
            return {
                "ok": False,
                "error": f"Tenable.sc API query failed: {str(e)}"
            }
        
        # Check if API call succeeded
        if not response.get("ok"):
            return {
                "ok": False,
                "error": f"Tenable.sc API returned error: {response.get('error', 'Unknown error')}",
                "details": response
            }
        
        # Parse plugin text for each result
        # tsc_analyze returns {"ok": True, "response": {"results": [...]}}
        patches_by_ip = []
        api_response = response.get("response", {})
        for result in api_response.get("results", []):
            plugin_text = result.get("pluginText", "")
            
            # Skip empty plugin text
            if not plugin_text or plugin_text.strip() == "":
                continue
            
            try:
                parsed = parse_patch_report(plugin_text, plugin_id)
            except Exception as e:
                # Log parsing error but continue processing other IPs
                parsed = {
                    "parse_error": f"Failed to parse plugin output: {str(e)}"
                }
            
            patches_by_ip.append({
                "ip": result.get("ip"),
                "hostname": result.get("dnsName", ""),
                "os": result.get("operatingSystem", ""),
                "repository": result.get("repository", {}).get("name", ""),
                **parsed
            })
        
        result = {
            "ok": True,
            "mode": mode,
            "plugin_id": plugin_id,
            "total_affected_ips": len(patches_by_ip),
            "patches_by_ip": patches_by_ip,
        }
        
        # Cache result
        if cache:
            cache.set(cache_key, result, ttl_seconds=240)
        
        return result
