---
title: "The pipelines host is also a solution archive, and nobody asked for that"
summary: "Every deployment through pipelines exports both the managed and the unmanaged solution and stores both in the pipelines host, so the host accumulates a copy of every version you have ever promoted."
surface: cross-cutting
tip_number: 23
state: draft
source: "https://learn.microsoft.com/en-us/power-platform/alm/pipelines"
next_step: "In a development environment with pipelines configured, deploy the same solution twice and list what lands in the pipelines host's solution history."
---

**Tip**

Read the pipelines host the way you would read any other environment, because it is one. The FAQ is
explicit:

> Both managed and unmanaged solutions are automatically exported and stored in the pipelines host for
> every deployment.

Two solutions per deployment, kept. The unmanaged export is the interesting half: it is the
maker-facing source of a version you already promoted, held in an environment that the makers usually
cannot see. It is not a backup feature and it was not designed as one, but it is the only place where
some of those versions exist at all.

The same FAQ answers the other question you were going to ask:

> Can customization bypass a deployment stage such as QA? No. Solutions are exported as soon as a
> deployment request is submitted … and the same

same solution moves through every stage. There is no skipping, so a pipeline's stage order is an
audit trail, not a suggestion.

**Where this bites**

In capacity. The host grows with every deployment and nothing prunes it, and the person who notices
is whoever is watching storage.

**Try it**

Count the solutions in the host's history after a month of deployments.
