---
title: "Pin pac in a tool manifest, and stop trusting the pac on your PATH"
summary: "Installing the Power Platform CLI into a .NET tool manifest pins the version, so the pac your pipeline runs is the pac you tested."
surface: extensibility
tip_number: 2
date: 2026-10-02
wave: "n/a - CLI only, no environment was touched"
build: "pac 2.13.1+g251dee1 on .NET SDK 10.0.400"
verified_on: 2026-10-09
verified_env: "Linux (CachyOS), .NET SDK 10.0.400; the CLI installed from nuget.org into a throwaway tool manifest - no environment connection, every command offline"
expires_on: 2027-03-31
cost: "Free - the .NET SDK, NuGet and pac are free; no premium connector or capacity involved"
source: "https://learn.microsoft.com/en-us/power-platform/developer/cli/introduction"
artifact: "assets/tips/2-pin-pac-cli-with-a-tool-manifest/check-pac-version.py"
evidence: |
  command: dotnet new tool-manifest && dotnet tool install Microsoft.PowerApps.CLI.Tool
  observed: |
    The template "Dotnet local tool manifest file" was created successfully.
    Tool 'microsoft.powerapps.cli.tool' (version '2.13.1') was successfully installed. Entry is added
    to the manifest file /home/you/probe/dotnet-tools.json

  command: cat dotnet-tools.json
  observed: |
    {
      "version": 1,
      "isRoot": true,
      "tools": {
        "microsoft.powerapps.cli.tool": {
          "version": "2.13.1",
          "commands": [ "pac" ],
          "rollForward": false
        }
      }
    }
    (and .config/dotnet-tools.json was not created: ls reports no such file)

  command: dotnet tool restore   # with no manifest anywhere above the working directory
  observed: |
    Cannot find a manifest file. The list of searched paths:
    	/home/you/probe/.config/dotnet-tools.json
    	/home/you/probe/dotnet-tools.json
    	...
    exit: 0      <-- the step passes, having restored nothing

  command: dotnet tool restore   # with the manifest in place
  observed: |
    Tool 'microsoft.powerapps.cli.tool' (version '2.13.1') was restored. Available commands: pac
    Restore was successful.
    exit: 0

  command: dotnet tool run pac --version
  observed: |
    Microsoft PowerPlatform CLI
    Version: 2.13.1+g251dee1 (.NET 10.0.11)
    Online documentation: https://aka.ms/PowerPlatformCLI
    Feedback, Suggestions, Issues: https://github.com/microsoft/powerplatform-build-tools/discussions

    Error: Not a valid command. Try running 'pac [command] help'.
    Hints:
    exit: 1

  command: dotnet tool run pac help
  observed: |
    Microsoft PowerPlatform CLI
    Version: 2.13.1+g251dee1 (.NET 10.0.11)
    Online documentation: https://aka.ms/PowerPlatformCLI
    (then the usage list)
    exit: 0

  command: dotnet tool run pac --help
  observed: |
    Description:
      Run a local tool. Note that this command cannot be used to run a global tool.
    Usage:
      dotnet tool run <commandName> [<toolArguments>...] [options]
    exit: 0      <-- dotnet answers, pac never sees the flag, no version is printed

  command: python3 check-pac-version.py        # no pac on PATH
  observed: |
    ok    the manifest resolves pac 2.13.1 (/home/you/probe/dotnet-tools.json)
    ok    no pac on PATH, so every pac command goes through the manifest
    exit: 0
    (with the pin edited to 2.12.0 it prints "Run \"dotnet tool restore\" to make the \"pac\" command
    available." and exits 1; with no manifest above the working directory it prints
    "FAIL  no dotnet-tools.json found at or above <path>" and exits 1)

  command: dotnet tool restore   # with the manifest pinned to 2.12.0, which the feed does not carry
  observed: |
    Version 2.12.0 of package microsoft.powerapps.cli.tool is not found in NuGet feeds
    https://api.nuget.org/v3/index.json.
    exit: 1
    (and pac is then unrunnable: `dotnet tool run pac help` exits 1 with
     Run "dotnet tool restore" to make the "pac" command available.
     `dotnet tool install Microsoft.PowerApps.CLI.Tool` rewrites the entry to 2.13.1 and fixes it)

  command: edit the pin to 2.11.2 and restore, with 2.13.1 already installed on the machine
  observed: |
    Restore was successful.
    dotnet tool run pac help -> Version: 2.11.2+g47bc199 (.NET 10.0.11), exit 0
    (the pin held; nothing rolled forward onto the 2.13.1 that was already there)

  command: manifest only at .config/dotnet-tools.json, nothing at the root
  observed: |
    dotnet tool restore      -> Restore was successful. exit 0
    dotnet tool run pac help -> Version: 2.13.1+g251dee1 (.NET 10.0.11), exit 0

  command: both manifests in one directory, the root pinned to 2.13.1 and .config to 2.11.2
  observed: |
    dotnet tool run pac help -> Version: 2.11.2+g47bc199 (.NET 10.0.11)
    (the .config file won; with only the root present the same command reported 2.13.1, and with only
    the .config file present it reported 2.11.2)

  command: the same question across directories - a parent's .config against a child's plain manifest
  observed: |
    parent/.config 2.11.2 vs child/dotnet-tools.json 2.13.1, run from the child
      -> Version: 2.13.1+g251dee1 (.NET 10.0.11)    the nearer directory won
    parent/dotnet-tools.json 2.13.1 vs child/.config 2.11.2, run from the child
      -> Version: 2.11.2+g47bc199 (.NET 10.0.11)
    a parent's .config alone, run from the child
      -> Version: 2.11.2+g47bc199 (.NET 10.0.11)    the search walks upward
    (so the order is: nearest directory first, and inside a directory .config before the root file -
    which is what check-pac-version.py implements and what its docstring now states)

  command: dotnet tool run pac data / pac package deploy / pac package show
  observed: |
    pac data           -> Error: Not a valid command. Try running 'pac [command] help'. exit 1
    pac package deploy -> Error: No profiles were found on this computer. Please run 'pac auth
                          create' to create one. exit 1   (the command exists; auth is what stopped it)
    pac package show   -> Error: The command 'show' is not understood in this context. exit 1
    pac package        -> Usage: pac package [init] [add-external-package] [add-solution] [add-reference]
                          [deploy] [db-sync]   exit 0
    (so this build has no data group and no package show, while package deploy is present and only
    wanted a login - which is what the caveat in the body now says)

  command: dotnet tool install --global Microsoft.PowerApps.CLI.Tool --version 2.11.2
  observed: |
    Tool 'microsoft.powerapps.cli.tool' (version '2.11.2') was successfully installed.
    which pac -> /home/you/.dotnet/tools/pac
    pac help  -> Version: 2.11.2+g47bc199 (.NET 10.0.11)

  command: python3 check-pac-version.py        # same directory, that global pac now on PATH
  observed: |
    ok    the manifest resolves pac 2.13.1 (/home/you/probe/dotnet-tools.json)
    FAIL  /home/you/.dotnet/tools/pac is on PATH and reports 2.11.2, but the pin is 2.13.1
          a step that runs `pac ...` gets the PATH one; remove it, or pin the same version
    exit: 1
    (with PAC_PATH_CHECK=0 the PATH half is skipped and it exits 0; with the global pac removed it
    prints "ok    no pac on PATH, so every pac command goes through the manifest" and exits 0)
