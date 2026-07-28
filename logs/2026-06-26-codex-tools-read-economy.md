# Codex tool economy: whole-file reads + eager subagent close

- Registered: 2026-06-26
- Status: CLOSED — NEGATIVE (codex-tools.md prose is not the lever)
- Method tier: FULL (small scenario first, then full), no separate MICRO this round
- Skill under test: `skills/using-superpowers/references/codex-tools.md`

## Motivation (from the codex-vs-claude transcript investigation, this session)

On `sdd-go-fractals-opus48`, codex runs ~2x claude's wall time and ~1.4x cost for
equivalent output. Three independent sub-agent analyses converged:

- Codex has **no native file-read tool**; ~50% of its ~357 shell calls are file
  reads (`cat`/`sed`/`nl`). Many are **chunked `sed -n` pages of small files** and
  **re-reads of unchanged files** (plan.md fully re-paginated 3x; `SKILL.md` read
  ~45x). Each read is a model turn re-sending the (flagship gpt-5.5) orchestrator
  context.
- Codex **defers `close_agent`**, accumulates 6 live handles, and hits the
  "agent thread limit reached" cap 3x per run → bulk-close + re-spawn churn
  (~9–21 wasted orchestrator turns). The existing codex-tools.md line ("close …
  when they have finished all their work") is too weak.

(Separately established this session: codex costs were also inflated ~2x by an
obol per-step large-context tiering artifact from cumulative-lumping in the codex
normalizer — fixed in commit c5de440. The numbers above are post-fix.)

## Hypothesis

Two guidance additions to `codex-tools.md` reduce codex's turn count (hence
cost + wall time) on an SDD task, with no quality regression:

1. **Read whole small files in one `cat`** (no chunked `sed` windows, no re-reads,
   batch reads, review from the diff). → fewer read turns.
2. **Close each subagent immediately after its `wait_agent` returns; limit is 6.**
   → eliminates thread-limit stalls/retries.

Predictions (to be falsified):
- Variant reduces codex total tool calls / shell-read calls by a meaningful margin
  (>20% to clear single-run noise per AR methodology).
- Variant shows 0 "agent thread limit reached" events vs baseline's >0.
- Pass rate and deliverable correctness unchanged (no quality regression).

## Setup

- Control root: `/Users/jesse/git/superpowers/sp-cxbase` (git archive of dev @98b0800).
- Variant root: `/Users/jesse/git/superpowers/sp-cxopt` (identical except the two
  codex-tools.md edits). Verified `diff -rq`: only codex-tools.md differs.
- Coding-agent: codex (codex_sub). Spark/mini pricing snapshot active in container.
- Smaller scenario: `sdd-tiny` (2-task Python SDD) — built to exercise file reads
  + subagent spawn/wait/close in ~⅓ the time of sdd-go-fractals.
- Caveat (AR methodology): sdd-tiny's plan is hand-authored, so its ABSOLUTE cost
  overstates a real elicited-plan baseline. We use it only for the BASELINE-vs-
  VARIANT delta and pipeline validation, not as a cost baseline.

## Runs

Scenario `sdd-tiny`, coding-agent codex (codex_sub), spark-priced.

### Baseline (sp-cxbase, codex-tools.md unchanged)
| rep | verdict | cost | steps | Bash | sed-n reads | cat reads | thread-limit events | spawns/closes |
|---|---|---|---|---|---|---|---|---|
| 1 | pass | $4.73 | 393 | 192 | 75 | 20 | 1 | 10/9 |
| 2 | pass | $3.55 | 272 | 115 | 37 | 10 | 0 | 7/7 |
| 3 | pass | $4.49 | 315 | 167 | 52 | 7 | 1 | 8/6 |
| **mean** | 3/3 pass | **$4.26** | 327 | **158** | **54.7** | 12.3 | 0.67 (2/3) | 8.3/7.3 |

Note: high baseline variance — rep1 was a heavy run (10 subagents, hit the
thread limit) vs rep2 light (7 subagents, no stall). Codex non-deterministically
spawns more/fewer subagents, which dominates Bash/read counts. Reps essential.

