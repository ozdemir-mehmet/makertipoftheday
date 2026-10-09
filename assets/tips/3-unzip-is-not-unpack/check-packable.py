#!/usr/bin/env python3
"""Is this folder in the shape `pac solution pack` accepts?

The zip and the unpacked folder are different shapes. A plain `unzip` gives you the zip's shape, and the
packer then refuses with "Cannot find required file '.../Other/Customizations.xml'" even though a
customizations.xml is sitting in the folder you pointed at. This says which shape you have:

    python3 check-packable.py <folder>

Exit 0 when the two files the packer looks for are present, 1 when they are not.
"""

from __future__ import annotations

import sys
from pathlib import Path

WANTED = ("Other/Solution.xml", "Other/Customizations.xml")


def main() -> int:
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    missing = [name for name in WANTED if not (folder / name).is_file()]
    flat = [name for name in ("solution.xml", "customizations.xml") if (folder / name).is_file()]

    if not missing:
        print(f"packable  {folder} has {' and '.join(WANTED)}")
        return 0

    print(f"REFUSED   {folder} is missing {' and '.join(missing)}")
    if flat:
        print(f"          but it does carry {', '.join(flat)} at the top level,")
        print("          which is the shape inside the zip, not the shape on disk.")
        print("          run `pac solution unpack` first.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
