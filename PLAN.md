# ldap-mcp Development Plan

MCP server for LDAP directory operations using `ldap3` Python library.

## Status: Planning Complete ✓

---

## Design Decisions

### 1. Target LDAP Server(s)
**Generic LDAPv3** — should work with:
- Active Directory
- FreeIPA / Red Hat IdM
- OpenLDAP
- 389 Directory Server

No vendor-specific features initially. Keep tools generic and schema-agnostic.

### 2. Authentication Methods
- **Simple bind** (DN + password) — primary method
- **SASL/GSSAPI** (Kerberos) — for AD/FreeIPA environments with SSO
- **Anonymous bind** — for read-only browsing without credentials

### 3. Connection Security
- **LDAPS** (port 636) — TLS from connection start
- **StartTLS** (port 389) — upgrade plain connection to TLS
- **Plain LDAP** (port 389) — no encryption (dev/testing)
- **CA certificate** — custom CA cert path for validation
- **Skip TLS verify** — for self-signed certs in dev environments

### 4. Core Operations (Tools)
**Read-only operations only:**
- `ldap_search` — Search with LDAP filters
- `ldap_get_entry` — Get single entry by DN
- `ldap_get_schema` — Browse schema (objectClasses, attributeTypes)
- `ldap_compare` — Compare attribute value (returns true/false)

**No write operations** — this is a read-only MCP server.

### 5. Read-Only Mode
No `--get-muddy` flag needed. Server is read-only by design with no write tools.

### 6. Configuration
Environment variables:
```
LDAP_URI=ldaps://ldap.example.com:636      # Server URI
LDAP_BIND_DN=cn=readonly,dc=example,dc=com # Bind DN (optional for anon)
LDAP_BIND_PASSWORD=secret                   # Bind password
LDAP_BASE_DN=dc=example,dc=com              # Default search base
LDAP_USE_STARTTLS=false                     # Use StartTLS on plain connection
LDAP_CA_CERT=/path/to/ca.crt                # Custom CA cert path
LDAP_TLS_VERIFY=true                        # Verify TLS certificates
LDAP_TIMEOUT=30                             # Connection timeout (seconds)
LDAP_AUTH_METHOD=simple                     # simple | gssapi | anonymous
```

### 7. Response Format
**Flat dict** for token efficiency:
```json
{"dn": "cn=user,dc=example,dc=com", "cn": ["user"], "mail": ["user@example.com"]}
```

**Two-step workflow pattern:**
1. **Search** → returns summary (DN + requested attributes, defaults to common identifiers)
2. **Get entry by DN** → returns all attributes for deep inspection

This keeps search results compact, then allows drilling into specific entries.

Operational attributes (createTimestamp, modifyTimestamp, etc.) available via optional `include_operational=True` parameter on search/get tools.

### 8. Search Features
- **Raw LDAP filter syntax** — `(objectClass=person)`, `(&(cn=*admin*)(mail=*))`
- **Scope options** — base, one-level, subtree
- **Attribute selection** — return only specific attributes
- **Size limit** — cap results (e.g., max 1000 entries)
- **Time limit** — timeout for long searches

No pagination — size limit handles result control.

### 9. MCP Resources
None. Tools only — keeps it simple.

