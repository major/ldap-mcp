"""LDAP compare tool."""

from typing import Annotated

from fastmcp import Context
from fastmcp.tools import tool

from ldap_mcp.errors import handle_ldap_error
from ldap_mcp.models import CompareResult
from ldap_mcp.tools._context import get_app_context


@tool
async def ldap_compare(
    ctx: Context,
    dn: Annotated[str, "Distinguished Name of the entry"],
    attribute: Annotated[str, "Attribute name to compare"],
    value: Annotated[str, "Value to compare against"],
) -> CompareResult:
    """Compare an attribute value in an LDAP entry.

    Returns whether the attribute contains the specified value.
    Useful for checking group membership or attribute presence without retrieving full entry.
    """
    app = get_app_context(ctx)

    await ctx.debug(f"Comparing {attribute} for {dn}")

    try:
        result = app.connection.compare(dn, attribute, value)
    except Exception as e:
        raise handle_ldap_error(e, "compare") from None

    return CompareResult(
        dn=dn,
        attribute=attribute,
        match=result,
    )
