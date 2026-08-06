# Seeded-trap ledger — p3-integration-trap

Answer key for the P3 walking-skeleton battery's discriminating
fixture (plan-decomposition campaign; specified-for-the-future in
`logs/2026-08-03-plan-decomposition-campaign.md`, "P3/P4 DISPOSITION"
entry, 2026-08-05). NEVER surfaced to the Coding-Agent or the
Gauntlet-Agent — `story.md` and `fixtures/docs/metrics-pipeline-
design.md` never use the words "trap," "mismatch," "walking
skeleton," "slice," "integration order," "rework," or "measurement,"
and the story's pinned replies refuse to resolve or acknowledge any
inconsistency the session raises ("use your best judgment…").
Everything here is synthetic; no real hosts.

## Why this fixture exists

The walking-skeleton hypothesis (P3: vertical-slice-first task
ordering beats horizontal layering) was parked INCONCLUSIVE-BY-CEILING
on 2026-08-05: every pd-pipeline / pd-overflow cell completes with
full scope and passing post-checks regardless of plan shape, so a P3
arm had no outcome variance to reduce — a battery would have measured
plan-artifact aesthetics only. The disposition specified what a
discriminating fixture needs: a spec with a seeded INTEGRATION TRAP —
two subsystems whose contract looks compatible layer-by-layer but
fails when composed, so horizontal-layer plans discover it at the
final task (expensive rework) and walking-skeleton plans at slice one
(cheap). Outcome metric: rework after the first integration failure.

This fixture is that spec: a metrics COLLECTOR (writes samples to a
JSONL stream) and a REPORTER (reads, validates, aggregates the same
stream), each specified in its own section with locally-sensible
detail, whose stream-contract framings quietly disagree. It is a
plan-AUTHORING scenario in the pd-pipeline mold — the session receives
the spec, writes its own plan with writing-plans, and executes it with
subagent-driven-development in the same session — because P3 is a
writing-plans rule and only an authored plan can carry a task
ordering.

## Trap refinement (why not the sketch's naive-local-vs-UTC trap)

The disposition's example trap — collector stamps naive local
wall-clock time, reporter windows by UTC — is INERT in the runtime
environment: the evals container sets no TZ (checked
`evals/container/Dockerfile`; no `ENV TZ`, no tzdata configuration),
so container-local time IS UTC and naive-local vs UTC-epoch values
never diverge. A trap whose firing depends on the host's timezone is
non-deterministic across environments in the wrong direction (it
would fire on a developer laptop and vanish in the battery). The seed
was therefore refined to two representation/scope mismatches that are
deterministic everywhere, while keeping the sketch's exact framing
vocabulary (collector "timestamps samples at write time" in
wall-clock form; reporter "windows samples by UTC epoch minutes with
monotonic sequence validation"):

## The two tripwires

Both live in the shared stream-file contract (`name`, `value`, `seq`,
`ts` — field NAMES are common ground in the spec's Stream file
section; field SEMANTICS are defined only inside each subsystem's own
section, which is where they disagree).

### TRIPWIRE-TS — timestamp representation (string vs integer)

- **Collector section says:** `ts` is the current wall-clock time
  "written in the human-readable form `YYYY-MM-DDTHH:MM:SS` (i.e.
  `time.strftime("%Y-%m-%dT%H:%M:%S")`) so an operator tailing the
  raw stream can read timestamps directly." Locally sensible
  (operator readability); produces a STRING.
- **Reporter section says:** "Reports are windowed by UTC epoch
  minute, so every `ts` must be an integer count of epoch seconds,
  and no earlier than 2020-01-01 UTC (`1577836800`)" — otherwise
  `SampleStreamError(f"line {n}: invalid timestamp {ts!r}")`. Locally
  sensible (windowing needs arithmetic; the floor is a corruption
  guard); demands an INT.
- **Composed:** the first real collector-written line fails reporter
  validation loudly — the string is not an int. Deterministic, in
  any timezone.

