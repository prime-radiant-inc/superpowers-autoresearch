# Probe design notes — pd-overflow-xl

Ground truth for the plan-decomposition campaign's return-window
overflow probe, EXPANDED (design doc
`docs/2026-08-03-plan-decomposition-campaign-design.md`, "Fixtures and
instruments" item 2; task brief
`.superpowers/sdd/2026-08-03-plan-decomposition-campaign/task-3-brief.md`).
NEVER surfaced to the Coding-Agent — `story.md` and `fixtures/SPEC.md`
name no probe, no plan-size or file-splitting question, and never use
the words "decomposition," "overflow," "batching," "coherence," or
"measurement." Everything here is synthetic; no real system, no real
orders.

## Why this fixture exists (and why `pd-overflow` wasn't enough)

`pd-overflow` (this campaign's Task 3) widened `pd-pipeline` from 7 to
16 tasks specifically to make a faithful monolithic plan large enough
to exceed one model write. Its own honest size model landed at roughly
10k-20k plan tokens depending on step-granularity assumptions — a real,
breadth-driven increase over `pd-pipeline`, but well short of certifying
a crossing of the ~25k-32k single-response output budget the probe
exists to test. The T4 battery confirmed this the hard way: both
monolithic-arm overflow-control reps completed their plans in full (no
confirmed truncation). `pd-overflow` remains valuable as the campaign's
mid-size point (see its own `probe-design-notes.md`); it stays
untouched. This fixture (`pd-overflow-xl`) exists to actually CERTIFY
overflow — the property `pd-overflow` could not honestly claim.

## Structure: three cohesive subsystems, not padding

Every added module below is a concrete, individually implementable
requirement a real multi-warehouse order-fulfillment operation would
need — nothing is generated-to-be-long. The domain grows along the
seam a real service actually grows along: from "process an order" to
"also run day-to-day operations for the people processing it" to "also
move data in and out of the system in bulk."

1. **Order pipeline** (`pd-overflow`'s 16 modules, byte-for-byte
   unchanged): intake, validation, discounts, pricing, allocation,
   shipping, fulfillment, backorders, notifications, loyalty, returns,
   refunds, reporting, archiving, cancellation, sla.
2. **Operations & administration** (8 new modules): staff roles &
   permissions, an audit log, inventory adjustments, support tickets,
   API rate limits, warehouse shift coverage, manual order overrides,
   an operations dashboard.
3. **Import/export & reconciliation** (8 new modules): bulk CSV order
   import, a marketplace export feed, warehouse count reconciliation,
   accounting ledger sync, a carrier manifest, duplicate order
   detection, a vendor restock feed, vendor restock lead times.

**Real cross-subsystem touchpoints**, not three isolated silos:
`manual_override.py` (ops) consumes `staff_roles.role_can_perform` and
re-enforces the pipeline's own `MAX_LINE_ITEMS` cap before reprocessing
an order; `csv_import.py` (import) mirrors `intake.py`'s
`OrderIntakeError` parsing pattern and *also* re-enforces
`MAX_LINE_ITEMS` on a bulk-imported order; `reconciliation.py` and
`carrier_manifest.py` and `shift_coverage.py` all validate against
`orders.settings.WAREHOUSES` (already consumed by `reporting.py` in the
base pipeline — now four consumers of that one list, not one);
`shift_coverage.py`'s staffed-hours table and `carrier_manifest.py`'s
cutoff table describe the same three warehouses and SPEC.md states they
must stay consistent; `vendor_lead_times.py` (import) is the estimate
`backorders.py`'s (pipeline) exhausted-retry path would hand to a
customer; `ledger_sync.py` (import) maps the same order-status
vocabulary `notifications.py` and `cancellation.py` (pipeline) already
use.

## The three unlabeled probes (unchanged in kind from `pd-overflow`)

### 1. Settings.py micro-edit candidates (P4 / right-sizing instrument)

Six tiny, same-shape additions to the pre-existing `orders/settings.py`
— `pd-overflow`'s four (`NOTIFY_MAX_RETRIES`, `DEFAULT_REPORT_TIMEZONE`,
`ARCHIVE_GRACE_DAYS`, `RETURN_WINDOW_DAYS`) plus two new ones landing
naturally in the new subsystems: `AUDIT_LOG_RETENTION_DAYS = 90`
(operations) and `RECONCILIATION_TOLERANCE_CENTS = 500`
(import/export). Each reads as a one-line aside within its own module's
requirements, exactly as before.

