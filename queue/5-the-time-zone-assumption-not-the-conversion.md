---
title: "The time zone bug in your flow is the assumption, not the conversion"
summary: "Connectors hand a flow datetimes in whichever zone they felt like, and the documented fix is naming the direction: `convertFromUtc` and `convertToUtc`."
surface: power-platform
tip_number: 5
state: draft
source: "https://learn.microsoft.com/en-us/power-automate/convert-time-zone"
next_step: "In a development environment, run a flow over a connector that returns local time and one that returns UTC, log both raw values, then convert each with `convertFromUtc` and paste the before and after into the evidence block."
---

**Tip**

Decide where the zone changes and do it in one place, with the function that names the direction.
`convertFromUtc` takes a UTC timestamp to a named zone and `convertToUtc` goes the other way; both are
documented alongside the Convert time zone action, and the reason to prefer the functions is that the
function name states which way the value is moving while the action's name does not.

The documented warning is the part worth pasting into a code review:

> Dates are passed through services in varying formats or time zones, so each connector might use a
> different datetime format or time zone. Some services strictly use UTC time to avoid confusion.

Read that again as an instruction: the format and the zone are properties of the connector, not of
the flow, so the same expression can be right in one flow and wrong in the next. A trigger that
returns a timestamp in UTC and a SharePoint column that returns one in the site's zone will both look
like "a date" in the run history, which is exactly why the bug survives review.

**Where this bites**

When the tenant is not in one zone. Everything looks correct to the maker who tested it until the
first user in Perth.

**Try it**

Log the raw value and the converted value in the same run, side by side, before anyone downstream
consumes it.
