# How We Test Superpowers Changes

One page for the human partner. If a claim in a log can't be audited
through this page, that's a bug in the program — say so.

## The gate

**Nothing ships on screening evidence. Quorum is the only ship gate.**
A change to superpowers text is ship-ready only when the exact shipped
text has run as a committed arm branch of the real plugin, loaded by a
real harness, on the current dev base, in a pre-registered quorum
battery with its verdict published. (Adopted as a standing rule
2026-08-05 after screening results were once presented as
promotion-grade; the merged PRs — #2077/#2078/#2080, x13, the spec
plumbing — all met this bar.)

## The tiers

**Screening (micro-ambient).** One real headless CLI session (claude /
codex / kimi / pi binaries), isolated throwaway HOME, tiny fixture, a
directive placed in the harness's ambient file, deterministic grading.
4-17¢/rep. Its ONLY legitimate outputs: "this text moves behavior at
all," "here is the mechanism," "kill this idea." Runner:
`campaigns/claudemd-lift/run_screening.py` / `run_tier2.py`. Known
limit: host-side isolation (the CLAUDE.md-leak class) — one more
reason it can't gate.

**Quorum static scenarios.** The consolidation target for everything
between screening and full SDD: a quorum scenario whose story.md pins
ONE exact user message and forbids engagement (the pattern quorum's own
smoke scenario uses), mechanical emit-only checks, arm-neutral ACs,
container isolation, real plugin loading. Model/harness variation is
pure config (`--coding-agent` × `--credential`). First consumers:
`sp-adjacent-breakage`, `sp-overbuild-bait`.

**Full quorum (SDD scenarios).** Containerized end-to-end multi-task
sessions: seeded defects, scripted user turns (class-routed pinned
replies), gauntlet verifier + mechanical checks, $7-15/rep. This is
where process-skill changes (SDD, writing-plans) are judged, and the
ship gate for everything.

## Standing rules (accumulated, all load-bearing)

1. **Pre-register before launch:** arms (manifest row with SHA),
   scenario, rep count, endpoints, pass bars, reachability of every
   arm's text. Verdicts append to the same log; corrections are dated
   entries, never edits.
2. **Per-rep served model is a mandatory covariate** (the codex_sub
   lane never pinned a model; terra/sol mix discovered 2026-08-05).
   Cross-arm comparisons are within-model or disclose the mix.
3. **Canary before real cells on any new harness** (MARIGOLD ambient
   canary): the ambient/plugin channel must provably reach the model.
4. **Mechanical layers screen; hand-reads carry verdicts.** Every
   zero, every outlier, every "unknown" cell gets eyes. Validators
   exercise the real checks.sh, not a reimplementation.
5. **Headroom scan before arm-build:** measure the failure class in
   controls first; no battery against a ceiling or an empty class.
6. **Behavioral nulls get an interrogation pass** (the
   rationalization-interrogation method) before a successor arm.
7. **Real-session provenance outranks eval-only provenance;
   eval-only findings need the failure observed, the fix demonstrated,
   or they go to docs/deferred-experiments.md with a revival trigger.**
8. **Subagent commits are audited (git show --stat) before push;
   no subagent pushes.**

## Where things live

- Verdict logs: `logs/*.md` (append-only, one per campaign/battery).
- Arms: local branches in the superpowers repo, SHAs pinned in
  `campaigns/cost-pathologies/arm-manifest.md`; never pushed.
- Raw evidence: rep dirs under the evals checkouts
  (`results/<scenario>-<arm>-rep<N>/` — rollouts, verdict.json,
  final trees); micro rows in `campaigns/claudemd-lift/out/`.
- Deferred work with triggers: `docs/deferred-experiments.md`.
- Method notes: `docs/rationalization-interrogation-method.md`,
  `docs/instruction-design-doctrine.md`, this file.

## How to audit any claim

Find its log entry (pre-registration + verdict) → the manifest row
gives the arm SHA (diff it against its stated base) → the rep dirs
named in the verdict hold the rollouts and trees the numbers came
from → the scorer named in the entry reproduces the mechanical layer;
hand-read notes are in the verdict. If any link is missing, the claim
is defective — flag it.
