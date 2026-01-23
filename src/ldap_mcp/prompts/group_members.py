"""Group members prompt for listing members of an LDAP group."""

from typing import Annotated

from fastmcp.prompts import prompt


@prompt
def group_members(
    group: Annotated[str, "Group name or DN to look up"],
    resolve_names: Annotated[bool, "Resolve member DNs to display names"] = True,
) -> str:
    """List members of an LDAP group.

    This prompt guides you through finding a group and listing its members.
    Optionally resolves member DNs to human-readable names.
    """
    resolve_instruction = ""
    if resolve_names:
        resolve_instruction = """
## Step 3: Resolve member names (optional)

For each member DN, use ldap_get_entry to get their display name:

```
dn: <member DN>
attributes: ["cn", "displayName", "mail"]
```
"""

    return f"""Find members of LDAP group: {group}

## Step 1: Find the group

If you have a group name (not a full DN), first search for the group:

```
filter: (&(objectClass=groupOfNames)(cn={group}))
attributes: ["cn", "member", "description"]
```

Alternative filters for different group types:
- POSIX groups: (&(objectClass=posixGroup)(cn={group}))
- AD groups: (&(objectClass=group)(cn={group}))
- groupOfUniqueNames: (&(objectClass=groupOfUniqueNames)(cn={group}))

## Step 2: Get group details and members

Use ldap_get_entry with the group's DN to get the full member list:

```
dn: <group DN from search>
attributes: ["member", "uniqueMember", "memberUid"]
```

The member attribute contains DNs of group members.
For POSIX groups, memberUid contains usernames instead.
{resolve_instruction}
## Tips

- Large groups may have many members - consider if you need all of them
- Some directories use "uniqueMember" instead of "member"
- Nested groups: member DNs might be other groups, not just users
"""
