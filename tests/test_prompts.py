"""Tests for LDAP MCP prompts."""

from __future__ import annotations

import pytest

from ldap_mcp.prompts.group_members import group_members
from ldap_mcp.prompts.group_membership import group_membership
from ldap_mcp.prompts.search_guide import search_guide
from ldap_mcp.prompts.user_lookup import user_lookup


class TestUserLookup:
    @pytest.mark.parametrize(
        ("query", "expected_substrings"),
        [
            ("jdoe", ["jdoe", "ldap_search", "ldap_get_entry"]),
            ("admin", ["admin", "cn=*admin*", "(|"]),
            ("test@example.com", ["test@example.com", "ldap_get_entry"]),
        ],
        ids=["basic", "wildcard_filter", "email"],
    )
    def test_includes_query_and_tools(self, query: str, expected_substrings: list[str]) -> None:
        result = user_lookup(query)

        assert isinstance(result, str)
        for substring in expected_substrings:
            assert substring in result


class TestGroupMembers:
    @pytest.mark.parametrize(
        ("group", "expected_substrings"),
        [
            ("admins", ["admins", "objectClass=groupOfNames", "objectClass=posixGroup"]),
            ("developers", ["developers", "member", "uniqueMember"]),
        ],
        ids=["basic", "member_attrs"],
    )
    def test_includes_group_and_filters(self, group: str, expected_substrings: list[str]) -> None:
        result = group_members(group)

        assert isinstance(result, str)
        for substring in expected_substrings:
            assert substring in result

    @pytest.mark.parametrize(
        ("resolve_names", "expected", "not_expected"),
        [
            (True, "Resolve member names", None),
            (False, "member", "Step 3"),
        ],
        ids=["resolve_true", "resolve_false"],
    )
    def test_resolve_names_option(
        self, resolve_names: bool, expected: str, not_expected: str | None
    ) -> None:
        result = group_members("staff", resolve_names=resolve_names)

        assert expected in result
        if not_expected:
            assert not_expected not in result


class TestGroupMembership:
    @pytest.mark.parametrize(
        ("user", "expected_substrings"),
        [
            ("jdoe", ["jdoe", "member=", "uniqueMember="]),
            ("alice", ["alice", "memberUid="]),
            ("aduser", ["aduser", "Active Directory", "memberOf"]),
        ],
        ids=["basic", "posix", "active_directory"],
    )
    def test_includes_user_and_filters(self, user: str, expected_substrings: list[str]) -> None:
        result = group_membership(user)

        assert isinstance(result, str)
        for substring in expected_substrings:
            assert substring in result


@pytest.fixture
def guide_output() -> str:
    return search_guide()


class TestSearchGuide:
    @pytest.mark.parametrize(
        "expected_content",
        [
            "(attribute=value)",
            "(attribute=*)",
            "(&",  # AND
            "(|",  # OR
            "(!",  # NOT
            "\\2a",  # escaped *
            "\\28",  # escaped (
            "\\29",  # escaped )
            "objectClass=person",
            "objectClass=groupOfNames",
        ],
        ids=[
            "equality_syntax",
            "presence_syntax",
            "and_operator",
            "or_operator",
            "not_operator",
            "escape_asterisk",
            "escape_lparen",
            "escape_rparen",
            "person_example",
            "group_example",
        ],
    )
    def test_includes_expected_content(self, guide_output: str, expected_content: str) -> None:
        assert expected_content in guide_output