---

The pac CLI packs your solutions, unpacks them and imports your environment variables. On most machines,
the version that runs is whichever one you installed last.

`dotnet new tool-manifest` and `dotnet tool install Microsoft.PowerApps.CLI.Tool` change that. They put a
manifest into version control, and every machine and pipeline then runs the same build through `dotnet
tool restore`. The entry carries the version and `"rollForward": false`, and that pair holds: I pinned a
manifest to 2.11.2 with 2.13.1 already installed on the same box, and `dotnet tool run pac help` still
reported 2.11.2.

Here is what bit me on the way to a pin that works.

## The manifest is not where the guides put it

Every guide says `.config/dotnet-tools.json`. On .NET SDK 10.0.400, `dotnet new tool-manifest` writes
`dotnet-tools.json` into the current directory instead - your repository root. Both layouts restore, and
restore walks upwards, so a root manifest is still found from a subdirectory.

If you end up with both files, `.config/dotnet-tools.json` is the one that wins. Edit the root copy and
nothing changes.

And when there is no manifest anywhere, the command does not fail. It prints `Cannot find a manifest
file. The list of searched paths:`, lists every path it looked in, and exits 0. Your pipeline step
passes, having restored nothing.

## The version check that breaks a build

`pac --version` looks harmless. It prints the banner, then `Error: Not a valid command. Try running 'pac
[command] help'.` and exits 1 - a red build from the most innocent-looking line in the script.

`pac help` exits 0 and carries the same `Version:` line.

`dotnet tool run pac --help` is worse than either. The .NET tool runner takes `--help` for itself,
prints its own usage and exits 0, so the step passes and never mentions pac.

## A pin the feed does not carry

Point the manifest at a version NuGet does not have and `dotnet tool restore` fails: `Version 2.12.0 of
package microsoft.powerapps.cli.tool is not found in NuGet feeds`. After that pac will not run at all -
`Run "dotnet tool restore" to make the "pac" command available`.

Fix the version in the file and run `dotnet tool restore`, or let `dotnet tool install
Microsoft.PowerApps.CLI.Tool` rewrite the entry to the newest version for you. The pipeline stops either
way, which is what you want - but the message names the version and not the file you have to edit.

## The second pac on your machine

A global install is a second pac, and it is the one your shell finds first. With 2.11.2 installed
globally while the manifest pinned 2.13.1, `which pac` pointed at `~/.dotnet/tools/pac` and a bare `pac
help` reported 2.11.2. A step that types `pac ...` gets that one. Only `dotnet tool run` honours the
manifest.

## What this install does not have

`pac data` is not a command in the .NET Tool build at all - `Error: Not a valid command`. The `package`
group it does have is `init`, `add-external-package`, `add-solution`, `add-reference`, `deploy` and
`db-sync`, with no `show`. The vendor's install matrix puts those behind the Windows MSI or the VS Code
extension. A manifest pins pac; it cannot add commands.
