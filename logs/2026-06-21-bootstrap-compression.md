# Bootstrap compression campaign — hypothesis log

**Started:** 2026-06-21
**Driver:** Jesse + Bot
**Goal:** Dramatically reduce the token size of the `using-superpowers` bootstrap
(injected into EVERY session + every subagent by `hooks/session-start`) WITHOUT
degrading skill auto-triggering — primarily `brainstorming` and
`systematic-debugging`, with the other triggering scenarios as regression guards.

## Why this matters

The bootstrap is the single most-repeated piece of context in the whole system:
it is injected at the start of every Claude/Codex/etc. session and (per the
instruction-design doctrine) re-read many times over a long session. Every token
shaved is paid back on every session and every subagent spawn. Baseline today:

- `skills/using-superpowers/SKILL.md` = 121 lines / 853 words / 6107 chars on disk.
- Injected blob (SKILL.md + `<EXTREMELY_IMPORTANT>` envelope) = 6125 bytes,
  **~1651 tokens (estimate; exact count needs an x-api-key the subscription
  path doesn't provide).**

## Measurement infrastructure

| Tool | Path | What it does |
|---|---|---|
| Token meter | `harnesses/measure-bootstrap-tokens.py` | Reconstructs the exact injected blob; exact tokens via count_tokens API if `ANTHROPIC_API_KEY`, else chars/3.7 estimate. `BASELINE=… python3 … variant.md` prints a delta. |
| Triggering harness | `harnesses/triggering-harness.py` | Runs real headless `claude -p --plugin-dir <root>` in an isolated $HOME, deterministically checks skill-before-Write/Edit using quorum's exact `isSkillInvocation` logic. No LLM verifier. Runs on subscription OAuth. |
| Compression loop | `harnesses/compression-loop.py` (TODO after baseline validated) | For each variant SKILL.md: build a scratch plugin root, measure tokens, run the harness across models, tabulate pass-rate + token delta vs baseline. |

### Auth / cost model (decided 2026-06-21)
- **Subscription OAuth only** (Jesse's `claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN`).
- quorum FULL is **unavailable** on subscription (its `required_env` hard-requires
  `ANTHROPIC_API_KEY`, and the gauntlet verifier uses the Anthropic SDK / x-api-key).
- Therefore the deterministic headless harness is the iteration engine; quorum
  FULL confirmation is reserved for *if/when* an x-api-key is supplied.
- Exact token counts likewise need an x-api-key; until then token numbers are
  chars/3.7 estimates (fine for relative compression tracking).

## Method tiers (cheapest first, per autoresearch doctrine)
- **MICRO/triggering** = `triggering-harness.py`. The workhorse. Many reps × models × variants.
- **FULL** = quorum `bun run quorum run scenarios/superpowers-bootstrap …` — only with an x-api-key, for final confirmation of the winning variant.

## Scenarios under test
Primary objectives (optimize these): `superpowers-bootstrap` (brainstorming on
"react todo list"), `triggering-systematic-debugging`,
`brainstorming-resists-jump-to-implementation`.
Regression guards (must-not-break): `triggering-test-driven-development`,
`triggering-writing-plans`, `triggering-requesting-code-review`,
`triggering-dispatching-parallel-agents`, `triggering-executing-plans`,
`triggering-finishing-a-development-branch`.

## Hypotheses (pre-registered)

| # | Hypothesis | Method | Prediction | Status | Verdict |
|---|---|---|---|---|---|
| H0 | **Baseline fires.** The unmodified bootstrap triggers brainstorming + systematic-debugging reliably on opus, sonnet, AND haiku via the headless `-p` harness. | triggering, 3 reps × 3 models × 3 primary scenarios | If a model/scenario doesn't fire on baseline, it has no headroom → exclude or escalate to tmux. **GATE: if baseline won't fire, STOP.** | **CONFIRMED** | **27/27 PASS** (100%), every run `skill_idx=0`, zero anomalies. Baseline hash `918562bbba1c`. Full headroom. |
| H0b | **`-p` is faithful.** Single-shot `-p` triggers at rates comparable to quorum's interactive runs. | observe H0 trigger rates | If `-p` under-triggers, switch to tmux interactive drive. | **CONFIRMED** | `-p` triggers 100% on baseline incl. haiku; target skill is the FIRST tool call every time. No tmux needed. |
| H1 | **The graphviz digraph is dead weight for triggering.** Removing the ~28-line `dot` flowchart (replaced by 1–2 prose lines) holds pass-rate. | ablation vs baseline | Digraph is token-heavy and redundant with the prose Rule. | **CONFIRMED** | a-no-digraph (−21%) held systematic-debugging 3/3 on haiku; no trigger lost. |
| H2 | **Cross-platform "How to Access Skills" + "Platform Adaptation" can be compressed** without hurting Claude triggering. | ablation | Holds (on Claude). | **CONFIRMED (Claude only)** | b-no-platform (−17%) held 3/3. CAVEAT: untested on Codex/Gemini/Copilot — the content those harnesses actually read. |
| H3 | **The Red Flags table is load-bearing.** Removing/shrinking it degrades triggering. | ablation | Degrades. | **REFUTED (for triggering)** | c-no-redflags (−17%) held systematic-debugging 3/3. Red Flags is NOT load-bearing for the trigger. (May still matter for rationalization-resistance my probes can't measure — don't reformat it without broader evidence.) |
| H4 | **Aggressive minimal bootstrap** hits a large token cut with acceptable triggering. | ablation | Some degradation; find the knee. | **CONFIRMED** | g-minimal (−56%) held systematic-debugging AND brainstorming **5/5 across opus/sonnet/haiku** — identical to baseline. The knee is between −56% (holds) and −94%/z-null (breaks, 0/5). |

## Methodology guardrails (bought with past mistakes)
- Manually inspect transcripts behind automated pass/fail (scoring bugs are real).
- Ablate ONE lever at a time so effects are attributable.
- Zero variance across reps = the guidance landed; high variance = marginal.
- Treat single runs as noisy; require a stable delta across reps before believing it.
- Negative results recorded at equal billing to wins.
- Don't ship any bootstrap change without triggering evidence across all 3 models
  (project rule: behavior-shaping content has a very high bar).

## Findings

### 2026-06-21 — H0 baseline gate: CONFIRMED (27/27, 100%)
Baseline triggers brainstorming + systematic-debugging at 100% on opus/sonnet/haiku,
3 reps each, every run `skill_idx=0`. `-p` harness is faithful. Baseline hash `918562bbba1c`.

### 2026-06-21 — Haiku variant screen: ALL VARIANTS HELD (suspicious ceiling)
All 7 ablations held 3/3 on haiku across the 3 primary scenarios — including
`g-minimal` (−56%) and `c-no-redflags`. Zero variance across 72 haiku runs.

**This is a CEILING problem, not a win.** Likely cause: on these obvious prompts the
*other skills' own descriptions* (e.g. brainstorming's "You MUST use this before any
creative work") visible in the Skill tool carry the triggering load, so the bootstrap
CONTENT is nearly irrelevant for easy triggers. If true, the harness can't discriminate
a good bootstrap from a gutted one on these scenarios.

→ Running **z-null** (all triggering guidance stripped from the bootstrap) as the
decisive negative control.

### 2026-06-21 — z-null negative control (haiku, 5 reps): HARNESS HAS POWER, but signal localized
| scenario | baseline | z-null (empty bootstrap) |
|---|---|---|
| superpowers-bootstrap (brainstorming) | 3/3 | **5/5** (still fires) |
| brainstorming-resists | 3/3 | **5/5** (still fires) |
| triggering-systematic-debugging | 3/3 | **0/5** (collapsed) |

**Key findings:**
1. The harness discriminates — systematic-debugging triggering went 100%→0% with an empty bootstrap.
2. **brainstorming is bootstrap-INDEPENDENT** here: the brainstorming skill's own description
   ("You MUST use this before any creative work…") carries the trigger. So the two brainstorming
   scenarios are SATURATED and cannot measure bootstrap compression. systematic-debugging is the probe.
3. With z-null, the model still *investigated* (Read/Bash) but never *loaded the skill* — the
   bootstrap is what converts "look at the bug" into "load systematic-debugging first".
4. All a–g variants kept systematic-debugging at 3/3 because they all RETAIN `## Skill Priority`
   ("Fix this bug → systematic-debugging first"), which z-null removed. → bisect that content next.

**Revised H3:** the load-bearing content for systematic-debugging is NOT the Red Flags table
(c-no-redflags held 3/3) — candidates are `## Skill Priority` and/or the `EXTREMELY-IMPORTANT`
1% block. New ablations h/i/j target these.

### 2026-06-21 — Phase A probe map (baseline vs z-null, haiku, 3 reps)
| scenario | baseline | z-null | classification |
|---|---|---|---|
| superpowers-bootstrap (brainstorming) | 3/3 | 5/5 | SATURATED (description-driven) — not a probe |
| brainstorming-resists | 3/3 | 5/5 | SATURATED — not a probe |
| triggering-systematic-debugging | 3/3 | 0/5 | **DISCRIMINATING** (clean) |
| triggering-executing-plans | 3/3 | TBD | clean baseline; null pending |
| triggering-finishing-a-development-branch | 3/3 | TBD | clean baseline; null pending |
| triggering-dispatching-parallel-agents | 2/3 | TBD | weak baseline (noisy probe) |
| triggering-requesting-code-review | 2/3 | 0/2 | discriminating but weak baseline |
| triggering-test-driven-development | 0/3 | 0/3 | CONFOUNDED — haiku reaches for brainstorming instead of TDD (the agent DOES call a Skill first, just the wrong one). Not a probe. |
| triggering-writing-plans | 0/3 | 0/3 | CONFOUNDED — haiku jumps to code or picks brainstorming. Not a probe. |

**Takeaways:** the bootstrap's triggering value concentrates on skills with *weaker self-descriptions*
(systematic-debugging). Skills with imperative descriptions (brainstorming: "You MUST use this before
any creative work") self-trigger regardless. TDD/writing-plans are *captured* by brainstorming on haiku
— a skill-selection issue, separate from compression.

**Harness hardening (this session):** an `claude` auto-update mid-run swapped the binary and crashed a
sweep (FileNotFoundError) → loop read a stale results.json. Fixed: absolute `CLAUDE_BIN` via
`shutil.which`, `DISABLE_AUTOUPDATER=1` + `autoUpdates:false` in seeded config (also kills version drift),
and OSError is caught per-run instead of aborting the sweep.

### 2026-06-21 — Bisection first datapoint (surprise)
`h-no-skill-priority` (removed `## Skill Priority` incl. "Fix this bug → systematic-debugging first")
STILL triggered systematic-debugging (1/1). → the trigger is NOT carried by a single line; likely
REDUNDANT cues. If no single removal breaks it (only total gutting z-null does), aggressive compression
is safe. Phase B (z-null/h/i/j/f-lean/g-minimal × systematic/executing/finishing × haiku) tests this.

**Next:** (B) running; (C) confirm winner on discriminating probes × opus/sonnet/haiku × 5 reps.

### 2026-06-21 — Jesse review round (Q's after Phase C)
On the discriminating probe (systematic-debugging × opus/sonnet/haiku × 5 reps, errs=0):
| variant | tokens | opus | sonnet | haiku |
|---|---|---|---|---|
| baseline | 1651 | 5/5 | 5/5 | 5/5 |
| k-digraph-only (digraph replaces prose) | ~816 (−50%) | 5/5 | 5/5 | 5/5 |
| l-no-access (drop "Never read skill files…" + Platform Adaptation) | ~1292 (−22%) | 5/5 | 5/5 | 5/5 |
| m-no-subagent-stop | ~1619 (−2%) | 5/5 | 5/5 | 5/5 |
| o-lean-description (trigger-only desc, writing-skills SDO) | ~1640 | _running_ | | |

**Verdicts:**
- **Q2 (digraph-only):** YES — the graphviz digraph carrying the decision logic with prose
  stripped preserves triggering (5/5/5) at ~−50%, nearly as compact as g-minimal. Viable.
- **Q3 (drop the access line):** CONFIRMED safe — l-no-access holds 5/5/5.
- **Q4 (SUBAGENT-STOP):** correctness catch is valid — "skip this skill" has no referent when
  the content is injected as prose. m-no-subagent-stop does no harm at top level (5/5/5), but
  the *actual* subagent-skip behavior CANNOT be measured by this top-level harness — needs a
  subagent-dispatch test. Recommend rewording (preserve intent, fix referent) rather than blind removal.
- **Q1 (plan-mode over-trigger): UNMEASURABLE with `-p`.** 0/242 runs touched EnterPlanMode/
  ExitPlanMode, but headless `-p` doesn't enter plan mode (it's an interactive/TUI behavior).
  This is a real blind spot — and directly relevant since the digraph is the part that routes
  plan-mode. Needs an interactive tmux harness (or quorum) to test. NOT yet answered.

### 2026-06-21 — New tool-mapping evals authored + headless-validated
Both scenarios pass `quorum check` and are non-vacuous on Claude (validate-toolmap-evals.py,
sonnet+haiku × 3 reps):
- `claude-tool-mapping-applied` (NOT told to read the file): subagent dispatched 3/3 sonnet,
  3/3 haiku; `claude-code-tools.md` read **0/6**.
- `global-tool-mapping-comprehension` (told to consult the mapping): sonnet read 3/3 / dispatched
  2/3 (one rep spelunked in Bash); haiku dispatched 3/3 / read **0/3** (knew it without reading).

**Finding (pre-confirms the queued audit):** on Claude the agent resolves Superpowers action
language to the correct native tool WITHOUT consulting `claude-code-tools.md` — the file is
largely redundant *for tool resolution*. Supports keep-on-demand + compressing the platform
pointer on Claude + Jesse's ≥50%-redundant hypothesis. `tool-called Agent` alone can't prove
file-comprehension (haiku passes without reading) — the loading diagnostic / gauntlet AC is what
separates "read it" from "knew it".

### 2026-06-22 — Faithful quorum/gauntlet re-test (Jesse: `-p` is only a screen)
- Got an x-api-key (`prime-radiant-inc/serf/.env`) for the gauntlet verifier. **Exact** baseline
  tokens (count_tokens API) = **1698**; a-no-digraph 1288 (−24%), p-recommended 905 (−47%),
  k-digraph-only 879 (−48%), g-minimal 708 (−58%). FULL triggering runs cost ~$0.25–0.65 each.
- **Auth saga → apiKeyHelper fix.** quorum's interactive (tmux) claude agent kept popping macOS
  Keychain / "use this API key?" dialogs; claude 2.1.185 broke the undocumented
  `customApiKeyResponses` pre-approval. Fixed by switching the claude agent to **apiKeyHelper**
  auth (outranks the keychain, not the env-key dialog) + stripping `ANTHROPIC_API_KEY` from the
  agent env. Quorum source edits (UNCOMMITTED): `src/agents/index.ts` ClaudeAgent.provision +
  `coding-agents/claude-context/launch-agent`. claude pinned 2.1.183 (autoUpdates off) for evals.
  Full detail: memory `reference_headless_claude_auth_for_evals`.
- **Matrix running:** `harnesses/quorum-matrix.sh` (REPS=2, JOBS=4) over baseline + a-no-digraph
  + p-recommended + g-minimal × {superpowers-bootstrap, triggering-systematic-debugging,
  cost-checkbox-over-trigger} × {opus,sonnet,haiku}. Aggregate with `harnesses/quorum-report.py`
  (verdicts + plan-mode scan). Results pending — compare vs the `-p` screen.

### 2026-06-22 — Faithful quorum/gauntlet RESULTS (matrix complete, n=2/cell, 72 runs)
Pass-rate [plan-mode count], faithful tmux/gauntlet. `quorum-report.py` fixed mid-run to scan the
coding-agent's own transcript jsonl (not trajectory.json, whose steps lack structured tool names)
for EnterPlanMode/ExitPlanMode. baseline-rep1 had a stale pre-compaction batch (out-root reused →
quorum appends); moved to `results/matrix-baseline-rep1/_stale-pre-recovery/`. Numbers below are
the clean fresh run.

```
superpowers-bootstrap (brainstorming)     opus    sonnet   haiku
  baseline                                 2/2     2/2     2/2
  a-no-digraph (-24%)                       2/2     2/2     2/2
  p-recommended (-47%)                      2/2     2/2     2/2
  g-minimal (-58%)                          2/2     2/2     2/2
triggering-systematic-debugging
  baseline                                 2/2     2/2     1/2  ← lone baseline-haiku miss
  a-no-digraph                              2/2     2/2     2/2
  p-recommended                             2/2     2/2     2/2
  g-minimal                                 2/2     2/2     2/2
cost-checkbox-over-trigger (pass = brainstorming NOT fired)
  baseline                                 1/2     0/2     1/2  ← over-fires even at full baseline
  a-no-digraph                              0/2     0/2     0/2
  p-recommended                             1/2     0/2     0/2
  g-minimal                                 0/2     0/2     1/2
plan-mode tool use across ALL 72 runs: 0/72
```

**Conclusions (faithful instrument confirms the `-p` screen):**
- **Brainstorming (primary):** every variant down to g-minimal (−58%) = 16/16 perfect across
  opus/sonnet/haiku. Compression does NOT hurt the primary trigger. Screen and ground-truth agree.
- **systematic-debugging:** every COMPRESSED variant = 6/6 perfect per variant; only miss is one
  baseline-haiku run. No compressed variant regressed; the weak-description skill keeps triggering
  at −58%. Screen and ground-truth agree.
- **Plan-mode over-trigger (Jesse Q1): NONE. 0/72** across every variant/model/scenario — even at
  full baseline. The "About to enter plan mode?" digraph node is not causing gratuitous plan mode.
  (Unmeasurable in `-p`; this is the faithful instrument's unique answer.)
- **cost-checkbox over-trigger guard:** mostly FAILS everywhere INCLUDING baseline (best baseline
  cell 1/2). No baseline headroom → cannot discriminate compression effects at n=2. Pre-existing
  over-eager brainstorming on trivial requests; needs its own investigation, NOT a blocker here.
- **Attribution of Jesse's Q3/Q4:** p-recommended (−47%) *removed* both the "Never read skill files
  manually" access line (Q3) AND the `<SUBAGENT-STOP>` block (Q4) and passed all triggers clean →
  removing them does not hurt triggering. CAVEAT: the matrix's agent-under-test is top-level, never
  a dispatched subagent, so it does NOT directly test Q4's actual concern (the subagent-stop block
  misfiring when the bootstrap is injected as PROSE in a subagent). A subagent-dispatch scenario is
  still needed to prove the subagent-stop block is safe/correct to change for that case.

**Caveats:** n=2 per cell (bootstrap+systdebug signals clean enough to conclude; over-trigger too
noisy). Claude-only (opus/sonnet/haiku). g-minimal/p-recommended reformat cross-platform content +
the tuned Red Flags table → a NON-CLAUDE harness check is still wanted before shipping the
aggressive variants. Ship-confidence order unchanged: a-no-digraph (lowest risk, −24%) <
p-recommended (−47%) < g-minimal (−58%); all three pass the two primary triggers faithfully.

### 2026-06-22 — Q4 mechanism investigation + new subagent-dispatch scenario (Jesse: "do 3 first")
Plan: (3) author a subagent-dispatch scenario to actually test Q4; (2) faithfully ablate the
individual Q-variants k/l/m/o; then test on other harnesses; then decide which variant ships.

**Q4 mechanism — three confirmed findings about the `<SUBAGENT-STOP>` block:**
1. **The block is INERT in the prose-injection path.** The SessionStart hook
   (`hooks/session-start`) injects the WHOLE SKILL.md as prose, but its matcher is
   `startup|clear|compact` — subagent dispatch is NOT a SessionStart event. Empirically confirmed
   by a direct probe subagent: it sees NONE of the bootstrap prose (no "You have superpowers", no
   `<EXTREMELY_IMPORTANT>`, no subagent-stop line, no Red Flags) — only the `using-superpowers`
   entry in the Skill *registry*. So the block only appears in the MAIN session, where the agent is
   never a subagent → its condition is never true where it lives. (Jesse's "wrong for prose
   sessions" = mechanically confirmed.)
2. **When subagents DO over-trigger, they bypass the gate.** A realistic probe subagent given a
   "let's build X" task invoked `superpowers:brainstorming` DIRECTLY from the registry, never
   loading `using-superpowers` (where the gate lives). So the gate can't catch the actual
   over-trigger path. (Confound: that probe ran with Jesse's global CLAUDE.md, which primes
   brainstorming — see #3.)
3. **In the ISOLATED faithful env, baseline subagents stay on task.** The new scenario's first
   faithful baseline-opus run: subagent dispatched, built todo.py with Bash/Read/Write, did NOT
   invoke brainstorming. Opposite of the probe → the probe's over-trigger was driven by the
   personal CLAUDE.md, not the registry. quorum's isolation controls that confound.

**New scenario `subagent-dispatch-no-overtrigger`** (`evals/scenarios/`). Gauntlet drives the main
agent to delegate a fully-specified "build a todo CLI" task to ONE subagent (main agent = pure
dispatcher). post-checks: `tool-called Agent` (a subagent WAS dispatched) + `skill-not-called
superpowers:brainstorming` (subagent did not over-trigger). **Observability verified end-to-end:**
the claude `session_log_glob` is `**/*.jsonl` (recursive) and capture MERGES all logs incl. the
subagent sidechain (`projects/<slug>/<uuid>/subagents/agent-<id>.jsonl`); the merged
`trajectory.json` of the validation run contained BOTH the main `Agent` dispatch AND the subagent's
`Bash/Read/Write` — so a subagent brainstorming call WOULD be caught (check is not vacuous). The
Gauntlet-Agent's own reasoning confirmed it read the subagent log. `quorum check` passes; single
faithful run passes ($0.51). Scenario restricted by nothing yet (claude-family is where it's
meaningful; mechanism verified claude-only).

**Step-2 ablation (running):** `harnesses/quorum-ablation.sh` (REPS=2 JOBS=4), out-roots
`results/abl-<variant>-rep<r>` (separate from matrix-*). Variants isolate ONE change each; exact
tokens vs baseline 1698: k-digraph-only 879 (−48%, digraph-only/English removed), l-no-access 1355
(−20%, access section removed), m-no-subagent-stop 1657 (−2.4%; block is only ~41 tok — value is
correctness not size), o-lean-description 1688 (−0.6%; ~10 tok — value is doctrine). Scenarios:
both primary triggers for all 5 variants (incl. baseline control); the Q4 scenario only for
baseline + m-no-subagent-stop (the A/B). Roots built by `harnesses/build-variant-roots.py`.
Aggregate with `python3 harnesses/quorum-report.py abl` (the report now takes a prefix arg).

### 2026-06-22 — ABLATION RESULTS (complete, 72 runs, n=2/cell) — every individual cut is SAFE
```
superpowers-bootstrap (brainstorming)         opus   sonnet  haiku
  baseline / k / l / m / o                     2/2    2/2    2/2   (ALL five variants)
triggering-systematic-debugging
  baseline / k / l / m / o                     2/2    2/2    2/2   (ALL five variants)
subagent-dispatch-no-overtrigger (Q4 A/B)
  baseline                                     2/2    2/2    2/2
  m-no-subagent-stop                           2/2    2/2    2/2   ← IDENTICAL to baseline
plan-mode across all 72 runs: 0/72
```
**Per-question answers (all clean):**
- **Q2 (digraph replaces English entirely):** k-digraph-only (−48%, English prose removed) preserves
  BOTH primary triggers 2/2 across all 3 models. Yes — the digraph can stand alone.
- **Q3 (drop the "Never read skill files manually" access section):** l-no-access (−20%) preserves both
  triggers 2/2 across all models. Safe to remove.
- **Q4 (drop `<SUBAGENT-STOP>`):** m-no-subagent-stop is IDENTICAL to baseline on the subagent
  over-trigger scenario (6/6 vs 6/6) AND preserves both primary triggers. A clean null result.
  Combined with the mechanism findings (block inert in the prose path; bypassed when over-triggering
  actually happens), the block is VESTIGIAL → safe to remove. Its ~41-tok size is incidental; the
  real justification is correctness.
- **o-lean-description:** leaning the description per writing-skills doctrine preserves both triggers
  2/2 across all models. Safe.
- This baseline is CLEANER than step-1's (which had one baseline-haiku systematic-debugging miss;
  here baseline is 2/2 everywhere) → that step-1 miss was noise.

**Caveat:** n=2/cell detects "did it break", not small rate shifts; the primary-trigger signal is
6/6-per-variant-per-scenario (solid for a no-regression call). Claude-only. The cross-platform
(non-Claude) check for the bundled aggressive variants is the NEXT step, then the ship decision.

### 2026-06-22 — CROSS-HARNESS (non-Claude) RESULTS — caveat RESOLVED
Gate first: baseline brainstorming triggers on BOTH codex (gpt) and gemini (gemini-3.5-flash) —
instrument valid (the skill detector catches codex's native load + gemini's `activate_skill`). NB:
my first smoke was indeterminate ONLY because I omitted the Gauntlet VERIFIER's ANTHROPIC_API_KEY;
codex/gemini agent auth is separate (codex = host login; gemini = GEMINI_API_KEY). Both harnesses
read the SAME swapped SKILL.md via `stageSuperpowersPlugin` (gemini synthesizes its own GEMINI.md
at the staged skills), so the variant roots inject the variant bootstrap. `harnesses/quorum-xharness.sh`.
```
                          codex    gemini      (n=2/cell, 24 runs, 0 indeterminate)
superpowers-bootstrap (brainstorming)
  baseline / g-minimal / p-recommended   2/2   2/2   (all three, both harnesses)
triggering-systematic-debugging
  baseline / g-minimal / p-recommended   2/2   2/2   (all three, both harnesses)
```
- **The aggressive variants do NOT break non-Claude triggering.** Even p-recommended — which removed
  the "How to Access Skills" section INCLUDING the Codex skill-loading line + the Platform-Adaptation
  pointer — triggers brainstorming AND systematic-debugging 2/2 on codex. g-minimal (dropped the
  tool-mapping pointer) likewise 2/2 on both. The cross-platform caveat blocking the aggressive
  variants is **resolved**.
- **Secondary finding (feeds the claude-code-tools.md audit):** p-recommended removed codex's
  textual skill-loading instruction and codex STILL triggered — codex skills "load natively" via the
  runtime, so the per-platform skill-loading prose in the bootstrap is largely redundant ON those
  harnesses. Supports Jesse's "≥50% of that content is redundant" hypothesis.
- ([pmN] is Claude-only — codex/gemini have no `.claude/projects` transcript, so their cells show
  pm0 = "no data", and the footer reads 0/0 trajectories scanned. Not a real plan-mode measurement.)

### 2026-06-22 — CONFIDENCE REP RUN (Jesse held for more reps before shipping)
+8 reps of baseline + g-minimal + p-recommended × {bootstrap, systematic-debugging} × {opus,sonnet,
haiku} = 144 runs (`harnesses/quorum-reps.sh`; aggregate `quorum-report.py reps`). POOLED with
step-1 matrix (+ abl baseline) for the final per-cell n:
```
superpowers-bootstrap (brainstorming) — POOLED
  baseline 36/36 · g-minimal 30/30 · p-recommended 30/30      (100%, ZERO misses anywhere)
triggering-systematic-debugging — POOLED by model
  variant          opus    sonnet   haiku
  baseline         12/12   12/12   11/12   ← baseline ITSELF misses this cell
  p-recommended    10/10   10/10   10/10
  g-minimal        10/10   10/10    9/10   ← the one miss
plan-mode across all 144 reps: 0/144
```
**The one g-minimal miss is NOT a compression regression — it's a pre-existing haiku property.**
Baseline misses the SAME haiku/systematic-debugging cell at the SAME rate (92% vs g-minimal 90%);
haiku occasionally jumps straight to investigating (Read/Glob/Bash, no Skill call) without loading
the weak-description skill EVEN AT FULL BASELINE. g-minimal 9/10 vs baseline 11/12 is one run apart
— statistically indistinguishable. The failing run (`reps-g-minimal-rep3/...haiku...`): haiku did
5×Read, 2×Glob, 5×Bash, never called systematic-debugging, made no edits. Conclusion: at n≈10/cell
there is NO evidence of a compression-induced triggering drop; brainstorming is 100% at every
compression level; the only failure mode is haiku under-triggering systematic-debugging, which is
bootstrap-size-independent. p-recommended happens to be 10/10 on that cell vs g-minimal 9/10 — a
one-run difference (noise), but it gives p-recommended a marginally cleaner record if Jesse wants
the safest aggressive option.

### 2026-06-22 — METHODOLOGY CORRECTION (Jesse): the brainstorming test was a NULL instrument
Jesse, on seeing "nothing breaks triggering": is one of the tests "Let's make a react todo list"
watching for brainstorming? YES — `superpowers-bootstrap` sends exactly that. BUT that test is NOT
sensitive to bootstrap compression: brainstorming has a STRONG skill *description*, so the agent
reaches for it from the Skill REGISTRY regardless of the bootstrap (the `-p` screen's z-null fired
brainstorming 5/5). So "brainstorming 100% across all variants" is largely uninformative about
compression — and I leaned on the `-p` screen (which Jesse told me to distrust) to wave it away.
Two gaps this exposed:
1. The campaign's only genuinely bootstrap-DEPENDENT discriminator was `systematic-debugging` (1
   skill). Thin basis for "compression doesn't hurt triggering."
2. I never ran the z-null NEGATIVE CONTROL in the FAITHFUL harness — so I hadn't proven the
   instrument can even detect bootstrap damage faithfully (only via the distrusted `-p`).
Jesse's steer: test BRAINSTORMING (the gateway skill), not (just) systematic-debugging. Key insight:
the EASY brainstorming prompts (`superpowers-bootstrap` react-todo; `brainstorming-companion`
"help me design a dashboard") explicitly cue building/design → brainstorming self-triggers → null
instrument. The HARD, bootstrap-dependent one is `brainstorming-resists-jump-to-implementation`
("build a notifications system" — looks like a build task, no design cue; the agent must RECOGNIZE
it's design-worthy). It's the calibration twin of `cost-checkbox-over-trigger` (same fixture).
**Running `quorum-brainstorm-ctrl.sh`:** baseline + z-null + g-minimal + p-recommended ×
{resists-jump (MUST fire), bootstrap (easy anchor), companion (design), cost-checkbox (MUST NOT
fire)} × haiku × 3 reps. z-null is the sensitivity gate: if it makes haiku jump-to-code on
resists-jump while baseline brainstorms, the instrument has teeth on brainstorming. SHIP DECISION
ON HOLD pending this.

### 2026-06-22 — Brainstorming control RESULTS + cross-harness z-null sweep (running)
Brainstorming-centered control (haiku, n=3): **z-null FIRES brainstorming 3/3 on the HARD
design-worthy "build a notifications system" prompt** (and on react-todo, and the dashboard design
request). So brainstorming UNDER-triggering is bootstrap-INDEPENDENT — it comes from the
brainstorming skill's own registry description, not the bootstrap. CONFIRMED faithfully (not just
the -p screen). The bootstrap's only measurable brainstorming effect is OVER-triggering: on the
trivial cost-checkbox (pass = brainstorming does NOT fire) — z-null 3/3, p-recommended 3/3,
baseline 1/3, g-minimal 0/3. i.e. MORE bootstrap pressure (1% rule / Red Flags) → MORE
over-triggering on trivial tasks; leaner/no bootstrap calibrates BETTER. g-minimal is the WORST on
calibration, p-recommended the best (== z-null). n=3 haiku — a strong LEAD, not a verdict.

**Now running the cross-harness z-null SENSITIVITY SWEEP** (Jesse: "run all the triggering scenarios
against claude code and gemini and kimi with z-null"). `harnesses/quorum-zsweep.sh`: baseline +
z-null × 12 triggering scenarios × {claude-haiku, gemini, kimi} × 3 reps = 216 runs (~$110, ~3-4h).
Goal: which skills actually depend on the bootstrap, across harnesses (z-null FAIL where baseline
PASSES = real dependence). All 3 harness instruments gated & PASS at baseline (codex/gemini earlier;
kimi smoke just now — auto-triggered brainstorming, first call Skill(brainstorming), think-trace "I
MUST invoke the brainstorming skill"). Aggregate: `quorum-report.py zsweep`.
- **kimi auth gotcha:** the env-key var is **`KIMI_MODEL_API_KEY`**, NOT `KIMI_API_KEY` (kimi.ts:148).
  Renamed it in `evals/.env`; verified env-key path active (`__kimi_env_model__` in the smoke).
  OAuth fallback exists from host ~/.kimi-code creds. kimi cost shows "UnpricedModel" (n/a) — fine.

### 2026-06-22 — CROSS-HARNESS z-null SWEEP RESULTS (216 runs) — the bootstrap's real triggering map
baseline vs z-null × 12 triggering scenarios × {claude-haiku, gemini, kimi} × 3 reps. Key grid
(claude-haiku, the clean instrument; baseline→z-null):
```
  requesting-code-review      3/3 -> 0/3   LOAD-BEARING (strong; haiku just talks, 0 tool calls — verified)
  systematic-debugging        2/3 -> 1/3   mild
  dispatching-parallel-agents 3/3 -> 2/3   mild
  executing-plans             3/3 -> 2/3   mild
  brainstorming-companion     3/3 -> 2/3   mild
  superpowers-bootstrap       3/3 -> 3/3   NOT (brainstorming self-triggers)
  brainstorming-resists-jump  3/3 -> 3/3   NOT (self-triggers even on the HARD prompt)
  finishing-branch/TDD/mid-conversation/subagent-dispatch  3/3 -> 3/3   NOT
  writing-plans               1/3 -> 0/3   baseline broken -> not a clean instrument
```
- **Brainstorming is bootstrap-INDEPENDENT on ALL 3 harnesses** (fires under z-null everywhere incl.
  the hard prompt). Confirmed faithfully. So all prior "compression preserves brainstorming" results
  measured an unbreakable thing.
- **The bootstrap is genuinely load-bearing for weak-description skills on the WEAKEST model
  (claude-haiku)** — strongest at requesting-code-review (3/3→0/3, verified: haiku responds in plain
  text, zero tool calls, no Skill). The instrument HAS TEETH there.
- **gemini & kimi are bootstrap-ROBUST** — z-null barely degrades them (gemini even IMPROVED on
  test-driven/writing-plans → its baseline fails are flakiness, not bootstrap-dependence). gemini is
  a noisy instrument (baseline 1/3 on two scenarios, 0/3 subagent-dispatch). Weight claude-haiku most.
- **THE GAP this exposes:** the compression matrices tested bootstrap + systematic-debugging — NEVER
  requesting-code-review (the actual load-bearing cell). So whether g-minimal/p-recommended preserve
  the triggering the bootstrap drives was UNTESTED.

**RUNNING: load-bearing compression test** (`quorum-loadbearing.sh`, task btb19v3e5): baseline +
z-null + a-no-digraph + p-recommended + g-minimal × {requesting-code-review, systematic-debugging,
dispatching-parallel-agents, executing-plans, brainstorming-companion, cost-checkbox} × claude-haiku
× 5 reps = 150 runs. z-null = in-batch control (must fail code-review). Decides whether compression
preserves the triggering that matters + the over-trigger calibration. Aggregate: `quorum-report.py lb`.

### 2026-06-22 — ⚠️ CONFOUND FOUND: CLAUDE.md leaks into the agent-under-test (campaign results suspect)
Jesse: "root cause the failed tool calls by restarting the sessions and interrogating them." Resuming
the failed requesting-code-review sessions, the agents (a) all RECOGNIZED the skill matched, (b) got
derailed by the scenario's deliberately-fake SHAs, and (c) cited CLAUDE.md ("just do it", "94% PR
rejection"). The CLAUDE.md citations were partly confabulated (my resume re-loaded it), but pointed at
the real bug, CONFIRMED by canary test:
- **Claude discovers CLAUDE.md by walking UP the cwd tree**, not from $HOME. quorum's coding-agent-
  workdir is `<repo>/superpowers/evals/results/<run>/coding-agent-workdir` — nested in the repo AND in
  /Users/jesse — so the agent loads `evals/CLAUDE.md` + `superpowers/CLAUDE.md` (94% rejection) +
  `~/.claude/CLAUDE.md` (Jesse's GLOBAL, which mandates brainstorm/TDD/root-cause-debug). The throwaway
  $HOME does NOT help. Ground truth: unique canary phrases ("slop that's made of lies" → superpowers
  CLAUDE.md; "Strange things are afoot at the Circle K" → global) returned VERBATIM from a host eval
  workdir; from a /tmp cwd they did NOT.
- **Impact:** every claude agent-under-test already had superpowers behaviors via leaked CLAUDE.md
  regardless of bootstrap variant → almost certainly why "nothing breaks triggering" / "brainstorming
  is bootstrap-independent." ALL host-run triggering results (steps 1-2, xharness, brainstorm-ctrl,
  zsweep, loadbearing) are confounded and need clean re-validation.
- **Methodology notes:** don't trust an agent's SELF-REPORT of its loaded context (haiku confabulates
  paths + post-hoc rationalizations); use verbatim canary phrases. Memory: [[reference_eval_claudemd_leak]].

### 2026-06-22 — FIX: run quorum in Docker (Jesse's idea); clean re-run started
`scripts/evals-container` (image superpowers-evals:local ~14GB, already built). Container HOME=
/workspace/evals/results/.container-home (no real home → global NOT loaded); superpowers mounted at
/workspace/superpowers, a SIBLING of /workspace/evals (NOT in workdir ancestry → contributor CLAUDE.md
NOT loaded). **Verified in-container canary: A(superpowers)=NO, B(global)=NO, C(evals/CLAUDE.md)=YES**
— both dangerous leaks gone; residual evals/CLAUDE.md is benign (harness internals, constant across
variants). Credentials: `evals/.env.container` (ANTHROPIC+GEMINI+KIMI_MODEL). Variant testing: the
container quorum wrapper hardcodes SUPERPOWERS_ROOT=/workspace/superpowers, so re-`up --superpowers-root
/tmp/sp-var-<variant>` per variant. RUNNING: clean baseline arm (`results/cclean-baseline-rep*`,
claude-haiku, 5 discriminating scenarios, 3 reps); then z-null arm (re-up) to get the TRUE
bootstrap-dependence map without the CLAUDE.md confound — esp. does brainstorming still self-trigger
under z-null when the global CLAUDE.md is gone?

### 2026-06-22 — CLEAN (Docker) GRID — the trustworthy result (75 runs, claude-haiku, n=3, 0 indet)
All in-container (no CLAUDE.md leak; canary-verified). baseline+z-null+a-no-digraph+p-recommended+
g-minimal × 5 scenarios × 3 reps.
```
                                    baseline  a-no-digraph  p-recommended  g-minimal  z-null
superpowers-bootstrap (brainstorm)    3/3       3/3          3/3           3/3        3/3
brainstorming-resists-jump (HARD)     3/3       3/3          3/3           3/3        3/3
triggering-systematic-debugging       3/3       3/3          3/3           3/3        0/3   <-teeth
triggering-requesting-code-review     3/3       3/3          3/3           3/3        1/3   <-teeth
cost-checkbox (pass = NOT fire)       0/3       0/3          0/3           0/3        1/3
```
**Confound removal CONFIRMED compression-is-safe (didn't reverse it):**
- Instrument now genuinely discriminates: z-null collapses on the load-bearing cells (systematic-
  debugging 0/3, code-review 1/3) vs baseline 3/3. NOT saturated.
- ALL 3 compression candidates incl g-minimal (−58%) HOLD the load-bearing triggering at baseline
  (3/3 / 3/3) while z-null falls apart → the compressed bootstraps keep exactly the content that
  drives weak-description-skill triggering. Compression safe on the clean, teeth-having instrument.
- Brainstorming bootstrap-INDEPENDENT confirmed clean (3/3 everywhere incl z-null, easy AND hard).
- Calibration: NO difference between candidates — every bootstrapped variant over-fires cost-checkbox
  equally (0/3); the earlier "g-minimal worst / p-recommended best" was confound noise (gone clean).
**Caveats:** n=3/cell (clean dynamic range is large — baseline 3/3 vs z-null 0/3 — so "holds vs
collapses" is well-supported, but n=3 can't catch a small drop). claude-haiku only (the discriminator).
Only the load-bearing cells re-tested clean (systematic-debugging is the clearest; others like
dispatching-parallel-agents/executing-plans showed mild HOST dependence, not yet re-tested clean).

### 2026-06-22 — FULL CLEAN MAP phase 1 (Docker, all 13 scenarios, baseline vs z-null, haiku n=3)
Jesse chose "full clean re-map". Complete clean bootstrap-dependence map (baseline → z-null):
```
NOT bootstrap-dependent (z-null == baseline 3/3):
  superpowers-bootstrap, brainstorming-resists-jump, brainstorming-companion,
  dispatching-parallel-agents, finishing-a-development-branch, subagent-dispatch
STRONGLY load-bearing:
  triggering-systematic-debugging   3/3 -> 0/3
  triggering-requesting-code-review 3/3 -> 1/3
mildly load-bearing (1-run drop @ n=3 — confirm in phase 2):
  triggering-executing-plans 3/3 -> 2/3 ; triggering-test-driven-development 3/3 -> 2/3 ;
  mid-conversation-skill-invocation 3/3 -> 2/3
NOT a clean instrument: triggering-writing-plans (baseline 1/3 — fails at baseline)
over-trigger: cost-checkbox 0/3 -> 1/3 (bootstrap CAUSES over-firing)
```
Bootstrap's genuine triggering value is CONCENTRATED in 2 weak-description skills (systematic-
debugging, requesting-code-review). All brainstorming scenarios self-trigger clean (3 of them).

**RUNNING phase 2** (`quorum-cleanmap2.sh`, task bj6w4a10f): deepen the 5 load-bearing cells
(2 strong + 3 mild) across ALL 5 variants (baseline, z-null, a-no-digraph, p-recommended, g-minimal)
+5 reps (rep4-8) → pooled n~8. Confirms whether the compression candidates hold the cells that
genuinely depend on the bootstrap. ~125 runs, Docker, claude-haiku. Aggregate: `quorum-report.py cclean`.

### 2026-06-23 — FULL CLEAN MAP phase 2 + TDD root-cause (Docker, haiku, pooled n)
Final clean grid on load-bearing cells (baseline/a-no-digraph/p-recommended/g-minimal vs z-null):
```
  systematic-debugging   8/8 / 8/8 / 8/8 / 8/8  vs z-null 4/8   ★ compression SAFE
  requesting-code-review 8/8 / 8/8 / 8/8 / 8/8  vs z-null 2/8   ★ compression SAFE
  executing-plans        8/8 / 5/5 / 5/5 / 5/5  vs z-null 3/8   ✓ compression SAFE (load-bearing confirmed)
  mid-conversation       8/8 / 5/5 / 5/5 / 5/5  vs z-null 7/8   (barely load-bearing)
  test-driven-development 4/8 / 0/5 / 3/5 / 1/5 vs z-null 3/8   ⚠ investigated below
```
**TDD root cause (Jesse: "investigate why TDD is flaky"):** the failures are NOT no-skill or a
compression regression — they're brainstorming-vs-TDD SKILL COMPETITION. Inspecting first-skill per
run: every BOOTSTRAPPED variant's TDD "failures" = `Skill(brainstorming)` (agent engaged a process
skill, just chose brainstorming over TDD on the borderline "implement email validation" request);
ONLY z-null's failures = `(no skill invoked)`. So the TDD scenario conflates (1) does the bootstrap
make the agent engage ANY process skill — YES, load-bearing (z-null ~50% no-skill; every bootstrapped
run incl g-minimal engaged a skill, ZERO no-skill) — with (2) is it specifically TDD vs brainstorming
— a bootstrap-size-INDEPENDENT ~50/50 toss-up (baseline picks TDD only 4/8). The incoherent ordering
(a-no-digraph 0/5 < z-null) dissolves: a-no-digraph engaged a skill 5/5 (all brainstorming), z-null
engaged nothing 5/8. **No compression regression; compression preserves skill-engagement on every
load-bearing cell.** (Aside for quorum: the TDD scenario is a flawed instrument — brainstorming
out-competes TDD on a feature request; it can't cleanly isolate TDD-triggering.)

## SHIP DECISION INPUTS (CLEAN, Docker — fully validated; TDD smudge resolved) — Jesse's step 1
**Bottom line:** on confound-free Docker data with a discriminating instrument (z-null collapses),
compression to **g-minimal (−58%, 708 tok vs 1698)** preserves skill-engagement on ALL load-bearing
cells (systematic-debugging, requesting-code-review, executing-plans), brainstorming self-triggers
regardless, plan-mode 0 everywhere. a-no-digraph (−24%) and p-recommended (−47%) likewise clean.
Recommendation: ship g-minimal.

### 2026-06-23 — CLEAN CROSS-HARNESS (Docker) — last gap closed; g-minimal safe on codex/gemini/kimi
baseline + z-null + g-minimal × {codex, gemini, kimi} × {superpowers-bootstrap, systematic-debugging,
requesting-code-review} × 3 reps (81 runs, `results/cxh-*`):
```
                       codex      gemini   kimi
superpowers-bootstrap  base 3/3 / g 3/3 / z 2/3   |  all 3/3  |  all 3/3
systematic-debugging   base 2/3*/ g 3/3 / z 1/3   |  all 3/3  |  base 3/3 / g 3/3 / z 1/3
requesting-code-review base 3/3 / g 3/3 / z 2/3   |  all 3/3  |  all 3/3
```
*codex baseline-2/3 + z-null dips are mostly codex app-server INFRA flakes ("app-server returned no
response") + 1 empty-capture, not triggering signal. **g-minimal == baseline on every cell/harness**
while z-null genuinely degrades on codex + kimi (systematic-debugging 1/3) → compression safe
cross-platform; bootstrap load-bearing on codex/kimi too; gemini self-triggers (bootstrap-robust).
**VALIDATION COMPLETE: g-minimal (−58%) clean-confirmed across opus/sonnet/haiku/codex/gemini/kimi.**
Next: prep ship diff (superpowers PLUGIN repo skills/using-superpowers/SKILL.md → g-minimal) +
RELEASE-NOTES + version bumps for Jesse's review. (Plugin repo is on branch `dev`; evals work is on
branch `bootstrap-compression-evals`.)
Exact tokens vs baseline 1698: a-no-digraph 1288 (−24%), p-recommended 905 (−47%), g-minimal 708
(−58%). All three preserve BOTH primary triggers faithfully on Claude {opus,sonnet,haiku}. The two
aggressive ones (p-recommended, g-minimal) ALSO preserve both triggers on codex + gemini.
plan-mode 0 across all Claude runs. The individual Q-cuts (digraph-only, no-access, no-subagent-stop,
lean-description) are each independently safe. Remaining honest caveats: n=2/cell (detects breakage,
not <~15% rate shifts); the cost-checkbox over-trigger axis has no baseline headroom (pre-existing,
orthogonal); g-minimal/p-recommended drop the Platform-Adaptation pointer (gemini auto-loads
gemini-tools.md anyway; codex loses the codex-tools.md pointer — but that content is the audit
target). RECOMMENDATION: g-minimal (−58%) is the biggest win with zero observed cost across 5
model/harness combos × 2 triggers; p-recommended (−47%) equally clean; a-no-digraph (−24%) the
conservative floor. Jesse decides.

## Backlog / queued work
- **(Jesse, queued 2026-06-21 — do AFTER current eval work)** Author an additional set of evals
  for the *content of* `claude-code-tools.md` itself. Jesse is ~99% sure ≥50% of that file is
  redundant or wrong. Plan: enumerate each mapping/claim in the file, classify
  redundant-vs-load-bearing-vs-wrong (against actual current Claude Code tool behavior), and build
  evals that would FAIL if a wrong/needed line were removed (so we can safely delete the dead 50%).
  Tie-in: this directly informs how aggressively the platform/reference section can be compressed.
- New eval scenarios authored this session (in `superpowers/evals/scenarios/`):
  `global-tool-mapping-comprehension` (all harnesses) and `claude-tool-mapping-applied` (claude only).
  Both pass `quorum check`. Full gauntlet runs need an x-api-key; deterministic behavior validated
  headless via `harnesses/validate-toolmap-evals.py`.

## Run mapping
(variant hash → SKILL.md → pass-rates)
- baseline `918562bbba1c`; a-no-digraph `0d2d4a4b3732`; b-no-platform `c8d90f6a07c4`;
  c-no-redflags `e94d0125a585`; d-no-skill-types `d7e83f0e90ff`;
  e-no-instruction-priority `9409d0a49071`; f-lean `e434caa024a2`; g-minimal `49d15fecbd3e`.
