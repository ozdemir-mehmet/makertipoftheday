#!/usr/bin/env python3
"""Scan tip bodies, and chat replies, for the constructions that read as machine-written.

This is an internal check, run before any external review. It looks only at the body of a
published tip - the part a reader sees - and never at the evidence block, which is internal.

Findings are quoted with their line number. A hit is a prompt to look, not a verdict: the
rule is to remove the construction, not to argue with the scanner.

    python3 scripts/slop_scan.py _tips/*.md            # tip bodies (the build gate)
    python3 scripts/slop_scan.py --prose draft.md      # a chat reply, before it is sent
    python3 scripts/slop_scan.py --prose -             # a draft on stdin

--prose scans the whole file rather than the part after the front matter, drops the rules
that only make sense inside a tip (talking about this repository, rhetorical questions,
bold text in prose), and adds the framing labels that show up in conversation: the colon
label that announces a judgement instead of making one - "the honest state:" - and the
stock openers and closers that rate your own work instead of stating it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RULES: list[tuple[str, str]] = [
    # the body is for a maker doing the work, never about our own repository or process
    ("forensics", r"\b(my|our|this) (repository|repo|checkout)\b"),
    ("forensics", r"\bqueue template\b|\bthe validator\b|\bvalidate_tips\b|\bevidence block\b|\btest fixture\b|\bverified_on\b|\bthe gates\b"),
    ("forensics", r"\bI scanned\b|\bmy own repository\b|\bthis tip's own\b|\bthe artifact (script|for this tip)\b|\bthis tip's artifact\b"),
    ("forensics", r"\breviewers?\b|\breview (round|pass|loop|process)\b|\bcode review\b|\bclaude\b|\bagy\b"),
    # announcing structure instead of saying something
    ("count opener", r"^\**\s*(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|\d+)\s+"
                     r"(things|reasons|parts|ways|rules|places|questions|gotchas|truths|notes)\b"),
    ("count opener", r"\b(Here (are|is)|There (are|is))\b[^.]{0,40}\b(things|reasons|parts|ways|rules|places)\b"),
    ("count fragment", r"\b(the|these|those) (two|three|four|five|\d+)\b[^.]{0,30}\b(are|is)\b"),
    # evaluative tails and rhetorical closes
    ("evaluative tail", r"\bworth knowing\b|\b(earns?|earned) (its|their) keep\b|\bis the part\b"),
    ("evaluative tail", r"\bthe (whole )?(point|trick|tell)\b|\bharder to notice than\b"),
    ("evaluative tail", r"\bis the one (that|to) (bites|biting|catches|trips|hurts|matters)\b|\bworth keeping\b"),
    ("evaluative tail", r"\bthe kind of thing you have to\b|\bwhich is why\b"),
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

# For prose rather than a tip body: the label that announces a judgement, the stock opener,
# the closer that rates the work. These are the tics that survive when the tip rules do not
# apply, because a conversation has no front matter and no reader-facing body to protect.
PROSE_ONLY: list[tuple[str, str]] = [
    # a colon-terminated label line - "the honest state:", "One honest caveat:" - which names
    # what is about to be said instead of saying it
    ("framing label", r"^\**[A-Za-z][^.!]{0,70}\b(honest|truth|real|hard|key|important|takeaway|bottom line|short version|caveat|reality)\b[^.!]{0,20}:$"),
    ("framing label", r"\bhonest (take|state|caveat|answer|assessment|truth|version)\b"),
    ("framing label", r"\bworth flagging\b|\bhas teeth\b"),
    ("framing label", r"\bthe (good|bad) news\b|\bthe takeaway\b|\bthe real (question|issue)\b|\bwhat matters here\b"),
    ("framing label", r"\b(fair point|good catch|great question|you were right|valid point|well spotted)\b"),
    ("framing label", r"\b(let me be|to be) honest\b|\bfull disclosure\b|\bI'?d be happy to\b"),
    ("framing label", r"\bthat said\b|\bit'?s worth (a |the )?(mention|note)\b"),
]

PROSE_SKIP = {"forensics", "rhetorical question", "bold in prose"}


def rules_for(prose: bool) -> list[tuple[str, str]]:
    if not prose:
        return RULES
    kept = [(n, p) for n, p in RULES if n not in PROSE_SKIP]
    return kept + PROSE_ONLY


def body_of(path: Path) -> tuple[int, list[str]]:
    """The reader-facing part: everything after the closing front-matter fence."""
    lines = path.read_text().split("\n")
    fences = [i for i, l in enumerate(lines) if l.strip() == "---"]
    if len(fences) < 2:                      # a draft with no front matter: scan all of it
        return 1, lines
    start = fences[1]
    return start + 2, lines[start + 1:]


def scan(path: Path, prose: bool = False) -> list[tuple[int, str, str]]:
    rules = rules_for(prose)
    if prose:
        offset, lines = 1, path.read_text().split("\n")
    else:
        offset, lines = body_of(path)
    hits = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or line.startswith("    ") or stripped.startswith(("#", "|", "```")):
            continue
        target = re.sub(r"`[^`]*`", " ", line)      # inline code is not prose
        for name, pattern in rules:
            for m in re.finditer(pattern, target, re.I):
                if " and " in m.group(0).lower():
                    continue
                # in a reply, a bullet is structure; its label is still worth a look
                hits.append((offset + i, name, m.group(0)[:60]))
    # a triad that wraps across lines is still a triad, so join each paragraph and retry that rule
    para, first = [], 0
    for i, line in enumerate(lines + [""]):
        if line.strip():
            if not para:
                first = i
            para.append(line.strip())
            continue
        if len(para) > 1 and not prose:
            joined = " ".join(para)
            for m in re.finditer(dict(RULES)["list triad"], joined, re.I):
                if " and " in m.group(0).lower():
                    continue
                hits.append((offset + first, "list triad (wrapped)", m.group(0)[:60]))
        para = []
    seen, unique = set(), []
    for line_no, name, text in hits:
        key = (line_no, text.lower().strip())
        if key in seen:
            continue
        seen.add(key)
        unique.append((line_no, name, text))
    return unique


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--prose"]
    prose = "--prose" in argv[1:]
    if not args:
        print("usage: slop_scan.py [--prose] <tip.md|-> ...")
        return 2
    total = 0
    for arg in args:
        if arg == "-":
            draft = Path("/tmp/.slop_scan_stdin")
            draft.write_text(sys.stdin.read())
            path = draft
        else:
            path = Path(arg)
        hits = scan(path, prose=prose)
        total += len(hits)
        label = "draft" if arg == "-" else str(path)
        if not hits:
            print(f"clear   {label}")
            continue
        print(f"\n{label} - {len(hits)} hit(s)")
        for line_no, name, text in hits:
            print(f"  line {line_no:<4} {name:<20} {text}")
    print(f"\n{total} hit(s) across {len(args)} file(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
