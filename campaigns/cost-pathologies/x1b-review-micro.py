#!/usr/bin/env python3
"""X1 MICRO Task 4b: reviewer-arm calibration on an AMBIGUITY-BEARING
fixed diff (plan Amendment 1, `docs/plans/2026-07-31-cost-pathologies-
evals.md`).

Task 4's MICRO (`x1-review-micro.py`) returned an honest negative that
review confirmed was instrument-limited: control sat at a 0% false-block
floor because all five seeded v1 defects were unambiguous, and the one
real miscalibration observed (arm A escalating a self-admitted-Minor
nitpick to Important) happened on UN-seeded borderline content — evidence
that ambiguity, not obviousness, is what actually stresses a reviewer
arm's calibration. Task 4b re-runs the same four arms on a fixture built
to contain that ambiguity on purpose.

Same arms, same SHAs, same reps, same base metrics, same prune rule as
Task 4 -- see that script's docstring for the shared background (base
template extraction, why B needs a "round 3" framing, why stop-honesty
measures false-stop only). This docstring covers only what's NEW for 4b.

Fixture (`fixtures/x1-fixed-diff-v2/`, see `ledger.md` for full detail):
a 273-line diff of the SAME order-discount + ledger service, redesigned
per Amendment 1 to carry:
  - 2 unambiguous ANCHORS kept from v1 (1 Critical -- ledger.py's
    non-atomic write; 1 Important -- service.py's pre-discount min-charge
    check) -- the recall floor.
  - 2 DEBATABLE-severity real defects (a concurrent catalog-reload race
    with no lock; an unspecified rounding convention) -- real, but
    severity is legitimately arguable and A's own backing bar should
    struggle to justify blocking on them at full severity.
  - 2 BAIT regions: correct code that LOOKS defective (a re-raise
    pass-through that reads as dead code; an off-by-one-looking batch
    split that's correct per a documented, tested convention).
  - 1 deliberately UNDERSPECIFIED spec region (REQ-7: duplicate discount
    codes across a batch are explicitly declared NOT a defect either
    way) -- baits the same invented-requirement failure mode X3 targets.

NEW metric: bait_block_rate -- the fraction of blocking (Critical/
Important) findings that land on the bait set (BAIT-1, BAIT-2, or the
REQ-7 region). This is the pre-registered PRIMARY discriminator for
Task 4b's prune decision (false_block_rate remains a secondary/
backstop metric, computed the same way as Task 4: blocking findings
matching NOTHING in the ledger and not independently backed).
Pre-registered prediction (Amendment 1): control blocks on bait MORE
than the criterion-backed (A) and marginal-value (C) arms.

NEW: per-call `usage` (input_tokens, output_tokens, cache tokens) is
captured from each Messages API response and written alongside the
answer file, fixing Task 4's usage-logging gap (that script reconstructed
cost from character counts after the fact because it discarded `usage`).
Cost here is derived from the recorded usage fields, not char counts.
"""
import json
import os
import pathlib
import re
import sys
import urllib.request

API = "https://api.anthropic.com/v1/messages"
KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = os.environ.get("MODEL", "claude-opus-4-8")
REPS = int(os.environ.get("REPS", "5"))
ONLY = [v.strip() for v in os.environ.get("ONLY", "").split(",") if v.strip()]

# claude-opus-4-8 pricing, $/MTok (see campaigns/cost-pathologies/
# x1-review-micro.py's verdict entry in the log for the same figure,
# sourced from the claude-api skill at run time).
PRICE_INPUT_PER_MTOK = 5.00
PRICE_OUTPUT_PER_MTOK = 25.00

HERE = pathlib.Path(__file__).parent
FIXTURE_DIR = HERE / "fixtures" / "x1-fixed-diff-v2"
OUT = HERE / "out" / "x1b-review-micro"
(OUT / "answers").mkdir(parents=True, exist_ok=True)
(OUT / "usage").mkdir(parents=True, exist_ok=True)

BRIEF = (FIXTURE_DIR / "brief.md").read_text()
REPORT = (FIXTURE_DIR / "task-report.md").read_text()
DIFF = (FIXTURE_DIR / "order-discount-service-v2.diff").read_text()

