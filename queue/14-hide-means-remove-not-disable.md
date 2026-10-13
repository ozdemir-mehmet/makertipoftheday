---
title: "Hide means remove, not disable"
summary: "A HideCustomAction does not grey a button out - the ribbon element is removed at runtime. The command behind it stays, and every removal travels with the solution."
surface: power-platform
tip_number: 14
state: ready
next_step: ""
source: "https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/define-custom-actions-modify-ribbon"
artifact: "assets/tips/14-hide-means-remove-not-disable/hide-actions-report.py"
wave: "n/a - the model-driven app command bar; release waves were retired in September 2026"
build: "customizations.xml inside a managed solution (CenterofExcellenceCoreComponents 4.50.9, from the CoE Starter Kit release) read by the artifact, with the rule from Define custom actions to modify the ribbon"
verified_on: 2026-10-13
verified_env: "Linux, Python 3.14.7 - a managed solution zip downloaded from the CoE Starter Kit release, no tenant and no environment"
expires_on: 2027-04-11
cost: "Free to read a solution zip you already have; the hide actions themselves ship with any managed solution"
evidence: |
  Artifact assets/tips/14-hide-means-remove-not-disable/hide-actions-report.py, run 2026-10-13 against
  CenterofExcellenceCoreComponents_4.50.9_managed.zip (28,975,074 bytes, downloaded from
  https://github.com/microsoft/coe-starter-kit/releases/download/CoEStarterKit-February2026/), command:

      $ python3 hide-actions-report.py CenterofExcellenceCoreComponents_4.50.9_managed.zip

  observed:
      entities defined: 46
      entities with at least one hide action: 22
      hide actions: 1025 (inside entity blocks: 1025, elsewhere: 0)
      distinct locations: 1025

      the surface the element sits on, by the middle segment of its location:
        HomepageGrid     488
        Form             302
        SubGrid          229
        admin_environmentcapacity 2
        admin_environmentsecurityrolepermission 2
        admin_customizedemail 1

      elements taken out on more than one surface: 50 of 110
        Activate         Form, HomepageGrid, SubGrid
        Deactivate       Form, HomepageGrid, SubGrid
        NewRecord        Form, HomepageGrid, SubGrid
        WordTemplate     Form, HomepageGrid, SubGrid
        Assign           Form, HomepageGrid, SubGrid

      the element that is removed, by its trailing name, most often:
        Activate         51
        Deactivate       51
        NewRecord        51
        WordTemplate     49
        Assign           46
        Sharing          41

      the locations begin with:
        Mscrm            1019
        AIBuilder        5
        AccessChecker    1

  Quoted from "Define custom actions to modify the ribbon (model-driven apps)",
  learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/define-custom-actions-modify-ribbon,
  fetched 200 on 2026-10-13, one sentence per line, in page order, nothing joined and nothing dropped from the
  list item that carries the alternative. The line beginning "Note" is the callout's body
  text with the callout's own label in front of it, as the page renders it:

      A <HideCustomAction> is a statement that you use when you want to remove an existing ribbon element so that it is not rendered.
      This does not hide the ribbon element, it actually removes the ribbon element at runtime so that it doesn't exist in the ribbon.
      The HideActionId element provides a unique ID for the action.
      The Location parameter must match the Id of the ribbon element you want to remove.
      Note Because the HideCustomAction element removes a specified node from the ribbon, removing ribbon elements in this manner may not be the best option for every situation.
      - If you want to remove a button that is associated with a specific privilege, you should adjust the privileges for the table in the security roles in your implementation.
      This will allow the default ribbon display and enables rules to hide or disable ribbon elements from users who do not have the necessary privileges to perform those actions.
---

## There is no disabled-but-present option

There is nothing in between. The command bar has one move for a control you do not want: take it
out. A HideCustomAction names the ribbon element it suppresses by that element's Location, and at
runtime the element is gone for everyone who loads the app. The command the button invoked is still
there - what you lose is the button.

## One element, or one on every surface

The action names an element, not a command, and the grid, the form and the subgrid carry an element
each. So the same button is taken out in three places rather than one, and a package's count of hide
actions runs past the number of buttons a maker remembers removing.

Finding them takes a search rather than an API call and a session. Expand the solution zip and read
customizations.xml:

    Select-String -Path customizations.xml -Pattern '<HideCustomAction'

## The removals are rules you keep

Each one travels with the solution, applies to everyone who opens the app, and is not a security
decision - the privilege behind the command is untouched. The same page makes that point and sets out
the alternative in the same breath: leave the command in place and let a rule or a privilege decide who
gets it, which keeps the button for the people entitled to press it.
