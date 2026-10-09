#!/usr/bin/env python3
"""The file that is in every solution package and in no unpacked folder.

`[Content_Types].xml` is the package's own list of parts. `pac solution pack` writes it; `pac solution
unpack` never gives you one; and it is the only file in the zip that is not part of the solution. This
reports what a package declares, and what the folder it came from holds:

    python3 content-types-report.py <package.zip> [unpacked-folder]

Exit 0 when the package has one, 1 when it does not (the import will not read it).
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

PART = re.compile(r'<Override PartName="([^"]+)"')


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python3 content-types-report.py <package.zip> [unpacked-folder]")
        return 2

    package = Path(sys.argv[1])
    if not package.is_file():
        print(f"FAIL  {package} is not a file")
        return 2

    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        if "[Content_Types].xml" not in names:
            print(f"FAIL  {package.name} has no [Content_Types].xml, so its {len(names)} parts are undeclared")
            return 1
        text = archive.read("[Content_Types].xml").decode("utf-8-sig", errors="replace")
        parts = PART.findall(text)

    print(f"in the package:       [Content_Types].xml, {len(text)} bytes, declaring {len(parts)} part(s)")
    for part in parts:
        print(f"                        {part}")
    print(f"                      and {len(names) - 1} other member(s) alongside it")

    if len(sys.argv) > 2:
        folder = Path(sys.argv[2])
        found = sorted(folder.rglob("[[]Content_Types[]].xml"))
        print(f"in {folder}:  {len(found)} file(s) of that name")
        if not found:
            print("                      the unpacker never writes one; the packer always does")
    return 0


if __name__ == "__main__":
    sys.exit(main())
