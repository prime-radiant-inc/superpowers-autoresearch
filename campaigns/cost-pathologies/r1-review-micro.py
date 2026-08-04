#!/usr/bin/env python3
"""R1 MICRO: review-triage policy calibration battery (plan-decomposition
campaign, 2026-08-03, Task 5).

Pre-registered per the campaign design's R1 axis
(`docs/2026-08-03-plan-decomposition-campaign-design.md`: "review triage /
cleanup wave... plus the x2b lens question as policy sub-arms (suppress vs
downgrade-to-deferred)") and the plan's Task 5
(`docs/plans/2026-08-03-plan-decomposition-campaign.md`: "x2b-review-micro
variants: lens-suppress vs lens-downgrade-to-deferred vs cleanup-wave
instruction; graded on severity/verdict language vs the controls' noise
floor... FULL R1 battery only if micro shows a usable policy separation").

## Why this instrument, and what it adds over x2b-review-micro.py

`x2b-review-micro.py` (Task 4 of the prior backlog campaign) measured
whether a reviewer LENS changes if a structure-only finding fires at all:
substance-over-structure suppresses it 10/10 -> 0/10 at zero
false-positive cost on a tree with ONLY a structural deviation, no real
defect. That result answers a mechanism question (does the lens work) but
not the POLICY question this campaign's R1 axis asks: once you accept
that structure-only findings need to stop rathole-ing the task loop,
which triage RULE should the review loop actually run --
suppress it entirely, downgrade it to a ledgered Minor, or route it to an
explicit non-blocking cleanup-wave section? And, load-bearingly. does
any of those three policies leak onto a REAL defect sitting in the same
tree -- the guard this design doc's R1 entry names explicitly ("Predicts:
fix-loop rounds per task drop without defect-escape growth (escape guard
binds -- X1-edit fixture class re-used)").

This script answers both by adding a second tree (`mixed`, see
`micro-fixtures/r1/mixed/` and its `SEEDED-BUG-LEDGER.md`) that carries
the SAME structural deviation as x2b's `deviant/` tree PLUS one
independent, genuine Important-severity behavior bug, and a 2x4 design
crossing {deviant, mixed} against four review-system-prompt policies.

## Reachability

Same argument as `x2b-review-micro.py`'s docstring, unchanged: the
reviewer subagent's entire system prompt for this battery IS the filled
template (derived from `task-reviewer-prompt.md`'s control text -- see
below), so every policy's patched paragraphs are read on every call of
that cell by construction. No reachability gap to pre-register against.

## Fixtures: three trees, one new

- `deviant` (reused, NOT duplicated): `micro-fixtures/x2b/deviant/`, the
  same tree `x2b-review-micro.py` uses -- referenced by path, read via
  this script's own `TREE_DIRS`, never copied.
- `mixed` (new): `micro-fixtures/r1/mixed/`, `deviant` plus one seeded
  Important bug (`formatSummaryCsv` silently drops zero-amount
  categories -- see `micro-fixtures/r1/SEEDED-BUG-LEDGER.md`, which lives
  outside `mixed/` and is never packed into a reviewer's prompt).
- `conformant` (x2b's fourth cell) is NOT reused here -- R1's question is
  about triage behavior on findings that exist, so both R1 trees carry
  the structural deviation; a no-deviation control adds a cost without
  adding discriminating power to a triage-POLICY question (x2b already
  covers the "does anything fire on a clean tree" case).

Both trees are reviewed against the same plan
(`micro-fixtures/x2b/plan.md`, imported, not copied) and the same global
constraints.

## Policy arms

Built on the same `task-reviewer-prompt.md` control template x2b uses
(imported here as `X2B.BASE_TEMPLATE`, byte-identical import -- not
retyped, so there is no drift risk between the two scripts' shared
control text). Two NEW insertion points are added via anchored
`str.replace()` on that imported string (`R1_TEMPLATE` below,
`{triage_policy_insert}` in Calibration and `{issues_subheadings}` in
Output Format) -- both replacements assert their anchor text is found
so a future edit to `x2b-review-micro.py`'s `BASE_TEMPLATE` fails loud
here instead of silently drifting. The two placeholders x2b already
defines (`{structure_line}`, `{judge_what_brief_insert}`) are reused
as-is.

  - **plain** (control): x2b's `PLAIN_STRUCTURE_LINE`, empty
    `judge_what_brief_insert`, empty `triage_policy_insert`, the
    unmodified Critical/Important/Minor sub-headings. Byte-identical to
    x2b's own `plain` variant.
  - **lens-suppress**: x2b's `X2B_STRUCTURE_LINE` +
    `JUDGE_WHAT_BRIEF_INSERT`, VERBATIM imports from x2b -- this IS
    x2b's `x2b-lens` arm, renamed for this battery's cell-naming
    convention. No new text.
  - **lens-downgrade**: same substance-over-structure judgment
    (`X2B_STRUCTURE_LINE`, reused) but a DIFFERENT Part-1 insert
    (`DOWNGRADE_JUDGE_INSERT`): a structure-only deviation is still
    filed, at Minor, with a one-line Cleanup Ledger entry -- never
    suppressed outright, never allowed above Minor, never moving the
    verdict. New `DOWNGRADE_TRIAGE_INSERT` in Calibration states the
    same rule from the severity-bucketing side.
  - **cleanup-wave**: judgment stays PLAIN (`PLAIN_STRUCTURE_LINE`, no
    Part-1 insert) -- this arm is purely about ROUTING, not about
    whether a structure-only finding is a finding at all. Output Format
    drops the `#### Minor (Nice to Have)` bucket in favor of a
    `### Cleanup Wave (non-blocking)` section (`CLEANUP_ISSUES_
    SUBHEADINGS`); `CLEANUP_TRIAGE_INSERT` in Calibration states
    Critical/Important are reserved for catastrophic/behavioral
    findings only.

## 2x4 design

{deviant, mixed} tree x {plain, lens-suppress, lens-downgrade,
cleanup-wave} prompt = 8 cells, REPS reps each (env `REPS`, default 8 per
the plan's Task 5 cell count; env `MODEL`, default `claude-opus-4-8`,
matching x2b).

## DO NOT RUN

This script makes real, billed API calls when invoked without
`--dry-run`. Per the R1 brief, this implementation does not run the
battery -- the controller does, and only after this MICRO shows a usable
policy separation (per the plan's Task 5). `--dry-run` assembles and
writes all 8 cells' system + user prompts to
`/tmp/r1-review-micro-dry-run/` for inspection and makes zero API calls.

## Output

One JSONL line per call, appended to `out/r1-review-micro/results.jsonl`:
`cell` (e.g. `"mixed--lens-downgrade"`), `rep` (0-indexed), `raw_review`
(full response text), and the extracted fields below. Extraction
(`extract_review_fields` and helpers) is TDD'd against handwritten sample
reviews in `test_r1_review_micro.py` before being trusted here, following
the same discipline as x2b/x1/x1b -- tolerant of multiple phrasings (see
`DEVIATION_RE`, reused from x2b, and the new `REAL_BUG_RE`), and every
raw answer is saved to `out/r1-review-micro/answers/` for hand-rescoring
regardless of what the extractor decides.

Section extraction is heading-position-based (`_heading_blocks`), not the
lookahead-regex design x2b's `SECTION_RE` uses: a recognized section's
body is cut off at the NEXT markdown heading of any kind, not just the
next RECOGNIZED one, so an off-canonical heading a model might emit
(a shortened `### Cleanup` instead of the prompted `### Cleanup Wave
(non-blocking)`, an invented `### Behavioral Findings`, or no heading at
all) never gets silently absorbed into -- and then discarded by -- the
preceding known bucket's "(none)" placeholder. Every signal below is
therefore reported in three states, not two: sectioned (found in a
recognized bucket, severity known), unsectioned-but-present (found
somewhere in the answer outside every recognized bucket's span --
severity ambiguous, flagged for hand review), or absent (no match
anywhere). The summary table prints unsectioned counts alongside
sectioned/blocking counts so the controller sees this ambiguity
directly instead of a fabricated "missed."

  - `structure_flagged` / `structure_section` / `structure_unsectioned`:
    does any finding match the plan-file-structure deviation signature
    (x2b's `DEVIATION_RE`, reused verbatim) inside a recognized bucket
    (`Critical` / `Important` / `Minor` / `Cleanup Wave`, first match by
    that severity order), or -- only checked when no sectioned match
    exists -- anywhere else in the answer text?
  - `real_bug_flagged` / `real_bug_section` / `real_bug_unsectioned` /
    `real_bug_blocking`: does any finding match the seeded zero-amount-
    CSV bug signature (`REAL_BUG_RE`), sectioned or unsectioned per the
    same rule, and -- only meaningful when sectioned, since an
    unsectioned match's severity is exactly what's ambiguous -- is that
    section one this cell's own policy treats as blocking (`Critical` or
    `Important`)? THE critical metric for `mixed--*` cells: does the
    real bug survive triage at blocking severity under every policy, or
    does some policy's machinery catch it in the same net as the
    structural finding -- or bury it somewhere the extractor can only
    mark ambiguous, never silently absent?
  - `verdict_language`: the `**Task quality:** ...` line verbatim, if
    present (x2b's `extract_verdict_language`, reused).

Everything here is synthetic; no real system.
"""
import argparse
import importlib.util
import json
import os
import pathlib
import re
import sys
import urllib.request

