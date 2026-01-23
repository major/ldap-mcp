"""FastMCP server setup and lifespan management."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastmcp import FastMCP
from ldap3 import Connection

from ldap_mcp.config import LDAPMCPSettings
from ldap_mcp.connection import create_connection


@dataclass
class AppContext:
    """Typed application context for lifespan-managed resources."""

    connection: Connection
    base_dn: str
    default_filter: str = ""


@asynccontextmanager
async def lifespan(mcp: "FastMCP") -> AsyncIterator[AppContext]:
    """Manage LDAP connection lifecycle."""
    settings = LDAPMCPSettings()
    connection = create_connection(settings)

    try:
        yield AppContext(
            connection=connection,
            base_dn=settings.base_dn,
            default_filter=settings.default_filter,
        )
    finally:
        if connection.bound:
            connection.unbind()


def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP(
        name="ldap",
        instructions="""LDAP directory operations (read-only).

Use ldap_search for finding entries, then ldap_get_entry for full details.
LDAP filters use syntax like (objectClass=person) or (&(cn=*admin*)(mail=*)).
""",
        lifespan=lifespan,
    )

    from ldap_mcp.prompts import register_prompts
    from ldap_mcp.tools import register_tools

    register_tools(mcp)
    register_prompts(mcp)

    return mcp
