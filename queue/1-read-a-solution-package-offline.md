---
title: "Read a solution package before you import it: three files and two things that lie to you"
summary: "A Dataverse solution is a zip: three files tell you what you are about to import, and two of them mislead you if you read them the obvious way."
surface: dataverse
tip_number: 1
wave: "n/a - file format only; release waves were retired in September 2026"
build: "MetadataBrowser 4.0.0.0 managed and JavaScriptWebResourceExampleSolution 1.0 managed, both from Microsoft's published samples"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), Python 3.14.7 - no environment and no login; both packages were read straight from Microsoft's published sample releases"
expires_on: 2027-03-31
cost: "Free - a zip reader and the documented component numbers"
source: "https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/solutioncomponent"
artifact: "assets/tips/1-read-a-solution-package-offline/solution-inventory.py"
state: ready
evidence: |
  command: unzip -l MetadataBrowser_4_0_0_0_managed.zip
  observed: |
    Length      Date    Time    Name
    4149  2026-04-26 21:16   customizations.xml
    5865  2026-04-26 21:16   solution.xml
  393147  2026-04-26 21:16   WebResources/sample_metadatabrowserCBB4EA46-D83D-F111-88B4-000D3A3420A3
     326  2026-04-26 21:16   [Content_Types].xml
    403487                     4 files

  command: python3 solution-inventory.py MetadataBrowser.zip JsWebResource.zip
  observed: |
    === MetadataBrowser.zip ===
      unique name  : MetadataBrowser
      version      : 4.0.0.0
      managed      : 1  (1 = managed)
      publisher    : microsoftdynamicscrmsdksamples
      components   : 3
           1    61  Web Resource
           1    62  Site Map
           1    80  type 80 - not in the documented component list
      payload files: 1
      web resource : sample_/metadatabrowser  (type 1 Webpage; extension should be .html; the name carries none either)
        in the zip : WebResources/sample_metadatabrowserCBB4EA46-D83D-F111-88B4-000D3A3420A3   <-- no extension on disk

    === JsWebResource.zip ===
      unique name  : JavaScriptWebResourceExampleSolution
      version      : 1.0
      managed      : 1  (1 = managed)
      publisher    : ExamplePublisher
      components   : 4
           1     1  Entity (table)
           1    61  Web Resource
           1    62  Site Map
           1    80  type 80 - not in the documented component list
      payload files: 1
      web resource : example_form-script.js  (type 3 Script; extension should be .js)
        in the zip : WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791   <-- no extension on disk

  command: python3 solution-inventory.py /etc/hostname
  observed: |
    FAIL  /etc/hostname: File is not a zip file
    exit code: 1

  command: grep -nE "^\\|(1|61|62|80)\\|" solutioncomponent.md   # the vendor's docs source
  observed: |
    86:|1|**Entity**|
    132:|61|**Web Resource**|
    133:|62|**Site Map**|
    (no row for 80)
---

**tl;dr** A Dataverse solution is a zip you can read offline: `solution.xml` holds the identity and the
root components, `customizations.xml` holds the payload, `[Content_Types].xml` keeps SolutionPackager
happy. Reading those three files tells you what you are about to import, with no environment and no
login. Two things in there will mislead you if you read them the obvious way.

## The two that lie

**`customizations.xml` declares containers it does not use.** Every solution carries the elements
`Entities`, `Roles`, `Workflows`, `Templates`, `EntityMaps`, `WebResources` and more, whether or not
anything is in them. Grepping for `<Entity>` or for an element's presence tells you nothing at all. The
truth is `<RootComponents>` in `solution.xml`, where each component is a type number and nothing else.

**Web resource files have no extension, and the name does not save you.** Inside the zip the file is
named after the logical name with the dot removed and the uppercased resource GUID glued on:
`example_form-script.js` becomes `WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791`.
Editors, diff tools and packers all guess wrong about it. The extension is only in `<WebResourceType>`
(3 = Script), and Microsoft's own MetadataBrowser sample is named `sample_/metadatabrowser` with no
extension at all, so the logical name is not a reliable hint either.

## One more worth knowing

The component and web resource type numbers are documented, but the documented component table is not
complete: Microsoft's own sample solutions declare `type 80`, and the reference page has no row for 80.
Build tooling that treats the published list as exhaustive and you will drop components on the floor.
The artifact reports an unknown type as unknown instead of guessing.

## Using it

`python3 solution-inventory.py <solution.zip> [more.zip ...]` prints the unique name, version, managed
flag, publisher, the component mix by documented type, the payload file count, and every web resource
with its type number, its expected extension and whether the name carries one. Exit 0 when everything
parses, 1 when a file is not a solution.

## Why this is worth thirty seconds before an import

A managed solution cannot be edited in the target environment, and an import that fails halfway leaves
you diagnosing in the portal. Knowing that the package carries one table, one web resource and a site
map - and that the site map is type 62, so it will overwrite one - is the difference between a
five-minute import and an afternoon.
