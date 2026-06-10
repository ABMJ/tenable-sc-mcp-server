"""
MCP Resources for Tenable.sc MCP Server.

Provides reference documentation and metadata as MCP resources that clients
can fetch to understand how to use tools effectively.
"""

def register_resources(mcp):
    """
    Register all MCP resources.
    
    Resources provide documentation, references, and metadata that MCP clients
    can fetch to enhance their understanding of tool capabilities.
    """
    from . import filter_reference
    from . import filter_format_reference_v2
    
    filter_reference.register_resources(mcp)
    filter_format_reference_v2.register_resources(mcp)
