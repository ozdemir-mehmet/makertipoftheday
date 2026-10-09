---
title: "Your table has twelve columns you did not create, and one of them rewrites Created On"
summary: "Every Dataverse table carries twelve columns nobody created - and mapping a source date to overriddencreatedon puts it in createdon instead."
surface: dataverse
tip_number: 9
date: 2026-10-09
wave: "n/a - solution package format; release waves were retired in September 2026"
build: "CenterofExcellenceCoreComponents 4.50.9 managed, MetadataBrowser 4.0.0.0 managed"
verified_on: 2026-10-09
verified_env: "Linux, Python 3.14.7 - no environment, no login; read from published solution packages"
expires_on: 2027-03-31
cost: "Free - no premium connector, no capacity; overriding Created On needs prvOverrideCreatedOnCreatedBy"
source: "https://learn.microsoft.com/en-us/power-apps/developer/data-platform/run-data-import"
artifact: "assets/tips/9-twelve-columns-you-did-not-create/table-columns.py"
evidence: |
  command: curl -sSL -o coe.zip https://github.com/microsoft/coe-starter-kit/releases/download/CoEStarterKit-February2026/CenterofExcellenceCoreComponents_4.50.9_managed.zip
  observed: |
    28975074 bytes, 534 payload files

  command: python3 table-columns.py coe.zip
  observed: |
    === coe.zip ===
      solution : CenterofExcellenceCoreComponents 4.50.9 (managed)
      tables   : 46 carrying a column list
      columns  : 1586 in total - 812 not created by a maker, 774 that were
      on all 46 : 12 columns that nobody created:
                 createdby
                 createdon
                 createdonbehalfby
                 importsequencenumber
                 modifiedby
                 modifiedon
                 modifiedonbehalfby
                 overriddencreatedon
                 statecode
                 statuscode
                 timezoneruleversionnumber
                 utcconversiontimezonecode

      the biggest:
                 admin_App                           20 nobody created /  99 maker
                 admin_Flow                          20 nobody created /  63 maker
                 admin_Environment                   20 nobody created /  58 maker
                 admin_PVA                           20 nobody created /  37 maker
                 admin_Connector                     20 nobody created /  33 maker
                 admin_Maker                         17 nobody created /  34 maker

  command: python3 table-columns.py --table admin_App coe.zip
  observed: |
    admin_App: 20 columns nobody created (required level in brackets)
               admin_appid (systemrequired)
               createdby (none)
               createdon (none)
               createdonbehalfby (none)
               importsequencenumber (none)
               modifiedby (none)
               modifiedon (none)
               modifiedonbehalfby (none)
               overriddencreatedon (none)
               ownerid (systemrequired)
               owningbusinessunit (none)
               owningteam (none)
               owninguser (none)
               processid (none)
               stageid (none)
               statecode (systemrequired)
               statuscode (none)
               timezoneruleversionnumber (none)
               traversedpath (none)
               utcconversiontimezonecode (none)
               and 99 the maker added

  command: python3 table-columns.py MetadataBrowser.zip
  observed: |
    === MetadataBrowser.zip ===
      solution : MetadataBrowser 4.0.0.0 (managed)
      tables   : 0 carrying a column list - the package ships entities as shells,
                 or ships none at all. Nothing to count.

  command: python3 table-columns.py /tmp/notazip.zip
  observed: |
    === /tmp/notazip.zip ===
      FAIL  a solution package this is not: File is not a zip file
    exit code: 1
---

Every Dataverse table you build comes with twelve columns you did not create. They are `createdby`,
`createdon`, `createdonbehalfby`, `modifiedby`, `modifiedon`, `modifiedonbehalfby`,
`importsequencenumber`, `overriddencreatedon`, `statecode`, `statuscode`, `timezoneruleversionnumber`
and `utcconversiontimezonecode`. A table that uses owners or business process flows carries eight
more, and `ownerid`, `owninguser`, `owningteam`, `owningbusinessunit`, `processid`, `stageid` and
`traversedpath` are the ones you will meet.

`overriddencreatedon` is the one people get wrong. It does not hold the date its name suggests. Map
your source system's created-on column to it during an import and Dataverse writes that value into
`createdon` and puts the import time into `overriddencreatedon`. Map nothing and `createdon` becomes
the day you ran the import while `overriddencreatedon` stays empty.

So after a migration, a report that reads `overriddencreatedon` as the date a record was really
created is reading your migration date, and a report that reads `createdon` is right, even though the
usual assumption is that a migration flattened it. The override also needs the
`prvOverrideCreatedOnCreatedBy` privilege. That is usually why one team's dates survive a migration
and another team's do not.

`importsequencenumber` does the same job for imports. Every import job stamps one sequence number on
every record it creates, so a single number finds all the rows from one import when something goes
wrong halfway through.

`utcconversiontimezonecode` and `timezoneruleversionnumber` are the platform's own time zone
bookkeeping and sit idle on most tables.

This matters most in two places: a migration that has to keep the original dates, and a report where
"created on" is supposed to mean something. If you are about to build one of these twelve columns
yourself, you almost certainly do not need to.