Baseline rep1 confirms sdd-tiny reproduces BOTH target behaviors: heavy chunked
`sed -n` reads (75 vs 20 cat) and a thread-limit stall (1) from deferred closes
(10 spawns, only 9 closes). Good proxy.

### Variant (sp-cxopt, codex-tools.md +whole-file-reads +eager-close)
| rep | verdict | cost | steps | Bash | sed-n reads | cat reads | thread-limit events | spawns/closes |
|---|---|---|---|---|---|---|---|---|
| 1 | pass | $5.53 | 401 | 192 | 57 | 5 | 1 | 11/11 |
| 2 | pass | $4.14 | 299 | 126 | 46 | 8 | 3 | 10/6 |
| 3 | pass | $5.09 | 396 | 190 | 85 | 3 | 0 | 9/9 |
| **mean** | 3/3 pass | **$4.92** | 365 | **169** | **62.7** | 5.3 | 1.33 | 10.0/8.7 |

Diagnostic (variant rep2): codex DID load codex-tools.md (the new guidance text
appears in sessions), yet sessions that loaded it still chunk-read (`sed -n`
13/12/6/4) and still deferred closes (10 spawns / 6 closes, hit thread limit 3x).
Guidance **read but not followed**. Also most reads happen in SUBAGENT sessions,
several of which never load codex-tools.md at all (refs=0 but still `sed -n`).

## Verdict — NEGATIVE

Adding whole-file-read + eager-close guidance to `codex-tools.md` did **not**
improve codex's read economy or thread-limit behavior on `sdd-tiny` (n=3 vs n=3,
all 6 pass). No predicted effect materialized:

- `sed -n` chunked reads: 54.7 → 62.7 (NOT reduced; +15%, within codex's large
  run-to-run variance). Per-subagent: 6.6 → 6.3 — identical.
- `cat` whole-file reads: 9.7 → 5.3 (went DOWN, not up).
- thread-limit stalls: 0.67 → 1.33/run (NOT eliminated).
- cost/Bash/steps all flat-to-slightly-worse; spawn count (8.3 → 10.0) is the
  dominant confound and tracks all the deltas — i.e. the differences are codex's
  non-determinism, not the guidance.
- No quality regression (6/6 pass).

### Why it didn't land (evidence)

1. **Read but not followed.** Sessions that loaded codex-tools.md (new guidance
   text present) still chunk-read (`sed -n`) and still deferred closes (rep2: 10
   spawns / 6 closes, 3 thread-limit hits). Prose in a reference file does not
   override codex's default read/close behavior.
2. **Wrong location.** Most reads happen in **subagent** sessions
   (subagent-driven-development implementer/reviewer contexts). Several subagent
   sessions never reference codex-tools.md at all (refs=0 but still `sed -n`), so
   the guidance can't reach where the cost is incurred.

### Implications / next options (NOT executed)

- The lever, if any, is the **subagent prompts** in subagent-driven-development
  (implementer-prompt / reviewer prompts), not codex-tools.md — that's where the
  reads happen and what those fresh contexts actually load. Worth a future
  variant, but a different experiment.
- Or accept codex's chunked shell-read + deferred-close as a **structural harness
  default** not fixable by superpowers prose.
- Did **not** run the full `sdd-go-fractals` before/after: the cheap proxy already
  shows no effect, so spending ~$15–30 on it is unjustified.

### Cost

~$30 of the $200 budget (6 × sdd-tiny codex runs ≈ $4–5 each). The smaller-eval
choice paid off: a clean negative for ~$30 instead of ~$90+ on full runs.

## Micro: in-prompt read-economy wording (POSITIVE — reframes the result)

Harness: `harnesses/codex-read-economy-micro.py`. BASE codex (no superpowers — the
ONLY variable is the injected guidance), single-turn `codex exec`, read-only, over
a real 331-line fixture (`economics.ts`). Task: "read the file and summarize every
export" (needs the whole file). n=5 per variant, guidance injected directly into
the prompt. Scores hand-verified against the rollouts.

