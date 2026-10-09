#!/usr/bin/env python3
"""List the columns a Dataverse table carries that nobody created.

    python3 table-columns.py <solution.zip> [more.zip ...]
    python3 table-columns.py --table admin_App <solution.zip>

Reads customizations.xml out of a solution package and splits every table's columns into the ones the
maker defined (`IsCustomField` 1) and the ones the platform adds (`IsCustomField` 0). It then reports
the columns that appear on *every* table in the package, which is the set no maker authored.

The numbers are what the package says, not what a documentation page claims: run it against a
solution you ship and the count is the count for your tables.

Exit 0 when every package parses, 1 when one does not.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

MANIFEST = "solution.xml"
PAYLOAD = "customizations.xml"


def read_member(archive: zipfile.ZipFile, name: str) -> str | None:
    try:
        return archive.read(name).decode("utf-8-sig")
    except KeyError:
        return None


def identity(archive: zipfile.ZipFile) -> str:
    xml = read_member(archive, MANIFEST)
    if xml is None:
        return "unknown"
    root = ET.fromstring(xml)
    name = (root.findtext(".//UniqueName") or "?").strip()
    version = (root.findtext(".//Version") or "?").strip()
    managed = "managed" if (root.findtext(".//Managed") or "0").strip() == "1" else "unmanaged"
    return f"{name} {version} ({managed})"


def tables(archive: zipfile.ZipFile) -> list[tuple[str, list[str], list[str]]]:
    xml = read_member(archive, PAYLOAD)
    if xml is None:
        return []
    root = ET.fromstring(xml)
    found: list[tuple[str, list[str], list[str]]] = []
    for entity in root.findall(".//Entity"):
        attributes = entity.findall(".//attributes/attribute")
        if not attributes:
            continue
        system, custom = [], []
        for attribute in attributes:
            column = (attribute.findtext("LogicalName") or "?").strip()
            required = (attribute.findtext("RequiredLevel") or "?").strip()
            if attribute.findtext("IsCustomField") == "1":
                custom.append(column)
            else:
                system.append(f"{column} ({required})")
        found.append(((entity.findtext("Name") or "?").strip(), system, custom))
    return found


def universal(found: list[tuple[str, list[str], list[str]]]) -> list[str]:
    names = [{column.split(" ")[0] for column in system} for _, system, _ in found]
    if not names:
        return []
    shared = set.intersection(*names)
    return sorted(shared)


def main(argv: list[str]) -> int:
    wanted = None
    if len(argv) > 2 and argv[1] == "--table":
        wanted = argv[2]
        argv = [argv[0]] + argv[3:]
    if len(argv) < 2:
        print((__doc__ or "").strip())
        return 1

    failures = 0
    for given in argv[1:]:
        path = Path(given)
        print(f"=== {given} ===")
        try:
            with zipfile.ZipFile(path) as archive:
                print(f"  solution : {identity(archive)}")
                found = tables(archive)
                if not found:
                    print("  tables   : 0 carrying a column list - the package ships entities as shells,")
                    print("             or ships none at all. Nothing to count.")
                    print()
                    continue
                system = sum(len(s) for _, s, _ in found)
                custom = sum(len(c) for _, _, c in found)
                print(f"  tables   : {len(found)} carrying a column list")
                print(f"  columns  : {system + custom} in total - {system} not created by a maker, "
                      f"{custom} that were")
                shared = universal(found)
                print(f"  on all {len(found):<3}: {len(shared)} columns that nobody created:")
                for column in shared:
                    print(f"             {column}")
                if wanted:
                    for name, syscols, cuscols in found:
                        if name != wanted:
                            continue
                        print(f"\n  {name}: {len(syscols)} columns nobody created "
                              f"(required level in brackets)")
                        for column in syscols:
                            print(f"             {column}")
                        print(f"             and {len(cuscols)} the maker added")
                else:
                    print("\n  the biggest:")
                    for name, syscols, cuscols in sorted(
                        found, key=lambda t: -(len(t[1]) + len(t[2]))
                    )[:6]:
                        print(f"             {name:34} {len(syscols):>3} nobody created / "
                              f"{len(cuscols):>3} maker")
        except (zipfile.BadZipFile, ET.ParseError) as exc:
            print(f"  FAIL  a solution package this is not: {exc}")
            failures += 1
        print()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
