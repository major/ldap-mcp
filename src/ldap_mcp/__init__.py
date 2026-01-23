"""LDAP MCP Server - Directory operations via Model Context Protocol."""

from __future__ import annotations

import argparse


def main() -> None:
    """Run the LDAP MCP server."""
    parser = argparse.ArgumentParser(
        description="LDAP Directory MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  LDAP_URI              LDAP server URI (ldap:// or ldaps://)
  LDAP_BIND_DN          Bind DN for authentication (optional for anonymous)
  LDAP_BIND_PASSWORD    Bind password
  LDAP_BASE_DN          Default base DN for searches
  LDAP_AUTH_METHOD      Auth method: simple, anonymous (default: simple)
  LDAP_USE_STARTTLS     Use StartTLS on plain connection (default: false)
  LDAP_CA_CERT          Path to CA certificate
  LDAP_TLS_VERIFY       Verify TLS certificates (default: true)
  LDAP_TIMEOUT          Connection timeout in seconds (default: 30)
  LDAP_DEFAULT_FILTER   Filter ANDed to all searches (e.g., '(!(status=terminated))')

Examples:
  ldap-mcp                         # Default stdio transport
  ldap-mcp --transport sse         # SSE transport
""",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    args = parser.parse_args()

    from ldap_mcp.server import create_server

    server = create_server()
    server.run(transport=args.transport)


__all__ = ["main"]
