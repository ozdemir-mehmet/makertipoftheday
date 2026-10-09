---
title: "Power Pages will not save a child permission that has a role its parent lacks"
summary: "A child table permission must not carry a web role its parent permission does not have, and the designer refuses with a specific error rather than a warning."
surface: power-platform
tip_number: 8
state: draft
source: "https://learn.microsoft.com/en-us/power-pages/security/table-permissions"
next_step: "In a development site, give a child table permission a web role the parent does not have, capture the exact error from the designer, then align the roles and confirm the save."
---

**Tip**

Fix the parent, not the child. When a child table permission is associated with a web role that the
parent permission does not carry, the designer refuses to save and says so:

> One or more roles applied to this permission aren't available to its parent table permission.
> Modify roles in either permissions.

The rule behind it is the shape of table permissions: they are hierarchical, and a child permission
inherits its reach through the parent. A role on the child that the parent does not have would create
a path to the child's rows that the parent cannot describe, so the platform rejects it rather than
guessing what you meant. Deleting and re-creating the child permission does not help - the same roles
reproduce the same error, and the second attempt usually loses whatever else you had set on it.

Read the error as a statement about the parent: add the missing role to the parent permission, or
remove it from the child.

**Where this bites**

In a site with more than one audience. Someone adds a role to a child table so the new audience can
read one list, the save fails, and the change gets made on the parent instead - widening access to
everything the parent covers. The error is the last moment at which that is still visible.

**Try it**

Take the roles off a parent permission in a development site and try to save a child.
