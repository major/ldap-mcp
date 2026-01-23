"""Group membership prompt for finding groups a user belongs to."""

from typing import Annotated

from fastmcp.prompts import prompt


@prompt
def group_membership(
    user: Annotated[str, "Username, email, or DN of user to look up"],
) -> str:
    """Find all groups a user belongs to.

    This prompt guides you through finding a user and listing their group memberships.
    """
    return f"""Find group memberships for user: {user}

## Step 1: Find the user (if not already a DN)

If you have a username or email, first find the user's DN:

```
filter: (|(uid={user})(mail={user})(cn={user}))
attributes: ["dn", "cn", "mail", "uid"]
```

## Step 2: Search for groups containing this user

Use the user's DN to find groups where they are a member:

```
filter: (|(member=<user DN>)(uniqueMember=<user DN>))
attributes: ["cn", "description"]
```

For POSIX groups (using memberUid with username):

```
filter: (memberUid={user})
attributes: ["cn", "gidNumber", "description"]
```

## Step 3: Check for nested group memberships (optional)

In directories with nested groups, the user might be a member of groups
that are themselves members of other groups. To find these:

1. For each group found, search for groups containing that group's DN
2. Repeat until no new groups are found

## Active Directory specific

AD stores group membership in the user's memberOf attribute:

```
filter: (sAMAccountName={user})
attributes: ["memberOf", "cn", "mail"]
```

The memberOf attribute contains DNs of all groups (including nested via AD's
computed memberOf).

## Tips

- Some directories have a memberOf operational attribute on users
- Use include_operational=True with ldap_get_entry to see memberOf if available
- AD's "Primary Group" is stored differently (primaryGroupID) and won't appear in memberOf
"""
