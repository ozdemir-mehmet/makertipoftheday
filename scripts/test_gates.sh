#!/usr/bin/env bash
# Prove that the mechanical gates in scripts/validate_tips.py actually fire.
#
# Throwaway documents are created under _tips/ and queue/ using the reserved tip number 9999. The
# script refuses to start if any path it would write already exists, validates only its own fixtures
# through the validator's scoped invocation, and removes everything it created on exit - including on
# the failure path. Nothing is committed.
#
#   ./scripts/test_gates.sh
#
# Exit codes: 0 every gate fired, 1 a gate did not fire, 2 refused to run because a fixture exists.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATE="$ROOT/scripts/validate_tips.py"
DOC="$ROOT/_tips/9999-gate-test.md"
ODD="$ROOT/_tips/gate-test.md"
QUEUED="$ROOT/queue/9999-gate-test.md"
LINK="$ROOT/_tips/9999-gate-link.md"
SURFACES="$ROOT/_data/surfaces.yml"
REPORT="$ROOT/reverify-report.md"
REPORT_BACKUP=""
fails=0

# reverify.py writes a report at the repository root. Keep any existing one intact: back it up now and
# restore it on exit, rather than deleting or overwriting what was there before this ran.
if [ -e "$REPORT" ]; then
  REPORT_BACKUP="$REPORT.bak"
  mv "$REPORT" "$REPORT_BACKUP"
fi

# These directories are empty in the repository and git does not carry empty directories, so a fresh
# clone has neither: the fixtures have to be able to create the ground they are written into.
mkdir -p "$ROOT/_tips" "$ROOT/queue"

for existing in "$DOC" "$ODD" "$QUEUED" "$LINK" "$REPORT.bak"; do
  if [ -e "$existing" ]; then
    echo "Refusing to run: $existing already exists and this test would overwrite it." >&2
    exit 2
  fi
done

cleanup() {
  rm -f "$DOC" "$ODD" "$QUEUED" "$LINK"
  if [ -n "$REPORT_BACKUP" ]; then mv -f "$REPORT_BACKUP" "$REPORT"; else rm -f "$REPORT"; fi
  [ -f "$SURFACES.off" ] && mv "$SURFACES.off" "$SURFACES"
  return 0
}
trap cleanup EXIT

# Under `set -e` an unexpected failure would otherwise abort the run silently and leave the exit code
# as the only clue: this line makes an incomplete run say so.
trap 'echo "ABORT line $LINENO: a fixture command failed - the run is incomplete" >&2' ERR

# Defaults for each case; individual cases override before calling write_doc.
reset_case() {
  TITLE="Gate test"
  SURFACE="dataverse"
  NUMBER="9999"
  PUBLISHED="2026-01-10"
  VERIFIED="2026-01-01"
  EXPIRES="2026-06-01"
  ARTIFACT="none"
  EVIDENCE="observed: test output"
  BODY="body"
  EXTRA=""
}

write_doc() {
  cat > "$DOC" <<EOF
---
title: "$TITLE"
summary: "One line that says what the reader gets"
surface: $SURFACE
tip_number: $NUMBER
date: $PUBLISHED
wave: "2026 wave 1"
verified_on: $VERIFIED
verified_env: "test environment"
expires_on: $EXPIRES
cost: "free"
source: "https://learn.microsoft.com/"
artifact: "$ARTIFACT"
$EXTRA
evidence: |
  command: test
  $EVIDENCE
---
$BODY
EOF
}

write_queue() { # write_queue <tip_number> <state> [extra front matter lines]
  local extra="${3-}"
  cat > "$QUEUED" <<EOF
---
title: "Gate test queued item"
summary: "One line that says what the reader gets"
surface: dataverse
tip_number: $1
state: $2
wave: "2026 wave 1"
verified_on: 2026-01-01
verified_env: "test environment"
expires_on: 2026-06-01
cost: "free"
source: "https://learn.microsoft.com/"
artifact: "none"
$extra
evidence: |
  command: test
  observed: test output
---
EOF
}

