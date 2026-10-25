---
title: "Every connection reference arrives in the target environment unconnected"
summary: "pac solution create-settings writes each connection reference with an empty ConnectionId, so the import has nothing to bind and the connections are still supplied in the UI afterwards."
surface: alm-governance
tip_number: 24
date: 2026-10-24
wave: "n/a - a CLI behaviour and a documented deployment setting, not a release wave"
build: "pac 2.13.1+g251dee1 (.NET 10.0.11) run locally; sample microsoft/CopilotStudioSamples@c615dea2eb69; Learn page fetched 2026-10-25"
verified_on: 2026-10-25
verified_env: "Linux (CachyOS), no tenant and no sign-in - pac solution pack and create-settings run against a public sample solution folder on disk, and the Learn page is fetched the same day; no solution was imported anywhere"
expires_on: 2027-04-24
cost: "Free to measure - pac CLI only. Importing the solution and running the flows it carries needs a licensed environment for those connectors"
source: "https://learn.microsoft.com/en-us/power-platform/alm/conn-ref-env-variables-build-tools"
artifact: "assets/tips/24-connection-references-arrive-unconnected/probe.py"
evidence: |
  run 2026-10-25. Executed offline: a Microsoft sample solution folder was packed with pac and
  create-settings run on the zip on this machine. No tenant, so no solution was imported and no flow was
  turned on - the import behaviour is the documented half.

  The date 2026-10-24 is a backfill: the tip was written and verified on 2026-10-25 for the day that had
  no tip, which backfilling allows and a future date refuses.

  command: PYTHONDONTWRITEBYTECODE=1 python3 assets/tips/24-connection-references-arrive-unconnected/probe.py

  observed:
    sample: microsoft/CopilotStudioSamples@c615dea2eb69  infrastructure/manage-paygo/sourcecode/Other/Customizations.xml
    sha256: 4f471298dc2dd108199020855e90ebe5bfdf557ada6f873f29e3c9b9c622e85c
    connection references in the settings file: 4
    references with an empty ConnectionId: 4
    distinct connectors: 3
    connector used by more than one reference (2): shared_powerplatformadminv2
        mcscat_sharedpowerplatformadminv2_df188
        new_sharedpowerplatformadminv2_498a1
    publisher prefixes in the reference names: mcscat, new
    environment variables in the settings file: 0
    page: https://learn.microsoft.com/en-us/power-platform/alm/conn-ref-env-variables-build-tools
      canonical matches: True
      quotes present: 7/7
    result: every reference is emitted with no connection, and one connector is named twice
    result: numbers and quotes both reproduce the evidence block
  exit 0

  The four entries, quoted from the settings file this run wrote, each one line as the file has it:

    "LogicalName": "mcscat_sharedazureusage5fcb336cc1377ded3a5fe4caae088dbe83f8_63b07", "ConnectionId": "", "ConnectorId": "/providers/Microsoft.PowerApps/apis/shared_azureusage-5fcb336cc1377ded3a-5fe4caae088dbe83f8"
    "LogicalName": "mcscat_sharedpowerplatformadminv2_df188", "ConnectionId": "", "ConnectorId": "/providers/Microsoft.PowerApps/apis/shared_powerplatformadminv2"
    "LogicalName": "mcscat_sharedpowerplatformbilliinpolicy5fcb336cc1377ded3a5fe4caae088dbe_25348", "ConnectionId": "", "ConnectorId": "/providers/Microsoft.PowerApps/apis/shared_powerplatformbilliinpolicy-5fcb336cc1377ded3a-5fe4caae088dbe83f8"
    "LogicalName": "new_sharedpowerplatformadminv2_498a1", "ConnectionId": "", "ConnectorId": "/providers/Microsoft.PowerApps/apis/shared_powerplatformadminv2"

  Quoted sentences, in page order, each matched whole by the run:

    "After importing a solution containing connection reference and environment variable information, you are prompted to provide information specific to your environment in the UI."
    "To enable a fully automated deployment, you can now pre-populate the connection reference and environment variable information specific to the target environment so that you don't have to interactively provide it after importing a solution."
    "To populate the deployment settings file, you will need to obtain the connection reference and environment variable information of the target solution."
    "To get the connection ID of the target environment, use one of the following ways:"
    "This will create the required connection reference and environments with appropriate values upon import without having the user to interactively specify the value."
    "During solution import, the connection references are validated to ensure that the connections placed inside them will be usable by the owner of the connection reference."
    "Ensure that the connections are owned by the owner of the connection references or that the connections are shared ."

  The fix rests on three of those: step 2 says the connection ID comes from the target environment, the
  Validation sentence says the import checks the connection against the owner of the reference, and the
  prompt sentence is why the body says the connections are still supplied in the UI. The import verb and
  its --settings-file parameter come from the pac help text run on this machine:

    pac solution import --settings-file   The .json file with the deployment settings for connection references and environment variables.

  NOT claimed: that the import fails. The page says what the file supplies is what the import applies to
  each reference and that without it you are prompted in the UI, so an empty file leaves the connections
  to be supplied afterwards. It never says an import carrying empty ConnectionId values errors, and
  nothing here was imported to find out.
---

You export a solution, generate the deployment settings file with `pac solution create-settings`, and hand it to the pipeline. Every entry the file writes carries an empty `ConnectionId`, so the import has no connection to attach to any of the references, and the target environment's connections are still supplied in the UI afterwards - the manual step the file exists to remove.

`pac solution create-settings` reads the solution's connection references and writes one entry per reference, with the logical name and the connector filled in and the connection left as an empty string. Each entry carries its own `ConnectionId`, and two entries can name the same connector, so a connector is not a key you fill once.

Fill `ConnectionId` on every entry with the ID of a connection in the target environment, read from that environment's Connection References table, then import with the file: `pac solution import --settings-file`, or the Build Tools Import Solution task with Use deployment settings file and the path to it. The import checks that the connection is usable by the owner of the reference, so use one that owner owns or one that is shared.
