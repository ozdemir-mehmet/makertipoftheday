#!/usr/bin/env python3
"""Check a solution's quick create forms against the columns their tables require.

The rule this checks against is the documented one: a table has to have Enable quick create forms
switched on and carry a form of type quickCreate, and the columns the table requires have to be on
that form. A separate rule, that the parent lookup on the form has to be business required before a
lookup's New opens the pane, is in two of the four write-ups I read and in no page I searched. Every
lookup the form carries is reported with its required level, so that rule can be checked against what
the solution actually holds rather than against belief.

What a solution cannot answer is whether the form is in the app, which the on-premises page requires
and the artifact cannot see.

    python3 quick-create-check.py <solution.zip | customizations.xml>
"""
import collections
import re
import sys
import zipfile

ENTITY = re.compile(r"<Entity>(.*?)</Entity>", re.S)
REQUIRED = ("systemrequired", "required", "applicationrequired")
SYSTEM = ("primarykey", "owner", "state", "status")


def read_xml(path):
    p = str(path)
    if p.lower().endswith(".zip"):
        with zipfile.ZipFile(p) as z:
            for name in z.namelist():
                if name.replace("\\", "/").endswith("customizations.xml"):
                    return z.read(name).decode("utf-8-sig", errors="replace")
        raise SystemExit("no customizations.xml in %s" % p)
    return open(p, encoding="utf-8-sig", errors="replace").read()


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2
    x = read_xml(sys.argv[1])
    entities = ENTITY.findall(x)
    on = [e for e in entities if "<IsQuickCreateEnabled>1</IsQuickCreateEnabled>" in e]
    print("tables in the solution: %d" % len(entities))
    print("tables with Enable quick create forms on: %d" % len(on))
    print("")
    for e in on:
        name = re.search(r"<Name[^>]*>([^<]+)</Name>", e)
        name = name.group(1) if name else "?"
        blocks = re.findall(r"<FormXml(.*?)</FormXml>", e, re.S)
        types = collections.Counter(re.findall(r'<forms\s+type="([^"]+)"', " ".join(blocks)))
        # one FormXml holds every form the table has; only the quickCreate block is the one that counts
        qc = re.findall(r'<forms\s+type="quickCreate"[^>]*>(.*?)</forms>', " ".join(blocks), re.S)
        columns = []
        for m in re.finditer(r"<attribute([^>]*)>(.*?)</attribute>", e, re.S):
            body = m.group(2)
            lvl = re.search(r"<RequiredLevel>([a-z]+)</RequiredLevel>", body)
            nm = re.search(r"<LogicalName>([^<]+)</LogicalName>", body)
            ty = re.search(r"<Type>([a-z]+)</Type>", body)
            tgt = re.search(r"<LookupType[^>]*>([a-z_]+)</LookupType>", body)
            columns.append((nm.group(1) if nm else "?", ty.group(1) if ty else "?",
                            lvl.group(1) if lvl else "none", tgt.group(1) if tgt else ""))
        required = [c for c in columns if c[2] in REQUIRED]
        if not qc:
            print("%s: quick create on, but no form of type quickCreate" % name)
            continue
        cols = re.findall(r'datafieldname="([^"]+)"', " ".join(qc), re.I)
        print("%s" % name)
        print("  forms: %s" % ", ".join("%s %d" % t for t in types.most_common()))
        print("  columns on the quick create form: %d" % len(set(cols)))
        lookups = [(nm, lvl) for nm, ty, lvl, _ in columns if ty == "lookup" and nm in cols]
        if lookups:
            for nm, lvl in lookups:
                state = "marked %s" % lvl if lvl in REQUIRED else "not marked required"
                print("  lookup on the form: %s - %s" % (nm, state))
        else:
            print("  lookups on the form: none")
        for nm, ty, lvl, tgt in required:
            if ty in SYSTEM:
                continue
            where = "on the form" if nm in cols else "MISSING from the form"
            if ty == "lookup" and nm in cols:
                where += ", a lookup to %s" % (tgt or "a target this export does not name")
            print("  required (%s, %s): %s - %s" % (lvl, ty, nm, where))
        sysreq = [nm for nm, ty, _, _ in required if ty in SYSTEM and nm not in cols]
        if sysreq:
            print("  system columns the table requires that the form does not carry: %s"
                  % ", ".join(sysreq))
        if not required:
            print("  no column on this table is systemrequired or required")
        elif all(ty in SYSTEM for _, ty, _, _ in required):
            print("  every required column on this table is a system column (key, owner, state),")
            print("  which no form carries - so there is nothing on the form to check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
