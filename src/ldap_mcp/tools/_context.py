"""Context extraction utilities for tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import Context

    from ldap_mcp.server import AppContext


def get_app_context(ctx: "Context") -> "AppContext":
    """Extract AppContext from FastMCP context.

    Raises:
        RuntimeError: If context is not properly initialized.
    """
    request_context = ctx.request_context
    if request_context is None:
        raise RuntimeError("Request context not available")

    lifespan_context = request_context.lifespan_context
    if lifespan_context is None:
        raise RuntimeError("Lifespan context not available")

    return lifespan_context
