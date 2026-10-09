---
title: "Your table has twelve columns you did not create, and one of them rewrites Created On"
summary: "Measured, not claimed: the 46 tables in the CoE Starter Kit carry 12 columns nobody created, and mapping a source date to overriddencreatedon puts it in createdon instead."
surface: dataverse
tip_number: 14
date: 2026-10-09
wave: "n/a - solution package format; release waves were retired in September 2026"
build: "CenterofExcellenceCoreComponents 4.50.9 managed (released 2026-02-10), MetadataBrowser 4.0.0.0 managed"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), Python 3.14.7 - no environment and no login; every count comes from Microsoft's own published solution packages"
expires_on: 2027-03-31
cost: "Free - the columns exist on every table already; the import needs prvOverrideCreatedOnCreatedBy, nothing premium"
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

**Tip**

Count them once on your own table and you stop re-creating them. Every Dataverse table carries a
fixed set of columns the maker never authored, and the count is not a guess: in Microsoft's own CoE
Starter Kit release, 46 tables carry **1,586 columns between them, 812 of which nobody created**, and
the same **twelve** appear on all 46 -

`createdby`, `createdon`, `createdonbehalfby`, `modifiedby`, `modifiedon`, `modifiedonbehalfby`,
`importsequencenumber`, `overriddencreatedon`, `statecode`, `statuscode`, `timezoneruleversionnumber`,
`utcconversiontimezonecode`

Tables that use owners or business process flows add more (`ownerid`, `owninguser`, `owningteam`,
`owningbusinessunit`, `processid`, `stageid`, `traversedpath`) - `admin_App` carries 20 in total.

**The one that surprises people is `overriddencreatedon`**, because the mapping is the reverse of
what the name suggests:

> To import data in the createdon column, map the source column that contains this data to the
> overriddencreatedon column. During import, the record's createdon column is updated with the value
> that was mapped to the overriddencreatedon column and the overriddencreatedon column is set to the
> date and time that the data was imported.

So after a migration, `createdon` holds the original date (the one you mapped) and
`overriddencreatedon` holds the day you ran the import - not the other way round. Any report that reads
`overriddencreatedon` as "when the record was really created" is reading the migration date. Map
nothing and `createdon` becomes the import date and `overriddencreatedon` stays empty.

**And `importsequencenumber` is how you audit one import.** Each import job stores a unique sequence
number in that column on every record it creates, so one number identifies exactly the rows a given
import produced - which is the question you actually have when something goes wrong halfway.

**Try it**

Run the artifact against a solution you ship and get your own numbers in the first three lines.
