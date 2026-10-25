#!/usr/bin/env python3
"""Re-verify the rollup-column tip against the Learn page it cites.

Nothing about this tip was executed: there is no tenant on this machine, so no rollup column was
created and no system job was watched. What this script proves is that the page still carries every
sentence the body and the evidence block quote, in full, and that the canonical link still points at
`source:`.

Run from the repo root: PYTHONDONTWRITEBYTECODE=1 python3 assets/tips/25-<slug>/check-page.py
Exit 0 means the page half still matches. Only the page half can drift - the record of what was
observed is fixed at publication and this script cannot refresh it.
"""
import html
import re
import sys
import urllib.request

DOC = "https://learn.microsoft.com/en-us/power-apps/maker/data-platform/define-rollup-fields"

QUOTES = [
    "A rollup column contains an aggregate value computed over the rows related to a specified row.",
    "The column value has been calculated per the last update time in _date column.",
    "The rollups are calculated by scheduled system jobs that run asynchronously in the background.",
    "Mass Calculate Rollup Field is a recurring job, created for each rollup column.",
    "It runs once, after you create or update a rollup column.",
    "The job recalculates the specified rollup column value in all existing records that contain this column.",
    "By default, the job will run 12 hours after you have created or updated a column.",
    "When the column is modified, the job resets to run again in 12 hours after the update.",
    "We recommend that an administrator adjusts the start time of a Mass Calculate Rollup Field job after the rollup column is created or modified, in such a way that it runs during nonoperational hours.",
    "Calculate Rollup Field is a recurring job that does incremental calculations of all rollup columns in the existing rows for a specified table.",
    "The incremental calculations mean that the Calculate Rollup Field job processes the rows that were created, updated, or deleted after the last Mass Calculate Rollup Field job finished execution.",
    "The rollup column on the form displays a calculator image, rollup value, and the time of the last calculation.",
    "To recalculate, select the calculator image, and then select the Recalculate button that appears.",
    "The maximum number of rows during the rollup refresh is limited to 50,000 rows.",
    "As a system administrator, you can modify the rollup job recurrence pattern, postpone, pause, or resume the rollup job.",
    "For the Mass Calculate Rollup Field job, the available selections are: Resume , Postpone , and Pause .",
    "For the Calculate Rollup Field job, the available selections are: Modify Recurrence , Resume , Postpone , and Pause .",
]


def plain(page):
    page = re.sub(r"<script[^>]*>.*?</script>", " ", page, flags=re.S)
    page = re.sub(r"<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(page))


def main():
    with urllib.request.urlopen(DOC, timeout=60) as r:
        raw = r.read()
    page = raw.decode("utf-8", "replace")
    text = plain(page)
    print(f"page: {DOC}")
    print(f"  fetched {len(raw)} bytes")

    canon = re.search(r'<link rel="canonical" href="([^"]+)"', page)
    ok = bool(canon and canon.group(1) == DOC)
    print(f"  canonical matches source: {ok}")
    if not ok:
        print("FAIL: canonical link no longer matches source:")
        return 1

    missing = 0
    for q in QUOTES:
        present = q in text
        print(f"  [{'ok' if present else 'MISSING'}] {q}")
        if not present:
            missing += 1
    print(f"  quotes present: {len(QUOTES) - missing}/{len(QUOTES)}")

    if missing:
        print("FAIL: a quoted sentence moved or was reworded; re-derive the body against the page")
        return 1
    print("result: every quoted sentence is still on the page, whole")
    print("note: this checks the page only - the observation that no tenant was available is a record, not a claim this script re-tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
