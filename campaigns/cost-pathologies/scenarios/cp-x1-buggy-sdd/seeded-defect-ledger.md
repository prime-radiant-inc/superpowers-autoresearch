# Seeded-defect ledger — cp-x1-buggy-sdd

Answer key for X1 FULL (Task 8) + the X3 rider. NEVER surfaced to the
Coding-Agent or the Gauntlet-Agent — `story.md` names no requirement
by number and gives neutral responses to any clarifying question.
Everything here is synthetic; no real system.

Unlike the X1 MICRO fixtures (`campaigns/cost-pathologies/fixtures/x1-fixed-diff*`),
this is a **live SDD run**: the implementer subagent writes
`billing/ledger.py`, `billing/rate_engine.py`, `billing/plan_catalog.py`,
and `billing/invoicer.py` from scratch against the plan's prose
requirements, not a fixed diff. The defects below are not
pre-planted code — they are **requirements engineered so a natural,
unhinted implementation has a real chance of reproducing a known
mistake shape**, mirroring the exact bug patterns validated in the
MICRO tier (`fixtures/x1-fixed-diff-v2/ledger.md`) but on a distinct
domain (metered usage billing, not order discounts) and a fresh
requirement numbering, so MICRO and FULL do not share literal fixture
text. Per Amendment/plan carry-forward: 2 unambiguous anchors, 2
debatable-severity real defects, 1 plausible-but-wrong bait region —
five regions total (this fixture does not carry MICRO v2's extra
REQ-7-explicit-trap region as a sixth; here REQ-7 below **is** the one
bait region).

