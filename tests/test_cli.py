"""Tests for CLI entry point."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from ldap_mcp import main


class TestMain:
    @pytest.fixture
    def mock_create_server(self) -> Iterator[MagicMock]:
        with patch("ldap_mcp.server.create_server") as mock:
            yield mock

    @pytest.mark.parametrize(
        ("args", "expected_transport"),
        [
            ([], "stdio"),
            (["--transport", "stdio"], "stdio"),
            (["--transport", "sse"], "sse"),
            (["--transport", "streamable-http"], "streamable-http"),
        ],
        ids=["default", "explicit_stdio", "sse", "streamable_http"],
    )
    def test_runs_server_with_transport(
        self, mock_create_server: MagicMock, args: list[str], expected_transport: str
    ) -> None:
        with patch("sys.argv", ["ldap-mcp", *args]):
            main()

        mock_create_server.return_value.run.assert_called_once_with(transport=expected_transport)

    def test_creates_server(self, mock_create_server: MagicMock) -> None:
        with patch("sys.argv", ["ldap-mcp"]):
            main()

        mock_create_server.assert_called_once()
