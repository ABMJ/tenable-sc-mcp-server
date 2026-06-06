from __future__ import annotations

import argparse
import base64
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .catalog import API_RESOURCES, RESOURCE_BY_PATH, catalog_as_dict
from .client import TenableScApiError, TenableScClient, TenableScConfigError, TenableScConfig
from .cache import (
    Cache,
    InMemoryCache,
    RedisCache,
    generate_cache_key,
    get_ttl_for_resource,
    get_ttl_for_analysis,
    initialize_cache,
    get_cache,
)
from .convenience_tools import (
    validate_ip,
    validate_severity,
    build_filters,
    parse_plugin_19506_output,
    format_vulnerability_summary,
    AUTH_PLUGINS,
)


_CLIENT_ENV_PREFIX = "TSC_"
_CLIENT_ENV_FILE: str | None = None
_CACHE: Cache | None = None

mcp = FastMCP(
    "tenable-sc-mcp",
    instructions=(
        "Direct MCP interface for Tenable Security Center Plus. "
        "All Tenable.sc permissions are enforced by the configured API keys. "
        "Use tsc_catalog to discover documented resources and tsc_request for endpoint-specific actions."
    ),
)


def _client() -> TenableScClient:
    return TenableScClient(env_prefix=_CLIENT_ENV_PREFIX, env_file=_CLIENT_ENV_FILE)


def _get_cache() -> Cache | None:
    """Get cache instance if enabled."""
    return _CACHE


def _init_cache() -> None:
    """Initialize cache based on configuration."""
    global _CACHE
    
    config = TenableScConfig.from_env(env_prefix=_CLIENT_ENV_PREFIX, env_file=_CLIENT_ENV_FILE)
    
    if not config.cache_enabled:
        _CACHE = None
        return
    
    if config.cache_backend == "redis":
        try:
            backend = RedisCache(
                host=config.cache_redis_host,
                port=config.cache_redis_port,
                db=config.cache_redis_db,
                password=config.cache_redis_password,
            )
            _CACHE = initialize_cache(backend)
            print(f"Cache initialized: Redis ({config.cache_redis_host}:{config.cache_redis_port})")
        except Exception as e:
            print(f"Failed to initialize Redis cache: {e}")
            print("Falling back to in-memory cache")
            _CACHE = initialize_cache(InMemoryCache())
    else:
        _CACHE = initialize_cache(InMemoryCache())
        print("Cache initialized: In-Memory")


def configure_client_env(*, env_prefix: str, env_file: str | None) -> None:
    global _CLIENT_ENV_PREFIX
    global _CLIENT_ENV_FILE
    _CLIENT_ENV_PREFIX = env_prefix
    _CLIENT_ENV_FILE = env_file
    # Reinitialize cache with new config
    _init_cache()


def _query_params(
    params: dict[str, Any] | None = None,
    fields: list[str] | None = None,
    expand: list[str] | None = None,
    editable: bool = False,
) -> dict[str, Any]:
    merged: dict[str, Any] = dict(params or {})
    if fields:
        merged["fields"] = ",".join(fields)
    if expand:
        merged["expand"] = ",".join(expand)
    if editable:
        merged["editable"] = ""
    return merged


def _handle_error(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, TenableScApiError):
        return {"ok": False, "status_code": exc.status_code, "error": str(exc), "response": exc.response}
    if isinstance(exc, TenableScConfigError):
        return {"ok": False, "error": str(exc), "configuration_error": True}
    return {"ok": False, "error": str(exc)}


def _select_response_path(value: Any, path: str) -> Any:
    current: Any = value
    for part in path.split("."):
        part = part.strip()
        if not part:
            continue
        if isinstance(current, dict):
            if part not in current:
                raise KeyError(part)
            current = current[part]
            continue
        if isinstance(current, list):
            index = int(part)
            current = current[index]
            continue
        raise KeyError(part)
    return current


