"""
Tenable.sc MCP Convenience Tools Registry.

This module provides the registration mechanism for all high-value convenience tools.
Each tool module contains domain-specific functionality (IP profiling, vulnerability lookup, etc.)
and registers its tools with the MCP server.

Design Pattern:
- Each module has a register_tools(mcp) function
- Tools are organized by logical domain (ip_profiling, vulnerability_lookup, etc.)
- Server.py imports this module to register all tools at startup
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def register_all_tools(mcp: "FastMCP") -> None:
    """
    Register all convenience tools with the MCP server.
    
    This function is called once during server initialization to register
    all tool modules. Each module's register_tools() function decorates
    its tools with @mcp.tool(), making them available to MCP clients.
    
    Args:
        mcp: The FastMCP server instance
    
    Module Organization:
        - ip_profiling: Tool 1, Tool 19 (IP profile efficient, bulk)
        - vulnerability_lookup: Tools 2a, 2b, 5, 14, 15 (vuln queries)
        - asset_discovery: Tools 4, 17, 18, 22, 23 (IP lists, OS detection)
        - compliance: Tool 8 (compliance status)
        - scanning: Tools 6, 7, 16 (patches, scan status, results)
        - network: Tool 10 (open ports)
        - inventory: Tools 11, 12 (software, services)
        - authentication: Tool 13 (credential audit)
        - risk_scoring: Tools 20, 21 (ACR scoring)
        - admin/: Tools 9, 24, 25, 26 (resource/plugin/license/repo status)
    """
    # Import and register IP profiling tools
    from .ip_profiling import register_tools as register_ip_profiling
    register_ip_profiling(mcp)
    
    # Import and register vulnerability lookup tools
    from .vulnerability_lookup import register_tools as register_vulnerability_lookup
    register_vulnerability_lookup(mcp)
    
    # Import and register asset discovery tools
    from .asset_discovery import register_tools as register_asset_discovery
    register_asset_discovery(mcp)
    
    # Future tool modules will be registered here as they're implemented


__all__ = ["register_all_tools"]
