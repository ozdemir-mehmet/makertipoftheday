---
title: "A OneLake shortcut is not a copy, and that is the whole point"
summary: "Shortcuts add selected data to the OneLake namespace without moving it; mirroring adds an external database or catalog and decides whether its data is read in place or replicated."
surface: fabric
tip_number: 9
state: draft
source: "https://learn.microsoft.com/en-us/fabric/onelake/unify-data"
next_step: "In a trial capacity, create a shortcut to a Dataverse table and, separately, mirror an external database, then compare storage consumed and data freshness for each."
---

**Tip**

Pick the mechanism by asking where the data is allowed to live. The documented difference is one
sentence:

> Shortcuts add selected data to the OneLake namespace. Mirroring adds an external database or catalog
> and determines whether its data can be accessed in place or must be replicated.

A shortcut is a reference: the bytes stay where they are and OneLake gains a name for them. Dataverse
is one of the documented sources you can shortcut - the platform lists Delta and Iceberg in Azure Data
Lake Storage, Amazon S3, Google Cloud Storage, or Dataverse - and shortcuts work at table, folder or
file level, so "make these twelve things visible" is expressible without copying anything.

Mirroring is the heavier commitment, and the sentence above is careful about why: it decides whether
the data is read in place or replicated. That decision is what you are actually choosing when you
choose mirroring, and it is the one that shows up later as storage and refresh questions.

**Where this bites**

When someone shortcuts a source and expects it to be a backup, or mirrors one and expects it to stay
free.

**Try it**

Shortcut an existing table and watch the source keep changing underneath it - that is the shortcut
working.
