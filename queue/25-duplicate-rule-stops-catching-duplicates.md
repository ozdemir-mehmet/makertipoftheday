---
title: "Your duplicate detection rule stopped catching duplicates the day someone lengthened a field"
summary: "A published rule builds its matchcodes at publish time; widen a field in its criteria later and that field can stop being verified, with no error and no duplicates found."
surface: dynamics-crm
tip_number: 25
state: draft
next_step: "In a development environment: publish a duplicate detection rule over a short text field, lengthen that field, then create a near-duplicate record and record whether detection fails; then republish the rule and retest, which settles whether republishing restores matching. Also record the exact duplicate dialog text, and whether a criterion over the first N characters behaves differently."
source: "https://learn.microsoft.com/en-us/power-platform/admin/detect-duplicate-data"
---

You lengthen a text field that a duplicate detection rule matches on - a postcode column that needs four
more characters, a migration that widens everything - and the rule keeps running. It raises no error, it
flags nothing, it just stops finding duplicates.

Microsoft puts the mechanism and the consequence on the same page, two paragraphs apart. The mechanism:

> When publishing a duplicate detection rule, a matchcode is created for each existing record. A
> matchcode is also created when a record is created or updated.

The consequence:

> After publishing a duplicate detection rule, increasing the length of fields that are included in the
> duplicate detection criteria goes undetected. The field length could exceed the matchcode length limit
> and not be verified. This may result in duplicates not being detected.

The page stops there. It says a lengthened criteria field could exceed the matchcode length limit, be
left unverified, and let duplicates through undetected. What it does not say is what restores verification:
whether republishing the rule rebuilds the matchcodes wide enough, or whether the criterion has to change.
No fix line goes in until that is measured - the tenant run in `next_step` is what decides it.