### 10. Error Handling
All scenarios get explicit handling with clear error messages:
- **Connection failures** — server down, network timeout
- **Authentication failures** — bad credentials, expired password
- **Authorization failures** — insufficient permissions
- **Referrals** — error out (don't follow)
- **Size/time limits exceeded** — server-side limits hit
- **Invalid filter syntax** — malformed LDAP filters
- **Entry not found** — DN doesn't exist

### 11. MCP Prompts
**Guided workflows with sensible defaults** — prompts handle the full search→inspect flow:

| Prompt | Workflow |
|--------|----------|
| `user_lookup` | 1. Search with `(\|(cn=*query*)(mail=query)(uid=query))` 2. Return summary (cn, mail, uid, title, department) 3. User picks entry → fetch full details |
| `group_members` | 1. Find group by name/DN 2. Extract member DNs 3. Optionally resolve members to names |
| `group_membership` | 1. Find user by name/DN 2. Search for groups containing user 3. Return list of groups |
| `search_guide` | Reference guide for LDAP filter syntax with examples (no searching, just education) |

Prompts will include instructions guiding the LLM through the two-step pattern.

---

## Architecture

### Project Structure

```
src/ldap_mcp/
├── __init__.py           # Public API + main() entry point
├── server.py             # FastMCP server setup + lifespan
├── config.py             # LDAPMCPSettings (pydantic-settings)
├── models.py             # Pydantic response models (LDAPEntry, SchemaInfo, etc.)
├── errors.py             # ldap3 -> MCP ToolError mapping
├── connection.py         # ldap3 connection factory (handles auth methods, TLS)
├── tools/
│   ├── __init__.py       # register_tools()
│   ├── search.py         # ldap_search tool
│   ├── entry.py          # ldap_get_entry tool
│   ├── schema.py         # ldap_get_schema tool
│   └── compare.py        # ldap_compare tool
└── prompts/
    ├── __init__.py       # register_prompts()
    └── helpers.py        # user_lookup, group_members, search_guide
```

### Tools Summary

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ldap_search` | Search with LDAP filters (summary view) | `filter`, `base_dn`, `scope`, `attributes` (default: cn, mail, uid), `size_limit`, `time_limit` |
| `ldap_get_entry` | Get single entry by DN (full details) | `dn`, `attributes`, `include_operational` |
| `ldap_get_schema` | Browse schema | `schema_type` (objectClasses, attributeTypes, or all) |
| `ldap_compare` | Compare attribute value | `dn`, `attribute`, `value` |

**Typical workflow:**
```
1. ldap_search(filter="(objectClass=person)", attributes=["cn", "mail", "uid"])
   → Returns list of entries with just DN + requested fields

2. ldap_get_entry(dn="cn=jdoe,ou=users,dc=example,dc=com")
   → Returns full entry with ALL attributes
```

### Prompts Summary

| Prompt | Description |
|--------|-------------|
| `user_lookup` | Guided workflow: search by name/email/uid → pick entry → get full details |
| `group_members` | Guided workflow: find group → list members → optionally resolve to names |
| `group_membership` | Guided workflow: find user → list groups they belong to |
| `search_guide` | Reference: LDAP filter syntax with examples |

---

## Dependencies

```toml
dependencies = [
    "fastmcp>=3.0.0b1",
    "ldap3>=2.9",
    "pydantic-settings>=2.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "pytest-asyncio>=0.25",
    "pytest-randomly>=4.0",
    "ruff>=0.9",
    "ty>=0.0.12",
]
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LDAP_URI` | LDAP server URI (ldap:// or ldaps://) | (required) |
| `LDAP_BIND_DN` | Bind DN for authentication | `""` (anonymous if empty) |
| `LDAP_BIND_PASSWORD` | Bind password | `""` |
| `LDAP_BASE_DN` | Default base DN for searches | (required) |
| `LDAP_AUTH_METHOD` | Auth method: `simple`, `gssapi`, `anonymous` | `simple` |
| `LDAP_USE_STARTTLS` | Use StartTLS on plain connection | `false` |
| `LDAP_CA_CERT` | Path to CA certificate | `""` |
| `LDAP_TLS_VERIFY` | Verify TLS certificates | `true` |
| `LDAP_TIMEOUT` | Connection timeout in seconds | `30` |

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Project structure matching porkbun-mcp
- [ ] Makefile with lint/format/typecheck/test targets
- [ ] pyproject.toml with full config (ruff, pytest, ty)
- [ ] Config via pydantic-settings (`config.py`)
- [ ] ldap3 connection factory (`connection.py`)
- [ ] Error mapping (`errors.py`)
- [ ] Pydantic models (`models.py`)
- [ ] FastMCP server with lifespan (`server.py`)
- [ ] Entry point (`__init__.py`)

### Phase 2: Core Tools
- [ ] `ldap_search` — full search with filters, scopes, limits
- [ ] `ldap_get_entry` — get single entry by DN
- [ ] `ldap_get_schema` — browse schema
- [ ] `ldap_compare` — compare attribute value

### Phase 3: Prompts
- [ ] `user_lookup` — find user by name/email
- [ ] `group_members` — list group members
- [ ] `group_membership` — list groups a user belongs to
- [ ] `search_guide` — LDAP filter syntax help

### Phase 4: Polish
- [x] Comprehensive tests (mocked ldap3)
- [x] AGENTS.md (agent guidelines)
- [x] README.md with usage examples
- [x] CI workflow (.github/workflows/ci.yml)