HERE = pathlib.Path(__file__).parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# x2b-review-micro.py is not a valid Python module name (hyphens); loaded
# by path, same idiom test_x2b_review_micro.py already uses. Reused for
# BASE_TEMPLATE, PLAN, GLOBAL_CONSTRAINTS, the two shared structure-line /
# judge-insert constants, DEVIATION_RE, pack_tree, split_findings, and
# extract_verdict_language -- everything this battery shares byte-for-byte
# with x2b rather than risking drift by retyping it.
X2B = _load("x2b_review_micro", HERE / "x2b-review-micro.py")

API = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("MODEL", "claude-opus-4-8")
REPS = int(os.environ.get("REPS", "8"))
ONLY = [v.strip() for v in os.environ.get("ONLY", "").split(",") if v.strip()]

X2B_FIXTURE_DIR = HERE / "micro-fixtures" / "x2b"
R1_FIXTURE_DIR = HERE / "micro-fixtures" / "r1"
OUT = HERE / "out" / "r1-review-micro"
DRY_RUN_DIR = pathlib.Path("/tmp/r1-review-micro-dry-run")

PLAN = X2B.PLAN
GLOBAL_CONSTRAINTS = X2B.GLOBAL_CONSTRAINTS

# ---------------------------------------------------------------------------
# R1_TEMPLATE: X2B.BASE_TEMPLATE (imported, byte-identical) plus two new
# anchored insertion points. Both anchors are asserted present so a future
# edit to x2b-review-micro.py's BASE_TEMPLATE fails loudly here rather than
# silently dropping a placeholder.
# ---------------------------------------------------------------------------