### TRIPWIRE-SEQ — sequence scope (per-metric vs global)

- **Collector section says:** `seq` is "the sample's ordinal within
  its own metric's history … counted independently per metric name."
  Locally sensible (per-metric gap detection).
- **Reporter section says:** "`seq` values must be strictly
  increasing in file order across the stream" — otherwise
  `SampleStreamError(f"line {n}: sequence regression at seq
  {seq!r}")`. Locally sensible (interleaved-writer/torn-write
  detection).
- **Composed:** any stream alternating two metric names (`cpu`,
  `mem`, `cpu`, …) yields `seq` 1, 1, 2, … — a "regression" at line
  2. The spec's mandated end-to-end test alternates two metric names
  for exactly this reason (see Reachability below). Deterministic.

Two independent tripwires make the trap robust: a shallow fix of one
field still fails loudly on the other (verified below), so a single
lucky harmonization cannot silently defuse the fixture.

## Why each side is individually green

Each section is complete, self-consistent, and unit-testable in
isolation — the natural horizontal-layer implementation of either
module, tested per its own section's text, passes:

- Collector unit tests (per its section): per-metric seq ordinals,
  strftime-shaped `ts`, append/flush behavior, ValueError cases. All
  consistent with the collector section alone.
- Reporter unit tests (per its section): hand-built streams with
  integer epoch-second `ts` ≥ 1577836800 and globally increasing
  `seq` (the only fixtures that satisfy the reporter's own stated
  contract), plus rejection cases. All consistent with the reporter
  section alone.

Nothing forces a layer implementer to run real collector output
through the reporter until the end-to-end test exists — which is why
WHEN that test gets built is the whole experiment.

## Reachability (why composition cannot be skipped)

The spec's Testing section mandates `tests/test_end_to_end.py`: "a
`Collector` records at least four samples alternating between two
metric names (`cpu`, then `mem`, then `cpu`, then `mem`) … then
`generate_report` runs over that same file," with the closing line
"Real collector output flowing through the real reporter is this
system's definition of done." This is ARM-NEUTRAL — both plan shapes
must eventually satisfy it; only its position in the task order
varies — and it guarantees (a) composition happens in every completed
rep, and (b) the alternating two-metric stream trips TRIPWIRE-SEQ
even if TRIPWIRE-TS was independently harmonized. `story.md`'s
pinned replies are the pd-pipeline class-routed set, so a session
that surfaces the contradiction mid-run gets "use your best judgment,
whatever fits best with the rest of the code" — never a resolution
and never an acknowledgment that the doc is inconsistent.

## Worked repro (run 2026-08-06, this task's own validation)

Reference implementations of each section's natural isolated reading
(scratchpad `p3-repro/`; not shipped in `fixtures/`):

1. **Layer-local green:** collector unit tests (4) + reporter unit
   tests (5), each written strictly from its own section:
   `python3 -m pytest tests/test_collector.py tests/test_reporter.py -q`
   → `9 passed`.
2. **Composed, loud (TRIPWIRE-TS):** the spec's own e2e test:
   `python3 -m pytest tests/test_end_to_end.py -q` →
   `FAILED … metrics.reporter.SampleStreamError: line 1: invalid
   timestamp '2026-08-06T14:37:57'`.
3. **Shallow fix still loud (TRIPWIRE-SEQ):** patch the collector's
   `ts` to `int(time.time())` and change nothing else; rerun the e2e
   test → `FAILED … metrics.reporter.SampleStreamError: line 2:
   sequence regression at seq 1`.
4. **Full harmonization completes (arm-neutral ceiling check):**
   collector writes `int(time.time())` + a single global counter →
   e2e + reporter tests `6 passed`. (The collector-side resolution
   rewrites the collector's own per-metric-seq unit test; a
   reporter-side resolution — parse the string form, validate seq
   per metric — is equally legitimate. Both arms can finish; the
   metric is cost, not completion.)

## Legitimate resolutions (the AC accepts any coherent one)

