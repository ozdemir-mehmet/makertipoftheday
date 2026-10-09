---
title: "Your web resource's type lives in a file you never open"
summary: "The resource itself is just bytes - no type, no display name, no GUID. Everything the packer and the platform know about it is in the .data.xml file beside it."
surface: dataverse
tip_number: 6
date: 2026-10-06
wave: "n/a - file format and CLI only; no environment was touched"
build: "pac 2.13.1+g251dee1 on .NET SDK 10.0.400"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), .NET SDK 10.0.400; Microsoft's JavaScriptWebResourceExampleSolution_1_0_managed.zip unpacked with pac, no environment and no login"
expires_on: 2027-03-31
cost: "Free - the CLI, the .NET SDK and the sample package are free; no environment involved"
source: "https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/web-resources"
artifact: "assets/tips/6-your-web-resource-type-is-in-a-sidecar/webresource-sidecars.py"
evidence: |
  command: unzip -l JavaScriptWebResourceExampleSolution_1_0_managed.zip
  observed: |
    WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791
    (inside the package the resource carries no extension at all; the complete member list is in tip 3)

  command: find unpacked/WebResources -type f
  observed: |
    unpacked/WebResources/example_form-script.js
    unpacked/WebResources/example_form-script.js.data.xml

  command: sed -n '1,12p' unpacked/WebResources/example_form-script.js.data.xml
  observed: |
    <?xml version="1.0" encoding="utf-8"?>
    <WebResource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
      <WebResourceId>{aefb6a9a-0ea4-f111-b8dc-7ced8da8a791}</WebResourceId>
      <Name>example_form-script.js</Name>
      <DisplayName>Example form script</DisplayName>
      <Description>Example form script web resource</Description>
      <WebResourceType>3</WebResourceType>
      <IntroducedVersion>1.0</IntroducedVersion>
      <IsEnabledForMobileClient>0</IsEnabledForMobileClient>
      <IsAvailableForMobileOffline>0</IsAvailableForMobileOffline>
      <IsCustomizable>1</IsCustomizable>
      <CanBeDeleted>1</CanBeDeleted>

  command: file -b unpacked/WebResources/example_form-script.js
  observed: ASCII text, with CRLF line terminators

  command: python3 webresource-sidecars.py unpacked
  observed: |
    example_form-script.js                   type 3 (JScript), 'Example form script', {aefb6a9a-0ea4-f111-b8dc-7ced8da8a791}
                                             the file itself: 1734 bytes, extension .js
    exit: 0

  command: cp -r unpacked bare                 # a copy, so the complete tree stays intact
  observed: (nothing on stdout; bare/ holds the same nine files)

  command: mv bare/WebResources/example_form-script.js.data.xml /tmp/kept.xml
            dotnet tool run pac solution pack --zipfile bare.zip --folder bare --packagetype Managed
  observed: |
    Packed Solution.    exit: 0    (no error, no warning)
    bare.zip 5416 bytes, against 6632 for the complete package
    its members:
        17637  customizations.xml
         7033  solution.xml
          191  [Content_Types].xml
    three members, and no WebResources member at all

  command: unzip -p bare.zip solution.xml | grep -oE 'type="61"[^/]*'
  observed: |
    type="61" schemaName="example_form-script.js" behavior="0"
    (the package still declares the component it no longer carries)

  command: python3 webresource-sidecars.py bare
  observed: |
    example_form-script.js                   no .data.xml sidecar - it still packs, but the package then ships no bytes for this component
    exit: 1
---

You can edit a web resource in a solution folder for a year without opening the file that says what it
is.

The resource itself is bytes. In the package it had no extension at all -
`WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791` - and after `pac solution
unpack` it is `example_form-script.js`, a friendlier name than the format gives you. Neither name is the
type. Beside it, the unpacker writes `example_form-script.js.data.xml`, and the component lives there:

    <WebResourceId>{aefb6a9a-0ea4-f111-b8dc-7ced8da8a791}</WebResourceId>
    <Name>example_form-script.js</Name>
    <DisplayName>Example form script</DisplayName>
    <WebResourceType>3</WebResourceType>

`WebResourceType 3` is JScript, and that number, not the extension, is what the platform reads. The
DisplayName is the name a maker sees.

Now move that sidecar out of the way and pack. The packer prints `Packed Solution.` and exits 0. What it
wrote is a package with three members - `customizations.xml`, `solution.xml`,
`[Content_Types].xml` - where the
complete one had four, and `solution.xml` still declares the resource:

    type="61" schemaName="example_form-script.js" behavior="0"

That is a package naming a component it does not carry. Nothing in the build output says so. The file
just gets 1,216 bytes smaller and a web resource stops existing.

So when a resource moves in your solution folder, the pair moves: the file and its `.data.xml`. A repo
that tracks one without the other still builds clean.
