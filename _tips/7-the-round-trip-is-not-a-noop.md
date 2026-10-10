---
title: "The round trip is not a no-op"
summary: "Unpack a package and pack it back and you do not get the file you started with: the XML gains a declaration, the line endings change, and the empty containers come back collapsed."
surface: solution-packaging
tip_number: 7
date: 2026-10-07
wave: "n/a - file format and CLI only; no environment was touched"
build: "pac 2.13.1+g251dee1 on .NET SDK 10.0.400"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), .NET SDK 10.0.400; Microsoft's JavaScriptWebResourceExampleSolution_1_0_managed.zip, unpacked and re-packed on the same host"
expires_on: 2027-03-31
cost: "Free - the CLI, the .NET SDK and the sample package are free; no environment involved"
source: "https://learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool"
artifact: "assets/tips/7-the-round-trip-is-not-a-noop/roundtrip-diff.py"
evidence: |
  command: dotnet tool run pac solution unpack ... --folder unpacked --packagetype Managed
            dotnet tool run pac solution pack --zipfile same1.zip --folder unpacked --packagetype Managed
            unzip -q same1.zip -d s1     # then compare s1 with the package's own layout

  command: head the first line of solution.xml in each
  observed: |
    original package : <ImportExportXml version="9.2.26083.148" SolutionPackageVersion="9.2" ...
    re-packed        : <?xml version="1.0" encoding="utf-8"?>

  command: for n in Roles Workflows FieldSecurityProfiles; do grep -o "<$n[^>]*>" plain/customizations.xml s1/customizations.xml; done
  observed: |
    original  <Roles>                  <Workflows>                  <FieldSecurityProfiles>
    repacked  <Roles />                <Workflows />                <FieldSecurityProfiles />
    (the same three elements in both files - open tags with nothing inside before, collapsed empties after)

  command: python3 roundtrip-diff.py plain s1
  observed: |
    solution.xml
      first line, original: <ImportExportXml version="9.2.26083.148" SolutionPac
      first line, repacked: <?xml version="1.0" encoding="utf-8"?>
    customizations.xml
      first line, original: <ImportExportXml xmlns:xsi="http://www.w3.org/2001/X
      first line, repacked: <?xml version="1.0" encoding="utf-8"?>
      line endings: CRLF in the original, LF in the repacked file
      Roles                  <Roles> -> <Roles />
      Workflows              <Workflows> -> <Workflows />
      FieldSecurityProfiles  <FieldSecurityProfiles> -> <FieldSecurityProfiles />
    the files differ
    exit: 1
---

Diff a package against the one you packed it from, and you will find changes nobody made. The round
trip through `unpack` and `pack` rewrites both XML files, and every difference is in the wrapper rather
than the solution.

The `solution.xml` inside Microsoft's own package opens like this:

    <ImportExportXml version="9.2.26083.148" SolutionPackageVersion="9.2" ...

Pack the folder it unpacked to, and the same file opens with an XML declaration the original did not
carry:

    <?xml version="1.0" encoding="utf-8"?>

`customizations.xml` is the one that moves more. The original carries `<Roles>`, `<Workflows>` and
`<FieldSecurityProfiles>` as open tags with nothing inside them, and all three come back collapsed to
`<Roles />`, `<Workflows />` and `<FieldSecurityProfiles />`. The line endings change as well - the member
inside the package is CRLF and the file you pack back is LF - which on its own is a whole-file diff, before
you have changed anything. In
Microsoft's sample neither a role, a workflow, nor a field security profile is anywhere in the package.

You did not make any of those changes - the writer puts back the elements the reader elides. A
diff between "the package I imported last week" and "the package I built today" is not a diff of the
solution: the first line of the file differs even when you changed nothing.

The version attribute is worth reading before you lean on it, too. `9.2.26083.148` in the line above is
the platform build that wrote the file you started from, and it is not a number your build produces.

If you want to know what changed between two solutions, compare unpacked folders - components, not
containers. The XML that wraps them is rewritten every time someone touches it.