**Observable:** unchanged `_pd_settings_disposition` logic in
`checks.sh` (reused verbatim from `pd-overflow`), emitting
`settings-micro-edits-touching-tasks`, `-dedicated-tasks`,
`-merged-tasks`.

### 2. One cross-cutting constant family, now spanning all three subsystems (P2 / coherence instrument)

`MAX_LINE_ITEMS = 12` is required, by SPEC.md's own text, in SIX
modules now — the pipeline's four (`orders/validation.py`,
`orders/pricing.py`, `orders/fulfillment.py`, `orders/allocation.py`)
plus one from each new subsystem: `orders/manual_override.py`
(operations — a manually reprocessed order is re-validated against the
same cap) and `orders/csv_import.py` (import/export — a bulk-imported
order is held to the same cap). This is the literal expansion the task
brief asked for: the SAME shared rule, now genuinely spanning
subsystem boundaries rather than living inside one.

**Observable:** `checks.sh` greps the FINAL CODE for `MAX_LINE_ITEMS` in
all six modules and emits each value plus a
`max-line-items-coherent: yes/no` line — the tolerant three-shape
extraction (bare / annotated / one-hop import) carried over unchanged
from `pd-overflow`'s T4 correction.

### 3. Simplest-thing / YAGNI probe (P4 instrument)

Unchanged from `pd-overflow` and `pd-pipeline`: `orders/pricing.py`'s
`CURRENCY = "USD"` constant with the same explicit "do not build a
currency-conversion layer" steer. `checks.sh`'s
`pricing-simplest-thing-signal` observable is identical.

## Size verification: does a faithful monolithic plan actually overflow?

**Requirement-density, directly countable in SPEC.md** (mechanical
counts — `grep -c '^## '` for module sections minus the four non-module
sections, `grep -oE` for the `` `name(args) -> Type` `` signature
pattern, `wc -c` for file size; the same method `pd-overflow`'s own
notes used, re-run here rather than assumed):

| | pd-pipeline | pd-overflow | pd-overflow-xl | xl / overflow |
|---|---|---|---|---|
| natural tasks (one per module) | 7 | 16 | **32** | 2.0x |
| distinct function signatures | 8 | 23 | **52** | 2.26x |
| SPEC.md file size (chars) | 5,241 | 15,553 | **31,027** | 2.00x |
| settings.py micro-edits | 3 | 4 | **6** | 1.5x |
| MAX_LINE_ITEMS consuming modules | 3 | 4 | **6** | 1.5x |
| subsystems | 1 | 1 | **3** | 3.0x |

(`pd-overflow`'s own notes reported 24 functions via the same regex;
re-running that exact command against the committed `pd-overflow`
SPEC.md today returns 23 — a pre-existing one-signature discrepancy in
that file's own count, most likely a manual miscount at the time, not a
change to the fixture. Left as-is; not this task's file to correct.
23 is used as the `pd-overflow` baseline throughout this table and the
model below so every ratio is apples-to-apples against a number
actually re-derived today.)

Task-count and SPEC-size both land at almost exactly 2.0x `pd-overflow`
— comfortably inside a doubling, driven by two genuinely new
subsystems of real breadth rather than by inflating the existing one.
Function-signature density lands higher (2.26x) because the two new
subsystems average more functions per module (1.81/module) than the
base pipeline (1.44/module) — operations and reconciliation logic
tends to need a lookup-table function plus a composing function per
concern, not just one.

**From requirement count to plan token count.** No API calls; this is
arithmetic, calibrated against `pd-overflow`'s own real, committed
calibration points (its `probe-design-notes.md`) plus one FRESH
calibration point drafted for this task specifically, to cover a shape
`pd-overflow`'s calibration never needed: a genuinely cross-subsystem
task whose implementation consumes another task's module.

**Reused directly from `pd-overflow`'s calibration** (maximal
bite-sized granularity — literal "each step is one action," a full
independent Step 1-5 TDD cycle per behavior, no bundling — the more
literal reading of the skill's own granularity rule, and the reading
`pd-overflow`'s own notes flagged as the harder-to-rule-out case):

