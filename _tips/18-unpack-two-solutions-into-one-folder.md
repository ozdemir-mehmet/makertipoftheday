---
title: "Unpack a second solution into the same folder and pac will not pack it"
summary: "pac solution unpack prints 'Not deleting files' and leaves the earlier solution's components behind, so the next pack fails RootComponent validation."
surface: solution-packaging
tip_number: 18
wave: "n/a - pac CLI behaviour, not a release wave"
build: "pac CLI 2.13.1+g251dee1 on .NET 10.0.11; MetadataBrowser_4_0_0_0_managed.zip sha256 adeb61f9fcb4966d50405d299d8ae4534071550f0b146156b0eedfc969419cc1 and JavaScriptWebResourceExampleSolution_1_0_managed.zip sha256 3d94d4dc7e63d336d2bf12721df9af470fa7c4f0a60f1ed8c88784c309831570, both from microsoft/PowerApps-Samples releases"
date: 2026-10-21
verified_on: 2026-10-22
verified_env: "Linux (CachyOS), pac CLI 2.13.1 installed locally against .NET SDK 10.0.400; no environment and no login - two published Microsoft sample solutions unpacked and packed on disk"
expires_on: 2027-04-15
cost: "Free - pac CLI and the sample packages need no licence"
source: "https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution"
artifact: "assets/tips/18-unpack-two-solutions-into-one-folder/check-unpack-folder.py"
evidence: |
  run 2026-10-17, pac CLI 2.13.1+g251dee1 (.NET 10.0.11), Linux, no tenant.
  re-run 2026-10-22 at promotion, same two zips re-downloaded from the microsoft/PowerApps-Samples
  releases and both sha256 hashes matched the ones recorded above: five checks ok, exit 0.

  re-runnable: python3 assets/tips/18-unpack-two-solutions-into-one-folder/check-unpack-folder.py
               --zip-a MetadataBrowser_4_0_0_0_managed.zip
               --zip-b JavaScriptWebResourceExampleSolution_1_0_managed.zip
  observed:
    ok    second unpack says it deletes nothing: Not deleting files
    ok    folder identity becomes solution B: 'MetadataBrowser' -> 'JavaScriptWebResourceExampleSolution'
    ok    solution A's files are still present: 6 files -> 13
    ok    packing the mixed folder fails RootComponent validation: Error: RootComponent validation failed.
    ok    packing a clean folder of the same solution succeeds: 4 file(s) packed
    exit 0

  raw transcript behind those checks:

  command: pac solution unpack --zipfile MetadataBrowser_4_0_0_0_managed.zip --folder A --packagetype Managed
  observed:
    Managed Extract complete.
    Unpacked Solution.
    find A -type f | wc -l   ->  6
    A/Other/Solution.xml  UniqueName MetadataBrowser, publisher microsoftdynamicscrmsdksamples

  command: echo "leftover from a branch I deleted" > A/stray-from-old-build.txt
           pac solution unpack --zipfile JavaScriptWebResourceExampleSolution_1_0_managed.zip --folder A --packagetype Managed
  observed:
    Not deleting files
    Unpacked Solution.
    grep UniqueName A/Other/Solution.xml  ->  JavaScriptWebResourceExampleSolution   (solution 2's identity replaced solution 1's)
    find A -type f | sort  ->  14 files, including
      A/AppModules/sample_MetadataBrowser/AppModule_managed.xml
      A/AppModuleSiteMaps/sample_MetadataBrowser/AppModuleSiteMap_managed.xml
      A/WebResources/sample_/metadatabrowser
      A/WebResources/sample_/metadatabrowser.data.xml
      A/stray-from-old-build.txt

  command: pac solution pack --zipfile mixed.zip --folder A --packagetype Managed
  observed:
    Processing Component: WebResources
     - example_form-script.js
     - sample_/metadatabrowser
    ...
    Following objects, required by the solution, are not present.
      Type='WebResource', Id (or schema name)='WebResource-sample_/metadatabrowser'.
      Type='SiteMap', Id (or schema name)='SiteMap-sample_MetadataBrowser'.
      Type='AppModule', Id (or schema name)='AppModule-sample_MetadataBrowser'.
    Error: RootComponent validation failed.
    (no mixed.zip written)

  control: pac solution pack --zipfile clean.zip --folder B --packagetype Managed
  observed:
    Packed Solution.
    unzip -l clean.zip  ->  4 files: customizations.xml, solution.xml,
      WebResources/sample_metadatabrowserCBB4EA46-D83D-F111-88B4-000D3A3420A3, [Content_Types].xml
    solution.xml UniqueName  ->  MetadataBrowser, publisher microsoftdynamicscrmsdksamples

  second unpack printed "Not deleting files" and did not remove solution 1's component folders,
  so the folder held two solutions' root components while its Solution.xml named only the second.
---



Unpack a second solution into a folder that already holds one and pac tells you what it is doing:

```
Not deleting files
Unpacked Solution.
```

That line is the whole warning. `pac solution unpack` writes the second solution's `Other/Solution.xml` over
the first one's, so the folder's identity becomes the solution you just unpacked, and every component folder
the first solution brought is still sitting beside it. The folder now describes one solution and contains the
root components of two.

The failure lands at pack time:

```
Following objects, required by the solution, are not present.
  Type='WebResource', Id (or schema name)='WebResource-sample_/metadatabrowser'.
  Type='SiteMap', Id (or schema name)='SiteMap-sample_MetadataBrowser'.
  Type='AppModule', Id (or schema name)='AppModule-sample_MetadataBrowser'.
Error: RootComponent validation failed.
```

Read that list carefully, because it is misleading: no object is missing from your source system and no
dependency is broken. The same run lists `sample_/metadatabrowser` under `Processing Component: WebResources`
two lines after calling it absent. Those are the previous solution's components, and the new `Solution.xml`
knows nothing about them, so the packer cannot place them in the package it builds.

It bites hardest in a build that keeps one workspace folder and unpacks whatever export it is handed: the
first solution goes fine, then a different export arrives and the build starts failing on a dependency error
that describes files sitting right there on disk. Chasing the dependency is a dead end.

Unpack into an empty folder. Delete the workspace before each unpack instead of reusing it:

```
pac solution unpack --zipfile SolutionOne_1_0_0_0_managed.zip --folder work --packagetype Managed
pac solution unpack --zipfile SolutionTwo_1_0_0_0_managed.zip --folder work --packagetype Managed
pac solution pack --zipfile out.zip --folder work --packagetype Managed
```

Delete `work`, unpack only the second zip, and that pack succeeds.
