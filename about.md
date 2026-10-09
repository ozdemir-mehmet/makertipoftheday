---
layout: default
title: About
permalink: /about/
---

# About

{{ site.description }}

Successor in spirit to [crmtipoftheday.com](https://crmtipoftheday.com/) (1462 tips, dormant since
June 2024), rebuilt for a stack that now ships on a release-wave cadence.

## How a tip gets published

Every tip has to clear these gates, in order:

1. **Provenance.** A primary source is cited - a Learn page, a documentation diff, a release note.
   No source, no post.
2. **Executed.** The artifact was deployed or run against a pinned environment, and the post carries
   the command and the observed output.
3. **Reproducible.** It deploys into a clean environment with no manual steps, or every manual step
   is enumerated.
4. **Fresh.** An expiry date no further out than one release wave. The nightly job flags a tip past
   its expiry rather than letting it serve stale text.
5. **Terminology.** Product, feature and tool names are checked against the vendor's own page on the
   day of publishing.
6. **Cost and supportability.** Licence and premium dependency stated; anything relying on
   unsupported configuration is labelled as such.
7. **Sanitised.** No tenant names, environment URLs, identifiers or customer data.
8. **Editorial.** One mechanism per tip, a tl;dr, the gotcha, and the evidence block.
9. **Reviewed.** Two independent reviewers over the text, which catches structure and consistency -
   never truth.
10. **Approved and rendered.** Published from a preview, checked as rendered, then promoted.

## Scope

Dataverse; Power Platform (Power Apps, Power Automate, Power Pages, Copilot Studio); Dynamics 365 CRM;
extensibility and tooling (client scripting and Xrm, PCF, FetchXML Builder, Ribbon Workbench,
XrmToolBox, PRT, CMT); Microsoft Fabric; Power BI - plus cross-cutting ALM, governance, licensing and
cost across all of them.

The seven surface slugs are listed in one place, `_data/surfaces.yml`: `scripts/validate_tips.py`
validates `surface:` against them and `/all/` groups by them.

Out of scope: Business Central (AL) and Finance & Operations (X++) - this is the CRM-side Dynamics
stack, not ERP.
