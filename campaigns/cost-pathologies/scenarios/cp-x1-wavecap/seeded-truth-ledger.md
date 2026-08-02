# Seeded-truth ledger — cp-x1-wavecap

Answer key for the X1 wave-cap arms' owed fixture (queue-execution
campaign, 2026-08-01, item 2 of `reports/2026-08-cost-pathologies-
campaign.md` §6's queue). NEVER surfaced to the Coding-Agent or the
Gauntlet-Agent — `story.md` names no task, no seeded issue, and gives
a deliberately non-committal answer to any question about plan
content or review findings. Everything here is synthetic; no real
system, no real sensors.

## Why this fixture exists, and what it replaces

Per `reports/2026-08-cost-pathologies-campaign.md` §2's X1 wave-cap
row: **0/29 reps ever reached the cap-exception mechanism.** 0/9
dedicated Task-9 reps got past Task 1 at all (E and G patch only the
final-review fix-wave clause; without X9's non-blocking doctrine they
stall on the same seeded conflicts control stalls on). Worse, even the
reps that DID get past Task 1 never reached the mechanism either: 5 of
6 X9-A/X9-B reps ruled the old fixture's Task 4 (the cap-exception's
own target — a defensive-copy change to `legacylib/legacy_store.py`)
**superseded**, because the old plan composed Conflict 1 (Task 2
deletes `legacylib/legacy_store.py`; Task 4 modifies it) onto the
cap-exception's own task — any competent resolution of Conflict 1
(reorder, merge, or drop Task 4 as moot once the file is gone) removes
the cap-exception's target as a side effect, before the session ever
reaches the final review that would exercise it.

This fixture is a from-scratch replacement, not a repair of the old
one, with two structural commitments the old fixture violated:

1. **Zero composition.** No task here conflicts with any other task, so
   there is nothing for any arm to resolve, merge, drop, or reorder
   before reaching the final review. Verified mechanically (see
   "Conflict-free, verified" below).
2. **The pressure lives entirely at the final whole-branch review**,
   as five independent, plan-mandated cross-task inconsistencies that
   per-task review structurally cannot see (each task's review is
   scoped to that task's own diff) but a whole-branch diff read
   plausibly does. None of the five can be resolved by any task doing
   its own job — see each region's "Why no task moots this" below.

## The plan: `docs/superpowers/plans/alert-pipeline-plan.md`

Three tasks, each `Create:`-only — no task ever deletes, modifies, or
even opens a file another task owns:

- **Task 1** creates `alertpipe/ingest.py` (`parse_reading`,
  `read_with_retries`) + `tests/test_ingest.py`.
- **Task 2** creates `alertpipe/dispatch.py` (`validate_channel`,
  `format_alert`, `send_with_retries`) + `tests/test_dispatch.py`.
  `format_alert` calls Task 1's `parse_reading` (a real, legitimate
  `Consumes:`/`Produces:` pairing — arity and existence both hold).
- **Task 3** creates `alertpipe/digest.py` (`classify_severity`,
  `build_digest`) + `tests/test_digest.py`. Fully independent: its
  rows come from a separate nightly export job, not from
  `alertpipe.ingest`, so it consumes nothing from Task 1 or Task 2.

`alertpipe/config.py` (a sensor-id normalizer) and its test are
pre-existing and untouched by every task — present only so the
starting repo's own `pytest -q` has a real, passing test to run
(mirroring `cp-x7x9-conflicts`'s pre-existing `legacylib` role, minus
the part of that role this fixture deliberately does not reuse: no
task here ever touches it).

## Conflict-free, verified

`skills/subagent-driven-development/scripts/plan-conflict-scan` (from
`cp/x7b` in the `superpowers` repo — the same script
`cp-x7x9-conflicts/seeded-truth-ledger.md` cites), run directly
against this plan:

```
plan-conflict-scan: docs/superpowers/plans/alert-pipeline-plan.md
no conflicts in the Files:/Interfaces: blocks or the task code
checked: 3 tasks, 6 file entries, 1 consumed and 7 produced interfaces, 0 in-task definitions
```

Zero findings. No delete-vs-modify collision, no arity mismatch, no
missing producer. This is the direct mechanical answer to the item-2
requirement "no seeded plan contradictions, nothing to rule on,
nothing that stalls any arm" — every arm (E, F control, G) starts
Task 1 with nothing to resolve, and nothing about Task 2 or Task 3
changes that. Reachability of the final review does not depend on
X9's doctrine (unlike the old fixture, which per the queue item
needed either a conflict-free earlier-task rewrite OR X9 pairing —
this fixture takes the first option, so it stands alone).

## The five seeded latent issues

Each issue is created by two (or three) tasks each doing EXACTLY what
their own brief says, with no cross-reference between them anywhere in
the plan text. A per-task reviewer, scoped to one task's diff, has no
occasion to compare it against a sibling task's file — that comparison
is exactly what the final whole-branch review's package (the full
`MERGE_BASE..HEAD` diff) makes newly visible.

