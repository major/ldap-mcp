"""Tests for FastMCP server setup and lifespan."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from fastmcp import FastMCP

from ldap_mcp.server import AppContext, create_server, lifespan


class TestAppContext:
    def test_stores_connection_and_base_dn(self, mock_connection: MagicMock) -> None:
        ctx = AppContext(connection=mock_connection, base_dn="dc=test,dc=com")

        assert ctx.connection is mock_connection
        assert ctx.base_dn == "dc=test,dc=com"


class TestLifespan:
    @pytest.fixture
    def mock_create_connection(self) -> Iterator[MagicMock]:
        with patch("ldap_mcp.server.create_connection") as mock:
            mock.return_value = MagicMock(bound=True)
            yield mock

    @pytest.fixture
    def mock_settings(self) -> Iterator[MagicMock]:
        with patch("ldap_mcp.server.LDAPMCPSettings") as mock:
            mock.return_value.base_dn = "dc=example,dc=com"
            yield mock

    @pytest.mark.asyncio
    async def test_yields_app_context(
        self, mock_create_connection: MagicMock, mock_settings: MagicMock
    ) -> None:
        mcp = MagicMock(spec=FastMCP)

        async with lifespan(mcp) as ctx:
            assert isinstance(ctx, AppContext)
            assert ctx.base_dn == "dc=example,dc=com"

    @pytest.mark.asyncio
    async def test_unbinds_connection_on_exit(
        self, mock_create_connection: MagicMock, mock_settings: MagicMock
    ) -> None:
        mcp = MagicMock(spec=FastMCP)
        conn = mock_create_connection.return_value

        async with lifespan(mcp):
            pass

        conn.unbind.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_unbind_when_not_bound(
        self, mock_create_connection: MagicMock, mock_settings: MagicMock
    ) -> None:
        mcp = MagicMock(spec=FastMCP)
        conn = mock_create_connection.return_value
        conn.bound = False

        async with lifespan(mcp):
            pass

        conn.unbind.assert_not_called()


class TestCreateServer:
    @pytest.fixture
    def mock_register_tools(self) -> Iterator[MagicMock]:
        with patch("ldap_mcp.tools.register_tools") as mock:
            yield mock

    @pytest.fixture
    def mock_register_prompts(self) -> Iterator[MagicMock]:
        with patch("ldap_mcp.prompts.register_prompts") as mock:
            yield mock

    def test_creates_fastmcp_server(
        self, mock_register_tools: MagicMock, mock_register_prompts: MagicMock
    ) -> None:
        server = create_server()

        assert isinstance(server, FastMCP)
        assert server.name == "ldap"

    def test_registers_tools_and_prompts(
        self, mock_register_tools: MagicMock, mock_register_prompts: MagicMock
    ) -> None:
        server = create_server()

        mock_register_tools.assert_called_once_with(server)
        mock_register_prompts.assert_called_once_with(server)
