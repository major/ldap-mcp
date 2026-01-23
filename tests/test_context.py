"""Tests for context extraction utilities."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ldap_mcp.tools._context import get_app_context


class TestGetAppContext:
    def test_returns_lifespan_context(self, mock_ctx: MagicMock) -> None:
        result = get_app_context(mock_ctx)

        assert result is mock_ctx.request_context.lifespan_context

    def test_raises_when_request_context_none(self) -> None:
        ctx = MagicMock()
        ctx.request_context = None

        with pytest.raises(RuntimeError, match="Request context not available"):
            get_app_context(ctx)

    def test_raises_when_lifespan_context_none(self) -> None:
        ctx = MagicMock()
        ctx.request_context.lifespan_context = None

        with pytest.raises(RuntimeError, match="Lifespan context not available"):
            get_app_context(ctx)
