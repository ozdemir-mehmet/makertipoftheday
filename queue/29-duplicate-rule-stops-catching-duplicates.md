---
title: "Your duplicate detection rule stopped catching duplicates the day someone lengthened a field"
summary: "A rule's matchcode is built when the rule is published; widen a criteria field later and that field can outrun the matchcode limit and go unverified, with no error and no duplicates found."
surface: dynamics-crm
tip_number: 29
state: draft
next_step: "In a development environment: publish a duplicate detection rule over a short text field, lengthen that field, create the near-duplicate that should match, and record whether detection fires; then unpublish and republish the rule and retest. That run is the only thing that can establish a fix - neither page states what restores verification after the field outruns the matchcode limit, and the criteria form's Current matchcode length value is documented only as an editing prompt."
source: "https://learn.microsoft.com/en-us/power-platform/admin/detect-duplicate-data"
---

You lengthen a text field that a duplicate detection rule matches on - a postcode column that needs four
more characters, a migration that widens everything - and the rule keeps running. It raises no error, it
flags nothing, it just stops finding duplicates.

The warning is one sentence on the page, and it is easy to read past:

> After publishing a duplicate detection rule, increasing the length of fields that are included in the
> duplicate detection criteria goes undetected. The field length could exceed the matchcode length limit
> and not be verified. This may result in duplicates not being detected.

Matchcodes are the reason the rule has a length limit at all: one is built when the rule is published and
when each record is written, and the criteria you can add are limited by how many characters fit in it.
Widen a field afterwards and its values can run past that limit, so the field drops out of verification,
with nothing on the rule to say a criterion left.

The page stops there. It does not say what restores verification: whether unpublishing and republishing
rebuilds the matchcodes to fit the widened field, whether the criterion has to change, or whether the field
stays unverified until it is shortened again. This draft carries no fix line until that is measured.
