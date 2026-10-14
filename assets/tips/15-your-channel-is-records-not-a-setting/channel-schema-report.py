#!/usr/bin/env python3
"""Report the tables a Customer Service channel is made of, from the sample channel schemas.

A channel you bring into Omnichannel is not a setting. It is records in msdyn_ tables, and the
samples in the Dynamics 365 apps samples repo ship the schema for those tables: every field with
its type, whether it is custom, and the number the platform uses for the table.

    python3 channel-schema-report.py <schema.xml | directory of schemas>

Reads the XML directly. For each table it prints the field count, how many of those fields are
marked custom, the table number where the schema carries one, the types in use, and the tables
the lookups point at, so a payload can be checked against a written list instead of a designer.
"""
import collections
import glob
import os
import re
import sys

ENTITY = re.compile(r'<entity\s+name="([^"]+)"([^>]*)>(.*?)</entity>', re.S)
FIELD = re.compile(r"<field\s+([^/>]+)/>")
ATTR = re.compile(r'(\w+)="([^"]*)"')


def report(path):
    text = open(path, encoding="utf-8-sig", errors="replace").read()
    print("%s" % os.path.basename(path))
    for name, head, body in ENTITY.findall(text):
        h = dict(ATTR.findall(head))
        fields = [dict(ATTR.findall(f)) for f in FIELD.findall(body)]
        types = collections.Counter(f.get("type", "?") for f in fields)
        custom = sum(1 for f in fields if f.get("customfield") == "true")
        lookups = sorted({f.get("lookupType", "") for f in fields if f.get("lookupType")})
        line = "  %-38s %3d fields, %2d custom" % (name, len(fields), custom)
        if h.get("etc"):
            line += ", table number %s" % h["etc"]
        print(line)
        if types:
            print("       types: %s" % ", ".join("%s %d" % t for t in types.most_common()))
        if lookups:
            print("       lookups point at: %s" % ", ".join(lookups))
    print("")


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2
    target = sys.argv[1]
    paths = sorted(glob.glob(os.path.join(target, "*schema*.xml"))) if os.path.isdir(target) else [target]
    if not paths:
        raise SystemExit("no xml files in %s" % target)
    tables, fields_total, types_total, custom_total = set(), 0, collections.Counter(), 0
    for p in paths:
        report(p)
        text = open(p, encoding="utf-8-sig", errors="replace").read()
        for name, head, body in ENTITY.findall(text):
            tables.add(name)
            for f in FIELD.findall(body):
                d = dict(ATTR.findall(f))
                fields_total += 1
                types_total[d.get("type", "?")] += 1
                if d.get("customfield") == "true":
                    custom_total += 1
    print("across %d file(s): %d distinct tables, %d fields (%d of them custom)"
          % (len(paths), len(tables), fields_total, custom_total))
    print("types in use: %s" % ", ".join("%s %d" % t for t in types_total.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
