#!/usr/bin/env python3
"""Fail when the pac CLI that runs is not the pac CLI the repository pinned.

`dotnet tool restore` normally guarantees this, but a global install of pac, an MSI install, or a
stale `~/.dotnet/tools` entry earlier on PATH can shadow the manifest version and the build then runs
on a CLI nobody chose. This compares the manifest entry with what the CLI reports.

    python3 check-pac-version.py

Exit 0 when they match, 1 when they do not or when no pin can be found. Run it as a CI step after
`dotnet tool restore` and before anything that touches an environment.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PACKAGE = "microsoft.powerapps.cli.tool"
MANIFESTS = ("dotnet-tools.json", ".config/dotnet-tools.json")


def find_manifest(start: Path) -> Path | None:
    """The first manifest at or above `start`, the way `dotnet tool restore` finds one."""
    for directory in (start, *start.parents):
        for name in MANIFESTS:
            candidate = directory / name
            if candidate.is_file():
                return candidate
    return None


def pinned_version(manifest: Path) -> str | None:
    entry = json.loads(manifest.read_text(encoding="utf-8")).get("tools", {}).get(PACKAGE)
    return entry.get("version") if entry else None


def running_version() -> tuple[str | None, str]:
    """Ask the CLI itself, through the manifest, so PATH cannot influence the answer.

    `pac help`, not `pac --version`: --version prints the banner and then fails with "Parse failed on:
    --version" and exit 1, which turns a version check into a broken build. `pac --help` exits 0 but
    does not print the banner, so help is the only one of the three that both succeeds and reports.
    """
    result = subprocess.run(
        ["dotnet", "tool", "run", "pac", "help"],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        return None, (result.stdout + result.stderr).strip()
    match = re.search(r"Version:\s*([0-9][^\s+]*)", result.stdout)
    return (match.group(1) if match else None), result.stdout.strip().splitlines()[1] if result.stdout else ""


def main() -> int:
    manifest = find_manifest(Path.cwd())
    if manifest is None:
        print(f"FAIL  no dotnet-tools.json found at or above {Path.cwd()}")
        return 1

    pin = pinned_version(manifest)
    if pin is None:
        print(f"FAIL  {manifest} has no entry for {PACKAGE}")
        return 1

    running, detail = running_version()
    if running is None:
        print("FAIL  `dotnet tool run pac help` did not report a version")
        print(detail)
        return 1

    if running != pin:
        print(f"FAIL  pinned {pin} in {manifest}, but the CLI that ran reports {running}")
        print(detail)
        return 1

    print(f"ok    pac {running} matches the pin in {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
