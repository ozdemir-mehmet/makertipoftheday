---
title: "You cannot block Dataverse with a DLP policy, and that is by design"
summary: "Dataverse is the only premium connector a data policy cannot block, because the platform depends on it — the block list has exceptions and advanced connector policies are the way round them."
surface: alm-governance
tip_number: 24
state: draft
source: "https://learn.microsoft.com/en-us/power-platform/admin/dlp-connector-classification"
next_step: "In a development tenant, create a data policy that classifies every connector as Blocked and confirm Dataverse remains usable, then repeat the attempt with advanced connector policies to see the difference."
---

**Tip**

Put connectors in groups, then find out which ones will not go where you put them. A data policy has
three groups by definition:

> The three data groups are the Business data group, the Non-Business data group, and the Blocked data
> group.

The exception list is the part worth reading before you promise anyone a lock-down:

> You can block all Microsoft-owned premium connectors, except Microsoft Dataverse. … you can't block
> connectors that drive core Microsoft Power Platform functionality, such as Dataverse, Approvals, and
> Notifications.

Dataverse is called out as the only premium connector that cannot be blocked, on the grounds that it
is an integral part of the platform. So "we block everything and allow-list nothing" is not a policy
you can express in a DLP policy - and the tenant that believes it has one has a gap where its most
important data lives.

If you actually need that control, the page points at the mechanism that has it: advanced connector
policies, which use a strict allow-list model.

**Try it**

Block everything in a development tenant and watch what still works. The answer is the list of things
your policy does not cover.
