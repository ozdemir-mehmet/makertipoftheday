---
title: "Your lookup column is a GUID because you forgot to ask for its name"
summary: "The Web API hands you `_primarycontactid_value` as a GUID unless you ask for annotations, and one request header puts the display name next to every lookup and option set."
surface: dataverse
tip_number: 26
state: draft
source: "https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query/overview"
next_step: "Run the same GET twice against a development environment with `$select=name,primarycontactid,statecode,statuscode`, once without and once with the annotation header set to the FormattedValue annotation, and paste both responses into the evidence block."
---

**Tip**

Ask for the annotation. The same GET, once with the header added:

    GET [Organization URI]/api/data/v9.2/accounts?$select=name,primarycontactid,statecode,statuscode
    Accept: application/json
    OData-MaxVersion: 4.0
    OData-Version: 4.0
    Prefer: odata.include-annotations="OData.Community.Display.V1.FormattedValue"

Without that header `primarycontactid` arrives as `_primarycontactid_value: "8f2c6a1e-…"` and
`statecode` as `0`. Both are correct and neither is useful: the GUID means nothing to a reviewer, and
`0` means nothing to anyone. With the header the same record carries the display name beside the
lookup and the label beside the integer, as separate `@OData.Community.Display.V1.FormattedValue`
properties that sit next to the values they describe rather than replacing them.

The library of annotations is large, so ask for the one you want. `"*"` returns all of them,
including the option-set and lookup detail you did not ask for, and the response grows accordingly.

**Where this bites**

In review. A GET that returns a wall of GUIDs reads as if the API cannot do better, so the query
gets rewritten as two calls - one for the record, one to resolve each lookup by hand. The header is
the difference between one round trip and N.

**Try it**

Run the request above against any development environment, then delete the `Prefer` line and run it
again. The values do not change; only the labels appear and disappear.
