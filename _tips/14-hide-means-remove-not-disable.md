---
title: "Hide means remove, not disable"
summary: "A HideCustomAction does not grey a button out - the ribbon element is removed at runtime. The command behind it stays, and every removal travels with the solution."
surface: power-platform
tip_number: 14
date: 2026-10-14
wave: "n/a - the model-driven app command bar; release waves were retired in September 2026"
build: "customizations.xml inside a managed solution (CenterofExcellenceCoreComponents 4.50.9, from the CoE Starter Kit release) read by the artifact, with the rule from Define custom actions to modify the ribbon"
verified_on: 2026-10-13
verified_env: "Linux, Python 3.14.7 - a managed solution zip downloaded from the CoE Starter Kit release, no tenant and no environment"
expires_on: 2027-04-11
cost: "Free to read a solution zip you already have; the hide actions themselves ship with any managed solution"

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
