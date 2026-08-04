#!/usr/bin/env python3
"""X2-B MICRO: review-only reviewer-lens calibration battery (backlog
campaign, 2026-08-02, Task 4 / item 5).

Pre-registered in `logs/2026-08-02-backlog-campaign.md`'s Task 8 entry
(the "X2 (9 reps)" writeup) BEFORE this script's first run. Adapts the
`x1-review-micro.py` / `x1b-review-micro.py` API-call pattern (same
mechanics: raw `urllib.request` calls to the Messages API, `ANTHROPIC_API_KEY`
from the environment only -- never printed, logged, or committed -- answers
cached per (cell, rep) under `out/x2b-review-micro/`) to a REVIEW-ONLY
instrument for X2-B (`sdd/task-reviewer-prompt.md`'s reviewer-lens patch,
`cp/x2b` @ dcdb3fb, content-identical after rebase at `03a28c5`): instead of
seeding a defect ledger and counting recall, this battery gives a reviewer
subagent a COMPLETE finished tree (not a diff) and asks whether it holds an
opinion about the tree's file organization relative to the plan that
produced it.

## Why review-only, and why this design

X2's 9-rep FULL battery (this campaign's Task 8 entry) found X2-B's
reviewer lens fires exactly once, off-axis: a severity downgrade
(Minor/"ready" vs Important elsewhere) on a diff that never changed --
behavior-only grading would have missed it entirely. That result also
carried two structural risks a MICRO here is built to close: (1) X2-A's
patch turned out UNREACHABLE in plan-execution fixtures (writing-plans
fires only at authoring, not during execution), so a null result there
was partly an artifact of the arm's text never being read -- the standing
rule this queue's design doc now states is that every battery must show
HOW the arm's text is reachable from the scenario's execution path; and
(2) with one real firing in 9 reps, severity/verdict-language needs
grading against the CONTROLS' OWN noise floor (controls already disagree
with each other on the same gap), not treated as a clean binary.

**Reachability for X2-B specifically:** the patched text lives in
`sdd/task-reviewer-prompt.md`, the file a controller copies VERBATIM into
a task-reviewer subagent's dispatch prompt (see that file's own docs).
Unlike X2-A's writing-plans hook, this is not a "does the mechanism ever
fire" question -- the reviewer subagent's entire system prompt for this
battery literally IS `task-reviewer-prompt.md`'s filled template, so the
patched paragraphs are read on every x2b-lens call by construction. There
is no reachability gap to pre-register against here.

## Fixture: two committed trees, not a diff

`campaigns/cost-pathologies/micro-fixtures/x2b/{conformant,deviant}/` (see
that directory's own commit message for provenance): `conformant/` is the
real final `src/reports/` tree from a `cp-x2-consequential` CONTROL rep
(`evals/results/cp-x2-consequential-control-rep1/`) -- an actual SDD
session's output, not a hand-built tree -- following the plan's named
four-file split (`parse.js`, `aggregate.js`, `format.js`, `index.js`) and
passing `node --test` cleanly (6/6). `deviant/` is the SAME tree with the
plan's `aggregate.js`/`format.js` merged into a single `summarize.js`
(mechanical, minimal: `parse.js` and `test/report.test.js` stay
byte-identical to `conformant/`; `index.js`'s two imports collapse to one),
also `node --test` clean. This mirrors the reasoning in
`scenarios/cp-x2-consequential/seeded-truth-ledger.md`'s "reasonable
deviation" tree, built independently here from a real session artifact
rather than reused from that scenario's hand-constructed
`fixtures/cp-x2-consequential-outcomes/` pair (a deliberate choice per the
Task 4 brief: ecological validity over reusing the synthetic pair).
`micro-fixtures/x2b/plan.md` is the plan the reviewer is shown, copied
verbatim from the scenario's own fixtures.

## 2x2 design

{conformant, deviant} tree x {plain, x2b-lens} reviewer system prompt = 4
cells, REPS reps each (env `REPS`, default 10; env `MODEL`, default
`claude-opus-4-8`, matching `x1-review-micro.py`'s default). The `plain`
system prompt is `task-reviewer-prompt.md`'s CONTROL text verbatim, from
`1fed99d` (the SHA the campaign design names as the control this arm was
diffed against -- confirmed content-identical to `x1-review-micro.py`'s
own `BASE_TEMPLATE`, extracted independently at an earlier SHA). The
`x2b-lens` prompt is the same template with `cp/x2b`'s two patched spots
applied VERBATIM, extracted via
`git diff 1fed99d cp/x2b -- skills/subagent-driven-development/task-reviewer-prompt.md`:

  1. Part 1 (Spec Compliance), inserted after the Missing/Extra/Misunderstood
     bullets: a new paragraph starting "Judge what the brief required,
     never how it illustrated the work."
  2. Part 2 (Code Quality) Structure checklist: the line "Is the
     implementation following the file structure from the plan?" is
     replaced with "Does the file organization serve this change on its
     own terms? (The plan's file list illustrates the change; it does not
     require it.)"

## Adaptation: "Tree Under Review" replaces "Diff Under Review"

The template's `## Diff Under Review` section (Base/Head SHA, diff-file
framing, "read the diff once" instructions) assumes a diff; this battery
has no base commit -- only a finished tree, because the question under
test is a reviewer's STRUCTURE judgment on completed work, not its
diff-reading behavior. That section is replaced with `## Tree Under
Review`, framing the same complete-tree contents (packed the same way
`x1-review-micro.py` inlines its diff: one fenced block per file, full
contents, no chunking) as "this is a completed task, not a diff." The
template's other five stray mentions of "diff" (in "Do Not Trust the
Report", "You Do Not Dispatch Subagents", the Part 1 intro line, the
Part 1 "cannot be verified" sentence, and the Output Format's "Cannot
verify from diff" bullet) are changed to "tree" for consistency -- these
disclosed substitutions are the only edits to the control template's
prose; everything else, including the x2b-lens patch text, is verbatim.
This is the same kind of disclosed single-purpose adaptation
`x1-review-micro.py`'s B-rising-floor arm used for its "round 3" framing.

## DO NOT RUN

This script makes real, billed API calls when invoked without `--dry-run`.
Per the Task 4 brief, this implementation does not run the battery -- the
controller does. `--dry-run` assembles and writes all 4 cells' system +
user prompts to `/tmp/x2b-review-micro-dry-run/` for inspection and makes
zero API calls.

## Output

One JSONL line per call, appended to `out/x2b-review-micro/results.jsonl`:
`cell` (e.g. `"deviant--x2b-lens"`), `rep` (0-indexed), `raw_review` (full
response text), and the three extracted fields below. Extraction logic
(`extract_review_fields` and its helpers) is TDD'd against 4 handwritten
sample reviews in `test_x2b_review_micro.py` before being trusted here --
same discipline `x1-review-micro.py`/`x1b-review-micro.py` apply to their
own defect-signature regexes, just exercised as a proper pytest suite
(loaded via `importlib`, this script's filename is not a valid Python
module name) instead of a one-off cross-check script, since this
battery's extraction question ("did a Structure finding land on the
plan's file split") is binary and small enough to pin down with a handful
of literal examples rather than a second independent parser.

  - `deviation_flagged` (bool): did any Critical/Important/Minor finding
    match the plan-file-structure deviation signature (see
    `DEVIATION_RE`)?
  - `severity` (`"Critical" | "Important" | "Minor" | "none"`): which
    bucket the (first) matching finding landed in; `"none"` if
    `deviation_flagged` is False.
  - `verdict_language` (str or None): the `**Task quality:** ...` line
    verbatim, if present.

Everything here is synthetic; no real system.
"""
import argparse
import json
import os
import pathlib
import re
import sys
import urllib.request

API = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("MODEL", "claude-opus-4-8")
REPS = int(os.environ.get("REPS", "10"))
ONLY = [v.strip() for v in os.environ.get("ONLY", "").split(",") if v.strip()]

HERE = pathlib.Path(__file__).parent
FIXTURE_DIR = HERE / "micro-fixtures" / "x2b"
OUT = HERE / "out" / "x2b-review-micro"
DRY_RUN_DIR = pathlib.Path("/tmp/x2b-review-micro-dry-run")

PLAN = (FIXTURE_DIR / "plan.md").read_text()

GLOBAL_CONSTRAINTS = (
    "Node.js ESM project; tests run via `npm test` (`node --test`). Public "
    "callers only ever import from `src/reports/index.js`."
)

# ---------------------------------------------------------------------------
# Reviewer-facing template text. Control body verbatim from `1fed99d`
# (`git show 1fed99d:skills/subagent-driven-development/task-reviewer-
# prompt.md`), confirmed content-identical to x1-review-micro.py's own
# BASE_TEMPLATE. The only edits from that source text: {structure_line}
# and {judge_what_brief_insert} placeholders (see PROMPT_VARIANTS below)
# and the disclosed "Diff Under Review" -> "Tree Under Review" adaptation
# documented in this module's docstring (plus 5 stray "diff" -> "tree"
# substitutions for consistency with that adaptation).
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

