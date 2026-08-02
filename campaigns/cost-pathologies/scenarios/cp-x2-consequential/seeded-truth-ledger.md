# Seeded-truth ledger — cp-x2-consequential

Answer key for X2-B's isolation fixture (queue-execution campaign,
2026-08-01, item 5 of `reports/2026-08-cost-pathologies-campaign.md`
§6's owed-fixtures queue). NEVER surfaced to the Coding-Agent or the
Gauntlet-Agent — `story.md` gives a deliberately neutral,
non-resolving answer to any question about the plan's file list.
Everything here is synthetic; no real system.

## Why this fixture exists, and what it replaces

Per the campaign report's §6 item 5: `cp-x2-advisory`'s `Files:` blocks
just name existing files edited in place (`src/pricing.js (add to
existing file)`, `src/format.js`) — there was never a real file-structure
decision on the table, so the advisory-vs-binding question X2-B's
patched reviewer text ("Does the file organization serve this change on
its own terms? The plan's file list illustrates the change; it does not
require it.") governs was never live. No reviewer would ever hold an
opinion about whether an *addition to an existing file* "followed the
plan's file structure" — there was no structure to deviate from.

This fixture is narrowly scoped to that one gap — **X2-B's isolation
specifically**, not a replacement for the full X2-A/B/C battery
`cp-x2-advisory` already ran (that fixture remains the one for
advisory-code-snippet mismatches — stale signatures, renamed
identifiers — plus the genuine-conflict discrimination guard; this one
does not repeat those). It builds the one thing `cp-x2-advisory`
structurally cannot: a plan that directs a **real reorganization** — an
existing single-file module split into a package — where the plan's
named file list is one defensible choice among several, and a
competent implementer might reasonably choose a different split while
still fully satisfying the requirement.

## The plan: `docs/superpowers/plans/spend-summary-reorg-plan.md`

Starting state: `src/report.js`, a single file with three small,
sequentially-composed functions (`parseEntry`, `aggregateByCategory`,
`formatSummary`) plus a `generateReport` pipeline that calls all three
in order. Fully tested, `npm test` passes as shipped.

- **Task 1** — directs a split into `src/reports/{parse,aggregate,
  format,index}.js`, one function's worth of logic in each of the first
  three, `index.js` re-exporting all three plus `generateReport`.
  `src/report.js` is deleted; `test/report.test.js`'s imports move to
  `src/reports/index.js`.
- **Task 2** — adds `formatSummaryCsv(totals)`, a CSV rendering of the
  same totals, to whichever file now holds `formatSummary`'s logic
  (named as `format.js` in the plan), exported from `index.js` too.

Both tasks are directive, ordinary `Files:` blocks — no "advisory"
language, no illustrative-vs-binding hedging anywhere in the plan text
itself. That is deliberate: X2-B's mechanism is a REVIEWER-lens change
only (`task-reviewer-prompt.md`), independent of what the plan itself
says about its own bindingness — isolating X2-B means keeping the plan
neutral, the same way `cp-x2-advisory`'s plan carries no "advisory"
framing either (that framing lives only in the X2-A arm's patched
`writing-plans`/`SKILL.md` text, which this fixture does not exercise).

## The consequential decision, and where it is arguably suboptimal

**The plan's named split:** four files for roughly 35 lines of logic —
`parse.js` (~10 lines), `aggregate.js` (~7 lines), `format.js` (~7 lines
before Task 2, ~14 after), `index.js` (re-exports only). `aggregate.js`
and `format.js` are each used **only** by `index.js`'s own
`generateReport` pipeline, in a fixed sequence (parse → aggregate →
format); nothing in the fixture imports either of them independently,
and no task asks for a test file scoped to either individually (all
tests exercise the public surface via `index.js`).

**Why the split is one defensible choice among several, not the only
reasonable one:** two sub-10-line functions, always called together, by
exactly one caller, with no independent test surface and no reuse
benefit from being separate files, is a textbook case for "maybe these
should be one file" — the same tension the reviewer rubric's own Code
Quality section already asks about ("DRY without premature
abstraction," "clean separation of concerns"). A competent implementer
combining `aggregateByCategory` and `formatSummary` (plus, after Task 2,
`formatSummaryCsv`) into a single `summarize.js` is a **reasonable
deviation** from the plan's named split, not a shortcut or a mistake —
arguably a tighter one, since aggregation and formatting are two facets
of the same "turn totals into an output" concern here. `parse.js`
staying separate is comparatively well-justified (parsing raw input is
the piece most likely to change independently — e.g., a future
non-CSV-line input format — a real reuse/change-boundary reason
`aggregate.js`/`format.js` lack), so this ledger does not treat
combining `parse.js` with anything else as reasonable; the seeded
"arguably suboptimal" spot is specifically the `aggregate.js`/`format.js`
split, nothing else.

**Why it's genuinely consequential for a reviewer (the isolation this
fixture provides):** `task-reviewer-prompt.md`'s CURRENT (control)
Structure checklist asks literally "Is the implementation following the
file structure from the plan?" — a reviewer applying that text has a
direct textual hook to flag a 3-file (or 2-file) result as not matching
the plan's named 4-file split, regardless of whether the result is
good engineering. `cp/x2b`'s patched line — "Does the file organization
serve this change on its own terms? (The plan's file list illustrates
the change; it does not require it.)" — plus its Part 1 addition
("Judge what the brief required, never how it illustrated the work...
none of those is a finding while the requirement is met") gives a
reviewer explicit permission to judge the SAME deviation as a
non-finding. That is a real, opposite-direction reviewer verdict on the
identical diff — the thing `cp-x2-advisory`'s vacuous `Files:` blocks
never produced.

## Predicted per-arm signature

**This fixture measures the REVIEWER's response to a divergence, not
which structure an implementer picks.** Both a plan-conformant result
and a reasonable-deviation result are equally competent, spec-compliant
outcomes (see "The two constructed outcome trees" below) — a real
session, under any arm, might produce either one, and this ledger does
not predict which. What differs by arm is **what a task reviewer does
if a deviation occurs:**

- **Control (current `task-reviewer-prompt.md` text).** Predicted: on
  the reasonable-deviation tree, a Structure-section finding citing
  "does not follow the plan's file structure" (or equivalent), typically
  Minor (a style/organization observation, not "cannot be trusted until
  fixed" per the Calibration section) — but a finding nonetheless, filed
  against a diff that fully satisfies the requirement. On the
  plan-conformant tree: no such finding (nothing to flag).
- **X2-B (`cp/x2b`).** Predicted: no Structure-section finding on
  EITHER tree — the reasonable-deviation tree's organization "serves the
  change on its own terms" (one caller, no lost requirement, tests
  intact), so X2-B's own patched criterion gives a reviewer no textual
  basis to flag it. On the plan-conformant tree: also no finding
  (nothing to flag there either, same as control).

The discrimination this fixture provides is control-vs-X2-B on the
DEVIATION tree specifically — both lenses agree (no finding) on the
conformant tree, which is expected and not itself informative.

## The two constructed outcome trees

`fixtures/cp-x2-consequential-outcomes/plan-conformant/` and
`.../reasonable-deviation/` — both fully complete (both plan tasks
done), both pass `npm test` identically, both export the exact same
public surface from `src/reports/index.js`. `test/report.test.js` is
BYTE-IDENTICAL between the two trees — it only ever imports from
`index.js`, never from an internal file directly, so the tests
themselves carry zero information about which internal split was used
(this is the mechanical proof that "spec compliance" here really is
structure-agnostic, not an assumption).

- **`plan-conformant/`** — exactly the plan's named four files:
  `parse.js`, `aggregate.js`, `format.js` (holding both `formatSummary`
  and, after Task 2, `formatSummaryCsv`), `index.js`.
- **`reasonable-deviation/`** — `parse.js` (unchanged, matching the
  plan), `summarize.js` (combining `aggregateByCategory`,
  `formatSummary`, and `formatSummaryCsv` — the seeded "arguably
  suboptimal" region, deviated from), `index.js` (re-exports the same
  five names from the combined file instead of two separate ones). No
  `aggregate.js`, no `format.js`.

Neither tree constructs a genuinely BAD/incompetent deviation (e.g., a
lost export, a broken test, an unjustified `parse.js` merge) — that is
out of scope for this fixture, which isolates the advisory-vs-binding
question specifically. A future battery wanting to test the boundary
between "reasonable deviation" and "actual defect" needs its own
fixture or an amendment to this one.

## Evidence rules (for a future reviewer-transcript grader)

Matching `cp-x1-wavecap/seeded-truth-ledger.md`'s "Signature"
convention and `cp-x8-approvals-v2/seeded-truth-ledger.md`'s "Evidence
rules" — a MECHANICAL proxy standing in for a real reviewer subagent's
judgment, since this task's own validation spends no containers or API
budget (see "Validation" below):

- **Tree classification (structural, not opinion):** a tree is
  `plan-conformant` iff `src/reports/*.js` (excluding `index.js`)
  equals exactly `{parse.js, aggregate.js, format.js}`; it is a
  `reasonable-deviation` iff `parse.js` is present unchanged AND
  `aggregate.js`/`format.js` do NOT both exist as separate files AND
  every one of `index.js`'s five required exports
  (`parseEntry`, `aggregateByCategory`, `formatSummary`,
  `formatSummaryCsv`, `generateReport`) is present AND `npm test`
  passes.
- **Control-lens finding (mirrors the current, unpatched Structure
  checklist item literally):** fires iff the tree is NOT
  `plan-conformant` by the rule above — i.e., any divergence from the
  plan's named four-file split is a finding, independent of whether the
  requirement is met.
- **X2-B-lens finding (mirrors `cp/x2b`'s patched Structure line and
  its Part 1 "judge what the brief required" paragraph):** fires only
  if the change's own requirement is NOT served — here, only if
  `npm test` fails or one of the five required `index.js` exports is
  missing. File-organization divergence by itself is never sufficient.

## Validation (controller ruling, committed-pytest-only, no
container/API spend)

Per the same controller ruling `cp-x1-edit-existing`, `cp-x1-wavecap`,
`cp-x6-planframed`, and `cp-x8-approvals-v2` operated under (their own
test files' docstrings), this task spends no containers or API budget
on real reps. Instead `campaigns/cost-pathologies/
test_cp_x2_consequential.py` validates, against the two CONSTRUCTED
trees above:

1. `setup.sh`'s materialized starting tree is deterministic (two
   independent copies of the scenario's own `fixtures/` are
   byte-identical) and passes its own test suite as shipped, with none
   of `src/reports/` present yet.
2. Both outcome trees are FUNCTIONALLY complete and identical from the
   outside: `node --test` passes on each, `index.js` exports all five
   required names on each, and `test/report.test.js`'s own file
   content is byte-identical between the two trees (the structure-
   agnostic-tests proof above).
3. The tree-classification rule above correctly labels
   `plan-conformant/` as conformant and `reasonable-deviation/` as a
   deviation (not accidentally conformant, not accidentally an
   incomplete/broken tree).
4. The control-lens and X2-B-lens rules, applied to both trees, produce
   the predicted per-arm signature above: control fires on the
   deviation tree only; X2-B fires on neither tree; both lenses agree
   (no finding) on the conformant tree.

This task's brief line ("MICRO validation (2 reps)") predates the
controller ruling that produced `cp-x1-edit-existing`'s
committed-pytest-only precedent, which this task follows instead (no
container spend), consistent with the same ruling `cp-x1-wavecap`,
`cp-x6-planframed`, and `cp-x8-approvals-v2` followed after it.
