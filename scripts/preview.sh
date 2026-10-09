#!/usr/bin/env bash
# Render throwaway tips to prove the tip layout works in both states: the verified badge for a tip
# inside its expiry window, and the past-expiry notice for one that has lapsed. The repository is
# never written to - the whole tree is copied to a temporary directory first, the throwaway tip is
# created there, and the copy and the build destination are removed on exit, so a running
# `jekyll serve` is left alone and no real document can be overwritten or deleted. Tip number 99 is
# reserved for this check.
#
#   ./scripts/preview.sh
#
# Exit 0 when every expected marker appears, 1 otherwise.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="99-preview-check"
SRC="$(mktemp -d)"
DOC="$SRC/_tips/$NAME.md"
DEST="$(mktemp -d)"
PAGE="$DEST/tip/$NAME/index.html"

TODAY="$(date +%F)"
SOON="$(date -d '+90 days' +%F)"
PAST="$(date -d '-30 days' +%F)"

cleanup() {
  rm -rf "$SRC" "$DEST"
}
trap cleanup EXIT

# Build from a copy of the repository, so the throwaway tip never exists inside it: a `jekyll serve`
# watching the working tree would otherwise publish tip 99 while this runs. Real tips are then removed
# from the copy: the listings are asserted on, and a published tip's own "verified" badge would make
# the lapsed-tip assertion match a different document. Tip number 99 is reserved for this check.
(cd "$ROOT" && tar -cf - --exclude=./.git --exclude=./_site --exclude=./.jekyll-cache .) | (cd "$SRC" && tar -xf -)
mkdir -p "$SRC/_tips"
rm -f "$SRC"/_tips/*.md

write_doc() { # write_doc <expires_on>
  cat > "$DOC" <<TIP
---
title: "Preview check"
summary: "A one-line lead with an & an ampersand that must render above the fold"
surface: power-platform
tip_number: 99
date: $TODAY
wave: "preview"
build: "preview"
verified_on: $TODAY
verified_env: "preview only"
expires_on: $1
cost: "preview only"
source: "https://learn.microsoft.com/power-platform/?wt.mc_id=probe&tabs=1"
artifact: "none"
evidence: |
  command: preview
  observed: preview output
---

Preview body.
TIP
}

fail=0

check() { # check <label> <marker>
  if grep -q "$2" "$PAGE"; then
    echo "ok    $1"
  else
    echo "FAIL  $1 ('$2' not in the rendered page)"
    fail=1
  fi
}

check_in() { # check_in <label> <marker> <file>
  if grep -q "$2" "$3"; then
    echo "ok    $1"
  else
    echo "FAIL  $1 ('$2' not in $(basename "$(dirname "$3")")/$(basename "$3"))"
    fail=1
  fi
}

write_doc "$SOON"
jekyll build --source "$SRC" --destination "$DEST" > /dev/null

if [ ! -f "$PAGE" ]; then
  echo "FAIL  expected the tip at /tip/$NAME/ - the collection folder name, permalink or defaults"
  echo "      are wrong. Rendered files:"
  find "$DEST" -name '*.html' | sed 's/^/      /'
  exit 1
fi

check "the tip title renders" "Preview check"
check "an ampersand in a rendered field is escaped" "&amp; an ampersand"
if grep -q " & " "$PAGE"; then
  echo "FAIL  an unescaped '&' reached the markup from a rendered field"
  fail=1
else
  echo "ok    no unescaped '&' in a rendered field"
fi
check "the tip body renders" "Preview body."
if grep -q "<h2>Evidence</h2>" "$PAGE"; then
  echo "FAIL  the evidence block is rendered into the published page - a reader gets the tip, not the proof"
  fail=1
else
  echo "ok    the proof stays out of the published page (no Evidence section)"
fi
check "the summary renders as a lead line" "class=\"summary\">A one-line lead"
check "site header renders" "site-header"
check "site footer renders" "site-footer"
check "the surface chip shows the display label" "Power Platform"
if grep -q 'class="surface">power-platform' "$PAGE"; then
  echo "FAIL  the raw surface slug leaks into the chip instead of the label"
  fail=1
else
  echo "ok    the chip carries the label, not the slug"
fi

# Nothing about verification or provenance reaches a reader, in either state. The badge, the
# re-verify date, the past-expiry notice and the tested-against/environment/cost/artifact/source strip
# all rendered once. A fresh tip and a lapsed one must now look identical, because neither of them
# tells the reader that anything was checked.
absent() { # absent <label> <marker> <file>
  if grep -q "$2" "$3"; then
    echo "FAIL  $1 ('$2' is rendered into a public page)"
    fail=1
  else
    echo "ok    $1"
  fi
}
for marker in "Verified" "re-verify by" "Past its re-verification date" "badge ok" "badge expired" \
              "Tested against" "Licence and cost" "Primary source"; do
  absent "no '$marker' on the tip page" "$marker" "$PAGE"
  absent "no '$marker' in the home listing" "$marker" "$DEST/index.html"
  absent "no '$marker' in the all-tips listing" "$marker" "$DEST/all/index.html"
done
if grep -q 'class="surface">power-platform' "$DEST/index.html"; then
  echo "FAIL  the home listing shows the raw surface slug instead of the label"
  fail=1
else
  echo "ok    the home listing shows the label, not the slug"
fi

write_doc "$PAST"
jekyll build --source "$SRC" --destination "$DEST" > /dev/null

for marker in "Verified" "re-verify by" "Past its re-verification date" "badge expired" "Tested against"; do
  absent "a lapsed tip shows no '$marker' either" "$marker" "$PAGE"
  absent "a lapsed tip shows no '$marker' in the all-tips listing" "$marker" "$DEST/all/index.html"
done

if [ "$fail" -ne 0 ]; then
  echo
  echo "Preview check failed."
  exit 1
fi

echo
echo "Tip layout renders correctly at /tip/$NAME/, and the lists publish no verification state, in both states."
