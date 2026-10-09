---
# Queue item template. Copy to queue/<tip_number>-<slug>.md and fill in.
# Nothing in this file is published; it is the holding pen for finished tips.
# A queued item carries every field a tip needs except `date` - the publish date is set when the
# item moves to _tips/, because the verification clock starts at publish.
title: ""
surface: dataverse          # a slug from _data/surfaces.yml
tip_number: 0               # the number it will carry when published
state: ready                # ready | blocked
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
---