@mcp.tool()
def tsc_catalog(
    include_admin_or_director: bool = True,
    query: str | None = None,
    limit: int | None = None,
    compact: bool = True,
) -> dict[str, Any]:
    """Returns Tenable.sc resource catalog; supports filtering and compact output."""
    # Check cache first
    cache = _get_cache()
    if cache:
        cache_key = generate_cache_key(
            "catalog",
            params={
                "include_admin_or_director": include_admin_or_director,
                "query": query,
                "limit": limit,
                "compact": compact,
            },
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    
    # Generate result
    resources = catalog_as_dict()
    if not include_admin_or_director:
        resources = [resource for resource in resources if not resource["admin_or_director"]]
    if query:
        q = query.lower()
        resources = [
            resource
            for resource in resources
            if q in str(resource["name"]).lower() or q in str(resource["path"]).lower()
        ]
    if limit is not None:
        resources = resources[: max(limit, 0)]
    if compact:
        resources = [{"name": resource["name"], "path": resource["path"]} for resource in resources]
    
    result = {"ok": True, "count": len(resources), "resources": resources}
    
    # Cache result (24 hours for catalog)
    if cache:
        cache.set(cache_key, result, get_ttl_for_resource("catalog"))
    
    return result


@mcp.tool()
def tsc_request(
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"],
    path: str,
    params: dict[str, Any] | None = None,
    body: Any | None = None,
    fields: list[str] | None = None,
    expand: list[str] | None = None,
    editable: bool = False,
    timeout_seconds: float | None = None,
    response_path: str | None = None,
    max_items: int | None = None,
    keys_only: list[str] | None = None,
) -> dict[str, Any]:
    """Calls any Tenable.sc endpoint; use as advanced escape hatch."""
    # Check cache for GET requests
    cache = _get_cache()
    cache_key = None
    if cache and method == "GET":
        # Extract resource name from path
        resource_name = path.strip("/").split("/")[0]
        cache_key = generate_cache_key(
            resource_name,
            object_id=None,
            params={
                "path": path,
                "params": params,
                "fields": fields,
                "expand": expand,
                "editable": editable,
                "response_path": response_path,
                "max_items": max_items,
                "keys_only": keys_only,
            },
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    
    try:
        response = _client().request(
            method,
            path,
            params=_query_params(params, fields, expand, editable),
            json_body=body,
            timeout_seconds=timeout_seconds,
        )
        if response_path:
            try:
                response = _select_response_path(response, response_path)
            except (KeyError, IndexError, ValueError) as exc:
                return {"ok": False, "error": f"invalid response_path: {response_path}", "details": str(exc)}
        if max_items is not None and isinstance(response, list):
            response = response[: max(max_items, 0)]
        if keys_only and isinstance(response, dict):
            response = {key: response[key] for key in keys_only if key in response}
        if keys_only and isinstance(response, list):
            response = [
                {key: item[key] for key in keys_only if isinstance(item, dict) and key in item}
                for item in response
            ]
        
        result = {"ok": True, "response": response}
        
        # Cache GET requests
        if cache and method == "GET" and cache_key:
            resource_name = path.strip("/").split("/")[0]
            ttl = get_ttl_for_resource(resource_name)
            cache.set(cache_key, result, ttl)
        
        # Invalidate cache on write operations
        if cache and method in ("POST", "PUT", "PATCH", "DELETE"):
            resource_name = path.strip("/").split("/")[0]
            cache.delete_pattern(resource_name)
        
        return result
    except Exception as exc:
        return _handle_error(exc)


@mcp.tool()
def tsc_resource_action(
    action: Literal["list", "get", "create", "update", "delete"],
    resource: str,
    object_id: str | None = None,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    fields: list[str] | None = None,
    expand: list[str] | None = None,
    editable: bool = False,
) -> dict[str, Any]:
    """Performs CRUD-like actions on a Tenable.sc resource path."""
    if action == "list":
        return tsc_request("GET", f"/{resource}", params=params, fields=fields, expand=expand, editable=editable)
    if action == "get":
        if not object_id:
            return {"ok": False, "error": "object_id is required for action=get"}
        return tsc_request(
            "GET",
            f"/{resource}/{object_id}",
            params=params,
            fields=fields,
            expand=expand,
            editable=editable,
        )
    if action == "create":
        if body is None:
            return {"ok": False, "error": "body is required for action=create"}
        return tsc_request("POST", f"/{resource}", body=body)
    if action == "update":
        if not object_id:
            return {"ok": False, "error": "object_id is required for action=update"}
        if body is None:
            return {"ok": False, "error": "body is required for action=update"}
        return tsc_request("PUT", f"/{resource}/{object_id}", body=body)
    if not object_id:
        return {"ok": False, "error": "object_id is required for action=delete"}
    return tsc_request("DELETE", f"/{resource}/{object_id}")


@mcp.tool()
def tsc_list(
    resource: str,
    params: dict[str, Any] | None = None,
    fields: list[str] | None = None,
    expand: list[str] | None = None,
    editable: bool = False,
) -> dict[str, Any]:
    """Deprecated alias for tsc_resource_action(action='list')."""
    return tsc_resource_action(
        "list",
        resource,
        params=params,
        fields=fields,
        expand=expand,
        editable=editable,
    )


@mcp.tool()
def tsc_get(
    resource: str,
    object_id: str,
    params: dict[str, Any] | None = None,
    fields: list[str] | None = None,
    expand: list[str] | None = None,
    editable: bool = False,
) -> dict[str, Any]:
    """Deprecated alias for tsc_resource_action(action='get')."""
    return tsc_resource_action(
        "get",
        resource,
        object_id=object_id,
        params=params,
        fields=fields,
        expand=expand,
        editable=editable,
    )


@mcp.tool()
def tsc_create(resource: str, body: dict[str, Any]) -> dict[str, Any]:
    """Deprecated alias for tsc_resource_action(action='create')."""
    return tsc_resource_action("create", resource, body=body)


@mcp.tool()
def tsc_update(resource: str, object_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Deprecated alias for tsc_resource_action(action='update')."""
    return tsc_resource_action("update", resource, object_id=object_id, body=body)


@mcp.tool()
def tsc_delete(resource: str, object_id: str) -> dict[str, Any]:
    """Deprecated alias for tsc_resource_action(action='delete')."""
    return tsc_resource_action("delete", resource, object_id=object_id)


@mcp.tool()
def tsc_current_user() -> dict[str, Any]:
    """Returns the current Tenable.sc API user details."""
    return tsc_request("GET", "/currentUser")


@mcp.tool()
def tsc_resource_docs(resource: str, compact: bool = False) -> dict[str, Any]:
    """Returns docs metadata for one Tenable.sc resource path."""
    item = RESOURCE_BY_PATH.get(resource)
    if not item:
        matches = [entry for entry in catalog_as_dict() if resource.lower() in str(entry["name"]).lower()]
        return {"ok": False, "error": f"Unknown resource: {resource}", "possible_matches": matches}
    if compact:
        return {"ok": True, "resource": {"name": item.name, "path": item.path, "docs": item.docs}}
    return {
        "ok": True,
        "resource": {
            "name": item.name,
            "path": item.path,
            "rest_path": f"/rest/{item.path}",
            "docs": item.docs,
            "description": item.description,
            "admin_or_director": item.admin_or_director,
        },
    }


@mcp.tool()
def tsc_analyze(
    query: dict[str, Any],
    fields: list[str] | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    """Runs a Tenable.sc analysis query via POST /analysis.
    
    Analysis queries are read-only operations that use POST for complex query parameters.
    They are cached to improve performance and reduce token usage.
    """
    # Check cache first (analysis queries are read-only despite using POST)
    cache = _get_cache()
    cache_key = None
    if cache:
        # Generate deterministic cache key from query body
        cache_key = generate_cache_key(
            "analysis",
            params={
                "query": query,  # Cache handles JSON serialization with sort_keys=True
                "fields": fields,
            },
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    
    # Call API if not cached
    result = tsc_request("POST", "/analysis", body=query, fields=fields, timeout_seconds=timeout_seconds)
    
    # Cache successful responses with smart TTL based on query type
    if cache and cache_key and result.get("ok"):
        ttl = get_ttl_for_analysis(query)
        cache.set(cache_key, result, ttl)
    
    return result


@mcp.tool()
def tsc_download(
    path: str,
    method: Literal["GET", "POST"] = "GET",
    params: dict[str, Any] | None = None,
    body: Any | None = None,
    timeout_seconds: float | None = None,
    max_bytes: int = 10_000_000,
) -> dict[str, Any]:
    """Downloads binary/text content and returns base64 payload."""
    try:
        response = _client().download(
            method,
            path,
            params=params,
            json_body=body,
            timeout_seconds=timeout_seconds,
        )
        content = response.content
        if len(content) > max_bytes:
            return {
                "ok": False,
                "error": f"download response is {len(content)} bytes, larger than max_bytes={max_bytes}",
                "content_type": response.headers.get("content-type", ""),
            }
        return {
            "ok": True,
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type", ""),
            "content_disposition": response.headers.get("content-disposition", ""),
            "bytes": len(content),
            "content_base64": base64.b64encode(content).decode("ascii"),
        }
    except Exception as exc:
        return _handle_error(exc)


@mcp.tool()
def tsc_upload_file(
    file_path: str,
    return_content: bool = False,
    context: Literal["auditfile", "tailoringfile"] | None = None,
    max_file_size: int | None = None,
    timeout_seconds: float | None = None,
) -> dict[str, Any]:
    """Uploads a local file to Tenable.sc via /file/upload."""
    try:
        response = _client().upload_file(
            file_path,
            return_content=return_content,
            context=context,
            max_file_size=max_file_size,
            timeout_seconds=timeout_seconds,
        )
        return {"ok": True, "response": response}
    except Exception as exc:
        return _handle_error(exc)


@mcp.tool()
def tsc_cache_stats() -> dict[str, Any]:
    """Returns cache performance metrics and statistics."""
    cache = _get_cache()
    if not cache:
        return {"ok": True, "enabled": False, "message": "Cache is disabled"}
    
    metrics = cache.metrics.to_dict()
    return {
        "ok": True,
        "enabled": True,
        "backend": "redis" if isinstance(cache.backend, RedisCache) else "memory",
        "key_count": cache.key_count(),
        "metrics": metrics,
    }


@mcp.tool()
def tsc_cache_clear(pattern: str | None = None) -> dict[str, Any]:
    """Clear cache entries matching pattern or all entries.
    
    Args:
        pattern: Pattern to match (e.g., 'scan:*' or 'repository'). 
                 If None, clears all cache.
    
    Returns:
        Status and number of keys deleted
    
    Examples:
        Clear all plugins: pattern="plugin"
        Clear specific scan: pattern="scan:10"
        Clear everything: pattern=None
    """
    cache = _get_cache()
    if not cache:
        return {"ok": True, "enabled": False, "message": "Cache is disabled"}
    
    if pattern:
        deleted = cache.delete_pattern(pattern)
        return {
            "ok": True,
            "action": "pattern_clear",
            "pattern": pattern,
            "keys_deleted": deleted,
        }
    else:
        cache.clear()
        return {
            "ok": True,
            "action": "clear_all",
            "message": "All cache entries cleared",
        }


# ============================================================================
# CONVENIENCE TOOLS - Week 1 Implementation
# ============================================================================


@mcp.tool()
def tsc_profile_ip_efficient(
    ip: str,
    include_software: bool = True,
    include_services: bool = True,
    include_scan_info: bool = True,
    include_asset_groups: bool = True,
) -> dict[str, Any]:
    """
    Get comprehensive IP profile using efficient multi-query approach.
    
    This tool provides a complete security profile for an IP address by combining
    data from multiple optimized queries. Each component is cached separately for
    maximum cache hit rates.
    
    Token Efficiency: ~2,500 tokens (vs ~15,000 for single comprehensive query)
    Cache TTL: 180s (3 minutes) for vulnerability data
    
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
    # Validate IP address
    valid, error = validate_ip(ip)
    if not valid:
        return {"ok": False, "error": error}
    
    result = {
        "ok": True,
        "ip": ip,
        "summary": {},
        "data": {}
    }
    
    try:
        # Query 1: Get basic IP info + vulnerability summary (sumip tool)
        # Token cost: ~500, Cache: 300s
        basic_query = {
            "tool": "sumip",
            "type": "vuln",
            "sourceType": "cumulative",
            "query": {
                "tool": "sumip",
                "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
            }
        }
        basic_result = tsc_analyze(basic_query)
        
        if not basic_result.get("ok"):
            return basic_result
        
        # Extract basic info
        basic_data = basic_result.get("response", {}).get("results", [])
        if not basic_data:
            return {
                "ok": False,
                "error": f"No data found for IP: {ip}",
                "suggestion": "IP may not exist in Tenable.sc inventory or has no scan results"
            }
        
        ip_info = basic_data[0]
        result["data"]["basic_info"] = {
            "ip": ip_info.get("ip"),
            "dns_name": ip_info.get("dnsName", ""),
            "netbios_name": ip_info.get("netbiosName", ""),
            "mac_address": ip_info.get("macAddress", ""),
            "operating_system": ip_info.get("operatingSystem", ""),
            "repository": ip_info.get("repository", {}),
            "uuid": ip_info.get("uuid", ""),
        }
        
        # Summary info
        result["summary"]["hostname"] = ip_info.get("dnsName") or ip_info.get("netbiosName") or ip
        result["summary"]["os"] = ip_info.get("operatingSystem", "Unknown")
        result["summary"]["repository"] = ip_info.get("repository", {}).get("name", "Unknown")
        
        # Query 2: Get vulnerability details for severity counts
        # Token cost: ~800, Cache: 180s
        vuln_query = {
            "tool": "vulnipsummary",
            "type": "vuln",
            "sourceType": "cumulative",
            "query": {
                "tool": "vulnipsummary",
                "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
            }
        }
        vuln_result = tsc_analyze(vuln_query)
        
        if vuln_result.get("ok"):
            vuln_data = vuln_result.get("response", {}).get("results", [])
            if vuln_data:
                vuln_summary = format_vulnerability_summary(vuln_data)
                result["data"]["vulnerabilities"] = vuln_summary
                result["summary"]["vulnerabilities"] = vuln_summary["by_severity"]
        
        # Query 3: Get scan metadata from plugin 19506 (if enabled)
        # Token cost: ~400, Cache: 180s
        if include_scan_info:
            scan_info_query = {
                "tool": "vulndetails",
                "type": "vuln",
                "sourceType": "cumulative",
                "query": {
                    "tool": "vulndetails",
                    "filters": [
                        {"filterName": "ip", "operator": "=", "value": ip},
                        {"filterName": "pluginID", "operator": "=", "value": "19506"}
                    ]
                },
                "sortField": "lastSeen",
                "sortDir": "DESC",
                "startOffset": 0,
                "endOffset": 1
            }
            scan_info_result = tsc_analyze(scan_info_query)
            
            if scan_info_result.get("ok"):
                scan_data = scan_info_result.get("response", {}).get("results", [])
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
                "tool": "listsoftware",
                "type": "vuln",
                "sourceType": "cumulative",
                "query": {
                    "tool": "listsoftware",
                    "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
                },
                "startOffset": 0,
                "endOffset": 50  # Limit to first 50 software packages
            }
            software_result = tsc_analyze(software_query)
            
            if software_result.get("ok"):
                software_data = software_result.get("response", {}).get("results", [])
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
                "tool": "listservices",
                "type": "vuln",
                "sourceType": "cumulative",
                "query": {
                    "tool": "listservices",
                    "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
                },
                "startOffset": 0,
                "endOffset": 50  # Limit to first 50 services
            }
            services_result = tsc_analyze(services_query)
            
            if services_result.get("ok"):
                services_data = services_result.get("response", {}).get("results", [])
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
        # Token cost: ~300, Cache: 600s
        if include_asset_groups:
            # Query via asset resource to find which asset groups contain this IP
            asset_query = {
                "tool": "sumasset",
                "type": "vuln",
                "sourceType": "cumulative",
                "query": {
                    "tool": "sumasset",
                    "filters": [{"filterName": "ip", "operator": "=", "value": ip}]
                }
            }
            asset_result = tsc_analyze(asset_query)
            
            if asset_result.get("ok"):
                asset_data = asset_result.get("response", {}).get("results", [])
                if asset_data:
                    # Note: Asset group membership may require additional query
                    # For now, return asset criticality rating if available
                    acr_score = ip_info.get("acrScore", "N/A")
                    result["data"]["asset_info"] = {
                        "acr_score": acr_score,
                        "asset_exposure_score": ip_info.get("assetExposureScore", "N/A"),
                    }
                    result["summary"]["acr_score"] = acr_score
        
        return result
    
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed to profile IP {ip}: {str(exc)}",
            "ip": ip
        }


