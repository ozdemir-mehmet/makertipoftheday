# Maker Tip Of The Day

Daily, verified tips for the Microsoft business-application stack: Dataverse, Power Platform
(Power Apps, Power Automate, Power Pages, Copilot Studio), Dynamics 365 CRM, Microsoft Fabric and
Power BI.

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
| Fabric | OneLake, Lakehouse/Warehouse, Data Factory, Real-Time Intelligence, Direct Lake, OneLake shortcuts to Dataverse |
| Power BI | semantic models, reports, Copilot |
| Cross-cutting | ALM (solutions, pipelines, managed environments, pac CLI), governance (DLP, CoE Toolkit, Purview), licensing and capacity |

Out of scope: Business Central (AL) and Finance & Operations (X++) - this is the CRM-side Dynamics
stack, not ERP.

## Repository layout

```
tips/                 one directory per tip: index.md + artifacts/
site/                 static site generator input (built in Actions, published to GitHub Pages)
.github/workflows/    build + deploy, and the scheduled re-verify job
references/           build/wave version pins used by the re-verify job
```

## Status

Skeleton only. The static site, the tip corpus, the re-verify workflow and the MCP endpoint are not
built yet.

## Licence

Undecided.
