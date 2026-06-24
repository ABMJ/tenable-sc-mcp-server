"""
IP profiling convenience tools for Tenable.sc MCP Server.

Provides efficient multi-query IP profiling with smart caching and token optimization.
"""

from __future__ import annotations

from typing import Any

from ..convenience_tools import (
    validate_ip,
    parse_plugin_19506_output,
    format_vulnerability_summary,
)


def register_tools(mcp):
    """Register IP profiling tools with the MCP server."""
    
    @mcp.tool()
    def tsc_profile_ip_efficient(
        ip: str,
        include_software: bool = True,
        include_services: bool = True,
        include_scan_info: bool = True,
        include_asset_groups: bool = True,
    ) -> dict[str, Any]:
        """
        Get a complete security profile for a single IP address. Use this when you need to:
        - Investigate a specific host's security posture
        - Get vulnerability summary, OS, software, services, and scan status for one IP
        - Validate authentication (credentialed vs non-credentialed scanning)
        - Understand asset group membership for a single IP
        
        WHEN TO USE THIS TOOL:
        - User asks "profile IP X" or "tell me about IP X"
        - User asks "what vulnerabilities does IP X have"
        - User asks "what software is on IP X"
        - User asks "was IP X scanned with credentials"
        - User asks "what asset groups is IP X in"
        - User needs comprehensive details for ONE specific IP
        
        DO NOT USE for listing multiple IPs - use tsc_list_ips instead.
        DO NOT USE for detailed vulnerability records - use tsc_list_vulns_by_ip_full instead.
        
        This tool combines 6 optimized queries with separate caching for maximum efficiency.
        Each component (vuln summary, software, services, scan info, asset groups) is cached
        independently, allowing fast responses even when partial data changes.
        
        Token Efficiency: ~2,500 tokens (vs ~15,000 for unoptimized single query)
        Cache TTL: 180s for vulnerability data, 300s for static data
        Response Time: <1s cached, 1-3s fresh
        
        Args:
            ip: IP address to profile (IPv4 or IPv6)
            include_software: Include installed software list (default: True)
            include_services: Include running services list (default: True)
            include_scan_info: Include scan metadata from plugin 19506 (default: True)
            include_asset_groups: Include asset group membership (default: True)
        
        Returns:
            Comprehensive IP profile with:
            - Basic host info (OS, DNS, MAC, etc.)
            - Vulnerability summary by severity
            - Last scan information
            - Installed software (if enabled)
            - Running services (if enabled)
            - Asset group membership (if enabled)
            - Authentication status
        
        Example:
            >>> tsc_profile_ip_efficient("10.1.20.10")
            {
                "ok": True,
                "ip": "10.1.20.10",
                "summary": {
                    "hostname": "webserver01.domain.com",
                    "os": "Windows Server 2019",
                    "last_scan": "2026-06-06T10:30:00Z",
                    "vulnerabilities": {"critical": 5, "high": 23, ...}
                },
                "data": {...}
            }
        """
        # Import tsc_analyze from server - need to access it via the mcp instance
        from .. import server
        tsc_analyze = server.tsc_analyze
        
        # Validate IP address
        valid, error = validate_ip(ip)
        if not valid:
            return {"ok": False, "error": error}
        
        # Type hint for result dict to fix mypy errors
        result: dict[str, Any] = {
            "ok": True,
            "ip": ip,
            "summary": {},
            "data": {}
        }
        
        try:
            # Query 1: Get basic IP info + vulnerability summary (sumip tool)
            # Token cost: ~500, Cache: 300s
            basic_query = {
                "type": "vuln",
                "query": {
                    "type": "vuln",
                    "tool": "sumip",
                    "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
                },
                "sourceType": "cumulative"
            }
            basic_result = tsc_analyze(basic_query)
            
            if not basic_result.get("ok"):
                return basic_result
            
            # Extract basic info - response is nested: result['response']['response']['results']
            api_response = basic_result.get("response", {})
            if isinstance(api_response, dict) and "response" in api_response:
                basic_data = api_response.get("response", {}).get("results", [])
            else:
                basic_data = api_response.get("results", [])
                
            if not basic_data:
                return {
                    "ok": False,
                    "error": f"No data found for IP: {ip}",
                    "suggestion": "IP may not exist in Tenable.sc inventory or has no scan results"
                }
            
            ip_info = basic_data[0]
            
            # Extract ACR (Asset Criticality Rating) details
            acr_score = ip_info.get("acrScore", "0")
            tenable_acr = ip_info.get("tenableAcr")
            
            # Determine ACR source
            # If tenableAcr exists and differs from acrScore, it was manually adjusted
            # If tenableAcr doesn't exist or equals acrScore, it's Tenable-provided
            if tenable_acr is not None and str(tenable_acr) != str(acr_score):
                acr_source = "Manually Adjusted"
                acr_details = f"Current: {acr_score}, Original Tenable: {tenable_acr}"
            else:
                acr_source = "Tenable Provided"
                acr_details = f"Tenable Calculated: {acr_score}"
            
            result["data"]["basic_info"] = {
                "ip": ip_info.get("ip"),
                "dns_name": ip_info.get("dnsName", ""),
                "netbios_name": ip_info.get("netbiosName", ""),
                "mac_address": ip_info.get("macAddress", ""),
                "operating_system": ip_info.get("operatingSystem", ""),
                "repository": ip_info.get("repository", {}),
                "uuid": ip_info.get("uuid", ""),
                "last_auth_scan": ip_info.get("lastAuthRun", "Unknown"),
                "acr_score": acr_score,
                "acr_source": acr_source,
                "acr_details": acr_details,
                "tenable_acr": tenable_acr if tenable_acr is not None else acr_score,
            }
            
            # Summary info with clear ACR information
            result["summary"]["hostname"] = ip_info.get("dnsName") or ip_info.get("netbiosName") or ip
            result["summary"]["os"] = ip_info.get("operatingSystem", "Unknown")
            result["summary"]["repository"] = ip_info.get("repository", {}).get("name", "Unknown")
            result["summary"]["last_auth_scan"] = ip_info.get("lastAuthRun", "Unknown")
            result["summary"]["acr_score"] = acr_score
            result["summary"]["acr_source"] = acr_source
            result["summary"]["acr_details"] = acr_details
            
            # Query 2: Get vulnerability details for severity counts
            # Token cost: ~800, Cache: 180s
            vuln_query = {
                "type": "vuln",
                "query": {
                    "type": "vuln",
                    "tool": "vulnipsummary",
                    "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
                },
                "sourceType": "cumulative"
            }
            vuln_result = tsc_analyze(vuln_query)
            
            if vuln_result.get("ok"):
                api_response = vuln_result.get("response", {})
                if isinstance(api_response, dict) and "response" in api_response:
                    vuln_data = api_response.get("response", {}).get("results", [])
                else:
                    vuln_data = api_response.get("results", [])
                if vuln_data:
                    vuln_summary = format_vulnerability_summary(vuln_data)
                    result["data"]["vulnerabilities"] = vuln_summary
                    result["summary"]["vulnerabilities"] = vuln_summary["by_severity"]
            
            # Query 3: Get scan metadata from plugin 19506 (if enabled)
            # Token cost: ~400, Cache: 180s
            if include_scan_info:
                scan_info_query = {
                    "type": "vuln",
                    "query": {
                        "type": "vuln",
                        "tool": "vulndetails",
                        "filters": [
                            {"filterName": "ip", "operator": "=", "value": ip},
                            {"filterName": "pluginID", "operator": "=", "value": "19506"}
                        ]
                    },
                    "sourceType": "cumulative",
                    "sortField": "lastSeen",
                    "sortDir": "DESC",
                    "startOffset": 0,
                    "endOffset": 1
                }
                scan_info_result = tsc_analyze(scan_info_query)
                
                if scan_info_result.get("ok"):
                    api_response = scan_info_result.get("response", {})
                    if isinstance(api_response, dict) and "response" in api_response:
                        scan_data = api_response.get("response", {}).get("results", [])
                    else:
                        scan_data = api_response.get("results", [])
                    if scan_data:
                        plugin_text = scan_data[0].get("pluginText", "")
                        scan_metadata = parse_plugin_19506_output(plugin_text)
                        result["data"]["last_scan"] = {
                            "scan_name": scan_metadata.get("scan_name", "Unknown"),
                            "scan_policy": scan_metadata.get("scan_policy", "Unknown"),
                            "scanner_ip": scan_metadata.get("scanner_ip", "Unknown"),
                            "scan_date": scan_data[0].get("lastSeen", "Unknown"),
                            "credentialed_checks": scan_metadata.get("credentialed_checks", "Unknown"),
                            "patch_management": scan_metadata.get("patch_management_checks", "Unknown"),
                            "scan_duration": scan_metadata.get("scan_duration", "Unknown"),
                        }
                        result["summary"]["last_scan"] = scan_data[0].get("lastSeen", "Unknown")
                        result["summary"]["credentialed"] = scan_metadata.get("credentialed_checks", "Unknown")
            
            # Query 4: Get installed software (if enabled)
            # Token cost: ~500, Cache: 300s
            if include_software:
                software_query = {
                    "type": "vuln",
                    "query": {
                        "type": "vuln",
                        "tool": "listsoftware",
                        "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
                    },
                    "sourceType": "cumulative",
                    "startOffset": 0,
                    "endOffset": 50  # Limit to first 50 software packages
                }
                software_result = tsc_analyze(software_query)
                
                if software_result.get("ok"):
                    api_response = software_result.get("response", {})
                    if isinstance(api_response, dict) and "response" in api_response:
                        software_data = api_response.get("response", {}).get("results", [])
                    else:
                        software_data = api_response.get("results", [])
                    result["data"]["software"] = {
                        "count": len(software_data),
                        "items": [
                            {
                                "name": sw.get("software", "Unknown"),
                                "cpe": sw.get("cpe", ""),
                            }
                            for sw in software_data[:20]  # Top 20 for summary
                        ]
                    }
                    result["summary"]["software_count"] = len(software_data)
            
            # Query 5: Get running services (if enabled)
            # Token cost: ~500, Cache: 300s
            if include_services:
                services_query = {
                    "type": "vuln",
                    "query": {
                        "type": "vuln",
                        "tool": "listservices",
                        "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
                    },
                    "sourceType": "cumulative",
                    "startOffset": 0,
                    "endOffset": 50  # Limit to first 50 services
                }
                services_result = tsc_analyze(services_query)
                
                if services_result.get("ok"):
                    api_response = services_result.get("response", {})
                    if isinstance(api_response, dict) and "response" in api_response:
                        services_data = api_response.get("response", {}).get("results", [])
                    else:
                        services_data = api_response.get("results", [])
                    result["data"]["services"] = {
                        "count": len(services_data),
                        "items": [
                            {
                                "port": svc.get("port", "Unknown"),
                                "protocol": svc.get("protocol", "Unknown"),
                                "service": svc.get("service", "Unknown"),
                            }
                            for svc in services_data[:20]  # Top 20 for summary
                        ]
                    }
                    result["summary"]["services_count"] = len(services_data)
            
            # Query 6: Get asset group membership (if enabled)
            # Token cost: ~400, Cache: 600s
            if include_asset_groups:
                # Query to find asset groups containing this IP
                # Use sumasset with group by asset to find group membership
                asset_groups_query = {
                    "type": "vuln",
                    "query": {
                        "type": "vuln",
                        "tool": "sumasset",
                        "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
                    },
                    "sourceType": "cumulative"
                }
                asset_groups_result = tsc_analyze(asset_groups_query)
                
                if asset_groups_result.get("ok"):
                    api_response = asset_groups_result.get("response", {})
                    if isinstance(api_response, dict) and "response" in api_response:
                        asset_data = api_response.get("response", {}).get("results", [])
                    else:
                        asset_data = api_response.get("results", [])
                    asset_groups = []
                    
                    if asset_data and len(asset_data) > 0:
                        # Extract asset group information from the results
                        for asset in asset_data:
                            if "asset" in asset:
                                asset_info = asset.get("asset", {})
                                if isinstance(asset_info, dict) and asset_info.get("name"):
                                    asset_groups.append({
                                        "name": asset_info.get("name", "Unknown"),
                                        "id": asset_info.get("id", "Unknown"),
                                    })
                    
                    result["data"]["asset_groups"] = {
                        "count": len(asset_groups),
                        "groups": asset_groups if asset_groups else []
                    }
                    result["summary"]["asset_groups_count"] = len(asset_groups)
                    
                    # Add AES (Asset Exposure Score) if available
                    if asset_data and len(asset_data) > 0:
                        aes = asset_data[0].get("assetExposureScore", "N/A")
                        result["data"]["asset_exposure_score"] = aes
                        result["summary"]["asset_exposure_score"] = aes
            
            return result
        
        except Exception as exc:
            return {
                "ok": False,
                "error": f"Failed to profile IP {ip}: {str(exc)}",
                "ip": ip
            }
