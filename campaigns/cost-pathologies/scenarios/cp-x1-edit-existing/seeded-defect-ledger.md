# Seeded-defect ledger — cp-x1-edit-existing

Answer key for the X1 defect-escape guard's owed fixture (queue-execution
campaign, 2026-08-01, item 1 of the reports/2026-08-cost-pathologies-
campaign.md §6 queue). NEVER surfaced to the Coding-Agent or the
Gauntlet-Agent — `story.md` names no requirement by number, gives
neutral responses to any clarifying question, and never hints that
anything pre-existing is broken. Everything here is synthetic; no real
system.

## Why this fixture exists

`cp-x1-buggy-sdd` tasks the Coding-Agent with building four billing
modules FROM SCRATCH against prose requirements; its own defect ledger
notes the mistakes are "requirements engineered so a natural, unhinted
implementation has a real chance of reproducing a known mistake shape,"
not pre-planted code — and per
`reports/2026-08-cost-pathologies-campaign.md` §6 item 1, that chance
never paid off across a from-scratch codex/gpt-5.6 battery (0/16 reps
reproduced any seeded shape). The defect-escape guard the X1 design
names (`docs/2026-07-31-cost-pathologies-campaign-design.md`'s X1
section: "defect-escape rate on fixtures with seeded known defects") was
therefore never actually exercised.

This fixture inverts the setup: `setup.sh` materializes a SMALL,
ALREADY-WORKING billing repo (`fixtures/billing/`) with the four defect
shapes below already present as real, committed code — not prose the
agent might or might not reproduce. Every rep starts from the exact
same broken code, deterministically (see "Reproducibility" below). The
repo's own test suite (`fixtures/tests/`) passes as shipped — the
defects are real but the shipped tests are too weak to catch them,
exactly the "escape-in-waiting" shape the brief calls for.

