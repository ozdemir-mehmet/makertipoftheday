---
title: "Read a solution package before you import it: three files and two things that lie to you"
summary: "A Dataverse solution is a zip: three files tell you what you are about to import, and two things inside them mislead you if you read them the obvious way."
surface: dataverse
tip_number: 1
date: 2026-10-01
wave: "n/a - file format only; release waves were retired in September 2026"
build: "MetadataBrowser 4.0.0.0 managed and JavaScriptWebResourceExampleSolution 1.0 managed, from Microsoft's published samples; CoE Core Components 4.50.9 managed"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), Python 3.14.7 - no environment and no login; every package read straight from its published release"
expires_on: 2027-03-31
cost: "Free - a zip reader and the documented type numbers"
source: "https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/solutioncomponent"
artifact: "assets/tips/1-read-a-solution-package-offline/solution-inventory.py"
evidence: |
  command: gh release download MetadataBrowser_v4.0.0.0 -R microsoft/PowerApps-Samples --dir .
  observed: MetadataBrowser_4_0_0_0_managed.zip, 101408 bytes

  command: unzip -l MetadataBrowser_4_0_0_0_managed.zip
  observed: |
      Length      Date    Time    Name
        4149  2026-04-26 21:16   customizations.xml
        5865  2026-04-26 21:16   solution.xml
      393147  2026-04-26 21:16   WebResources/sample_metadatabrowserCBB4EA46-D83D-F111-88B4-000D3A3420A3
         326  2026-04-26 21:16   [Content_Types].xml
      403487                     4 files

  command: python3 solution-inventory.py MetadataBrowser_4_0_0_0_managed.zip JavaScriptWebResourceExampleSolution_1_0_managed.zip
  observed: |
    === MetadataBrowser_4_0_0_0_managed.zip ===
      unique name  : MetadataBrowser
      version      : 4.0.0.0
      managed      : 1  (1 = managed)
      publisher    : microsoftdynamicscrmsdksamples
      components   : 3
           1    61  Web Resource
           1    62  Site Map
           1    80  type 80 - not listed by this script
      payload files: 1
      web resource : sample_/metadatabrowser  (type 1 Webpage; extension should be .html; the name carries none either)
        in the zip : WebResources/sample_metadatabrowserCBB4EA46-D83D-F111-88B4-000D3A3420A3   <-- no extension on disk
    === JavaScriptWebResourceExampleSolution_1_0_managed.zip ===
      unique name  : JavaScriptWebResourceExampleSolution
      version      : 1.0
      managed      : 1  (1 = managed)
      publisher    : ExamplePublisher
      components   : 4
           1     1  Entity (table)
           1    61  Web Resource
           1    62  Site Map
           1    80  type 80 - not listed by this script
      payload files: 1
      web resource : example_form-script.js  (type 3 Script; extension should be .js)
        in the zip : WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791   <-- no extension on disk
    exit: 0

  command: unzip -o MetadataBrowser_4_0_0_0_managed.zip customizations.xml && grep -c "<Entities>" customizations.xml && grep -oE "<Entity[ >]" customizations.xml | wc -l && grep -c "<RootComponent " solution.xml
  observed: |
      <Entities>        1
      <Entity> elements 0
      root components   3

  command: grep -c "|80|" solutioncomponent.md    # the reference page the front matter cites
  observed: 0

  command: grep -nE "^\| *(63|66|431|432) *\|" solutioncomponent.md
  observed: |
      134:|63|**Connection Role**|
      137:|66|**Custom Control**|
      174:|431|**Attribute Image Configuration**|
      175:|432|**Entity Image Configuration**|
    (so the script's table was wrong to call 63 a custom control - that is 66 - and 431 and 432 are
    documented, which is why the table now carries them by name rather than printing an unknown-type
    label for them)

  command: python3 solution-inventory.py coe.zip   # CoE Core Components 4.50.9 managed, for the type mix
  observed: |
    components   : 337
       120    29  Workflow (process)
        69   300  Canvas App
        55    61  Web Resource
        46     1  Entity (table)
         9    62  Site Map
         9    80  type 80 - not listed by this script
         2   431  Attribute Image Configuration
         2   432  Entity Image Configuration
    (the eight most common types; 337 components in total; exit 0)

  command: python3 solution-inventory.py /etc/hostname
  observed: |
    FAIL  /etc/hostname: File is not a zip file
    exit: 1

  note: type 80 is absent from the solutioncomponent reference page the front matter cites - the table
  was grepped for a row and there is none, which is the claim this tip makes. Its neighbours are not
  absent: the same page documents 431 and 432 as Attribute Image Configuration and Entity Image
  Configuration, so this script's table carries those two by name.
---

A Dataverse solution is a zip file, and you can read it without an environment, a login or a single
`pac` command. Two files inside it carry most of what you need to know before an import.

`solution.xml` is the identity: the unique name, the version, whether the package is managed, the
publisher, and a `<RootComponents>` list in which every component is a type number and nothing more.
`customizations.xml` is the payload - tables, columns, forms, views. `[Content_Types].xml` keeps
SolutionPackager happy and tells you nothing.

## `customizations.xml` declares things the package does not carry

It declares `Entities`, `Roles`, `Workflows` and
`WebResources` whether or not the package carries any. Microsoft's metadata sample has three root
components and not one of them is a table, yet its `<Entities>` element is there with nothing inside it
- zero `<Entity>` elements in the file - which is enough for a quick look to conclude that the solution
carries a table. What the package actually changes is `<RootComponents>` in `solution.xml`.

## The web resource payload has no extension

Inside the zip a file is named after its logical name with the
dot removed and the resource's uppercase GUID glued on: `example_form-script.js` becomes
`WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791`. There is no extension, so
editors, diff tools and packers each guess the type and each guess differently. The only honest source
is `<WebResourceType>`, where 3 means a script. The logical name is not a hint either: Microsoft's own
metadata sample ships a resource called `sample_/metadatabrowser`, which carries no extension and is a
web page.

## The published type table is not the whole set

Microsoft's metadata sample declares type 80, the CoE starter kit ships nine of them, and the
reference page has no row for 80 at all. Tooling that treats the documented list as exhaustive drops
those components on the floor.

A managed solution cannot be edited once it is in the target environment, and an import that fails
halfway leaves you diagnosing from the portal. Thirty seconds with the zip - how many components, of
which types, and which web resources - is the difference between a five-minute import and an
afternoon.
