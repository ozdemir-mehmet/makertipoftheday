#!/usr/bin/env python3
"""Where a web resource's type actually lives in an unpacked solution.

The resource file is just bytes - no extension in the zip, and whatever the file had after unpack. The
type, the display name and the component's GUID are in a `.data.xml` sidecar next to it, and the packer
reads that file, not the bytes:

    python3 webresource-sidecars.py <unpacked-solution-folder>

Exit 0 when every resource has a sidecar. Exit 1 when one does not, because that is a quiet failure
rather than a loud one: `pac solution pack` reports "Packed Solution." and writes a package whose
solution.xml still declares the component, with no member carrying its bytes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TYPES = {1: "HTML", 2: "CSS", 3: "JScript", 4: "XML", 5: "PNG", 6: "JPG", 7: "GIF", 8: "XAP", 9: "XSL", 10: "ICO"}


def field(text: str, name: str) -> str:
    match = re.search(rf"<{name}>(.*?)</{name}>", text, re.DOTALL)
    return match.group(1).strip() if match else ""


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".") / "WebResources"
    if not root.is_dir():
        print(f"FAIL  no WebResources folder under {root.parent}")
        return 2

    missing = 0
    for resource in sorted(p for p in root.iterdir() if not p.name.endswith(".data.xml")):
        sidecar = resource.with_name(resource.name + ".data.xml")
        if not sidecar.is_file():
            print(f"{resource.name:<40} no .data.xml sidecar - it still packs, but the package then ships "
                  f"no bytes for this component")
            missing += 1
            continue
        meta = sidecar.read_text(encoding="utf-8-sig", errors="replace")
        code = field(meta, "WebResourceType")
        label = TYPES.get(int(code), "?") if code.isdigit() else "?"
        print(f"{resource.name:<40} type {code} ({label}), {field(meta, 'DisplayName')!r}, "
              f"{field(meta, 'WebResourceId')}")
        print(f"{'':<40} the file itself: {resource.stat().st_size} bytes, extension "
              f"{resource.suffix or 'none'}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