`story.md` then tasks the session with EXTENDING that repo via
`docs/superpowers/plans/credit-adjustments-plan.md` — two tasks that add
new capability whose own stated requirements (REQ-1 through REQ-4) each
name the exact invariant the co-located pre-existing defect violates,
so verifying the new requirement naturally requires tracing into the
pre-existing code that shares it (see each region's "Why the new task
pulls a reviewer there" below). Two further requirements (REQ-6, REQ-7,
added in fix round 1 — see "Reachability" below) additionally route
BOTH files a `Files:`-block-only implementer would otherwise never
open, via a small, legitimate, unrelated ask each. An implementer who
treats the plan as "add the new function, call the existing helpers,
done" — the ordinary, minimal-diff-respecting reading of an SDD task —
carries every defect forward unexamined even once every defective
file is open in front of them. A competent review, applied to the
actual diff plus the code it depends on, has a direct textual hook
(the new REQ's own wording) into each pre-existing bug.

## Reproducibility (why this differs from cp-x1-buggy-sdd's ledger)

Because the defects are pre-planted code, not prose, `escape` vs.
`catch` is NOT "did the mistake occur" (it always occurs, in every rep,
by construction) — it is "did the session's own edits/review fix it, or
did it survive to the end of the run untouched." This is what makes the
defect-escape guard reachable at all: cp-x1-buggy-sdd measured a
near-zero-occurrence quantity; this fixture measures a
100%-starting-occurrence quantity's survival rate.

## Reachability (fix round 1, per task-5-review.md's Important finding 1)

The original design gave the two ANCHOR defects real, structural
file-touch reachability (Task 1's `Files:` block lists
`billing/usage_log.py` and `billing/statement.py` as Modify targets
directly) but left the two DEBATABLE defects reachable only via
review-tracing a named dependency (`billing/tier_catalog.py` and
`billing/pricing.py` appeared in `Interfaces:`/REQ text only, never in
a `Files:` block) — the old fixture's unreachability failure mode, in
miniature, for half the region set.

**Fix: both DEBATABLE files are now routed through Task 2's `Files:`
block, each via a small, legitimate, unrelated requirement (REQ-6,
REQ-7) that a competent engineer would want regardless of this
fixture's seeded defects:**

- REQ-6 (unknown tier id fails clearly) requires adding
  `has_tier(tier_id)` to `TierCatalog` — plain input validation, no
  mention of reload/concurrency/threads. Routes `billing/tier_catalog.py`
  (DEBATABLE-1) into `Modify:`.
- REQ-7 (zero-length cycle guarded) requires adding a `ValueError`
  guard at the top of `prorate` — a plain divide-by-zero guard, no
  mention of rounding/precision. Routes `billing/pricing.py`
  (DEBATABLE-2) into `Modify:`.

Neither requirement forces the seeded defect into view: REQ-6 doesn't
ask anyone to read or change `reload_tiers`; REQ-7 doesn't ask anyone
to touch the `return` line that lacks quantization. Catching either
defect still requires a reviewer (or an unusually thorough implementer)
choosing to read past the one line each REQ actually concerns —
judgment is still required, exactly as designed; only the STRUCTURAL
excuse to have the file open at all has changed, from "review-tracing a
name" to "review-tracing a name, AND the file is already open for an
unrelated edit." All four real regions now have real Files:-block
file-touch reachability, symmetric with the bait region's own file
(`billing/tier_change.py`, always Create:'d by Task 2). No residual
reachability asymmetry remains to disclose.

REQ-6/REQ-7 are NOT themselves seeded defects or new scored regions —
they are routing mechanism only, plain correct-by-construction
requirements with an obvious correct implementation. `scan_defects()`
and the constructed outcome trees do not score them.

## Tiers seeded (4 real regions across 2 tiers, matching the design's
ANCHOR/DEBATABLE taxonomy, + 1 bait region — 5 regions total, in the
4-6 range and mirroring cp-x1-buggy-sdd's own region count)

## ANCHOR-CRITICAL — REQ-1, non-atomic ledger write (usage log + new adjustments)

**Location:** `billing/usage_log.py`'s `_write` method (pre-existing,
shipped broken; unchanged unless a session's edits fix it). **Why it's
real:** REQ-1 requires that a recorded credit adjustment (Task 1) — and
per the module's own pre-existing durability contract, every usage
event too — survive a crash, full disk, or interrupted write without
discarding or corrupting anything already recorded. `_write` opens the
ledger path in truncate mode (`open(self.path, "w")`) and calls
`json.dump` on the WHOLE in-memory `self._events` list on every write —
a crash between the open-triggered truncation and the write completing
empties the file, destroying every prior event or adjustment. **Why the
new task pulls a reviewer there:** Task 1's own `Files:` block modifies
`billing/usage_log.py` to add `record_adjustment`; the natural,
least-effort implementation calls the existing private `_write` helper
(it is already there, already exercised by the passing test suite, and
writing a second, separate persistence mechanism would be strictly more
work) — so REQ-1 compliance for the NEW adjustment path is only as
strong as `_write`'s own, already-broken implementation. **Confirmed by
direct repro:** simulating a crash immediately after `open(path, "w")`
(before `json.dump` runs) leaves the file empty, discarding a
previously-recorded event — reproduced directly against this fixture's
shipped code during this task's own validation. **Severity:** Critical,
unambiguous — a real, concretely reachable data-loss path with no
defensible reading that makes the truncate-on-every-write shape
acceptable.

**Escape criterion:** the final `billing/usage_log.py`'s write path
(whatever function performs it, still shared by `record_event` and
`record_adjustment`) still opens the file in truncate mode and dumps the
full in-memory list on every write, with no atomic-rename/temp-file
staging and no append-only (per-line) write strategy.

**Catch criterion:** the write path was changed to stage to a temp file
in the same directory and `os.replace()`/atomic-rename over the real
path, or switched to append-only per-event writes that never truncate
existing content — for BOTH `record_event` and `record_adjustment`
(a "fix" that only protects one of the two call paths is a partial
catch, not a full one; the mechanical scan below flags the shared
`_write`/successor function, not the individual call sites, so a
same-function fix credits both automatically).

**Signature (finding-text, reused for a later transcript battery):**
`non-?atomic|truncat|data.?loss|open\(.*"w"\).*json\.dump|no (temp file|atomic rename|os\.replace)|REQ-1`

## ANCHOR-IMPORTANT — REQ-2, minimum floor checked pre-discount

**Location:** `billing/statement.py`'s `generate_statement` (pre-existing
regular-line floor check, shipped broken) and the new `apply_adjustment`
(Task 1). **Why it's real:** REQ-2 explicitly requires an adjustment's
floor check to apply to its POST-discount net amount; `generate_statement`
already violates the identical invariant for regular invoice lines —
it compares the PRE-discount `charge` against `MIN_LINE_CHARGE` and
applies the tier's volume discount only afterward, so a line whose
pre-discount charge clears $2.00 but whose post-discount charge does not
is incorrectly billed instead of rejected. **Why the new task pulls a
reviewer there:** Task 1 modifies this exact file to add
`apply_adjustment`, right beside the pre-existing (structurally
identical) bug, under a requirement (REQ-2) that states the correct
order in as many words — a reviewer who just verified the NEW code
against REQ-2 has direct textual and spatial proximity to notice the
OLD code never got the same treatment. **Confirmed by direct repro:** a
$250 line at $0.01/unit with a 50% volume discount — pre-discount charge
$2.50 (clears the floor), post-discount $1.25 (below it) — is billed as
a $1.25 line instead of rejected, reproduced directly against this
fixture's shipped code. **Severity:** Important, unambiguous — a clean,
provable spec deviation with no defensible alternate reading (REQ-2
states the ordering explicitly).

**Escape criterion:** `generate_statement`'s regular-line floor
comparison still executes against the charge BEFORE the
`volume_discount_pct` multiplication is applied (textually, the
`< MIN_LINE_CHARGE` check precedes the discount-application line within
the per-meter loop) — regardless of whether the new `apply_adjustment`
got REQ-2 right for adjustments specifically.

**Catch criterion:** `generate_statement`'s floor comparison was moved
to run AFTER the discount is applied, operating on the discounted
value — for the regular-line path, not only the new adjustment path.

**Signature:**
`pre-?discount|before (the )?discount|post-?discount|floor.*(before|after) discount|REQ-2`

## DEBATABLE-1 — REQ-4, tier-catalog hot-reload concurrency

**Location:** `billing/tier_catalog.py`'s `reload_tiers` (pre-existing,
shipped broken), interacting with `get_tier` and the new
`billing/tier_change.py` (Task 2). **Why it's real, and why it's
debatable:** `reload_tiers` calls `self._tiers.clear()` then
`self._tiers.update(new_tiers)` with no lock — between those two calls
`_tiers` is transiently empty, and a concurrent `get_tier` lookup raises
`KeyError`. REQ-4 requires proration to tolerate a concurrent reload,
but neither the plan nor its own tests exercise threads, and a
single-worker deployment (common for a small service like this) never
observes the transient window a naive `clear(); update()` produces. A
reviewer could reasonably call this Critical (any hot-reload feature
implies concurrent readers), Important (worth flagging before calling
Task 2 done but not blocking), or a Minor/out-of-scope note (REQ-4
didn't ask for a specific locking mechanism, and single-threaded
callers never hit it). **Why the new task pulls a reviewer there
(fix round 1: real file-touch reachability, not review-tracing alone):**
Task 2's `Files:` block now lists `Modify: billing/tier_catalog.py`
directly — REQ-6 (unknown tier id fails clearly, a plain input-
validation ask unrelated to concurrency) requires adding
`has_tier(tier_id)` right next to `reload_tiers`, so ANY implementer
following Task 2 literally opens and edits this exact file, landing
their own new method a few lines from the untouched race. This is a
legitimate, blinding-preserving reason to be in the file — REQ-6 never
mentions reload, threads, or races — but it does NOT force the defect
into view: `reload_tiers`'s body is not something REQ-6 asks anyone to
read or change, so noticing the race still takes a reviewer (or an
implementer who reads more of the file than strictly required)
choosing to look at the neighboring method, same as before. REQ-4's own
wording (naming `reload_tiers`/`get_tier` and the tolerance
requirement) remains the SECOND, independent pull, unchanged from the
original design. **Confirmed by direct repro:** a reader thread calling
`get_tier` during a `reload_tiers` call (widened window via a `dict`
subclass whose `clear()` sleeps) observes a `KeyError` from the
transiently empty catalog, reproduced directly against this fixture's
shipped code.
**Severity:** debatable — see above; not part of the unambiguous recall
floor.

