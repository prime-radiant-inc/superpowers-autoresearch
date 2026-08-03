# CLAUDE.md-Lift Campaign — Design (2026-08-03)

Campaign 3. Directive (Jesse, 2026-08-03): his `~/.claude/CLAUDE.md`
carries many directives that may or may not impact outcomes; determine
which units actually change behavior, and which of those should be
lifted into superpowers. Shape: a wide tier of small cheap screening
experiments, then rigorous batteries for units that screen positive.

**Privacy rule for this campaign:** the source file is private config.
Public artifacts (this repo) reference directive units by ID +
paraphrase; the verbatim unit corpus lives on-host outside the repo
(same handling as donor corpora). Genericized text (e.g. "your human
partner" for a personal name) is what any lift candidate ships as.

## Unit inventory (by ID; paraphrases)

Grouped; each unit is separately toggleable in screening arms.

- **U-honesty**: never invent technical details; state ignorance and
  research instead. (Anti-fabrication.)
- **U-pushback**: call out bad ideas; disagree with citations; no
  agreeable-to-be-nice. (Anti-sycophancy.)
- **U-noglaze**: no flattery/glazing in collaboration tone.
- **U-ask-vs-assume**: stop and ask rather than assume on ambiguity.
- **U-smallest-change**: smallest reasonable change; no rewrites
  without permission.
- **U-simple-first**: simplest thing that could possibly work;
  simple > clever.
- **U-yagni**: YAGNI in design.
- **U-tedious-ok**: tedious systematic work is often correct; don't
  abandon repetitive approaches.
- **U-root-cause**: find root cause, never patch symptoms.
- **U-tdd**: TDD for every feature/bugfix.
- **U-test-integrity**: never test mocked behavior; no mocks in e2e;
  pristine test output; never ignore test/system output.
- **U-broken-windows**: all test failures are your responsibility;
  fix broken things when found.
- **U-comments**: name by domain; comments say WHAT/WHY, never
  history.
- **U-vcs**: WIP branches, frequent commits, never skip hooks, no
  blind `git add -A`.
- **U-automation**: scripts with names/help/error reporting over
  one-liners; manage script output context.
- **U-loc-estimates**: estimate in lines of code, not wall-clock.
- **U-proactive**: just do it including follow-ups; enumerated pause
  conditions.
- **U-no-trivial-exception**: process applies to trivial tasks too.
- **U-style-concise**: concise/direct/no contrastive negation/one
  question at a time.

Overlap classes vs superpowers (screening must respect these):
(A) **already-covered** — a skill exists (U-tdd, U-root-cause, U-yagni,
partially U-pushback via receiving-code-review): the question is
MARGINAL effect on top of superpowers, not standalone effect.
(B) **uncovered** — no skill equivalent (U-honesty, U-smallest-change,
U-test-integrity's mock clauses, U-tedious-ok, U-loc-estimates,
U-automation, U-broken-windows): standalone effect first.
(C) **personal/identity** — not lift candidates (naming, journal
mechanics, style particulars); excluded unless screening says
otherwise.

## Tier 1 — screening (cheap, wide, lane-free)

Isolated headless sessions (the evals-container / isolated-HOME
pattern — host runs are CONFOUNDED by the real global CLAUDE.md, per
the eval-claudemd-leak finding; container or clean-HOME is mandatory).
Single- or few-turn probe tasks, each designed so the unit under test
has a measurable discriminating behavior:

- U-honesty → probes asking about plausible-but-nonexistent
  flags/APIs/config keys; measure fabrication vs
  state-unknown/research. (Mechanically gradable: the flag doesn't
  exist.)
- U-pushback/U-noglaze → present a plan with a real flaw + social
  pressure to agree; measure flaw-named-or-not, sycophantic framing.
- U-smallest-change → small bugfix task in a file with tempting
  adjacent refactors; measure diff size / files touched beyond the
  fix.
- U-simple-first/U-yagni → open-ended "add X" where a 10-line
  solution exists; measure abstraction count/LOC.
- U-test-integrity → task with a failing test whose easy "fix" is
  mocking the behavior under test; measure mock-vs-real resolution.
- U-tedious-ok → task needing 20 repetitive edits; measure
  completion vs premature scripting/abandonment.
- U-broken-windows → task adjacent to an unrelated pre-broken test;
  measure whether it gets flagged/fixed vs ignored.
- U-proactive → task with an obvious required follow-up; measure
  follow-up completion vs stopping to ask.
- Others analogously; each probe pre-registered with its mechanical
  grading rule before any runs.

Arms per unit (screening): {empty-baseline, unit-only} for class B;
{superpowers-baseline, superpowers+unit} for class A (marginal
effect). n=6-10/cell, single model (session default tier), fixed
probe set. A unit screens POSITIVE only if the discriminating
behavior separates cells beyond the empty-vs-empty noise floor
(measured once, shared).

## Tier 2 — rigorous batteries (winners only)

For each screening-positive unit: genericize the text, place it where
it would actually live in superpowers (using-superpowers bootstrap vs
a specific skill vs a new small skill — placement is part of the
arm), build a cp/-style arm branch, and run containerized quorum
batteries on BOTH claude and codex — the superpowers bar is
cross-harness value delivered via skill text, which is a different
delivery channel than CLAUDE.md ambient context. Guards: completion,
cost, and no regression on the probe suites of OTHER units
(interaction check). Only cross-harness winners become PR
candidates.

## Budget and sequencing

Tier 1: ~19 units × ~2 cells × n≈8 × short sessions — estimate
$40-80 total at screening depth; runs parallel to campaign 2's
container batteries (no lane contention; API/headless only).
Tier 2: ~$30-60 per surviving unit; expect 3-6 survivors.
Sequencing: screening harness build queues behind campaign 2's
current autoresearch build task (repo serial rule); screening RUNS
overlap campaign 2 batteries freely.
