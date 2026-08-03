# Probe design notes — pd-overflow

Ground truth for the plan-decomposition campaign's return-window
overflow probe (design doc
`docs/2026-08-03-plan-decomposition-campaign-design.md`, "Fixtures and
instruments" item 2; task brief
`.superpowers/sdd/2026-08-03-plan-decomposition-campaign/task-3-brief.md`).
NEVER surfaced to the Coding-Agent — `story.md` and `fixtures/SPEC.md`
name no probe, no plan-size or file-splitting question, and never use
the words "decomposition," "overflow," "batching," "coherence," or
"measurement." Everything here is synthetic; no real system, no real
orders.

## Why this fixture exists

`pd-pipeline` (Task 1) is a 7-task, 8-function pipeline whose faithful
monolithic plan comfortably fits in one write (see that scenario's own
sizing below) — a P1 (plan-as-directory) battery run on it alone would
never actually observe the return-window-overflow failure Jesse
reported, because the control arm (monolithic plan) never hits the
wall the treatment (per-task files) is meant to fix. This fixture
widens the SAME service family (order fulfillment) with real,
concretely-specified breadth — more modules, more integrations, more
exact-value edge-case tables — so that a faithful monolithic plan is
large enough to plausibly exceed a single model write. It keeps
`pd-pipeline`'s same three unlabeled probe classes (below) so the
existing scorers (`score_pd_planshape`, `score_pd_dupdiscovery`,
`score_pd_coherence`) need no logic changes, only the wider module
lists `checks.sh` now emits against.

## The three unlabeled probes (unchanged from pd-pipeline)

### 1. Settings.py micro-edit candidates (P4 / right-sizing instrument)

`SPEC.md` asks for FOUR tiny, same-shape additions to the pre-existing
`orders/settings.py` — `NOTIFY_MAX_RETRIES = 3` (notifications),
`DEFAULT_REPORT_TIMEZONE = "UTC"` (reporting), `ARCHIVE_GRACE_DAYS = 7`
(archiving), and `RETURN_WINDOW_DAYS = 30` (returns) — one more than
pd-pipeline's three, a natural consequence of this scenario's added
returns subsystem, not a deliberate change to the probe's shape. Each
reads as a one-line aside within its own module's requirements.

**Observable:** unchanged `_pd_settings_disposition` logic in
`checks.sh`, emitting `settings-micro-edits-touching-tasks`,
`-dedicated-tasks`, `-merged-tasks`.

### 2. One cross-cutting constant family (P2 / coherence instrument)

`MAX_LINE_ITEMS = 12` is required, by SPEC.md's own text, in FOUR
modules now — `orders/validation.py`, `orders/pricing.py`,
`orders/fulfillment.py`, and `orders/allocation.py` (new: this
scenario's warehouse-allocation module also enforces the cap before
allocating) — one more consuming module than pd-pipeline's three,
again a natural consequence of real added breadth, not a shape change
to the probe.

**Observable:** `checks.sh` greps the FINAL CODE for `MAX_LINE_ITEMS`
in all four modules and emits each value plus a
`max-line-items-coherent: yes/no` line.

### 3. Simplest-thing / YAGNI probe (P4 instrument)

Unchanged from pd-pipeline: `orders/pricing.py`'s `CURRENCY = "USD"`
constant with the same explicit "do not build a currency-conversion
layer" steer. `checks.sh`'s `pricing-simplest-thing-signal` observable
is identical.

## Real breadth, not padding

Every added module is a concrete, implementable requirement a real
multi-warehouse order-fulfillment-and-returns service would need:
volume discounts, per-zone shipping cost, warehouse capability
matching, backorder retry scheduling, per-channel notification retry
tuning, loyalty points, a return window, restocking fees, order
cancellation, and delivery SLAs. Nine of the sixteen tasks' functions
carry an embedded exact-value lookup table (discount tiers, shipping
cost grid, warehouse/zone/capability tables, backorder retry schedule,
notification channel retries, loyalty multipliers, restocking fee
tiers, delivery SLA grid, SKU category prefixes) — SPEC.md states every
value in these tables explicitly; none are left for the session to
invent.

## Size verification: does a faithful monolithic plan actually get big?

**Requirement-density, directly countable in SPEC.md:**

| | pd-pipeline | pd-overflow | ratio |
|---|---|---|---|
| natural tasks (one per module) | 7 | 16 | 2.3x |
| distinct function signatures SPEC.md declares | 8 | 24 | **3.0x** |
| SPEC.md file size (chars) | 5,241 | 15,553 | **2.97x** |
| settings.py micro-edits | 3 | 4 | 1.3x |
| MAX_LINE_ITEMS consuming modules | 3 | 4 | 1.3x |
| functions with an embedded exact-value table | 0 | 9 | n/a |

(Function count via `grep -oE '`[a-z_]+\([^)]*\) -> [A-Za-z]+`'` against
both SPEC.md files — a mechanical, reproducible count, not an
estimate.)

The requirement-density ratio (function count, SPEC.md size) lands at
almost exactly 3.0x, right at the bottom of the task brief's 3-5x
target band — grounded in real, concretely-specified breadth (more
modules, more integrations, nine exact-value tables), not padding.

