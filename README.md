# Maker Tip Of The Day

Daily, verified tips for the Microsoft business-application stack: Dataverse, Power Platform
(Power Apps, Power Automate, Power Pages, Copilot Studio), Dynamics 365 CRM, extensibility and
tooling (PCF, XrmToolBox, PRT, CMT), Microsoft Fabric, Power BI, and cross-cutting ALM, governance
and licensing.

Successor in spirit to [crmtipoftheday.com](https://crmtipoftheday.com/) (1462 tips, dormant since
June 2024), rebuilt for a stack that now ships on a release-wave cadence.

## What makes a tip here

Rules every tip in this repository must satisfy:

- **Verified, not evergreen.** Every tip records the build/wave it was tested on and a
  re-verification expiry. A tip that has not been re-tested past its expiry is flagged, not silently
  served stale.
- **A runnable artifact, not a screenshot.** Each tip ships the thing that actually does the work -
  an unpacked solution, a flow JSON, a Fabric notebook, TMDL/PBIR, a PCF control - plus a short
  written explanation of the mechanism.
- **Cross-surface by default.** The value is the wiring: Dataverse → OneLake shortcut → Direct Lake
  semantic model → agent tool; or the choice between a plug-in and an MCP tool.
- **Cost and licence stated.** The deciding question is often supportability and capacity spend, not
  syntax.
- **Agent-readable by design.** Tip metadata is structured so the build can publish a machine-readable
  index and serve an MCP endpoint in front of it, letting Copilot Studio agents and coding agents
  query tips directly.

## Surfaces covered

| Bucket | Includes |
| --- | --- |
| Dataverse | data model, security roles and column-level security, sync/async plug-ins, virtual tables, Git integration, solutions, Dataverse MCP server |
| Power Platform | Power Apps (canvas, model-driven, custom pages), Power Automate (cloud and desktop flows, process mining and process intelligence), Power Pages, Copilot Studio agents |
| Dynamics 365 CRM | Sales, Customer Service, Field Service, Contact Center, Customer Insights |
| Extensibility and tooling | client scripting and Xrm, PCF, FetchXML Builder, Ribbon Workbench, XrmToolBox, PRT, CMT |
| Microsoft Fabric | OneLake, Lakehouse/Warehouse, Data Factory, Real-Time Intelligence, Direct Lake, OneLake shortcuts to Dataverse |
| Power BI | semantic models, reports, Copilot |
| Cross-cutting | ALM (solutions, pipelines, managed environments, pac CLI), governance (DLP, CoE Toolkit, Purview), licensing and capacity |

Out of scope: Business Central (AL) and Finance & Operations (X++) - this is the CRM-side Dynamics
stack, not ERP.

The vocabulary itself lives in one file, `_data/surfaces.yml`: `surface:` in a tip's front matter has
to be one of those slugs, `/all/` groups by them, and `scripts/validate_tips.py` rejects any value
outside that list.

## Repository layout

```
_tips/                one markdown file per tip (a Jekyll collection)
assets/tips/          internal artifacts, one directory per tip (excluded from the site)
_data/surfaces.yml    the surface vocabulary the validator and /all/ share
_layouts/             the tip layout; _includes/ the shared partials (surface-label.html)
queue/                the publish-ready buffer plus the item template
scripts/              validate_tips.py, reverify.py, preview.sh, test_gates.sh
.github/workflows/    Pages build and deploy, and the nightly re-verify job
```

## Status

The static site is built and the gates are enforced in CI: the Jekyll site, the tip layout, the front
matter validator, the nightly re-verify job and the Pages workflow are all in place and exercised
locally. No tip has been published yet, so the home page ships the empty state.

Outstanding: the MCP endpoint over the tip corpus, and pointing DNS at Pages once the first tip
lands.

## Licence

Undecided.
