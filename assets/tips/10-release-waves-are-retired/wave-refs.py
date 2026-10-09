#!/usr/bin/env python3
"""Find the release-wave references the retirement has made stale.

    python3 wave-refs.py <folder> [<folder> ...]

Waves were retired in September 2026. New capability is disclosed on the AI at Work roadmap as it is
committed, and each item carries In Development / Rolling Out / Launched instead of a wave number, so
anything still named after a wave will never be refreshed again: a pipeline that gates on "release wave
1", a wiki page that says "2026 release wave 2", a bookmark to a release plan that retires in November.

This walks a folder, skips the obvious build and vendor directories, reads files that look like text,
and prints every line that matches the retired vocabulary. Exit 0 when a folder comes back clean, 1 when
it does not, so it can sit in a pipeline as a check.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS = (
    ("release wave", re.compile(r"release[\s_-]*wave", re.I)),
    ("wave 1 or wave 2", re.compile(r"\bwave\s*[12]\b", re.I)),
    ("RW1 or RW2", re.compile(r"\bRW[12]\b", re.I)),
    ("a year in front of a wave", re.compile(r"\b20\d\d[\s_-]*wave", re.I)),
    ("a Release Planner link", re.compile(r"release[\s_-]*plans?\.microsoft\.com", re.I)),
    ("a shortlink that resolves to a release plan", re.compile(r"aka\.ms/[A-Za-z0-9]*[Rr]elease", re.I)),
    ("a release plan", re.compile(r"\brelease[\s_-]*plans?\b", re.I)),
)

SKIP_DIRS = {
    ".git", ".github", "node_modules", ".venv", "venv", "__pycache__",
    "bin", "obj", "packages", "dist", "build", ".vs", ".idea", "coverage",
}

TEXT_SUFFIXES = {
    ".md", ".txt", ".rst", ".yml", ".yaml", ".json", ".xml", ".csv", ".config", ".ini", ".toml",
    ".ps1", ".psm1", ".psd1", ".sh", ".bash", ".bat", ".cmd", ".cs", ".js", ".ts", ".py", ".sql",
    ".props", ".targets", ".nuspec", ".editorconfig", ".gitignore", ".gitattributes",
}

MAX_BYTES = 2 * 1024 * 1024


def is_text(path: Path) -> bool:
    """Text by suffix, plus the extension-less files that carry settings."""
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    return path.name in {"Makefile", "Dockerfile", ".gitignore", ".gitattributes", ".editorconfig"}


def scan(root: Path) -> tuple[int, int]:
    files = refs = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not is_text(path):
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        hits = []
        for number, line in enumerate(lines, start=1):
            for label, pattern in PATTERNS:
                match = pattern.search(line)
                if match:
                    hits.append((number, label, line.strip()[:96]))
                    break
        if hits:
            files += 1
            refs += len(hits)
            print(f"  {path}")
            for number, label, text in hits:
                print(f"    line {number:<5} {label:<45} {text}")
    return files, refs


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python3 wave-refs.py <folder> [<folder> ...]")
        return 2

    total_files = total_refs = 0
    for argument in sys.argv[1:]:
        root = Path(argument)
        if not root.is_dir():
            print(f"  {argument}: not a directory")
            continue
        print(f"=== {root} ===")
        files, refs = scan(root)
        total_files += files
        total_refs += refs
        if not refs:
            print("  nothing named after a wave")

    print()
    if total_refs:
        print(f"{total_files} file(s) still name a wave, {total_refs} reference(s) in total")
        print("none of it will ever be refreshed again - the roadmap is continuous now")
        return 1
    print("no file named a wave")
    return 0


if __name__ == "__main__":
    sys.exit(main())