expect() { # expect <label> <expected-exit> <message-substring> [paths to validate...]
  local label="$1" want="$2" needle="$3"
  shift 3
  local out rc
  out="$(python3 "$VALIDATE" "$@" 2>&1)" && rc=0 || rc=$?
  if [ "$rc" -ne "$want" ]; then
    echo "FAIL  $label: exit $rc, expected $want"
    printf '%s\n' "$out" | sed 's/^/      /'
    fails=1
    return
  fi
  if [ -n "$needle" ] && ! printf '%s' "$out" | grep -q "$needle"; then
    echo "FAIL  $label: no message containing '$needle'"
    printf '%s\n' "$out" | sed 's/^/      /'
    fails=1
    return
  fi
  echo "ok    $label"
}

reset_case; write_doc
expect "a clean tip passes" 0 "all gates pass" "$DOC"

reset_case; TITLE=""; write_doc
expect "an empty title is rejected" 1 "required field 'title' is empty" "$DOC"

reset_case; NUMBER=""; write_doc
expect "an empty tip_number is rejected" 1 "required field 'tip_number' is empty" "$DOC"

reset_case; VERIFIED=""; write_doc
expect "an empty verified_on is rejected" 1 "required field 'verified_on' is empty" "$DOC"

reset_case; ARTIFACT=""; write_doc
expect "an empty artifact is rejected" 1 "required field 'artifact' is empty" "$DOC"

reset_case; EXPIRES="2026-08-01"; write_doc
expect "expiry beyond one release wave is rejected" 1 "over the" "$DOC"

reset_case; EXPIRES="2025-12-01"; write_doc
expect "expiry before verification is rejected" 1 "must be after" "$DOC"

reset_case; ARTIFACT="assets/tips/nope/solution.zip"; write_doc
expect "a missing artifact path is rejected" 1 "does not exist" "$DOC"

reset_case; ARTIFACT="/etc/passwd"; write_doc
expect "an artifact outside the repository is rejected" 1 "resolves outside" "$DOC"

reset_case; EVIDENCE="result: something happened"; write_doc
expect "evidence without observed output is rejected" 1 "observed" "$DOC"

reset_case; BODY="Deployed against https://contoso.crm6.dynamics.com/main.aspx"; write_doc
expect "an environment URL in the body is rejected" 1 "environment-specific URL" "$DOC"

reset_case; EXTRA='build: "https://contoso.crm6.dynamics.com"'; write_doc
expect "an environment URL in the front matter is rejected" 1 "environment-specific URL" "$DOC"

reset_case; BODY="Mail the maintainer at someone@example.com"; write_doc
expect "an email address is rejected" 1 "email address" "$DOC"

reset_case; EXTRA="published: false"; write_doc
expect "published: false inside _tips is rejected" 1 "must not appear" "$DOC"

reset_case; EXTRA='build: "9.2.26094.00" # the build verified against'; write_doc
expect "a quoted value with a trailing comment parses" 0 "all gates pass" "$DOC"

reset_case; EXTRA='build: "9.2.26094.00" garbage'; write_doc
expect "junk after a closing quote is rejected" 1 "after the closing quote" "$DOC"

reset_case; EXTRA="example: true"; write_doc
expect "example: true inside _tips is rejected" 1 "must not appear" "$DOC"

reset_case; SURFACE="sharepoint"; write_doc
expect "an unknown surface is rejected" 1 "is not one of" "$DOC"

reset_case; SURFACE="extensibility"; write_doc
expect "the seventh surface is accepted" 0 "all gates pass" "$DOC"

reset_case; PUBLISHED="last Tuesday"; write_doc
expect "a non-ISO publish date is rejected" 1 "not an ISO date" "$DOC"

reset_case; PUBLISHED="2025-12-30"; write_doc
expect "a publish date before the verification is rejected" 1 "before verified_on" "$DOC"

