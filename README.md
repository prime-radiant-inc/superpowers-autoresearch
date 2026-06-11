# superpowers-autoresearch

Machinery for running autoresearch loops against superpowers skill behavior:
hypothesis logs, micro-test harnesses, transcript mining, and report
generators. Born from the 2026-06-10/11 SDD cost campaign (46 runs) and
build-loop autoresearch (25 experiments).

## The loop

1. **Hypothesis log first.** Every experiment pre-registers a prediction in a
   dated log under `logs/`. Negative results get equal billing. Verdicts cite
   evidence. Durable results also copy to superpowers-evals
   `docs/experiments/`.
2. **Method tiers, cheapest first:**
   - **MINE** — answer from existing run artifacts (free). Scripts in `mining/`.
   - **MICRO** — one API call per sample, guidance variant in realistic
     context, 5+ reps, ALWAYS a no-guidance control (~$0.15–0.50/sample).
     Harnesses in `harnesses/`.
   - **FULL** — quorum eval runs via superpowers-evals (~$7–15 each). Only
     when cheaper tiers can't answer.
3. **Quality gates guard config changes** (planted-defect scenario et al.).
   Pass/fail alone is insufficient — read the gauntlet reasoning; runs pass
   while components fail.

## Non-negotiable methodology (each rule bought with a real mistake)

- **Manually inspect every automated score match.** Three scoring bugs in one
  campaign: a grep counting template echoes as findings, a harness that never
  inlined the diff it claimed to test, a regex blind across newlines.
- **No-guidance control in every micro battery.** It exposed both a backfire
  (prohibition worse than nothing) and a working prohibition.
- **Zero-variance across reps is the signature of guidance that landed.**
- **Single-run deltas under ~20% are noise** on full eval runs.
- **Fixture realism bounds everything:** hand-written fixture plans executed
  at ~2× the cost of real skill output. Generate fixtures with the system
  under test.
- **If the baseline won't fail, stop** — inconclusive-by-zero ≠ pass; don't
  author guidance for failures you can't elicit.

## Layout

- `harnesses/` — micro-test runners (self-contained Python, stdlib only;
  parameterized via env: MODEL, SPEC_FILE, OUT_DIR, VARIANTS). Caching per
  (variant, rep): reruns fill gaps.
- `mining/` — transcript/economics miners for quorum run dirs.
- `fixtures/` — design specs used by plan-generation micros.
- `logs/` — dated hypothesis logs + run mappings (the working records).
- `reports/` — generated HTML narratives/dashboards + generators.
- `campaigns/<name>/` — per-campaign battery: prompts, runner, researcher
  instructions, results.

## Requirements

`ANTHROPIC_API_KEY` in env for micros. FULL runs go through a
superpowers-evals checkout (`uv run quorum run …` from its evals dir —
never `cd` away mid-command; SUPERPOWERS_ROOT points at the skill-config
clone under test, which must NOT be edited while a run reads it).