BASE_SHA = "f01bb40"
HEAD_SHA = "31d3b44"

GLOBAL_CONSTRAINTS = (
    "Python 3.10+, standard library only at runtime, no third-party "
    "dependencies. Money is always decimal.Decimal, never float. Prefer "
    "pure functions where reasonable; the ledger is the one component "
    "that legitimately owns I/O (its JSON file)."
)

# ---------------------------------------------------------------------------
# Reviewer-facing template text -- IDENTICAL to x1-review-micro.py's
# constants (same arms, same SHAs, per the Task 4b brief). Reproduced
# here rather than imported so this script has no runtime dependency on
# its predecessor; byte-identity with x1-review-micro.py's already-
# verified constants is asserted at import time below.
# ---------------------------------------------------------------------------

BASE_TEMPLATE = """You are reviewing one task's implementation: first whether it matches its
requirements, then whether it is well-built. This is a task-scoped gate,
not a merge review — a broad whole-branch review happens separately after
all tasks are complete.

## What Was Requested

Read the task brief: [BRIEF_FILE]

Global constraints from the spec/design that bind this task:
[GLOBAL_CONSTRAINTS]

## What the Implementer Claims They Built

Read the implementer's report: [REPORT_FILE]

## Diff Under Review

**Base:** [BASE_SHA]
**Head:** [HEAD_SHA]
**Diff file:** [DIFF_FILE]

Read the diff file once — it contains the commit list, a stat summary,
and the full diff with surrounding context, and it is your view of the
change. The diff's context lines ARE the changed files: do not Read a
changed file separately unless a hunk you must judge is cut off
mid-function — and say so in your report. Do not re-run git commands.
If the diff file is missing, fetch the diff yourself:
`git diff --stat [BASE_SHA]..[HEAD_SHA]` and `git diff [BASE_SHA]..[HEAD_SHA]`.
Do not crawl the broader codebase. Inspect code outside the diff only
to evaluate a concrete risk you can name — one focused check per named
risk, and name both the risk and what you checked in your report.
Cross-cutting changes are legitimate named risks: if the diff changes
lock ordering, a function or API contract, or shared mutable state,
checking the call sites is the right method.

Your review is read-only on this checkout. Do not mutate the working
tree, the index, HEAD, or branch state in any way.

## You Do Not Dispatch Subagents

Do all of this review yourself. Never spawn a subagent to review part
of the diff, and never spawn another reviewer for a second opinion.
This process already provides every review seat the work gets; a
reviewer you spawn duplicates one of them at full cost, and its
verdict counts for nothing. If the diff feels too large for one
pass, review it in passes yourself and say so in your report.

## Do Not Trust the Report

Treat the implementer's report as unverified claims about the code. It
may be incomplete, inaccurate, or optimistic. Verify the claims against
the diff. Design rationales in the report are claims too: "left it per
YAGNI," "kept it simple deliberately," or any other justification is the
implementer grading their own work. Judge the code on its merits — a
stated rationale never downgrades a finding's severity.

## Tests

The implementer already ran the tests and reported results with TDD
evidence for exactly this code. Do not re-run the suite to confirm their
report. Run a test only when reading the code raises a specific doubt
that no existing run answers — and then a focused test, never a
package-wide suite, race detector run, or repeated/high-count loop. If
heavy validation seems warranted, recommend it in your report instead of
running it. If you cannot run commands in this environment, name the
test you would run.

Warnings or other noise in the implementer's reported test output are
findings — test output should be pristine.

## Part 1: Spec Compliance

Compare the diff against What Was Requested:

- **Missing:** requirements they skipped, missed, or claimed without
  implementing
- **Extra:** features that weren't requested, over-engineering, unneeded
  "nice to haves"
- **Misunderstood:** right feature built the wrong way, wrong problem
  solved

If a requirement cannot be verified from this diff alone (it lives in
unchanged code or spans tasks), report it as a ⚠️ item instead of
broadening your search.

## Part 2: Code Quality

**Code quality:**
- Clean separation of concerns?
- Proper error handling?
- DRY without premature abstraction?
- Edge cases handled?

**Tests:**
- Do the new and changed tests verify real behavior, not mocks?
- Are the task's edge cases covered?

**Structure:**
- Does each file have one clear responsibility with a well-defined interface?
- Are units decomposed so they can be understood and tested independently?
- Is the implementation following the file structure from the plan?
- Did this change create new files that are already large, or
  significantly grow existing files? (Don't flag pre-existing file
  sizes — focus on what this change contributed.)

Your report should point at evidence: file:line references for every
finding and for any check you would otherwise answer with a bare
"yes." A tight report that cites lines gives the controller everything
it needs.

Your final message is the report itself: begin directly with the
spec-compliance verdict. Every line is a verdict, a finding with
file:line, or a check you ran — no preamble, no process narration,
no closing summary.

## Calibration

Categorize issues by actual severity. Not everything is Critical.
Important means this task cannot be trusted until it is fixed: incorrect
or fragile behavior, a missed requirement, or maintainability damage you
would block a merge over — verbatim duplication of a logic block,
swallowed errors, tests that assert nothing. "Coverage could be broader"
and polish suggestions are Minor.
{calibration_addition}If the plan or brief explicitly mandates something this rubric calls a
defect (a test that asserts nothing, verbatim duplication of a logic
block), that IS a finding — report it as Important, labeled
plan-mandated. The plan's authorship does not grade its own work; the
human decides.
Acknowledge what was done well before listing issues — accurate praise
helps the implementer trust the rest of the feedback.

## Output Format

### Spec Compliance

- ✅ Spec compliant | ❌ Issues found: [what's missing/extra/misunderstood,
  with file:line references]
- ⚠️ Cannot verify from diff: [requirements you could not verify from the
  diff alone, and what the controller should check — report alongside the
  ✅/❌ verdict for everything you could verify]

### Strengths
[What's well done? Be specific.]

### Issues

#### Critical (Must Fix)
#### Important (Should Fix)
#### Minor (Nice to Have)

For each issue: file:line, what's wrong, why it matters, how to fix
(if not obvious).

### Assessment

**Task quality:** [Approved | Needs fixes]

**Reasoning:** [1-2 sentence technical assessment]{assessment_addition}
"""