| variant | one-cat% | chunk/run | notes |
|---|---|---|---|
| V0-control (no guidance) | **0%** | 0.4 | 2/5 `sed -n '1,240p'` (TRUNCATES the 331-line file); 3/5 fumbled (`rg`, wrong `src/` path) — none read it whole |
| V1-plain | **100%** | 0 | all 5 `cat economics.ts` |
| V2-cost | **100%** | 0 | all 5 whole `cat` |
| V3-imperative | **100%** | 0 | all 5 whole `cat` |

### Findings

1. **In-prompt read guidance DOES change codex's read behavior — decisively**
   (0% → 100% whole-file reads). Opposite of the SDD/codex-tools.md result above.
2. **The lever is DELIVERY/SALIENCE, not wording.** All three wordings hit 100%
   identically; the variable that mattered vs the SDD failure is WHERE the
   guidance lives — directly in the prompt (works) vs buried in a `references/`
   file amid a long multi-turn flow (ignored).
3. **Quality risk, not just cost:** control's `sed -n '1,240p'` silently dropped
   91 of 331 lines. Codex's chunked reads can miss content, not merely waste turns.
4. **Unsolved:** guidance fixed chunking but not RE-READING (variants `cat` 2–3×).
   "Don't re-read" is a separate behavior the wording didn't move.
5. `reads/run` is NOT a clean metric here (control's 0.4 is low because it often
   failed to read at all); `one-cat%` and `chunk/run` are the trustworthy signals.

### Implication / next step

The wording works; the question is DELIVERY. See the delivery micro below.

## Micro: delivery position (CONFIRMS the "why rules don't fire" mechanism)

Harness `harnesses/codex-read-delivery-micro.py`. ONE fixed wording; vary only
WHERE it's delivered. n=5, BASE codex, real fixture. Hand-verified.

| delivery | one-cat% | chunk/run |
|---|---|---|
| D0-control (none) | 20% | 1.4 |
| D1-inprompt (top of prompt) | **100%** | 0 |
| D2-pointer (guidance in ./codex-tools.md; prompt only points to it — REAL superpowers structure) | **0%** | 1.4 |
| D3-injected (`<EXTREMELY_IMPORTANT>` wrapper — the session-start-codex hook format) | **100%** | 0 |

CLINCHER: all 5 D2-pointer runs actually `cat`'d codex-tools.md (the pointer
worked) yet still chunk-read the target (`sed -n '1,260p'`), identical to
control. **Referenced guidance is ignored even when read; only injected guidance
fires.**

### Why the rules don't fire (answered)

The session-start-codex hook injects `using-superpowers/SKILL.md` into context
(high-salience `<EXTREMELY_IMPORTANT>`). The read/close rules live in
`codex-tools.md`, which is NEVER injected — SKILL.md only names it as a one-line
pointer. So codex sees a reference it `cat`s as a throwaway observation; the rule
never has system-prompt-level salience. Subagents get no session-start injection
at all (they crawl skills via `cat`), so they never load it. Delivery, not wording.

### Core Superpowers change (built as variant root sp-cxinject; validating)

3-file diff off dev: (1) `hooks/session-start-codex` now INJECTS codex-tools.md
alongside SKILL.md (orchestrator high-salience); (2) `codex-tools.md` carries the
read-economy section; (3) `implementer-prompt.md` gets a prominent "Reading files
efficiently" note (subagents get no hook, so it must ride in their prompt).
Scenario validation (sdd-tiny codex, sp-cxinject vs baseline) below.

### Delivery-wiring finding (debugged during validation)

