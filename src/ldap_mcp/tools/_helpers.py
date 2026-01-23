"""Shared helpers for LDAP tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ldap_mcp.models import LDAPEntry

if TYPE_CHECKING:
    from collections.abc import Sequence


def entry_to_model(entry: Any) -> LDAPEntry:
    """Convert an ldap3 entry to an LDAPEntry model."""
    return LDAPEntry(
        dn=entry.entry_dn,
        attributes={attr: [str(v) for v in entry[attr].values] for attr in entry.entry_attributes},
    )


def prepare_attributes(
    attributes: Sequence[str] | None,
    default: Sequence[str],
    include_operational: bool,
) -> list[str]:
    """Prepare attribute list with optional operational attributes."""
    attrs = list(attributes) if attributes else list(default)
    if include_operational:
        attrs.append("+")
    return attrs