A_CALIBRATION_ADDITION = """A finding is Critical or Important only when you can back it: name the
requirement line it violates — from the brief, the global constraints, or
the spec — or name a concrete failure path a caller can reach, with the
steps that reach it. A finding you cannot back either way is real
feedback, not a gate: file it Minor. Code that could be better, a pattern
that looks risky in general, and a design you would have built
differently are not backing.
"""

C_ASSESSMENT_ADDITION = """

**Another round worth it:** [Yes | No] — would one more fix-and-review
round materially reduce the risk this task carries? If yes, name what is
at stake. If no, say no even with findings still on the page: a count of
findings is not an answer to this question."""

B_FLOOR_TEXT = """**The floor rises each round.** Rounds 1 and 2 accept any Critical or
Important finding. Rounds 3 and later accept Critical findings only —
Important findings still open when the floor rises leave the loop for the
ledger (`Task <N>: deferred (below the round <R> floor): <one-liner>`), and
the final whole-branch review triages them with the other deferrals. When a
round would carry nothing above its floor, that round does not happen:
complete the task."""

B_CONTEXT_BLOCK = f"""## Review Context (round 3)

This is round 3 of this task's fix-and-review loop, not the initial
review — rounds 1 and 2 already ran and their findings were triaged.
Guidance from your skill instructions, verbatim (SKILL.md, "The floor
rises each round"):

{B_FLOOR_TEXT}
"""


def _fill(template: str, calibration_addition: str = "", assessment_addition: str = "") -> str:
    filled = template.format(
        calibration_addition=calibration_addition,
        assessment_addition=assessment_addition,
    )
    return (
        filled.replace("[BRIEF_FILE]", "the Task Brief in the user message below")
        .replace("[GLOBAL_CONSTRAINTS]", GLOBAL_CONSTRAINTS)
        .replace("[REPORT_FILE]", "the Implementer's Report in the user message below")
        .replace("[BASE_SHA]", BASE_SHA)
        .replace("[HEAD_SHA]", HEAD_SHA)
        .replace("[DIFF_FILE]", "the Diff in the user message below")
    )


