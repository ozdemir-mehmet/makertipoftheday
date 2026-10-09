#!/usr/bin/env python3
"""What unpacking and packing back actually changes in the XML.

A round trip is not a no-op. Compare the package you started with against the one you packed back, and the
differences are in the boilerplate rather than the payload: the re-packed solution.xml gains an XML
declaration, and customizations.xml gains empty containers the original did not carry. Neither shows up in
a diff of the unpacked tree, because both files are rewritten on the way out.

    python3 roundtrip-diff.py <original-extracted-folder> <repacked-extracted-folder>

Exit 0 when the files agree, 1 when they do not.
"""

from __future__ import annotations

import sys
from pathlib import Path

CONTAINERS = ("<Roles />", "<Workflows />", "<FieldSecurityProfiles />", "<Templates />", "<EntityMaps />")


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: python3 roundtrip-diff.py <original-folder> <repacked-folder>")
        return 2

    original, repacked = (Path(arg) for arg in sys.argv[1:3])
    same = True

    for name in ("solution.xml", "customizations.xml"):
        before = (original / name).read_text(encoding="utf-8-sig", errors="replace")
        after = (repacked / name).read_text(encoding="utf-8-sig", errors="replace")
        first_before = before.splitlines()[0][:52] if before.splitlines() else ""
        first_after = after.splitlines()[0][:52] if after.splitlines() else ""
        print(f"{name}")
        print(f"  first line, original: {first_before}")
        print(f"  first line, repacked: {first_after}")
        if (original / name).read_bytes() != (repacked / name).read_bytes():
            same = False
        if name == "customizations.xml":
            for container in CONTAINERS:
                was, now = before.count(container), after.count(container)
                if was != now:
                    print(f"  {container:<26} {was} -> {now}")

    print("the files agree" if same else "the files differ")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
