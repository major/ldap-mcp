"""Tests for LDAP MCP tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastmcp.exceptions import ToolError
from ldap3 import BASE, LEVEL, SUBTREE

from ldap_mcp.models import CompareResult, LDAPEntry, SchemaInfo, SearchResult
from ldap_mcp.tools.compare import ldap_compare
from ldap_mcp.tools.entry import ldap_get_entry
from ldap_mcp.tools.schema import SchemaType, ldap_get_schema
from ldap_mcp.tools.search import SearchScope, ldap_search


class TestLdapSearch:
    @pytest.mark.asyncio
    async def test_search_basic(self, mock_ctx: MagicMock, mock_connection: MagicMock) -> None:
        result = await ldap_search(mock_ctx, filter="(objectClass=person)")

        assert isinstance(result, SearchResult)
        assert result.total == 1
        assert len(result.entries) == 1
        assert result.entries[0].dn == "cn=jdoe,ou=users,dc=example,dc=com"
        mock_connection.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_custom_base_dn(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", base_dn="ou=admins,dc=example,dc=com")

        call_args = mock_connection.search.call_args
        assert call_args.kwargs["search_base"] == "ou=admins,dc=example,dc=com"

    @pytest.mark.asyncio
    async def test_search_uses_default_base_dn(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)")

        call_args = mock_connection.search.call_args
        assert call_args.kwargs["search_base"] == "dc=example,dc=com"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("scope", "expected_ldap3_scope"),
        [
            (SearchScope.BASE, BASE),
            (SearchScope.ONE, LEVEL),
            (SearchScope.SUBTREE, SUBTREE),
        ],
    )
    async def test_search_scopes(
        self,
        mock_ctx: MagicMock,
        mock_connection: MagicMock,
        scope: SearchScope,
        expected_ldap3_scope: str,
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", scope=scope)

        call_args = mock_connection.search.call_args
        assert call_args.kwargs["search_scope"] == expected_ldap3_scope

    @pytest.mark.asyncio
    async def test_search_with_attributes(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", attributes=["cn", "mail", "telephoneNumber"])

        call_args = mock_connection.search.call_args
        assert call_args.kwargs["attributes"] == ["cn", "mail", "telephoneNumber"]

    @pytest.mark.asyncio
    async def test_search_with_operational_attrs(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", include_operational=True)

        call_args = mock_connection.search.call_args
        assert "+" in call_args.kwargs["attributes"]

    @pytest.mark.asyncio
    async def test_search_with_limits(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", size_limit=50, time_limit=30)

        call_args = mock_connection.search.call_args
        assert call_args.kwargs["size_limit"] == 50
        assert call_args.kwargs["time_limit"] == 30

    @pytest.mark.asyncio
    async def test_search_empty_results(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_connection.entries = []

        result = await ldap_search(mock_ctx, filter="(cn=nonexistent)")

        assert result.total == 0
        assert result.entries == []


class TestLdapGetEntry:
    @pytest.mark.asyncio
    async def test_get_entry_basic(self, mock_ctx: MagicMock, mock_connection: MagicMock) -> None:
        result = await ldap_get_entry(mock_ctx, dn="cn=jdoe,ou=users,dc=example,dc=com")

        assert isinstance(result, LDAPEntry)
        assert result.dn == "cn=jdoe,ou=users,dc=example,dc=com"
        assert "cn" in result.attributes

    @pytest.mark.asyncio
    async def test_get_entry_uses_base_scope(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_get_entry(mock_ctx, dn="cn=jdoe,ou=users,dc=example,dc=com")

        call_args = mock_connection.search.call_args
        assert call_args.kwargs["search_scope"] == BASE

    @pytest.mark.asyncio
    async def test_get_entry_not_found(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_connection.entries = []

        with pytest.raises(ToolError, match="Entry not found"):
            await ldap_get_entry(mock_ctx, dn="cn=nonexistent,dc=example,dc=com")

    @pytest.mark.asyncio
    async def test_get_entry_with_operational_attrs(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_get_entry(
            mock_ctx,
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            include_operational=True,
        )

        call_args = mock_connection.search.call_args
        assert "+" in call_args.kwargs["attributes"]

    @pytest.mark.asyncio
    async def test_get_entry_with_specific_attrs(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_get_entry(
            mock_ctx,
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            attributes=["cn", "mail"],
        )

        call_args = mock_connection.search.call_args
        assert call_args.kwargs["attributes"] == ["cn", "mail"]


class TestLdapCompare:
    @pytest.mark.asyncio
    async def test_compare_match(self, mock_ctx: MagicMock, mock_connection: MagicMock) -> None:
        mock_connection.compare.return_value = True

        result = await ldap_compare(
            mock_ctx,
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            attribute="uid",
            value="jdoe",
        )

        assert isinstance(result, CompareResult)
        assert result.match is True
        assert result.dn == "cn=jdoe,ou=users,dc=example,dc=com"
        assert result.attribute == "uid"

    @pytest.mark.asyncio
    async def test_compare_no_match(self, mock_ctx: MagicMock, mock_connection: MagicMock) -> None:
        mock_connection.compare.return_value = False

        result = await ldap_compare(
            mock_ctx,
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            attribute="uid",
            value="wrong",
        )

        assert result.match is False

    @pytest.mark.asyncio
    async def test_compare_calls_connection(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_compare(
            mock_ctx,
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            attribute="memberOf",
            value="cn=admins,ou=groups,dc=example,dc=com",
        )

        mock_connection.compare.assert_called_once_with(
            "cn=jdoe,ou=users,dc=example,dc=com",
            "memberOf",
            "cn=admins,ou=groups,dc=example,dc=com",
        )


class TestLdapGetSchema:
    @pytest.mark.asyncio
    async def test_get_schema_all(self, mock_ctx: MagicMock) -> None:
        result = await ldap_get_schema(mock_ctx)

        assert isinstance(result, SchemaInfo)
        assert len(result.object_classes) == 1
        assert len(result.attribute_types) == 1
        assert result.object_classes[0].name == "person"
        assert result.attribute_types[0].name == "cn"

    @pytest.mark.asyncio
    async def test_get_schema_object_classes_only(self, mock_ctx: MagicMock) -> None:
        result = await ldap_get_schema(mock_ctx, schema_type=SchemaType.OBJECT_CLASSES)

        assert len(result.object_classes) == 1
        assert len(result.attribute_types) == 0

    @pytest.mark.asyncio
    async def test_get_schema_attribute_types_only(self, mock_ctx: MagicMock) -> None:
        result = await ldap_get_schema(mock_ctx, schema_type=SchemaType.ATTRIBUTE_TYPES)

        assert len(result.object_classes) == 0
        assert len(result.attribute_types) == 1

    @pytest.mark.asyncio
    async def test_get_schema_with_name_filter(self, mock_ctx: MagicMock) -> None:
        result = await ldap_get_schema(mock_ctx, name_filter="person")

        assert len(result.object_classes) == 1
        assert len(result.attribute_types) == 0

    @pytest.mark.asyncio
    async def test_get_schema_name_filter_case_insensitive(self, mock_ctx: MagicMock) -> None:
        result = await ldap_get_schema(mock_ctx, name_filter="PERSON")

        assert len(result.object_classes) == 1

    @pytest.mark.asyncio
    async def test_get_schema_no_match(self, mock_ctx: MagicMock) -> None:
        result = await ldap_get_schema(mock_ctx, name_filter="nonexistent")

        assert len(result.object_classes) == 0
        assert len(result.attribute_types) == 0

    @pytest.mark.asyncio
    async def test_get_schema_unavailable(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_connection.server.schema = None

        with pytest.raises(ToolError, match="Schema not available"):
            await ldap_get_schema(mock_ctx)
