"""Tests for LDAP connection factory."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from ldap3 import AUTO_BIND_TLS_BEFORE_BIND, SIMPLE

from ldap_mcp.config import AuthMethod, LDAPMCPSettings
from ldap_mcp.connection import create_connection


class TestCreateConnection:
    @pytest.fixture
    def mock_server(self) -> Iterator[MagicMock]:
        with patch("ldap_mcp.connection.Server") as mock:
            yield mock

    @pytest.fixture
    def mock_connection(self) -> Iterator[MagicMock]:
        with patch("ldap_mcp.connection.Connection") as mock:
            yield mock

    @pytest.fixture
    def mock_tls(self) -> Iterator[MagicMock]:
        with patch("ldap_mcp.connection.Tls") as mock:
            yield mock

    def test_creates_anonymous_connection(
        self, mock_server: MagicMock, mock_connection: MagicMock
    ) -> None:
        settings = LDAPMCPSettings(
            uri="ldap://localhost:389",
            base_dn="dc=example,dc=com",
            auth_method=AuthMethod.ANONYMOUS,
        )

        create_connection(settings)

        mock_connection.assert_called_once()
        call_kwargs = mock_connection.call_args.kwargs
        assert "user" not in call_kwargs
        assert call_kwargs["read_only"] is True

    def test_creates_simple_bind_connection(
        self, mock_server: MagicMock, mock_connection: MagicMock
    ) -> None:
        settings = LDAPMCPSettings(
            uri="ldap://localhost:389",
            bind_dn="cn=admin,dc=example,dc=com",
            bind_password="secret",
            base_dn="dc=example,dc=com",
        )

        create_connection(settings)

        call_kwargs = mock_connection.call_args.kwargs
        assert call_kwargs["user"] == "cn=admin,dc=example,dc=com"
        assert call_kwargs["password"] == "secret"
        assert call_kwargs["authentication"] == SIMPLE

    def test_creates_ldaps_connection_with_tls(
        self, mock_server: MagicMock, mock_connection: MagicMock, mock_tls: MagicMock
    ) -> None:
        settings = LDAPMCPSettings(
            uri="ldaps://localhost:636",
            base_dn="dc=example,dc=com",
            auth_method=AuthMethod.ANONYMOUS,
        )

        create_connection(settings)

        mock_tls.assert_called_once()
        tls_kwargs = mock_tls.call_args.kwargs
        assert tls_kwargs["validate"] == 2  # TLS verify on

    def test_creates_starttls_connection(
        self, mock_server: MagicMock, mock_connection: MagicMock, mock_tls: MagicMock
    ) -> None:
        settings = LDAPMCPSettings(
            uri="ldap://localhost:389",
            base_dn="dc=example,dc=com",
            use_starttls=True,
            auth_method=AuthMethod.ANONYMOUS,
        )

        create_connection(settings)

        mock_tls.assert_called_once()
        call_kwargs = mock_connection.call_args.kwargs
        assert call_kwargs["auto_bind"] == AUTO_BIND_TLS_BEFORE_BIND

    @pytest.mark.parametrize(
        ("tls_verify", "expected_validate"),
        [
            (True, 2),
            (False, 0),
        ],
        ids=["verify_on", "verify_off"],
    )
    def test_tls_verify_setting(
        self,
        mock_server: MagicMock,
        mock_connection: MagicMock,
        mock_tls: MagicMock,
        tls_verify: bool,
        expected_validate: int,
    ) -> None:
        settings = LDAPMCPSettings(
            uri="ldaps://localhost:636",
            base_dn="dc=example,dc=com",
            tls_verify=tls_verify,
            auth_method=AuthMethod.ANONYMOUS,
        )

        create_connection(settings)

        assert mock_tls.call_args.kwargs["validate"] == expected_validate

    def test_uses_custom_ca_cert(
        self, mock_server: MagicMock, mock_connection: MagicMock, mock_tls: MagicMock
    ) -> None:
        settings = LDAPMCPSettings(
            uri="ldaps://localhost:636",
            base_dn="dc=example,dc=com",
            ca_cert=Path("/path/to/ca.crt"),
            auth_method=AuthMethod.ANONYMOUS,
        )

        create_connection(settings)

        assert mock_tls.call_args.kwargs["ca_certs_file"] == "/path/to/ca.crt"

    def test_uses_timeout_setting(self, mock_server: MagicMock, mock_connection: MagicMock) -> None:
        settings = LDAPMCPSettings(
            uri="ldap://localhost:389",
            base_dn="dc=example,dc=com",
            timeout=60,
            auth_method=AuthMethod.ANONYMOUS,
        )

        create_connection(settings)

        assert mock_server.call_args.kwargs["connect_timeout"] == 60
        assert mock_connection.call_args.kwargs["receive_timeout"] == 60
