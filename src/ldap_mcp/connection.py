"""LDAP connection factory using ldap3."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ldap3 import AUTO_BIND_TLS_BEFORE_BIND, SIMPLE, Connection, Server, Tls

if TYPE_CHECKING:
    from ldap_mcp.config import LDAPMCPSettings


def create_connection(settings: "LDAPMCPSettings") -> Connection:
    """Create an LDAP connection from settings.

    Args:
        settings: LDAP configuration settings.

    Returns:
        A bound LDAP connection ready for operations.

    Raises:
        LDAPException: If connection or binding fails.
    """
    tls_config = None
    if settings.uri.startswith("ldaps://") or settings.use_starttls:
        tls_config = Tls(
            validate=2 if settings.tls_verify else 0,
            ca_certs_file=str(settings.ca_cert) if settings.ca_cert else None,
        )

    server = Server(
        settings.uri,
        tls=tls_config,
        connect_timeout=settings.timeout,
    )

    auto_bind = AUTO_BIND_TLS_BEFORE_BIND if settings.use_starttls else True

    if settings.is_anonymous:
        return Connection(
            server,
            auto_bind=auto_bind,
            read_only=True,
            receive_timeout=settings.timeout,
        )

    return Connection(
        server,
        user=settings.bind_dn,
        password=settings.bind_password,
        authentication=SIMPLE,
        auto_bind=auto_bind,
        read_only=True,
        receive_timeout=settings.timeout,
    )
