"""Pytest configuration and fixtures."""

from __future__ import annotations

import pytest

from ldap_mcp.config import LDAPMCPSettings


@pytest.fixture
def mock_settings() -> LDAPMCPSettings:
    """Create test settings with mock values."""
    return LDAPMCPSettings(
        uri="ldap://localhost:389",
        bind_dn="cn=admin,dc=example,dc=com",
        bind_password="secret",
        base_dn="dc=example,dc=com",
    )
