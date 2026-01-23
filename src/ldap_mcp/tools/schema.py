"""LDAP schema browsing tool."""

from enum import Enum
from typing import Annotated

from fastmcp import Context
from fastmcp.tools import tool

from ldap_mcp.errors import handle_ldap_error
from ldap_mcp.models import SchemaAttributeType, SchemaInfo, SchemaObjectClass
from ldap_mcp.tools._context import get_app_context


class SchemaType(str, Enum):
    """Type of schema elements to retrieve."""

    OBJECT_CLASSES = "object_classes"
    ATTRIBUTE_TYPES = "attribute_types"
    ALL = "all"


@tool
async def ldap_get_schema(
    ctx: Context,
    schema_type: Annotated[
        SchemaType,
        "Type of schema to retrieve: object_classes, attribute_types, or all",
    ] = SchemaType.ALL,
    name_filter: Annotated[
        str | None,
        "Filter schema elements by name (case-insensitive substring match)",
    ] = None,
) -> SchemaInfo:
    """Browse LDAP schema definitions.

    Returns objectClasses and/or attributeTypes defined in the directory.
    """
    app = get_app_context(ctx)

    await ctx.debug(f"Getting schema: {schema_type.value}")

    try:
        schema = app.connection.server.schema
    except Exception as e:
        raise handle_ldap_error(e, "get_schema") from None

    if schema is None:
        from fastmcp.exceptions import ToolError

        raise ToolError("Schema not available from server")

    result = SchemaInfo()

    if schema_type in (SchemaType.OBJECT_CLASSES, SchemaType.ALL):
        for name, oc in schema.object_classes.items():
            if name_filter and name_filter.lower() not in name.lower():
                continue
            result.object_classes.append(
                SchemaObjectClass(
                    name=name,
                    oid=oc.oid,
                    description=oc.description[0] if oc.description else None,
                    superior=list(oc.superior) if oc.superior else [],
                    must=list(oc.must_contain) if oc.must_contain else [],
                    may=list(oc.may_contain) if oc.may_contain else [],
                )
            )

    if schema_type in (SchemaType.ATTRIBUTE_TYPES, SchemaType.ALL):
        for name, at in schema.attribute_types.items():
            if name_filter and name_filter.lower() not in name.lower():
                continue
            result.attribute_types.append(
                SchemaAttributeType(
                    name=name,
                    oid=at.oid,
                    description=at.description[0] if at.description else None,
                    syntax=at.syntax,
                    single_value=at.single_value or False,
                )
            )

    return result
