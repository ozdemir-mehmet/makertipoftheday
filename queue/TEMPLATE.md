---
# Queue item template. Copy to queue/<tip_number>-<slug>.md and fill in.
# Nothing in this file is published; it is the holding pen for tips that are on their way.
#
# Three states live here, and `state` decides which schema applies:
#
#   state: ready   finished work. Every field below is required, including `evidence` - the pasted
#                  output of the artifact as it was actually run. This is the only state counted
#                  toward the buffer depth that reverify.py reports.
#   state: draft   a tip sourced from a primary document whose mechanism has not been executed yet.
#                  Requires title, summary, surface, tip_number, source and `next_step` only. It
#                  deliberately cannot carry `verified_on` or `evidence`, so a sourced tip can never
#                  look like a verified one. Drafts are excluded from the buffer depth.
#   state: blocked waiting on something outside the tip itself; say what in `next_step`.
#
# A queued item carries every field a tip needs except `date` - the publish date is set when the
# item moves to _tips/, because the verification clock starts at publish.
title: ""
summary: ""                 # one line, 200 characters max - what the reader gets, not the tip itself
surface: dataverse          # a slug from _data/surfaces.yml
tip_number: 0               # the number it will carry when published
state: ready                # ready | draft | blocked
next_step: ""               # draft or blocked only: the one step that would finish this tip
wave: ""                    # the wave or build line it was verified against
build: ""
verified_on: 2026-01-01     # the date the artifact was last executed
verified_env: ""            # region and shape of environment, no tenant names or URLs
expires_on: 2026-07-01      # no further out than one release wave
cost: ""                    # licence and premium dependency
source: ""                  # primary source URL
artifact: none              # path to the artifact, or none
evidence: |
  command:
  observed:
  # internal only. The proof the tip was really run - commands, pasted output, counts. Never rendered
  # on the site: a reader gets the tip and the provenance strip, the author keeps the lab notebook.
---