## Tree Under Review

**Tree contents:** [TREE_FILE]

This is a completed task, not a diff — both of the plan's tasks are
marked done, and what follows is the finished `src/reports/` package plus
its test file in full, and it is your view of the change. Read it once.
Do not crawl the broader codebase. Inspect code outside what's shown only
to evaluate a concrete risk you can name — one focused check per named
risk, and name both the risk and what you checked in your report.
Cross-cutting changes are legitimate named risks: if the tree changes
lock ordering, a function or API contract, or shared mutable state,
checking the call sites is the right method.

Your review is read-only on this checkout. Do not mutate the working
tree, the index, HEAD, or branch state in any way.

## You Do Not Dispatch Subagents

Do all of this review yourself. Never spawn a subagent to review part
of the tree, and never spawn another reviewer for a second opinion.
This process already provides every review seat the work gets; a
reviewer you spawn duplicates one of them at full cost, and its
verdict counts for nothing. If the tree feels too large for one
pass, review it in passes yourself and say so in your report.

## Do Not Trust the Report

Treat the implementer's report as unverified claims about the code. It
may be incomplete, inaccurate, or optimistic. Verify the claims against
the tree. Design rationales in the report are claims too: "left it per
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

Compare the tree against What Was Requested:

- **Missing:** requirements they skipped, missed, or claimed without
  implementing
- **Extra:** features that weren't requested, over-engineering, unneeded
  "nice to haves"
