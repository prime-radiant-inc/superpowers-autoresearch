# Instruction-design doctrine

When negative instructions backfire vs work, and how to settle wording
questions cheaply. Measured on superpowers SDD guidance, 2026-06-10/11
(opus, 5+ reps per phrasing, programmatic scoring + manual inspection,
no-guidance controls). Evidence:
- **Raw per-arm samples** (prohibition/recipe/control etc., 5 reps each):
  `raw/dispatch-composition-micro/` in this repo (rescued from
  `/tmp/sdd-exp/micro`); follow-up micros in `raw/follow-up-micros/`.
- **Experiment narratives:** superpowers-evals
  `docs/experiments/2026-06-10-sdd-cost-experiments.md` and
  `2026-06-11-build-loop-autoresearch.md` — NOTE: these live on the
  local evals branch `sdd-l1-elicited-plan` (worktree
  `superpowers/.claude/worktrees/sdd-review-dispatch/evals`), not yet on
  evals main. Until that branch lands, this repo's raw/ + logs/ are the
  durable copies.

## Classify the instruction before "fixing" it

- **Tripwires work.** Phrase-level self-checks on concrete tokens ("if the
  prompt you are writing contains 'do not flag'… stop") fire reliably.
- **Recognition / Red-Flags tables work.** Read at decision time, not
  composition time.
- **Discrete-directive prohibitions work** when the model has no competing
  incentive ("do not ask the reviewer to re-run tests": 0/5 violations vs
  3/5 control).
- **Composition prohibitions backfire under competing incentive.** "Do not
  restate the brief" scored WORSE than no guidance (4.4 vs 3.6 transcribed
  values) — the model relabeled the content to route around the rule.
  Only a positive composition recipe moved it ("your dispatch should
  contain: (1)…(5)": 3.0, zero variance).
- **Nuance clauses dilute recipes.** Appending a caveat to the winning
  recipe regressed it (3.0 → 3.8, noisy). Iterate by re-deriving the
  recipe, never by appending.
- **Exemption clauses don't scope their instruction** (E17). "Keep prose
  under 1,200 words — code blocks don't count" still slashed code fences
  39→14 and test content −62%, with prose already under budget. Models
  obey the instruction's mood, not its clause structure. Never introduce
  economy pressure near load-bearing content.
- **Conditionals on observable predicates work** (E22). "Use the cheapest
  tier when the plan text contains the complete code" discriminated
  correctly 9/10 on a prose plan. Conditions must be checkable facts, not
  judgment calls.
- **Structure beats prose.** A REQUIRED template field held 100+
  dispatches where guidance-only decayed by Task 3 (+$5); scripts were
  adopted 100%; a clean guidance line lost to a trained habit (E09:
  controller ran the survey command, then read the full plan anyway).
  Before writing a sentence, ask if a template field, script, or file
  contract can make the behavior structural.
- **Zero variance across reps is the signature of guidance that landed**
  (recipe: 3.0 no spread; narration recipe: 74/74/74/74/74 chars).
- **Ties go to shorter prose.** Codex re-reads SKILL.md ~500× per long
  session; every added counter has a recurring cost.

## How to apply — micro-test, don't full-run

One API call per sample: guidance variant in realistic context → composed
artifact → programmatic scoring (~$0.20/sample vs $12 eval runs whose
±20% variance swamps wording effects). Always include a no-guidance
control — it distinguishes works / backfires / can't-elicit. Manually
inspect every flagged match (agents quoting the rule they follow are
false positives; so are template echoes). If the control doesn't fail,
STOP: inconclusive-by-zero ≠ pass; don't author guidance for failures you
can't elicit. Working method implementations: `harnesses/*.py` and
`campaigns/writing-skills/run-battery.py` in this repo. (An earlier
draft cited a superpowers-evals method doc that was never written —
corrected 2026-06-11 after adversarial review.)

## Prompt-immune floors (don't fight these with wording)

- The SDD controller emits exactly ONE tool call per assistant message
  (0 multi-tool messages ever, with or without guidance).
- Thinking is load-bearing: capping MAX_THINKING_TOKENS raised the turn
  count 92→138 and doubled output tokens (E06). ~2/3 of controller output
  tokens are billed thinking invisible in transcripts.
- Controller cost yields only to structural change (fewer dispatches,
  smaller resident context), not turn discipline or narration trims
  (narration is ~2% of output).
