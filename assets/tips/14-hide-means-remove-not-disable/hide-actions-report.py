#!/usr/bin/env python3
"""Report what a solution hides from the command bar, from customizations.xml.

Learn is blunt that this is not a cosmetic setting: "This does not hide the ribbon element, it
actually removes the ribbon element at runtime so that it doesn't exist in the ribbon." A
HideCustomAction names one ribbon element by its Location - the element's id, not the command
it invokes - and that element stops being rendered. Every one of them travels in the solution.

    python3 hide-actions-report.py <solution.zip | customizations.xml>

Reports the entities the package defines and how many carry a hide action, the total hide actions
and how many sit inside an entity block rather than elsewhere in the file, the distinct locations,
and four breakdowns of those locations: the leading segment, which is whose it is; the middle
segment, which is the surface for the usual Mscrm names - the grid, the form, the subgrid - though a
few locations carry an entity name there instead; the trailing name, which is the element; and the
element names that appear on more than one surface.
"""
import collections
import re
import sys
import zipfile

HIDE = re.compile(r"<HideCustomAction\s[^>]*?/?>")
LOCATION = re.compile(r'Location="([^"]+)"')


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
    entities = re.findall(r"<Entity>(.*?)</Entity>", x, re.S)
    hides = HIDE.findall(x)
    inside = sum(len(HIDE.findall(e)) for e in entities)
    with_hides = sum(1 for e in entities if HIDE.search(e))
    locations = [LOCATION.search(h).group(1) for h in hides if LOCATION.search(h)]
    suffix = collections.Counter(l.split(".")[-1] for l in locations)
    middle = collections.Counter(l.split(".")[1] for l in locations if l.count(".") >= 2)
    prefix = collections.Counter(l.split(".")[0] for l in locations)
    print("entities defined: %d" % len(entities))
    print("entities with at least one hide action: %d" % with_hides)
    print("hide actions: %d (inside entity blocks: %d, elsewhere: %d)"
          % (len(hides), inside, len(hides) - inside))
    print("distinct locations: %d" % len(set(locations)))
    print("")
    print("the surface the element sits on, by the middle segment of its location:")
    for name, count in middle.most_common(6):
        print("  %-16s %d" % (name, count))
    by_name = collections.defaultdict(set)
    for l in locations:
        parts = l.split(".")
        if len(parts) >= 3:
            by_name[parts[-1]].add(parts[1])
    spread = {n: sorted(s) for n, s in by_name.items() if len(s) > 1}
    print("")
    print("elements taken out on more than one surface: %d of %d"
          % (len(spread), len(by_name)))
    for name in sorted(spread, key=lambda n: -sum(1 for l in locations if l.endswith("." + n)))[:5]:
        print("  %-16s %s" % (name, ", ".join(spread[name])))
    print("")
    print("the element that is removed, by its trailing name, most often:")
    for name, count in suffix.most_common(6):
        print("  %-16s %d" % (name, count))
    print("")
    print("the locations begin with:")
    for name, count in prefix.most_common():
        print("  %-16s %d" % (name, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