@mcp.tool()
def tsc_list_vulns_by_ip_summary(
    ip: str,
    # Top 10 common filters
    severity: str | None = None,
    exploit_available: str | None = None,
    first_seen: str | None = None,
    last_seen: str | None = None,
    family: str | None = None,
    vpr_score: str | None = None,
    plugin_id: str | None = None,
    cve: str | None = None,
    port: int | None = None,
    protocol: str | None = None,
) -> dict[str, Any]:
    """
    Get vulnerability summary (counts by severity) for an IP address.
    
    Returns aggregated vulnerability counts without detailed records.
    Use this for quick overview and dashboards.
    
    Token Efficiency: ~700 tokens (vs ~6,000 for full details)
    Cache TTL: 180s (3 minutes)
    
    Args:
        ip: IP address to query (required)
        severity: Filter by severity (0-4 or info/low/medium/high/critical)
        exploit_available: Filter by exploit availability (Yes/No)
        first_seen: Filter by first seen date (epoch timestamp)
        last_seen: Filter by last seen date (epoch timestamp)
        family: Filter by plugin family name
        vpr_score: Filter by VPR score (e.g., "7.0" or ">=7.0")
        plugin_id: Filter by specific plugin ID
        cve: Filter by CVE ID
        port: Filter by port number
        protocol: Filter by protocol (TCP/UDP)
    
    Returns:
        Summary with vulnerability counts by severity
    
    Example:
        >>> tsc_list_vulns_by_ip_summary("10.1.20.10", severity="critical")
        {
            "ok": True,
            "ip": "10.1.20.10",
            "summary": {
                "total": 183,
                "by_severity": {
                    "critical": 15,
                    "high": 45,
                    "medium": 123,
                    "low": 0,
                    "info": 0
                }
            }
        }
    """
    # Validate IP
    valid, error = validate_ip(ip)
    if not valid:
        return {"ok": False, "error": error}
    
    # Validate severity if provided
    if severity:
        valid, error = validate_severity(severity)
        if not valid:
            return {"ok": False, "error": error}
    
    try:
        # Build filters from parameters
        filters = build_filters(
            ip=ip,
            severity=severity,
            exploit_available=exploit_available,
            first_seen=first_seen,
            last_seen=last_seen,
            family=family,
            vpr_score=vpr_score,
            plugin_id=plugin_id,
            cve=cve,
            port=port,
            protocol=protocol,
        )
        
        # Query using vulnipsummary tool (efficient aggregation)
        query = {
            "tool": "vulnipsummary",
            "type": "vuln",
            "sourceType": "cumulative",
            "query": {
                "tool": "vulnipsummary",
                "filters": filters
            }
        }
        
        result = tsc_analyze(query)
        
        if not result.get("ok"):
            return result
        
        # Format summary
        vuln_data = result.get("response", {}).get("results", [])
        summary = format_vulnerability_summary(vuln_data)
        
        return {
            "ok": True,
            "ip": ip,
            "summary": summary,
            "filters_applied": {
                "severity": severity,
                "exploit_available": exploit_available,
                "family": family,
                "vpr_score": vpr_score,
                "plugin_id": plugin_id,
                "cve": cve,
                "port": port,
                "protocol": protocol,
            }
        }
    
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed to get vulnerability summary for {ip}: {str(exc)}",
            "ip": ip
        }


