#!/usr/bin/env python3
"""Re-check both halves of the tip: the SKU ceiling table and the vendor sentences it quotes.

    python3 check-size-limits.py

Two things are checked, because the tip rests on two kinds of fact:

1. The numbers, parsed out of the capacity-settings page: the per-SKU hard ceiling on the offline
   semantic model size (F2 through F64 and beyond), and the statement that the `Max Offline
   Semantic model Size` setting applies to both storage formats. The table is sliced out of the
   page between its own heading and the next setting's, so a row cannot be lifted from the query
   memory table that sits below it and reports different numbers for the same SKUs.
2. Quotes, from the two Learn pages the body paraphrases. Each page is fetched, its canonical link
   is read from the HTML, and every sentence the evidence block quotes is matched against the page
   text, ignoring tags, punctuation and whitespace. This half can genuinely drift, and it is the
   half a nightly re-verification needs.

No tenant, no login, no capacity.

Exit 0 when the table rows match and every quote is still on its page, 1 when either has changed,
2 when a page could not be fetched at all.
"""
from __future__ import annotations

import html
import re
import sys
import urllib.error
import urllib.request

WORKLOADS = "https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-admin-premium-workloads"
LARGE_MODELS = "https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-large-models"

# The ceiling table the tip cites: SKU -> hard ceiling in GB, small storage format only.
EXPECTED_CEILING = {
    "F2": 1, "F4": 2, "F8/EM1/A1": 3, "F16/EM2/A2": 5, "F32/EM3/A3": 6,
    "F64/P1/A4": 10, "F128/P2/A5": 10, "F256/P3/A6": 10, "F512/P4/A7": 10,
    "F1024/P5/A8": 10, "F2048": 10, "F4096": 10, "F8192": 10,
}

PAGES = [
    (WORKLOADS, [
        "The default value is 0, which is the highest limit defined by SKU.",
        "The allowable range is between 0 and the capacity size limit.",
        "This setting is applicable for models in both small semantic model storage format (ABF format) and large semantic model storage format (PremiumFiles), although the offline size of the same model might differ when stored in one format vs another.",
        "If you have an existing semantic model that is larger than the size you specify for this setting, the semantic model will fail to load when a user tries to access it.",
        "The additional SKU-specific hard ceiling in the below table does not apply to Power BI semantic models stored in large semantic model storage format.",
    ]),
    (LARGE_MODELS, [
        "The default size limit is 1 GB.",
        "While required for semantic models to grow beyond 10 GB, enabling the Large semantic model storage format has other benefits.",
        "For Pro workspaces assigned to the Reserved Capacity for Pro Workspaces , the semantic model size limit is 1 GB.",
        "expand Large semantic model storage format , set the slider to On , and then select Apply .",
    ]),
]

CEILING_CAPTION = "Hard ceiling for Max Offline Semantic model size (small storage format)."


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "makertipoftheday-reverify"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "replace")


def squash(text: str) -> str:
    """Lowercase alphanumerics only: tags, punctuation and whitespace stop mattering."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[^a-z0-9]+", "", html.unescape(text).lower())


def canonical(raw: str) -> str:
    m = re.search(r'<link rel="canonical" href="([^"]+)"', raw)
    return html.unescape(m.group(1)) if m else ""


def ceiling_table(raw: str) -> dict[str, int]:
    """The SKU rows between the Max Offline Semantic model Size heading and the next one.

    Sliced rather than grepped page-wide: the query memory table further down lists the same SKUs
    against different sizes, so a page-wide match would report numbers belonging to another setting.
    """
    start = raw.find('id="max-offline-semantic-model-size"')
    end = raw.find('id="max-result-row-set-count"')
    if start < 0 or end < 0 or end < start:
        return {}
    section = raw[start:end]
    rows: dict[str, int] = {}
    for sku, size in re.findall(r"<td>([^<]*(?:EM|F\d)[^<]*)</td>\s*<td>(\d+) GB</td>", section):
        sku = html.unescape(sku).strip()
        sku = "" if sku.lower().startswith("sku") else sku
        if sku:
            rows[sku] = int(size)
    return rows


def main() -> int:
    try:
        workloads_raw = get(WORKLOADS)
        large_raw = get(LARGE_MODELS)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"could not fetch a page: {exc}")
        return 2

    rows = ceiling_table(workloads_raw)
    print(f"SKU hard ceiling, small storage format only ({len(rows)} rows parsed)")
    for sku, size in rows.items():
        print(f"  {sku:14} {size:>3} GB")
    missing = {k: v for k, v in EXPECTED_CEILING.items() if rows.get(k) != v}
    print(f"rows matching the evidence block: {len(EXPECTED_CEILING) - len(missing)}/{len(EXPECTED_CEILING)}")
    for sku, size in missing.items():
        print(f"  MISMATCH {sku}: expected {size} GB, page says {rows.get(sku, 'nothing')}")
    print(f"caption present: {CEILING_CAPTION!r} -> {squash(CEILING_CAPTION) in squash(workloads_raw)}")

    quotes_ok = True
    for url, sentences, raw in ((WORKLOADS, PAGES[0][1], workloads_raw),
                                (LARGE_MODELS, PAGES[1][1], large_raw)):
        text = squash(raw)
        found = [s for s in sentences if squash(s) in text]
        canon = canonical(raw)
        print(f"page: {url}")
        print(f"  page text {len(text)} chars after tag strip, canonical "
              f"{'matches' if canon == url else 'DIFFERS: ' + canon}")
        print(f"  quotes present: {len(found)}/{len(sentences)}")
        for s in sentences:
            if s not in found:
                print(f"    MISSING: {s[:90]}")
        quotes_ok = quotes_ok and len(found) == len(sentences) and canon == url

    ok = not missing and all(rows.get(k) == v for k, v in EXPECTED_CEILING.items()) and quotes_ok
    print("result:", "table and quotes both reproduce the evidence block" if ok
          else "a row or a quote no longer matches the evidence block")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
