---
title: "Your canvas app is not showing the first 500 rows, it is showing the wrong answer"
summary: "One nondelegable operator in a Power Fx query makes the whole query local, so Power Apps reads the first 500 rows and filters those — silently, and with no error."
surface: power-platform
tip_number: 6
state: draft
source: "https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview"
next_step: "Point a development app at a table with more than 500 rows and 10 million is ideal but 5,000 will do, add a nondelegable operator such as `distinct` to the query, and compare the count the app shows against the same query in the data source."
---

**Tip**

Treat the delegation warning as a build failure, not a yellow squiggle. The documented rule is blunt:

> If any part of a query expression is nondelegable, Power Apps doesn't delegate any part of the
> query. When a query is nondelegable, Power Apps gets the first 500 records from the data source and
> then runs the actions in the query. You can increase this limit to 2,000 records.

The limit is the visible half. The invisible half is what the documentation's own example makes plain:
10 million records, a query over family names that start with Z, one nondelegable operator - and you
get the first 500 rows, filtered. The app renders, the gallery fills, the count looks plausible, and
the answer is wrong. There is no error state for this because from Power Apps' side nothing failed.

Delegability is per data source, not per app: Dataverse supports the `in` membership operator and
Excel does not, so the same expression that is safe against one table quietly degrades against
another.

**Where this bites**

In a demo with test data. Two hundred rows fit inside 500, so the query is correct until the day the
real table is bigger than the number.

**Try it**

Put a nondelegable operator in a query against a large table and watch the count change when you
remove it.