First validation attempt failed: the injected read-economy text reached 0 codex
sessions despite the hook edit. Root cause: **`hooks/session-start-codex` is not
wired** — `hooks/hooks-codex.json` is EMPTY and `hooks/hooks.json` registers the
GENERIC `hooks/session-start` for SessionStart. The eval's codex gets its
SessionStart injection from the generic `session-start` (its "use the 'Skill'
tool" wrapper appears verbatim in the codex session), and nothing injects
codex-tools.md. So editing session-start-codex was dead code.

Fix in the variant: inject codex-tools.md via the WIRED generic `session-start`
hook (verified: a fresh rep's orchestrator context now contains the read-economy
section). PRODUCTION implication for the core PR: the change is not just
"edit codex-tools.md" — it must **wire a codex injection path** (populate
hooks-codex.json to use session-start-codex, or extend session-start to inject
codex-tools.md gated on the codex harness). Subagents still get no session-start
injection → the implementer-prompt note is their only channel.

### Scenario validation result (sdd-tiny codex, sp-cxinject vs baseline) — SPLIT VERDICT

All reps pass (no quality regression). Orchestrator-vs-subagent chunked-read split:

| | orchestrator sed-n | subagent sed-n | total sed-n | cost |
|---|---|---|---|---|
| baseline (n=3) | 12 / 12 / 18 (~14) | 73 / 33 / 63 (~56) | 54.7 | $4.26 |
| inject (n=3) | **2 / 2 / 2** (zero-variance — guidance landed) | 95 / 61 / 60 (unchanged, scales w/ spawns) | 74 / 35 / 50 | $4.89 / $2.93 / $4.25 |

- ORCHESTRATOR: the injection WORKS end-to-end — chunked reads collapse ~14→2
  (~85%), reliably, guidance confirmed in the injected SessionStart context.
  Proves the mechanism in the real agentic flow.
- SUBAGENTS: NO change (~60, baseline range). No session-start injection reaches
  them; the implementer-prompt note did not reduce their chunking.
- Subagents do the BULK of reads (~56 of ~70 sed-n), so TOTAL sed-n and cost
  barely move. This change ALONE won't materially cut scenario cost.

## VERDICT (campaign) — what's ready for Core Superpowers

1. Wording is not the lever; DELIVERY is (micro: injected 100%, referenced 0%).
2. READY TO PR: wire a codex SessionStart injection of codex-tools.md
   (harness-gated). Today session-start-codex is dead (unwired) and the generic
   session-start injects only SKILL.md. Validated: orchestrator chunked reads
   ~14→2, no regression. Makes the existing codex rules actually fire for the
   orchestrator.
3. KNOWN GAP / follow-up: subagents (where most reads happen) get no
   session-start injection; the implementer-prompt note was insufficient, so
   total cost stays ~flat. Next experiment: a micro injecting read guidance into a
   spawned subagent's prompt/context (and split implementer vs reviewer chunking).

Cost: ~$50 of the +$100 (micros ~$16; scenario reps ~$34 incl. 3 discarded
broken-injection reps).

## Micro: strong SKILL.md pointer (compel read+follow) — POSITIVE

Q (Jesse): can strengthening the using-superpowers SKILL.md *pointer* compel codex
to read+follow codex-tools.md, instead of rewiring the hook to inject its content?

Delivery micro re-run, bypass-sandbox (the read-only/bwrap sandbox was broken in
the later container instance — caught via manual inspection: D4's first
0/0 result was 5/5 `bwrap: No permissions to create a new namespace`, not a
guidance signal). n=5, hand-verified, zero sandbox errors this run.

| delivery | one-cat% | chunk/run |
|---|---|---|
| D0-control | 0% | 2.0 |
| D1-inprompt | 100% | 0 |
| D2-pointer (weak: "consult ./codex-tools.md" — ~current SKILL.md) | 20% | 0.8 |
| D3-injected (codex-tools.md content in context) | 100% | 0 |
| **D4-strong-pointer** ("you MUST read ./codex-tools.md and follow every rule, binding, before ANY command") | **100%** | 0 |

D4 hand-verified 5/5: codex read the guide AND then `cat`'d the target whole (0
chunk). **A strong injected compulsion to read+obey the referenced guide works as
well as injecting the content.** The weak pointer (today's SKILL.md) is ~20% —
*strength is the variable, not whether it's a pointer.*

### Revised Core Superpowers recommendation

Two equivalent ways to fix the ORCHESTRATOR; prefer the smaller one:
- **Preferred: strengthen the codex pointer in `using-superpowers/SKILL.md`** to a
  binding "before running any command, read references/codex-tools.md and follow it
  exactly" — one line, SKILL.md is already injected high-salience, keeps
  codex-tools.md the single source. (Validated equivalent: D4=100%.)
- Alternative: wire the hook to inject codex-tools.md content (bigger change).
- Both fix the ORCHESTRATOR only. SUBAGENTS get no SKILL.md injection (they crawl
  skills), so the subagent read gap remains for EITHER approach — still the
  open follow-up.

## Micro: subagent delivery + METRIC CORRECTION

Goal: improve codex SUBAGENT read delivery (subagents chunked in the scenario
despite the implementer-prompt note).

Subagent-prompt salience micro on the REAL subagent model gpt-5.4-mini (codex
exec -m honors it; the gpt-5.5 proxy was misleading — it follows even buried
guidance): SUB0-control 0% one-cat (chunks); SUB1-buried / SUB2-top / SUB3-wrap
ALL 100%. So on a SIMPLE read task mini follows the guidance at any position.

BUT the scenario contradicts that, and digging in caught a METRIC ERROR:
- In the inject run, implementer subagents that HAD the note still showed many
  `sed -n` (e.g. mini implementer, note present, 17 sed-n). Inspecting them:
  most are `sed -n '1,220p' file` = whole small file in ONE command (a capped-read
  idiom), or `find … | sed -n` capping a listing — NOT pathological chunking.
- **`sed -n` count ≠ chunking.** Re-measured with true signals: continuation
  windows (`sed -n 'A,Bp'` with A>1) and re-reads (same file read 2+×/session).

True-metric results (orchestrator | subagents, cont-window / reread-files):
- baseline: 1/5, 1/2  |  0/11, 1/9
- inject:   0/1, 0/1  |  0/14, 1/8

Findings (corrected):
1. Windowed chunking is rare everywhere; the real waste is RE-READING the same
   file within a session.
2. ORCHESTRATOR: guidance reduced re-reads (5/2 → 1/1) and switched to `cat`.
   Real, validated improvement.
3. SUBAGENTS: re-reads unchanged (~8–14) with or without the note. The note
   didn't fix subagent re-reading in the complex multi-turn task.
4. The simple micro (one file to read) OVERSTATED the fix — it can't surface
   re-reading, the actual subagent problem. Fixture-realism gap (the framework's
   own warning) bit here.

### Subagent verdict + recommendation

Subagent read-economy is NOT cleanly fixable by a prompt note: mini follows read
guidance on a trivial read but reverts to re-reading in real multi-turn
implementer/reviewer work, and reviewers don't get the note at all. The cheap
micro can't faithfully test it (needs a multi-file, multi-turn fixture ≈ a
scenario). Recommendation: SHIP the validated orchestrator fix (strengthened
SKILL.md pointer); treat subagent re-read economy as a separate, harder problem
(uncertain payoff) — only pursue with a realistic multi-file subagent harness or
scenario-level iteration, not the single-read micro.

