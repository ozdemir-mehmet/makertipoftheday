---
title: "You cannot unzip a solution and pack it back"
summary: "A solution zip and an unpacked solution are different shapes on disk. The packer refuses the zip's shape, naming a file that is sitting right there."
surface: cross-cutting
tip_number: 3
date: 2026-10-03
wave: "n/a - file format and CLI only; no environment was touched"
build: "pac 2.13.1+g251dee1 on .NET SDK 10.0.400"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), .NET SDK 10.0.400; Microsoft's JavaScriptWebResourceExampleSolution_1_0_managed.zip read straight from the published release, no environment and no login"
expires_on: 2027-03-31
cost: "Free - the CLI, the .NET SDK and the sample package are free; no environment involved"
source: "https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution"
artifact: "assets/tips/3-unzip-is-not-unpack/check-packable.py"
evidence: |
  command: unzip -q JavaScriptWebResourceExampleSolution_1_0_managed.zip -d plain
  observed: |
    plain/[Content_Types].xml
    plain/customizations.xml
    plain/solution.xml
    plain/WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791
    (4 files)

  command: dotnet tool run pac solution pack --zipfile from-plain.zip --folder plain --packagetype Managed
  observed: |
    Error: Cannot find required file '.../plain/Other/Customizations.xml'.
    (and customizations.xml is sitting in that folder - one directory level off)

  command: dotnet tool run pac solution unpack --zipfile JavaScriptWebResourceExampleSolution_1_0_managed.zip --folder unpacked --packagetype Managed
  observed: |
    Unpacked Solution.
    AppModules/AccountManagement/AppModule_managed.xml
    AppModuleSiteMaps/AccountManagementSiteMap/AppModuleSiteMap_managed.xml
    Entities/Account/Entity.xml
    Entities/Account/FormXml/main/{8448b78f-8f42-454e-8e2a-f8196b0419af}_managed.xml
    Entities/Account/RibbonDiff.xml
    Other/Customizations.xml
    Other/Solution.xml
    WebResources/example_form-script.js
    WebResources/example_form-script.js.data.xml
    files in the unpacked tree: 9; in the zip: 4

  command: python3 check-packable.py plain            # and against the unpacked folder
  observed: |
    REFUSED   plain is missing Other/Solution.xml and Other/Customizations.xml
              but it does carry solution.xml, customizations.xml at the top level,
              which is the shape inside the zip, not the shape on disk.
              run `pac solution unpack` first.
    exit: 1
    ---
    packable  unpacked has Other/Solution.xml and Other/Customizations.xml
    exit: 0
---

The zip you import is not the folder you edit. Inside the package a solution is four members at the top
level: `solution.xml`, `customizations.xml`, `[Content_Types].xml`, and a `WebResources` folder whose
files are named after their logical name with the dot removed and the component's GUID glued on.
`pac solution pack` will not touch that shape.

Try the obvious thing - unzip the package, point the packer at the folder you just made - and this is
what you get:

    Error: Cannot find required file '.../plain/Other/Customizations.xml'.

`customizations.xml` was sitting in the folder you just named. The packer was looking one level
lower, for `Other/Customizations.xml`, with `Other/Solution.xml` beside it - because the folder it
accepts is the one `pac solution unpack` writes, not the one a zip contains. Unpack the same package and
you get nine files: components under `Entities/` with their forms and `RibbonDiff.xml`, the app module
and its site map under `AppModules/` and `AppModuleSiteMaps/`, web resources under `WebResources/` with
their real extensions and a `.data.xml` sidecar each, and the two XML files under `Other/`.

Four members in the package, nine files on disk, and the resource that had no extension at all is now a
`.js` file with a `.data.xml` sidecar beside it. So the working folder is
always `pac solution unpack`, never `unzip` - and if your pipeline unzips a solution to get at a web
resource, it is editing a folder that can never be packed back.

If `solution.xml` is sitting at the top of the folder you are about to pack, the packer is going to look
for the one under `Other/` and fail on a file you can see.
