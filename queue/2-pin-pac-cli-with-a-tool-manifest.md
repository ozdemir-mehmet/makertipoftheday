---
title: "Pin pac in a tool manifest, and stop trusting the pac on your PATH"
summary: "`dotnet tool install Microsoft.PowerApps.CLI.Tool` in a tool manifest turns pac into a pinned dependency, so the version you tested is the version everyone runs."
surface: cross-cutting
tip_number: 2
wave: "n/a - CLI only, no environment was touched"
build: "pac 2.13.1+g251dee1"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), .NET SDK 10.0.400, dotnet tool install from nuget.org, no environment connection - every command below ran offline"
expires_on: 2027-03-31
cost: "Free - the .NET SDK, NuGet and pac are free; no premium connector or capacity involved"
source: "https://learn.microsoft.com/en-us/power-platform/developer/cli/introduction"
artifact: "assets/tips/2-pin-pac-cli-with-a-tool-manifest/check-pac-version.py"
state: ready
evidence: |
  command: dotnet new tool-manifest && dotnet tool install Microsoft.PowerApps.CLI.Tool
  observed: |
    You can invoke the tool from this directory using the following commands: 'dotnet tool run pac' or 'dotnet pac'.
    Tool 'microsoft.powerapps.cli.tool' (version '2.13.1') was successfully installed.
    Entry is added to the manifest file /home/you/probe/dotnet-tools.json

  command: ls dotnet-tools.json .config/dotnet-tools.json
  observed: dotnet-tools.json exists at the repository root; .config/dotnet-tools.json was not created

  command: dotnet tool restore && dotnet tool run pac help
  observed: |
    Tool 'microsoft.powerapps.cli.tool' (version '2.13.1') was restored. Available commands: pac
    Restore was successful.
    Microsoft PowerPlatform CLI
    Version: 2.13.1+g251dee1 (.NET 10.0.11)

  command: dotnet tool run pac --version   # the version check that does not work
  observed: |
    Microsoft PowerPlatform CLI
    Version: 2.13.1+g251dee1 (.NET 10.0.11)
    Error: Not a valid command. Try running 'pac [command] help'.
    Hints:
      Parse failed on:            --version
      Is this a known command?    No, was it misspelled?
    exit code: 1

  command: python3 assets/tips/1-pin-pac-cli-with-a-tool-manifest/check-pac-version.py
  observed: |
    ok    pac 2.13.1 matches the pin in /home/you/probe/dotnet-tools.json
    exit code: 0
    (with the pin edited to 2.12.0 it prints "Run \"dotnet tool restore\" to make the \"pac\" command
    available." and exits 1; with no manifest above the working directory it prints
    "FAIL  no dotnet-tools.json found at or above <path>" and exits 1)
---

**tl;dr** `dotnet new tool-manifest` then `dotnet tool install Microsoft.PowerApps.CLI.Tool` puts a pac
version under version control, and every machine and pipeline then runs that exact build through
`dotnet tool restore`. It also gives you a version check that does not quietly pass.

## The mechanism

1. `dotnet new tool-manifest` at the repository root.
2. `dotnet tool install Microsoft.PowerApps.CLI.Tool` - 2.13.1 was current when this was verified.
3. Commit the manifest. In the pipeline: `dotnet tool restore`, then `dotnet tool run pac ...`.

`rollForward: false` in the manifest is what makes this a pin rather than a suggestion: the tool does
not drift onto a newer patch because someone's machine had a newer one.

## The gotchas

**The manifest is not where the blog posts put it.** On .NET SDK 10.0.400, `dotnet new tool-manifest`
writes `dotnet-tools.json` in the current directory, at the repository root - not
`.config/dotnet-tools.json`. Both layouts restore, and restore searches upward, so a manifest at the
root is found from a subdirectory and a hand-made `.config/dotnet-tools.json` is honoured too. If you
find neither, `dotnet tool restore` says `No tools were restored.` and prints the path it searched,
which is the fastest way to see which manifest your build is actually reading.

**`pac --version` fails the build.** It prints the version banner and then reports
`Parse failed on: --version` and exits 1. In a pipeline step, that is a red build from a command whose
name suggests it is harmless. `pac help` exits 0 and carries the same banner; `pac --help` exits 0 but
does not print a version at all. Use `pac help` and read the `Version:` line.

**A pinned pac is not a full pac.** By the vendor's own page, the .NET Tool install method does not
enable `pac data`, `pac package deploy` or `pac package show` - those need the Windows MSI or the VS
Code extension. If a pipeline stage needs them, the tool manifest alone cannot run it.

## The artifact

`check-pac-version.py` reads the pin from the manifest, asks the CLI through the manifest
(`dotnet tool run pac help`, so PATH cannot sway the answer), and fails when the two disagree or when
no pin can be found. Run it after `dotnet tool restore` and before anything that touches an
environment.

## Why this is not just tidiness

The CLI you think you are running is the one that writes your solution packages, packages your
plugins and imports your environment variables. A laptop with an MSI install and a pipeline running a
NuGet tool can disagree about behaviour without anyone changing anything, and the difference surfaces
as a diff in a solution file that nobody edited.
