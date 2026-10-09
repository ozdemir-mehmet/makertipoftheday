#!/usr/bin/env python3
"""Two packs of the same folder: same size, different bytes.

A pipeline that hashes or diffs the packed artifact reports a change every run, because packing is not
byte-stable - the zip's metadata moves even when every file inside is identical. This compares two
packages on both axes, so the difference between "the content changed" and "the container did" is
visible:

    python3 compare-packages.py a.zip b.zip

Exit 0 when the contents agree (whatever the bytes do), 1 when the contents differ.
"""

from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def members(path: Path) -> dict[str, str]:
    with zipfile.ZipFile(path) as archive:
        return {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()}


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: python3 compare-packages.py a.zip b.zip")
        return 2

    first, second = (Path(arg) for arg in sys.argv[1:3])
    for path in (first, second):
        print(f"{path.name:<28} {path.stat().st_size:>8} bytes  sha256 {digest(path)[:24]}")

    if digest(first) == digest(second):
        print("the two files are byte-identical")
        return 0

    print("different bytes")
    left, right = members(first), members(second)
    if left == right:
        print(f"but every one of the {len(left)} members hashes the same,")
        print("so the difference is the container and not the solution.")
        return 0

    for name in sorted(set(left) | set(right)):
        if left.get(name) != right.get(name):
            print(f"  content differs: {name}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
