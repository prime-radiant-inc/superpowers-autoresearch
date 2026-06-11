# Campaign: writing-skills composition doctrine

**Question:** Does the current `writing-skills` skill steer skill-authors
wrong on composition-shaping problems — and do the proposed revisions fix
it without breaking what works?

**Branch under test:** `writing-skills-composition-doctrine` (worktree
`.claude/worktrees/writing-skills-research`, off origin/dev).

**Evidence base (already collected, 2026-06-10/11):** composition
prohibitions backfire (4.4 vs 3.6 control vs 3.0 recipe); nuance clauses
dilute recipes (3.0→3.8); exemptions don't scope (E17: −62% test content
despite code exemption); structure beats prose (REQUIRED model: field vs
guidance decay; E09 habit beat advice); zero-variance = landed guidance;
elicit-first (placeholders 40/40 clean → decline).

## RED battery — authoring tasks against the CURRENT skill

Each task: one API call; system prompt = full current writing-skills
SKILL.md + "You are authoring/editing superpowers skills; follow your
writing-skills training."; user = the task. 5 reps, opus (the model that
authors skills in practice). Author output = proposed guidance text +
test plan.

| Task | Problem given to the author | Correct form | Predicted with current skill |
|---|---|---|---|
| T1 | Controllers retype exact spec values into dispatch prompts; transcription errors result. Add guidance to stop it. | Positive composition recipe | Prohibition ("do not restate") |
| T2 | Reviewer reports bury verdicts under process narration. Fix via prompt-template guidance. | Positive contract ("final message IS the report") | Prohibition list |
| T3 | Implementers skip re-running tests after review fixes. Add guidance. | Discrete prohibition / contract (prohibition CORRECT here) | Prohibition (current skill OK; revised must not overcorrect) |
| T4 | Plans are bloated; add guidance to keep them shorter. | Push back / test first — length pressure slashes load-bearing content | Adds a word budget |
| T5 | Plans sometimes contain TBD placeholders; strengthen writing-plans. | Baseline-elicit first; decline if 0/N | May skip baseline or author anyway |
| T6 | Dispatches keep omitting the model field, inheriting expensive defaults. Fix via skill. | Structural: REQUIRED template field | Prose guidance |
| T7 | Given a draft recipe change: design the pre-deployment verification. | Micro-battery w/ no-guidance control, 5+ reps, manual inspection | Pressure-scenario subagents, n=1, no control |

**Scoring:** programmatic classification (prohibition/recipe/structural/
budget/control-present/n-reps) + MANDATORY manual excerpt review. The
researcher pastes excerpts; the driver (opus session) confirms every
classification. No verdict finalizes without driver review.

## GREEN

Driver writes revised sections on the branch (doctrine table, composition
test type + micro method, variance-as-metric, stop conditions
[elicit-first, accretion warning], structure-before-prose, prompt-template
authoring). Battery reruns with SKILL_FILE=revised. Expected flips: T1,
T2, T4, T6, T7. Expected holds: T3 (prohibition stays correct), T5.

## REFACTOR

New failure shapes → close → rerun. Also micro-check the revised skill's
own length cost (it is itself frequently loaded).

## Roles

- **Researcher (sonnet, driven session):** executes the battery exactly
  per RESEARCHER-PROTOCOL.md. Mechanics only.
- **Driver (opus, this session):** designs variants, reviews every
  classification, writes the revised skill text, owns verdicts and the log.

Budget: RED ≈ $15-20 (35 opus calls), GREEN similar, total ≤ $60.