_CALIBRATION_ANCHOR = "human decides.\nAcknowledge what was done well"
_CALIBRATION_REPLACEMENT = (
    "human decides.\n{triage_policy_insert}Acknowledge what was done well"
)
_OUTPUT_ANCHOR = (
    "#### Critical (Must Fix)\n#### Important (Should Fix)\n"
    "#### Minor (Nice to Have)\n\nFor each issue:"
)
_OUTPUT_REPLACEMENT = "{issues_subheadings}\n\nFor each issue:"

if _CALIBRATION_ANCHOR not in X2B.BASE_TEMPLATE:
    raise RuntimeError("R1: Calibration anchor not found in X2B.BASE_TEMPLATE -- drifted?")
if _OUTPUT_ANCHOR not in X2B.BASE_TEMPLATE:
    raise RuntimeError("R1: Output Format anchor not found in X2B.BASE_TEMPLATE -- drifted?")

R1_TEMPLATE = X2B.BASE_TEMPLATE.replace(
    _CALIBRATION_ANCHOR, _CALIBRATION_REPLACEMENT, 1
).replace(_OUTPUT_ANCHOR, _OUTPUT_REPLACEMENT, 1)

# ---------------------------------------------------------------------------
# Policy-arm text. lens-suppress reuses X2B.X2B_STRUCTURE_LINE and
# X2B.JUDGE_WHAT_BRIEF_INSERT verbatim -- no new text for that arm.
# ---------------------------------------------------------------------------