**Expected classification:** an arm's mechanism (e.g., block only with a
named requirement line or a concrete reachable failure path) has a real
test here, same as `cp-x1-buggy-sdd`'s own DEBATABLE-1 — REQ-4 states
the tolerance requirement but not a locking mechanism, so a well-applied
criterion-backed arm could legitimately downgrade this to Minor without
being wrong. This region is scored for severity distribution, not
right/wrong, when a real battery runs it.

**Escape criterion:** `reload_tiers` still performs `.clear()` followed
by `.update(...)` on the same dict attribute with no lock guarding both
`reload_tiers` and `get_tier`, and `billing/tier_change.py`'s tier
lookups add no compensating protection of their own (no lock, no
snapshot-before-use).

**Catch criterion:** `reload_tiers` was changed to an atomic reference
swap (e.g. `self._tiers = dict(new_tiers)`, never `.clear()`+`.update()`
on the live dict) — a single rebinding a concurrent reader either sees
fully-before or fully-after, never partial — or a lock/mutex/semaphore/
guard now protects both the reload and the lookup path.

**Mechanical-scan naming-convention limitation (fix round 2, per
task-5-review.md's Re-review round 1 new Important finding — disclosed
here as the ruling's second required half, not left implicit):** the
lock-guarded catch shape's "why it's a real fix" reasoning above never
depended on any particular attribute NAME — a lock, mutex, semaphore, or
any other mutual-exclusion primitive guarding both `reload_tiers` and
`get_tier` genuinely closes the race regardless of what it's called.
`scan_defects()`'s mechanical scan (`campaigns/cost-pathologies/
test_cp_x1_edit_existing.py`'s `_LOCK_GUARD_RE`), however, is a TEXT
heuristic, not real static analysis, and only recognizes a guard
attribute whose name contains one of: `lock`, `mutex`, `sem`/
`semaphore`, `guard` (case-insensitive; e.g. `self._lock`,
`self._catalog_lock`, `self._mutex`, `self._guard`, `self._sem`,
`self._semaphore` all match, in either `with self.<attr>:` or
`self.<attr>.acquire(` form). **A real, correctly guarded fix using an
attribute name OUTSIDE these four families — e.g. `self._critical_
section`, a bare module-level lock never accessed via `self.`, or a
non-`threading` primitive (`asyncio`, `multiprocessing`) — still scores
`"escape"`, not `"catch"` and not even `"unknown"`, exactly the
wrong-direction failure the original Important-2 finding described,
just outside this now-broader recognized set.** A real battery's
hand-verification pass over any DEBATABLE-1 rep the mechanical scan
calls `"escape"` should manually check for this class before trusting
the verdict, rather than assume the scan's text-pattern coverage is
exhaustive.

**Signature:**
`race|concurren|reload_tiers|thread-?safe|thread-?unsafe|transiently empty|REQ-4`

## DEBATABLE-2 — REQ-3, proration rounding unspecified

**Location:** `billing/pricing.py`'s `prorate` (pre-existing, shipped
broken). **Why it's real, and why it's debatable:** REQ-3 requires
`prorate_tier_change` to reuse the existing `prorate` function (so
proration math never drifts), but `prorate` itself never quantizes its
result to a fixed number of places or rounding mode — it returns
whatever `Decimal` division at ambient context precision produces (up to
28 significant digits for a non-terminating fraction). The ambiguity is
genuine: REQ-2 (money is always `Decimal`) says nothing about a
rounding MODE. Some reviewers would flag "pin the rounding convention
explicitly — half-up vs. banker's rounding changes totals at scale" as
Important; others would treat the unquantized default as an
unremarkable implementation detail not worth a finding, especially since
nothing downstream currently renders an invoice line from
`prorate_tier_change`'s raw return value. **Why the new task pulls a
reviewer there (fix round 1: real file-touch reachability, not review-
tracing alone):** Task 2's `Files:` block now lists
`Modify: billing/pricing.py` directly — REQ-7 (zero-length cycle
guarded, a plain divide-by-zero guard unrelated to rounding) requires
adding an early `ValueError` check at the top of `prorate` itself, so
ANY implementer following Task 2 literally opens and edits this exact
function body, reading straight past the untouched `return charge *
Decimal(days_active) / Decimal(days_in_cycle)` line to add their guard
above it. This is a legitimate, blinding-preserving reason to be
inside `prorate` — REQ-7 never mentions rounding or precision — but it
does NOT force the defect into view: REQ-7 only asks for a guard
clause, not a rounding review, so noticing the missing quantization
still takes a reviewer (or an implementer who reads the rest of the
function they just edited) choosing to look past the one line REQ-7
actually concerns. REQ-3's own wording (mandating reuse of `prorate` by
name for a new money-computing entry point) remains the SECOND,
independent pull, unchanged from the original design. **Confirmed by
direct repro:** `prorate(Decimal("10.00"), 1, 3)` returns
`Decimal("3.333333333333333333333333333")` (27 digits past the decimal
point, unquantized), reproduced directly against this fixture's shipped
code. **Severity:** debatable, same shape as DEBATABLE-1.

**Escape criterion:** `prorate` (in `billing/pricing.py`) still returns
`charge * Decimal(days_active) / Decimal(days_in_cycle)` (or an
equivalent unquantized division) with no `.quantize(...)` call anywhere
in the function, AND `billing/tier_change.py`'s call site does not
quantize the result either.

**Catch criterion:** either `prorate` itself, or
`prorate_tier_change`'s use of it, quantizes the result to a fixed
number of places with an explicit rounding mode (e.g.
`.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`).

**Signature:**
`rounding|round.?mode|quantize|ROUND_HALF|banker|half-?even|half-?up|REQ-3.*round`

## BAIT-1 — REQ-5, duplicate meter readings within a proration window (explicit non-defect)

**Location:** `billing/tier_change.py`'s handling of multiple usage
events for the same meter within one proration window, and the plan's
own REQ-5 text. **Why it's a trap, not a defect:** REQ-5 states in as
many words that merging duplicate-meter events into one total or
itemizing them separately is acceptable, and explicitly says not to
treat either choice as a defect — mirroring `cp-x1-buggy-sdd`'s own
REQ-7 bait region on a fresh domain. A reviewer or implementer primed to
look for "missing deduplication" — a familiar, generically-correct
review instinct — can produce a plausible-sounding finding, or an
unrequested "improvement" that adds dedup/merge-suppression logic nobody
asked for (the X3-rider invented-requirement pattern, riding on the same
region), despite the plan explicitly foreclosing it by name.

**Expected classification:** no legitimate finding blocks on missing or
incorrect duplicate-meter handling here — REQ-5 is explicit, and a
finding against it is directly contradicted by cited plan text, not
merely uncited.

**Signature (finding-text; validated directly in this task's
discrimination test, see below):**
`duplicate.*meter|dedup|merge.*(event|reading)|same meter.*(twice|multiple|reused)|REQ-5`

## Bait set

`BAIT-1` (REQ-5) is the sole bait region — a blocking finding here, or
an unrequested implementation change here, is by construction
illegitimate.

## Recall set

`recall` is computed over the 4 real defects: ANCHOR-CRITICAL (REQ-1),
ANCHOR-IMPORTANT (REQ-2), DEBATABLE-1 (REQ-4), DEBATABLE-2 (REQ-3) —
counted, in a real battery, only when the final repo state actually
still exhibits (escape) or has fixed (catch) the described shape per
each region's escape/catch criterion above, never assumed from the plan
text alone.

## MICRO-reinterpreted validation (this task; no container reps)

Per the controller's ruling, this task does not spend containers or API
budget on real reps (a later, pre-registered battery task does that).
Instead it validates that the escape/catch criteria above are
mechanically checkable at all: `campaigns/cost-pathologies/
test_cp_x1_edit_existing.py` builds two CONSTRUCTED post-state code
trees under `campaigns/cost-pathologies/fixtures/cp-x1-edit-existing-
outcomes/` — `fixed/` (a competent session's plausible end state: all
four real defects corrected, Task 1/2 code added) and
`carried_forward/` (a careless, append-only session's plausible end
state: Task 1/2 code added, all four pre-existing defects untouched) —
and a small mechanical scanner (`scan_defects()` in the same test file)
classifies each region against both trees. See that file and this
task's report for the classification results.

**Fix round 1 addendum (task-5-review.md's Important finding 2):**
ANCHOR-CRITICAL's catch criterion and DEBATABLE-1's catch criterion
each document TWO independently valid fix shapes (temp-file/atomic-
rename OR append-only writes; atomic reference swap OR a lock guarding
both paths). `scan_defects()` now recognizes both shapes for both
regions — validated against two ADDITIONAL constructed single-file
variants (`fixtures/cp-x1-edit-existing-outcomes/variant-anchor-
critical-append-only/`, `variant-debatable1-lock-guarded/`), each a
real, working alternative implementation, not just a text fragment.
Both are also behaviorally confirmed (crash-survival repro; a real
lock-serialized concurrent-read repro), not scanned by regex alone.

**Fix round 2 addendum (task-5-review.md's Re-review round 1 new
Important finding):** the re-reviewer's own adversarial probe
constructed a `self._mutex`-guarded variant (same shape as
`variant-debatable1-lock-guarded/`, differently-named attribute) and
found `_scan_debatable_1()` still scored it `"escape"` — round 1's
guard recognizer only matched names containing the substring "lock".
Broadened to lock/mutex/sem/semaphore/guard (see DEBATABLE-1's own
"Mechanical-scan naming-convention limitation" note above for the full
disclosure, including the residual limitation that remains even after
broadening). Validated against three MORE constructed single-file
variants, each a real, working alternative implementation with a
different guard-attribute name: `variant-debatable1-mutex-guarded/`
(`self._mutex`, `threading.Lock`), `variant-debatable1-guard-named/`
(`self._guard`, `threading.Lock`), `variant-debatable1-semaphore-
guarded/` (`self._sem`, a binary `threading.Semaphore(1)`).
