"""User lookup prompt for guided user search workflow."""

from typing import Annotated

from fastmcp.prompts import prompt


@prompt
def user_lookup(
    query: Annotated[str, "Name, email, or uid to search for"],
) -> str:
    """Search for a user by name, email, or uid.

    This prompt guides you through a two-step lookup:
    1. Search with a flexible filter matching cn, mail, or uid
    2. Select an entry and retrieve full details

    Use ldap_search followed by ldap_get_entry to complete the lookup.
    """
    return f"""Find LDAP user matching: {query}

## Step 1: Search for the user

Use the ldap_search tool with a filter that matches common user attributes:

```
filter: (|(cn=*{query}*)(mail={query})(uid={query}))
attributes: ["cn", "mail", "uid", "title", "department"]
```

This filter searches for:
- cn (common name) containing "{query}"
- mail exactly matching "{query}"
- uid exactly matching "{query}"

## Step 2: Get full user details

Once you find matching entries, use ldap_get_entry with the DN of the
desired user to retrieve all their attributes:

```
dn: <selected user's DN from search results>
```

## Tips

- If searching by partial email, use: (mail=*{query}*)
- For exact name matches, use: (cn={query})
- Add (objectClass=person) or (objectClass=inetOrgPerson) to filter only user objects
"""
