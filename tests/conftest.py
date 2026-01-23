"""Pytest configuration and fixtures."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ldap_mcp.config import LDAPMCPSettings
from ldap_mcp.server import AppContext


@pytest.fixture
def mock_settings() -> LDAPMCPSettings:
    """Create test settings with mock values."""
    return LDAPMCPSettings(
        uri="ldap://localhost:389",
        bind_dn="cn=admin,dc=example,dc=com",
        bind_password="secret",
        base_dn="dc=example,dc=com",
    )


@pytest.fixture
def mock_entry() -> MagicMock:
    """Create a mock LDAP entry with realistic attributes."""
    entry = MagicMock()
    entry.entry_dn = "cn=jdoe,ou=users,dc=example,dc=com"
    entry.entry_attributes = ["cn", "mail", "uid"]

    attr_values = {
        "cn": ["jdoe"],
        "mail": ["jdoe@example.com"],
        "uid": ["jdoe"],
    }

    def get_attr(key: str) -> MagicMock:
        attr = MagicMock()
        attr.values = attr_values[key]
        return attr

    entry.__getitem__ = lambda self, key: get_attr(key)
    return entry


@pytest.fixture
def mock_schema() -> MagicMock:
    """Create a mock LDAP schema with sample objectClass and attributeType."""
    schema = MagicMock()

    person_oc = MagicMock()
    person_oc.oid = "2.5.6.6"
    person_oc.description = ["Person object class"]
    person_oc.superior = ["top"]
    person_oc.must_contain = ["cn", "sn"]
    person_oc.may_contain = ["telephoneNumber", "mail"]

    cn_at = MagicMock()
    cn_at.oid = "2.5.4.3"
    cn_at.description = ["Common Name"]
    cn_at.syntax = "1.3.6.1.4.1.1466.115.121.1.15"
    cn_at.single_value = False

    schema.object_classes = {"person": person_oc}
    schema.attribute_types = {"cn": cn_at}
    return schema


@pytest.fixture
def mock_connection(mock_entry: MagicMock, mock_schema: MagicMock) -> MagicMock:
    """Create a mock LDAP connection with schema."""
    conn = MagicMock()
    conn.entries = [mock_entry]
    conn.search.return_value = True
    conn.compare.return_value = True
    conn.server.schema = mock_schema
    return conn


@pytest.fixture
def mock_app_context(mock_connection: MagicMock) -> AppContext:
    """Create a mock AppContext with connection."""
    return AppContext(connection=mock_connection, base_dn="dc=example,dc=com", default_filter="")


@pytest.fixture
def mock_ctx(mock_app_context: AppContext) -> MagicMock:
    """Create a mock FastMCP context."""
    ctx = MagicMock()
    ctx.lifespan_context = mock_app_context
    return ctx
