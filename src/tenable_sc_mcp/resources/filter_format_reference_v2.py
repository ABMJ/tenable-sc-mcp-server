"""
MCP Resource: Comprehensive Filter Format Reference v1.2.0

Exposes the comprehensive FILTER_FORMAT_REFERENCE.md as an MCP resource
that Claude can access directly for filter guidance.
"""

from __future__ import annotations
import os


def load_filter_format_reference() -> str:
    """
    Load the comprehensive FILTER_FORMAT_REFERENCE.md file.
    
    Returns:
        Full markdown content of the filter format reference
    """
    # Get the project root directory (3 levels up from this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    reference_path = os.path.join(project_root, "FILTER_FORMAT_REFERENCE.md")
    
    try:
        with open(reference_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return """# Filter Format Reference (Not Found)

The comprehensive filter format reference file was not found at the expected location.

Please ensure FILTER_FORMAT_REFERENCE.md exists in the project root directory.

**Expected location:** {reference_path}

**Fallback:** Use the filter_reference resource for basic filter documentation.
""".format(reference_path=reference_path)
    except Exception as e:
        return f"""# Filter Format Reference (Error)

An error occurred while loading the filter format reference:

**Error:** {str(e)}

**Fallback:** Use the filter_reference resource for basic filter documentation.
"""


def register_resources(mcp):
    """Register filter format reference resource with MCP server."""
    
    @mcp.resource("tenable-sc://filters/format-reference")
    async def get_filter_format_reference() -> str:
        """
        Comprehensive filter format reference for v1.2.0 unified filters API.
        
        Returns the complete FILTER_FORMAT_REFERENCE.md document with:
        - Simple filters (string/number format)
        - Range filters (min-max format)
        - Complex filters (array of objects format)
        - Tool-specific examples
        - Common filter combinations
        - Troubleshooting guide
        - Test results reference
        
        This is the primary reference for filter usage in v1.2.0.
        
        Returns:
            Markdown-formatted comprehensive filter reference
        """
        # Load the comprehensive filter format reference
        docs = load_filter_format_reference()
        
        # Add dynamic header with metadata
        header = """# Comprehensive Filter Format Reference - Tenable.sc MCP v1.2.0

**📌 MCP Resource URI:** `tenable-sc://filters/format-reference`  
**📅 Version:** 1.2.0  
**✅ Test Pass Rate:** 93.3% (56/60 tests)  
**🔗 GitHub:** https://github.com/abmj01/tenable-sc-mcp-server

---

**QUICK NAVIGATION:**
- [Quick Reference](#quick-reference) - Common filter examples
- [Simple Filters](#-simple-filters-stringnumber-format) - Easy formats
- [Range Filters](#-range-filters-min-max-format) - Scoring metrics
- [Complex Filters](#-complex-filters-array-of-objects-format) - Advanced formats
- [Tool Examples](#filter-examples-by-tool) - Per-tool usage
- [Common Combinations](#common-filter-combinations) - Real-world scenarios
- [Troubleshooting](#troubleshooting) - Error solutions
- [Test Results](#test-results-reference) - What's been validated

---

"""
        
        return header + docs
