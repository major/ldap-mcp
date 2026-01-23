"""Configuration for the LDAP MCP server."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthMethod(str, Enum):
    """LDAP authentication methods."""

    SIMPLE = "simple"
    ANONYMOUS = "anonymous"


class LDAPMCPSettings(BaseSettings):
    """Configuration for the LDAP MCP server.

    Attributes:
        uri: LDAP server URI (ldap:// or ldaps://).
        bind_dn: Bind DN for authentication (optional for anonymous).
        bind_password: Bind password.
        base_dn: Default base DN for searches.
        auth_method: Authentication method (simple, gssapi, anonymous).
        use_starttls: Use StartTLS on plain connection.
        ca_cert: Path to CA certificate for TLS validation.
        tls_verify: Verify TLS certificates.
        timeout: Connection timeout in seconds.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LDAP_",
        extra="ignore",
    )

    uri: str = Field(default="", description="LDAP server URI (ldap:// or ldaps://)")
    bind_dn: str = Field(default="", description="Bind DN for authentication")
    bind_password: str = Field(default="", description="Bind password")
    base_dn: str = Field(default="", description="Default base DN for searches")
    auth_method: AuthMethod = Field(
        default=AuthMethod.SIMPLE,
        description="Authentication method",
    )
    use_starttls: bool = Field(default=False, description="Use StartTLS on plain connection")
    ca_cert: Path | None = Field(default=None, description="Path to CA certificate")
    tls_verify: bool = Field(default=True, description="Verify TLS certificates")
    timeout: int = Field(default=30, ge=1, description="Connection timeout in seconds")
    default_filter: str = Field(
        default="",
        description="Default filter ANDed to all searches (e.g., '(!(employeeStatus=terminated))')",
    )

    @property
    def is_anonymous(self) -> bool:
        """Check if using anonymous authentication."""
        return self.auth_method == AuthMethod.ANONYMOUS or not self.bind_dn
