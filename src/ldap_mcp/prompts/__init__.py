"""Prompt registration for the LDAP MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ldap_mcp.prompts.group_members import group_members
from ldap_mcp.prompts.group_membership import group_membership
from ldap_mcp.prompts.search_guide import search_guide
from ldap_mcp.prompts.user_lookup import user_lookup

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_prompts(mcp: "FastMCP") -> None:
    """Register all prompts with the MCP server."""
    mcp.add_prompt(user_lookup)
    mcp.add_prompt(group_members)
    mcp.add_prompt(group_membership)
    mcp.add_prompt(search_guide)
