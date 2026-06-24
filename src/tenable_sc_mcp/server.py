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
        
        # Invalidate cache on write operations (but NOT for /analysis - it's read-only despite using POST)
        if cache and method in ("PUT", "PATCH", "DELETE"):
            resource_name = path.strip("/").split("/")[0]
            cache.delete_pattern(resource_name)
        
        # POST creates should also invalidate cache (except /analysis)
        if cache and method == "POST" and not path.strip("/").startswith("analysis"):
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
    # Tenable.sc /analysis endpoint requires query to be wrapped in {"query": {...}}
    request_body = {"query": query}
    result = tsc_request("POST", "/analysis", body=request_body, fields=fields, timeout_seconds=timeout_seconds)
    
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
# CONVENIENCE TOOLS - Modular Implementation
# ============================================================================

# Import and register all convenience tools from modules
from .tools import register_all_tools  # noqa: E402

# Re-export convenience tool functions for backwards compatibility with tests
# These are populated after register_all_tools() is called
_tool_functions = {}

def _get_tool(name: str):
    """Get a registered tool function by name."""
    return _tool_functions.get(name)

# Tools are registered during module initialization via register_all_tools(mcp)
# This is called at the end of this file before main() runs


# ============================================================================
# MCP RESOURCES - Documentation & References
# ============================================================================

# Import and register all MCP resources (filter docs, etc.)
from .resources import register_resources  # noqa: E402

# Resources are registered during module initialization via register_resources(mcp)
# This provides documentation like tenable-sc://filters/reference for LLM consumption


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
    
    # Register all MCP resources (filter documentation, etc.)
    register_resources(mcp)
    
    # Register all convenience tools from modules
    register_all_tools(mcp)
    
    mcp.settings.host = args.host
    mcp.settings.port = args.port
    if args.allow_remote_hosts:
        mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
