#!/usr/bin/env python3
"""Nightly re-verification check.

Reports two things, both of which mean work:

  * published tips past their expiry, which the site marks as unverified and which must be re-run or
    retired;
  * the depth of the ready queue, which is the cover for days when the change feed produces nothing;
  * any document the corpus walk had to refuse, which `validate_tips.py` reports as a failure but which
    this script would otherwise pass over in silence.

Writes `reverify-report.md` at the repository root (gitignored) and prints a one-line summary.

Exit codes - the workflow distinguishes them, so they matter:

    0   nothing to do
    10  something lapsed or the buffer is under the alarm threshold (EXIT_ATTENTION)
    any other non-zero code, including the 1 Python uses for an uncaught exception, means the check
    itself failed. The workflow fails the run rather than opening a tracking issue for a crash.

Run locally with `python3 scripts/reverify.py`.
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_tips import (  # noqa: E402  - local module, same directory
    FrontMatterError,
    QUEUE_DIR,
    ROOT,
    TIPS_DIR,
    as_date,
    display,
    markdown_files,
    parse_front_matter,
)

DUE_SOON_DAYS = 14
QUEUE_TARGET = 10
QUEUE_MINIMUM = 5

EXIT_CLEAN = 0
EXIT_ATTENTION = 10


def collect(directory: Path, errors: list[str]) -> list[tuple[Path, dict[str, str]]]:
    items = []
    for path in markdown_files(directory, errors):
        try:
            data, _body, _raw = parse_front_matter(path)
        except FrontMatterError as exc:
            # Reported, not skipped. A document this script cannot read is a document it cannot date,
            # and validate_tips.py failing on the same file does not make it visible from here.
            errors.append(f"{display(path)}: {exc}")
            continue
        items.append((path, data))
    return items


def main() -> int:
    today = dt.date.today()
    errors: list[str] = []
    tips = collect(TIPS_DIR, errors)
    queued = collect(QUEUE_DIR, errors)

    expired, due_soon, healthy = [], [], []
    for path, data in tips:
        expires = as_date(data.get("expires_on", ""))
        if expires is None:
            continue
        days = (expires - today).days
        row = (path.relative_to(ROOT).as_posix(), data.get("title", "?"), expires, days)
        if days < 0:
            expired.append(row)
        elif days <= DUE_SOON_DAYS:
            due_soon.append(row)
        else:
            healthy.append(row)

    ready = [q for q in queued if q[1].get("state") == "ready"]
    blocked = [q for q in queued if q[1].get("state") == "blocked"]

    lines = ["# Tip re-verification report", "", f"Generated {today.isoformat()} (UTC date of the runner).", ""]

    lines += ["## Published tips", ""]
    if not tips:
        lines += ["Nothing published yet.", ""]
    else:
        lines += [
            f"{len(healthy)} within expiry, {len(due_soon)} due within {DUE_SOON_DAYS} days, "
            f"{len(expired)} expired.",
            "",
        ]
    if expired:
        lines += ["### Expired - the site marks these as unverified", ""]
        lines += [f"- {title} (`{path}`) - expired {expires.isoformat()}, {abs(days)} days ago" for path, title, expires, days in expired]
        lines += [""]
    if due_soon:
        lines += [f"### Due within {DUE_SOON_DAYS} days", ""]
        lines += [f"- {title} (`{path}`) - expires {expires.isoformat()} in {days} days" for path, title, expires, days in due_soon]
        lines += [""]

    if errors:
        lines += ["## Structural problems", ""]
        lines += [f"- {message}" for message in errors]
        lines += [
            "",
            "A document the corpus walk refuses is a failure in `validate_tips.py`; it is repeated here",
            "so that the nightly job cannot pass over it in silence.",
            "",
        ]

    lines += ["## Buffer", ""]
    lines += [
        f"{len(ready)} ready, {len(blocked)} blocked. Target {QUEUE_TARGET}, alarm below {QUEUE_MINIMUM}.",
        "",
    ]
    if len(ready) < QUEUE_MINIMUM:
        lines += [
            "The ready queue is under the alarm threshold: a day with a thin change feed has no cover.",
            "Mine the change feed (MicrosoftDocs diffs, pac CLI and XrmToolBox release notes, the AI at",
            "Work roadmap) and move items to `state: ready` once the artifact has actually been run.",
            "",
        ]

    lines += ["## What this report is not", ""]
    lines += [
        "A clean report means no dates have lapsed - it is not evidence that a tip still behaves as",
        "described. Re-running the artifact is the only thing that shows that.",
        "",
    ]

    (ROOT / "reverify-report.md").write_text("\n".join(lines), encoding="utf-8")

    needs_attention = bool(expired) or len(ready) < QUEUE_MINIMUM or bool(errors)
    print(
        f"{len(tips)} published ({len(expired)} expired, {len(due_soon)} due soon); "
        f"queue {len(ready)} ready / {len(blocked)} blocked "
        f"(target {QUEUE_TARGET}, alarm {QUEUE_MINIMUM}); "
        f"{len(errors)} structural problem(s); "
        f"report: {ROOT / 'reverify-report.md'}"
    )
    print("NEEDS ATTENTION" if needs_attention else "Nothing due.")
    return EXIT_ATTENTION if needs_attention else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
