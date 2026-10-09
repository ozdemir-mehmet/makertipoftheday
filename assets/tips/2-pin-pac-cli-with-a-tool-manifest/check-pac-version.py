#!/usr/bin/env python3
"""Fail when the pac CLI that runs is not the pac CLI the repository pinned.

`dotnet tool restore` normally guarantees this, but a global install of pac, an MSI install, or a stale
`~/.dotnet/tools` entry earlier on PATH can shadow the manifest version, and the pipeline then runs on a
CLI nobody chose. This checks both halves of that:

  1. the CLI the manifest resolves to, which is what `dotnet tool run pac` always uses, and
  2. the CLI a bare `pac` on PATH resolves to, which is what a pipeline step that just types `pac ...`
     actually gets.

If those are different versions, a build that passes locally can pack or import with a different CLI in
CI without anyone changing a file, so this exits 1 and names the path that has to go.

    python3 check-pac-version.py

Exit 0 when the pin matches and any pac on PATH matches it too, 1 when they do not, when PAC_PATH_CHECK=0
is not set and a PATH pac disagrees, or when no pin can be found. Run it as a CI step after
`dotnet tool restore` and before anything that touches an environment.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE = "microsoft.powerapps.cli.tool"
# .config first: with both files in the same directory, that is the one `dotnet tool restore` honours,
# which is the opposite of the intuitive answer and the reason this list has an order at all.
MANIFESTS = (".config/dotnet-tools.json", "dotnet-tools.json")


def find_manifest(start: Path) -> Path | None:
    """The first manifest at or above `start`, in the order `dotnet tool restore` searches.

    Nearest directory first, and within a directory `.config/dotnet-tools.json` before the root
    `dotnet-tools.json`.
    """
    for directory in (start, *start.parents):
        for name in MANIFESTS:
            candidate = directory / name
            if candidate.is_file():
                return candidate
    return None


def pinned_version(manifest: Path) -> str | None:
    entry = json.loads(manifest.read_text(encoding="utf-8")).get("tools", {}).get(PACKAGE)
    return entry.get("version") if entry else None


def version_from(output: str) -> str | None:
    match = re.search(r"Version:\s*([0-9][^\s+]*)", output)
    return match.group(1) if match else None


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
    lines = result.stdout.strip().splitlines()
    return version_from(result.stdout), (lines[1] if len(lines) > 1 else result.stdout.strip())


def path_cli() -> tuple[str | None, str | None]:
    """The pac a bare `pac` in a shell or a YAML step would run, and the version it reports."""
    executable = shutil.which("pac")
    if executable is None:
        return None, None
    try:
        result = subprocess.run([executable, "help"], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return executable, None
    return executable, version_from(result.stdout + result.stderr)


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

    print(f"ok    the manifest resolves pac {running} ({manifest})")

    if os.environ.get("PAC_PATH_CHECK", "1") == "0":
        return 0

    executable, on_path = path_cli()
    if executable is None:
        print("ok    no pac on PATH, so every pac command goes through the manifest")
        return 0
    if on_path is None:
        print(f"FAIL  {executable} is on PATH and did not report a version")
        return 1
    if on_path != pin:
        print(f"FAIL  {executable} is on PATH and reports {on_path}, but the pin is {pin}")
        print("      a step that runs `pac ...` gets the PATH one; remove it, or pin the same version")
        return 1

    print(f"ok    {executable} on PATH reports the same {on_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
