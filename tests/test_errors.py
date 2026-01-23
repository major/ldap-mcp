"""Tests for LDAP error handling."""

from __future__ import annotations

import pytest
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

from ldap_mcp.errors import handle_ldap_error


class TestHandleLdapError:
    @pytest.mark.parametrize(
        ("exception", "expected_message"),
        [
            (LDAPBindError("bad creds"), "Authentication failed"),
            (LDAPSocketOpenError("no route"), "Cannot connect to LDAP server"),
            (LDAPNoSuchObjectResult("gone"), "Entry not found"),
            (LDAPInvalidFilterError("bad filter"), "Invalid LDAP filter syntax"),
            (LDAPSizeLimitExceededResult("too many"), "Size limit exceeded"),
            (LDAPTimeLimitExceededResult("too slow"), "Time limit exceeded"),
            (
                LDAPOperationResult(description="insufficientAccessRights", message="no write"),
                "LDAP operation failed",
            ),
            (LDAPException("generic ldap"), "LDAP error during"),
            (ValueError("random error"), "Error during"),
        ],
        ids=[
            "bind_error",
            "socket_error",
            "no_such_object",
            "invalid_filter",
            "size_limit",
            "time_limit",
            "operation_result",
            "generic_ldap",
            "unknown_error",
        ],
    )
    def test_maps_exception_to_tool_error(
        self, exception: Exception, expected_message: str
    ) -> None:
        result = handle_ldap_error(exception, "test_op")

        assert isinstance(result, ToolError)
        assert expected_message in str(result)

    def test_includes_operation_in_generic_error(self) -> None:
        result = handle_ldap_error(LDAPException("oops"), "my_operation")

        assert "my_operation" in str(result)

    def test_includes_details_in_socket_error(self) -> None:
        result = handle_ldap_error(LDAPSocketOpenError("connection refused"), "connect")

        assert "connection refused" in str(result)