@mcp.tool()
def tsc_list_vulns_by_ip_full(
    ip: str,
    # Top 10 common filters
    severity: str | None = None,
    exploit_available: str | None = None,
    first_seen: str | None = None,
    last_seen: str | None = None,
    family: str | None = None,
    vpr_score: str | None = None,
    plugin_id: str | None = None,
    cve: str | None = None,
    port: int | None = None,
    protocol: str | None = None,
    # Additional common filters
    cvss_v3_base_score: str | None = None,
    epss_score: str | None = None,
    patch_published: str | None = None,
    vuln_published: str | None = None,
    mitigated_status: str | None = None,
    # Pagination
    start_offset: int = 0,
    end_offset: int = 50,
) -> dict[str, Any]:
    """
    Get full vulnerability details for an IP address with filtering and pagination.
    
    Returns complete vulnerability records with all fields.
    Use this for detailed investigation and reporting.
    
    Token Efficiency: ~5,000 tokens for 50 records (vs ~12,000 unfiltered)
    Cache TTL: 180s (3 minutes)
    
    Args:
        ip: IP address to query (required)
        
        Common Filters:
        severity: Filter by severity (0-4 or info/low/medium/high/critical)
        exploit_available: Filter by exploit availability (Yes/No)
        first_seen: Filter by first seen date (epoch timestamp)
        last_seen: Filter by last seen date (epoch timestamp)
        family: Filter by plugin family name
        vpr_score: Filter by VPR score (e.g., "7.0" or ">=7.0")
        plugin_id: Filter by specific plugin ID
        cve: Filter by CVE ID
        port: Filter by port number
        protocol: Filter by protocol (TCP/UDP)
        
        Additional Filters:
        cvss_v3_base_score: Filter by CVSS v3 base score
        epss_score: Filter by EPSS score
        patch_published: Filter by patch publication date
        vuln_published: Filter by vulnerability publication date
        mitigated_status: Filter by mitigation status
        
        Pagination:
        start_offset: Starting record (0-indexed, default: 0)
        end_offset: Ending record (exclusive, default: 50, max: 200)
    
    Returns:
        Full vulnerability records with pagination info
    
    Example:
        >>> tsc_list_vulns_by_ip_full("10.1.20.10", severity="critical", end_offset=10)
        {
            "ok": True,
            "ip": "10.1.20.10",
            "summary": {
                "total_records": 15,
                "returned_records": 10,
                "start_offset": 0,
                "end_offset": 10
            },
            "vulnerabilities": [
                {
                    "plugin_id": "98765",
                    "name": "Critical RCE Vulnerability",
                    "severity": "Critical",
                    "cvss_v3_base_score": 9.8,
                    "vpr_score": 9.2,
                    "exploit_available": "Yes",
                    ...
                }
            ]
        }
    """
    # Validate IP
    valid, error = validate_ip(ip)
    if not valid:
        return {"ok": False, "error": error}
    
    # Validate severity if provided
    if severity:
        valid, error = validate_severity(severity)
        if not valid:
            return {"ok": False, "error": error}
    
    # Validate pagination
    if end_offset > 200:
        return {
            "ok": False,
            "error": f"end_offset cannot exceed 200 (requested: {end_offset})",
            "suggestion": "Use pagination by setting start_offset/end_offset in multiple queries"
        }
    
    if start_offset < 0 or end_offset < 0:
        return {
            "ok": False,
            "error": "start_offset and end_offset must be non-negative"
        }
    
    if start_offset >= end_offset:
        return {
            "ok": False,
            "error": f"start_offset ({start_offset}) must be less than end_offset ({end_offset})"
        }
    
    try:
        # Build filters from parameters
        filters = build_filters(
            ip=ip,
            severity=severity,
            exploit_available=exploit_available,
            first_seen=first_seen,
            last_seen=last_seen,
            family=family,
            vpr_score=vpr_score,
            plugin_id=plugin_id,
            cve=cve,
            port=port,
            protocol=protocol,
            cvss_v3_base_score=cvss_v3_base_score,
            epss_score=epss_score,
            patch_published=patch_published,
            vuln_published=vuln_published,
            mitigated_status=mitigated_status,
        )
        
        # Query using vulnipdetail tool (full details)
        query = {
            "tool": "vulnipdetail",
            "type": "vuln",
            "sourceType": "cumulative",
            "query": {
                "tool": "vulnipdetail",
                "filters": filters
            },
            "sortField": "severity",
            "sortDir": "DESC",
            "startOffset": start_offset,
            "endOffset": end_offset,
        }
        
        result = tsc_analyze(query)
        
        if not result.get("ok"):
            return result
        
        # Extract vulnerability data
        response = result.get("response", {})
        vuln_data = response.get("results", [])
        
        # Format vulnerabilities for cleaner output
        formatted_vulns = []
        for vuln in vuln_data:
            formatted_vulns.append({
                "plugin_id": vuln.get("pluginID"),
                "name": vuln.get("pluginName"),
                "severity": vuln.get("severity", {}).get("name"),
                "severity_id": vuln.get("severity", {}).get("id"),
                "port": vuln.get("port"),
                "protocol": vuln.get("protocol"),
                "family": vuln.get("family", {}).get("name"),
                "cvss_v3_base_score": vuln.get("cvssV3BaseScore"),
                "vpr_score": vuln.get("vprScore"),
                "epss_score": vuln.get("epssScore"),
                "exploit_available": vuln.get("exploitAvailable"),
                "exploit_frameworks": vuln.get("exploitFrameworks"),
                "cve": vuln.get("cve"),
                "first_seen": vuln.get("firstSeen"),
                "last_seen": vuln.get("lastSeen"),
                "synopsis": vuln.get("synopsis", "")[:200],  # Truncate for token efficiency
                "solution": vuln.get("solution", "")[:200],
            })
        
        return {
            "ok": True,
            "ip": ip,
            "summary": {
                "total_records": response.get("totalRecords"),
                "returned_records": response.get("returnedRecords"),
                "start_offset": start_offset,
                "end_offset": end_offset,
                "has_more": int(response.get("totalRecords", 0)) > end_offset,
            },
            "vulnerabilities": formatted_vulns,
            "filters_applied": {
                "severity": severity,
                "exploit_available": exploit_available,
                "family": family,
                "vpr_score": vpr_score,
                "plugin_id": plugin_id,
                "cve": cve,
                "port": port,
                "protocol": protocol,
                "cvss_v3_base_score": cvss_v3_base_score,
                "epss_score": epss_score,
            }
        }
    
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed to get vulnerabilities for {ip}: {str(exc)}",
            "ip": ip
        }


