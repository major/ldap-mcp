"""Tool registration for the LDAP MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ldap_mcp.tools.compare import ldap_compare
from ldap_mcp.tools.entry import ldap_get_entry
from ldap_mcp.tools.schema import ldap_get_schema
from ldap_mcp.tools.search import ldap_search

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(mcp: "FastMCP") -> None:
    """Register all tools with the MCP server."""
    mcp.add_tool(ldap_search)
    mcp.add_tool(ldap_get_entry)
    mcp.add_tool(ldap_get_schema)
    mcp.add_tool(ldap_compare)
