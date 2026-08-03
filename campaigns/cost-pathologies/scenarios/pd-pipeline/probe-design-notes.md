# Probe design notes — pd-pipeline

Ground truth for the plan-decomposition campaign's pipeline fixture
(design doc `docs/2026-08-03-plan-decomposition-campaign-design.md`,
Task 1). NEVER surfaced to the Coding-Agent — `story.md` and
`fixtures/SPEC.md` name no probe, no task-sizing question, and never
use the words "decomposition," "batching," "coherence," "dedupe," or
"measurement." Everything here is synthetic; no real system, no real
orders.

## Why this fixture exists

Unlike `cp-x10-consistency` (a pre-written plan the session only
executes), this fixture is an AUTHORING+EXECUTION pipeline: the
session receives `SPEC.md`, writes its own plan with `writing-plans`,
then executes it with `subagent-driven-development` in the same
session. This is the fixture class the plan-decomposition campaign's
P1–P4/K1/D1 axes need — authoring-side arms (plan-as-directory,
plan-time coherence gate, walking skeleton, radical right-sizing)
can only be tested against a session that writes its own plan.

## The three unlabeled probes

### 1. Three micro-edit candidates (P4 / right-sizing instrument)

`SPEC.md` asks for three tiny, same-shape additions to the
pre-existing `orders/settings.py` — `NOTIFY_MAX_RETRIES = 3` (in the
notifications section), `DEFAULT_REPORT_TIMEZONE = "UTC"` (in the
reporting section), and `ARCHIVE_GRACE_DAYS = 7` (in the archiving
section). Each reads as a one-line aside within its own module's
requirements, not as a batch of three identical asks — nothing in
SPEC.md groups them or calls them out as small.

**What right-sizing predicts:** a well-sized plan folds each constant
into its own module's task (settings.py touched alongside
notifications.py / reporting.py / archiving.py in the same task) —
zero extra tasks. An over-decomposed plan spins up a dedicated
one-line task per constant (settings.py touched ALONE in three
separate tasks) — three extra tasks, three extra dispatches, for work
that has no independent test cycle of its own.

**Observable:** `checks.sh`'s `_pd_settings_disposition` walks the
plan text (Task-header or per-file boundaries) and classifies each
task/file that touches `orders/settings.py` as *dedicated* (settings.py
is the only `orders/*.py` file it touches) or *merged* (settings.py
plus another module file). Emitted as
`settings-micro-edits-touching-tasks`, `-dedicated-tasks`,
`-merged-tasks`.

### 2. One cross-cutting constant family (P2 / coherence instrument)

`MAX_LINE_ITEMS = 12` is required, by SPEC.md's own text, in THREE
modules — `orders/validation.py`, `orders/pricing.py`, and
`orders/fulfillment.py` — framed explicitly as one shared business
rule ("all three must agree on exactly what the cap is"), not as
three independent decisions the way `cp-x10-consistency`'s seeded
defects were. This is the opposite failure mode from cp-x10: there,
the PLAN itself already baked in a contradiction a reviewer had to
notice; here, the SPEC states one true value, and the risk is that
the session's OWN plan (authored per-task, dispatched to independent
implementers who each see only their own task) lets the shared value
drift across three task briefs it wrote itself.

**What the coherence gate predicts:** a plan with a shared-constants
doc or a plan-time consistency check keeps all three at 12. A plan
that treats each module's brief as an independent unit (no
cross-task constraint propagation) risks divergence despite the spec
never asking for one.

**Observable:** `checks.sh` greps the FINAL CODE (not the plan text)
for `MAX_LINE_ITEMS` in all three modules and emits each value plus a
`max-line-items-coherent: yes/no` line.

### 3. Simplest-thing / YAGNI probe (P4 instrument)

`SPEC.md`'s pricing section explicitly names the temptation and asks
for the plain thing anyway: a `CURRENCY = "USD"` constant, with an
explicit "do not build a currency-conversion layer, a currency
registry, or any pluggable-currency abstraction" — multi-currency
support is called out as a future roadmap item, out of scope now.

**What it predicts:** despite the explicit steer, an over-engineering-
prone plan/implementation may still grow a currency abstraction
(a `Currency` class hierarchy, a registry, a strategy pattern) that
the spec asked it not to build.

**Observable:** `checks.sh` greps `orders/pricing.py` for abstraction
markers (`class .*Currency`, `CurrencyRegistry`, `SUPPORTED_CURRENCIES`,
`abstractmethod`, `Protocol[`, `CurrencyConverter`) and emits
`pricing-simplest-thing-signal: overbuilt (<n> marker(s))` or `simple
(0 markers)`.

## Natural decomposition size

Seven modules (`intake`, `validation`, `pricing`, `fulfillment`,
`notifications`, `reporting`, `archiving`) each need their own file,
tests, and verification step — a natural one-task-per-module plan
lands at 7 tasks. Folding the three settings.py micro-edits into their
module's task keeps it at 7; spinning each off as its own task pushes
it to 10 — both ends of SPEC.md's target 6–10 natural task range are
real, reachable outcomes depending on how a plan is authored, not
fixture artifacts.

## Validation (no container spend)

Per the same controller ruling `cp-x1-edit-existing` and
`cp-x10-consistency` operated under, this task spends no containers or
API budget on real reps. `campaigns/cost-pathologies/
validate_pd_pipeline.py` and `campaigns/cost-pathologies/
test_pd_pipeline_fixture.py` construct two synthetic post-states under
`campaigns/cost-pathologies/fixtures/pd-pipeline-outcomes/` —

- `monolithic-layered/`: a single plan file, tasks in per-module
  (layer) order, the three settings.py edits folded into their
  module's own task (merged disposition), `MAX_LINE_ITEMS` coherent at
  12 everywhere, and simple (non-abstracted) pricing.
- `directory-skeleton/`: a plan directory (manifest + constraints doc +
  one file per task), a walking-skeleton-style first task followed by
  per-module widening tasks, the three settings.py edits as three
  dedicated one-line tasks (over-decomposed disposition),
  `MAX_LINE_ITEMS` INCOHERENT (fulfillment diverges to 10), and an
  overbuilt (currency-registry) pricing module.

Both trees pass their own `pytest` in full — the seeded divergences
are invisible to each module's own unit tests, the same property that
made `cp-x10-consistency`'s defects invisible to per-task review.
Reimplementing `checks.sh`'s detection logic in Python (mirroring
`validate_x10_fixture.py`'s own approach for its scenario), the
validation proves every emitted observable fires correctly and
differs between the two trees exactly as designed above.
