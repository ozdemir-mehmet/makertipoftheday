#!/usr/bin/env python3
"""Scan tip bodies for the constructions that read as machine-written.

This is an internal check, run before any external review. It looks only at the body of a
published tip - the part a reader sees - and never at the evidence block, which is internal.

Findings are quoted with their line number. A hit is a prompt to look, not a verdict: the
rule is to remove the construction, not to argue with the scanner.

    python3 scripts/slop_scan.py _tips/*.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RULES: list[tuple[str, str]] = [
    # the body is for a maker doing the work, never about our own repository or process
    ("forensics", r"\b(this|the) (repository|repo|checkout)\b"),
    ("forensics", r"\bqueue template|\bvalidator\b|\bevidence block\b|\btest fixture|\bverified_on\b|\bgates?\b"),
    ("forensics", r"\bI scanned\b|\bmy own repository\b|\bthe artifact\b|\bthis tip's own\b"),
    ("forensics", r"\breviewers?\b|\breview (round|pass|loop|process)\b|\bcode review\b|\bclaude\b|\bagy\b"),
    # announcing structure instead of saying something
    ("count opener", r"^\**\s*(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|\d+)\s+"
                     r"(things|reasons|parts|ways|rules|places|questions|gotchas|truths|notes)\b"),
    ("count opener", r"\b(Here (are|is)|There (are|is))\b[^.]{0,40}\b(things|reasons|parts|ways|rules|places)\b"),
    ("count fragment", r"\b(the|these|those) (two|three|four|five|\d+)\b[^.]{0,30}\b(are|is)\b"),
    # evaluative tails and rhetorical closes
    ("evaluative tail", r"\bworth knowing\b|\b(earns?|earned) (its|their) keep\b|\bis the part\b"),
    ("evaluative tail", r"\bthe (whole )?(point|trick|tell)\b|\bharder to notice than\b"),
    ("evaluative tail", r"\bthe kind of thing you have to\b|\bwhich is why\b$"),
    # essay frames
    ("essay frame", r"\bnot (only|just)\b[^.]{0,60}\b(but|they became|it)\b|\bmore than just\b"),
    ("essay frame", r"\b(it|that) is worth (noting|saying)\b|\blet'?s (look|start|walk)\b"),
    ("essay frame", r"\bin this tip\b|\bthis (tip|article) (covers|will|explains)\b|\bwhat follows\b"),
    # the interrogative hook
    ("rhetorical question", r"\?"),
    # emphasis in prose, rather than in headings
    ("bold in prose", r"\*\*[^*]+\*\*"),
    # stock phrasing
    ("stock phrase", r"\bquietly\b|\bseamless\w*|\bleverag\w+|\bdelv\w+|\bunlock\w*|\bempower\w*"),
    ("stock phrase", r"\bat scale\b|\bdeep dive\b|\bwhen it comes to\b|\bthe reality is\b"),
    ("stock phrase", r"\bgame.chang\w+|\blandscape\b|\brobust\w*|\bholistic\w*|\bparadigm\b"),
    # a dash followed by three comma-separated items - the list triad
    ("list triad", r"[-\u2014]\s*[^,.\n]{2,40},\s*[^,.\n]{2,40},\s*[^,.\n]{2,40}\."),
]


def body_of(path: Path) -> tuple[int, list[str]]:
    """The reader-facing part: everything after the closing front-matter fence."""
    lines = path.read_text().split("\n")
    fences = [i for i, l in enumerate(lines) if l.strip() == "---"]
    if len(fences) < 2:                      # a draft with no front matter: scan all of it
        return 1, lines
    start = fences[1]
    return start + 2, lines[start + 1:]


def scan(path: Path) -> list[tuple[int, str, str]]:
    offset, lines = body_of(path)
    hits = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "|", "```")):
            continue
        for name, pattern in RULES:
            for m in re.finditer(pattern, line, re.I):
                hits.append((offset + i, name, m.group(0)[:60]))
    return hits


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv[1:]]
    if not paths:
        print("usage: slop_scan.py <tip.md> ...")
        return 2
    total = 0
    for path in paths:
        hits = scan(path)
        total += len(hits)
        if not hits:
            print(f"clear   {path}")
            continue
        print(f"\n{path} - {len(hits)} hit(s)")
        for line_no, name, text in hits:
            print(f"  line {line_no:<4} {name:<20} {text}")
    print(f"\n{total} hit(s) across {len(paths)} file(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