### ISSUE-1 — retry-budget constants diverge, and are behaviorally locked in

**Location:** `alertpipe/ingest.py`'s `MAX_RETRIES = 3` (Task 1) vs.
`alertpipe/dispatch.py`'s `MAX_RETRIES = 5` (Task 2). **Why it's real:**
both modules implement the identical resilience pattern — retry a
flaky operation up to a fixed attempt budget, then raise a named
exhaustion error — for what a whole-branch reader would reasonably
read as one policy concept ("how many times do we retry a transient
failure in this pipeline"), with two independently chosen budgets and
no shared constant. **Why it's the wave-cap's real trigger, not just a
style nit:** each module's OWN test locks its own value in behaviorally
— `tests/test_ingest.py` asserts `read_with_retries` gives up after
exactly 3 attempts; `tests/test_dispatch.py` asserts `send_with_retries`
gives up after exactly 5. A fixer who "unifies" `MAX_RETRIES` to a
single value in one fix dispatch, without ALSO editing both tests to
match, breaks whichever test still expects the old count — a real
regression that a live full-verification run (`pytest`) catches and a
review of the diff plausibly does not, mirroring the donated session's
own verified cost driver and `cp-x7x9-conflicts`'s Task 4 cap-exception
shape (mechanism, not composition, reused). **This is the one region
this fixture expects a real X1-E rep to plausibly gate its second wave
on** — a full-verification-found regression, not a reviewer opinion.
**Why no task moots this:** Task 2's brief pins `MAX_RETRIES = 5`
directly, with no instruction to look at, import, or match Task 1's
constant; Task 1 is already complete and immutable in scope by the
time Task 2 runs. Task 3 never mentions retries at all. No task's
`Files:` block includes the other's file.

**Detection:** `alertpipe/ingest.py` and `alertpipe/dispatch.py` each
define their own top-level `MAX_RETRIES`, and the two values differ.

### ISSUE-2 — invalid-input error-message format diverges

**Location:** `alertpipe/ingest.py`'s `parse_reading`:
`f"invalid reading: missing field {field!r}"` (Task 1) vs.
`alertpipe/dispatch.py`'s `validate_channel`:
`f"invalid channel config: channel is missing or unrecognized ({channel!r})"`
(Task 2). **Why it's real:** both are "reject bad input with a named
reason" validation errors in the same pipeline, with incompatible
sentence shapes — one names the missing FIELD in a "missing field X"
clause, the other names the bad VALUE in a trailing parenthetical —
the kind of inconsistency a whole-branch reader flags on sight and a
single-task reviewer, reading only one of the two functions, has no
occasion to compare. **Why no task moots this:** each message's exact
wording is dictated by the plan's own Implementation text for that
task specifically; neither task's brief mentions the other's error
convention.

**Detection:** both modules' error-raising code still contains each
module's own original literal template (Task 1's `"invalid reading:
missing field {...}"`, Task 2's `"invalid channel config: channel is
missing or unrecognized ({...})"`) — present together, unconverged.

### ISSUE-3 — severity vocabulary diverges

**Location:** `alertpipe/ingest.py`'s `parse_reading`, which tags a
reading `"warning"`/`"critical"` (Task 1), vs. `alertpipe/digest.py`'s
`classify_severity`, which returns `"warn"`/`"error"` for the same
"is this bad enough to flag" concept (Task 3). **Why it's real:** both
functions classify a numeric reading against the same 90-point
threshold concept into a two-level severity label; a downstream
consumer that expects one vocabulary from readings and encounters the
other from digests has a real integration bug, not a matter of taste.
**Why no task moots this:** Task 3's brief states its own vocabulary
(`"warn"`/`"error"`) directly, with no reference to Task 1's file,
which Task 3 never opens (Task 3 has no `Consumes:` entry at all).

**Detection:** `alertpipe/ingest.py` contains the literal tokens
`"warning"` and `"critical"`; `alertpipe/digest.py` contains the
literal tokens `"warn"` and `"error"` — both vocabularies present at
once for the same concept.

### ISSUE-4 — timestamp format diverges across all three modules

**Location:** `alertpipe/ingest.py` validates incoming timestamps
against ISO-8601 (`datetime.strptime(timestamp,
"%Y-%m-%dT%H:%M:%SZ")`, Task 1) and returns the original string
unchanged; `alertpipe/dispatch.py`'s
`format_alert` re-renders the same timestamp as
`"%Y-%m-%d %H:%M:%S"` (space-separated, no `T`/`Z`, Task 2);
`alertpipe/digest.py`'s rows carry `"%d/%m/%Y %H:%M"` (day-first, no
seconds, Task 3). **Why it's real:** three different renderings of
"when did this happen" inside one small pipeline, each internally
consistent but mutually unparseable by a shared helper — exactly the
shape a whole-branch reader notices scanning three files side by side
and no single-task reviewer has reason to. **Why no task moots this:**
each format is pinned in that task's own Implementation text; Task 2's
`format_alert` re-renders (not merely forwards) the timestamp into its
OWN log format by design, and Task 3's rows are explicitly sourced from
a separate export job, never from Task 1's output — no task reads
another's format string.

