#!/usr/bin/env python3
"""Measure what a Power BI Desktop project's reports actually point at.

    python3 check-dataset-reference.py --repo microsoft/finops-toolkit --sha <commit>

Reads every `*.Report/definition.pbir` under `src/power-bi/` in a public Microsoft sample, at a pinned
commit, and reports which semantic model folder each report resolves to through `datasetReference.byPath`.

The point the tip makes: copying a report folder does not copy its model, because the copy keeps the same
relative `byPath` - and `byPath` opens the model in full edit mode, so model edits made while working in the
copy are written into the one folder every report on it shares.

Exits 0 when the sample shows the reference shape the tip describes, 1 when it does not (which is what a
re-verification run wants to know).
"""
from __future__ import annotations

import argparse
import json
import posixpath
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "makertipoftheday-check-dataset-reference",
    })
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="microsoft/finops-toolkit")
    ap.add_argument("--sha", required=True, help="commit sha to read (pinned, not a branch)")
    ap.add_argument("--prefix", default="src/power-bi/")
    args = ap.parse_args()

    tree = get_json(f"{API}/repos/{args.repo}/git/trees/{args.sha}?recursive=1")
    paths = [n["path"] for n in tree.get("tree", []) if n.get("type") in ("blob", "tree")]

    pbirs = sorted(p for p in paths
                   if p.startswith(args.prefix) and p.endswith(".Report/definition.pbir"))
    dirs = {p for p in paths if p.startswith(args.prefix)}

    refs: list[tuple[str, str, str]] = []      # (report folder, kind, target)
    for p in pbirs:
        raw = (f"https://raw.githubusercontent.com/{args.repo}/{args.sha}/" + p)
        with urllib.request.urlopen(raw, timeout=45) as r:
            doc = json.loads(r.read().decode("utf-8"))
        ref = doc.get("datasetReference", {}) or {}
        if "byPath" in ref:
            refs.append((p, "byPath", ref["byPath"].get("path", "")))
        elif "byConnection" in ref:
            refs.append((p, "byConnection", ref["byConnection"].get("connectionString", "")))
        else:
            refs.append((p, "none", ""))

    by_path = [(p, t) for p, k, t in refs if k == "byPath"]
    by_conn = [(p, t) for p, k, t in refs if k == "byConnection"]
    absolute = [(p, t) for p, t in by_path if t.startswith("/") or ":" in t.split("/")[0]]
    # a byPath reference is relative to the report folder - the folder holding definition.pbir
    resolved = [(p, posixpath.normpath(posixpath.join(posixpath.dirname(p), t)))
                for p, t in by_path]
    targets: dict[str, list[str]] = {}
    for p, target in resolved:
        targets.setdefault(target, []).append(p)
    missing = [(p, target) for p, target in resolved if target not in dirs]
    shared = {t: ps for t, ps in targets.items() if len(ps) > 1}

    checks: list[tuple[str, bool, str]] = []
    checks.append((f"the sample has report folders carrying definition.pbir", bool(pbirs), f"{len(pbirs)} report folder(s)"))
    checks.append(("every one of them uses a byPath reference", not by_conn and bool(by_path),
                   f"{len(by_path)} byPath, {len(by_conn)} byConnection"))
    checks.append(("none of the paths is absolute", not absolute,
                   f"{len(absolute)} absolute path(s)" if absolute else "all relative"))
    checks.append(("at least two reports resolve to the same model folder", bool(shared),
                   "; ".join(f"{len(ps)} report(s) -> {t}" for t, ps in shared.items()) or "no shared target"))
    checks.append(("every resolved model folder exists in the sample", not missing,
                   f"{len(missing)} missing" if missing else f"{len(targets)} distinct target(s), all present"))

    for label, ok, detail in checks:
        print(f"{'ok  ' if ok else 'FAIL'}  {label}: {detail}")
    print()
    for p, target in resolved:
        print(f"  {p}\n    -> {target}")

    failed = sum(0 if ok else 1 for _, ok, _ in checks)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.URLError as e:
        print(f"network error: {e}", file=sys.stderr)
        sys.exit(2)
