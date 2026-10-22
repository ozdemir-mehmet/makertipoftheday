#!/usr/bin/env python3
"""Reproduce: unpacking a second solution over an unpacked folder breaks the next pack.

    python3 check-unpack-folder.py --zip-a SolutionOne_managed.zip --zip-b SolutionTwo_managed.zip

Unpacks zip A into <work>/mixed, unpacks zip B over the top of it, and shows that the mixed folder
will not pack while a clean folder of zip A packs fine. Exits 0 when the behaviour matches the tip,
1 when it does not (which is what a re-verification run wants to know).

Needs pac on PATH. If pac lives under ~/.dotnet, the script points DOTNET_ROOT there for you.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def pac_env() -> dict:
    env = os.environ.copy()
    if "DOTNET_ROOT" not in env:
        local = Path.home() / ".dotnet"
        if (local / "dotnet").exists():
            env["DOTNET_ROOT"] = str(local)
            env["PATH"] = f"{local}:{local / 'tools'}:{env.get('PATH', '')}"
    return env


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, env=pac_env())


def unpack(zip_path: Path, folder: Path) -> str:
    r = run(["pac", "solution", "unpack", "--zipfile", str(zip_path),
             "--folder", str(folder), "--packagetype", "Managed"])
    return (r.stdout + r.stderr).strip()


def pack(folder: Path, out: Path) -> tuple[int, str]:
    r = run(["pac", "solution", "pack", "--zipfile", str(out),
             "--folder", str(folder), "--packagetype", "Managed"])
    return r.returncode, (r.stdout + r.stderr).strip()


def solution_name(folder: Path) -> str:
    xml = (folder / "Other" / "Solution.xml")
    if not xml.exists():
        return "(no Other/Solution.xml)"
    text = xml.read_text(encoding="utf-8", errors="replace")
    i = text.find("<UniqueName>")
    return text[i + 12:text.find("<", i + 12)] if i >= 0 else "(unreadable)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip-a", required=True, help="first solution package (managed)")
    ap.add_argument("--zip-b", required=True, help="second solution package (managed)")
    ap.add_argument("--work", default=None, help="work directory (default: a fresh temp dir)")
    ap.add_argument("--keep", action="store_true", help="leave the work directory in place")
    args = ap.parse_args()

    zip_a, zip_b = Path(args.zip_a).resolve(), Path(args.zip_b).resolve()
    work = Path(args.work).resolve() if args.work else Path(tempfile.mkdtemp(prefix="unpackfolder-"))
    work.mkdir(parents=True, exist_ok=True)
    mixed, clean = work / "mixed", work / "clean"
    for d in (mixed, clean):
        if d.exists():
            shutil.rmtree(d)

    checks: list[tuple[str, bool, str]] = []

    unpack(zip_a, mixed)
    name_a = solution_name(mixed)
    files_a = sum(1 for _ in mixed.rglob("*") if _.is_file())

    out_b = unpack(zip_b, mixed)
    name_b = solution_name(mixed)
    files_mixed = sum(1 for _ in mixed.rglob("*") if _.is_file())
    not_deleting = next((l.strip() for l in out_b.splitlines() if "Not deleting" in l), "(line absent)")
    checks.append(("second unpack says it deletes nothing", "Not deleting files" in out_b, not_deleting))
    checks.append(("folder identity becomes solution B", name_b not in ("", name_a), f"{name_a!r} -> {name_b!r}"))
    checks.append(("solution A's files are still present", files_mixed > files_a, f"{files_a} files -> {files_mixed}"))

    code, out = pack(mixed, work / "mixed.zip")
    checks.append(("packing the mixed folder fails RootComponent validation",
                   "RootComponent validation failed" in out and not (work / "mixed.zip").exists(),
                   next((l.strip() for l in out.splitlines() if "RootComponent validation" in l), out[-160:])))

    unpack(zip_a, clean)
    code2, out2 = pack(clean, work / "clean.zip")
    packed = work / "clean.zip"
    contents = zipfile.ZipFile(packed).namelist() if packed.exists() else []
    checks.append(("packing a clean folder of the same solution succeeds",
                   code2 == 0 and "Packed Solution" in out2 and bool(contents),
                   f"{len(contents)} file(s) packed"))

    failed = 0
    for label, ok, detail in checks:
        print(f"{'ok  ' if ok else 'FAIL'}  {label}: {detail}")
        failed += 0 if ok else 1

    print(f"\nwork directory: {work}")
    if failed == 0 and not args.keep and not args.work:
        shutil.rmtree(work, ignore_errors=True)
        print("(removed - pass --keep or --work to inspect it)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
