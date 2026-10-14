---
title: "Your channel is records, not a setting"
summary: "Bringing a channel into Customer Service is not a toggle or a plugin. It is records in msdyn_ tables, and the samples ship the schema that types every field of them."
surface: dynamics-crm
tip_number: 15
state: ready
next_step: ""
source: "https://github.com/microsoft/Dynamics365-Apps-Samples/blob/master/customer-service/omnichannel/sms-channel-sample-schema/sms-workstream-sample-schema.xml"
artifact: "assets/tips/15-your-channel-is-records-not-a-setting/channel-schema-report.py"
wave: "n/a - Customer Service Omnichannel; release waves were retired in September 2026"
build: "The sample channel schema from the Dynamics 365 apps samples repo (master, 451d0d3, 2026-06-12), read by the artifact"
verified_on: 2026-10-14
verified_env: "Linux, Python 3.14.7 - the sample schema files cloned from the public samples repo, no tenant and no environment"
expires_on: 2027-04-12
cost: "Free to read the samples; a live channel needs Customer Service and the Omnichannel add-on"
evidence: |
  Artifact assets/tips/15-your-channel-is-records-not-a-setting/channel-schema-report.py, run 2026-10-14
  against the clone of microsoft/Dynamics365-Apps-Samples at master (451d0d3, 2026-06-12), command:

      $ python3 channel-schema-report.py sms-channel-sample-schema/sms-workstream-sample-schema.xml

  observed:
      sms-workstream-sample-schema.xml
        msdyn_liveworkstream                    65 fields, 60 custom, table number 10481
             types: string 21, number 15, optionsetvalue 10, entityreference 7, bool 6, datetime 2, optionsetvaluecollection 1, guid 1, state 1, status 1
             lookups point at: msdyn_decisioncontract, msdyn_entityroutingconfiguration, msdyn_masterentityroutingconfiguration, queue, systemuser
        msdyn_liveworkstreamcapacityprofile      4 fields,  3 custom, table number 10537
             types: entityreference 2, string 1, guid 1
             lookups point at: msdyn_capacityprofile, msdyn_liveworkstream
        msdyn_ocliveworkstreamcontextvariable   13 fields, 10 custom, table number 10494
             types: string 4, bool 4, optionsetvalue 1, entityreference 1, guid 1, state 1, status 1
             lookups point at: msdyn_liveworkstream
        msdyn_decisioncontract                   4 fields,  3 custom, table number 10456
             types: string 3, guid 1
        msdyn_decisionruleset                   12 fields, 11 custom, table number 10457
             types: string 4, entityreference 3, optionsetvalue 3, guid 1, bool 1
             lookups point at: msdyn_aimodel, msdyn_decisioncontract
        msdyn_routingconfiguration               5 fields,  4 custom, table number 10467
             types: string 2, guid 1, entityreference 1, bool 1
             lookups point at: msdyn_liveworkstream
        msdyn_routingconfigurationstep           7 fields,  6 custom, table number 10468
             types: string 2, entityreference 2, guid 1, number 1, optionsetvalue 1
             lookups point at: msdyn_decisionruleset, msdyn_routingconfiguration
        msdyn_cannedmessage                      8 fields,  4 custom, table number 10468
             types: string 3, optionsetvalue 1, entityreference 1, guid 1, state 1, status 1
             lookups point at: organization
        msdyn_octag                              2 fields,  1 custom, table number 10509
             types: string 1, guid 1
      
      across 1 file(s): 9 distinct tables, 120 fields (102 of them custom)
      types in use: string 41, entityreference 17, number 16, optionsetvalue 16, bool 12, guid 9, state 3, status 3, datetime 2, optionsetvaluecollection 1

  Across all six schema files in the omnichannel samples folder: 15 distinct tables, 568 fields, and a
  type in use for each. All ten types, in full: string 195, entityreference 85, optionsetvalue 78,
  number 66, bool 59, guid 42, state 15, status 15, datetime 9, optionsetvaluecollection 4 - which sums
  to the 568 fields. Nine of those 15 tables are not named by any of the five sample config files beside them, which
  between them write to 20 tables. Nothing here is quoted from documentation: the docs page for this
  sample (configure-custom-channel) answers 0 bytes to a plain fetch and the develop page asks for
  authorization, so the files are the source.

  The sample schema gives msdyn_cannedmessage and msdyn_routingconfigurationstep the same table number,
  10468. Confirmed by grep: two occurrences of etc="10468" in one file, on two different entities.

  The promotion section is from a second page, fetched 200 on 2026-10-14. Its table "Tables
  automatically added to solution" carries a Voice row and an SMS row, and both list
  "Phone Number (msdyn_ocphonenumber)" - two occurrences of that table name in the page's HTML, missed
  by a first pass over a text conversion of it: "Migrate configurations for
  channels using solutions",
  learn.microsoft.com/en-us/dynamics365/customer-service/administer/migrate-channel-config-using-solutions.
  Quoted from that page, each on its own line, whole, nothing joined and nothing dropped:

      Use solutions and the Configuration Migration tool to migrate the configurations from the source environment to the target environment for channels.
      In the source environment, if any table or column refers to the following, then make sure that they exist in the target environment before you proceed with the migration:
      Custom tables (entities)
      Columns (attributes)
      Relationships
      Choices (option sets)
      Lookup values
      The migration of the account, channel provider, agent configuration, and AI and analytics settings is not in scope.
      You must perform the steps in the order they're listed to migrate your configuration data successfully:
      Migrate configuration for session templates and notification templates
      Migrate configuration for skill-based routing rulesets
      Migrate configuration for new capacity profiles
      Migrate configuration for queues
      Migrate configuration for channel workstreams and channel settings
      Verify your migration

  Source file fetched 2026-10-14: the blob URL above answers 200, raw.githubusercontent.com on master
  answers 200, and the same path on main answers 404.
---

## A channel is rows, not a setting

Bringing your own channel into Customer Service is not a toggle and not a plugin. It is a load of
records into msdyn_ tables: the workstream that decides how a conversation is routed, the capacity
profile behind it, the context variables it carries, the routing configuration and its steps, the
messages and tags. The samples in the Dynamics 365 apps samples repo include the schema for those
tables, and it types every field a channel will write.

## What the schema carries that the portal does not

Each field has a name, a type, and whether it is custom. Lookups name the table they point at, and each
table carries the number the platform uses for it. So a channel being built against the raw API has a
written type list to check its payloads against, instead of a designer to click through.

## Reading it

The schemas are XML, one file per channel's routing, with the channel's config files sitting beside them,
and small enough to read in an editor. Start with the SMS one: it covers the workstream table and the
eight others behind it.

    Select-String -Path sms-workstream-sample-schema.xml -Pattern '<field'

## Promoting it up the chain

A channel is data, so promoting one is a data job: solutions and the Configuration Migration tool, in the
order the dependencies run - templates, then routing rulesets, then capacity profiles, then queues, then
the workstream and its channel settings, then a verification pass. The page is plain that part of it is out of scope: the account,
the channel provider itself, agent configuration, and the AI and analytics settings stay where they are.
The number is the other way round: the page lists phone number among the tables that come with the
solution automatically, so it travels with the rest.

## The table numbers do not always add up

Each table in the schema carries the number the platform uses for it, and the portal does not show you
those. Worth having beside the field list, with one caveat: the sample schema gives the same number,
10468, to two different tables, msdyn_cannedmessage and msdyn_routingconfigurationstep. So read them as
a hint rather than an identifier, and check the one you need against your own environment.
