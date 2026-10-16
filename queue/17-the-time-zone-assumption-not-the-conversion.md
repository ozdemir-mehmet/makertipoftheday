---
title: "The time zone bug in your flow is the assumption, not the conversion"
summary: "Find out which zone the datetime is already in before you convert it, then name that zone as the source: connectors differ, and the platform converts whatever you give it."
surface: power-platform
tip_number: 17
state: draft
source: "https://learn.microsoft.com/en-us/power-automate/convert-time-zone"
next_step: "In a development environment, run a flow over a connector that returns local time and one that returns UTC, log both raw values, then convert each with the Convert time zone action and with convertFromUtc/convertToUtc, and paste the before and after into the evidence block."
---

## The zone comes from the connector, not from your flow

A datetime arrives from a trigger or an action, and the zone it is in is the sending service's choice:
connectors differ in the formats and zones they work in, and some of them work only in UTC. Before you
convert anything, run the flow and read the datetime the action actually produced: a trailing `Z` is how a
UTC value shows itself, the way `2020-04-10T01:28:14.0406387Z` does in the guidance.

## The action asks you to name the source zone

Convert time zone, the built-in operation, takes the base time, a source time zone, a destination time zone
and an optional format string. The source time zone is the zone the datetime is currently in, and it is the
one input the platform cannot work out for itself, so it is the one worth checking against the raw value you
just read.

## The functions name the direction

When one end of the conversion is UTC, the expression functions carry the direction in their names:
`convertFromUtc` takes a UTC timestamp to a named zone, `convertToUtc` takes a timestamp in a named zone to
UTC. When you want both ends written out in the expression, `convertTimeZone` takes the source zone and the
destination zone:

    convertTimeZone(triggerBody()?['Date'],'UTC','Eastern Standard Time','HH:mm')

## An ISO8601 message is about the value, not the zone

An error saying the date time string must match ISO8601 format is about the shape of the value, so compare
the raw string against what the function expects before you change the zone.

## Some connectors show the zone their own way

A connector can carry its own limits on how the time zone displays, and the connector reference is where
each one's behaviour is written down.

Convert once, where the value crosses into storage or out to the consumer, and the step after it reads the
value you decided on rather than a value that moved again.