- Collector-side: write integer epoch seconds and a global stream
  counter (deviates from the collector section's letter).
- Reporter-side: parse `YYYY-MM-DDTHH:MM:SS` (declaring the stamp
  UTC) and validate monotonicity per metric name (deviates from the
  reporter section's letter).
- Split: any mix that makes the composed pipeline work.

Story ACs are deliberately neutral: "The two modules agree on the
stream contract by the end — whichever way the agent chose to make
them agree is acceptable." A DEGENERATE resolution — deleting the
reporter's validation so anything aggregates — is instrumented
(`p3-validation-retained`: count of `raise SampleStreamError` sites
in the final reporter.py; 0 = validation dropped) and hand-read, not
gated.

## What the battery measures (instrument map)

Primary endpoint — rework after the first integration failure — is a
mechanically-assisted hand-read composed from emit-only lines
(`checks.sh` post() via `instruments.py`; every line `true # p3-…`,
never a gate):

- Plan shape: `p3-first-task-shape` (slice vs layer vs unknown,
  heuristic over the authored plan's Task 1: slice = names both
  subsystems or an e2e marker; unknown on ambiguity),
  `p3-first-e2e-task-index`, `p3-plan-shape` (files/task count),
  `p3-trap-in-plan` (plan-time discovery: contract-conflict language
  near ts/seq vocabulary).
- Integration timing: `p3-first-e2e-run-step` (trajectory step first
  naming test_end_to_end), `p3-first-e2e-commit-ordinal`,
  `p3-trap-sighting-step` (first trajectory step mentioning
  `SampleStreamError` — the class name exists only in this fixture,
  but innocent mentions occur while writing reporter code, so the
  failure MOMENT is a hand-read anchored by this line).
- Rework ingredients: `p3-commit-timeline`, `p3-collector-commits` /
  `p3-reporter-commits` (per-file totals, first-touch ordinal,
  re-touches after the first e2e commit — with a file born after the
  e2e commit explicitly marked, since skeleton-style widening
  legitimately touches subsystem files after the slice exists; git
  alone cannot distinguish planned widening from unplanned rework,
  which is why the endpoint is a hand-read over these plus the
  trajectory, per the campaign's standing mechanically-assisted
  hand-read discipline).
- Resolution: `p3-trap-resolved` (live probe: a real `Collector`
  records cpu/mem alternating in a temp dir, then `generate_report`
  over that file — `ok` means composition genuinely works in the
  final tree), `p3-ts-convention` / `p3-seq-convention` (which side
  won), `p3-validation-retained`.
- Covariates: `p3-served-model` (census rule), `p3-dispatches`,
  `p3-traj-steps`, `p3-total-commits`,
  `p3-main-advanced-past-seed`.

## Known limits (disclosed up front)

- **Plan-time discovery defeats the timing contrast, and that is
  data:** a session that reads the whole spec and harmonizes the
  contract in the plan itself never composes-and-fails. The base2
  cells measure this base rate first; if control sessions already
  write skeleton-ish plans or resolve the trap at plan time
  (`p3-trap-in-plan: yes` + `p3-first-e2e-task-index` ≈ 1), the
  battery is INCONCLUSIVE-BY-CEILING and must say so (pre-registered
  expectation, not a surprise).
- The plan-shape heuristic is text-matching over task sections;
  scaffolding-first plans and unconventional task headers grade
  `unknown` — hand-read every unknown.
- `p3-first-e2e-run-step` keys on the literal name
  `test_end_to_end`; a session that names the mandated file
  differently (deviating from the spec's letter) grades `unknown`
  there and in `p3-first-e2e-commit-ordinal` (the commit scan
  matches `e2e|end_to_end` in tests/ paths, slightly broader).
- The live probe assumes the spec-pinned API surface
  (`Collector(path).record(name, value)`,
  `generate_report(path)`); a renamed API grades
  `probe=import-error…` — hand-read, never guessed.
