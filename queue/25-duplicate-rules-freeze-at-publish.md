---
title: "Your duplicate detection rule stopped catching duplicates the day someone lengthened a field"
summary: "A published rule builds matchcodes from the criteria as they were at publish time; lengthening a field in that criteria later goes undetected, so the rule keeps running and quietly stops matching."
surface: dynamics-crm
tip_number: 25
state: draft
source: "https://learn.microsoft.com/en-us/power-platform/admin/detect-duplicate-data"
next_step: "In a development environment, publish a duplicate detection rule over a short text field, then lengthen that field and create a near-duplicate record to confirm whether the rule still fires, and paste both attempts into the evidence block."
---

**Tip**

Re-publish the rule after you touch the fields it matches on. The documented warning is easy to read
past:

> After publishing a duplicate detection rule, increasing the length of fields that are included in
> the duplicate detection criteria goes undetected. The field length could exceed the matchcode length
> limit and not be verified. This may result in duplicates not being detected.

The mechanism explains why: publishing a rule builds a matchcode for each existing record, and a
matchcode is also built when a record is created or updated. The matchcode is computed against the
field's length at that moment. Lengthen the field afterwards and the criteria and the matchcode no
longer agree, so the rule reports nothing - not an error, not a warning, just no duplicates. A rule
that has stopped working looks exactly like a table with no duplicates.

There is a ceiling worth knowing before you automate this: you can publish a maximum of five
duplicate detection rules per table type at one time. Extra rules have to be unpublished rather than
disabled, which is why the set on a mature table tends to be five long-lived rules and a spreadsheet
explaining them.

**Where this bites**

After a data migration or a schema change. Both add duplicates and change field lengths, in the same
window.
