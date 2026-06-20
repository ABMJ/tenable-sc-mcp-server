"""
Admin tools for Tenable.sc MCP Server.

Current tools:
- tsc_list_plugin_families (v1.3.0) - Plugin family discovery

Future tools:
- Tool 9: tsc_resources_status (Scanner/NNM/WAS health)
- Tool 24: tsc_plugin_update_status
- Tool 25: tsc_license_usage
- Tool 26: tsc_repo_status

Admin tools typically require elevated Tenable.sc privileges.
"""

from __future__ import annotations


def register_all_admin_tools(mcp):
    """Register all admin tools."""
    from .plugins import register_tools as register_plugin_tools
    
    register_plugin_tools(mcp)


__all__ = ["register_all_admin_tools"]
