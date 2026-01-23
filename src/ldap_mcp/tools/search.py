"""LDAP search tool."""

from enum import Enum
from typing import Annotated

from fastmcp import Context
from fastmcp.tools import tool
from ldap3 import BASE, LEVEL, SUBTREE

from ldap_mcp.errors import handle_ldap_error
from ldap_mcp.models import SearchResult
from ldap_mcp.tools._context import get_app_context
from ldap_mcp.tools._helpers import entry_to_model, prepare_attributes


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


def combine_filters(user_filter: str, default_filter: str) -> str:
    """Combine user filter with default filter using AND."""
    if not default_filter:
        return user_filter
    return f"(&{user_filter}{default_filter})"


@tool(timeout=60.0)
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
    attrs = prepare_attributes(attributes, DEFAULT_ATTRIBUTES, include_operational)
    search_filter = combine_filters(filter, app.default_filter)

    await ctx.debug(f"Searching {search_base} with filter {search_filter}")

    try:
        app.connection.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=SCOPE_MAP[scope],
            attributes=attrs,
            size_limit=size_limit,
            time_limit=time_limit,
        )
    except Exception as e:
        raise handle_ldap_error(e, "search") from None

    entries = [entry_to_model(entry) for entry in app.connection.entries]
    await ctx.info(f"Found {len(entries)} entries")
    return SearchResult(entries=entries, total=len(entries))
