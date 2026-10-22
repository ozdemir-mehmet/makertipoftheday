---
title: "Your status filter on a plug-in step does not mean the status changed"
summary: "A filtering attribute fires when the column is in the update request, not when its value changes, so an update that carries the same status still runs the step."
surface: extensibility
tip_number: 18
wave: "n/a - documented behaviour, not a release wave"
build: "none - no CLI build involved; two sample solutions read at pinned commits and four Learn pages checked"
date: 2026-10-18
verified_on: 2026-10-18
verified_env: "Linux (CachyOS); two Microsoft sample solutions measured from their unpacked SdkMessageProcessingSteps XML at pinned commits, four Learn pages fetched and their quoted sentences matched the same day; no tenant, no plug-in executed"
expires_on: 2027-04-19
cost: "Free - plug-in registration and the vendor documentation need no licence"
source: "https://learn.microsoft.com/en-us/power-apps/developer/data-platform/register-plug-in"
artifact: "assets/tips/19-status-filter-does-not-mean-status-changed/count-filtered-steps.py"
evidence: |
  run 2026-10-18. Documentation-sourced tip: the mechanism and the fix are each quoted from a vendor page,
  and nothing about runtime behaviour was executed - there is no tenant on this machine. The artifact
  re-checks both halves that can be checked: the sample counts, and whether every sentence quoted below is
  still on the page it is attributed to.

  re-runnable: PYTHONDONTWRITEBYTECODE=1 python3 assets/tips/19-status-filter-does-not-mean-status-changed/count-filtered-steps.py

  observed:
    microsoft/Nonprofits@11e976e8274e: 24 step file(s)
    microsoft/Power-CAT-Tools@c33f47982cd2: 7 step file(s)
    steps: 31
    empty FilteringAttributes: 18
    naming filtering attributes: 13
      Create steps  18  of which filtered 1
      Update steps  12  of which filtered 12
      other  steps   1  of which filtered 0
    filtering on statecode or statuscode: 2
      Update msnfp_engagementopportunityschedule
        Post-Update Engagement Opportuntiy Schedule
        filters on msnfp_maximum|msnfp_minimum|statecode
      Update cat_riskassessment
        Microsoft.PowerCATTools.SecRoleAssessmentPlugin.AssessmentPlugin: Update of cat_riskassessment
        filters on cat_roleid|statecode|statuscode
    counts: reproduce the evidence block
    page: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/register-plug-in
      78773 bytes, canonical matches
      quotes present: 4/4
    page: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/sdkmessageprocessingstep
      117083 bytes, canonical matches
      quotes present: 1/1
    page: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/understand-the-data-context
      73866 bytes, canonical matches
      quotes present: 3/3
    page: https://learn.microsoft.com/en-us/dotnet/api/microsoft.xrm.sdk.messages.updaterequest?view=dataverse-sdk-latest
      51072 bytes, canonical matches
      quotes present: 1/1
    result: counts and quotes both reproduce the evidence block
  exit 0

  `source:` carries one URL because validate_tips.py requires a single http(s) URL. The other three pages
  the body relies on are attributed below, and the artifact fetches all four and reports each one's
  canonical link and quote count in the run above.

  Quoted sentences, page by page, in page order. Every one is matched by that run, ignoring tags,
  punctuation and whitespace. Where a plain-text render leaves a space before a comma around a `<code>`
  element, or puts a table row's field label on the same line, the quote below is the sentence itself.

  register-plug-in:
    "For the Update , OnExternalUpdated , or other message, when you set the primary entity, filtering attributes (columns) limits the execution of the plug-in to cases where the specified columns are included in the update."
    "Only include columns with changed values in update operations."
    "If a request contains a filtering attribute, the plug-in will be triggered regardless of whether the attribute’s value is changed or not."
    "Don't include the primary key of the entity in the filtering attributes. The primary key is always included in update operations, so doing this negates all other filtered attributes."

  reference/entities/sdkmessageprocessingstep, the FilteringAttributes row:
    "Comma-separated list of attributes. If at least one of these attributes is modified, the plug-in should execute."

  understand-the-data-context, which carries the image description and the name of the request parameter the
  body tells the reader to read:
    "When you register a step for a plug-in that includes a table as one of the parameters, you can specify that a copy of the table data be included as a snapshot or image by using the PreEntityImages and PostEntityImages properties."
    "This data provides a comparison point for table data as it flows through the event pipeline."
    "For example, to access the Entity property that’s passed as part of the CreateRequest , you need to know that the name of that property is Target ."

  microsoft.xrm.sdk.messages.updaterequest, the Target property, which is what makes `Target` the right
  parameter for an Update step rather than the Create-only example above:
    "Gets or sets an instance of an entity that is used to update a record. Required."

  The first two pages disagree on the load-bearing word, which is the tip: the registration page says the
  step fires when the column is in the request whether or not the value changed; the entity reference says it
  fires when at least one of the attributes "is modified". The body follows the registration page. Its fix is
  quoted rather than reasoned: what to register comes from the third page, and the parameter it tells you to
  read comes from the fourth, so the body claims nothing about runtime behaviour it could not execute here.
---

You filter an Update step on `statuscode`, expecting the plug-in to run only when the status moves. Dataverse does not compare values. It checks whether the column is in the update message at all, so an update that carries `statuscode` with the value it already had still triggers the step.

Microsoft's own documentation says both things. The property's entity reference says the step executes if at least one of the filtering attributes is modified. The registration page says the step fires regardless of whether the value changed, and adds the caller-side rule that you send only columns whose values changed. Presence is the trigger; proving a change is your own job.

The filter still earns its place, because it keeps the step out of updates that never mention the column. To know the value actually moved, register a pre-image on the step, which Microsoft describes as a comparison point for the record as it flows through the pipeline. Then read the record in `Target` and the copy in the pre-image inside the plug-in, and return before doing any work when the status they carry agrees.
