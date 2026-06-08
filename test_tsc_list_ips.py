#!/usr/bin/env python3
"""
Direct test script for tsc_list_ips tool.
Tests the tool directly without MCP client to verify basic functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from tenable_sc_mcp.tools.asset_discovery import register_tools

class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}
    
    def tool(self):
        """Decorator that captures tool functions."""
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

def test_basic():
    """Test basic tool registration and structure."""
    print("=" * 60)
    print("TEST 1: Basic Tool Registration")
    print("=" * 60)
    
    mcp = MockMCP()
    register_tools(mcp)
    
    if "tsc_list_ips" in mcp.tools:
        print("✓ tsc_list_ips registered successfully")
        tool = mcp.tools["tsc_list_ips"]
        print(f"✓ Tool function: {tool.__name__}")
        print(f"✓ Tool docstring (first 100 chars): {tool.__doc__[:100]}...")
    else:
        print("✗ tsc_list_ips NOT registered")
        print(f"Available tools: {list(mcp.tools.keys())}")
        return False
    
    print()
    return True

def test_validation():
    """Test input validation without calling API."""
    print("=" * 60)
    print("TEST 2: Input Validation")
    print("=" * 60)
    
    mcp = MockMCP()
    register_tools(mcp)
    tool = mcp.tools["tsc_list_ips"]
    
    # Test 1: No parameters should fail
    print("Test 2.1: No parameters (should fail)...")
    result = tool()
    if not result.get("ok") and "Must provide either" in result.get("error", ""):
        print("✓ Correctly rejects missing parameters")
        print(f"  Error: {result.get('error')[:80]}...")
    else:
        print("✗ Should have rejected missing parameters")
        print(f"  Result: {result}")
        return False
    
    # Test 2: Both repository and asset_group should fail
    print("\nTest 2.2: Both repository and asset_group (should fail)...")
    result = tool(repository="Default", asset_group="Windows")
    if not result.get("ok") and "only ONE" in result.get("error", ""):
        print("✓ Correctly rejects conflicting parameters")
        print(f"  Error: {result.get('error')[:80]}...")
    else:
        print("✗ Should have rejected conflicting parameters")
        print(f"  Result: {result}")
        return False
    
    # Test 3: Invalid IP should fail
    print("\nTest 2.3: Invalid IP format (should fail)...")
    result = tool(ip="not.an.ip.address")
    if not result.get("ok") and "Invalid IP" in result.get("error", ""):
        print("✓ Correctly validates IP format")
        print(f"  Error: {result.get('error')[:80]}...")
    else:
        print("✗ Should have rejected invalid IP")
        print(f"  Result: {result}")
        return False
    
    print()
    return True

def test_structure():
    """Test response structure (without live API)."""
    print("=" * 60)
    print("TEST 3: Code Structure Validation")
    print("=" * 60)
    
    # Check that imports work
    try:
        from tenable_sc_mcp.tools.asset_discovery import (
            _resolve_asset_group_name,
            _find_ip_membership
        )
        print("✓ Helper functions imported successfully")
        print(f"  - _resolve_asset_group_name: {_resolve_asset_group_name.__name__}")
        print(f"  - _find_ip_membership: {_find_ip_membership.__name__}")
    except ImportError as e:
        print(f"✗ Failed to import helper functions: {e}")
        return False
    
    # Check convenience_tools imports
    try:
        from tenable_sc_mcp.convenience_tools import validate_ip, build_filters
        print("✓ Convenience tools imported successfully")
        
        # Test validate_ip
        valid, error = validate_ip("10.1.20.10")
        if valid:
            print("  - validate_ip('10.1.20.10'): ✓ Valid")
        else:
            print(f"  - validate_ip('10.1.20.10'): ✗ {error}")
            return False
    except ImportError as e:
        print(f"✗ Failed to import convenience_tools: {e}")
        return False
    
    print()
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TSC_LIST_IPS TOOL TEST SUITE")
    print("=" * 60)
    print("\nNote: This tests tool structure and validation only.")
    print("API calls require live Tenable.sc connection via Docker.\n")
    
    results = []
    
    results.append(("Basic Registration", test_basic()))
    results.append(("Input Validation", test_validation()))
    results.append(("Code Structure", test_structure()))
    
    print("=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Rebuild Docker container: docker-compose build")
        print("2. Restart container: docker-compose up -d")
        print("3. Test with real Tenable.sc data via MCP client")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED ✗")
        print("=" * 60)
        print("\nFix the issues above before proceeding.")
        sys.exit(1)
