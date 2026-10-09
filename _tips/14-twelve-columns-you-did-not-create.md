---
title: "Your table has twelve columns you did not create, and one of them rewrites Created On"
summary: "Every Dataverse table carries twelve columns nobody created - and mapping a source date to overriddencreatedon puts it in createdon instead."
surface: dataverse
tip_number: 14
date: 2026-10-09
wave: "n/a - solution package format; release waves were retired in September 2026"
build: "CenterofExcellenceCoreComponents 4.50.9 managed, MetadataBrowser 4.0.0.0 managed"
verified_on: 2026-10-09
verified_env: "Linux, Python 3.14.7 - no environment, no login; read from published solution packages"
expires_on: 2027-03-31
cost: "Free - no premium connector, no capacity; overriding Created On needs prvOverrideCreatedOnCreatedBy"
source: "https://learn.microsoft.com/en-us/power-apps/developer/data-platform/run-data-import"
artifact: "assets/tips/14-twelve-columns-you-did-not-create/table-columns.py"
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

Twelve columns turn up on every Dataverse table you build and you did not create a single one of them:
`createdby`, `createdon`, `createdonbehalfby`, `modifiedby`, `modifiedon`, `modifiedonbehalfby`,
`importsequencenumber`, `overriddencreatedon`, `statecode`, `statuscode`, `timezoneruleversionnumber`
and `utcconversiontimezonecode`. Tables that use owners or business process flows carry eight more:
`ownerid`, `owninguser`, `owningteam`, `owningbusinessunit`, `processid`, `stageid` and `traversedpath`.

The one to understand is `overriddencreatedon`, because it does not hold the date its name suggests.
Map your source system's created-on column to it during an import and Dataverse writes that value into
`createdon` - the column everyone actually reads - and stamps the import time into
`overriddencreatedon` instead. Map nothing and `createdon` becomes the day you ran the import, while
`overriddencreatedon` stays empty.

Which means, after a migration, a report that reads `overriddencreatedon` as "when this was really
created" is reading your migration date, and a report that reads `createdon` is right - even though
the usual assumption is that a migration flattened it. The override also needs the
`prvOverrideCreatedOnCreatedBy` privilege, and that is the ordinary reason one team's dates survive a
migration while another's do not.

Two more on the list earn their keep:

- `importsequencenumber` is the audit handle for a single import. Each import job stamps one unique
  sequence number on every record it creates, so that one number finds exactly the rows a run
  produced - which is the question you have when an import goes wrong halfway through.
- `utcconversiontimezonecode` and `timezoneruleversionnumber` are the platform's own time zone
  bookkeeping. They sit idle on most tables.

Where it pays: a migration that has to preserve original dates, a report where "created on" has to
mean something, and a schema review where somebody is about to build a column that already exists.

Want the list for your own tables? [table-columns.py](/assets/tips/14-twelve-columns-you-did-not-create/table-columns.py)
prints it for any solution package you point it at.
