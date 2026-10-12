---
title: "Fabric deletes what you leave in an item folder"
summary: "An item folder is the one carrying .platform, or the older metadata pair. Files inside it that are not part of the item definition go at the next commit; files outside any item folder stay."
surface: fabric
tip_number: 13
state: ready
next_step: ""
wave: "n/a - Fabric Git integration; release waves were retired in September 2026"
build: "Fabric workspace source control as documented in Git integration process (the commit rule) and Git source code format (the item folder and .platform); a tree in those documented shapes read by the artifact"
verified_on: 2026-10-12
verified_env: "Linux, Python 3.14.7 - a workspace tree in the documented shapes, no Fabric tenant and no capacity"
expires_on: 2027-04-09
cost: "Free to read a workspace already committed to Git; writing back needs that Fabric workspace and its capacity"
source: "https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process"
artifact: "assets/tips/13-fabric-deletes-what-you-leave-in-an-item-folder/workspace-lint.py"
evidence: |
  command: a workspace tree in the shapes the two pages describe
  observed: |
    Sales.SemanticModel/.platform, definition/tables/Sales.tmdl
    Ops.Notebook/.platform, notes.md, definition/scratch.bak
    Legacy.Report/item.metadata.json, item.config.json, notes.md      (version 1, no .platform)
    Broken.Report/.platform, item.metadata.json, item.config.json
    README.md                                                        (outside every item folder)

  command: python3 assets/tips/13-fabric-deletes-what-you-leave-in-an-item-folder/workspace-lint.py .
  observed: |
    workspace: .
    item folders: 4, of which 1 read as version 1

      Broken.Report  (version 2)
        files: 3, of which 0 outside definition/
        all three present: item.config.json, item.metadata.json
          the pair and the platform file cannot sit together: one of them goes on the next commit

      Legacy.Report  (version 1)
        files: 3, of which 1 outside definition/
          covered by the commit rule: notes.md

      Ops.Notebook  (version 2)
        files: 3, of which 1 outside definition/
          covered by the commit rule: notes.md

      Sales.SemanticModel  (version 2)
        files: 2, of which 0 outside definition/

    covered by the commit rule: 2 file(s); item folders holding all three: 1

  The check reads the part of the rule that is visible in the tree: a file inside an item folder but
  outside definition/ is not part of the item definition. Ops.Notebook/definition/scratch.bak is the case
  it does not cover - a file the schema does not name, sitting inside definition/, which the same sentence
  covers and this check does not.

  source quotes, verbatim, from
  learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process, fetched 2026-10-12, 200:
    "During the Commit to Git process, the Fabric service deletes files inside the item folder that
     aren't part of the item definition."
    "Unrelated files not in an item folder aren't deleted."

  source quotes, verbatim, from
  learn.microsoft.com/en-us/fabric/cicd/git-integration/source-code-format, fetched 2026-10-12, 200:
    "In version 2, instead of having two source files in each item directory, the .platform file combines
     all the information into one file along with a $schema property."
    "If you have this file, you can't have the other two files."
    "You can’t have all three files."
---

## An item folder carries one metadata file, or a pair

Commit a workspace to Git and you get a folder of items. A version 2 item is a folder carrying a
`.platform` file, and a version 1 item is a folder carrying the older pair, `item.metadata.json` and
`item.config.json`. Everything the item is made of sits under its `definition` folder. Finding the items in
a clone is a search for those file names, with no API call and no workspace open.

## What the commit does to everything else

Learn's wording is that the commit deletes files inside the item folder that are not part of the item
definition, and that unrelated files outside every item folder are left alone. Put a `notes.md` beside the
`definition` folder of a notebook to remind yourself what it does, and the next commit takes it away.
Leave the same file at the root of the workspace, outside every item folder, and it stays.

The rule is about the item definition rather than the folder, so a file the schema does not name is not
part of it even when it sits inside `definition`.

## The older pair and the newer file cannot both be there

A version 2 folder that also keeps `item.metadata.json` and `item.config.json` is one commit away from
losing two of them, and that combination is worth finding before you commit rather than after.
