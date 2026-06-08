#!/usr/bin/env python3
"""Direct test of tsc_list_ips functionality."""

import sys
import os
sys.path.insert(0, 'src')

# Set up environment
os.environ['TSC_URL'] = os.getenv('TSC_URL', 'https://192.168.40.75:8443')
os.environ['TSC_ACCESS_KEY'] = os.getenv('TSC_ACCESS_KEY', '')
os.environ['TSC_SECRET_KEY'] = os.getenv('TSC_SECRET_KEY', '')
os.environ['TSC_VERIFY_SSL'] = 'false'
os.environ['TSC_CACHE_ENABLED'] = 'false'  # Disable cache for testing

from tenable_sc_mcp import server
from tenable_sc_mcp.tools.asset_discovery import register_tools
from mcp.server.fastmcp import FastMCP

# Create MCP server and register tools
mcp = FastMCP("test")
server.configure_client_env(env_prefix="TSC_", env_file=None)
register_tools(mcp)

# Get the tool function
tool = mcp._tool_manager._tools.get("tsc_list_ips")
if not tool:
    print("❌ Tool not found!")
    sys.exit(1)

print("✅ Tool found, testing with asset_group='Windows Hosts'...")
print()

# Call the tool
try:
    result = tool.fn(asset_group="Windows Hosts")
    print(f"Result: {result}")
    
    if result.get("ok"):
        print(f"\n✅ SUCCESS!")
        print(f"   Asset Group: {result.get('asset_group')}")
        print(f"   Total IPs: {result.get('total_ips')}")
        if result.get('total_ips', 0) > 0:
            print(f"   First 5 IPs: {result.get('ips', [])[:5]}")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")
        print(f"   Hint: {result.get('hint')}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
