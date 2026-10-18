#!/usr/bin/env python3
"""Re-check both halves of the tip: the sample counts and the vendor sentences it quotes.

    python3 count-filtered-steps.py

Two things are checked, because the tip rests on two kinds of fact:

1. Counts, from the `SdkMessageProcessingSteps` folder of two public Microsoft sample solutions at the
   commits pinned below. The commits are pinned, so these numbers are a record of what those samples
   contained; they cannot drift, and a mismatch means this script or its pin was edited.
2. Quotes, from the four Learn pages the body paraphrases. Each page is fetched, its canonical link is
   read from the HTML, and every sentence the evidence block quotes is matched against the page text,
   ignoring tags, punctuation and whitespace. This half can genuinely drift, and it is the half a
   nightly re-verification needs.

No tenant, no login, no pac.

Exit 0 when the counts match and every quote is still on its page, 1 when either has changed, 2 when a
page or the GitHub API could not be fetched at all.
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

SOURCES = [
    ("microsoft/Nonprofits",
     "VolunteerManagement/VolunteerManagement/Solution/SdkMessageProcessingSteps",
     "11e976e8274e0608e46bbd229ea97fdb7d821ec6"),
    ("microsoft/Power-CAT-Tools",
     "PowerCATToolkit/SolutionPackage/src/SdkMessageProcessingSteps",
     "c33f47982cd25f3dae32fd3ca1aab1f0fc883762"),
]

PAGES = [
    ("https://learn.microsoft.com/en-us/power-apps/developer/data-platform/register-plug-in", [
        "For the Update , OnExternalUpdated , or other message, when you set the primary entity, filtering attributes (columns) limits the execution of the plug-in to cases where the specified columns are included in the update.",
        "Only include columns with changed values in update operations.",
        "If a request contains a filtering attribute, the plug-in will be triggered regardless of whether the attribute’s value is changed or not.",
        "Don't include the primary key of the entity in the filtering attributes. The primary key is always included in update operations, so doing this negates all other filtered attributes.",
    ]),
    ("https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/sdkmessageprocessingstep", [
        "If at least one of these attributes is modified, the plug-in should execute.",
    ]),
    ("https://learn.microsoft.com/en-us/power-apps/developer/data-platform/understand-the-data-context", [
        "When you register a step for a plug-in that includes a table as one of the parameters, you can specify that a copy of the table data be included as a snapshot or image by using the PreEntityImages and PostEntityImages properties.",
        "This data provides a comparison point for table data as it flows through the event pipeline.",
        "For example, to access the Entity property that’s passed as part of the CreateRequest , you need to know that the name of that property is Target .",
    ]),
    ("https://learn.microsoft.com/en-us/dotnet/api/microsoft.xrm.sdk.messages.updaterequest?view=dataverse-sdk-latest", [
        "Gets or sets an instance of an entity that is used to update a record. Required.",
    ]),
]

EXPECTED_STEPS = 31
EXPECTED_FILTERED = 13
EXPECTED_STATE = 2

# SdkMessageId values seen in these samples. Each step's own Name states the message it is registered
# for, which is what the name column of the output lets a reader check this mapping against.
MESSAGES = {
    "9ebdbb1b-ea3e-db11-86a7-000a3a5473e8": "Create",
    "20bebb1b-ea3e-db11-86a7-000a3a5473e8": "Update",
    "f0bdbb1b-ea3e-db11-86a7-000a3a5473e8": "other",
}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "makertipoftheday-reverify"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def squash(text: str) -> str:
    """Lowercase alphanumerics only: tags, punctuation and whitespace stop mattering."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[^a-z0-9]+", "", html.unescape(text).lower())


def canonical(raw: str) -> str:
    m = re.search(r'<link rel="canonical" href="([^"]+)"', raw)
    return m.group(1) if m else ""


def main() -> int:
    steps = []
    try:
        for repo, path, sha in SOURCES:
            listing = json.loads(get(f"https://api.github.com/repos/{repo}/contents/{path}?ref={sha}"))
            print(f"{repo}@{sha[:12]}: {len(listing)} step file(s)")
            for entry in listing:
                req = urllib.request.Request(entry["download_url"],
                                             headers={"User-Agent": "makertipoftheday"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    body = resp.read()
                root = ET.fromstring(body)
                fa = (root.findtext("FilteringAttributes") or "").strip()
                attrs = [a.strip() for a in fa.split(",") if a.strip()]
                steps.append({
                    "name": root.get("Name", ""),
                    "entity": (root.findtext("PrimaryEntity") or "").strip(),
                    "msg": MESSAGES.get((root.findtext("SdkMessageId") or "").strip(), "unknown"),
                    "attrs": attrs,
                })
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"could not fetch the samples: {exc}")
        return 2

    filtered = [s for s in steps if s["attrs"]]
    state = [s for s in filtered if {"statecode", "statuscode"} & set(s["attrs"])]
    by_msg = {}
    for s in steps:
        by_msg.setdefault(s["msg"], [0, 0])
        by_msg[s["msg"]][0] += 1
        if s["attrs"]:
            by_msg[s["msg"]][1] += 1

    print(f"steps: {len(steps)}")
    print(f"empty FilteringAttributes: {len(steps) - len(filtered)}")
    print(f"naming filtering attributes: {len(filtered)}")
    for msg, (total, filt) in sorted(by_msg.items()):
        print(f"  {msg:6} steps {total:3}  of which filtered {filt}")
    print(f"filtering on statecode or statuscode: {len(state)}")
    for s in state:
        print(f"  {s['msg']:6} {s['entity']}")
        print(f"    {s['name']}")
        print(f"    filters on {'|'.join(s['attrs'])}")

    counts_ok = (len(steps) == EXPECTED_STEPS and len(filtered) == EXPECTED_FILTERED
                 and len(state) == EXPECTED_STATE)
    print("counts:", "reproduce the evidence block" if counts_ok else "DO NOT match the evidence block")

    quotes_ok = True
    for url, sentences in PAGES:
        try:
            raw = get(url).decode("utf-8", "replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            print(f"page: could not fetch {url}: {exc}")
            return 2
        text = squash(raw)
        found = [s for s in sentences if squash(s) in text]
        canon = canonical(raw)
        print(f"page: {url}")
        print(f"  {len(raw)} bytes, canonical {'matches' if canon == url else 'DIFFERS: ' + canon}")
        print(f"  quotes present: {len(found)}/{len(sentences)}")
        for s in sentences:
            if s not in found:
                print(f"    MISSING: {s[:90]}")
        quotes_ok = quotes_ok and len(found) == len(sentences) and canon == url

    ok = counts_ok and quotes_ok
    print("result:", "counts and quotes both reproduce the evidence block" if ok
          else "a count or a quote no longer matches the evidence block")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
