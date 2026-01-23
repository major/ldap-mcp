"""LDAP get entry tool."""

from typing import Annotated

from fastmcp import Context
from fastmcp.tools import tool
from ldap3 import BASE

from ldap_mcp.errors import handle_ldap_error
from ldap_mcp.models import LDAPEntry
from ldap_mcp.tools._context import get_app_context
from ldap_mcp.tools._helpers import entry_to_model, prepare_attributes


@tool
async def ldap_get_entry(
    ctx: Context,
    dn: Annotated[str, "Distinguished Name of the entry to retrieve"],
    attributes: Annotated[
        list[str] | None,
        "Specific attributes to return (default: all user attributes)",
    ] = None,
    include_operational: Annotated[
        bool,
        "Include operational attributes (createTimestamp, modifyTimestamp, etc.)",
    ] = False,
) -> LDAPEntry:
    """Get a single LDAP entry by DN with all attributes.

    Use this after ldap_search to get full details of a specific entry.
    """
    app = get_app_context(ctx)
    conn = app.connection
    attrs = prepare_attributes(attributes, ["*"], include_operational)

    await ctx.debug(f"Getting entry: {dn}")

    try:
        conn.search(
            search_base=dn,
            search_filter="(objectClass=*)",
            search_scope=BASE,
            attributes=attrs,
        )
    except Exception as e:
        raise handle_ldap_error(e, "get_entry") from None

    if not conn.entries:
        from fastmcp.exceptions import ToolError

        raise ToolError(f"Entry not found: {dn}")

    return entry_to_model(conn.entries[0])