reset_case; PUBLISHED="2026-09-01"; write_doc
expect "a publish date after the expiry is rejected" 1 "already expired" "$DOC"

mv "$SURFACES" "$SURFACES.off"
reset_case; write_doc
expect "a missing surface vocabulary is the validator's own failure" 2 "surface vocabulary" "$DOC"
mv "$SURFACES.off" "$SURFACES"

reset_case; EXTRA='wav: "typo"'; write_doc
expect "an unknown key is rejected" 1 "unknown key" "$DOC"

reset_case; EXTRA="state: ready"; write_doc
expect "a promoted item still carrying state is rejected" 1 "drop it when the" "$DOC"

reset_case; EXTRA="expires_on: 2026-07-01"; write_doc
expect "a duplicated key is rejected" 1 "duplicate key" "$DOC"

reset_case; write_doc; mv "$DOC" "$ODD"
expect "a filename without a tip number is rejected" 1 "must be named" "$ODD"
rm -f "$ODD"

reset_case; write_doc
write_draft() { # write_draft <tip_number> [extra front matter lines]
  local extra="${2-}"
  cat > "$QUEUED" <<EOF
---
title: "Gate test draft"
summary: "One line that says what the reader gets"
surface: dataverse
tip_number: $1
state: draft
source: "https://learn.microsoft.com/"
$extra
---
EOF
}

write_queue 9999 ready
expect "a tip number reused between _tips and queue is rejected" 1 "already used" "$DOC" "$QUEUED"

write_queue 9999 ready "published: false"
expect "published inside a queued item is rejected without a move instruction" 1 "staying in queue" "$QUEUED"

write_queue 9999 ready
expect "a well-formed queued item passes" 0 "all gates pass" "$QUEUED"

write_queue 9998 mostly
expect "an unknown queue state is rejected" 1 "not one of" "$QUEUED"

write_queue 9998 ready "date: 2026-01-10"
expect "a queued item carrying a publish date is rejected" 1 "publish date" "$QUEUED"

# A sourced tip that has not been executed must not be able to look like finished work, and must not
# inflate the buffer metric that reverify.py reports.
write_draft 9997 "next_step: \"Run the two GETs against a development environment\""
expect "a sourced draft passes on the lighter schema" 0 "all gates pass" "$QUEUED"

write_draft 9997
expect "a draft without a next step is rejected" 1 "missing required field 'next_step'" "$QUEUED"

