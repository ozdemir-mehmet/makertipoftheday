#!/usr/bin/env python3
"""Report what a Fabric workspace commit would act on, reading only the files.

An item folder is one carrying a .platform file, or the older pair item.metadata.json and
item.config.json, which is how version 1 works. Learn, on the source code format: "In version
2, instead of having two source files in each item directory, the .platform file combines all
the information into one file along with a $schema property." On the commit itself it is
blunt: "During the Commit to Git process, the Fabric service deletes files inside the item
folder that aren't part of the item definition. Unrelated files not in an item folder aren't
deleted." And of the two shapes: "If you have this file, you can't have the other two files."

    python3 workspace-lint.py <workspace-folder>

The check reads the part of the rule visible in the tree: a file inside an item folder but
outside definition/ is not part of the item definition. A file the schema does not name inside
definition/ falls under the same sentence and is not covered here.
"""
import pathlib
import sys

PLATFORM = ".platform"
LEGACY = ("item.metadata.json", "item.config.json")


def files_in(item):
    return [p for p in item.rglob("*") if p.is_file() and ".git" not in p.parts]


def items(root):
    """Every item folder: .platform marks version 2, the legacy pair marks version 1."""
    found = {}
    for folder in sorted(p for p in root.rglob("*") if p.is_dir() and ".git" not in p.parts):
        names = {p.name for p in folder.iterdir() if p.is_file()}
        if PLATFORM in names:
            found[folder] = "version 2"
        elif set(LEGACY) <= names:
            found[folder] = "version 1"
    return found


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2
    root = pathlib.Path(sys.argv[1])
    if not root.is_dir():
        print("%s is not a folder" % root)
        return 2
    found = items(root)
    v1 = sum(1 for k in found.values() if k == "version 1")
    print("workspace: %s" % root)
    print("item folders: %d, of which %d read as version 1" % (len(found), v1))
    strays = 0
    allthree = 0
    for item, version in sorted(found.items()):
        inside = files_in(item)
        names = {p.name for p in inside}
        # the platform file and the version 1 pair are the item definition themselves, not strays
        metadata = (PLATFORM,) + LEGACY
        outs = sorted(p for p in inside if p.name not in metadata and "definition" not in p.parts)
        print("")
        print("  %s  (%s)" % (item.relative_to(root), version))
        print("    files: %d, of which %d outside definition/" % (len(inside), len(outs)))
        for p in outs:
            print("      covered by the commit rule: %s" % p.relative_to(item))
            strays += 1
        legacy_here = sorted(n for n in names if n in LEGACY)
        if legacy_here and PLATFORM in names:
            print("    all three present: %s" % ", ".join(legacy_here))
            print("      the pair and the platform file cannot sit together: one of them goes on the next commit")
            allthree += 1
    print("")
    print("covered by the commit rule: %d file(s); item folders holding all three: %d" % (strays, allthree))
    return 0


if __name__ == "__main__":
    sys.exit(main())
