# User-Preference-Overrides-Skill Evals — Design

Status: design approved (Jesse, 2026-06-23), executing iteratively.
Home of the scenarios: `superpowers/evals/scenarios/` (branch `bootstrap-compression-evals`).
Campaign log: `superpowers-autoresearch/logs/2026-06-21-bootstrap-compression.md`.

## Purpose

Test that an **ambient user preference** (a project-instructions file the harness honors)
correctly **overrides** a superpowers skill — the skill is suppressed, scoped, modified, or
augmented as the user asked. This is the test of the compressed `using-superpowers`
bootstrap's `## User Instructions` section: after cutting 42%, does the agent still honor
"user instructions take precedence over skills"? The override behaviors are grounded in real
user requests from the issue tracker (see Appendix), not invented.

## The core risk the design must avoid

A user-override eval has one dominant failure mode: a **false pass**. If the preference never
actually loads (wrong file for that harness) or the skill wouldn't have fired anyway, then
"skill correctly suppressed" is vacuous. Two principles defend against it:

1. **The agent→file map is established empirically, not assumed.** Each harness honors a
   different ambient file (Claude → `CLAUDE.md`, Gemini → `GEMINI.md`, Codex → `AGENTS.md`,
   others unknown). Guessing wrong = silent false-pass on that harness. Phase 0 pins the map
   with a canary probe.
2. **Every scoped/conditional override is a discrimination pair.** One cell where the
   condition holds (skill suppressed) AND one where it does not (skill still fires). A model
   that just never triggers anything fails the second cell. Full-suppression (A) gets its
   positive control for free from the existing triggering battery.

## Mechanism: the injection seam

`setup.sh` is currently agent-blind (`src/setup-step.ts` passes only `QUORUM_WORKDIR`,
`QUORUM_REPO_ROOT`, prelude). To inject "whichever file the harness honors":

- Runner threads `QUORUM_CODING_AGENT=<slug>` into setup's env (`envExtra` in the runner →
  `setup-step.ts`).
- New setup-helper `inject_user_preference "<text>"` reads the slug, looks up the
  **empirically-established** map (from Phase 0), and appends the preference to the right
  workdir file. Scenarios stay harness-agnostic — they just call
  `inject_user_preference "Don't use the brainstorming skill."`.
- Harnesses whose ambient file is unknown/unsupported are excluded until the probe confirms
  them.

## Phase 0 — canary probe (establishes the map + runnable-harness list)

A throwaway scenario whose setup writes, into **each candidate file**, a unique instruction:

> "If you are reading this file, your VERY FIRST action must be to create a file named
> `CANARY-<FILENAME>.txt` (e.g. `CANARY-CLAUDE.txt`). Do nothing else first."

Plus a trivial task prompt. Check: which `CANARY-*.txt` exists → that's the file the harness
honors. Deterministic (`file-exists`), reusable as a permanent guard that each harness still
respects its instruction file.

- Candidate files (superset; refine from the enumeration): `CLAUDE.md`, `AGENTS.md`,
  `GEMINI.md`, `.cursorrules`, plus any others the per-harness adapters reveal.
- Run per runnable harness. Output = the verified agent→file map + the confirmed set of
  harnesses the rig can actually run.
- **Runnable-harness list is itself a Phase-0 output** (from the static enumeration +
  whichever CLIs are installed in the Docker image). Target set per Jesse: claude(+sonnet/
  haiku), codex, gemini, kimi, pi, opencode, antigravity, cursor — include each that is
  wired and runnable.

### Phase 0 RESULT (2026-06-23)

Verified agent→ambient-file map (canary probe, `scenarios/probe-ambient-instruction-file`,
runner `harnesses/quorum-probe-ambient.sh`):

