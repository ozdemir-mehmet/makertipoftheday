---
title: "Get the quick create pane to open"
summary: "The pane opens when the table flag is on, the table and its quick create form are in the app, and the parent lookup on that form is set to business required."
surface: power-platform
tip_number: 16
state: ready
next_step: ""
source: "https://learn.microsoft.com/en-us/dynamics365/customerengagement/on-premises/customize/create-edit-quick-create-forms"
artifact: "assets/tips/16-the-parent-lookup-has-to-be-required/quick-create-check.py"
wave: "n/a - model-driven app quick create forms; release waves were retired in September 2026"
build: "customizations.xml inside a managed solution (CenterofExcellenceCoreComponents 4.50.9) read by the artifact, plus the Learn pages on quick create forms (cloud and on-premises) and form troubleshooting, crmtipoftheday 1192, and community.dynamics.com write-ups"
verified_on: 2026-10-14
verified_env: "Linux, Python 3.14.7 - a managed solution zip from the CoE Starter Kit release, no tenant and no environment"
expires_on: 2027-04-14
cost: "Free to read a solution zip and the pages cited"
evidence: |
  Artifact assets/tips/16-the-parent-lookup-has-to-be-required/quick-create-check.py, run 2026-10-14 against
  CenterofExcellenceCoreComponents_4.50.9_managed.zip, command:

      $ python3 quick-create-check.py CenterofExcellenceCoreComponents_4.50.9_managed.zip

  observed, as printed, top to bottom:

      tables in the solution: 46
      tables with Enable quick create forms on: 2

      admin_EnvironmentBusinessArea
        forms: main 1, quickCreate 1, quick 1, card 1
        columns on the quick create form: 3
        lookups on the form: none
        required (required, nvarchar): admin_areaname - on the form
        system columns the table requires that the form does not carry: admin_environmentbusinessareaid, ownerid, statecode
      admin_EnvironmentCapacity
        forms: quickCreate 1, card 1, quick 1, main 1
        columns on the quick create form: 4
        lookups on the form: none
        required (required, nvarchar): admin_capacitytype - on the form
        system columns the table requires that the form does not carry: admin_environmentcapacityid, ownerid, statecode

  The same artifact against assets/tips/16-the-parent-lookup-has-to-be-required/fixture-customizations.xml,
  a hand-built fixture carrying the shapes the docs describe and nothing else, made to reach the lookup
  path the CoE solution never reaches. Run 2026-10-14:

      $ python3 quick-create-check.py fixture-customizations.xml

      tables in the solution: 1
      tables with Enable quick create forms on: 1

      new_child
        forms: main 1, quickCreate 1
        columns on the quick create form: 3
        lookup on the form: new_parentid - marked required
        lookup on the form: new_optionalid - not marked required
        required (required, nvarchar): new_name - on the form
        required (required, lookup): new_parentid - on the form, a lookup to new_parent
        system columns the table requires that the form does not carry: new_childid, ownerid

  The app requirement is on Microsoft's on-premises page for quick create forms, fetched 200 on
  2026-10-14. It sits in a Note under that page's "Create a quick create form" heading, as the second of
  the Note's three bullets, the first being that the Allow Quick Create option has to be on:

      You must also add the entity and the quick create form to your app.

  crmtipoftheday.com/1192/quick-create-for-custom-entities-in-unified-interface/, fetched 200 the same
  day, carries the same rule as the second of the two items in its list. The item is quoted whole, both
  of its sentences:

      At least one Quick Create form is included in your app (using App Designer). Apps seem to be now not showing what's not included.

  community.dynamics.com/blogs/post/?postid=6509d2c2-749e-4507-9d12-f39d6bc186cb, fetched 200 the same
  day, reports the symptom the question turns on, and its resolution. Both sentences below come from that
  one post, the first taken whole from a long paragraph, the second from the post's closing summary after
  its four app-designer steps:

      If you look from the header quick create + icon I can see all the entity even I have not added entity into app designer and I can open the quick create forms, but in same apps from subgrid "+ New" navigation its redirecting me the main forms from subgrid "+New".
      In summary the make sure you added your quick create entity in the app designer to access quick create forms from apps.

  The cloud page for quick create forms,
  learn.microsoft.com/en-us/power-apps/maker/model-driven-apps/create-edit-quick-create-forms, fetched 200
  the same day, says the opposite in its Important box about a form that is missing from the app:

      If a quick create form exists for a table but isn't included in the app, the Unified Interface runtime will still open the quick create form. This behavior occurs with lookup controls and subgrids. If you don't want a quick create form to appear in your app you must delete it.

  Those two statements are left standing side by side rather than reconciled. The on-premises page states
  the requirement, the field reports describe the pane failing without it, and the cloud page describes a
  form that still opens. Which of the three describes a given tenant is not something a solution zip or a
  documentation read can settle.

  On the parent lookup rule: the two quick create pages were fetched (200 each) and their raw HTML searched
  with grep for the string "required", which appears in neither. The forms troubleshooting page names the
  main form dialog force flag and quick create being unavailable as the reasons a lookup or a grid opens
  another form, and gives seven reasons a table is filtered out of the create flyout, none of them a column
  requirement. Two of the four write-ups state the parent lookup rule, alexmscrm and meghshyam;
  crmtipoftheday's requirements list does not carry it, and the community.dynamics.com post is about the
  app requirement rather than a column. A required level is spelled "required" in this solution's exported
  XML, 55 columns of it and five of them lookups; "applicationrequired" does not occur, and the artifact
  accepts all three spellings. That is the extent of the search, and the tip does not claim more than it.

  alexmscrm.blogspot.com/2017/11/dynamics-365-quick-create-form-does-not-show-up.html, fetched 200 the same
  day, after listing quick create enabled and a quick create form as its prerequisites. Each line is a
  separate sentence on the page, quoted whole:

      I've enabled the setting above, but the quick create form does not show up. Why ?
      Now you should check the parent lookup field in your child entity, in order to use the quick create form, the parent lookup field in child entity must be set as "Business Required".

  meghshyam.wordpress.com/2020/10/07/quick-create-form-is-not-showing-up-in-dynamics-365-uci-app/, fetched
  200 the same day, carries it as a requirement bullet on its own line:

      Parent lookup field in child entity set as "Business Required"