ready_on_disk=$(grep -l "^state: ready" "$ROOT"/queue/*.md 2>/dev/null | grep -vE "/(README|TEMPLATE)\.md$" | wc -l)
reported=$(python3 "$ROOT/scripts/reverify.py" 2>&1 | grep -oE "queue [0-9]+ ready" | grep -oE "[0-9]+" || echo "")
if [ -n "$reported" ] && [ "$ready_on_disk" = "$reported" ]; then
  echo "ok    drafts are excluded from the ready-queue depth ($reported ready)"
else
  echo "FAIL  ready count mismatch: $ready_on_disk ready on disk, reverify reported '$reported'"
  fails=1
fi

cat > "$QUEUED" <<'EOF'
---
title: "Ready without evidence"
summary: "One line that says what the reader gets"
surface: dataverse
tip_number: 9996
state: ready
wave: "2026 wave 1"
verified_on: 2026-01-01
expires_on: 2026-06-01
cost: "free"
source: "https://learn.microsoft.com/"
artifact: "none"
---
EOF
expect "a ready item with no evidence block is rejected" 1 "missing required field 'evidence'" "$QUEUED"

cat > "$QUEUED" <<'EOF'
---
title: "Empty summary"
summary: ""
surface: dataverse
tip_number: 9995
state: ready
wave: "2026 wave 1"
verified_on: 2026-01-01
expires_on: 2026-06-01
cost: "free"
source: "https://learn.microsoft.com/"
artifact: "none"
evidence: |
  command: test
  observed: test output
---
EOF
expect "an empty summary is rejected" 1 "required field 'summary' is empty" "$QUEUED"

write_queue 9995 ready
python3 - "$QUEUED" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
p.write_text(p.read_text().replace('summary: "One line that says what the reader gets"',
                                   'summary: "' + "x" * 201 + '"'))
PY
expect "a 201-character summary is rejected" 1 "over the 200-character cap" "$QUEUED"

expect "a path outside the corpus is rejected" 1 "not a document under" "$ROOT/CONTRIBUTING.md"

reset_case; write_doc
# queue/../_tips is the discriminating form: its lexical parents do not contain _tips, so this case
# fails if the resolve() call is removed. _tips/../_tips would pass lexically either way, which is a
# false positive - proved by deleting the call and watching the suite stay green.
expect "a scoped path crossing a directory and landing in _tips is resolved" 0 "all gates pass" "$ROOT/queue/../_tips/9999-gate-test.md"

# A symlink must be refused in both entry points: the scoped one, and the whole-corpus walk, which
# reaches the file through glob() and never goes near scoped_files().
reset_case; write_doc; ln -s "$DOC" "$LINK"
expect "a symlinked document is rejected when named" 1 "symlinked document is not accepted" "$LINK"
expect "a symlinked document is rejected by the corpus walk" 1 "symlinked document is not accepted"
rm -f "$LINK"

# SKIP_NAMES covers a glob over a corpus directory, not a README from anywhere else.
expect "the queue readme is still skipped by name" 0 "all gates pass" "$ROOT/queue/README.md"
expect "the queue template is still skipped by name" 0 "all gates pass" "$ROOT/queue/TEMPLATE.md"
expect "a readme outside the corpus is rejected, not skipped" 1 "not a document under" "$ROOT/README.md"

# The nightly job imports validate_tips and calls into it. A change to a shared signature that only the
# validator's own self-test exercises would take out the scheduled run with a TypeError, and nothing in
# CI runs reverify.py outside the nightly schedule, so it is checked here.
reset_case
out="$(python3 "$ROOT/scripts/reverify.py" 2>&1)" && rc=0 || rc=$?
if [ "$rc" -eq 0 ] || [ "$rc" -eq 10 ]; then
  echo "ok    reverify.py still runs and returns a documented code (exit $rc)"
else
  echo "FAIL  reverify.py exited $rc - its own contract calls anything outside 0 and 10 a crash"
  printf '%s\n' "$out" | sed 's/^/      /'
  fails=1
fi
for needle in "ready" "alarm" "report:"; do
  if printf '%s' "$out" | grep -q "$needle"; then
    echo "ok    reverify.py reports '$needle'"
  else
    echo "FAIL  reverify.py output is missing '$needle'"
    printf '%s\n' "$out" | sed 's/^/      /'
    fails=1
  fi
done

# A document the nightly job cannot read must be reported, not counted as a healthy absence.
printf 'this file has no front matter at all\n' > "$QUEUED"
out="$(python3 "$ROOT/scripts/reverify.py" 2>&1)" && rc=0 || rc=$?
if [ "$rc" -eq 10 ] && printf '%s' "$out" | grep -q "structural problem"; then
  echo "ok    an unparseable document is reported as a structural problem"
else
  echo "FAIL  an unparseable document was not reported (exit $rc)"
  printf '%s\n' "$out" | sed 's/^/      /'
  fails=1
fi
if grep -q "## Structural problems" "$REPORT"; then
  echo "ok    the report carries a Structural problems section"
else
  echo "FAIL  the report has no Structural problems section"
  fails=1
fi
rm -f "$QUEUED"

cleanup
if [ "$fails" -ne 0 ]; then
  echo
  echo "Gate self-test failed."
  exit 1
fi

echo
echo "All gates fired as expected. Repository left clean:"
echo "  _tips: $(ls -A "$ROOT/_tips" | wc -l) file(s), queue: $(ls -A "$ROOT/queue" | wc -l) file(s)"
