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
