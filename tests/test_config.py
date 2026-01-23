from __future__ import annotations

from ldap_mcp.config import AuthMethod, LDAPMCPSettings


class TestLDAPMCPSettings:
    def test_default_values(self) -> None:
        settings = LDAPMCPSettings()

        assert settings.uri == ""
        assert settings.bind_dn == ""
        assert settings.bind_password == ""
        assert settings.base_dn == ""
        assert settings.auth_method == AuthMethod.SIMPLE
        assert settings.use_starttls is False
        assert settings.ca_cert is None
        assert settings.tls_verify is True
        assert settings.timeout == 30
        assert settings.default_filter == ""

    def test_default_filter_setting(self) -> None:
        settings = LDAPMCPSettings(default_filter="(!(status=terminated))")

        assert settings.default_filter == "(!(status=terminated))"

    def test_is_anonymous_with_anonymous_method(self) -> None:
        settings = LDAPMCPSettings(auth_method=AuthMethod.ANONYMOUS)

        assert settings.is_anonymous is True

    def test_is_anonymous_with_empty_bind_dn(self) -> None:
        settings = LDAPMCPSettings(bind_dn="")

        assert settings.is_anonymous is True

    def test_is_not_anonymous_with_bind_dn(self) -> None:
        settings = LDAPMCPSettings(bind_dn="cn=admin,dc=example,dc=com")

        assert settings.is_anonymous is False
