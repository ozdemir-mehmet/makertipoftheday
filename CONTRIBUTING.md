# Contributing

A tip is published only after it clears every gate below, in order. The gates are enforced where
they can be: `scripts/validate_tips.py` runs in CI before the site builds, and `scripts/reverify.py`
runs nightly.

## Gates

| # | Gate | What it means | Enforced by |
|---|------|---------------|-------------|
| 1 | Provenance | A primary source is cited - a Learn page, a documentation diff, a release note | `validate_tips.py` (source required, must be http(s)) |
| 2 | Executed | The artifact was run against a pinned environment; the command and its observed output are recorded with the tip | `validate_tips.py` (evidence block must contain `observed`) |
| 3 | Reproducible | Clean-room deploy with no manual steps, or every manual step enumerated | Reviewer |
| 4 | Fresh | An expiry date, capped at 183 days so that no tip claims to be current indefinitely | `validate_tips.py`, `reverify.py` |
| 5 | Terminology | Names checked against the vendor's own page on the day of publishing | Reviewer with the vendor page open |
| 6 | Cost and supportability | Licence and premium dependency stated; unsupported configuration labelled | `validate_tips.py` (cost required) |
| 7 | Sanitised | No tenant names, environment URLs, identifiers or customer data | `validate_tips.py` (blocks organisation endpoints - `*.crm*.dynamics.com`, make.powerapps.com, app.powerbi.com, app.fabric.microsoft.com, `*.sharepoint.com` - and email addresses, over the whole file) |
| 8 | Editorial | One mechanism per tip, told plainly: what it is, and what to do about it | Reviewer, against the template |
| 9 | Reviewed | Two independent reviewers over the text. Catches structure and consistency, never truth | `agent-code-review` loop, both at zero |
| 10 | Approved and rendered | Published from a preview, checked as rendered, then promoted | Merge to `main` |

## Front matter

```yaml
---
title: "Catchy and true - it has to earn the click and still be honest"
summary: "One line, 200 characters max: what the reader gets, not the tip in a paragraph."
surface: dataverse          # a slug from _data/surfaces.yml - the one place the vocabulary lives
tip_number: 42
date: 2026-10-09            # the date the tip carries; the feed dates entries from it and the listings order by it
wave: "2026 wave 1"
build: "9.2.26094.00"        # optional; the build verified against
verified_on: 2026-10-09
verified_env: "developer environment, one region, default security roles"
expires_on: 2027-04-01
cost: "Free - no premium connector, no capacity add-on"
source: "https://learn.microsoft.com/..."
artifact: "assets/tips/42-slug/solution.zip"   # or none
evidence: |
  command: ...
  observed: ...
---
```

The title and the summary are the two things a reader sees before deciding to read the tip, and the
summary is capped at 200 characters on purpose: a summary that runs longer than that is the tip.

**The body is the tip. The proof is internal, and so is the provenance.** `evidence` holds the
commands and the pasted output that convinced you the tip is true; the rest of the front matter holds
what it was checked against. None of it is rendered - `_layouts/tip.html` publishes no Evidence
section, no badge, no re-verify date, no tested-against/environment/cost/artifact/source strip, and
the listings publish no badge either. `scripts/preview.sh` asserts every one of those is ABSENT, in a
fresh state and in a lapsed one, so the rule has a guard rather than a convention. Nothing in the body
should read as proof either: no methodology recitals, no "measured across N tables", no long verbatim
quotations from the source. Those belong in `evidence`. The artifact is internal too - it is how the claim
was measured and how the tip gets re-verified - so a tip does not link it from the body, and the directory
it lives in is not published at all: `_config.yml` excludes `assets/tips` from the build.

A front-matter value in double quotes cannot contain an escaped double quote - the validator's reader
ends the value at the first closing quote and rejects what follows. If a value needs to quote
something, rephrase it or drop the quotes; the error names the offending line and key.

File naming: `_tips/<tip_number>-<slug>.md` - the `_tips` folder is a Jekyll collection, so documents
render at `/tip/<file name without extension>/`. Artifacts live separately, under
`assets/tips/<tip_number>-<slug>/`, because `_tips/` holds tip documents and nothing else - the validator
parses every file in it. That directory is excluded from the built site, so an artifact is tooling you run
from a checkout, never a download. Tip numbers are unique and never reused.

## What the validator refuses

These are file-level rules, checked in both the named-path and whole-corpus runs:

Do not use `published: false` or a `_drafts/` folder to park a document. `published: false` takes the
document out of the collection entirely - no page is written and its URL 404s - and Jekyll accepts
several spellings of false (`False`, `no`, `off`), so the failure is silent. A `_drafts/` document is
treated as a post. `scripts/validate_tips.py` rejects both, and the tip layout has no branch to
render them, because a tip that vanishes from the site with no error is the worst outcome this
repository can produce.

