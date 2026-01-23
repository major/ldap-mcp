"""Error mapping from ldap3 to MCP ToolErrors."""

from __future__ import annotations

from fastmcp.exceptions import ToolError
from ldap3.core.exceptions import (
    LDAPBindError,
    LDAPException,
    LDAPInvalidFilterError,
    LDAPNoSuchObjectResult,
    LDAPOperationResult,
    LDAPSizeLimitExceededResult,
    LDAPSocketOpenError,
    LDAPTimeLimitExceededResult,
)


def handle_ldap_error(e: Exception, operation: str) -> ToolError:
    """Convert ldap3 exceptions to MCP ToolErrors."""
    match e:
        case LDAPBindError():
            return ToolError("Authentication failed. Check LDAP_BIND_DN and LDAP_BIND_PASSWORD.")
        case LDAPSocketOpenError():
            return ToolError(f"Cannot connect to LDAP server. Check LDAP_URI. Details: {e}")
        case LDAPNoSuchObjectResult():
            return ToolError(f"Entry not found: {e}")
        case LDAPInvalidFilterError():
            return ToolError(f"Invalid LDAP filter syntax: {e}")
        case LDAPSizeLimitExceededResult():
            return ToolError("Size limit exceeded. Use a more specific filter or reduce limit.")
        case LDAPTimeLimitExceededResult():
            return ToolError("Time limit exceeded. Use a more specific filter.")
        case LDAPOperationResult() as op:
            return ToolError(f"LDAP operation failed: {op.description} - {op.message}")
        case LDAPException():
            return ToolError(f"LDAP error during {operation}: {e}")
        case _:
            return ToolError(f"Error during {operation}: {e}")
