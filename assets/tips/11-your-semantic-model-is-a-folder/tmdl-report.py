#!/usr/bin/env python3
"""Report what a Power BI project folder actually is on disk.

Point it at a folder holding one or more *.SemanticModel / *.Report folders (a PBIP
project, or a repo full of them) and it reports, per model, whether the model is saved
as TMDL text under definition/ or as one TMSL model.bim, how many files that is, the
tables, and whether git tracks the per-machine files the article says belong in .gitignore.

Exit 1 if a per-machine file is tracked, 0 otherwise.
"""
import argparse, os, subprocess, sys

PER_MACHINE = ("localSettings.json", "cache.abf")   # per user and computer, out of source control
SHARED_HINT = "editorSettings.json"                  # the FabricTools samples track this


def project_dirs(root):
    for cur, dirs, _ in os.walk(root):
        for d in list(dirs):
            if d.endswith((".SemanticModel", ".Report")):
                yield os.path.join(cur, d)
                dirs.remove(d)


def tracked(path):
    repo = subprocess.run(["git", "-C", os.path.dirname(path), "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True)
    if repo.returncode:
        return None
    top = repo.stdout.strip()
    rel = os.path.relpath(path, top)
    out = subprocess.run(["git", "-C", top, "ls-files", "--", rel], capture_output=True, text=True)
    return [p for p in out.stdout.splitlines() if p]


def model_report(path):
    name = os.path.basename(path)
    def_dir, bim = os.path.join(path, "definition"), os.path.join(path, "model.bim")
    if os.path.isdir(def_dir):
        fmt = "TMDL"
        tmdl = [os.path.join(dp, f) for dp, _, fs in os.walk(def_dir) for f in fs if f.endswith(".tmdl")]
    elif os.path.isfile(bim):
        fmt, tmdl = "TMSL", [bim]
    else:
        fmt, tmdl = "unknown", []
    total = sum(os.path.getsize(f) for f in tmdl)
    tables = sorted(f[:-5] for f in os.listdir(os.path.join(def_dir, "tables"))
                    if f.endswith(".tmdl")) if os.path.isdir(os.path.join(def_dir, "tables")) else []
    real = [t for t in tables if not t.startswith(("LocalDateTable_", "DateTableTemplate_"))]
    autos = [t for t in tables if t not in real]
    pbi = os.path.join(path, ".pbi")
    pbi_files = sorted(os.listdir(pbi)) if os.path.isdir(pbi) else []
    return fmt, tmdl, total, real, autos, pbi_files, tracked(path)


def main():
    ap = argparse.ArgumentParser(description="Report what a Power BI project folder is on disk.")
    ap.add_argument("path")
    args = ap.parse_args()
    if not os.path.isdir(args.path):
        print(f"{args.path}: not a directory"); return 2

    projects = sorted(project_dirs(args.path))
    models = [p for p in projects if p.endswith(".SemanticModel")]
    reports = [p for p in projects if p.endswith(".Report")]
    print(f"{args.path}")
    print(f"  {len(models)} semantic model(s), {len(reports)} report(s)")

    bad = []
    print("\n  semantic models")
    print(f"    {'model':<34} {'format':<7} {'files':>5} {'bytes':>8}  tables  .pbi")
    for p in models:
        fmt, tmdl, total, real, autos, pbi_files, trk = model_report(p)
        note = "none"
        if pbi_files:
            tracked_per_machine = [f for f in pbi_files if f in PER_MACHINE] if trk is None else \
                [f for f in pbi_files if f in PER_MACHINE and any(t.endswith("/.pbi/" + f) for t in trk)]
            note = "" if not tracked_per_machine else "TRACKED:" + ",".join(tracked_per_machine)
            if not tracked_per_machine:
                shared = [f for f in pbi_files if f == SHARED_HINT]
                note = (SHARED_HINT + " tracked") if (shared and trk and any(t.endswith("/.pbi/" + SHARED_HINT) for t in trk)) else ",".join(pbi_files)
        if note.startswith("TRACKED"):
            bad.append((p, note))
        label = os.path.basename(p)[:-len(".SemanticModel")]
        print(f"    {label[:34]:<34} {fmt:<7} {len(tmdl):>5} {total:>8}  {len(real):>6}  {note}")

    print("\n  what each model is made of")
    for p in models[:1]:
        fmt, tmdl, total, real, autos, _, _ = model_report(p)
        print(f"    {os.path.basename(p)}")
        for f in sorted(os.path.relpath(t, p) for t in tmdl):
            print(f"      {f}")
        if autos:
            print(f"      ({len(autos)} auto date/time tables omitted)")

    if reports:
        print("\n  reports")
        for p in reports:
            has_def = os.path.isdir(os.path.join(p, "definition"))
            print(f"    {os.path.basename(p)[:-len('.Report')]:<34} {'PBIR' if has_def else 'legacy':<7} "
                  f"{'definition.pbir present' if os.path.isfile(os.path.join(p, 'definition.pbir')) else 'no definition.pbir'}")

    print()
    if bad:
        print("  per-machine files are tracked:")
        for p, note in bad:
            print(f"    {p}: {note}")
        return 1
    print("  no per-machine files (.pbi/localSettings.json, .pbi/cache.abf) are tracked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