| Agent | Honored ambient file | Status |
|---|---|---|
| claude / claude-sonnet / claude-haiku | `CLAUDE.md` | verified ✓ |
| codex | `AGENTS.md` | verified ✓ |
| gemini | `GEMINI.md` | verified ✓ |
| **kimi** | **`AGENTS.md`** | verified ✓ — **NOT `CLAUDE.md`** (probed, not assumed) |
| pi | (TBD) | Launcher FIXED (`--no-context-files` removed → reads workdir context files), but won't run in our image: pi/pi-subagents package mismatch (image has `@mariozechner/pi-coding-agent`; pi-subagents needs renamed `@earendil-works/pi-coding-agent`). Needs a coherent image rebuild; then re-probe its ambient file. |
| antigravity | — | OUT for now: agy IS in the image (1.0.9). Perms bug — installer puts it under 700 `/root`; eval runs non-root → unreachable. Fix = `install -m0755 /root/.local/bin/agy /usr/local/bin/agy` (1 line). After that, blocked on Gemini Code-Assist OAuth ("Authentication required"). Needs creds, NOT a rebuild. |
| opencode | — | excluded: no provider key wired in `.env.container` |
| copilot / claude-windows | — | excluded: interactive GitHub auth / Windows-SSH |

Headline: **kimi honors `AGENTS.md`, not `CLAUDE.md`** — assuming the natural guess would have
silently false-passed every kimi override eval. v1 ambient channel is solid for **claude,
codex, gemini, kimi**. pi/antigravity are a coverage follow-up and are NOT rebuild-fixable
(pi = `--no-context-files` + bring-up; agy = a 1-line perms fix + valid Gemini Code-Assist
OAuth) — neither blocks the seam or the A/B/C battery.

## Scenario inventory

| Scenario | Preference injected | Check | Notes |
|---|---|---|---|
| **A1** brainstorm-disabled | "Don't use the brainstorming skill — just build what I ask." | `skill-not-called brainstorming` | control = existing `superpowers-bootstrap` |
| **A2** tdd-disabled | "Don't use TDD on this project." | `skill-not-called test-driven-development` | control = existing TDD trigger |
| **B-worktree** | "Don't use git worktrees here; work in the main checkout." | `skill-not-called using-git-worktrees` | #1 real cluster (#583/#721/#348) |
| **B-corp-MET** | "Never brainstorm for projects inside `corporate-work/`." + project IS in `corporate-work/` | `skill-not-called brainstorming` | conditional |
| **B-corp-UNMET** | *same preference* + project NOT in `corporate-work/` | `skill-called brainstorming` | discrimination control |
| **B-react-MET** | "Never do TDD on React projects." + React project | `skill-not-called test-driven-development` | conditional |
| **B-react-UNMET** | *same preference* + non-React project | `skill-called test-driven-development` | discrimination control |
| **C-visual** | "Never use the visual brainstorming companion." | `skill-called brainstorming` + companion never started | offer-detection soft — pin the concrete signal (the `--open` server-start command) |
| **OUT-path** | "Write design specs to `docs/specs/`, not `docs/superpowers/specs/`." | spec written to `docs/specs/` + not default | guards real bug #939; multi-turn (past approval gate) |
| **E-sdd** | "Always use subagent-driven dev; don't prompt me to pick a strategy." | `tool-called Agent` + `tool-not-called AskUserQuestion` | multi-turn |
| **E-skip-review** | "Skip the two-stage review on mechanical tasks." | no reviewer subagent dispatched | softest, multi-turn |

## Build order (iterative)

- **Phase 0** — canary probe → verified map + runnable-harness list.
- **Phase 1** — injection seam (`QUORUM_CODING_AGENT` + `inject_user_preference`).
- **Phase 2** — A/B/C suppression battery (8 scenarios incl. discrimination controls);
  validate in Docker across the runnable harnesses. This is what re-validates the compression.
- **Phase 3** — SPIKE `OUT-path` + `E-sdd` (one each) to find out whether the multi-turn
  gate is even reachable under the harness driver, BEFORE authoring the rest.
- **Phase 4** — remaining `OUT`/`E` scenarios, gated on what the spike learns.

## Phase 2 results (2026-06-23, n=1, cost-optimized: claude@haiku + codex + kimi; $4.87/12 cells)

Suppression battery + the B-react discrimination pair. **Override suppression is honored
broadly** — every "don't X" cell suppressed the skill (`skill-not-called`=true):