DOWNGRADE_JUDGE_INSERT = """
Judge what the brief required, not how it illustrated the work. A file
at another path, a differently named helper, or a structure that departs
from the plan's illustration costs the implementer nothing while the
requirement is still met -- but note it anyway, filed at Minor per the
triage policy in Calibration below, never as Critical or Important, and
never weighed against the Task quality verdict. When a deviation loses a
requirement, that is a different kind of finding: the lost requirement,
quoted to the line that states it, at full severity.
"""

DOWNGRADE_TRIAGE_INSERT = """Triage policy for structure-only findings: when a finding is purely
about file organization or naming and the requirement it touches is
still met, file it as Minor -- never Critical or Important -- and add
one line to a Cleanup Ledger at the end of your Minor list, in the form
`- [structure] <one-sentence summary>.` A structure-only finding never
moves the Task quality verdict; a behavioral or missed-requirement
finding always can, regardless of its own severity bucket.
"""

CLEANUP_TRIAGE_INSERT = """Triage policy: Critical and Important are reserved for catastrophic or
behavioral defects -- incorrect output, a missed or broken requirement, a
crash, or damage severe enough to block the task. A finding that is
purely structural (file organization, naming) or purely polish
("coverage could be broader," style nits) never occupies Critical or
Important, no matter how strongly you feel about it -- route it instead
to the Cleanup Wave section at the end of your report, one line per
finding, clearly non-blocking.
"""

DEFAULT_ISSUES_SUBHEADINGS = (
    "#### Critical (Must Fix)\n#### Important (Should Fix)\n#### Minor (Nice to Have)"
)
CLEANUP_ISSUES_SUBHEADINGS = (
    "#### Critical (Must Fix)\n#### Important (Should Fix)\n\n"
    "### Cleanup Wave (non-blocking)\n"
    "[Structural and polish findings only -- one line each, never blocking.]"
)


def _fill(template, structure_line, judge_what_brief_insert, triage_policy_insert, issues_subheadings):
    filled = template.format(
        structure_line=structure_line,
        judge_what_brief_insert=judge_what_brief_insert,
        triage_policy_insert=triage_policy_insert,
        issues_subheadings=issues_subheadings,
    )
    return (
        filled.replace("[BRIEF_FILE]", "the Plan in the user message below")
        .replace("[GLOBAL_CONSTRAINTS]", GLOBAL_CONSTRAINTS)
        .replace("[REPORT_FILE]", "the Implementer's Report in the user message below")
        .replace("[TREE_FILE]", "the Tree Contents in the user message below")
    )


PROMPT_VARIANTS = {
    "plain": _fill(R1_TEMPLATE, X2B.PLAIN_STRUCTURE_LINE, "", "", DEFAULT_ISSUES_SUBHEADINGS),
    "lens-suppress": _fill(
        R1_TEMPLATE, X2B.X2B_STRUCTURE_LINE, X2B.JUDGE_WHAT_BRIEF_INSERT, "", DEFAULT_ISSUES_SUBHEADINGS
    ),
    "lens-downgrade": _fill(
        R1_TEMPLATE, X2B.X2B_STRUCTURE_LINE, DOWNGRADE_JUDGE_INSERT,
        DOWNGRADE_TRIAGE_INSERT, DEFAULT_ISSUES_SUBHEADINGS,
    ),
    "cleanup-wave": _fill(
        R1_TEMPLATE, X2B.PLAIN_STRUCTURE_LINE, "", CLEANUP_TRIAGE_INSERT, CLEANUP_ISSUES_SUBHEADINGS
    ),
}

TREES = ["deviant", "mixed"]
POLICIES = ["plain", "lens-suppress", "lens-downgrade", "cleanup-wave"]
TREE_DIRS = {
    "deviant": X2B_FIXTURE_DIR / "deviant",
    "mixed": R1_FIXTURE_DIR / "mixed",
}
CELLS = [f"{tree}--{policy}" for tree in TREES for policy in POLICIES]


def build_user_message(tree_name):
    tree_dir = TREE_DIRS[tree_name]
    report = (tree_dir / "task-report.md").read_text()
    tree_contents = X2B.pack_tree(tree_dir)
    return f"""## Plan

{PLAN}

## Implementer's Report

{report}

## Tree Contents

{tree_contents}

Produce your review now, following the Output Format exactly."""


