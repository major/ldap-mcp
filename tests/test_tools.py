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
from ldap_mcp.tools.search import SearchScope, combine_filters, ldap_search


class TestLdapSearch:
    @pytest.mark.asyncio
    async def test_search_returns_entries(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        result = await ldap_search(mock_ctx, filter="(objectClass=person)")

        assert isinstance(result, SearchResult)
        assert result.total == 1
        assert len(result.entries) == 1
        assert result.entries[0].dn == "cn=jdoe,ou=users,dc=example,dc=com"
        mock_connection.search.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("base_dn", "expected"),
        [
            (None, "dc=example,dc=com"),
            ("ou=admins,dc=example,dc=com", "ou=admins,dc=example,dc=com"),
        ],
        ids=["default", "custom"],
    )
    async def test_search_base_dn(
        self,
        mock_ctx: MagicMock,
        mock_connection: MagicMock,
        base_dn: str | None,
        expected: str,
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", base_dn=base_dn)

        assert mock_connection.search.call_args.kwargs["search_base"] == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("scope", "expected"),
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
        expected: str,
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", scope=scope)

        assert mock_connection.search.call_args.kwargs["search_scope"] == expected

    @pytest.mark.asyncio
    async def test_search_with_attributes(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", attributes=["cn", "mail", "telephoneNumber"])

        assert mock_connection.search.call_args.kwargs["attributes"] == [
            "cn",
            "mail",
            "telephoneNumber",
        ]

    @pytest.mark.asyncio
    async def test_search_with_operational_attrs(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", include_operational=True)

        assert "+" in mock_connection.search.call_args.kwargs["attributes"]

    @pytest.mark.asyncio
    async def test_search_with_limits(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_search(mock_ctx, filter="(cn=*)", size_limit=50, time_limit=30)

        call_kwargs = mock_connection.search.call_args.kwargs
        assert call_kwargs["size_limit"] == 50
        assert call_kwargs["time_limit"] == 30

    @pytest.mark.asyncio
    async def test_search_empty_results(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_connection.entries = []

        result = await ldap_search(mock_ctx, filter="(cn=nonexistent)")

        assert result.total == 0
        assert result.entries == []

    @pytest.mark.asyncio
    async def test_search_applies_default_filter(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_ctx.lifespan_context.default_filter = "(!(status=terminated))"

        await ldap_search(mock_ctx, filter="(objectClass=person)")

        expected = "(&(objectClass=person)(!(status=terminated)))"
        assert mock_connection.search.call_args.kwargs["search_filter"] == expected


class TestCombineFilters:
    @pytest.mark.parametrize(
        ("user_filter", "default_filter", "expected"),
        [
            ("(cn=*)", "", "(cn=*)"),
            ("(cn=*)", "(!(status=terminated))", "(&(cn=*)(!(status=terminated)))"),
            ("(objectClass=person)", "(active=true)", "(&(objectClass=person)(active=true))"),
        ],
        ids=["no_default", "with_default", "complex"],
    )
    def test_combines_filters(self, user_filter: str, default_filter: str, expected: str) -> None:
        assert combine_filters(user_filter, default_filter) == expected


class TestLdapGetEntry:
    @pytest.mark.asyncio
    async def test_get_entry_returns_entry(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        result = await ldap_get_entry(mock_ctx, dn="cn=jdoe,ou=users,dc=example,dc=com")

        assert isinstance(result, LDAPEntry)
        assert result.dn == "cn=jdoe,ou=users,dc=example,dc=com"
        assert "cn" in result.attributes
        assert mock_connection.search.call_args.kwargs["search_scope"] == BASE

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

        assert "+" in mock_connection.search.call_args.kwargs["attributes"]

    @pytest.mark.asyncio
    async def test_get_entry_with_specific_attrs(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        await ldap_get_entry(
            mock_ctx,
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            attributes=["cn", "mail"],
        )

        assert mock_connection.search.call_args.kwargs["attributes"] == ["cn", "mail"]


class TestLdapCompare:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("expected_match", [True, False], ids=["match", "no_match"])
    async def test_compare_result(
        self, mock_ctx: MagicMock, mock_connection: MagicMock, expected_match: bool
    ) -> None:
        mock_connection.compare.return_value = expected_match

        result = await ldap_compare(
            mock_ctx,
            dn="cn=jdoe,ou=users,dc=example,dc=com",
            attribute="uid",
            value="jdoe",
        )

        assert isinstance(result, CompareResult)
        assert result.match is expected_match
        assert result.dn == "cn=jdoe,ou=users,dc=example,dc=com"
        assert result.attribute == "uid"

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
    @pytest.mark.parametrize(
        ("schema_type", "expected_oc_count", "expected_at_count"),
        [
            (SchemaType.OBJECT_CLASSES, 1, 0),
            (SchemaType.ATTRIBUTE_TYPES, 0, 1),
            (SchemaType.ALL, 1, 1),
        ],
    )
    async def test_get_schema_by_type(
        self,
        mock_ctx: MagicMock,
        schema_type: SchemaType,
        expected_oc_count: int,
        expected_at_count: int,
    ) -> None:
        result = await ldap_get_schema(mock_ctx, schema_type=schema_type)

        assert len(result.object_classes) == expected_oc_count
        assert len(result.attribute_types) == expected_at_count

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("name_filter", "expected_oc_count", "expected_at_count"),
        [
            ("person", 1, 0),
            ("PERSON", 1, 0),
            ("cn", 0, 1),
            ("nonexistent", 0, 0),
        ],
        ids=["lowercase", "uppercase", "attribute", "no_match"],
    )
    async def test_get_schema_name_filter(
        self,
        mock_ctx: MagicMock,
        name_filter: str,
        expected_oc_count: int,
        expected_at_count: int,
    ) -> None:
        result = await ldap_get_schema(mock_ctx, name_filter=name_filter)

        assert len(result.object_classes) == expected_oc_count
        assert len(result.attribute_types) == expected_at_count

    @pytest.mark.asyncio
    async def test_get_schema_unavailable(
        self, mock_ctx: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_connection.server.schema = None

        with pytest.raises(ToolError, match="Schema not available"):
            await ldap_get_schema(mock_ctx)
