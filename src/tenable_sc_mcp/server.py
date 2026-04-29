from __future__ import annotations

import argparse
import base64
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .catalog import API_RESOURCES, RESOURCE_BY_PATH, catalog_as_dict
from .client import TenableScApiError, TenableScClient, TenableScConfigError


_CLIENT_ENV_PREFIX = "TSC_"
_CLIENT_ENV_FILE: str | None = None

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


def configure_client_env(*, env_prefix: str, env_file: str | None) -> None:
    global _CLIENT_ENV_PREFIX
    global _CLIENT_ENV_FILE
    _CLIENT_ENV_PREFIX = env_prefix
    _CLIENT_ENV_FILE = env_file


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


@mcp.tool()
def tsc_catalog(
    include_admin_or_director: bool = True,
    query: str | None = None,
    limit: int | None = None,
    compact: bool = True,
) -> dict[str, Any]:
    """Returns Tenable.sc resource catalog; supports filtering and compact output."""
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
    return {"ok": True, "count": len(resources), "resources": resources}


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
) -> dict[str, Any]:
    """Calls any Tenable.sc endpoint; use as advanced escape hatch."""
    try:
        response = _client().request(
            method,
            path,
            params=_query_params(params, fields, expand, editable),
            json_body=body,
            timeout_seconds=timeout_seconds,
        )
        return {"ok": True, "response": response}
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
def tsc_resource_docs(resource: str) -> dict[str, Any]:
    """Returns docs metadata for one Tenable.sc resource path."""
    item = RESOURCE_BY_PATH.get(resource)
    if not item:
        matches = [entry for entry in catalog_as_dict() if resource.lower() in str(entry["name"]).lower()]
        return {"ok": False, "error": f"Unknown resource: {resource}", "possible_matches": matches}
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
    """Runs a Tenable.sc analysis query via POST /analysis."""
    return tsc_request("POST", "/analysis", body=query, fields=fields, timeout_seconds=timeout_seconds)


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
    mcp.settings.host = args.host
    mcp.settings.port = args.port
    if args.allow_remote_hosts:
        mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
