---
title: "Your canvas app's formulas are plain JSON on disk"
summary: "A canvas app package is a zip: Controls carries every formula, and References\\DataSources.json records the data row limit of 500 against each Dataverse table it binds."
surface: power-platform
tip_number: 12
date: 2026-10-12
wave: "n/a - canvas app .msapp packaging; release waves were retired in September 2026"
build: "Canvas app .msapp as saved by Power Apps Studio; measured against the canvas app inside CenterofExcellenceCoreComponents 4.50.9 (managed, from microsoft/coe-starter-kit tag CoEStarterKit-February2026)"
verified_on: 2026-10-11
verified_env: "Linux, Python 3.14.7 - no Power Apps Studio and no tenant; read from the app inside a managed CoE solution package"
expires_on: 2027-04-09
cost: "Free to read - unpacking a file needs no licence and no premium connector"
source: "https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview"
artifact: "assets/tips/12-your-canvas-apps-formulas-are-json-on-disk/msapp-report.py"
evidence: |
  command: unzip -o one.msapp -d one     # one.msapp extracted from the CoE managed package
  observed: |
    Controls/  References/  Resources/  Assets/   - 17 files

  command: python3 assets/tips/12-your-canvas-apps-formulas-are-json-on-disk/msapp-report.py one.msapp
  observed: |
    data sources: 94
      OptionSetInfo              73
      ViewInfo                   6
      NativeCDSDataSourceInfo    6
      ServiceInfo                4
      CollectionDataSourceInfo   3
      StaticDataSourceInfo       2

    Dataverse tables, and the record cap each carries:
      Environment Variable Values environmentvariablevalue MaxGetRowsCount=500
      Environment Variable Definitions environmentvariabledefinition MaxGetRowsCount=500
      Power Platform Users     admin_powerplatformuser  MaxGetRowsCount=500
      PowerApps Apps           admin_app                MaxGetRowsCount=500
      Environments             admin_environment        MaxGetRowsCount=500
      Makers                   admin_maker              MaxGetRowsCount=500
      distinct caps: [500]

    formulas: 1642 InvariantScript values, 1634 non-empty, in 1.json, 4.json, 5.json
      delegation-sensitive calls: {'LookUp': 8, 'Filter': 5, 'Max': 4, 'CountRows': 3, 'CountIf': 3, 'SortByColumns': 1, 'Sum': 0, 'Average': 0, 'Min': 0, 'Search': 0, 'Sort': 0, 'Distinct': 0, 'GroupBy': 0, 'AddColumns': 0, 'Collect': 0, 'Patch': 0, 'Remove': 0, 'FirstN': 0, 'LastN': 0}

  command: grep -c delegat References/DataSources.json
  observed: |
    6 - all six inside TableDefinition, all the same Dataverse description: "Unique identifier of
    the delegate user who created the record", for the createdby and modifiedby columns. The file
    carries no delegation metadata, so neither the cap nor the metadata tells you which call is
    delegable. Learn states the consequence: when a query is nondelegable, Power Apps gets the
    first 500 records from the data source.

  source quote, verbatim: "When a query is nondelegable, Power Apps gets the first 500 records from the
    data source and then runs the actions in the query" - and, from the same page, "You can increase
    this limit to 2,000 records". Both fetched 2026-10-11, 200.
---

A canvas app leaves the designer as a single file. The formulas, the tables it binds and the data row
limit it is built with are all inside it, as text.

## A canvas app is a zip file

Save an app as a package and you get one `.msapp`. Copy it to `.zip`, expand it, and the app is sitting
there as folders: `Controls\` holds the screens and their controls, `References\DataSources.json` lists every data
source the app binds, and `Resources\` holds what it ships with.

## The formulas are in there as text

Every control property that carries an expression stores it under `InvariantScript`. The app I unpacked,
from the CoE Starter Kit package, has 1,642 of those properties across three files, 1,634 of them holding
an expression, and they read fine outside Studio. Against the folder the expansion creates, with your app's name in place of the one shown:

    Select-String -Path .\AdminApp\Controls\*.json -Pattern 'LookUp\(|Filter\(|Max\(|CountRows\(|CountIf\(|SortByColumns\('

That lists the matching property lines. Counted, this app holds 8 LookUp, 5 Filter, 4 Max, 3 CountRows,
3 CountIf and 1 SortByColumns call.

## The data row limit is recorded against each table

`References\\DataSources.json` names the six Dataverse tables the app binds, and every one of them
carries `MaxGetRowsCount` set to 500 - the data row limit the app is built with. It is the same 500 Learn describes
for a query that cannot be delegated: Power Apps takes the first 500 records from the data source and then
runs the actions in the query. That limit can be raised to 2,000 in the app's settings.
Reading `MaxGetRowsCount` out of that file tells you where each table stands before you open the
designer.
