#!/usr/bin/env python3
"""Enforce the mechanical gates on tips and queued items.

Gates 1 (provenance), 2 (executed), 4 (fresh), 6 (cost) and 7 (sanitised) from CONTRIBUTING.md are
checked here. Gates 3, 5, 8, 9 and 10 are human or reviewer gates and cannot be enforced by a script.

Whole repository:

    python3 scripts/validate_tips.py

Specific documents only (used by scripts/test_gates.sh):

    python3 scripts/validate_tips.py _tips/42-slug.md queue/43-other.md

Front matter is parsed by a deliberately small parser that understands only what the tip schema uses:
`key: value` scalars (quoted or bare), `key: |` block scalars, and `#` comments. Anything else -
nested maps, lists, anchors, an unterminated quote, a duplicated key, a key outside the schema - is
reported as an error rather than silently ignored, so a document that parses here is a document these
checks actually read in full.

Exit code 0 when everything passes, 1 when any document fails a gate, 2 when the validator itself
cannot run - a missing surface vocabulary, for instance. CI treats anything but 0 as a failure.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROOT_RESOLVED = ROOT.resolve()
TIPS_DIR = ROOT / "_tips"  # Jekyll collections live in _<collection_name>/
QUEUE_DIR = ROOT / "queue"
DRAFTS_DIR = ROOT / "_drafts"

SURFACES_FILE = ROOT / "_data" / "surfaces.yml"


def load_surfaces() -> dict[str, str]:
    """Read the surface vocabulary from _data/surfaces.yml, mapping slug to label.

    The site groups /all/ by the same file, so a bucket cannot exist in the validator but not on the
    site. A missing, unreadable or empty file is a defect in the repository rather than in a tip, so
    it raises and the caller exits 2 instead of reporting a bogus surface error on every document.
    """
    name = SURFACES_FILE.relative_to(ROOT).as_posix()
    if not SURFACES_FILE.exists():
        raise RuntimeError(f"{name} is missing - it holds the surface vocabulary the site groups by")
    try:
        lines = SURFACES_FILE.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"{name} cannot be read: {exc}") from exc

    surfaces: dict[str, str] = {}
    slug: str | None = None
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- slug:"):
            slug = line.split(":", 1)[1].strip().strip("\"'")
            surfaces.setdefault(slug, slug)
        elif line.startswith("label:") and slug is not None:
            surfaces[slug] = line.split(":", 1)[1].strip().strip("\"'")
    if not surfaces:
        raise RuntimeError(f"{name} lists no surfaces")
    return surfaces


try:
    SURFACES = load_surfaces()
except RuntimeError as exc:
    print(f"error: the surface vocabulary is unusable - {exc}", file=sys.stderr)
    sys.exit(2)

STATES = {"ready", "blocked"}

# `date` is the day the tip was published. Jekyll reads a collection document's date from front
# matter, so the feed sorts and dates entries off it - a collection without it feeds jekyll-feed a nil
# date. It is the one field a queued item does not carry: the publish date is set at promotion.
TIP_REQUIRED = (
    "title",
    "surface",
    "tip_number",
    "date",
    "wave",
    "verified_on",
    "expires_on",
    "cost",
    "source",
    "artifact",
    "evidence",
)
QUEUE_REQUIRED = (
    "title",
    "surface",
    "tip_number",
    "state",
    "wave",
    "verified_on",
    "expires_on",
    "cost",
    "source",
    "artifact",
    "evidence",
)

# `build` and `verified_env` are the only optional keys. `published` and `example` are rejected
# outright rather than validated: Jekyll's YAML reader accepts several spellings of false (false,
# False, FALSE, no, off) and any of them drops the document out of the collection, and an `example`
# document belongs in queue/TEMPLATE.md, which is skipped by name.
OPTIONAL_KEYS = {"build", "verified_env"}
FORBIDDEN_KEYS = {"published", "example"}
ALLOWED_TIP_KEYS = set(TIP_REQUIRED) | OPTIONAL_KEYS
ALLOWED_QUEUE_KEYS = set(QUEUE_REQUIRED) | OPTIONAL_KEYS

MAX_WINDOW_DAYS = 183  # one release wave
SKIP_NAMES = {"README.md", "TEMPLATE.md"}

# A symlinked document is not a document here. git stores the link and not the content, Jekyll would
# index it under the link's name while this validator would check the target's name, and a fresh
# checkout on a platform without symlink support has no file at that path at all. The gate is meant to
# prove what the published site contains, so the file has to be the file.
SYMLINK_RULE = (
    "a symlinked document is not accepted - commit the file itself, not a link to it"
)

# Gate 7 is a heuristic net over organisation-specific endpoints, not proof of sanitisation: a tip can
# leak an identifier in prose that no pattern catches. These are the shapes that appear most often.
ORG_URL_PATTERNS = (
    r"https?://[A-Za-z0-9.\-]*\.crm\d*\.[A-Za-z0-9.\-]*dynamics\.com",  # Dataverse org, incl. /api/mcp
    r"https?://make\.powerapps\.com",
    r"https?://admin\.powerplatform\.microsoft\.com",
    r"https?://app\.powerbi\.com",
    r"https?://app\.fabric\.microsoft\.com",
    r"https?://[A-Za-z0-9.\-]+\.sharepoint\.com",
)
ORG_URL = re.compile("|".join(ORG_URL_PATTERNS), re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
BARE_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")


class FrontMatterError(Exception):
    pass


def parse_front_matter(path: Path) -> tuple[dict[str, str], str, str]:
    """Return (front matter mapping, body, raw text).

    Raises FrontMatterError on anything the schema does not allow, so no document is half-read.
    """
    try:
        raw_text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise FrontMatterError(f"cannot be read as UTF-8 text: {exc}") from exc

    lines = raw_text.splitlines()  # tolerates CRLF as well as LF
    if not lines or lines[0].strip() != "---":
        raise FrontMatterError("no front matter: the file must start with '---'")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise FrontMatterError("front matter is never closed with '---'")

    data: dict[str, str] = {}
    block_key: str | None = None
    block_lines: list[str] = []

    for offset, raw in enumerate(lines[1:end], start=2):
        if block_key is not None:
            if raw.strip() == "" or raw.startswith((" ", "\t")):
                block_lines.append(raw.rstrip("\r"))
                continue
            data[block_key] = "\n".join(block_lines).strip("\n")
            block_key, block_lines = None, []
        stripped = raw.strip()
        if stripped == "" or stripped.startswith("#"):
            continue
        m = BARE_KEY.match(raw)
        if not m:
            raise FrontMatterError(
                f"line {offset}: only 'key: value' scalars, 'key: |' blocks and '#' comments are "
                f"supported - got {raw[:60]!r}"
            )
        key, value = m.group(1), m.group(2).strip()
        if key in data:
            # block_key is always None here: the branch above flushes and resets it on any line that
            # is not part of the block, and a blank or indented line continues the loop.
            raise FrontMatterError(
                f"line {offset}: duplicate key '{key}' - the second value would win here but the "
                f"site build's YAML reader is a different parser, so the document cannot be trusted"
            )
        if value == "|":
            block_key, block_lines = key, []
            continue
        if value.startswith(("[", "{")):
            raise FrontMatterError(f"line {offset}: nested structures are not supported for '{key}'")
        data[key] = scalar(value, offset, key)

    if block_key is not None:
        data[block_key] = "\n".join(block_lines).strip("\n")

    body = "\n".join(lines[end + 1 :])
    return data, body, raw_text


def scalar(value: str, offset: int, key: str) -> str:
    """Resolve a scalar: unquote a quoted value, or strip a trailing comment from a bare one.

    Anything left after a closing quote that is not a comment is an error rather than a silent
    discard, because the module's promise is that a document which parses here is a document every
    check read in full.
    """
    if value[:1] in ('"', "'"):
        quote = value[0]
        closing = value.find(quote, 1)
        if closing == -1:
            raise FrontMatterError(f"line {offset}: unterminated quote on '{key}'")
        rest = value[closing + 1 :].strip()
        if rest and not rest.startswith("#"):
            raise FrontMatterError(
                f"line {offset}: unexpected text after the closing quote on '{key}': {rest[:30]!r} "
                f"- only a '#' comment may follow"
            )
        return value[1:closing]
    comment_at = value.find(" #")
    if comment_at != -1:
        value = value[:comment_at]
    return value.strip()


def as_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def check_schema(
    data: dict[str, str], allowed: set[str], where: str, errors: list[str], *, kind: str
) -> None:
    """Reject forbidden keys and anything outside the schema.

    `kind` is what the document is ("tip" or "queue"), so a message can name the right place to put
    the document rather than assuming it is a tip.
    """
    for key in data:
        if key in FORBIDDEN_KEYS:
            if key == "published":
                parking = (
                    "A tip that is not ready to publish belongs in queue/."
                    if kind == "tip"
                    else "A queued item is unpublished by staying in queue/, which the site never builds."
                )
                errors.append(
                    f"{where}: the key '{key}' must not appear - Jekyll treats false/False/no/off "
                    f"as false and silently drops the document out of the collection. {parking}"
                )
            else:
                errors.append(
                    f"{where}: the key '{key}' must not appear - the shape reference is "
                    f"queue/TEMPLATE.md and scripts/preview.sh renders a throwaway tip."
                )
        elif key not in allowed:
            if key == "state":
                errors.append(
                    f"{where}: unknown key 'state' - it belongs to a queued item; drop it when the "
                    f"item moves from queue/ to _tips/ and add 'date' instead"
                )
            elif key == "date":
                errors.append(
                    f"{where}: unknown key 'date' - a queued item does not carry the publish date: it "
                    f"is set at promotion, where the artifact is re-run and verified_on becomes that day"
                )
            else:
                errors.append(
                    f"{where}: unknown key '{key}' - expected one of {', '.join(sorted(allowed))}"
                )


def check_forbidden_content(raw_text: str, where: str, errors: list[str]) -> None:
    """Gate 7. Scans the whole file, front matter included."""
    hit = ORG_URL.search(raw_text)
    if hit:
        errors.append(
            f"{where}: contains an environment-specific URL ({hit.group(0)[:60]}) - gate 7 forbids "
            f"it, front matter included"
        )
    hit = EMAIL.search(raw_text)
    if hit:
        errors.append(f"{where}: contains an email address ({hit.group(0)}) - gate 7 forbids it")


def check_common(
    data: dict[str, str], raw_text: str, where: str, errors: list[str]
) -> None:
    # Emptiness is not re-checked here: every field this function inspects is required by both
    # schemas, and the required-field loop treats a present-but-empty value as missing.
    if data.get("surface") and data["surface"] not in SURFACES:
        errors.append(
            f"{where}: surface '{data['surface']}' is not one of {', '.join(sorted(SURFACES))}"
        )
    if data.get("source") and not data["source"].startswith(("http://", "https://")):
        errors.append(f"{where}: source must be an http(s) URL, got '{data['source'][:50]}'")
    evidence = data.get("evidence", "")
    if evidence and "observed" not in evidence.lower():
        errors.append(
            f"{where}: the evidence block must contain the observed output (a line starting "
            f"'observed:'), not just the command"
        )

    artifact = data.get("artifact", "")
    if artifact and artifact != "none":
        candidate = (ROOT / artifact).resolve()
        if not candidate.is_relative_to(ROOT_RESOLVED):
            errors.append(
                f"{where}: artifact '{artifact}' resolves outside the repository - it must be a "
                f"path inside it"
            )
        elif not candidate.exists():
            errors.append(f"{where}: artifact '{artifact}' does not exist in the repository")

    verified = as_date(data.get("verified_on", ""))
    expires = as_date(data.get("expires_on", ""))
    if verified and expires:
        if expires <= verified:
            errors.append(
                f"{where}: expires_on ({expires}) must be after verified_on ({verified})"
            )
        elif (expires - verified).days > MAX_WINDOW_DAYS:
            errors.append(
                f"{where}: expiry window is {(expires - verified).days} days, over the "
                f"{MAX_WINDOW_DAYS}-day cap (one release wave)"
            )
    else:
        if data.get("verified_on") and not verified:
            errors.append(f"{where}: verified_on is not an ISO date: '{data['verified_on']}'")
        if data.get("expires_on") and not expires:
            errors.append(f"{where}: expires_on is not an ISO date: '{data['expires_on']}'")

    check_forbidden_content(raw_text, where, errors)


def check_tip_number(data: dict[str, str], where: str, errors: list[str]) -> int | None:
    number = data.get("tip_number", "")
    if not number:
        return None
    if not number.isdigit():
        errors.append(f"{where}: tip_number must be an integer, got '{number}'")
        return None
    if int(number) < 1:
        errors.append(f"{where}: tip_number must be 1 or greater")
        return None
    return int(number)


def check_tip(path: Path, errors: list[str]) -> int | None:
    where = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    try:
        data, _body, raw_text = parse_front_matter(path)
    except FrontMatterError as exc:
        errors.append(f"{where}: {exc}")
        return None

    check_schema(data, ALLOWED_TIP_KEYS, where, errors, kind="tip")

    for field in TIP_REQUIRED:
        if field not in data:
            errors.append(f"{where}: missing required field '{field}'")
        elif not data[field].strip():
            errors.append(
                f"{where}: required field '{field}' is empty - an empty value reads as present to "
                f"this checker and as absent to a reader"
            )

    number = check_tip_number(data, where, errors)

    published = data.get("date", "")
    if published and not as_date(published):
        errors.append(
            f"{where}: date is not an ISO date: '{published}' - it is the publish date, and "
            f"jekyll-feed dates every entry from it"
        )
    else:
        publish_date = as_date(published) if published else None
        verified = as_date(data.get("verified_on", ""))
        expires = as_date(data.get("expires_on", ""))
        if publish_date and verified and publish_date < verified:
            errors.append(
                f"{where}: date ({publish_date}) is before verified_on ({verified}) - a tip is "
                f"verified before it is published"
            )
        if publish_date and expires and publish_date > expires:
            errors.append(
                f"{where}: date ({publish_date}) is after expires_on ({expires}) - it would be "
                f"published already expired"
            )

    expected = re.match(r"^(\d+)-[a-z0-9\-]+\.md$", path.name)
    if not expected:
        errors.append(f"{where}: file must be named <tip_number>-<slug>.md")
    elif number is not None and int(expected.group(1)) != number:
        errors.append(
            f"{where}: filename says tip {int(expected.group(1))} but tip_number is {number}"
        )

    check_common(data, raw_text, where, errors)
    return number


def check_queue_item(path: Path, errors: list[str]) -> int | None:
    where = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    try:
        data, _body, raw_text = parse_front_matter(path)
    except FrontMatterError as exc:
        errors.append(f"{where}: {exc}")
        return None

    check_schema(data, ALLOWED_QUEUE_KEYS, where, errors, kind="queue")

    for field in QUEUE_REQUIRED:
        if field not in data:
            errors.append(f"{where}: missing required field '{field}'")
        elif not data[field].strip():
            errors.append(
                f"{where}: required field '{field}' is empty - an empty value reads as present to "
                f"this checker and as absent to a reader"
            )

    if data.get("state") and data["state"] not in STATES:
        errors.append(f"{where}: state '{data['state']}' is not one of {', '.join(sorted(STATES))}")

    number = check_tip_number(data, where, errors)
    check_common(data, raw_text, where, errors)
    return number


def check_drafts(directory: Path, errors: list[str]) -> None:
    """_drafts is not used: Jekyll treats drafts as posts, not as collection documents."""
    if not directory.is_dir():
        return
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        errors.append(
            f"{path.relative_to(ROOT).as_posix()}: _drafts must not be used - a Jekyll draft is "
            f"rendered as a post, not as a tip, so the tip layout is never exercised. The shape "
            f"reference is queue/TEMPLATE.md, and scripts/preview.sh renders a throwaway tip to "
            f"check the layout."
        )


def display(path: Path) -> str:
    """A path as a contributor sees it in the repository, or the absolute path if it is outside."""
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def markdown_files(directory: Path, errors: list[str]) -> list[Path]:
    if not directory.is_dir():
        return []
    kept: list[Path] = []
    for path in sorted(directory.glob("*.md")):
        if path.name in SKIP_NAMES:
            continue
        if path.is_symlink():
            errors.append(f"{display(path)}: {SYMLINK_RULE}")
            continue
        kept.append(path)
    return kept


def scoped_files(arguments: list[str], errors: list[str]) -> tuple[list[Path], list[Path], list[str]]:
    """Resolve explicit paths into (_tips, queue) documents, noting anything skipped by name."""
    tips: list[Path] = []
    queued: list[Path] = []
    skipped: list[str] = []
    for argument in arguments:
        given = Path(argument)
        if not given.is_absolute():
            given = Path.cwd() / given
        try:
            # os.path.realpath, not Path.resolve(): resolve() raised RuntimeError on a symlink loop
            # before Python 3.10 and realpath never raises for one - it returns the path unchanged and
            # the exists() check below turns the loop into a clean message. Resolving matters because a
            # relative path containing '..', or a cwd reached through a symlink, would otherwise not
            # match TIPS_DIR and would read as being outside the corpus.
            resolved = Path(os.path.realpath(given))
        except (OSError, ValueError) as exc:
            errors.append(f"{argument}: cannot be resolved: {exc}")
            continue
        if not resolved.exists():
            errors.append(f"{argument}: no such file")
            continue
        if given.is_symlink():
            errors.append(f"{argument}: {SYMLINK_RULE}")
            continue
        # The corpus check comes before the skip list. SKIP_NAMES exists so that a glob over a corpus
        # directory tolerates queue/README.md and queue/TEMPLATE.md, and it applies only INSIDE the
        # corpus: a README.md from anywhere else is a caller mistake, and reporting it is better than
        # silently skipping it.
        if TIPS_DIR in resolved.parents or QUEUE_DIR in resolved.parents:
            if resolved.name in SKIP_NAMES:
                skipped.append(argument)
            elif TIPS_DIR in resolved.parents:
                tips.append(resolved)
            else:
                queued.append(resolved)
        else:
            errors.append(f"{argument}: not a document under _tips/ or queue/")
    return tips, queued, skipped


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    errors: list[str] = []
    seen: dict[int, str] = {}

    skipped: list[str] = []
    if arguments:
        tips, queued, skipped = scoped_files(arguments, errors)
        scope = f"{len(arguments)} path(s) given on the command line"
    else:
        tips, queued = markdown_files(TIPS_DIR, errors), markdown_files(QUEUE_DIR, errors)
        scope = "the whole repository"

    for argument in skipped:
        print(f"skip  {argument}: a template or readme, checked by name exclusion")

    for path in tips:
        where = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        number = check_tip(path, errors)
        if number is not None:
            if number in seen:
                errors.append(
                    f"{where}: tip_number {number} is already used by {seen[number]} - numbers are "
                    f"unique and never reused"
                )
            else:
                seen[number] = where

    for path in queued:
        where = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        number = check_queue_item(path, errors)
        if number is not None:
            if number in seen:
                errors.append(
                    f"{where}: tip_number {number} is already used by {seen[number]} - a published "
                    f"tip and a queued item cannot share a number"
                )
            else:
                seen[number] = where

    if not arguments:
        check_drafts(DRAFTS_DIR, errors)

    for message in errors:
        print(f"FAIL {message}", file=sys.stderr)

    if errors:
        print(
            f"\n{len(errors)} problem(s) across {len(tips) + len(queued)} document(s) "
            f"({scope}).",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK  {len(tips)} tip document(s), {len(queued)} queued item(s), all gates pass "
        f"({scope})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