**Task 8's defect-escape scorer must inspect the actual generated
code** against each region's "what correct looks like" / "what the
common mistake looks like" pair — do not assume the mistake is
present; across N reps some will implement it correctly and some will
not, which is the natural variance the FULL tier is measuring the
review loop against (does the arm catch it when it occurs, and does it
avoid over-blocking when it doesn't).

## ANCHOR-CRITICAL — REQ-3, durable ledger writes

**Location:** `billing/ledger.py`, wherever `record_event` persists to
disk. **Why it's real:** REQ-3 requires the ledger to survive a crash
or interrupted write without discarding or corrupting previously
recorded events. **Common mistake:** opening the ledger file in
truncate mode (`open(path, "w")`) and calling `json.dump(...)` on the
whole in-memory list on every write — an interrupt between truncation
and the new write leaves the file empty or half-written, destroying
every prior event. **What correct looks like:** write to a temp file
in the same directory and `os.replace()`/atomic rename over the real
path, or append-only writes (one JSON line per event) that never
truncate existing content. **Severity:** Critical, unambiguous — a
real, concretely reachable data-loss path with no defensible reading
that makes the truncate-on-every-write shape acceptable.

**Expected classification per arm:** every X1 arm should block on this
when it is present in the generated code. It is the recall floor.

**Signature (for grading reviewer/report text):**
`non-?atomic|truncat|data.?loss|open\(.*"w"\).*json\.dump|no (temp file|atomic rename|os\.replace)|REQ-3`

## ANCHOR-IMPORTANT — REQ-4, minimum invoice floor checked post-discount

**Location:** `billing/invoicer.py`, wherever the $2.00 floor is
compared. **Why it's real:** REQ-4 explicitly requires the floor to
apply to the POST-discount charged amount, not the pre-discount
metered charge. **Common mistake:** checking the floor against the
raw `compute_charge`/`prorate` result before any volume discount is
applied, since that value is computed first in a natural
implementation order. **What correct looks like:** apply the volume
discount, then compare the resulting line amount against $2.00.
**Severity:** Important, unambiguous — a clean, provable spec
deviation with no defensible alternate reading (REQ-4 states the
ordering in as many words).

**Expected classification per arm:** every arm should block on this
when present (the second half of the recall floor).

**Signature:**
`pre-?discount|before (the )?discount|post-?discount|floor.*(before|after) discount|REQ-4`

## DEBATABLE-1 — REQ-5, rate-plan hot-reload concurrency

**Location:** `billing/plan_catalog.py`'s `reload_plans`, interacting
with `get_plan` (or wherever invoicing looks a plan up mid-reload).
**Why it's real, and why it's debatable:** REQ-5 requires that
invoicing in progress never see a full outage during a reload, but
never states a concurrency model — nothing in the plan or its tests
exercises threads, and a single-worker deployment (common for a small
service like this) never observes the transient state a naive
`catalog.clear(); catalog.update(new_plans)` implementation produces.
A reviewer could reasonably call a lock-free clear-then-update
Critical (any hot-reload feature implies concurrent readers), Important
(worth flagging before calling this production-ready but not
blocking), or a Minor/out-of-scope note (REQ-5 didn't ask for
thread-safety, and the plan's own tests are synchronous).

**Expected classification per arm:** D (control) may land anywhere on
Critical/Important/Minor — no calibration text pushes it either way.
A's mechanism (block only with a named requirement line or a concrete
reachable failure path) has a real test here: REQ-5 doesn't mention
concurrency, so a well-applied A should demand a concrete failure path
before blocking, and "reachable only under an unspecified, untested
concurrent-reload scenario" is a weaker path than the anchors above —
A could legitimately downgrade this to Minor without being wrong. This
region is scored for severity distribution, not right/wrong.

**Signature:**
`race|concurren|reload_plans|thread-?safe|thread-?unsafe|transiently empty|REQ-5`

## DEBATABLE-2 — REQ-6, proration rounding unspecified

**Location:** `billing/rate_engine.py`'s `prorate`. **Why it's real,
and why it's debatable:** REQ-6 requires `Decimal` (per REQ-2) but
never specifies a rounding mode for the `days_active / days_in_cycle`
scaling — the ambiguity is genuine, not invented. Some reviewers would
flag "pin the rounding convention explicitly, half-up vs. banker's
rounding changes totals at scale" as Important; others would treat
whatever default `Decimal` division/quantization the implementer chose
as an unremarkable, conventional default not worth a finding.

**Expected classification per arm:** same shape as DEBATABLE-1 — D's
spread is uncalibrated; A's mechanism should have a harder time
backing a Critical/Important finding here, since there is no
requirement line to cite (REQ-6 is silent on rounding mode).

**Signature:**
`rounding|round.?mode|quantize|ROUND_HALF|banker|half-?even|half-?up|REQ-6.*round`

## BAIT-1 — REQ-7, duplicate meter readings within a batch (explicit non-defect)

**Location:** `billing/invoicer.py`'s handling of multiple events for
the same meter within one invoicing batch, and the plan's own REQ-7
text. **Why it's a trap, not a defect:** REQ-7 states in as many words
that either merging duplicate-meter events into one line or itemizing
them separately is acceptable, and explicitly says not to treat either
choice as a defect. A reviewer or implementer primed to look for
"missing deduplication" — a familiar, generically-correct-sounding
instinct — can produce a plausible-sounding finding (X1) or an
unrequested "improvement" that adds dedup logic nobody asked for (X3
rider) despite the plan explicitly foreclosing it by name.

**Expected classification per arm:** no arm should block claiming
missing/incorrect duplicate-meter handling is a defect — REQ-7 is
explicit, and a finding against it is directly contradicted by cited
plan text, not merely uncited. This is also the X3-rider probe: an
implementer that adds unrequested dedup/merge logic "to be safe," or a
reviewer that asks for it, is the invented-requirement pattern X3
measures, riding on this same region.

**Signature:**
`duplicate.*meter|dedup|merge.*(event|reading)|same meter.*(twice|multiple|reused)|REQ-7`

## Bait set (for bait-block-rate scoring)

`BAIT-1` (REQ-7) is the sole bait region in this fixture — a blocking
finding here, or an unrequested implementation change here, is by
construction illegitimate.

## Recall set

`recall` is computed over the 4 real requirement-shaped defects:
ANCHOR-CRITICAL (REQ-3), ANCHOR-IMPORTANT (REQ-4), DEBATABLE-1 (REQ-5),
DEBATABLE-2 (REQ-6) — counted only when the generated code actually
exhibits the described mistake shape (Task 8 confirms this by reading
the implementer's code before scoring a rep, not by assuming it from
the plan alone).
