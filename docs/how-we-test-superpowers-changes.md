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

## Standing rules 9-16 (adopted 2026-08-07 from the adversarial audit)

The audit found the program's existing habits protect against false
mechanical gates but not against narrative overreach on top of
correct mechanics. These rules target that gap.

9. **Reachability-under-driver, stated as an event signature.** A
   pre-registration names, per arm, the concrete raw-data event that
   constitutes the discriminating behavior (e.g. "a tool-output
   record showing an e2e run raising SampleStreamError"), and affirms
   both the control's failure mode and the treatment's success mode
   can physically occur under this driver/fixture. The verdict
   reports the observed count of that signature per rep BEFORE any
   mechanism narrative; a narrative about an event whose signature
   count is zero may not be written.
10. **Instrument validation against a positive AND a near-miss
    negative.** Every PRIMARY-endpoint instrument is dry-run
    validated on (a) a synthetic positive and (b) a synthetic
    NEAR-MISS — the same tokens in the wrong channel (plan/spec text
    for a runtime instrument, an attempted-but-failed command for an
    execution instrument). The near-miss must classify as not-yes.
11. **Rep-level provenance for hand-read claims; recounts are
    corrections.** Any sentence attributing behavior to a named rep
    cites the record. If a later entry's counts contradict an earlier
    entry's for the same cells, the later entry carries a dated
    CORRECTION naming the superseded entry — silent supersession is a
    log defect.
12. **Denominator lock.** Pre-registration fixes what counts as a
    scoreable rep; every table states n per cell with exclusions
    itemized by rep number; a changed denominator requires a dated
    correction.
13. **Pre-registered inconclusive conditions are binding gates.** If
    a pre-registration names an INCONCLUSIVE-BY-* condition, the
    verdict's first line evaluates it (met / not met, with instrument
    values). Only after "not met" may any NULL/positive label be
    assigned.
14. **Dropped-endpoint disclosure.** Every pre-registered endpoint
    appears in the verdict — with results, or with "DROPPED
    because ...".
15. **Absence-based claims are bounds.** A positive inferred from an
    event's absence ("no error → inherited") is phrased as a bound
    ("no firsthand re-discovery observed") in the verdict and every
    downstream summary.
16. **Tool-availability parity.** A scenario whose primary endpoint
    depends on the session running a tool preinstalls that tool in
    setup and asserts it in pre().
17. **Scenario-visibility scan.** The session's container can
    currently read the scenario directory (story, checks,
    instruments) — a rep that reads its own rubric is contaminated
    (first caught 2026-08-08, arf r1t-rep2). Until the mount is
    closed, every battery's scoring includes a scenario-dir-read scan
    over all transcripts, and any rep that read scenario files is
    excluded with a dated note.
