"""Prompt registration for the LDAP MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_prompts(mcp: "FastMCP") -> None:
    """Register all prompts with the MCP server."""
    # Prompts will be registered in Phase 3
    pass
