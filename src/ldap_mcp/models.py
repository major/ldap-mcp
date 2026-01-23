"""Pydantic response models for LDAP operations."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LDAPEntry(BaseModel):
    """A single LDAP directory entry."""

    dn: str = Field(description="Distinguished Name")
    attributes: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Entry attributes (all values are lists)",
    )


class SearchResult(BaseModel):
    """Result of an LDAP search operation."""

    entries: list[LDAPEntry] = Field(default_factory=list, description="Matching entries")
    total: int = Field(description="Number of entries returned")


class CompareResult(BaseModel):
    """Result of an LDAP compare operation."""

    dn: str = Field(description="Distinguished Name that was compared")
    attribute: str = Field(description="Attribute that was compared")
    match: bool = Field(description="Whether the value matched")


class SchemaObjectClass(BaseModel):
    """An LDAP objectClass definition."""

    name: str = Field(description="objectClass name")
    oid: str = Field(description="Object identifier")
    description: str | None = Field(default=None, description="Human-readable description")
    superior: list[str] = Field(default_factory=list, description="Parent objectClasses")
    must: list[str] = Field(default_factory=list, description="Required attributes")
    may: list[str] = Field(default_factory=list, description="Optional attributes")


class SchemaAttributeType(BaseModel):
    """An LDAP attributeType definition."""

    name: str = Field(description="Attribute name")
    oid: str = Field(description="Object identifier")
    description: str | None = Field(default=None, description="Human-readable description")
    syntax: str | None = Field(default=None, description="Syntax OID")
    single_value: bool = Field(default=False, description="Whether single-valued")


class SchemaInfo(BaseModel):
    """LDAP schema information."""

    object_classes: list[SchemaObjectClass] = Field(
        default_factory=list,
        description="Available objectClasses",
    )
    attribute_types: list[SchemaAttributeType] = Field(
        default_factory=list,
        description="Available attributeTypes",
    )