@mcp.resource("tenable-sc://catalog")
def catalog_resource() -> str:
    """Human-readable Tenable.sc API catalog."""
    lines = ["# Tenable.sc API Catalog", ""]
    for item in API_RESOURCES:
        lines.append(f"- {item.name}: /rest/{item.path} ({item.docs})")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Tenable.sc MCP server")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind for sse or streamable-http transports")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind for sse or streamable-http transports")
    parser.add_argument(
        "--env-file",
        default=None,
        help="Path to env file with Tenable.sc credentials (example: ~/.tenable-sc-mcp.env)",
    )
    parser.add_argument(
        "--env-prefix",
        default="TSC_",
        help="Environment variable prefix for Tenable.sc settings, default TSC_",
    )
    parser.add_argument(
        "--allow-remote-hosts",
        action="store_true",
        help="Disable MCP DNS rebinding protection for lab/VPN HTTP access. Use only on trusted networks.",
    )
    args = parser.parse_args()
    configure_client_env(env_prefix=args.env_prefix, env_file=args.env_file)
    
    # Initialize cache (already done in configure_client_env, but ensure it's set up)
    if _CACHE is None:
        _init_cache()
    
    mcp.settings.host = args.host
    mcp.settings.port = args.port
    if args.allow_remote_hosts:
        mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
