---
title: "Two packs of one folder are never the same bytes"
summary: "Pack the same unpacked folder twice and you get two files of the same size and different bytes. Hash the artifact in a pipeline and every run looks like a change."
surface: cross-cutting
tip_number: 5
date: 2026-10-05
wave: "n/a - file format and CLI only; no environment was touched"
build: "pac 2.13.1+g251dee1 on .NET SDK 10.0.400"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), .NET SDK 10.0.400; the same unpacked folder packed twice, one second apart"
expires_on: 2027-03-31
cost: "Free - the CLI, the .NET SDK and the sample package are free; no environment involved"
source: "https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution"
artifact: "assets/tips/5-two-packs-are-never-the-same-bytes/compare-packages.py"
evidence: |
  command: dotnet tool run pac solution pack --zipfile same1.zip --folder unpacked --packagetype Managed   # then same2.zip, one second later
  observed: |
    same1.zip  6632 bytes  sha256 35998096895556804644d0d9
    same2.zip  6632 bytes  sha256 dfa77e387980a4d25ef968e3
    different bytes, same size

  command: unzip same1.zip -d s1 && unzip same2.zip -d s2 && diff -rq s1 s2
  observed: |
    (no output - the unpacked contents of the two packages are identical)

  command: python3 compare-packages.py same1.zip same2.zip
  observed: |
    same1.zip                        6632 bytes  sha256 35998096895556804644d0d9
    same2.zip                        6632 bytes  sha256 dfa77e387980a4d25ef968e3
    different bytes
    but every one of the 4 members hashes the same,
    so the difference is the container and not the solution.
    exit: 0
---

Pack the same unpacked folder twice and you get two different files. Not different versions - the same
version, the same components, the same bytes inside, and a different file on disk.

    same1.zip  6632 bytes  sha256 35998096895556804644d0d9
    same2.zip  6632 bytes  sha256 dfa77e387980a4d25ef968e3

Same size, different hash. Unzip both and the contents are identical, down to the hashes of every
member. The difference is the container - the
zip's own metadata - and it moves every time you pack.

This matters the moment a pipeline looks at the built package rather than at the solution. A step that hashes
the zip to detect "did anything change" reports a change on every build. A PR that includes the built
package shows a binary diff nobody can review. An artifact cache keyed on the file's hash misses every
time. None of it is a change to your solution, and all of it looks like one.

Compare the thing that carries meaning instead. Diff the unpacked folder - that is text, and it
tells you which component moved. If you have to compare two packages, compare them member by member
rather than byte by byte, because that is the comparison that answers the question you were asking.

Ship the zip, version the folder.
