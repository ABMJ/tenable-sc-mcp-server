from __future__ import annotations

import argparse
import base64
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings

from .catalog import API_RESOURCES, RESOURCE_BY_PATH, catalog_as_dict
from .client import TenableScApiError, TenableScClient, TenableScConfigError

mcp = FastMCP(
    "tenable-sc-mcp",
    instructions=(
        "Direct MCP interface for Tenable Security Center Plus. "
        "All Tenable.sc permissions are enforced by the configured API keys. "
        "Use tsc_catalog to discover documented resources and tsc_request for endpoint-specific actions."
    ),
)


def _client() -> TenableScClient:
    return TenableScClient()


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
def tsc_catalog(include_admin_or_director: bool = True) -> dict[str, Any]:
    """Return the built-in Tenable.sc API resource catalog with REST paths and documentation links.

    Set include_admin_or_director=false to hide resources that commonly require administrator,
    director, or system-level Tenable.sc permissions. This is only a documentation filter;
    Tenable.sc remains the source of truth for RBAC enforcement.
    """
    resources = catalog_as_dict()
    if not include_admin_or_director:
        resources = [resource for resource in resources if not resource["admin_or_director"]]
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
    """Call any Tenable.sc REST API endpoint using direct HTTP.

    The path can be either a documented resource path such as /scan, /scan/123,
    /analysis, /scan/123/launch, or a full /rest/... path. Use params for query
    parameters, body for JSON request payloads, fields for ?fields=..., expand for
    ?expand=..., and editable=true for ?editable. This tool is the escape hatch for
    all documented Tenable.sc API actions beyond simple CRUD.
    """
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
def tsc_list(
    resource: str,
    params: dict[str, Any] | None = None,
    fields: list[str] | None = None,
    expand: list[str] | None = None,
    editable: bool = False,
) -> dict[str, Any]:
    """List objects for any documented Tenable.sc resource.

    resource is the catalog path, for example scan, repository, asset, user,
    organizationUser, plugin, role, or currentUser. RBAC is enforced by Tenable.sc.
    """
    return tsc_request("GET", f"/{resource}", params=params, fields=fields, expand=expand, editable=editable)


@mcp.tool()
def tsc_get(
    resource: str,
    object_id: str,
    params: dict[str, Any] | None = None,
    fields: list[str] | None = None,
    expand: list[str] | None = None,
    editable: bool = False,
) -> dict[str, Any]:
    """Get one object from any documented Tenable.sc resource by ID.

    Supports fields, expand, editable, and custom query parameters where the
    underlying Tenable.sc endpoint accepts them.
    """
    return tsc_request("GET", f"/{resource}/{object_id}", params=params, fields=fields, expand=expand, editable=editable)


@mcp.tool()
def tsc_create(resource: str, body: dict[str, Any]) -> dict[str, Any]:
    """Create an object in any Tenable.sc resource that supports POST.

    The body must match Tenable.sc's documented JSON payload for the target resource.
    Tenable.sc rejects calls that the API identity is not permitted to perform.
    """
    return tsc_request("POST", f"/{resource}", body=body)


@mcp.tool()
def tsc_update(resource: str, object_id: str, body: dict[str, Any]) -> dict[str, Any]:
    """Update an object in any Tenable.sc resource that supports PUT.

    The body must match Tenable.sc's documented JSON payload for the target resource.
    """
    return tsc_request("PUT", f"/{resource}/{object_id}", body=body)


@mcp.tool()
def tsc_delete(resource: str, object_id: str) -> dict[str, Any]:
    """Delete an object from any Tenable.sc resource that supports DELETE.

    Destructive operations are still subject to Tenable.sc RBAC and API validation.
    """
    return tsc_request("DELETE", f"/{resource}/{object_id}")


@mcp.tool()
def tsc_current_user() -> dict[str, Any]:
    """Return the current Tenable.sc API user's details.

    Use this first when validating RBAC, role membership, and what the configured
    API identity can see in Tenable.sc.
    """
    return tsc_request("GET", "/currentUser")


@mcp.tool()
def tsc_resource_docs(resource: str) -> dict[str, Any]:
    """Return documentation metadata for a Tenable.sc resource path.

    Example resource values: analysis, scan, scanResult, repository, asset,
    credential, user, role, currentUser.
    """
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
    """Run a Tenable.sc analysis query.

    Pass the Analysis API payload in query. This commonly includes type, sourceType,
    query filters, sort, and pagination fields as documented by Tenable.sc. This helper
    uses POST /analysis and exists because analysis is one of the highest-use APIs.
    """
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
    """Download a binary or text response from a Tenable.sc endpoint.

    Use this for documented download endpoints such as /scanResult/{id}/download
    or /scanResult/{id}/attachment/{attachmentID}. The response body is returned
    as base64 because MCP tool responses are JSON. Tenable.sc still enforces RBAC.
    """
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
    """Upload a local file to Tenable.sc using POST /file/upload.

    file_path is resolved on the machine/container running this MCP server. The
    returned filename can be passed to APIs such as scanResult import or audit
    file creation. Tenable.sc still enforces RBAC.
    """
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
        "--allow-remote-hosts",
        action="store_true",
        help="Disable MCP DNS rebinding protection for lab/VPN HTTP access. Use only on trusted networks.",
    )
    args = parser.parse_args()
    mcp.settings.host = args.host
    mcp.settings.port = args.port
    if args.allow_remote_hosts:
        mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
