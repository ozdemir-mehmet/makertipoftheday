---
title: "Your semantic model is a folder of text now"
summary: "A Power BI semantic model saves as 13 to 20 TMDL text files rather than one model.bim, so a measure change shows up as a diff and Desktop is not needed to read it."
surface: power-bi
tip_number: 11
date: 2026-10-11
wave: "n/a - Power BI project format; release waves were retired in September 2026"
build: "Power BI project format, TMDL and PBIR, as documented for Power BI Desktop; measured against FabricTools/pbir-samples @ 2713c2e"
verified_on: 2026-10-10
verified_env: "Linux, Python 3.14.7 - no Power BI Desktop and no tenant; read from a public PBIP sample repository"
expires_on: 2027-03-31
cost: "Free - Power BI Desktop is free, and saving a project as TMDL needs no Fabric capacity"
source: "https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset"
artifact: "assets/tips/11-your-semantic-model-is-a-folder/tmdl-report.py"
evidence: |
  command: git clone --depth 1 https://github.com/FabricTools/pbir-samples.git
  observed: |
    cloned at 2713c2e, 18 MB, 8 semantic models and 8 reports in powerbi-desktop-samples/

  command: cd pbir-samples && python3 /home/mozdemir/src/makertipoftheday/assets/tips/11-your-semantic-model-is-a-folder/tmdl-report.py .
  observed: |
    .
      8 semantic model(s), 8 report(s)

      semantic models
        model                              format  files    bytes  tables  .pbi
        Adventure Works DW 2020            TMDL       16   167828      11  editorSettings.json tracked
        AdventureWorks Sales               TMDL       16    35237       8  editorSettings.json tracked
        Competitive Marketing Analysis     TMDL       15    41923       9  editorSettings.json tracked
        Corporate Spend                    TMDL       15    24688       9  editorSettings.json tracked
        Employee Hiring and History        TMDL       20    43473      10  editorSettings.json tracked
        Regional Sales Sample              TMDL       14   314050      10  editorSettings.json tracked
        Revenue Opportunities              TMDL       17   247942       8  editorSettings.json tracked
        Store Sales                        TMDL       13    61500       6  editorSettings.json tracked

      what each model is made of
        Adventure Works DW 2020.SemanticModel
          definition/cultures/en-US.tmdl
          definition/database.tmdl
          definition/expressions.tmdl
          definition/model.tmdl
          definition/relationships.tmdl
          definition/tables/Currency Rate.tmdl
          definition/tables/Currency.tmdl
          definition/tables/Customer.tmdl
          definition/tables/Date.tmdl
          definition/tables/Product.tmdl
          definition/tables/Reseller.tmdl
          definition/tables/Sales Order.tmdl
          definition/tables/Sales Reason Bridge.tmdl
          definition/tables/Sales Reason.tmdl
          definition/tables/Sales Territory.tmdl
          definition/tables/Sales.tmdl

      reports
        Adventure Works DW 2020            PBIR    definition.pbir present
        AdventureWorks Sales               PBIR    definition.pbir present
        Competitive Marketing Analysis     PBIR    definition.pbir present
        Corporate Spend                    PBIR    definition.pbir present
        Employee Hiring and History        PBIR    definition.pbir present
        Regional Sales Sample              PBIR    definition.pbir present
        Revenue Opportunities              PBIR    definition.pbir present
        Store Sales                        PBIR    definition.pbir present

      no per-machine files (.pbi/localSettings.json, .pbi/cache.abf) are tracked
---

Save a Power BI project as PBIP and the semantic model is not a file. It is a folder of TMDL text,
one file per table, and you can read all of it in any editor. The eight models in the
`FabricTools/pbir-samples` repository come to between 13 and 20 files each - the smallest is 24 KB of text, the
largest 314 KB, and every one of them is diffable.

## One file per table changes what a review looks like

The model folder holds `definition.pbism`, `definition/database.tmdl` for the compatibility level,
`definition/model.tmdl`, `definition/relationships.tmdl` with every relationship in one place,
`definition/cultures/` for the culture's linguistic metadata, and `definition/tables/` with one file per
table carrying its DAX. Rename a measure or change a
calculation in Sales and the pull request shows a few changed lines in `tables/Sales.tmdl`. The same
edit in the older TMSL format is a change inside a single `model.bim`, and a diff of a file like that
tells you nothing - if your repository still holds one, that is what you have.

## Two files in the project belong to your machine, not the model

Every model folder also carries a `.pbi` folder. Two of its files are yours alone. Learn singles out `localSettings.json` as holding settings that apply only for the current user
and computer, and says to exclude it from source control. The samples in that repository ignore exactly
two files - `**/.pbi/localSettings.json` and `**/.pbi/cache.abf` - and commit `editorSettings.json`
next to them. That split is the useful part:
`cache.abf` is a binary model cache and `localSettings.json` records your machine, while
`editorSettings.json` is shared editor state that the team may as well have. A repository that
commits the first two gains a blob that changes on every open.

## What this gives you

A model you can review line by line, search with grep, and open without Desktop; and a tidy
project folder, because the two files that change per machine are named and excluded.
