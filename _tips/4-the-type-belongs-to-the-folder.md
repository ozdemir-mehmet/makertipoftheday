---
title: "The package type is the folder's decision, not your flag"
summary: "Managed or unmanaged is not a switch you throw on the way out. The type lives in the folder, and a --packagetype that disagrees with it is refused without writing anything."
surface: dataverse
tip_number: 4
date: 2026-10-04
wave: "n/a - file format and CLI only; no environment was touched"
build: "pac 2.13.1+g251dee1 on .NET SDK 10.0.400"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), .NET SDK 10.0.400; Microsoft's JavaScriptWebResourceExampleSolution_1_0_managed.zip, unpacked with pac and never imported anywhere"
expires_on: 2027-03-31
cost: "Free - the CLI, the .NET SDK and the sample package are free; no environment involved"
source: "https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution"
artifact: "assets/tips/4-the-type-belongs-to-the-folder/package-type.py"
evidence: |
  command: dotnet tool run pac solution unpack --zipfile JavaScriptWebResourceExampleSolution_1_0_managed.zip --folder wrong-type --packagetype Unmanaged
  observed: |
    Error: Solution package type did not match requested type.
    Command line argument: Unmanaged
    Package type: Managed
    files written into wrong-type: 0

  command: grep -o '<Managed>[01]</Managed>' unpacked/Other/Solution.xml
  observed: <Managed>1</Managed>

  command: find unpacked -type f | sort
  observed: |
    AppModules/AccountManagement/AppModule_managed.xml
    AppModuleSiteMaps/AccountManagementSiteMap/AppModuleSiteMap_managed.xml
    Entities/Account/Entity.xml
    Entities/Account/FormXml/main/{8448b78f-8f42-454e-8e2a-f8196b0419af}_managed.xml
    Entities/Account/RibbonDiff.xml
    Other/Customizations.xml
    Other/Solution.xml
    WebResources/example_form-script.js
    WebResources/example_form-script.js.data.xml
    (the _managed suffixes in this tree are the <Managed>1</Managed> above, spelled out by the unpacker)

  command: dotnet tool run pac solution pack --zipfile um.zip --folder unpacked --packagetype Unmanaged
  observed: |
    Error: Solution package type did not match requested type.
    Command line argument: Unmanaged
    Package type: Managed
    (JavaScriptWebResourceExampleSolution 1.0, packed from the folder that carries the <Managed>1</Managed> above)

  command: python3 package-type.py unpacked
  observed: |
    Managed   unpacked/Other/Solution.xml
              <Managed>1</Managed> - every -managed.xml suffix you see came from this bit
    exit: 0

  command: python3 package-type.py unpacked Unmanaged
  observed: |
    REFUSED   you asked for Unmanaged; the folder says Managed
    exit: 1
---

Managed and unmanaged are not two formats you pick between at build time. They are a flag inside the
package, and the tooling on either side refuses to be told otherwise.

Take a managed package and ask the unpacker for the unmanaged one:

    Error: Solution package type did not match requested type.
    Command line argument: Unmanaged
    Package type: Managed

No folder is written. Not a partial one, not a warning-then-continue - the command reads the package,
compares it to what you asked for, and stops. The same thing happens at the other end: unpack a managed
solution, then pack it back asking for `Unmanaged`, and you get the identical refusal.

Where does the answer live? In the folder you unpacked, in `Other/Solution.xml`:

    <Managed>1</Managed>

That one bit is also where the `_managed` suffixes come from. Every `AppModule_managed.xml` and
`{8448b78f-8f42-454e-8e2a-f8196b0419af}_managed.xml` in your working tree is the packer telling you which
tree you are standing in, not something a maker typed.

The practical consequence for a pipeline is that you cannot flip a solution's type as a build step, so
the type has to be a property of the repo folder you check out. If a step reads its argument from a
variable, the failure you get is a message about a mismatch that names your flag - which reads as if you
typed something wrong, when the folder is what decided.
