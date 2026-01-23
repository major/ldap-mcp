# Agent Guidelines for ldap-mcp

## Project Overview

MCP server providing read-only LDAP directory operations. Built with FastMCP, ldap3, and pydantic-settings.

## Architecture

```
src/ldap_mcp/
├── __init__.py       # CLI entry point (argparse)
├── server.py         # FastMCP server + lifespan (AppContext)
├── config.py         # LDAPMCPSettings (env vars)
├── connection.py     # ldap3 connection factory
├── errors.py         # ldap3 -> ToolError mapping
├── models.py         # Pydantic response models
├── tools/            # MCP tools (search, get_entry, schema, compare)
└── prompts/          # MCP prompts (user_lookup, group_members, etc.)
```

## Key Patterns

### Context Flow
```
lifespan() → AppContext(connection, base_dn, default_filter)
    ↓
get_app_context(ctx) → extracts from request_context.lifespan_context
    ↓
tools use app.connection, app.base_dn, app.default_filter
```

### Error Handling
All ldap3 exceptions are mapped to `ToolError` in `errors.py`. Tools catch exceptions and call `handle_ldap_error()`.

### Filter Combination
User filters are combined with `default_filter` config using AND:
```python
combine_filters("(cn=*)", "(!(status=terminated))")
# → "(&(cn=*)(!(status=terminated)))"
```

## Development Commands

```bash
make check      # lint + format-check + typecheck + test
make test       # pytest with coverage
make fix        # auto-fix lint issues
```

## Testing Approach

- Mock ldap3 objects (Server, Connection, Entry)
- Use `conftest.py` fixtures for shared mocks
- Patch at the right level (e.g., `ldap_mcp.connection.Server`)
- Test error paths with explicit exception types

## Configuration (Environment Variables)

| Variable | Required | Description |
|----------|----------|-------------|
| `LDAP_URI` | Yes | Server URI (ldap:// or ldaps://) |
| `LDAP_BASE_DN` | Yes | Default search base |
| `LDAP_BIND_DN` | No | Bind DN (empty = anonymous) |
| `LDAP_BIND_PASSWORD` | No | Bind password |
| `LDAP_DEFAULT_FILTER` | No | Filter ANDed to all searches |
| `LDAP_AUTH_METHOD` | No | `simple` or `anonymous` |
| `LDAP_USE_STARTTLS` | No | Upgrade to TLS on port 389 |
| `LDAP_TLS_VERIFY` | No | Verify TLS certs (default: true) |
| `LDAP_CA_CERT` | No | Custom CA cert path |
| `LDAP_TIMEOUT` | No | Connection timeout seconds |

## Read-Only Design

This server is intentionally read-only. No write operations are implemented. Tools:
- `ldap_search` - Search with filters
- `ldap_get_entry` - Get single entry by DN
- `ldap_get_schema` - Browse schema
- `ldap_compare` - Compare attribute value