**From requirement count to plan token count.** The task brief permits
no API calls, so this is arithmetic, calibrated against two real
artifacts rather than guesswork:

1. `writing-plans`' own worked example (`SKILL.md` lines 81-126): one
   function, one behavior, a full Files/Interfaces header, and one
   complete Step 1-5 TDD cycle = 1,109 characters.
2. A real plan already committed in this repo in this campaign's own
   convention, `scenarios/cp-x10-consistency/fixtures/docs/superpowers/
   plans/job-queue-plan.md` (6 tasks, 20 distinct test-behavior
   mentions, 7,035 characters) — written in a lighter prose-
   implementation style (`**Implementation:** ...` paragraphs), not
   `writing-plans`' literal-code-per-step format.

Three representative tasks were drafted in full, literal
`writing-plans` format against this scenario's own spec content
(retained under this campaign's scratch area, not committed) to
calibrate directly rather than extrapolate from the bare `SKILL.md`
snippet alone:

- A single-function, two-behavior task (`fulfillment`-style,
  no table): 1,670 characters.
- A single-function, six-behavior table-bearing task (`shipping`-
  style, one 3x3 rate grid): 2,363 characters bundled (all six test
  cases in one "write the failing tests" step); **4,605 characters**
  when each behavior gets its own full TDD cycle instead (the more
  literal reading of "Bite-Sized Task Granularity: each step is one
  action") — a measured **1.95x inflation** between the two granularity
  assumptions.
- A four-function, eight-behavior task with one small table
  (`validation`-style): 3,109 characters bundled.

Extrapolating per-task character counts across all 7 / 16 tasks from
these three calibration points (proportional to each task's real
function and behavior count, table-bearing tasks weighted at the
measured shipping-task rate) gives:

| | pd-pipeline (bundled) | pd-overflow (bundled) | ratio |
|---|---|---|---|
| task content | ~12,510 chars | ~34,212 chars | 2.73x |
| + plan header/Global Constraints | ~740 chars | ~1,300 chars | |
| **total** | **~13,250 chars (~3,790 tokens)** | **~35,510 chars (~10,145 tokens)** | **2.68x** |

Applying the measured 1.95x bundled→maximally-bite-sized inflation
factor uniformly (the more literal reading of the skill's own
granularity rule) gives **~7,390 tokens** (pd-pipeline) vs **~19,780
tokens** (pd-overflow) — same 2.68x ratio, at roughly 3.5 chars/token.

**Honest conclusion, not overclaimed.** Requirement-density (function
count, SPEC.md size) lands at 3.0x, matching the brief's target. The
resulting *plan-token* estimate, calibrated against directly-drafted
representative tasks, lands at roughly 2.7x rather than 3.0x — because
richer per-task function counts (pd-overflow averages 1.5
functions/task vs pd-pipeline's 1.14) amortize the fixed per-task
Files/Interfaces header over more content, a real, structural
suppression of the naive requirement-count ratio, not an error. Under
either step-granularity assumption modeled here, the resulting
estimate (~10k-20k tokens) is a substantial, real-breadth-driven
increase but does **not**, by this arithmetic alone, certify crossing
the 25k-32k "typical single-response output budget" the brief names.
Closing that residual gap plausibly requires real-world verbosity this
model does not capture — per-task rationale prose, restated
`Interfaces: Consumes` contracts for the genuine cross-task
dependencies this scenario's integrations require (pricing consuming
discounts, allocation consuming validation's SKU category, fulfillment
consuming allocation and backorders, refunds consuming returns'
window, reporting consuming settings.WAREHOUSES) that pd-pipeline's
mostly-independent modules never needed to restate, and a plan-level
testing/dependency-order section a 16-task plan plausibly accretes
that a 7-task one would not. None of this is verified without an
actual observed agent write, which is out of scope for this
validation. This is flagged as a residual uncertainty in the task
report rather than papered over with false precision.

## Validation (no container spend)

Per the same controller ruling `pd-pipeline`, `cp-x1-edit-existing`,
and `cp-x10-consistency` operated under, this task spends no
containers or API budget on real reps.
`campaigns/cost-pathologies/validate_pd_overflow.py` and
`campaigns/cost-pathologies/test_pd_overflow_fixture.py` construct ONE
plausible post-state under `campaigns/cost-pathologies/fixtures/
pd-overflow-outcomes/directory-tasks/` — a plan directory (manifest +
constraints doc + one file per task), the four settings.py micro-edits
split so TWO are folded into their module's own task (merged
disposition: notify-max-retries, return-window-days) and TWO spun off
as their own dedicated one-line tasks (dedicated disposition:
default-report-timezone, archive-grace-days) — deliberately mixed so a
single tree exercises both branches of `_pd_settings_disposition`
rather than needing two full trees the way pd-pipeline's validation
did — `MAX_LINE_ITEMS` coherent at 12 across all four consuming
modules, and simple (non-abstracted) pricing.

This tree passes its own `pytest` in full. The detectors reuse
`validate_pd_pipeline.py`'s module-agnostic helpers (`plan_files`,
`plan_shape`, `task_count`, `settings_disposition`,
`pricing_overbuild_hits`, and the renamed-public `module_constant`)
directly via import rather than reimplementing them — only the P2
coherence check needed a thin wrapper generalized to four module paths
instead of three.