- **Misunderstood:** right feature built the wrong way, wrong problem
  solved
{judge_what_brief_insert}
If a requirement cannot be verified from this tree alone (it lives in
code that wasn't shown or spans tasks), report it as a ⚠️ item instead of
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
{structure_line}
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
If the plan or brief explicitly mandates something this rubric calls a
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
- ⚠️ Cannot verify from tree: [requirements you could not verify from the
  tree alone, and what the controller should check — report alongside the
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

**Reasoning:** [1-2 sentence technical assessment]
"""

# X2-B reviewer lens, cp/x2b @ dcdb3fb (content-identical post-rebase at
# 03a28c5). Both insertions verbatim from `git diff 1fed99d cp/x2b --
# skills/subagent-driven-development/task-reviewer-prompt.md`.

JUDGE_WHAT_BRIEF_INSERT = """
Judge what the brief required, never how it illustrated the work. A file
at another path, a differently named helper, a signature that does not
match a snippet — none of those is a finding while the requirement is
met, and the implementer owes you no permission for them. When a
deviation loses a requirement, the finding is the lost requirement,
quoted to the line that states it.
"""

PLAIN_STRUCTURE_LINE = "- Is the implementation following the file structure from the plan?"
X2B_STRUCTURE_LINE = (
    "- Does the file organization serve this change on its own terms? (The\n"
    "  plan's file list illustrates the change; it does not require it.)"
)


def _fill(template, structure_line, judge_what_brief_insert=""):
    filled = template.format(
        structure_line=structure_line,
        judge_what_brief_insert=judge_what_brief_insert,
    )
    return (
        filled.replace("[BRIEF_FILE]", "the Plan in the user message below")
        .replace("[GLOBAL_CONSTRAINTS]", GLOBAL_CONSTRAINTS)
        .replace("[REPORT_FILE]", "the Implementer's Report in the user message below")
        .replace("[TREE_FILE]", "the Tree Contents in the user message below")
    )


PROMPT_VARIANTS = {
    "plain": _fill(BASE_TEMPLATE, PLAIN_STRUCTURE_LINE),
    "x2b-lens": _fill(BASE_TEMPLATE, X2B_STRUCTURE_LINE, JUDGE_WHAT_BRIEF_INSERT),
}

TREES = ["conformant", "deviant"]
CELLS = [f"{tree}--{prompt}" for tree in TREES for prompt in PROMPT_VARIANTS]


def pack_tree(tree_dir):
    """Inline every source file's full contents, one fenced block each --
    same packing approach x1-review-micro.py uses for its diff (full
    content, no chunking; small enough here that nothing needs it)."""
    files = [tree_dir / "package.json"]
    files += sorted((tree_dir / "src" / "reports").glob("*.js"))
    files.append(tree_dir / "test" / "report.test.js")
    parts = []
    for f in files:
        rel = f.relative_to(tree_dir)
        lang = "json" if f.suffix == ".json" else "javascript"
        parts.append(f"### {rel}\n\n```{lang}\n{f.read_text()}\n```")
    return "\n\n".join(parts)


def build_user_message(tree_name):
    tree_dir = FIXTURE_DIR / tree_name
    report = (tree_dir / "task-report.md").read_text()
    tree_contents = pack_tree(tree_dir)
    return f"""## Plan

{PLAN}

## Implementer's Report

{report}

## Tree Contents

{tree_contents}

Produce your review now, following the Output Format exactly."""


USER_MESSAGE = {tree: build_user_message(tree) for tree in TREES}


def cell_prompt(cell):
    tree, prompt_variant = cell.split("--")
    return PROMPT_VARIANTS[prompt_variant], USER_MESSAGE[tree]


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
# Extraction heuristics. TDD'd against 4 handwritten sample reviews in
# test_x2b_review_micro.py.
# ---------------------------------------------------------------------------

SECTION_RE = re.compile(
    r"#{2,4}\s*(Critical|Important|Minor)\b[^\n]*\n(.*?)"
    r"(?=\n#{2,4}\s*(?:Critical|Important|Minor)\b|\n#{2,3}\s*Assessment|\Z)",
    re.I | re.S,
)

# Matches a Structure finding that flags the tree's file organization
# against the PLAN's named split, in the several ways a reviewer
# following the control (unpatched) template's "Is the implementation
# following the file structure from the plan?" checklist item is likely
# to phrase it. Deliberately scoped to plan-relative structure language
# (not any mention of aggregate.js/format.js/summarize.js by name, which
# also appears in neutral contexts like the Strengths section or an
# unrelated Minor finding -- see test_x2b_review_micro.py's samples C/D).
DEVIATION_RE = re.compile(
    r"diverges?\s+from\s+the\s+plan"
    r"|does(?:\s+not|n't)\s+follow\s+the\s+plan"
    r"|deviat(?:e|es|ed|ion|ing)\s+from\s+the\s+plan"
    r"|(?:four|4)[- ]file\s+split"
    r"|(?:combin|merg)(?:e|es|ed|ing)\s+aggregate\.js\s+and\s+format\.js"
    r"|plan'?s?\s+(?:named\s+)?file\s+structure"
    r"|specified\s+structure"
    # 2026-08-04 expansion, calibrated against the 104-answer corpus
    # (8th undercount instance): the phrasings real reviewers used that
    # the original alternations missed. Still plan-relative by design --
    # every branch carries a deviation/mandate signal, never a bare
    # aggregate.js/format.js mention (those appear in praise contexts in
    # conformant-tree answers).
    r"|file[- ]?(?:structure|layout|split)\s+deviation"
    r"|structur(?:e|al)\s+deviation"
    r"|\[structure\]"
    r"|merged?\s+into\s+(?:a\s+)?(?:single|one)\b"
    r"|deviation\s*\((?:file|structure|layout)"
    r"|plan[- ]mandated\s+file\s+(?:split|layout|structure)"
    r"|(?:file\s+)?(?:split|layout|structure)\s+(?:was\s+|is\s+)?not\s+followed"
    r"|departs?\s+from\s+the\s+plan"
    r"|ignores?\s+the\s+plan'?s"
    r"|instead\s+of\s+the\s+plan'?s"
    r"|plan(?:'s)?\s+(?:explicit\s+)?`?files?:?`?\s+list"
    r"|plan\s+(?:explicitly\s+)?(?:mandates?|names?|named|specifie[sd]|requires?|calls?\s+for)\s+(?:separate|two|the\s+separate)\s+(?:files?|`?aggregate)"
    r"|(?:file\s+)?consolidat(?:e|es|ed|ion|ing)\s+(?:of\s+|into\s+)?(?:`?aggregate|`?summarize|one\s+file|a\s+single)"
    r"|(?:ships?|shipped|has|contains?|uses?)\s+a\s+(?:single|combined)\s+`?summarize\.js"
    r"|merge[sd]?\s+(?:of\s+)?`?aggregate(?:\.js)?`?\s+and\s+`?format",
    re.I,
)

TASK_QUALITY_LINE_RE = re.compile(r"^.*\*\*Task quality:\*\*.*$", re.M | re.I)


def extract_sections(answer_text):
    out = {}
    for m in SECTION_RE.finditer(answer_text):
        key = m.group(1).capitalize()
        body = m.group(2).strip()
        out[key] = (out[key] + "\n\n" + body) if key in out else body
    return out


def split_findings(block_text):
    if not block_text or re.match(r"^[\(\*]*\s*none\b", block_text.strip(), re.I):
        return []
    bullets = re.findall(r"(?:^|\n)[-*]\s+(.+?)(?=\n[-*]\s+|\Z)", block_text, re.S)
    if bullets:
        return [b.strip() for b in bullets]
    numbered = re.findall(r"(?:^|\n)\d+[.)]\s+(.+?)(?=\n\d+[.)]\s+|\Z)", block_text, re.S)
    if numbered:
        return [b.strip() for b in numbered]
    paras = [p.strip() for p in re.split(r"\n\s*\n", block_text) if p.strip()]
    return paras if paras else [block_text.strip()]


def extract_verdict_language(answer_text):
    m = TASK_QUALITY_LINE_RE.search(answer_text)
    return m.group(0).strip() if m else None


SEVERITY_ORDER = ["Critical", "Important", "Minor"]


def extract_review_fields(answer_text):
    sections = extract_sections(answer_text)
    severity = "none"
    flagged = False
    for sev in SEVERITY_ORDER:
        findings = split_findings(sections.get(sev, ""))
        if any(DEVIATION_RE.search(f) for f in findings):
            severity = sev
            flagged = True
            break
    return {
        "deviation_flagged": flagged,
        "severity": severity,
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
        help="Assemble and write all 4 cells' prompts to /tmp for inspection; make no API calls.")
    args = parser.parse_args()

    if args.dry_run:
        dry_run()
        return

    (OUT / "answers").mkdir(parents=True, exist_ok=True)
    (OUT / "usage").mkdir(parents=True, exist_ok=True)
    cells = [c for c in CELLS if not ONLY or c in ONLY]
    print(f"# X2-B review-only MICRO (MODEL={MODEL}, REPS={REPS})")

    jsonl_path = OUT / "results.jsonl"
    total_input_tokens = 0
    total_output_tokens = 0
    counts = {}
    with jsonl_path.open("w") as jsonl_f:
        for cell in cells:
            n_flagged = 0
            for rep in range(REPS):
                raw_review, usage = run_sample(cell, rep)
                fields = extract_review_fields(raw_review)
                if fields["deviation_flagged"]:
                    n_flagged += 1
                total_input_tokens += usage.get("input_tokens", 0) + usage.get(
                    "cache_creation_input_tokens", 0)
                total_output_tokens += usage.get("output_tokens", 0)
                jsonl_f.write(json.dumps({
                    "cell": cell,
                    "rep": rep,
                    "raw_review": raw_review,
                    **fields,
                }) + "\n")
            counts[cell] = n_flagged

    print()
    header = f"{'cell':<24}{'deviation-flagged':>20}{'n':>6}"
    print(header)
    print("-" * len(header))
    for cell in cells:
        print(f"{cell:<24}{counts[cell]:>19}/{REPS:<3}")
    print()
    print(f"wrote {jsonl_path}", file=sys.stderr)
    print(f"usage: {total_input_tokens} input tokens (incl. cache-creation), "
          f"{total_output_tokens} output tokens", file=sys.stderr)


if __name__ == "__main__":
    main()
