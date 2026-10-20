#!/usr/bin/env python3
"""Re-check both halves of the tip: the option values in a public sample, and the vendor sentences.

    python3 check-choice-values.py

Two things are checked, because the tip rests on two kinds of fact:

1. The numbers, from the option-set XML of a public Microsoft sample solution at the pinned commit
   below. Every option's stored value is parsed out of `<option value="...">` and compared with the
   range the heat map reads by default (0-100). The commit is pinned, so these numbers are a record
   of what that sample contained; a mismatch means this script or its pin was edited.
2. Quotes, from the Learn page that describes the visualizations. The page is fetched, its canonical
   link is read from the HTML, and every sentence the evidence block quotes is matched against the
   page text, ignoring tags, punctuation and whitespace. This half can genuinely drift, and it is
   the half a nightly re-verification needs.

No tenant, no login, no Power Apps.

Exit 0 when the numbers match and every quote is still on the page, 1 when either has changed, 2
when a page or the GitHub API could not be fetched at all.
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.error
import urllib.request

REPO = "microsoft/Nonprofits"
FOLDER = "Fundraising/Solution/OptionSets"
SHA = "e41c4afec718cbe98df906ffe9e6a4b20da7b9f2"

PAGE = "https://learn.microsoft.com/en-us/power-apps/maker/data-platform/column-visualizations-grids"
QUOTES = [
    "For choice (option set) columns, the numeric value behind the selected choice is used, and the choice's text is shown as the label.",
    "By default, the range is 0 to 100, and the value's position in that range decides the color.",
    "Values outside the range are pulled to the nearest end of the range (0 or 100 by default).",
    "For choice columns, the color follows the number assigned to each choice, which might not match the visible list order if those numbers aren't in low-to-high sequence.",
]

EXPECTED_SETS = 15
EXPECTED_OUTSIDE = 15
EXPECTED_MIN_VALUE = 844060000


def get(url: str, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "makertipoftheday-reverify"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def squash(text: str) -> str:
    """Lowercase alphanumerics only: tags, punctuation and whitespace stop mattering."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[^a-z0-9]+", "", html.unescape(text).lower())


def canonical(raw: str) -> str:
    m = re.search(r'<link rel="canonical" href="([^"]+)"', raw)
    return html.unescape(m.group(1)) if m else ""


def options(body: str) -> list[tuple[int, str]]:
    """(value, label) for every <option>, in file order."""
    out = []
    for value, block in re.findall(r'<option value="(-?\d+)"[^>]*>\s*<labels>(.*?)</labels>', body, re.S):
        m = re.search(r'description="([^"]*)"', block) or re.search(r"<label[^>]*>([^<]*)<", block)
        out.append((int(value), m.group(1) if m else "?"))
    return out


def main() -> int:
    try:
        listing = json.loads(get(f"https://api.github.com/repos/{REPO}/contents/{FOLDER}?ref={SHA}"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"could not list the sample: {exc}")
        return 2

    print(f"{REPO}@{SHA[:12]}  option set files: {len(listing)}")
    sets, outside, lowest, highest = 0, 0, None, None
    example = None
    for entry in listing:
        try:
            body = get(entry["download_url"], accept="application/xml").decode("utf-8", "replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            print(f"  could not fetch {entry['name']}: {exc}")
            return 2
        pairs = options(body)
        if not pairs:
            continue
        sets += 1
        values = [v for v, _ in pairs]
        lowest = min(values) if lowest is None else min(lowest, min(values))
        highest = max(values) if highest is None else max(highest, max(values))
        if all(v < 0 or v > 100 for v in values):
            outside += 1
        if example is None and len(pairs) > 5:
            example = (entry["name"], pairs)

    print(f"option sets with options: {sets}")
    print(f"sets where every value is outside 0-100: {outside}")
    print(f"lowest stored value: {lowest}   highest stored value: {highest}")
    if example:
        name, pairs = example
        print(f"example, {name}: {len(pairs)} options")
        for v, label in pairs:
            print(f"   {v:>12}  {label}")

    numbers_ok = (sets == EXPECTED_SETS and outside == EXPECTED_OUTSIDE
                  and lowest == EXPECTED_MIN_VALUE)
    print("numbers:", "reproduce the evidence block" if numbers_ok else "DO NOT match the evidence block")

    try:
        raw = get(PAGE, accept="text/html").decode("utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"page: could not fetch {PAGE}: {exc}")
        return 2
    text = squash(raw)
    found = [q for q in QUOTES if squash(q) in text]
    canon = canonical(raw)
    print(f"page: {PAGE}")
    print(f"  page text {len(text)} chars after tag strip, canonical "
          f"{'matches' if canon == PAGE else 'DIFFERS: ' + canon}")
    print(f"  quotes present: {len(found)}/{len(QUOTES)}")
    for q in QUOTES:
        if q not in found:
            print(f"    MISSING: {q[:90]}")

    ok = numbers_ok and len(found) == len(QUOTES) and canon == PAGE
    print("result:", "numbers and quotes both reproduce the evidence block" if ok
          else "a number or a quote no longer matches the evidence block")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