## Interview: WHY mini re-reads (resumed real subagent sessions) — VERIFIED

Resumed two real gpt-5.4-mini subagent sessions from run a07f that re-read files
(`codex exec resume <id> -c model=gpt-5.4-mini`, reflective prompt, no new work)
and then VERIFIED the self-report against the rollout commands.

Both re-readers were REVIEWERS (not implementers). Self-reported causes, both
confirmed in the command log:
1. WRONG-WORKTREE-PATH RETRIES. The reviewer didn't know the work lived in
   `.worktrees/wordstat-sdd/`. It read the wrong path first, ran `rg --files`/
   `find` to locate, then re-read at the correct worktree path. Every re-read
   file appears at 2+ distinct paths in the log. This is
   sdd-worktree-dispatch-hazard manifesting in REVIEWERS.
2. LINE-NUMBERED CITATION READS. Reviewers read once to understand, then re-read
   WITH line numbers (`sed -n`, `nl -ba`) to cite exact `file:line`. 8/9 and 4/5
   reads were line-numbered. Each is a single whole-file capped read — legitimate
   review grounding, NOT chunking, NOT waste.

What mini said would help (both sessions, converging unprompted): "resolve the
correct worktree path up front" + "a running checklist of already-inspected
files."

### Reframe — the subagent read fix is NOT a read-economy note