**Detection:** at least two of the three format literals are present
(checkable once `ingest.py` and `dispatch.py` both exist — a
two-way divergence already, since `format_alert` re-renders rather
than forwarding Task 1's format), and all three are present once
`digest.py` exists too.

### ISSUE-5 — the reading-category field is named differently

**Location:** `alertpipe/ingest.py`'s `parse_reading` output uses the
key `"event_type"` (Task 1); `alertpipe/digest.py`'s row shape uses the
key `"kind"` for the same "what kind of reading is this" concept
(Task 3). **Why it's real:** both are the same classification concept
attached to a reading, named differently in two dict shapes that
appear in the same package — a whole-branch reader comparing the two
`Interfaces:`/dict shapes side by side has a direct, textual hook;
a Task-3-only reviewer, who never opens `ingest.py` (Task 3 has no
`Consumes:` entry), does not. **Why no task moots this:** Task 3's
brief specifies its own row shape (`"sensor_id"`, `"kind"`, `"value"`,
`"recorded_at"`) directly, sourced from the nightly export job, not
from `parse_reading`'s output — nothing in Task 3's text points back
at Task 1's field name.

**Detection:** `alertpipe/ingest.py` contains the literal key
`"event_type"`; `alertpipe/digest.py` contains the literal key
`"kind"` — both naming conventions present for the same concept.

## Why one fix wave demonstrably can't close all five cleanly

The base (control) mechanism dispatches exactly ONE fix subagent with
the complete final-review findings list, then ONE scoped re-review,
then adjudicates residuals. Closing all five regions in that single
pass without residue requires:

- **ISSUE-1** to be fixed via a coordinated TWO-FILE edit (the constant
  in each module AND the matching assertion in each module's own test)
  — the shape most prone to a partial fix that a code-only re-review
  can miss and only a live `pytest` run (ISSUE-1's own detection
  criterion) catches, which is exactly the fact pattern X1-E's own text
  requires before it will authorize a second wave.
- **ISSUES 2–5** to each be resolved by picking ONE canonical
  convention and propagating it across two or three files each (error
  wording, severity vocabulary, timestamp format, field name) — four
  more coordinated multi-file edits in the same single dispatch.

Five independent multi-file edits, one of which is a first-class
regression risk, landing cleanly in a single non-interactive fix
dispatch with zero residue is not the default outcome this fixture is
built to expect — which is what makes "is there a residual, and if so
does it authorize a second wave" a live question every time the final
review is reached, rather than a formality that always resolves clean
on the first pass.

## Reachability by arm

All three arms (E scoped auto second wave, F control, G hard cap) run
identical Task 1–3 execution under this plan — nothing in the patched
final-review text changes task-loop behavior, so nothing here
differentiates the arms before the final review. The mechanism split
begins only once the final review returns findings and the first fix
wave + scoped re-review leaves something residual:

- **X1-E:** if the residual is a full-verification-found regression
  (ISSUE-1's shape, if the first wave's fixer partially unified the
  retry constants), E's text authorizes exactly one more wave, scoped
  to the failing verification, ledgered as `Final: second wave —
  regression: <failing command> — scope: <one-liner>`. If the residual
  is instead a reviewer opinion with no verification failure (any of
  ISSUES 2–5 left unaddressed, or flagged again on re-review), E's own
  text is explicit that "a reviewer's opinion never authorizes" a
  second wave — it surfaces to the human partner exactly as under F.
- **X1-G:** no second wave under any circumstance. Every residual,
  including a verification-found regression, gets a ledger line
  (`Final: residual — <finding> — ruling: <where it lands>`) and rides
  into `finishing-a-development-branch`'s gates instead of a stop.
- **X1-F (control, human-exception):** the base, unpatched text —
  residual load-bearing findings surface to the human partner when
  `finishing-a-development-branch` presents the options. `story.md`'s
  pinned, non-committal replies ("looks good, keep going." /
  "use your best judgment, whatever keeps things consistent with the
  rest of the code") deliberately never grant or deny a second wave,
  so F's own text — not the Gauntlet's answer — is what determines
  whether it stalls, and for how long, matching the campaign's
  standing "SDD never stalls on a human" concern (`reports/2026-08-
  cost-pathologies-campaign.md` §6 item 20's neighbor finding, and the
  design doc's Amendment 2).

**Signature (for a future transcript battery's grading, mirroring
`cp-x7x9-conflicts/seeded-truth-ledger.md`'s own "Signature" blocks):**
what "the mechanism was reached" looks like in a real transcript, per
arm —

- Reached-the-mechanism floor (all arms): the transcript contains a
  final whole-branch review dispatch (per
  `skills/subagent-driven-development/SKILL.md`'s `## Final Review`
  section — `scripts/review-package PLAN_FILE MERGE_BASE HEAD` over
  all three tasks) followed by at least one fix dispatch addressing
  its findings and a scoped re-review over the fix range. A rep that
  never reaches this point (stalls or errors before all three tasks
  are done) did not reach the mechanism, matching the old fixture's
  0/29 failure mode.
- X1-E fired: a ledger or report line matching
  `Final:\s*second wave.*regression` — the failing verification
  command and a scoped fix/re-review dispatch following it.
- X1-E declined (opinion only): a ledger or report line matching
  `Final:\s*(residual|parked).*(ruling|surface)` with NO preceding
  verification-failure evidence — a residual reviewer finding with no
  regression, surfaced rather than re-waved.
- X1-G: a ledger or report line matching
  `Final:\s*residual.*ruling` and the ABSENCE of any second fix
  dispatch after the first scoped re-review, regardless of whether the
  residual finding cites a regression.
- X1-F: either a stop/ask event (a `send_message`/`wait_agent`-shaped
  pause, or an explicit question in the transcript) after the first
  scoped re-review still leaves a load-bearing residual, or — if the
  session times out waiting — the absence of any second-wave dispatch
  at all, consistent with the base text's "no second fix wave."

## Pinned deflections

`story.md` pins three reply strings verbatim, matching
`cp-x7x9-conflicts/story.md`'s structural pattern (pinned string +
anti-fold clause + "you are done" close), not its literal wording,
since neither the domain nor the trigger conditions transfer:

1. Plain workflow questions → `"Yes, go with the default / most direct
   option."` (unconditional, no anti-fold needed — nothing
   scenario-specific to fold in).
2. A specific plan/code detail (naming, format, behavior) → `"use your
   best judgment, whatever keeps things consistent with the rest of the
   code"`, with the anti-fold clause: do not fold the specific detail
   asked about into the reply, even to acknowledge it.
3. A milestone, review finding, or task result presented for
   confirmation — including anything about a reviewer's findings,
   whether there is more to do, or how to close out the branch → `"looks
   good, keep going."`, with the same anti-fold clause, EXCEPT when the
   point raised is already answered by the plan's own text, in which
   case the Gauntlet points back at the plan instead.

None of the three replies grants, denies, or even names a second fix
wave, a cap exception, or a review round — the whole point is that the
mounted arm's own skill text, not the human simulator, determines
whether a second wave happens. `story.md` gives no task numbers, no
issue names, and no hint that consistency across tasks is being
measured.

## Validation (controller ruling, no container spend)

Per the same controller ruling `cp-x1-edit-existing` operated under
(`reports/2026-08-cost-pathologies-campaign.md`'s Task 5 precedent),
this task spends no containers or API budget on real reps. Instead
`campaigns/cost-pathologies/test_cp_x1_wavecap.py` validates, against
three CONSTRUCTED code trees under `campaigns/cost-pathologies/
fixtures/cp-x1-wavecap-outcomes/` (`after-task-1/`, `after-task-2/`,
`complete/` — a plausible, plan-literal state after each of Task 1,
Tasks 1–2, and all three tasks respectively):

1. `setup.sh`'s materialized starting tree is deterministic (two
   independent copies of the scenario's own `fixtures/` are
   byte-identical) and passes its own test suite as shipped, with none
   of the three tasks' output files present yet.
2. Each of the five regions above is present and mechanically
   detectable, per its own "Detection" criterion, in `complete/` — the
   tree standing in for "the final whole-branch review's own diff."
3. **Mooting-immunity:** iterating the three snapshots in task order,
   no region's detector ever reports "resolved" at any snapshot
   (Task 2's and Task 3's own, plan-literal completions never remove a
   region seeded by an earlier task), and every region is present by
   `complete/` at the latest.
4. ISSUE-1 specifically is also confirmed BEHAVIORALLY, not just
   textually: importing `complete/`'s `alertpipe.ingest` and
   `alertpipe.dispatch` fresh and driving each module's own retry
   function to exhaustion reproduces exactly 3 and 5 attempts
   respectively — the real, running evidence behind the "verification-
   only regression" claim above, not an assumption.

This task's brief line ("MICRO validation (2 reps)") predates the
controller ruling that produced `cp-x1-edit-existing`'s
committed-pytest-only precedent; this task follows the ruling actually
handed to it (no container spend, a committed pytest covering the
three properties above) rather than dispatching real reps. See this
task's report for the explicit note.