---

## What has to be true

1. On the table, turn on Enable quick create forms.
2. Add the table and its quick create form to the app in the app designer. Both of them, not just the
   table. Leave the form out and the header quick create keeps working while the plus on a subgrid opens
   the main form instead.
3. Give the table a form of type Quick Create. More than one is allowed; form order decides which one
   everyone gets, and it cannot be assigned per security role.
4. On that form, put the lookup back to the parent and set that column to Business Required.

The last of those is easy to skip, because it lives on the form rather than on the table. Create from a
lookup or a subgrid and the new record belongs to the row you were on, and the pane opens only when the
form it would use carries the column that holds that row, marked as required.

## When it still does not open

Check the plain ones first: no create privilege on the table, no permission on the form through the user's
security roles, or a read-only table. Past those, Monitor answers the question of whether the form is being
offered at all. The FormType operation lists the reasons a quick create form was not opened, and
QuickCreateMenu does the same for the create flyout. Neither of them reports a column problem, so from
there check the form itself.

## What the failure looks like

Nothing throws. Quick create is switched on, the form exists, and the pane does not come up where it used
to. There are two causes. If the quick create form is not in the app, the plus on a subgrid opens the main
form while the header quick create still opens its own pane. If the form is in the app but the parent
lookup is not marked required, the lookup and the subgrid both stop offering it, because that is the column
that carries the context. Work out which cause you have before you change anything, because one
is fixed in the app designer and the other in the form.

Some environments do still open a quick create form that is not in the app from a lookup or a subgrid, so
if yours is in the app and the pane still refuses, the lookup is the next thing to check.
