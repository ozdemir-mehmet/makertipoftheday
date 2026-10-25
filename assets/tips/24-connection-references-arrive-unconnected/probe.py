#!/usr/bin/env python3
"""Re-measure what `pac solution create-settings` writes for a solution that carries connection references.

Fetches a Microsoft sample solution folder at a pinned commit, packs it with pac, runs
create-settings on the zip, and reports what each connection reference's ConnectionId holds.
Then fetches the Learn page the tip cites and checks the sentences the tip rests on.

Run from the repo root:  PYTHONDONTWRITEBYTECODE=1 python3 assets/tips/24-<slug>/probe.py
Exit 0 means the counts and the quotes still match the evidence block.
"""
import hashlib
import html
import json
import os
import pwd
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

PIN = "c615dea2eb698ba24d4a31f7f0a686bf868761ba"
SAMPLE_PATH = "infrastructure/manage-paygo/sourcecode/Other/Customizations.xml"
SAMPLE_URL = f"https://raw.githubusercontent.com/microsoft/CopilotStudioSamples/{PIN}/{SAMPLE_PATH}"
SAMPLE_SHA256 = "4f471298dc2dd108199020855e90ebe5bfdf557ada6f873f29e3c9b9c622e85c"

DOC = "https://learn.microsoft.com/en-us/power-platform/alm/conn-ref-env-variables-build-tools"
QUOTES = [
    "After importing a solution containing connection reference and environment variable information, you are prompted to provide information specific to your environment in the UI.",
    "To enable a fully automated deployment, you can now pre-populate the connection reference and environment variable information specific to the target environment so that you don't have to interactively provide it after importing a solution.",
    "To populate the deployment settings file, you will need to obtain the connection reference and environment variable information of the target solution.",
    "To get the connection ID of the target environment, use one of the following ways:",
    "This will create the required connection reference and environments with appropriate values upon import without having the user to interactively specify the value.",
    "During solution import, the connection references are validated to ensure that the connections placed inside them will be usable by the owner of the connection reference.",
    "Ensure that the connections are owned by the owner of the connection references or that the connections are shared .",
]

SOLUTION_XML = """<?xml version="1.0" encoding="utf-8"?>
<ImportExportXml version="9.2.0.0" SolutionPackageVersion="9.2" languagecode="1033" generatedBy="CrmLive" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SolutionManifest>
    <UniqueName>ConnRefProbe</UniqueName>
    <LocalizedNames><LocalizedName description="ConnRefProbe" languagecode="1033" /></LocalizedNames>
    <Version>1.0.0.0</Version>
    <Managed>0</Managed>
    <Publisher><UniqueName>mcscat</UniqueName><LocalizedNames><LocalizedName description="mcscat" languagecode="1033" /></LocalizedNames><Descriptions /><DefaultLocale xml:lang="en">1033</DefaultLocale><CustomizationPrefix>mcscat</CustomizationPrefix><CustomizationOptionValuePrefix>10000</CustomizationOptionValuePrefix></Publisher>
    <RootComponents />
    <MissingDependencies />
  </SolutionManifest>
</ImportExportXml>
"""


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def pac():
    home = os.environ.get("HOME") or pwd.getpwuid(os.getuid()).pw_dir
    dotnet = os.path.join(home, ".dotnet")
    env = dict(os.environ)
    env["HOME"] = home
    env["DOTNET_ROOT"] = dotnet
    env["PATH"] = f"{dotnet}/tools:{dotnet}:" + env.get("PATH", "")
    return env


def plain(page):
    page = re.sub(r"<script[^>]*>.*?</script>", " ", page, flags=re.S)
    page = re.sub(r"<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(page))


def main():
    fails = []
    work = tempfile.mkdtemp(prefix="connref-")
    try:
        raw = fetch(SAMPLE_URL)
        digest = hashlib.sha256(raw).hexdigest()
        print(f"sample: microsoft/CopilotStudioSamples@{PIN[:12]}  {SAMPLE_PATH}")
        print(f"sha256: {digest}")
        if digest != SAMPLE_SHA256:
            fails.append("sample sha256 moved - re-derive the claim, do not reuse this evidence")

        sol = os.path.join(work, "sol")
        os.makedirs(os.path.join(sol, "Other"))
        with open(os.path.join(sol, "Other", "Customizations.xml"), "wb") as f:
            f.write(raw)
        with open(os.path.join(sol, "Other", "Solution.xml"), "w", encoding="utf-8") as f:
            f.write(SOLUTION_XML)

        env = pac()
        zipfile = os.path.join(work, "probe.zip")
        pack = subprocess.run(
            [f"{env['DOTNET_ROOT']}/tools/pac", "solution", "pack", "--zipfile", zipfile, "--folder", sol, "--packagetype", "Unmanaged"],
            env=env, capture_output=True, text=True,
        )
        if pack.returncode != 0 or not os.path.exists(zipfile):
            fails.append(f"pac solution pack failed: {pack.stdout[-400:]}{pack.stderr[-400:]}")
            return report(fails)

        settings = os.path.join(work, "settings.json")
        made = subprocess.run(
            [f"{env['DOTNET_ROOT']}/tools/pac", "solution", "create-settings", "--solution-zip", zipfile, "--settings-file", settings],
            env=env, capture_output=True, text=True,
        )
        if made.returncode != 0 or not os.path.exists(settings):
            fails.append(f"pac solution create-settings failed: {made.stdout[-400:]}{made.stderr[-400:]}")
            return report(fails)

        with open(settings, encoding="utf-8") as f:
            doc = json.load(f)

        refs = doc.get("ConnectionReferences", [])
        empty = [r for r in refs if not r.get("ConnectionId", "").strip()]
        connectors = {}
        for r in refs:
            connectors.setdefault(r["ConnectorId"], []).append(r["LogicalName"])
        shared = {k: v for k, v in connectors.items() if len(v) > 1}
        prefixes = sorted({r["LogicalName"].split("_")[0] for r in refs})

        print(f"connection references in the settings file: {len(refs)}")
        print(f"references with an empty ConnectionId: {len(empty)}")
        print(f"distinct connectors: {len(connectors)}")
        for cid, names in shared.items():
            print(f"connector used by more than one reference ({len(names)}): {cid.rsplit('/', 1)[-1]}")
            for n in names:
                print(f"    {n}")
        print(f"publisher prefixes in the reference names: {', '.join(prefixes)}")
        print("environment variables in the settings file: %d" % len(doc.get("EnvironmentVariables", [])))

        page = fetch(DOC).decode("utf-8", "replace")
        text = plain(page)
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', page)
        print(f"page: {DOC}")
        print(f"  canonical matches: {bool(canon and canon.group(1) == DOC)}")
        if not (canon and canon.group(1) == DOC):
            fails.append("canonical link does not match source:")
        hits = 0
        for q in QUOTES:
            if q in text:
                hits += 1
            else:
                fails.append(f"quote not on the page any more: {q[:70]}...")
        print(f"  quotes present: {hits}/{len(QUOTES)}")
        if empty and len(empty) == len(refs) and len(refs) >= 4 and shared:
            print("result: every reference is emitted with no connection, and one connector is named twice")
        else:
            fails.append("the counts moved: the tip's sentence 'every reference comes out with no connection' no longer holds")
        return report(fails)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def report(fails):
    if fails:
        for f in fails:
            print(f"FAIL: {f}")
        return 1
    print("result: numbers and quotes both reproduce the evidence block")
    return 0


if __name__ == "__main__":
    sys.exit(main())