The implementer-prompt read-economy note "failed" because it was aimed at the
wrong target on both axes:
- Wrong AGENT: the re-readers are REVIEWERS, who never get the implementer note.
- Wrong BEHAVIOR: the cost is path-confusion retries + citation grounding, not
  chunking. The note addresses chunking, which barely happens.

Actionable levers (priority order):
1. PASS THE EXACT WORKTREE PATH into spawn prompts (implementer AND reviewer):
   give the absolute `.worktrees/<name>/` cwd up front so subagents don't
   read-wrong-path -> locate -> re-read-right-path. Single biggest subagent
   read-cost lever; ties to sdd-worktree-dispatch-hazard.
2. Leave reviewer line-numbered reads alone — whole-file, citation-necessary;
   suppressing them would hurt review quality.

Cost: ~$0.10 (two mini resumes reloading session context).

## Implementation: line-number the review package (the real root cause)

Reading `skills/subagent-driven-development/scripts/review-package` after the
interview found the deeper root cause for the citation re-reads: the package is
`git diff -U10` with NO line numbers, yet `task-reviewer-prompt.md` tells the
reviewer to "cite file:line for every finding" from that package. The reviewer
literally can't, so it re-opens each changed file with `nl -ba`/`sed -n` to
recover citable line numbers. The fix fulfills the EXISTING design intent
("read the diff once, cite from it") rather than changing tuned behavior.

FIX (branch `read-economy-review-package-linenum`, commit 09f82b3, off `dev`):
annotate the diff body with new-file line numbers (`annotate_diff_lines` awk:
context + added lines numbered from each hunk's `+start`; deletions blank;
headers untouched). Reviewer can now cite straight from the package. Added
`tests/claude-code/test-review-package.sh` (TDD: RED before, GREEN after),
registered in `run-skill-tests.sh`. `test-sdd-workspace.sh` still green.

### Baseline (n=12 existing sdd-tiny codex runs) — reviewer SOURCE reads

Per run, reviewer shell reads of changed source (counter/formatter/cli/test):
7,3,9,1,3,12,10,8,2,16,3,7 → median ~7, range 1–16, and ~99% of those reads are
line-numbered (`nl`/`sed -n`) — the citation signature, confirmed at scale. The
line-numbering hypothesis predicts fixed runs collapse these toward ~0.

### Validation: 4 fixed reps (line-numbered package) — NEGATIVE

4 reps on the fix branch (container, codex), all 4 verdict=pass (the
line-numbered package did NOT break review quality). Reviewer source-reads/run:
[0, 6, 8, 13] → median 7.0, mean 6.8 — STATISTICALLY IDENTICAL to the n=12
baseline (median 7, mean 6.75). The line-numbering hypothesis is DISPROVEN.

Mechanism verified, not assumed: extracted a reviewer's actual VIEW of the
package from the rollout — it was line-numbered (`     0| new file mode...`),
the reviewer saw the numbers, and STILL re-read source with `nl -ba`. So the
fix was active and simply didn't change behavior. The interview's truer reason
holds: reviewers re-read to VERIFY AGAINST THE ACTUAL FILE, not to get numbers.

Decomposition of the 27 fixed-run source-reads (the decisive cut):
- 23/27 (85%) are DISTINCT files read ONCE — a reviewer verifying each changed
  file against real code. Legitimate review behavior, NOT waste.
- ~4 reads total (≈1/run) are re-reads/wrong-path waste. Negligible.
- One reviewer (56ab) read ZERO source — cited entirely from the package.

So there is no meaningful, fixable read inefficiency in the reviewer flow: what
looked like a "re-read problem" is mostly legitimate per-file verification. The
worktree-path fix (Fix B) would only touch the ~1/run wrong-path subset — not
worth pursuing.

(Minor cosmetic bug in the change if ever revived: git extended headers like
`new file mode`/`rename from` fall through the awk and get numbered `0`.)

### Campaign end-state — read-economy is NOT a viable lever for codex cost

