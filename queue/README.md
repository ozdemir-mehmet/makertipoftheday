# Queue - the tip buffer

A day with nothing worth publishing is normal: the change feed is thin between release waves, and a
generated filler tip is worse than no tip. The queue is what covers those days.

## Rules

1. **A `ready` item is finished work.** Artifact built, executed, evidence captured, nothing left to
   write. A `draft` is the exception the state exists for: a tip sourced from a primary document whose
   mechanism nobody has run yet. Drafts are recorded here so the sourcing is not lost, and they are
   excluded from the depth count so they can never stand in for cover.
2. **Depth.** Target 10 ready items; the alarm threshold is 5. `scripts/reverify.py` reports the
   depth and the nightly workflow opens an issue when it drops below the threshold.
3. **The verification clock runs from the re-run, not from authoring.** CI re-runs every queued item
   minutes before it goes out. If it fails, it goes back to the queue and the day stays empty. The
   clock runs from `verified_on` to `expires_on`, so a date the tip carries that is earlier than the
   re-run - a backfill - shows the tip as older without moving it nearer to its expiry.
4. **Build the buffer unevenly.** Mechanism tips - pipeline stages, security model behaviour, Direct
   Lake semantics - keep for a year. Feature tips ("what wave 1 added to X") rot in weeks. The
   buffer's backbone is the slow-rotting kind; change-driven tips publish near-immediately.
5. **Expect the season.** Power Platform ships two waves a year - wave 1 GA in April, wave 2 GA in
   October, plans published in January and July - so the feed is dense for roughly six weeks after
   each plan. Fill the queue in those windows; drain it in the quiet ones.
6. **The change feed is not the release plans.** Release plans stopped publishing in September 2026
   in favour of the "AI at Work" roadmap. Watch that page plus the MicrosoftDocs repos, the pac CLI
   and XrmToolBox release notes, and the Fabric and Power Platform blog feeds.

## Item states

- `ready` - verified, publishable today.
- `draft` - sourced from a primary document, mechanism not yet executed. Needs `next_step`, cannot
  carry `verified_on` or `evidence`, and does not count toward the depth.
- `blocked` - verified but waiting on something external (an environment, a licence, a wave).

## Naming

`<tip_number>-<slug>.md`, matching the tip number it will carry when published, so the queue and the
published collection stay reconcilable. Publishing is a move and three edits:
`queue/<n>-<slug>.md` to `_tips/<n>-<slug>.md`, **drop the `state:` key** (it is queue-only, and the
validator rejects unknown keys in a tip), add `date:` - the date the tip carries, backfillable to
2026-10-01 and never forward - and re-run the artifact.