USER_MESSAGE = {tree: build_user_message(tree) for tree in TREES}


def cell_prompt(cell):
    tree, policy = cell.split("--", 1)
    return PROMPT_VARIANTS[policy], USER_MESSAGE[tree]


def call(system_text, user_text):
    key = os.environ["ANTHROPIC_API_KEY"]
    body = {
        "model": MODEL,
        "max_tokens": 3000,
        "system": system_text,
        "messages": [{"role": "user", "content": user_text}],
    }
    req = urllib.request.Request(
        API, json.dumps(body).encode(),
        {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    text = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
    usage = d.get("usage", {})
    return text, usage


def run_sample(cell, rep):
    system_text, user_text = cell_prompt(cell)
    ans_f = OUT / "answers" / f"{cell}-r{rep}.txt"
    usage_f = OUT / "usage" / f"{cell}-r{rep}.json"
    if not ans_f.exists() or not usage_f.exists():
        print(f"  calling {cell} r{rep} ...", file=sys.stderr, flush=True)
        text, usage = call(system_text, user_text)
        ans_f.write_text(text)
        usage_f.write_text(json.dumps(usage, indent=2))
    return ans_f.read_text(), json.loads(usage_f.read_text())


# ---------------------------------------------------------------------------
# Extraction heuristics. TDD'd against handwritten sample reviews in
# test_r1_review_micro.py.
#
# Section splitting is heading-POSITION-based (`_heading_blocks`), not the
# lookahead-regex design x2b's SECTION_RE uses (match up to the next
# RECOGNIZED bucket heading). That lookahead design has a silent failure
# mode: an unrecognized heading in between (a shortened "### Cleanup"
# instead of the prompted "### Cleanup Wave (non-blocking)", an invented
# "### Behavioral Findings") gets absorbed into the PRECEDING recognized
# section's captured body instead of ending it -- and if that preceding
# section is an empty "(none)" bucket, split_findings' leading-"(none)"
# shortcut then discards everything after it, including the absorbed
# heading's real content. `_heading_blocks` splits at every heading
# (recognized or not), so an unrecognized heading's body is simply never
# "covered" by a known bucket and falls through to the full-text fallback
# search in `extract_review_fields` below instead of being swallowed.
# ---------------------------------------------------------------------------

_ANY_HEADING_RE = re.compile(r"^#{2,4}[ \t]*(.+?)[ \t]*$", re.M)
_BUCKET_NAMES = {"critical": "Critical", "important": "Important", "minor": "Minor",
                  "cleanup wave": "Cleanup Wave"}
# Longest name first: cheap insurance against a future bucket name that is
# itself a prefix of another (none collide today).
_BUCKET_NAME_ORDER = sorted(_BUCKET_NAMES, key=len, reverse=True)
SEVERITY_ORDER = ["Critical", "Important", "Minor", "Cleanup Wave"]
BLOCKING_SECTIONS = {"Critical", "Important"}

# Reused verbatim from x2b: the plan-file-structure deviation signature.
DEVIATION_RE = X2B.DEVIATION_RE

# The seeded mixed-tree bug: formatSummaryCsv filters out zero-amount
# categories (see micro-fixtures/r1/SEEDED-BUG-LEDGER.md). Tolerant of
# either "zero-amount signal near a CSV/filter signal" ordering, up to 300
# chars apart, case-insensitive -- mirrors DEVIATION_RE's multi-phrasing
# tolerance rather than pinning one exact sentence.
_ZERO_SIGNAL = r"(?:zero[- ]?(?:amount|total|value)s?|amounts?\s*(?:of\s*|is\s*|=+\s*)?0\b|totals?\s+of\s+0|net[- ]zero)"
_CSV_SIGNAL = r"(?:\bcsv\b|formatsummarycsv|\.filter\()"
REAL_BUG_RE = re.compile(
    rf"{_ZERO_SIGNAL}[\s\S]{{0,300}}?{_CSV_SIGNAL}"
    rf"|{_CSV_SIGNAL}[\s\S]{{0,300}}?{_ZERO_SIGNAL}",
    re.I,
)

TASK_QUALITY_LINE_RE = X2B.TASK_QUALITY_LINE_RE
split_findings = X2B.split_findings
extract_verdict_language = X2B.extract_verdict_language


def _bucket_name(heading_title):
    """Map a heading's title text to a known bucket name, or None if it
    doesn't start with one of the four recognized names (a model-invented
    "Behavioral Findings", a shortened "Cleanup", "Assessment", "Issues",
    "Strengths", etc. all correctly map to None here)."""
    t = heading_title.strip().lower()
    for name in _BUCKET_NAME_ORDER:
        if t.startswith(name):
            return _BUCKET_NAMES[name]
    return None


def _heading_blocks(answer_text):
    """Split answer_text at every markdown heading (## through ####,
    recognized bucket name or not). Returns (bucket_or_None, start, end,
    body_start) per heading, each block running from its heading to the
    START of the next heading of ANY kind (or end of text) -- this is
    what stops a recognized section's body from swallowing an
    unrecognized heading placed after it."""
    headings = list(_ANY_HEADING_RE.finditer(answer_text))
    blocks = []
    for i, m in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(answer_text)
        blocks.append((_bucket_name(m.group(1)), m.start(), end, m.end() + 1))
    return blocks


def extract_sections(answer_text):
    out = {}
    for bucket, _start, end, body_start in _heading_blocks(answer_text):
        if bucket is None:
            continue
        body = answer_text[body_start:end].strip()
        out[bucket] = (out[bucket] + "\n\n" + body) if bucket in out else body
    return out


def _covered_spans(answer_text):
    """Character spans of every RECOGNIZED bucket's block -- the region
    the sectioned path (extract_sections + split_findings) already
    scanned. Anything outside these spans (an unrecognized heading's
    body, a table under a custom heading, bare prose with no heading at
    all, or text before the first heading) is what the full-text
    fallback in extract_review_fields checks."""
    return [(start, end) for bucket, start, end, _body_start in _heading_blocks(answer_text)
            if bucket is not None]


def _matches_outside_spans(pattern, answer_text, covered_spans):
    return any(
        not any(s <= m.start() < e for s, e in covered_spans)
        for m in pattern.finditer(answer_text)
    )


def _first_match(sections, pattern):
    for sev in SEVERITY_ORDER:
        findings = split_findings(sections.get(sev, ""))
        if any(pattern.search(f) for f in findings):
            return sev
    return None


_LIST_LINE_RE = re.compile(r"^\s*(?:[-*•]|\d+\.)\s")
_TOP_SECTION_RE = re.compile(r"^#{2,4}\s*(.+?)\s*$")
_PROSE_SECTIONS = ("strength", "assessment", "reasoning")


def _structure_raised(answer_text):
    """Hand-rescore semantics for 'the structure issue was RAISED': a
    DEVIATION_RE match on a finding line (list item) in any section
    except Strengths/Assessment. This is what the bucket model misses --
    reviewers using the task-reviewer layout raise the deviation as a
    Spec Compliance ❌ line, which is a raise even though Spec Compliance
    is not a severity bucket. Prose mentions in Assessment/Reasoning
    ('the only deviation is disclosed...') and 'None.'-lead bucket
    explanations are reasoned-away, not raised -- they are list-item-less
    or live in prose sections, so they stay excluded. Calibrated against
    the 104-answer corpus (2026-08-04)."""
    section = ""
    for line in answer_text.splitlines():
        m = _TOP_SECTION_RE.match(line)
        if m:
            section = m.group(1).lower()
            continue
        if any(p in section for p in _PROSE_SECTIONS):
            continue
        if _LIST_LINE_RE.match(line) and DEVIATION_RE.search(line):
            return True
    return False


def extract_review_fields(answer_text):
    sections = extract_sections(answer_text)
    covered = _covered_spans(answer_text)

    structure_section = _first_match(sections, DEVIATION_RE)
    real_bug_section = _first_match(sections, REAL_BUG_RE)

    # Three states per signal: sectioned (a section name below), absent
    # (neither field set), or unsectioned-but-present -- only checked
    # when the sectioned path found nothing, since a sectioned match
    # already proves presence.
    structure_unsectioned = structure_section is None and _matches_outside_spans(
        DEVIATION_RE, answer_text, covered)
    real_bug_unsectioned = real_bug_section is None and _matches_outside_spans(
        REAL_BUG_RE, answer_text, covered)

    return {
        "structure_flagged": structure_section is not None or structure_unsectioned,
        "structure_raised": structure_section is not None or _structure_raised(answer_text),
        "structure_section": structure_section or "none",
        "structure_unsectioned": structure_unsectioned,
        "real_bug_flagged": real_bug_section is not None or real_bug_unsectioned,
        "real_bug_section": real_bug_section or "none",
        "real_bug_unsectioned": real_bug_unsectioned,
        "real_bug_blocking": real_bug_section in BLOCKING_SECTIONS if real_bug_section else False,
        "verdict_language": extract_verdict_language(answer_text),
    }


def dry_run():
    DRY_RUN_DIR.mkdir(parents=True, exist_ok=True)
    for cell in CELLS:
        system_text, user_text = cell_prompt(cell)
        (DRY_RUN_DIR / f"{cell}.system.md").write_text(system_text)
        (DRY_RUN_DIR / f"{cell}.user.md").write_text(user_text)
    print(f"wrote {len(CELLS)} cells' assembled prompts to {DRY_RUN_DIR}")
    for cell in CELLS:
        print(f"  {cell}.system.md, {cell}.user.md")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Assemble and write all 8 cells' prompts to /tmp for inspection; make no API calls.")
    args = parser.parse_args()

    if args.dry_run:
        dry_run()
        return

    (OUT / "answers").mkdir(parents=True, exist_ok=True)
    (OUT / "usage").mkdir(parents=True, exist_ok=True)
    cells = [c for c in CELLS if not ONLY or c in ONLY]
    print(f"# R1 review-triage MICRO (MODEL={MODEL}, REPS={REPS})")

    jsonl_path = OUT / "results.jsonl"
    total_input_tokens = 0
    total_output_tokens = 0
    counts = {}
    with jsonl_path.open("w") as jsonl_f:
        for cell in cells:
            n_structure_sectioned = 0
            n_structure_unsectioned = 0
            n_bug_blocking = 0
            n_bug_unsectioned = 0
            for rep in range(REPS):
                raw_review, usage = run_sample(cell, rep)
                fields = extract_review_fields(raw_review)
                if fields["structure_section"] != "none":
                    n_structure_sectioned += 1
                if fields["structure_unsectioned"]:
                    n_structure_unsectioned += 1
                if fields["real_bug_blocking"]:
                    n_bug_blocking += 1
                if fields["real_bug_unsectioned"]:
                    n_bug_unsectioned += 1
                total_input_tokens += usage.get("input_tokens", 0) + usage.get(
                    "cache_creation_input_tokens", 0)
                total_output_tokens += usage.get("output_tokens", 0)
                jsonl_f.write(json.dumps({
                    "cell": cell,
                    "rep": rep,
                    "raw_review": raw_review,
                    **fields,
                }) + "\n")
            counts[cell] = (n_structure_sectioned, n_structure_unsectioned, n_bug_blocking, n_bug_unsectioned)

    # Unsectioned counts are printed alongside sectioned/blocking counts,
    # not folded into "flagged" totals -- an unsectioned hit means
    # "present, severity ambiguous, go read the raw answer," which the
    # controller needs to see as its own number, not a rounding error.
    print()
    header = (f"{'cell':<28}{'struct-sectioned':>17}{'struct-unsect':>15}"
              f"{'bug-blocking':>14}{'bug-unsect':>12}{'n':>5}")
    print(header)
    print("-" * len(header))
    for cell in cells:
        n_ss, n_su, n_bb, n_bu = counts[cell]
        print(f"{cell:<28}{n_ss:>13}/{REPS:<3}{n_su:>10}/{REPS:<3}"
              f"{n_bb:>9}/{REPS:<3}{n_bu:>7}/{REPS:<3}{REPS:>5}")
    print()
    print("(*-unsect counts are present-but-ambiguous, not absent -- see", file=sys.stderr)
    print(" raw_review in results.jsonl for hand-rescoring.)", file=sys.stderr)
    print(f"wrote {jsonl_path}", file=sys.stderr)
    print(f"usage: {total_input_tokens} input tokens (incl. cache-creation), "
          f"{total_output_tokens} output tokens", file=sys.stderr)


if __name__ == "__main__":
    main()
