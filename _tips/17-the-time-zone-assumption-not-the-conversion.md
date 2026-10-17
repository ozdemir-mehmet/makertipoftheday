---
title: "The time zone bug in your flow is the assumption, not the conversion"
summary: "Find out which zone the datetime is already in before you convert it, then name that zone as the source: connectors differ, and the action converts from the zone you name."
surface: power-platform
tip_number: 17
date: 2026-10-17
source: "https://learn.microsoft.com/en-us/power-automate/convert-time-zone"
artifact: none
wave: "n/a - documentation-based tip; the mechanism is a flow run in a tenant this machine cannot reach, so nothing was executed"
build: "Power Automate's Convert a time zone page and the workflow expression function reference, both fetched 2026-10-17"
verified_on: 2026-10-17
verified_env: "No environment and no login - the two Learn pages fetched with curl on 2026-10-17; no flow was run"
expires_on: 2027-04-17
cost: "Free to read; running the flow needs a Power Automate licence the reader may already hold"
evidence: |
  Documentation read on 2026-10-17 and nothing executed: this machine has no pac and no az CLI, so no
  Power Automate environment was reachable and no flow was run. Both sources fetched with curl the same day.

      $ curl -sL -o /tmp/c17.html -w 'http %{http_code} bytes %{size_download}\n' \
          https://learn.microsoft.com/en-us/power-automate/convert-time-zone

  observed: http 200 bytes 53624, title "Convert a time zone", "Last updated on 2026-08-19". The page
  opens with an authorization banner and still returns the whole article, judged by byte count and by the
  sections present, not by the banner.

      $ curl -sL -o /tmp/wdl.html -w 'http %{http_code} bytes %{size_download}\n' \
          https://learn.microsoft.com/en-us/azure/logic-apps/workflow-definition-language-functions-reference

  observed: http 200 bytes 312256.

  From convert-time-zone, in page order, quoted whole:

      Dates are passed through services in varying formats or time zones, so each connector might use a different datetime format or time zone. Some services strictly use UTC time to avoid confusion.

      Base time : The datetime you wish to convert.
      Source time zone : The time zone that the datetime is currently in.
      Destination time zone : The time zone you want to convert your date to.
      Format string (Optional) : The string that specifies the desired format of the converted time.

      If your datetime has a Z at the end, it means it's in UTC time.
      Example : 2020-04-10T01:28:14.0406387Z
      You might receive an error that states your date time string isn't in the correct format.
      Example : 'The date time string must match ISO8601 format.'
      If you're unsure what format the datetime time zone is currently in, you can run your flow and see the datetime output format.
      To convert a timestamp from the source time zone to UTC, or from UTC to the target time zone, use the convertFromUtc and convertToUtc expression functions.
      Some connectors have limitations in how the time zone displays.

  The page's own expression example, quoted whole:

      convertTimeZone(triggerBody()?['Date'],'UTC','Eastern Standard Time','HH:mm')

  From the functions reference, each function's opening sentence:

      convertFromUtc - Convert a timestamp from Universal Time Coordinated (UTC) to the target time zone.
      convertToUtc - Convert a timestamp from the source time zone to Universal Time Coordinated (UTC).
      convertTimeZone - Convert a timestamp from the source time zone to the target time zone.

  The same reference, on the source and destination zone names, quoted whole:

      For time zone names, see Microsoft Windows Default Time Zones , but you might have to remove any punctuation from the time zone name.

  Two inferences were cut rather than dressed as sourced. An earlier draft called the source zone the one
  input the platform cannot work out for itself, and said the zone names are not IANA ones. Neither page
  says either, so the body states the definitional facts and leaves the reasoning to the reader.
---

## The zone comes from the connector, not from your flow

A datetime arrives from a trigger or an action, and the zone it is in is the sender's choice: connectors
differ in the formats and zones they use, and some services work strictly in UTC to avoid confusion. A
trailing `Z` is how a UTC value shows itself, the way `2020-04-10T01:28:14.0406387Z` does in the guidance.
When you are unsure what format the datetime is in, running the flow and reading what the action produced
is what Microsoft points you at, and it answers the question the conversion depends on.

## The action asks you to name the source zone

Convert time zone, the built-in operation, takes a base time, a source time zone, a destination time zone
and an optional format string. The source time zone is the zone the datetime is currently in, which means
the value you already have rather than the zone you want it to end up in. That input describes the raw
value, so read it off the output the action printed instead of filling it in from memory.

## The functions name the direction

When one end of a conversion is UTC, the function name carries the direction: `convertFromUtc` converts a
UTC timestamp to a target zone, and `convertToUtc` converts a timestamp in a named zone to UTC. When both
ends need writing out, `convertTimeZone` takes the source zone and the destination zone:

    convertTimeZone(triggerBody()?['Date'],'UTC','Eastern Standard Time','HH:mm')

The zone names are the Windows ones, listed under Microsoft Windows Default Time Zones in the reference,
and a name can need its punctuation removed before the function accepts it.

## An ISO8601 message is about the value, not the zone

The error the guidance shows as its example is that the date time string must match ISO8601 format. That
names the shape of the string you passed rather than the zone you picked, so compare the raw value's format
against what the function takes before you change anything about the conversion.

## Some connectors show the zone their own way

Some connectors have limitations in how the time zone displays, and the connector reference is where each
one's behaviour is written down. The datetime an action hands you is that connector's output, so the source
zone you name belongs to the action you took the value from.
