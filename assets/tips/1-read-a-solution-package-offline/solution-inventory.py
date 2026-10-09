#!/usr/bin/env python3
"""Say what is inside a Dataverse solution package, without importing it anywhere.

    python3 solution-inventory.py MetadataBrowser_4_0_0_0_managed.zip [more.zip ...]

Reads `solution.xml` for the identity and the root components, and `customizations.xml` for the web
resource payload. Needs nothing but a zip file and this script: no environment, no `pac`, no login.

Exit 0 when every file parses, 1 when one does not.
"""

from __future__ import annotations

import collections
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# Component type numbers, from the solutioncomponent reference. Deliberately not treated as
# complete: Microsoft's own sample solutions declare type 80, which this table does not list, and
# anything unknown is reported as such rather than guessed at.
COMPONENT_TYPES = {
    1: "Entity (table)", 2: "Attribute (column)", 9: "Option Set", 10: "Entity Relationship",
    20: "Role", 26: "Saved Query (view)", 29: "Workflow (process)", 31: "Report",
    60: "System Form", 61: "Web Resource", 62: "Site Map", 63: "Custom Control",
    70: "Field Security Profile", 71: "Field Permission", 90: "Plugin Type",
    91: "Plugin Assembly", 92: "SDK Message Processing Step", 93: "SDK Message Processing Step Image",
    95: "Service Endpoint", 300: "Canvas App", 371: "Connector",
    380: "Environment Variable Definition", 381: "Environment Variable Value",
}

# Web resource type numbers, from the webresource reference.
WEB_RESOURCE_TYPES = {
    1: ("Webpage", ".html"), 2: ("Style Sheet", ".css"), 3: ("Script", ".js"), 4: ("Data", ".xml"),
    5: ("PNG", ".png"), 6: ("JPG", ".jpg"), 7: ("GIF", ".gif"), 8: ("Silverlight", ".xap"),
    9: ("Style Sheet", ".xsl"), 10: ("ICO", ".ico"), 11: ("Vector", ".svg"), 12: ("String", ".resx"),
}


def text(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    return element.text.strip()


def inventory(path: Path) -> int:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            solution = archive.read("solution.xml").decode("utf-8-sig")
            customizations = archive.read("customizations.xml").decode("utf-8-sig")
    except (zipfile.BadZipFile, KeyError, OSError) as exc:
        print(f"FAIL  {path}: {exc}")
        return 1

    manifest = ET.fromstring(solution).find(".//SolutionManifest")
    if manifest is None:
        print(f"FAIL  {path}: solution.xml has no SolutionManifest")
        return 1

    print(f"=== {path.name} ===")
    print(f"  unique name  : {text(manifest.find('UniqueName'))}")
    print(f"  version      : {text(manifest.find('Version'))}")
    print(f"  managed      : {text(manifest.find('Managed'))}"
          f"{'  (1 = managed)' if text(manifest.find('Managed')) == '1' else ''}")
    publisher = manifest.find("Publisher")
    if publisher is not None:
        print(f"  publisher    : {text(publisher.find('UniqueName'))}")

    types = collections.Counter(m.group(1) for m in re.finditer(r'<RootComponent type="(\d+)"', solution))
    total = sum(types.values())
    print(f"  components   : {total}")
    for code, count in sorted(types.items(), key=lambda kv: -kv[1]):
        label = COMPONENT_TYPES.get(int(code), f"type {code} - not in the documented component list")
        print(f"    {count:>4}  {code:>4}  {label}")

    files = [n for n in names if n not in ("solution.xml", "customizations.xml", "[Content_Types].xml")]
    print(f"  payload files: {len(files)}")

    if "<WebResources>" in customizations:
        for resource in re.finditer(r"<WebResource>(.*?)</WebResource>", customizations, re.S):
            block = resource.group(1)
            name = re.search(r"<Name>([^<]*)</Name>", block)
            kind = re.search(r"<WebResourceType>(\d+)</WebResourceType>", block)
            file_name = re.search(r"<FileName>([^<]*)</FileName>", block)
            code = int(kind.group(1)) if kind else -1
            label, extension = WEB_RESOURCE_TYPES.get(code, ("unknown type", ""))
            named = name.group(1) if name else "?"
            carries = extension and named.lower().endswith(extension)
            print(f"  web resource : {named}"
                  f"  (type {code} {label}; extension should be {extension or 'unknown'}"
                  f"{'; the name carries none either' if extension and not carries else ''})")
            if file_name:
                physical = file_name.group(1).lstrip("/")
                has_extension = Path(physical).suffix != ""
                print(f"    in the zip : {physical}"
                      f"{'   <-- no extension on disk' if not has_extension else ''}")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.strip())
        return 1
    return max(inventory(Path(argument)) for argument in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
