"""LDAP schema browsing tool."""

from collections.abc import Callable, Iterable, Mapping
from enum import Enum
from typing import Annotated, Any

from fastmcp import Context
from fastmcp.tools import tool

from ldap_mcp.errors import handle_ldap_error
from ldap_mcp.models import SchemaAttributeType, SchemaInfo, SchemaObjectClass
from ldap_mcp.tools._context import get_app_context


def _filter_and_collect[T](
    items: Mapping[str, Any],
    name_filter: str | None,
    builder: Callable[[str, Any], T],
) -> list[T]:
    """Filter schema items by name and build model objects."""
    result: list[T] = []
    filter_lower = name_filter.lower() if name_filter else None
    for name, item in items.items():
        if filter_lower and filter_lower not in name.lower():
            continue
        result.append(builder(name, item))
    return result


def _build_object_class(name: str, oc: Any) -> SchemaObjectClass:
    """Build SchemaObjectClass from ldap3 ObjectClassInfo."""
    return SchemaObjectClass(
        name=name,
        oid=oc.oid,
        description=oc.description[0] if oc.description else None,
        superior=_to_list(oc.superior),
        must=_to_list(oc.must_contain),
        may=_to_list(oc.may_contain),
    )


def _build_attribute_type(name: str, at: Any) -> SchemaAttributeType:
    """Build SchemaAttributeType from ldap3 AttributeTypeInfo."""
    return SchemaAttributeType(
        name=name,
        oid=at.oid,
        description=at.description[0] if at.description else None,
        syntax=at.syntax,
        single_value=at.single_value or False,
    )


def _to_list(value: Iterable[str] | None) -> list[str]:
    """Convert optional iterable to list."""
    return list(value) if value else []


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
        result.object_classes = _filter_and_collect(
            schema.object_classes, name_filter, _build_object_class
        )

    if schema_type in (SchemaType.ATTRIBUTE_TYPES, SchemaType.ALL):
        result.attribute_types = _filter_and_collect(
            schema.attribute_types, name_filter, _build_attribute_type
        )

    return result
