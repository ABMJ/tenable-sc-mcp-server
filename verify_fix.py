#!/usr/bin/env python3
"""
Verification test for analysis query caching fix.

This test verifies the code changes are correct by inspecting the source code.
For actual runtime testing, rebuild the Docker containers and test through MCP.
"""

import re
from pathlib import Path


def verify_fix():
    """Verify the tsc_analyze function has caching implemented."""
    print("=" * 70)
    print("Verifying Analysis Query Caching Fix")
    print("=" * 70)
    
    server_file = Path(__file__).parent / "src/tenable_sc_mcp/server.py"
    
    if not server_file.exists():
        print(f"\n❌ ERROR: server.py not found at {server_file}")
        return False
    
    content = server_file.read_text()
    
    # Check if tsc_analyze function exists
    if "def tsc_analyze(" not in content:
        print("\n❌ ERROR: tsc_analyze function not found")
        return False
    
    print("\n✅ Found tsc_analyze function")
    
    # Extract the tsc_analyze function
    pattern = r'def tsc_analyze\(.*?\n(?:.*?\n)*?(?=\n@mcp\.tool\(\)|def \w+\(|$)'
    match = re.search(pattern, content, re.MULTILINE)
    
    if not match:
        print("⚠️  Could not extract function body (might be OK)")
        function_body = ""
    else:
        function_body = match.group(0)
        print(f"✅ Extracted function body ({len(function_body)} chars)")
    
    # Verify caching logic is present
    checks = {
        "Cache retrieval": "_get_cache()" in function_body,
        "Cache key generation": "generate_cache_key(" in function_body,
        "Cache lookup": "cache.get(cache_key)" in function_body,
        "Cache storage": "cache.set(cache_key" in function_body,
        "TTL configuration": "get_ttl_for_resource(" in function_body,
    }
    
    print("\n" + "=" * 70)
    print("Verification Results:")
    print("=" * 70)
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {'PASS' if passed else 'FAIL'}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✅ SUCCESS: All caching components are present in tsc_analyze!")
        print("\nThe fix implements:")
        print("  • Cache lookup before API call")
        print("  • Deterministic cache key generation from query body")
        print("  • Cache storage after successful API response")
        print("  • TTL-based expiration (60 seconds for analysis)")
        print("\nNext steps:")
        print("  1. Rebuild Docker containers: docker-compose build")
        print("  2. Restart containers: docker-compose up -d")
        print("  3. Test with actual MCP queries")
        return True
    else:
        print("❌ FAILURE: Some caching components are missing!")
        print("\nThe fix may be incomplete.")
        return False


def show_function_snippet():
    """Show the updated tsc_analyze function."""
    server_file = Path(__file__).parent / "src/tenable_sc_mcp/server.py"
    content = server_file.read_text()
    
    # Find the function
    lines = content.split('\n')
    in_function = False
    function_lines = []
    indent_level = None
    
    for i, line in enumerate(lines):
        if 'def tsc_analyze(' in line:
            in_function = True
            function_lines.append(f"{i+1:4d}: {line}")
            indent_level = len(line) - len(line.lstrip())
            continue
        
        if in_function:
            # Check if we've left the function (next function or decorator)
            if line.strip() and not line.startswith(' ' * (indent_level + 1)) and line.strip() not in ['"""', "'''"]:
                if line.startswith('@') or line.startswith('def '):
                    break
            
            function_lines.append(f"{i+1:4d}: {line}")
            
            # Stop after return statement at function level
            if line.strip().startswith('return ') and len(line) - len(line.lstrip()) == indent_level + 4:
                break
    
    if function_lines:
        print("\n" + "=" * 70)
        print("Updated tsc_analyze function:")
        print("=" * 70)
        print('\n'.join(function_lines[:40]))  # Show first 40 lines
        if len(function_lines) > 40:
            print(f"... ({len(function_lines) - 40} more lines)")
        print("=" * 70)


if __name__ == "__main__":
    success = verify_fix()
    show_function_snippet()
    
    if success:
        print("\n🎉 Fix verification complete! Ready to rebuild and test.")
        exit(0)
    else:
        print("\n⚠️  Fix verification failed. Please review the changes.")
        exit(1)
