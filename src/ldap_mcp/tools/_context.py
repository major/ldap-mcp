"""Context extraction utilities for tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from fastmcp import Context

    from ldap_mcp.server import AppContext


def get_app_context(ctx: "Context") -> "AppContext":
    """Extract AppContext from FastMCP context."""
    return cast("AppContext", ctx.lifespan_context)