- No-table, single-function, two-behavior task: **3,257 chars**
  (`pd-overflow`'s measured 1,670 bundled chars × the same project's
  measured 1.95x bundled→maximal inflation factor).
- Table-bearing, single-function, ~six-behavior task (shipping-style):
  **4,605 chars** (`pd-overflow`'s own DIRECT measurement, not derived).
- Small-table, four-function, eight-behavior task (validation-style):
  **6,063 chars** (3,109 bundled × 1.95x).

**New calibration point, drafted for this task** (retained under this
campaign's scratch area, not committed — same convention `pd-overflow`
used for its own three drafts): a full literal `writing-plans`-format
task for `orders/manual_override.py` (2 functions, 5 behaviors,
zero tables, but consuming another task's module — `staff_roles.py` —
and stating that dependency up front, the exact shape `pd-overflow`'s
own calibration never covered because its 16 modules were mostly
independent). Measured: **6,156 chars** — noticeably above what a
behavior/function-count-only scaling of the three anchors above would
predict (≈4,600-5,500 chars for a 2-function/5-behavior task with no
table), because of the added cross-module dependency note and the two
extra test behaviors this fixture's SPEC.md explicitly calls for
(authorization checked before the line-item cap, and each checked
independently). This is the direct, measured evidence for the "residual
uncertainty" `pd-overflow`'s own notes flagged and left unmodeled:
restated cross-task interface/dependency text measurably inflates a
task beyond what bare function/behavior counts predict, for the exact
subset of tasks (six of sixteen new modules here) that have one.

**Per-module estimate**, each of the 16 new modules mapped to the
nearest-shaped anchor (or the fresh cross-module anchor, for the two
modules — `manual_override.py`, `reconciliation.py`'s
`reconcile_warehouse_count` — that share its shape) and scaled by its
own behavior count where it differs from the anchor's:

| Module | Shape | Maximal chars |
|---|---|---|
| staff_roles.py | 1fn/5beh table | 3,838 |
| audit_log.py | 2fn/6beh table + settings edit | 6,527 |
| inventory_adjustments.py | 2fn/6beh table | 6,327 |
| support_tickets.py | 2fn/7beh table | 7,095 |
| rate_limits.py | 2fn/6beh table | 6,327 |
| shift_coverage.py | 2fn/6beh table + cross-module note | 6,627 |
| manual_override.py | 2fn/5beh cross-module (measured) | 6,156 |
| ops_dashboard.py | 2fn/6beh table | 4,770 |
| csv_import.py | parser (validation-style) + cap fn | 9,320 |
| export_feed.py | 2fn/6beh table | 6,327 |
| reconciliation.py | 3fn incl. cross-module | 9,892 |
| ledger_sync.py | 1fn/5beh table | 3,838 |
| carrier_manifest.py | 2fn/6beh table cross-module | 6,327 |
| duplicate_detection.py | 1fn/4beh no table | 3,931 |
| vendor_feed.py | parser (intake-mirroring) | 4,800 |
| vendor_lead_times.py | 2fn/6beh table + cross-module note | 6,577 |
| **new-subsystem total** | | **98,679** |

Subsystem A (unchanged content) reuses `pd-overflow`'s own maximal
task-content figure directly: 34,212 bundled chars × 1.95 = **66,713
chars** for its 16 tasks.

**Total task content (maximal):** 66,713 + 98,679 = **165,392 chars.**

**Header / Global Constraints doc:** `pd-overflow`'s was ~1,300 chars
bundled for a 3-module-wide constant family and a 16-entry task index.
This scenario's is wider on both axes — a 6-module constant family, 6
settings constants, a 32-entry task index, and a 3-subsystem
architecture description — estimated at ~2,400 chars bundled (a
proportional but sub-linear scale-up: most of the header is fixed
boilerplate that doesn't grow with task count). Maximal: 2,400 × 1.95 =
**4,680 chars.**

**Grand total (maximal bite-sized granularity):** 165,392 + 4,680 =
**170,072 chars ≈ 48,592 tokens** (at the same ~3.5 chars/token
`pd-overflow`'s own model used, for direct comparability).

## Result: CERTIFIED overflow, with margin

**≈48,600 estimated tokens vs. the ~25k-32k typical single-response
output budget** — exceeds the top of that band by roughly **1.5x**
(~16,600 tokens of margin over 32k), and clears the task's own ≥45k
target. This is a **2.46x** increase over `pd-overflow`'s own maximal
estimate (19,780 tokens) against a 2.26x increase in raw function
count — the extra ~9% comes from the measured cross-module-dependency
overhead (six of the sixteen new modules restate a dependency on
another task's module; `pd-overflow`'s sixteen modules mostly didn't
need to), not from any change in per-behavior verbosity assumptions.

**Why this should hold even under the SAME conservative methodology
that undershot for `pd-overflow`.** `pd-overflow`'s honest model (10k-
20k tokens) turned out directionally right but did not, in the T4
battery, produce confirmed truncation — real agent output apparently
ran at or below that estimate's low end for those two reps, not above
it. Nothing here assumes real output will run richer than modeled;
the margin is structural: even if `pd-overflow-xl`'s real plan authoring
comes in as far below this model as `pd-overflow`'s did (this model's
low end, using bundled rather than maximal-bite-size granularity
throughout, is 165,392÷1.95 + 4,680÷1.95 ≈ **87,215 chars ≈ 24,919
tokens** — still short of 32k on its own), the true unknown this
fixture cannot resolve without a real rep is exactly where between
"bundled" and "maximal" a real session's granularity choice falls.
What changed since `pd-overflow`: requirement density roughly doubled
(2.0x tasks/chars, 2.26x functions) while this model's TOKEN estimate
grew 1.95x-2.46x depending on granularity assumption — landing this
fixture's own bundled-granularity floor (~24,900 tokens) already above
`pd-overflow`'s own maximal-granularity ceiling (19,780 tokens), and
its maximal-granularity estimate (~48,600 tokens) at roughly 1.5x the
budget's own upper bound. Both ends of the plausible range sit closer
to or above the 32k line than `pd-overflow`'s did at either end. This
is disclosed as the honest bound of what arithmetic alone can certify;
whether a real session lands at the bundled floor, the maximal ceiling,
or (as `pd-overflow`'s T4 reps suggest is plausible) below both, remains
for an actual observed battery to resolve — flagged here as a residual
uncertainty, not papered over.

## Validation (no container spend)

Per the same controller ruling `pd-pipeline`, `pd-overflow`,
`cp-x1-edit-existing`, and `cp-x10-consistency` operated under, this
task spends no containers or API budget on real reps.
`campaigns/cost-pathologies/validate_pd_overflow_xl.py` and
`campaigns/cost-pathologies/test_pd_overflow_xl_fixture.py` construct
ONE plausible post-state under `campaigns/cost-pathologies/fixtures/
pd-overflow-xl-outcomes/directory-tasks/` — a plan directory (manifest +
constraints doc + one file per task) with all 32 modules present, the
six settings.py micro-edits split so THREE fold into their module's own
task (merged disposition: notify-max-retries, return-window-days,
audit-log-retention-days) and THREE are spun off as their own dedicated
one-line tasks (dedicated disposition: default-report-timezone,
archive-grace-days, reconciliation-tolerance-cents) — mixed across
BOTH the pipeline and the new subsystems so a single tree exercises
both branches of `_pd_settings_disposition` without needing two full
32-module trees — `MAX_LINE_ITEMS` coherent at 12 across all six
consuming modules, and simple (non-abstracted) pricing.

This tree passes its own `pytest` in full. `validate_pd_overflow_xl.py`
reuses `validate_pd_pipeline.py`'s module-agnostic helpers (`plan_files`,
`plan_shape`, `task_count`, `settings_disposition`, `module_constant`,
`pricing_overbuild_hits`, `run_checks_sh_instruments`,
`parse_emit_lines`) via import, the same way `validate_pd_overflow.py`
does — and additionally imports `validate_pd_overflow` itself for its
already-generalized `run_checks_sh_instruments` wrapper pattern, only
widening the two module lists (`MAX_LINE_ITEMS_MODULES` to six entries,
`SETTINGS_CONSTANT_NAMES` to six entries, `MODULE_FILES` to all 32) —
per this task's instruction to follow `validate_pd_overflow.py`'s
updated (post-T4) approach of actually exercising `checks.sh` itself via
the stubbed-`command-succeeds` harness, not a from-scratch
reimplementation of its bash/awk logic.
