"""LDAP search tool."""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from fastmcp import Context
from ldap3 import BASE, LEVEL, SUBTREE

from ldap_mcp.errors import handle_ldap_error
from ldap_mcp.models import LDAPEntry, SearchResult
from ldap_mcp.tools._context import get_app_context


class SearchScope(str, Enum):
    """LDAP search scope."""

    BASE = "base"
    ONE = "one"
    SUBTREE = "subtree"


SCOPE_MAP = {
    SearchScope.BASE: BASE,
    SearchScope.ONE: LEVEL,
    SearchScope.SUBTREE: SUBTREE,
}

DEFAULT_ATTRIBUTES = ["cn", "mail", "uid"]


async def ldap_search(
    ctx: Context,
    filter: Annotated[str, "LDAP filter (e.g., '(objectClass=person)')"],
    base_dn: Annotated[str | None, "Base DN for search (uses default if not specified)"] = None,
    scope: Annotated[SearchScope, "Search scope: base, one, or subtree"] = SearchScope.SUBTREE,
    attributes: Annotated[
        list[str] | None,
        "Attributes to return (defaults to cn, mail, uid)",
    ] = None,
    size_limit: Annotated[int, "Maximum entries to return (0 = no limit)"] = 100,
    time_limit: Annotated[int, "Search timeout in seconds (0 = no limit)"] = 0,
    include_operational: Annotated[
        bool,
        "Include operational attributes (createTimestamp, modifyTimestamp, etc.)",
    ] = False,
) -> SearchResult:
    """Search LDAP directory with filters.

    Returns a summary view with DN and requested attributes.
    Use ldap_get_entry for full details of a specific entry.
    """
    app = get_app_context(ctx)
    search_base = base_dn or app.base_dn
    attrs = attributes or DEFAULT_ATTRIBUTES

    if include_operational:
        attrs = [*attrs, "+"]

    try:
        app.connection.search(
            search_base=search_base,
            search_filter=filter,
            search_scope=SCOPE_MAP[scope],
            attributes=attrs,
            size_limit=size_limit,
            time_limit=time_limit,
        )
    except Exception as e:
        raise handle_ldap_error(e, "search") from None

    entries = [
        LDAPEntry(
            dn=entry.entry_dn,
            attributes={
                attr: [str(v) for v in entry[attr].values] for attr in entry.entry_attributes
            },
        )
        for entry in app.connection.entries
    ]

    return SearchResult(entries=entries, total=len(entries))
