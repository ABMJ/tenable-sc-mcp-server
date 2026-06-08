#!/usr/bin/env python3
"""Test if tsc_list_ips is registered correctly."""

import sys
sys.path.insert(0, 'src')

from mcp.server.fastmcp import FastMCP

# Create a test MCP server
mcp = FastMCP("test-server")

# Import and register tools
from tenable_sc_mcp.tools import register_all_tools
register_all_tools(mcp)

# List all registered tools
print("Registered tools:")
for tool in mcp._tool_manager._tools.values():
    print(f"  - {tool.name}")
    if tool.name == "tsc_list_ips":
        print(f"    ✅ Found tsc_list_ips!")
        print(f"    Description: {tool.description[:100]}...")

# Check if tsc_list_ips exists
if any(t.name == "tsc_list_ips" for t in mcp._tool_manager._tools.values()):
    print("\n✅ SUCCESS: tsc_list_ips is registered")
else:
    print("\n❌ FAILURE: tsc_list_ips NOT found")
    print("\nAvailable tools:")
    for tool in mcp._tool_manager._tools.values():
        print(f"  - {tool.name}")
