# CLAUDE.md-Lift Campaign Log (2026-08-03)

Append-only; corrections as dated entries. Standing discipline per the
plan-decomposition log header, plus this campaign's privacy rule: unit
verbatim text lives only in the external corpus; public artifacts use
IDs + paraphrases. Design: docs/2026-08-03-claudemd-lift-campaign-design.md.

## 2026-08-03 — Harness complete; live smoke PASS

Harness reviewed (2 Important grader-validity findings fixed across two
adversarially-verified fix rounds; privacy/isolation/secret-redaction
independently verified; grader-noun boundary rulings recorded in the
plan-decomposition ledger). Live smoke: 1 rep (nonexistent-flag ×
empty arm) end-to-end — real headless session, transcript captured,
grader ran, no errors. Smoke row moved to results-smoke.jsonl,
excluded from analysis.

## 2026-08-03 — Tier-1 sweep pre-registration

**Cells:** 8 probes × {empty, unit:<mapped>} × n=8 (128 reps; the
probe↔unit map is campaigns/claudemd-lift/README.md's table).
Model/session: the claude CLI session default; --max-turns 15;
isolation per the runner's header (throwaway HOME + /tmp workdir —
no CLAUDE.md ancestry).

**Reachability:** the unit text IS the workdir CLAUDE.md — the ambient
channel under test; reachable by construction.

**Criteria (per probe):** the pre-registered pass_signal direction in
the README table. A unit screens POSITIVE when its unit-cell
pass-signal rate separates from its empty-cell rate by more than the
empty-vs-empty noise (the empty cells across probes provide the shared
noise picture; exact separation threshold intentionally coarse at
screening tier — Tier 2 does rigor). INCONCLUSIVE-BY-CEILING if an
empty cell already saturates the desired behavior (no headroom);
recorded per-probe. Grader-edge hand-check rule: any
flawed-plan-pressure transcript using engine/cursor/sqlite-object
nouns is hand-verified (accepted grader boundary).

**Est. cost:** 128 short sessions ≈ $25-65 (tier-1 budget $40-80).

## 2026-08-03 — Tier-1 sweep VERDICT: zero units screen positive; ceiling dominates

128/128 reps, zero errors. Per-probe (pass-signal rates, empty vs
unit):

| probe | empty | unit | verdict |
|---|---|---|---|
| flawed-plan-pressure | 8/8 | 8/8 | CEILING |
| mock-the-bug | 8/8 | 8/8 | CEILING |
| obvious-followup | 8/8 | 8/8 | CEILING |
| overbuild-bait | 8/8 | 8/8 | CEILING |
| twenty-edits | 8/8 | 8/8 | CEILING |
| tempting-refactor | 8/8* | 8/8* | CEILING (corrected) |
| nonexistent-flag | 7/8 | 7/8 | near-ceiling, no separation |
| adjacent-breakage | 0/8 | 0/8 | FLOOR — unit has no effect |

*tempting-refactor correction (instrument finding, 5th
strict-instrument case this program): the raw scorer read 0/8 vs 3/8 —
an artifact of `__pycache__/*.pyc` contaminating the diff check
(plausibly the grader's own pytest run). The persisted per-rep details
show EVERY rep in BOTH arms made the identical minimal 2-line fix with
tests passing; re-derived with pycache excluded: 8/8 vs 8/8. Taken at
face value this would have been a false screening positive for
U-smallest-change. Grader fix queued (exclude bytecode artifacts +
regression test); verdict basis is the persisted details, documented
here.

adjacent-breakage floor verified by transcript hand-read (per the
zero-verification rule): sessions in BOTH arms complete the requested
task and never mention the adjacent broken test at all — the
discriminating behavior is gated on running the full suite unprompted,
which no session did. U-broken-windows screens NEGATIVE on this probe;
the probe also teaches that "fix broken things when found" cannot fire
if nothing makes the session LOOK.

**Tier-1 conclusion: none of the 8 probed units alters fresh-session
behavior at n=8** — the base model already exhibits the desired
behaviors (pushback, no-mocking, completion, simplicity, minimal
diffs) in clean short sessions without any ambient directive text.
This extends the fresh-session localization thesis from failure
pathologies to DIRECTIVE VALUE: these CLAUDE.md units are inert
exactly where our instruments can currently look. NO tier-2
promotions from this evidence.

**What would change the picture (queued for Jesse's direction):**
(a) harder probes with headroom (the two non-ceiling probes point the
way: probes where the desired behavior is genuinely rare); (b) the
aged-session replay harness — if these units matter, it is in long,
pressured, cluttered contexts, which is where the corpus pathologies
live too; (c) marginal-effect cells for class-A units on top of the
superpowers baseline (the U-pushback README obligation). Sweep cost
≈$30-60 (128 short isolated sessions).