| Scenario | claude@haiku | codex | kimi |
|---|---|---|---|
| A1 user-pref-no-brainstorm (ran earlier, opus/4-agents) | pass | pass | pass (+gemini pass) |
| A2 user-pref-no-tdd | pass | pass | suppressed ✓ but gauntlet-fail* |
| B-worktree user-pref-no-worktree | pass | pass | pass |
| B-react-MET (React → suppress TDD) | pass | pass | pass |
| B-react-UNMET (non-React → TDD should FIRE) | TDD didn't fire† | **fired ✓** | indeterminate‡ |

\* kimi honored "no TDD" then **over-triggered brainstorming** on a one-function task, stuck in
the design gate 8+ turns, never implemented → gauntlet engagement-fail (calibration issue, NOT an
override failure).
† claude-haiku went straight to implementation without TDD; gauntlet found **no evidence it cited
the React preference** → TDD-trigger noise, not over-application.
‡ kimi's own reasoning said *"does not use React, so TDD could apply"* (condition read CORRECTLY)
but it wandered into 5+ clarifying questions and never reached the TDD decision.

**codex shows clean discrimination** (suppressed-when-React, fired-when-not). claude/kimi are
inconclusive — but from trigger noise + brainstorming-wander, not over-application.

### KEY LESSON: a discrimination control is only as reliable as the skill's trigger rate
The positive-control cell ("the skill STILL fires when the condition is absent") inherits the
skill's own self-trigger reliability. **TDD is a noisy trigger** (~90%, worse on haiku/small
tasks) and agents wander into brainstorming/clarification before the TDD decision, so the
TDD-based discrimination pair is weak at n=1. For a ROBUST conditional pair, use **brainstorming**
(the reliable trigger) with a path/condition — i.e. the deferred **B-corp** ("never brainstorm in
`corporate-work/`") pair is actually the *better* discrimination vehicle than B-react+TDD. Also:
run reps + a no-preference baseline to establish the skill's base trigger rate before reading the
control.

### B-corp pair (brainstorming, path-conditional) — CLEAN, validates the lesson (2026-06-23)

`user-pref-corp-no-brainstorm-{met,unmet}`: same preference ("no brainstorming under
`corporate-work/`"), same notifications-system task, ONLY the project's parent dir differs
(`corporate-work/acme-portal/` vs `side-projects/acme-portal/`). Result — **6/6 pass across
claude@haiku + codex + kimi**:

| Cell | claude | codex | kimi |
|---|---|---|---|
| MET (under corporate-work/ → suppress) | not-called ✓ | not-called ✓ | not-called ✓ |
| UNMET (outside → fire) | called ✓ | called ✓ | called ✓ |

Every agent suppressed brainstorming under `corporate-work/` AND fired it outside — reads the path
condition, applies the scoped override correctly, does NOT over-apply. Swapping the noisy TDD
trigger for reliable brainstorming turned the inconclusive B-react control into a clean result —
the lesson, confirmed. **B-corp is the canonical discrimination pair.** ($3.95/6 cells.)

Phase 2 spend total: ~$15.63 (A1 $6.81 opus/4-agents + battery $4.87 + B-corp $3.95).

## Open risks

- **Multi-turn reachability:** OUT and E scenarios need the agent to get past brainstorming's
  user-approval gate / reach plan execution. Under a one-shot driver these gates may never be
  reached → false "indeterminate". The Phase-3 spike de-risks this before we over-invest.
- **Visual-companion signal:** "companion not started" is a negative over a soft signal; need
  to pin the concrete command/tool the companion uses so the check is deterministic.
- **Per-harness ambient file unknown** for kimi/pi/opencode/antigravity/cursor until Phase 0.

## Appendix — real-issue grounding (issue miner, obra/superpowers)

- Worktrees = most-contested behavior: #583, #721, #348 (submodules), #839, #1108 — "stop
  inflicting this skill on my project."
- Output-location is a documented bug: **#939** ("the skill hardcodes the path… even when
  CLAUDE.md defines a different location, the skill's concrete path wins every time"); #807
  ("they commit working documents without asking"); #337/#975 (configurable dir).
- Off-switch / too-heavy: #938 (`/superpower off`), #645 (`SUPERPOWERS_MODE`), #1501
  (`/fast`), #1120 / #1286 (skip review on mechanical tasks).
- Visual-companion opt-out: #892 (open).
- Execution-mode / model-effort per subagent: #846 (default-implementation-strategy), #817 /
  #59 / #1747.