Three avenues, all closed:
1. Chunking (orchestrator + subagent): rare. Not a problem.
2. Reviewer source re-reads: ~85% legitimate verification; line-numbered package
   shows NO improvement (negative, n=4 vs n=12). Do not ship.
3. The real codex cost driver is architectural — no prompt caching, so each turn
   reprocesses full context (root-caused earlier in the campaign). Not
   addressable by superpowers skill content.

Net: the `read-economy-review-package-linenum` change is committed (09f82b3) but
should NOT be proposed to core — the project bar requires eval evidence of
improvement and there is none. Recommend abandoning the branch.

### Matched before/after (sdd-tiny, 6 FIX vs 3 clean DEV) — confirms NEGATIVE

Ran a matched dev-baseline-vs-fix set (same container/day). Result:
- Verdict: FIX 6/6 pass, DEV 3/3 pass — quality preserved, no regression.
- Cost (coding-agent est): FIX mean $4.45, DEV mean $4.24 — NEUTRAL. Run-to-run
  variance is enormous ($3.5–5.5; the FIX sub-batches alone averaged $4.90 vs
  $3.56), swamping any package-size effect. The bigger package does not show up.
- Reviewer source-reads: FIX mean 5.5 vs DEV mean 3.3 — NOT reduced (higher if
  anything; noise). Crucially, DEV reviewers already cite package-only 2–3×/run
  WITHOUT line numbers — so missing numbers were never what forced the re-reads.

Operational note (cost of the run): Phase-2 wave-2 of the dev baseline WEDGED
for ~2 days (3 reps returned `indeterminate`; gauntlet's 45m max-time did not
terminate them — they hung below it, likely codex/network/tmux). The queued
sdd-go-fractals before/after timed out waiting and never ran. Container drained
and recovered clean afterward. Lesson for re-runs: per-rep hard host-side
timeout + lower parallelism; do not trust gauntlet max-time to bound a wedged
codex session.

FINAL: line-numbering the review package is quality-neutral, cost-neutral, and
does NOT reduce reviewer reads. Do not ship. Read-economy remains a non-lever
for codex cost (architectural: no prompt caching).

## Dropped: the orchestrator read-economy wording change

`references/codex-tools.md` on dev contains NO read-economy guidance (it's
subagent-config + git-detection + app-finishing). "Strengthen the pointer to
compel reading it" (validated as a delivery mechanism, D4=100%) would require
ADDING "cat whole files" content — but the campaign's own evidence is that
windowed chunking is rare, so that content would be a speculative fix (the kind
this repo rejects). Not pursuing it. The evidence-backed orchestrator-read
result this campaign produced is null; the only shippable change is the
review-package line-numbering above.

## Docs/tooling to make this easier next time (TODO)

Friction hit while setting this campaign up — worth smoothing in docs/helpers:

- **Variant roots for non-bootstrap skill files.** `harnesses/build-variant-roots.py`
  only swaps `using-superpowers/SKILL.md`. Testing a `references/codex-tools.md`
  change meant hand-rolling `git archive HEAD | tar -x` into two trees + editing
  one. A generic "build a variant root swapping path X for content Y" helper (or a
  `--swap <relpath>=<file>` flag) would remove the hand-roll.
- **scenario `setup.sh` exec bit.** `quorum check` correctly fails "setup.sh is
  not executable", but `quorum new` (scaffold) and `docs/scenario-authoring.md`
  should make it obvious up front (scaffold could chmod +x; doc could call it out
  next to the "checks.sh must NOT be executable" note).
- **before/after container dance.** Comparing two SUPERPOWERS_ROOTs means
  `evals-container down` + `up --superpowers-root <dir>` between conditions (one
  mount at a time). A documented helper to run "scenario × {root A, root B} × N
  reps" would save the manual swap loop.
- **obol spark pricing for live container runs.** Pricing `gpt-5.3-codex-spark`
  required staging an on-disk obol snapshot under the container HOME
  (`results/.container-home/.local/share/obol/current.json`) since the bundled
  table is compiled in. Either ship the obol rate (commit + rebuild) or document
  the OBOL_PRICING_DIR/on-disk-snapshot recipe in the appliance/container runbook.
