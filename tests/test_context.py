"""Tests for context extraction utilities."""

from __future__ import annotations

from unittest.mock import MagicMock

from ldap_mcp.server import AppContext
from ldap_mcp.tools._context import get_app_context


class TestGetAppContext:
    def test_returns_lifespan_context(self) -> None:
        app_context = AppContext(
            connection=MagicMock(),
            base_dn="dc=example,dc=com",
            default_filter="",
        )
        ctx = MagicMock()
        ctx.lifespan_context = app_context

        result = get_app_context(ctx)

        assert result is app_context
