#!/usr/bin/env python3
"""What package type is this solution, and would your --packagetype be accepted?

`pac solution unpack --packagetype Unmanaged` against a managed package fails with "Solution package
type did not match requested type" and writes no folder at all, so the flag has to agree with the
package. The answer is inside the package, in the same file the packer reads:

    python3 package-type.py <folder-with-Other/Solution.xml|solution.xml> [requested-type]

Exit 0 when the requested type matches (or when none was given), 1 when it does not.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    for candidate in (target / "Other/Solution.xml", target / "solution.xml", target):
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8-sig", errors="replace")
            break
    else:
        print(f"FAIL  no Solution.xml under {target}")
        return 2

    match = re.search(r"<Managed>\s*([01])\s*</Managed>", text)
    if not match:
        print(f"FAIL  {candidate} carries no <Managed> element")
        return 2

    kind = "Managed" if match.group(1) == "1" else "Unmanaged"
    print(f"{kind:<9} {candidate}")
    if kind == "Managed":
        print("          <Managed>1</Managed> - every -managed.xml suffix you see came from this bit")

    if len(sys.argv) > 2:
        requested = sys.argv[2]
        if requested.lower() != kind.lower():
            print(f"REFUSED   you asked for {requested}; the folder says {kind}")
            return 1
        print(f"accepted  you asked for {requested}, which is what the folder is")
    return 0


if __name__ == "__main__":
    sys.exit(main())