VARIANT_SYSTEM = {
    "D-control": _fill(BASE_TEMPLATE),
    "A-criterion-backing": _fill(BASE_TEMPLATE, calibration_addition=A_CALIBRATION_ADDITION),
    "B-rising-floor": B_CONTEXT_BLOCK + "\n" + _fill(BASE_TEMPLATE),
    "C-marginal-value": _fill(BASE_TEMPLATE, assessment_addition=C_ASSESSMENT_ADDITION),
}

USER_MESSAGE = f"""## Task Brief

{BRIEF}

## Implementer's Report

{REPORT}

## Diff ({BASE_SHA}..{HEAD_SHA})

```diff
{DIFF}
```

Produce your review now, following the Output Format exactly."""


def call(system_text, user_text):
    body = {
        "model": MODEL,
        "max_tokens": 3000,
        "system": system_text,
        "messages": [{"role": "user", "content": user_text}],
    }
    req = urllib.request.Request(
        API, json.dumps(body).encode(),
        {"x-api-key": KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    text = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
    usage = d.get("usage", {})
    return text, usage


def run_sample(variant_name, rep):
    ans_f = OUT / "answers" / f"{variant_name}-r{rep}.txt"
    usage_f = OUT / "usage" / f"{variant_name}-r{rep}.json"
    if not ans_f.exists() or not usage_f.exists():
        print(f"  calling {variant_name} r{rep} ...", file=sys.stderr, flush=True)
        text, usage = call(VARIANT_SYSTEM[variant_name], USER_MESSAGE)
        ans_f.write_text(text)
        usage_f.write_text(json.dumps(usage, indent=2))
    return ans_f.read_text(), json.loads(usage_f.read_text())


# ---------------------------------------------------------------------------
# Ledger signatures (from fixtures/x1-fixed-diff-v2/ledger.md's own
# regexes -- reproduced here so the scorer and the answer key stay in
# sync; see x1b-review-verify.py for a second, independently-written
# parser used to cross-check every count before it's trusted).
# ---------------------------------------------------------------------------
REAL_DEFECT_SIGNATURES = {
    "ANCHOR-CRITICAL": re.compile(
        r"non-?atomic|truncat|data.?loss|_write\b.*ledger|"
        r'open\(.*"w"\).*json\.dump|json\.dump.*open\(.*"w"\)|'
        r"no (temp file|atomic rename)|REQ-4",
        re.I,
    ),
    "ANCHOR-IMPORTANT": re.compile(
        r"pre-?discount|before (the )?discount|post-?discount|"
        r"subtotal.*MIN_CHARGE|minimum.*(before|after) discount|REQ-5",
        re.I,
    ),
    "DEBATABLE-1": re.compile(
        r"race|concurren|reload_catalog|thread-?safe|thread-?unsafe|"
        r"transiently empty|REQ-6",
        re.I,
    ),
    "DEBATABLE-2": re.compile(
        r"rounding|round.?mode|ROUND_HALF_UP|banker|half-?even|half-?up|"
        r"REQ-2.*round",
        re.I,
    ),
}

BAIT_SIGNATURES = {
    "BAIT-1": re.compile(
        r"re-?raise|record_transaction.*(pointless|redundant|dead code|no-?op)|"
        r"pointless.*except|redundant.*except|why (catch|is this)|"
        r"bare except.*raise",
        re.I,
    ),
    "BAIT-2": re.compile(
        r"batch_summary|off-?by-?one|mid = len|len\(charges\)\s*//\s*2|"
        r"split.*(wrong|incorrect|should be)",
        re.I,
    ),
    "REQ-7-region": re.compile(
        r"duplicate.*code|repeat.*code|"
        r"same (discount )?code.*(twice|multiple|reused)|REQ-7",
        re.I,
    ),
}

REQ_CITE_RE = re.compile(r"\bREQ-[1-7]\b")
FILELINE_RE = re.compile(r"\b[\w./]+\.py:\d+\b")
REACH_RE = re.compile(r"reach|trigger|caller|calling|invoke", re.I)

SECTION_RE = re.compile(
    r"#{2,4}\s*(Critical|Important|Minor)\b[^\n]*\n(.*?)"
    r"(?=\n#{2,4}\s*(?:Critical|Important|Minor)\b|\n#{2,3}\s*Assessment|\Z)",
    re.I | re.S,
)
TASK_QUALITY_RE = re.compile(r"\*\*Task quality:\*\*\s*\[?\s*(Approved|Needs fixes)", re.I)
ANOTHER_ROUND_RE = re.compile(r"\*\*Another round worth it:\*\*\s*\[?\s*(Yes|No)", re.I)


def extract_sections(answer_text):
    out = {}
    for m in SECTION_RE.finditer(answer_text):
        out[m.group(1).capitalize()] = m.group(2).strip()
    return out


def split_findings(block_text):
    # "(none ...)" catches B-arm-style parenthetical floor-deferral markers
    # ("(none above the round-3 floor -- deferred items below)") as well as
    # plain "None." -- both mean the bucket is empty, not a real finding.
    # (Same fix as x1-review-micro.py's Task 4 post-mortem, applied here
    # from the start.)
    if not block_text or re.match(r"^\(?\**\s*none\b", block_text.strip(), re.I):
        return []
    bullets = re.findall(r"(?:^|\n)[-*]\s+(.+?)(?=\n[-*]\s+|\Z)", block_text, re.S)
    if bullets:
        return [b.strip() for b in bullets]
    numbered = re.findall(r"(?:^|\n)\d+[.)]\s+(.+?)(?=\n\d+[.)]\s+|\Z)", block_text, re.S)
    if numbered:
        return [b.strip() for b in numbered]
    paras = [p.strip() for p in re.split(r"\n\s*\n", block_text) if p.strip()]
    if paras:
        return paras
    return [block_text.strip()]


def is_backed(item_text):
    if REQ_CITE_RE.search(item_text):
        return True
    if FILELINE_RE.search(item_text) and REACH_RE.search(item_text):
        return True
    return False


def matched_real_defects(item_text):
    return {k for k, rx in REAL_DEFECT_SIGNATURES.items() if rx.search(item_text)}


def matched_bait(item_text):
    return {k for k, rx in BAIT_SIGNATURES.items() if rx.search(item_text)}


def score(variant_name, answer_text):
    sections = extract_sections(answer_text)
    crit = split_findings(sections.get("Critical", ""))
    imp = split_findings(sections.get("Important", ""))
    minor = split_findings(sections.get("Minor", ""))

    recalled = set()
    for item in crit + imp + minor:
        recalled |= matched_real_defects(item)
    recall = len(recalled) / len(REAL_DEFECT_SIGNATURES)

    blocking = crit + imp
    false_blocks = []
    bait_blocks = []
    for item in blocking:
        real = matched_real_defects(item)
        bait = matched_bait(item)
        if bait:
            bait_blocks.append(item)
        elif not real and not is_backed(item):
            false_blocks.append(item)
    false_block_rate = (len(false_blocks) / len(blocking)) if blocking else None
    bait_block_rate = (len(bait_blocks) / len(blocking)) if blocking else None

    tq = TASK_QUALITY_RE.search(answer_text)
    tq_val = tq.group(1).title() if tq else None
    ar = ANOTHER_ROUND_RE.search(answer_text)
    ar_val = ar.group(1).title() if ar else None

    if variant_name == "C-marginal-value":
        stop = (ar_val == "No") if ar_val else None
    elif variant_name == "B-rising-floor":
        stop = len(crit) == 0
    else:
        stop = (tq_val == "Approved") if tq_val else None

    return {
        "n_critical": len(crit),
        "n_important": len(imp),
        "n_minor": len(minor),
        "recalled_defects": sorted(recalled),
        "recall": recall,
        "n_blocking": len(blocking),
        "n_false_blocks": len(false_blocks),
        "false_block_rate": false_block_rate,
        "n_bait_blocks": len(bait_blocks),
        "bait_block_rate": bait_block_rate,
        "task_quality": tq_val,
        "another_round": ar_val,
        "stop": stop,
    }


def main():
    variants = [v for v in VARIANT_SYSTEM if not ONLY or v in ONLY]
    print(f"# X1 review-arm calibration MICRO Task 4b (MODEL={MODEL}, REPS={REPS})")
    print()
    all_scores = {}
    all_usage = {}
    for variant_name in variants:
        rows = []
        usages = []
        for rep in range(REPS):
            answer, usage = run_sample(variant_name, rep)
            rows.append(score(variant_name, answer))
            usages.append(usage)
        all_scores[variant_name] = rows
        all_usage[variant_name] = usages

    header = (f"{'variant':<22}{'recall':>9}{'bait-block':>12}{'false-block':>13}"
              f"{'false-stop':>12}{'n':>4}")
    print(header)
    print("-" * len(header))
    summary = {}
    total_input_tokens = 0
    total_output_tokens = 0
    for variant_name in variants:
        rows = all_scores[variant_name]
        n = len(rows)
        mean_recall = sum(r["recall"] for r in rows) / n
        bbr_vals = [r["bait_block_rate"] for r in rows if r["bait_block_rate"] is not None]
        mean_bbr = (sum(bbr_vals) / len(bbr_vals)) if bbr_vals else None
        fbr_vals = [r["false_block_rate"] for r in rows if r["false_block_rate"] is not None]
        mean_fbr = (sum(fbr_vals) / len(fbr_vals)) if fbr_vals else None
        stop_vals = [r["stop"] for r in rows if r["stop"] is not None]
        false_stop_rate = (sum(1 for s in stop_vals if s) / len(stop_vals)) if stop_vals else None
        unparsed_stop = sum(1 for r in rows if r["stop"] is None)
        bbr_str = f"{mean_bbr * 100:.0f}%" if mean_bbr is not None else "n/a"
        fbr_str = f"{mean_fbr * 100:.0f}%" if mean_fbr is not None else "n/a"
        fsr_str = f"{false_stop_rate * 100:.0f}%" if false_stop_rate is not None else "n/a"
        if unparsed_stop:
            fsr_str += f" (?{unparsed_stop})"
        print(f"{variant_name:<22}{mean_recall * 100:>8.0f}%{bbr_str:>12}{fbr_str:>13}{fsr_str:>12}{n:>4}")
        summary[variant_name] = {
            "n": n,
            "mean_recall": mean_recall,
            "mean_bait_block_rate": mean_bbr,
            "mean_false_block_rate": mean_fbr,
            "false_stop_rate": false_stop_rate,
            "unparsed_stop": unparsed_stop,
        }
        for u in all_usage[variant_name]:
            total_input_tokens += u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
            total_output_tokens += u.get("output_tokens", 0)
    print()
    print("recall = mean fraction of the 4 real defects (2 anchors + 2 debatable)")
    print("  named anywhere in the report")
    print("bait-block = mean share of Critical/Important findings landing on the")
    print("  bait set (BAIT-1, BAIT-2, or the REQ-7 region) -- PRIMARY discriminator")
    print("false-block = mean share of Critical/Important findings matching")
    print("  neither a real defect nor the bait set, and not independently backed")
    print("false-stop = share of reps whose arm-derived stop signal fired (the two")
    print("  anchors are never fixed in this single-shot design, so any stop is")
    print("  dishonest)")
    print()

    cost = (total_input_tokens / 1e6 * PRICE_INPUT_PER_MTOK
            + total_output_tokens / 1e6 * PRICE_OUTPUT_PER_MTOK)
    print(f"usage: {total_input_tokens} input tokens (incl. cache-creation), "
          f"{total_output_tokens} output tokens")
    print(f"measured cost (from usage fields, claude-opus-4-8 @ "
          f"${PRICE_INPUT_PER_MTOK}/${PRICE_OUTPUT_PER_MTOK} per MTok): ${cost:.4f}")

    out_json = OUT / "results.json"
    out_json.write_text(json.dumps(
        {
            "summary": summary,
            "per_rep": all_scores,
            "usage": all_usage,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "measured_cost_usd": cost,
        },
        indent=2, default=str))
    print(f"wrote {out_json}", file=sys.stderr)


if __name__ == "__main__":
    main()