An `example:` key is rejected for the same reason: it was the flag on the shape reference, and the
shape reference is now `queue/TEMPLATE.md`, which the validator skips by name. Nothing under `_tips/`
carries it, and `scripts/preview.sh` renders a throwaway tip when the layout needs checking.

A document must be a file, not a symlink. The validator refuses a symlinked document in both the
scoped and whole-corpus paths: git would store the link rather than the content, Jekyll would index it
under the link's name while the validator checked the target's, and a checkout on a platform without
symlink support would have no file there at all. Commit the file itself.

## Adding a tip

Queue items come in three states, and `state` decides which schema applies:

| State | Needs | Counts toward the buffer |
|---|---|---|
| `ready` | Every field in the shape above, including a real `evidence` block | Yes - it is finished work |
| `draft` | Title, summary, surface, tip_number, source, `next_step` | No |
| `blocked` | The same as ready, plus `next_step` saying what it waits on | No |

A `draft` exists so a tip sourced from a primary document can be recorded before anyone has run its
mechanism. It deliberately cannot carry `verified_on` or `evidence`, because a sourced tip that can
look verified will eventually be published as verified. Drafts are visible in the nightly report and
excluded from the ready depth, so backfilling ideas never fakes cover for a thin week.

1. Write it into `queue/<tip_number>-<slug>.md` first, in the shape above, and mark it `state: ready`
   only when the artifact has actually been run and the evidence block holds the real output.
2. When it is due to publish, move it to `_tips/` and make two edits: **drop `state:`** (that key is
   queue-only and the validator rejects unknown keys in a tip) and add `date:` - the date the tip
   carries - after re-running the artifact. `verified_on` is the day you re-ran it. `date` is the one
   field a queued item does not carry.
3. Run `python3 scripts/validate_tips.py` and `python3 scripts/reverify.py` locally.
4. Open a PR. Two independent reviewers must return zero findings on the frozen revision.
5. Merge to `main`: the workflow validates, builds and deploys.

## Backfilling

`date` may be earlier than the day the tip was re-run. The backlog of a new site is published onto it
after the fact, and the archive should read as the run of days it describes rather than a cliff at the
day the site went up: dates from 2026-10-01, the site's first day, forward.

Three things keep that honest:

- **Never forward.** Jekyll withholds a future-dated collection document, so the tip would be missing
  from the site with no error and no failing build. `validate_tips.py` refuses the date instead.
- **One tip per date.** The listings sort by `date` alone and Liquid's `sort` has no tie-break, so two
  tips sharing a date would render in an arbitrary order.
- **The clock does not move.** The verification clock runs from `verified_on` to `expires_on`, never
  from `date`, so a backfilled tip reads as older without being any nearer to its expiry.

## Buffer

Target 10 ready items in `queue/`, alarm at 5. See `queue/README.md` for why a queued item is
finished work and why the clock runs from the re-run rather than from authoring.

## Local build and checks

```bash
jekyll build                          # the published site, in _site/
jekyll build --destination /tmp/site  # the same, without touching _site/
./scripts/preview.sh                  # throwaway tip; asserts the layout in both expiry states
python3 scripts/validate_tips.py      # the whole corpus; pass _tips/<file>.md to check one document
python3 scripts/reverify.py           # 0 = nothing due, 10 = something lapsed, anything else = it crashed
./scripts/test_gates.sh               # proves each mechanical gate actually fires
```

The deployed build is not the local build. CI uses `actions/jekyll-build-pages@v1`, which is Jekyll
3.10 with the GitHub Pages plugin allowlist; a developer's machine may have Jekyll 4. Keep to Liquid
and configuration that both understand - anything newer is a defect, not a convenience. CI is the
authority on what the site renders, and `preview.sh` is the local smoke test.

CI runs `validate_tips.py`, then `test_gates.sh`, then the build. `preview.sh` is deliberately local
only: it needs a Jekyll on the runner that the Pages action installs inside itself rather than on the
path, and a job that cannot be rehearsed locally is a job that breaks the deploy on its first push.

`reverify.py`'s exit codes matter to the nightly workflow: 10 means something lapsed and an issue is
opened, while any other non-zero code (including the 1 Python returns for an uncaught exception)
means the check itself failed and the run is failed instead. `validate_tips.py` splits the same way:
1 is a document that fails a gate, 2 is the validator itself being unable to run - a missing
`_data/surfaces.yml`, say - and the test suite proves that path too.
