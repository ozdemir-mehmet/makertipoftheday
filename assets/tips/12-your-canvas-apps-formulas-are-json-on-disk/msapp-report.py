#!/usr/bin/env python3
"""Report what a canvas app keeps on disk: its formulas, and the row cap each table carries.

An .msapp is a zip. Controls/*.json holds the app's own Power Fx, one InvariantScript per
control property; References/DataSources.json lists every data source, and each Dataverse table
carries MaxGetRowsCount, the number of records the app will fetch. The archive stores its paths
with backslashes rather than forward slashes, so a zip reader that expects slashes finds nothing.

    python3 msapp-report.py <app.msapp>

Measured on the CoE Admin app (CenterofExcellenceCoreComponents 4.50.9, managed):
References/DataSources.json is 3,194,207 bytes with 94 data sources - 6 Dataverse tables, 73
option sets, 6 views, 4 connectors, 2 static, 3 collections; all 6 tables MaxGetRowsCount 500;
Controls/1.json, 4.json and 5.json carry 1,642 InvariantScript values, 1,634 of them non-empty,
containing LookUp x8, Filter x5, Max x4, CountRows x3, CountIf x3, SortByColumns x1, and no Sum,
Average, Search, Distinct, FirstN or LastN at all.

The count of "delegat" in that file is six, and all six are the Dataverse description "Unique
identifier of the delegate user who created the record" inside TableDefinition - the createdby
and modifiedby columns. The file carries no delegation metadata.
"""
import collections
import json
import pathlib
import re
import sys
import zipfile

BS = chr(92)
DELEGATION_SENSITIVE = (
    "CountRows", "CountIf", "Sum", "Average", "Min", "Max", "Filter", "Search", "LookUp",
    "Sort", "SortByColumns", "Distinct", "GroupBy", "AddColumns", "Collect", "Patch", "Remove",
    "FirstN", "LastN",
)
CONTROL_JSON = re.compile("Controls/[^/]+[.]json$")


def member(zf, wanted):
    """Resolve a member name, since the archive stores its paths with backslashes."""
    for name in zf.namelist():
        if name.replace(BS, "/") == wanted:
            return name
    raise KeyError(wanted)


def formulas(zf):
    """Every InvariantScript value in Controls/, and the files they came from."""
    found = []
    names = [n for n in zf.namelist() if CONTROL_JSON.match(n.replace(BS, "/"))]
    for name in sorted(names):
        with zf.open(name) as fh:
            tree = json.loads(fh.read().decode("utf-8-sig", errors="replace"))

        def walk(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == "InvariantScript" and isinstance(value, str):
                        found.append(value)
                    else:
                        walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(tree)
    return found, sorted(pathlib.Path(n.replace(chr(92), "/")).name for n in names)


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2
    with zipfile.ZipFile(sys.argv[1]) as zf:
        raw = zf.read(member(zf, "References/DataSources.json"))
        body = json.loads(raw.decode("utf-8-sig", errors="replace"))
        scripts, formula_files = formulas(zf)
    sources = body.get("DataSources", [])
    print("data sources: %d" % len(sources))
    for kind, count in collections.Counter(s.get("Type") for s in sources).most_common():
        print("  %-26s %d" % (kind, count))
    tables = [s for s in sources if s.get("Type") == "NativeCDSDataSourceInfo"]
    print("")
    print("Dataverse tables, and the record cap each carries:")
    for s in tables:
        print("  %-24s %-24s MaxGetRowsCount=%s" % (s.get("Name"), s.get("LogicalName"), s.get("MaxGetRowsCount")))
    print("  distinct caps: %s" % sorted({s.get("MaxGetRowsCount") for s in tables}))
    print("")
    print("formulas: %d InvariantScript values, %d non-empty, in %s" % (
        len(scripts), sum(1 for s in scripts if s.strip()), ", ".join(formula_files)))
    counts = collections.Counter()
    for script in scripts:
        for name in DELEGATION_SENSITIVE:
            counts[name] += len(re.findall(BS + "b" + name + BS + "s*" + BS + "(", script))
    print("  delegation-sensitive calls: %s" % dict(counts.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
