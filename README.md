# ldap-mcp

MCP server for read-only LDAP directory operations.

## Installation

```bash
pip install ldap-mcp
# or
uv add ldap-mcp
```

## Configuration

Set environment variables before running:

```bash
export LDAP_URI="ldaps://ldap.example.com:636"
export LDAP_BASE_DN="dc=example,dc=com"
export LDAP_BIND_DN="cn=readonly,dc=example,dc=com"
export LDAP_BIND_PASSWORD="secret"

# Optional: filter out terminated employees from all searches
export LDAP_DEFAULT_FILTER="(!(employeeStatus=terminated))"
```

### All Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LDAP_URI` | Yes | - | Server URI (ldap:// or ldaps://) |
| `LDAP_BASE_DN` | Yes | - | Default search base DN |
| `LDAP_BIND_DN` | No | - | Bind DN (empty = anonymous) |
| `LDAP_BIND_PASSWORD` | No | - | Bind password |
| `LDAP_DEFAULT_FILTER` | No | - | Filter ANDed to all searches |
| `LDAP_AUTH_METHOD` | No | `simple` | `simple` or `anonymous` |
| `LDAP_USE_STARTTLS` | No | `false` | Upgrade to TLS on port 389 |
| `LDAP_TLS_VERIFY` | No | `true` | Verify TLS certificates |
| `LDAP_CA_CERT` | No | - | Path to CA certificate |
| `LDAP_TIMEOUT` | No | `30` | Connection timeout (seconds) |

## Usage

Run the server:

```bash
ldap-mcp                    # stdio transport (default)
ldap-mcp --transport sse    # SSE transport
```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ldap": {
      "command": "ldap-mcp",
      "env": {
        "LDAP_URI": "ldaps://ldap.example.com:636",
        "LDAP_BASE_DN": "dc=example,dc=com",
        "LDAP_BIND_DN": "cn=readonly,dc=example,dc=com",
        "LDAP_BIND_PASSWORD": "secret"
      }
    }
  }
}
```

## Tools

### ldap_search

Search LDAP directory with filters.

```
filter: "(objectClass=person)"
base_dn: "ou=users,dc=example,dc=com"  # optional
scope: "subtree"  # base, one, or subtree
attributes: ["cn", "mail", "uid"]  # optional
size_limit: 100
```

### ldap_get_entry

Get a single entry by DN with all attributes.

```
dn: "cn=jdoe,ou=users,dc=example,dc=com"
attributes: ["*"]  # optional, defaults to all
include_operational: true  # include createTimestamp, etc.
```

### ldap_get_schema

Browse LDAP schema definitions.

```
schema_type: "all"  # object_classes, attribute_types, or all
name_filter: "person"  # optional substring filter
```

### ldap_compare

Compare an attribute value without retrieving the entry.

```
dn: "cn=jdoe,ou=users,dc=example,dc=com"
attribute: "memberOf"
value: "cn=admins,ou=groups,dc=example,dc=com"
```

## Prompts

### user_lookup

Guided workflow for finding users by name, email, or uid.

### group_members

List members of an LDAP group with optional name resolution.

### group_membership

Find all groups a user belongs to.

### search_guide

LDAP filter syntax reference with examples.

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run checks
make check    # lint + format + typecheck + test

# Run tests only
make test

# Auto-fix issues
make fix
```

## License

MIT
