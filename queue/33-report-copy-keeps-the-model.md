---
title: "Your copy of the report opens the shared model for editing"
summary: "A copy of a report folder keeps the relative model reference in definition.pbir, and byPath opens that model in full edit mode - so the model behind a copy is one folder other reports read too."
surface: power-bi
tip_number: 33
state: ready
wave: "n/a - Power BI Desktop project file behaviour, not a release wave"
build: "none - no CLI build involved; 12 report folders read from microsoft/finops-toolkit at commit 1da3fcbe, and one Learn page fetched at its canonical URL"
verified_on: 2026-10-22
verified_env: "Linux (CachyOS), no Power BI Desktop and no tenant: 12 definition.pbir files and the repo tree read over the GitHub API at a pinned commit, one Learn page fetched; nothing opened in Desktop and nothing published"
expires_on: 2027-04-15
cost: "Free - no licence and no Desktop needed for the measurement; the project format itself is free"
source: "https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report"
artifact: "assets/tips/33-report-copy-keeps-the-model/check-dataset-reference.py"
evidence: |
  run 2026-10-22, no tenant, no Power BI Desktop on this machine.

  command: python3 assets/tips/33-report-copy-keeps-the-model/check-dataset-reference.py --sha 1da3fcbe1b12b3fc82f483889efdc6c431f684a3
  observed:
    ok    the sample has report folders carrying definition.pbir: 12 report folder(s)
    ok    every one of them uses a byPath reference: 12 byPath, 0 byConnection
    ok    none of the paths is absolute: all relative
    ok    at least two reports resolve to the same model folder: 6 report(s) -> src/power-bi/kql/Shared.Dataset; 6 report(s) -> src/power-bi/storage/Shared.Dataset
    ok    every resolved model folder exists in the sample: 2 distinct target(s), all present
    exit 0

  the twelve report folders are src/power-bi/{kql,storage}/<name>.Report, each with
  datasetReference.byPath.path = "../Shared.Dataset", which resolves to the Shared.Dataset folder beside
  them - six reports per model folder.

  quoted from the source page (fetched 2026-10-22, HTTP 200, 79503 bytes, rel=canonical matches source:):
    "byPath - Specifies a relative path to the target semantic model folder. Absolute paths aren't
     supported. A forward slash (/) is used as a folder separator. When used, Power BI Desktop also opens
     the semantic model in full edit mode."
    "byConnection - Specifies the connection to a semantic model in a Fabric workspace by using a
     connection string. When a byConnection reference is used, Power BI Desktop doesn't open the semantic
     model in edit mode."

  what is measured and what is quoted: the twelve reports pointing at two shared model folders is the
  measurement; "opens the model in full edit mode" and the byConnection alternative are the page's
  sentences. NOT executed here: nothing was opened in Desktop, so the tip does not claim what the dialog
  looks like or what Desktop writes on save - it stops at which folder the edits go to, which the relative
  path decides.
---

You copy a report folder to build a variant - a different audience for the same data - and you open the copy
to add a measure. Both items now read the same model folder.

The copy is only a copy of the report. Its `definition.pbir` still carries the reference to the model:

```
"datasetReference": { "byPath": { "path": "../Shared.Dataset" } }
```

That path is relative to the report folder, so the copy resolves to the same model the original does. In
Microsoft's own sample, twelve report folders under `src/power-bi/` all carry `"path": "../Shared.Dataset"`,
six to each of two model folders: the reports are separate, the models are not.

The page documenting the file says what `byPath` does with that model:

> byPath - Specifies a relative path to the target semantic model folder. Absolute paths aren't supported.
> A forward slash (/) is used as a folder separator. When used, Power BI Desktop also opens the semantic
> model in full edit mode.

Full edit mode is what makes this matter: the copy opens the folder the other reports read, for change.
The model is not part of the copy.

Give the variant its own model: copy the model folder beside the report copy, then set the copy's
`datasetReference.byPath.path` to it (`"../<YourModel>.Dataset"`). If the variant should read the shared
model without opening it for edit, point it at that model in its Fabric workspace with a `byConnection`
reference - Desktop does not open the model in edit mode for one.
