---
title: "Your Direct Lake model is running as DirectQuery and nothing told you"
summary: "A Direct Lake model falls back to DirectQuery when it cannot read the Delta table directly — a SQL view is enough — and a semantic model property decides what happens next."
surface: power-bi
tip_number: 10
state: draft
source: "https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview"
next_step: "In a trial workspace, publish a Direct Lake semantic model over a SQL view, then over the Delta table itself, and compare the storage mode reported for each in the model's properties."
---

**Tip**

Check the storage mode before you believe the performance number. Direct Lake is three modes wearing
one name, and the handover between them is documented:

> Direct Lake on SQL analytics endpoints fall back to DirectQuery table storage mode when they can't
> load the data directly from a Delta table, such as when the data source is a SQL view or when the
> warehouse uses SQL-based granular access control. The semantic model property, Direct Lake behavior,
> controls the fallback behavior.

Both triggers in that sentence are easy to create by accident: a view is the normal way to shape data
for a model, and SQL-based granular access control is the normal way to secure it. Neither reports an
error. The model name still says Direct Lake, the report still renders, and the query that should
have read in-memory Delta files is going back to the source instead.

That is also why a view-shaped Direct Lake model can be slower than DirectQuery: it is DirectQuery,
with the extra expectation of Direct Lake performance attached to it.

**Where this bites**

During a benchmark. Direct Lake over the Delta table looks excellent, then the secured or
view-shaped version of the same model ships to users with a different number attached.

**Try it**

Set the `Direct Lake behavior` property deliberately, and open the model's storage mode to see which
mode is actually in play.
