---
title: "Your upsert returns 204 whether it created or updated a record"
summary: "A PATCH with `If-Match: *` is an upsert, and with no `Prefer` header the status is 204 No Content either way, so your sync code cannot tell an insert from an update."
surface: dataverse
tip_number: 27
state: draft
source: "https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-upsert-insert-update-record"
next_step: "PATCH the same alternate-key URL twice against a development environment, first without and then with `Prefer: return=representation`, and paste the status codes into the evidence block."
---

**Tip**

Add `Prefer: return=representation` to the upsert request. The documented behaviour:

> The request creates a new record if it doesn't find any records matching the keys in the URL.
> However, unlike the SDK, the response doesn't tell you whether it created a record. The status
> response is 204 No Content in either case. If you include a Prefer: return=representation request
> header, the system returns a 201 Created status for Create, and a 200 OK status for Update.

So a sync job that reports "1,204 records synchronised" is reporting the number of requests it made,
not the number of records it created. With the header, `201` means created and `200` means updated,
and you can count both honestly.

The header is not free: it adds a Retrieve to every request. Keep the `$select` you pair with it down
to the primary key value, and only switch it on for the runs where you need the distinction.

The URL for an upsert carries the alternate key, which is what makes the pattern useful for data
coming from a system that has never seen your GUIDs. Alternate keys are visible in the `$metadata`
annotations for the table, so you can discover them rather than guess.

**Try it**

Send the same upsert twice by hand. Without the header you get `204` twice. With it you get `201`
and then `200`.
