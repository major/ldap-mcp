# ldap-mcp

**Commit:** d9e5863 | **Branch:** main

Read-only LDAP MCP server. FastMCP + ldap3 + pydantic-settings.

## Structure

```
src/ldap_mcp/
├── __init__.py       # CLI (argparse → create_server → run)
├── server.py         # FastMCP + lifespan → AppContext
├── config.py         # LDAPMCPSettings (LDAP_* env vars)
├── connection.py     # ldap3 factory (TLS, auth, read_only=True)
├── errors.py         # ldap3 exceptions → ToolError
├── models.py         # Pydantic: LDAPEntry, SearchResult, SchemaInfo
├── tools/
│   ├── _context.py   # get_app_context(ctx) → AppContext
│   ├── _helpers.py   # entry_to_model(), prepare_attributes()
│   ├── search.py     # ldap_search + combine_filters()
│   ├── entry.py      # ldap_get_entry
│   ├── schema.py     # ldap_get_schema
│   └── compare.py    # ldap_compare
└── prompts/          # Guided workflows (user_lookup, group_*)
```

## Where to Look

| Task | Location |
|------|----------|
| Add env config | `config.py` → add Field to LDAPMCPSettings |
| Add new tool | `tools/` → new file + register in `tools/__init__.py` |
| Add new prompt | `prompts/` → new file + register in `prompts/__init__.py` |
| Map ldap3 error | `errors.py` → add case to handle_ldap_error() |
| Modify search behavior | `tools/search.py` → combine_filters(), ldap_search() |

## Context Flow

```
lifespan() → AppContext(connection, base_dn, default_filter)
     ↓
get_app_context(ctx) → extracts from request_context.lifespan_context
     ↓
tools use: app.connection, app.base_dn, app.default_filter
```

## Anti-Patterns

| ❌ NEVER | Why |
|----------|-----|
| Implement write operations | Read-only by design. `read_only=True` enforced in connection.py |
| Use `from __future__ import annotations` in tools/prompts | Breaks FastMCP Annotated type evaluation at runtime |
| Let ldap3 exceptions bubble up | Always use `handle_ldap_error(e, "operation")` |
| Create connections in tools | Use `app.connection` from AppContext |
| Skip filter combination | User filters must AND with `app.default_filter` |

## Conventions

| Pattern | Implementation |
|---------|----------------|
| Filter combination | `(&{user_filter}{default_filter})` via `combine_filters()` |
| Tool error handling | `try: ... except Exception as e: raise handle_ldap_error(e, "op") from None` |
| Private modules | Prefix with `_` (e.g., `_context.py`, `_helpers.py`) |
| Async tools | All tools are `async def` even if sync internally |
| Default search attrs | `["cn", "mail", "uid"]` — keep responses compact |

## Testing

```bash
make check   # lint + format + typecheck + test (95% coverage)
make test    # pytest only
make fix     # auto-fix lint/format
```

**Mocking pattern:**
```python
# Patch at module level, not ldap3 level
with patch("ldap_mcp.connection.Server") as mock:
    ...
```

**Fixtures:** `tests/conftest.py` provides `mock_connection`, `mock_ctx`, `mock_entry`, `mock_schema`

## Config

| Variable | Required | Notes |
|----------|----------|-------|
| `LDAP_URI` | Yes | ldap:// or ldaps:// |
| `LDAP_BASE_DN` | Yes | Default search base |
| `LDAP_BIND_DN` | No | Empty = anonymous |
| `LDAP_DEFAULT_FILTER` | No | ANDed to all searches (e.g., `(!(status=terminated))`) |
| `LDAP_USE_STARTTLS` | No | Upgrade plain → TLS |
| `LDAP_TLS_VERIFY` | No | Default: true |

## Tools (4 only)

| Tool | Purpose |
|------|---------|
| `ldap_search` | Search with filters, returns summary |
| `ldap_get_entry` | Get full entry by DN |
| `ldap_get_schema` | Browse objectClasses/attributeTypes |
| `ldap_compare` | Compare attribute value (returns bool) |

Two-step workflow: `ldap_search` (find) → `ldap_get_entry` (details)
