"""Tool registration for the LDAP MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(mcp: "FastMCP") -> None:
    """Register all tools with the MCP server."""
    # Tools will be registered in Phase 2
    pass
