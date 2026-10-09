---
title: "The file that is in every package and in no unpacked folder"
summary: "Every solution package carries a [Content_Types].xml that no unpacked folder ever has, and it names the exact parts the import will read."
surface: cross-cutting
tip_number: 8
date: 2026-10-08
wave: "n/a - file format and CLI only; no environment was touched"
build: "pac 2.13.1+g251dee1 on .NET SDK 10.0.400"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), .NET SDK 10.0.400; Microsoft's JavaScriptWebResourceExampleSolution_1_0_managed.zip and the same solution re-packed with pac"
expires_on: 2027-03-31
cost: "Free - the CLI, the .NET SDK and the sample package are free; no environment involved"
source: "https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm"
artifact: "assets/tips/8-content-types-is-in-every-package/content-types-report.py"
evidence: |
  command: unzip -l same1.zip
  observed: |
    customizations.xml
    solution.xml
    WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791
    [Content_Types].xml

  command: cat '[Content_Types].xml'          # from inside the re-packed package
  observed: |
    <?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/octet-stream" /><Override PartName="/WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791" ContentType="application/octet-stream" /></Types>

  command: cat '[Content_Types].xml'          # from Microsoft's own published package
  observed: |
    byte for byte the same file, including the part name above

  command: find unpacked -name '[Content_Types].xml' | wc -l
  observed: 0

  command: python3 content-types-report.py same1.zip unpacked
  observed: |
    in the package:       [Content_Types].xml, 322 bytes, declaring 1 part(s)
                            /WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791
                          and 3 other member(s) alongside it
    in unpacked:  0 file(s) of that name
                          the unpacker never writes one; the packer always does
    exit: 0
---

Every solution package carries a `[Content_Types].xml`, and no unpacked solution folder ever has one.

It is the package's list of parts, written in the container's vocabulary rather than the platform's:

    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
      <Default Extension="xml" ContentType="application/octet-stream" />
      <Override PartName="/WebResources/example_form-scriptjsAEFB6A9A-0EA4-F111-B8DC-7CED8DA8A791"
                ContentType="application/octet-stream" />
    </Types>

Three hundred and twenty-two bytes, naming the one part that is not an XML file, with a default that
covers the ones that are. Microsoft's published package and the package you pack from its unpacked
folder hold that file byte for byte - the same default, the same override, the same GUID.

The asymmetry is the part worth knowing. `pac solution unpack` never writes it, so it cannot live in
your repository and you cannot break it by editing the folder. `pac solution pack` always writes it, so
it turns up in every artifact you build. It is the only member of the package that describes the
package.

If you compare two packages part by part to find what changed, this is the part that will never tell you
anything. It is also the part nobody remembers when a package is assembled by hand - and the one that
says what the other parts are.
