---
title: "Your business rule does not run on the record your flow writes"
summary: "Entity scope runs a business rule on the server as a synchronous plug-in; any other scope runs it as client-side JavaScript, so a write that never opens the form never runs it."
surface: power-platform
tip_number: 23
date: 2026-10-23
source: "https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-create-business-rule"
artifact: none
wave: "n/a - documentation-based tip; the mechanism is a business rule published in a tenant this machine cannot reach, so nothing was executed"
build: "The Dataverse business-rule page, learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-create-business-rule, fetched 2026-10-23, 64673 bytes, sha256 b16aa88364d4f57249617c31e1ba394d86ad659a0312332c459d3e7e3f9fbb0b"
verified_on: 2026-10-23
verified_env: "No environment and no login - the cited Learn page fetched with curl on 2026-10-23; no business rule was created, no scope was changed and no record was written"
expires_on: 2027-04-23
cost: "Free to read; publishing a rule and testing it against a flow needs a Power Apps licence and an environment"
evidence: |
  NOT EXECUTED. No tenant on this machine: no business rule was created, no scope was changed, and no
  record was written from a flow. One page carries every claim, fetched whole the day of publication.

  command: curl -sSL -o p33.html -w 'http %{http_code} bytes %{size_download}' https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-create-business-rule

  observed:
    http 200, bytes 64673
    sha256 b16aa88364d4f57249617c31e1ba394d86ad659a0312332c459d3e7e3f9fbb0b
    rel=canonical href -> https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-create-business-rule (matches source:)
    updated_at 2026-07-06T19:07:00Z

  The scope table, in page order, each cell quoted whole:

      Set the scope, according to the following:
      If you select this item...
      The scope is set to...
      Entity
      Model-driven app forms and server
      All Forms
      Model-driven app forms
      Specific form ( Account form, for example)
      Just that model-driven app form

  The form-only actions, and the client/server split, quoted whole:

      The following actions only apply to form scope business rules.
      Set column requirement levels
      Show or hide columns
      Enable or disable columns
      Create business recommendations based on business intelligence.
      This limit includes both client side (JavaScript) and server side (XAML generated as synchronous plugins) business rules.

  The three steps the fix is built from, quoted whole:

      If you want to modify an existing business rule, you must deactivate it before you can modify it.
      To save the business rule, select Save on the action bar.
      To activate the business rule, select it in the Solution Explorer window, and then select Activate . You can't activate the business rule from the designer window.
      A business rule might not execute because the field referenced in the business rule isn't included with the form.

  The FIX rests on two of those: Entity is the one scope whose value is "Model-driven app forms and
  server", and the four UI actions are the ones that "only apply to form scope business rules" - which is
  why a rule that also hides a column cannot hold both halves at Entity scope.

  NOT claimed, because the page does not say it: nothing here names Power Automate, an import or a plug-in
  as the channel. The opening is the reader's situation; what the page carries is that the server half of
  a business rule exists only at Entity scope, and that the server half is generated as a synchronous
  plug-in. A second page on the same doc set,
  learn.microsoft.com/en-us/power-apps/maker/model-driven-apps/create-business-rules-recommendations-apply-logic-form,
  fetched 2026-10-23 (http 200, 63569 bytes), says the same from the designer side - "Actions that only
  apply to model-driven apps are ignored when the rule is run server-side." - and is corroboration only;
  no sentence in the body rests on it.
---

You write a rule that shows an error when priority is empty, and on the form it does. Then a flow creates
the record with priority empty, and the rule has nothing to say about it.

Scope is the setting that decides where the rule runs, and it reads like a question about which form to put
it on. Entity runs the rule on the model-driven app forms and on the server, All Forms runs it on the forms
only, and a named form runs it on that one form. The server run is the rule generated as a synchronous
plug-in; the form run is JavaScript on the client, and a write that never opens the form never runs it.

To hold a validation on a record written away from the form:

1. Deactivate the rule. It cannot be edited while it is active.
2. Set Scope to Entity.
3. Save it, then select it in Solution Explorer and activate it there. The designer has no activate.
4. If it also sets a requirement level, hides or disables a column, or carries a recommendation, those
   actions only apply to form-scope rules, so give them a rule of their own and leave that one on a form.

Then write the record from the flow and watch whether the rule catches it.

A rule that does not fire on the form at all is a different fault: check that every column the rule names,
in a condition or an action, is on that form.
