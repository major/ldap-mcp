"""LDAP filter syntax reference guide."""

from fastmcp.prompts import prompt


@prompt
def search_guide() -> str:
    """LDAP filter syntax reference with examples.

    A comprehensive guide to LDAP search filter syntax for constructing queries.
    """
    return """# LDAP Filter Syntax Guide

## Basic Syntax

LDAP filters are enclosed in parentheses and use prefix notation:

```
(attribute=value)      # Equality
(attribute=*value*)    # Substring (contains)
(attribute=value*)     # Prefix (starts with)
(attribute=*value)     # Suffix (ends with)
(attribute=*)          # Presence (attribute exists)
(attribute>=value)     # Greater than or equal
(attribute<=value)     # Less than or equal
(attribute~=value)     # Approximate match
```

## Boolean Operators

Combine filters with AND, OR, and NOT:

```
(&(filter1)(filter2))     # AND - both must match
(|(filter1)(filter2))     # OR - either can match
(!(filter))               # NOT - must not match
```

## Common Examples

### Find users
```
(objectClass=person)
(objectClass=inetOrgPerson)
(&(objectClass=person)(uid=jdoe))
```

### Find by name
```
(cn=John Doe)             # Exact match
(cn=*john*)               # Contains "john" (case-insensitive in most dirs)
(|(cn=*smith*)(sn=smith)) # Name contains or surname equals "smith"
```

### Find by email
```
(mail=user@example.com)   # Exact email
(mail=*@example.com)      # All users in domain
```

### Find groups
```
(objectClass=groupOfNames)
(objectClass=posixGroup)
(&(objectClass=group)(cn=admins))  # AD group by name
```

### Find group members
```
(memberOf=cn=admins,ou=groups,dc=example,dc=com)  # Users in group (if memberOf supported)
```

### Complex queries
```
# Active users in IT department
(&(objectClass=person)(department=IT)(!(accountStatus=disabled)))

# Users created in 2024
(&(objectClass=person)(createTimestamp>=20240101000000Z))

# Users with email but no phone
(&(objectClass=person)(mail=*)(!(telephoneNumber=*)))
```

## Special Characters

Escape these characters in values:
- `*` -> `\\2a`
- `(` -> `\\28`
- `)` -> `\\29`
- `\\` -> `\\5c`
- NUL -> `\\00`

Example: `(cn=John \\28Jr\\29)` matches "John (Jr)"

## Tips

1. **Start broad, then narrow**: Begin with `(objectClass=person)` and add filters
2. **Use attributes list**: Request only needed attributes for faster searches
3. **Set size limits**: Avoid overwhelming results with `size_limit` parameter
4. **Check objectClass**: Different directory types use different objectClasses
5. **Case sensitivity**: Most directories are case-insensitive for common attributes
"""
