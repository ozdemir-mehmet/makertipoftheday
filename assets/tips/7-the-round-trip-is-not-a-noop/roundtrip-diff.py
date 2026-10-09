#!/usr/bin/env python3
"""What unpacking and packing back actually changes in the XML.

A round trip is not a no-op. Compare the package you started with against the one you packed back, and the
differences are in the boilerplate rather than the payload: the re-packed solution.xml gains an XML
declaration, the line endings change, and customizations.xml's empty containers come back collapsed. Neither shows up in
a diff of the unpacked tree, because both files are rewritten on the way out.

    python3 roundtrip-diff.py <original-extracted-folder> <repacked-extracted-folder>

Exit 0 when the files agree, 1 when they do not.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Element names, not one spelling of them. The original writes <Roles> with nothing inside and the writer
# emits <Roles /> - count only the self-closing form and you report a container appearing out of nowhere
# when it was in the package all along.
CONTAINERS = ("Roles", "Workflows", "FieldSecurityProfiles", "Templates", "EntityMaps")


def container_form(text: str, name: str) -> str:
    for spelling in (f"<{name} />", f"<{name}/>", f"<{name}>"):
        if spelling in text:
            return spelling
    return "(absent)"


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
            if b"\r\n" in (original / name).read_bytes() and b"\r\n" not in (repacked / name).read_bytes():
                print("  line endings: CRLF in the original, LF in the repacked file")
            for container in CONTAINERS:
                was, now = container_form(before, container), container_form(after, container)
                if was != now:
                    print(f"  {container:<22} {was} -> {now}")

    print("the files agree" if same else "the files differ")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
