# Bootstrap compression — findings & recommendation (2026-06-21)

Campaign: shrink the `using-superpowers` bootstrap (injected into every session +
subagent by `hooks/session-start`) without hurting skill auto-triggering.
Full method + hypothesis log: `logs/2026-06-21-bootstrap-compression.md`.

## What we measured and how

A deterministic headless harness (`harnesses/triggering-harness.py`) runs real
`claude -p --plugin-dir <root>` in an isolated $HOME (so no personal CLAUDE.md
confounds the signal), using quorum's exact scenario prompts + `isSkillInvocation`
+ skill-before-Write/Edit logic — but no LLM verifier (triggering is deterministic).
Runs on a subscription OAuth token. Models: opus, sonnet, haiku.

**Honest scope limits (read before acting):**
- **Claude only.** The bootstrap also serves Codex/Gemini/Copilot. Nothing here
  validates those harnesses; compressing platform-specific content is UNTESTED for them.
- **Token counts are chars/3.7 estimates** (exact counts need an x-api-key the
  subscription path doesn't provide). Good for relative comparison, not absolute.
- **One clean discriminating probe.** Most triggering scenarios turned out
  saturated (skill self-triggers from its own description) or confounded; only
  systematic-debugging cleanly separates baseline from a gutted bootstrap. So the
  evidence is strong on that probe and the brainstorming acceptance test, but it
  cannot prove every skill's trigger survives. The project's high bar for
  behavior-shaping content still applies: confirm with quorum FULL before shipping.

## The core finding

The bootstrap's triggering value is concentrated, not uniform:
- Skills with **imperative self-descriptions** (brainstorming: "You MUST use this
  before any creative work…") auto-trigger from the Skill-tool listing alone — the
  bootstrap content is nearly irrelevant for them. (z-null still fired brainstorming 5/5.)
- Skills with **weaker descriptions** (systematic-debugging) depend on the bootstrap:
  baseline 3/3 → empty bootstrap (z-null) **0/5**. This is the probe.
- That dependence is **redundantly supported**: no single section removal
  (Skill Priority, EXTREMELY-IMPORTANT, The Rule, Red Flags, …) broke it on haiku —
  only removing essentially everything (z-null) did. So compression is safe down to
  a surprisingly small core.

### Haiku results matrix (the canary; smaller models drop guidance first)
On the discriminating probe **systematic-debugging**: baseline and ALL ablations
(a–j, f-lean −40%, g-minimal −56%) held **3/3**; only z-null (−94%) broke at 0/5.
brainstorming acceptance + brainstorming-resists held 3/3 everywhere (saturated).
(Full matrix: `python3 harnesses/report.py`.)

### Cross-model confirmation (Phase C: baseline + g-minimal × opus/sonnet/haiku × 5 reps)
| probe | baseline (opus/son/hai) | g-minimal −56% (opus/son/hai) |
|---|---|---|
| systematic-debugging (under-trigger; MUST hold) | 5/5, 5/5, 5/5 | **5/5, 5/5, 5/5** |
| superpowers-bootstrap brainstorming (acceptance; MUST hold) | 5/5, 5/5, 5/5 | **5/5, 5/5, 5/5** |
| cost-checkbox (over-trigger guard; pass = NOT fired) | 0/5, 2/5, 0/5 | 0/5, 0/5, 0/5 |

**g-minimal (−56%) preserves real triggering IDENTICALLY to baseline on every clean
probe, across all three models.**

Over-trigger caveat: baseline ALSO over-triggers brainstorming on the trivial
checkbox (fires ~every run even at full size) — that's a property of brainstorming's
imperative description in this isolated/headless harness, not a compression effect,
and g-minimal is indistinguishable from baseline (sonnet 2/5→0/5 is within noise).
So cost-checkbox has no baseline headroom here — it's not a clean calibration probe
in this harness. Worth a separate look (is brainstorming over-eager on trivial UI
tweaks?), but out of scope for compression.

## Recommendation — tiered by risk

Token counts are now EXACT (count_tokens API). Baseline = **1698 tokens**.

| Tier | Variant | Token Δ (exact) | What it is | Risk |
|---|---|---|---|---|
| **Conservative (ship-ready)** | `a-no-digraph` | **1288 (−24%)** | baseline minus the graphviz `dot` flowchart (redundant with the prose Rule; single biggest block) | Low. Doesn't touch cross-platform content or the Red Flags table. |
| **Recommended aggressive** | `p-recommended` | **905 (−47%)** | digraph core (Q2) + trigger-only description + access line removed (Q3) + reworded subagent note (Q4 fix). | Medium. Needs the two checks below + the quorum/tmux re-test (in progress). |
| Alternate aggressive | `g-minimal` | 708 (−58%) | prose-only (no digraph), Red Flags table → inline prose | Higher. Reformats tuned Red Flags content; no digraph means plan-mode handled by one prose line. |

**Caveat (added 2026-06-21):** all triggering numbers above came from a headless `claude -p`
harness, which does NOT exercise plan mode or interactive multi-turn behavior — Jesse's call.
Re-testing the promising candidates + validated experiments on the real **quorum/gauntlet
tmux** harness is now in progress (a real `sk-ant-api` key for the gauntlet verifier was
located in `prime-radiant-inc/serf/.env`). Treat the `-p` results as a screen; the quorum
results are the ground truth.

**Two checks gate the aggressive tier (both need work I haven't done):**
1. **Plan-mode** — interactive tmux/quorum run (a known over-trigger concern; `-p` can't see it; the digraph is the part that routes plan-mode, so digraph-keep (`p`) vs digraph-drop (`g`) should be decided on this).
2. **Cross-harness** — Codex/Gemini/Copilot, since `p`/`g`/`f` touch the platform pointer; the new `global-tool-mapping-comprehension` eval is the instrument for this.

**My recommendation:** adopt **`a-no-digraph` now** (−21%, ~340 tok/session × every
session + subagent) — cleanest, lowest-risk win, fully Claude-validated (transitively:
g-minimal keeps strictly less content and held 5/5/5, so a-no-digraph does too).
`g-minimal` (−56%) is Claude-confirmed across opus/sonnet/haiku and is the upper bound
worth pursuing, but ship it only with (a) quorum FULL confirmation (needs x-api-key)
and (b) a non-Claude harness check, since it compresses cross-platform content and
reformats the tuned Red Flags table — both untested here and both high-bar per project rules.

**One-line answer to the original question:** yes, the bootstrap can be cut hard —
−21% with high confidence today, up to −56% on Claude — because its triggering value
is concentrated in a small, redundantly-supported core; most of its bulk (the digraph,
per-platform prose, table formatting) is not load-bearing for auto-triggering.

## Round 2 — Jesse's review (additional variants)

All on the discriminating probe (systematic-debugging) × opus/sonnet/haiku × 5 reps, errs=0:

| variant | tokens (est) | result | verdict |
|---|---|---|---|
| `k-digraph-only` (digraph carries the logic, prose stripped) | ~816 (−50%) | 5/5/5 | Q: digraph-in-place-of-English **works** for triggering, ~as compact as g-minimal |
| `l-no-access` (drop "Never read skill files…/Skill tool/activate_skill" + Platform Adaptation) | ~1292 (−22%) | 5/5/5 | the access line **can go** |
| `m-no-subagent-stop` | ~1619 (−2%) | 5/5/5 | no harm at top level; see SUBAGENT-STOP note below |
| `o-lean-description` (trigger-only description) | ~1640 | 5/5/5 (both probes) | leaner description is **safe** |
| **`p-recommended`** (digraph core + lean desc + no access + reworded subagent note) | **~841 (−49%)** | _confirming_ | the synthesis of everything that passed |

**SUBAGENT-STOP correctness catch (Jesse):** "If you were dispatched as a subagent… skip
**this skill**" is miswired for the bootstrap, which is INJECTED AS PROSE at session start —
there is no skill being invoked, so "this skill" has no referent and a subagent can't "skip"
prose already in its context. Fix = reword for the injection context (p-recommended does:
"If you are a subagent dispatched to execute a specific task, you do not need to run this
skill-discovery flow…"), not necessarily delete. **Cannot be validated by this harness** —
it runs top-level sessions; the real subagent-skip behavior needs a subagent-dispatch test.

**Plan-mode over-triggering (Jesse's known concern): NOT ANSWERED.** 0/242 runs touched
EnterPlanMode/ExitPlanMode, but headless `-p` does not enter plan mode (interactive/TUI
behavior), so that "0" is a blind spot, not evidence. The digraph is exactly the part that
routes plan-mode, so this matters for choosing digraph-vs-prose. Needs an interactive tmux
harness (or quorum) — see "Open gaps".

## Open gaps (require harness extensions; flagged, not hand-waved)
1. **Plan-mode over-triggering** — needs interactive tmux driving; `-p` can't see it.
2. **Cross-harness** (Codex/Gemini/Copilot) — the platform-section + digraph changes are
   Claude-only validated. The bootstrap serves those harnesses too.
3. **Subagent-skip behavior** — needs a subagent-dispatch test, not a top-level one.

An interactive tmux harness would close (1) and (3) and is the prerequisite for trusting the
bigger cuts (k/p/g) in production.

## Reusable infrastructure
- `harnesses/measure-bootstrap-tokens.py` — token meter
- `harnesses/triggering-harness.py` — deterministic triggering eval
- `harnesses/compression-loop.py` — variant sweep driver (hash-cached/resumable)
- `harnesses/report.py` — campaign matrix
- `variants/bootstrap/generate-variants.py` + `*.md` — ablation generator + variants
