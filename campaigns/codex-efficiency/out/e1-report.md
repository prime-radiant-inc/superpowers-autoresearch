# E1 fork-hygiene verdict: baseline (dev), FULL battery

**Status: BLOCKED at the discrimination gate.** The treatment battery
(`codex-spinout-fixes` arm) was **not run**. This report scores the 4-rep
`dev`-arm baseline in full, evaluates it against the registered E1
prediction, and hands the mixed result back for adjudication per the
task brief's "the controller adjudicates" instruction.

## Scorer design (`score_e1.py`)

For each RUNDIR (a quorum run's coding-agent directory, one level below
`results/cx-eff-<scenario>-<arm>-repN/`):

1. Glob every `*.jsonl` under `home/.codex/sessions/**`, sorted by
   filename. Rollout filenames are `rollout-<ISO-timestamp>-<uuid>.jsonl`,
   so lexicographic filename order is chronological order; the first file
   is the root/controller rollout.
2. Call `extract_spawns()` on **every** rollout file in the run, not just
   the root — a spawned child can itself dispatch further children (a
   depth-2 fork), so limiting extraction to the root would silently drop
   those spawns.
3. For each spawn, resolve its child rollout: `child_links(parent_path)`
   maps `event_id` (== the spawn's `call_id`) to the child's
   `agent_thread_id`; the child rollout is whichever rollout filename in
   the run contains that UUID substring.
4. When a child rollout resolves, record its byte size and
   `parse_session()`'s `first_instruction_line`, `skill_reads_strict`,
   and `task_complete` (the last as the completion-parity signal for the
   spec's "no loss of task completion" success leg).
5. Emit a markdown table (raw tuples, per run + an aggregate across all
   RUNDIRs given in one invocation) to stdout, and a JSON blob of the
   same raw data to `out/e1-<label>.json` (label auto-derived from the
   `cx-eff-<scenario>-<arm>-repN` battery-dir naming convention).

No message/instruction text is ever extracted — `extract_spawns()`'s
`Spawn` dataclass has no such field, and nothing in `score_e1.py` reads
`payload["arguments"]["message"]`. `task_name` values are fixture-derived
(`task1_implementer`, `final_reviewer`, etc. — labels the SDD plan's own
task structure produces) and safe to commit verbatim, per the task
brief.

Verified against raw rollout JSON by hand (rep2's controller rollout,
`spawn_agent` function-call arguments minus the `message` key) — the
scorer's tuples match the raw data exactly; this is not a parsing
artifact of the extremely uniform result below.

## Baseline battery: run inventory (dev arm, `cx-sdd-small`, 4 reps)

| Rep | Run dir (leaf) | Gauntlet | Spawns | Coding cost | Gauntlet cost |
|---|---|---|---:|---:|---:|
| 1 | `cx-eff-cx-sdd-small-dev-rep1/cx-sdd-small-codex-codex_sub-linux-20260728T195835Z-c0bf` | pass | 7 | $4.14 | $0.32 |
| 2 | `cx-eff-cx-sdd-small-dev-rep2/cx-sdd-small-codex-codex_sub-linux-20260728T203056Z-de3b` | pass | 9 | $5.50 | $0.27 |
| 3 | `cx-eff-cx-sdd-small-dev-rep3/cx-sdd-small-codex-codex_sub-linux-20260728T205321Z-dad9` | pass | 9 | $5.25 | $0.25 |
| 4 | `cx-eff-cx-sdd-small-dev-rep4/cx-sdd-small-codex-codex_sub-linux-20260728T211212Z-fd5e` | pass | 9 | $4.54 | $0.33 |
| **Total** | | 4/4 pass | **34** | **$19.43** | **$1.16** |

Reps 2-4 spawned 9 (implementer+reviewer ×3 tasks, a final whole-branch
reviewer, and a fix+re-review round after the final reviewer caught a
bug); rep 1 spawned 7 (no fix round needed — the final reviewer found
nothing to fix). This is scenario-organic variance in *how much* SDD
work happened, not a scorer difference.

### rep1 / blinding-fix note

Rep1 (`19:58:35Z`) ran before commit `292b548` ("blind the Gauntlet
brief" — task-5-report.md, Fix round 1), which rewrote `story.md`'s
Gauntlet-facing persona to stop naming the scored axes. Reps 2-4
(`20:30`-`21:12Z`) ran against the blinded `story.md`.

Checked whether rep1 is an outlier on the metrics that matter to E1: **it
is not.** Rep1's 7/7 spawns are 100% `fork_turns:"none"`, 100%
model-omitted, 100% child-rollout-resolved, 100% child `task_complete` —
byte-for-byte the same hygiene pattern as every spawn in reps 2-4. The
only difference (7 vs 9 spawns) is the presence/absence of a fix round,
unrelated to blinding. Per the task instructions ("if clearly outlier,
run a replacement rep 5 and exclude rep1"): **not an outlier, rep1 kept,
no replacement rep run.**

## Full spawn-tuple table (all 34 baseline spawns)

`child_bytes` in bytes; `child_first_instruction_line` is `None` for
every row because child sessions receive their task via a
`sub_agent_activity` payload, not an `event_msg/user_message` record —
`parse_session()`'s `first_instruction_line` only fires on
`user_message`, so it's structurally `None` for every spawned child in
this harness (worth noting for E6, which also reads this field).

### rep1 (7 spawns)

| call_id | task_name | fork_turns | model | reasoning_effort | child_bytes | child_skill_reads_strict | child_task_complete |
|---|---|---|---|---|---:|---:|---:|
| call_8x3CT29ZJiZeNqm0WQ7kW2Jh | task1_implementer | none | (omitted) | (omitted) | 152069 | 1 | 1 |
| call_65rPEzIHVjbkwlnRezsdo5C7 | task1_reviewer | none | (omitted) | (omitted) | 77764 | 1 | 1 |
| call_TlUSM25CSlzBLsfLuWe4nQJ8 | task2_implementer | none | (omitted) | (omitted) | 181695 | 2 | 1 |
| call_jCgHJVulItUk1sijCazz1AZc | task2_reviewer | none | (omitted) | (omitted) | 92343 | 1 | 1 |
| call_eQU8hoyzV7cJ4WkrXNXdJPgy | task3_implementer | none | (omitted) | (omitted) | 151052 | 3 | 1 |
| call_9Q9WoPBlbXPMZ7KDslsZ7o9S | task3_reviewer | none | (omitted) | (omitted) | 75338 | 1 | 1 |
| call_FxvIHBTQXWEIJZMznmkfZV8i | final_reviewer | none | (omitted) | (omitted) | 94511 | 1 | 1 |

### rep2 (9 spawns)

| call_id | task_name | fork_turns | model | reasoning_effort | child_bytes | child_skill_reads_strict | child_task_complete |
|---|---|---|---|---|---:|---:|---:|
| call_WUQPVD1fPVPboSHo8rqMqv5D | task1_implementer | none | (omitted) | (omitted) | 152247 | 2 | 1 |
| call_m5ALoXKAIsXgyQtwGpebWHAF | task1_reviewer | none | (omitted) | (omitted) | 83177 | 1 | 1 |
| call_8E53ZWLcFo0tCEAP1Xfhbmhb | task2_implementer | none | (omitted) | (omitted) | 163750 | 2 | 1 |
| call_xops09CD6BXLcAxXGsdTkbqe | task2_reviewer | none | (omitted) | (omitted) | 91093 | 1 | 1 |
| call_BU4kYPSzCOByhf5BpkMdA7Wu | task3_implementer | none | (omitted) | (omitted) | 179283 | 3 | 1 |
| call_g2b1Ckl7MM4ObG3pLpKBVmBU | task3_reviewer | none | (omitted) | (omitted) | 89178 | 1 | 1 |
| call_Ck6d3NqnNRUbUCWinjAJX7Ey | final_reviewer | none | (omitted) | (omitted) | 109196 | 1 | 1 |
| call_CtiYRy4aK4uIdf4ZXRLv3xW9 | final_fixer | none | (omitted) | (omitted) | 145615 | 2 | 1 |
| call_8AL5mbu1swL7bixBEnFmuP4O | final_rereviewer | none | (omitted) | (omitted) | 89681 | 1 | 1 |

### rep3 (9 spawns)

| call_id | task_name | fork_turns | model | reasoning_effort | child_bytes | child_skill_reads_strict | child_task_complete |
|---|---|---|---|---|---:|---:|---:|
| call_kSBQHsxTfk0g5ZivjrHQhun0 | task1_implementer | none | (omitted) | (omitted) | 135914 | 2 | 1 |
| call_FdDW0qHnn0aADFthYHUN8Glz | task1_reviewer | none | (omitted) | (omitted) | 79151 | 1 | 1 |
| call_7zisjmoLsGI0Mor7e0KsrF5g | task2_implementer | none | (omitted) | (omitted) | 179954 | 2 | 1 |
| call_R6B3MVmUgbeC7lQ9nG2ddd6d | task2_reviewer | none | (omitted) | (omitted) | 83846 | 1 | 1 |
| call_BwTMep0mGYoS5kQDBxlTc0LC | task3_implementer | none | (omitted) | (omitted) | 127825 | 2 | 1 |
| call_8VFSyGp19dYXyAXMWblUUMlE | task3_reviewer | none | (omitted) | (omitted) | 76939 | 1 | 1 |
| call_NcxhMIaR39QvAVKm88WkEqJ6 | final_reviewer | none | (omitted) | (omitted) | 122846 | 1 | 1 |
| call_bEiWZSfwlBu29UD4oTSUoCPK | final_fix | none | (omitted) | (omitted) | 159696 | 2 | 1 |
| call_vFLo8ceSu02qfYt67ttzfNkK | final_fix_reviewer | none | (omitted) | (omitted) | 76548 | 1 | 1 |

### rep4 (9 spawns)

| call_id | task_name | fork_turns | model | reasoning_effort | child_bytes | child_skill_reads_strict | child_task_complete |
|---|---|---|---|---|---:|---:|---:|
| call_JkBrbwNj3XkuIbaaqQBtgH7s | task1_implementer | none | (omitted) | (omitted) | 157074 | 1 | 1 |
| call_fXgNkKDNzHfaYW7Pkb0Fk07T | task1_reviewer | none | (omitted) | (omitted) | 78953 | 1 | 1 |
| call_pjBCbggjHFKZX3LDTIpCOz1p | task2_implementer | none | (omitted) | (omitted) | 164357 | 2 | 1 |
| call_y1LxnfCBoRsHoYOM4tCmcTe2 | task2_reviewer | none | (omitted) | (omitted) | 84918 | 1 | 1 |
| call_nYq8AGzZDv2wQ04VGaSk8ej6 | task3_implementer | none | (omitted) | (omitted) | 145159 | 2 | 1 |
| call_17eXWMcv5uYFIozW9TmHEdhe | task3_reviewer | none | (omitted) | (omitted) | 80254 | 1 | 1 |
| call_GusxjXAwfvsdV7PDXqseROPS | final_reviewer | none | (omitted) | (omitted) | 102501 | 1 | 1 |
| call_alespbPXOFuxOK4Uz3V0cnhw | final_fix | none | (omitted) | (omitted) | 169274 | 2 | 1 |
| call_xrgH4bYezcZR4Y1TDtbkLwgu | final_fix_reviewer | none | (omitted) | (omitted) | 75860 | 1 | 1 |

Every one of the 34 spawns was manually inspected in the tables above
(none elided).

## Aggregate (34/34 spawns, all 4 reps)

| Metric | Count | % |
|---|---:|---:|
| `fork_turns == "none"` (isolated) | 34/34 | **100.0%** |
| `fork_turns == "all"` (full history) | 0/34 | 0.0% |
| `fork_turns == "all"` OR partial-numeric | 0/34 | 0.0% |
| Explicit `model` | 0/34 | 0.0% |
| `model` omitted | 34/34 | **100.0%** |
| Child rollout resolved | 34/34 | 100.0% |
| Child `task_complete` present (of resolved) | 34/34 | 100.0% |

Identical across all 4 reps individually — this is not an averaging
artifact; every single rep independently produced 100% isolated / 0%
full-or-partial / 100% model-omitted.

## Discrimination gate evaluation

**Registered prediction** (hypothesis log, `logs/2026-07-28-codex-efficiency.md`):
"≥40% of SDD spawns use `fork_turns:"all"`; ≥60% omit model" — phrased as
a single compound prediction ("the ≥40%/≥60% prediction holds"). The
task-6 controller message restated it as "≥40% of SDD spawns use
fork_turns 'all' OR partial numeric; ≥60% omit model" (the OR there is
*within* the fork_turns clause — "all" or partial-numeric both count as
non-isolated — not between the two clauses).

Both clauses of the compound prediction must hold for baseline to "land"
(exhibit the registered pathology):

| Clause | Threshold | Observed | Holds? |
|---|---|---:|:---:|
| fork_turns "all" or partial-numeric | ≥40% | 0.0% | **NO** |
| model omitted | ≥60% | 100.0% | YES |

**The compound prediction does not hold** — the fork-isolation clause
fails decisively (0% against a ≥40% bar, not a borderline miss), even
though the model-omission clause is satisfied more strongly than
predicted. Per the task brief: *"If the baseline does NOT exhibit the
pathology, do NOT run the treatment battery — return status BLOCKED with
the scored evidence; the controller adjudicates."*

This is a genuinely mixed result, not a clean pass or fail, so I did not
resolve the AND/OR ambiguity in the gate's phrasing unilaterally by
picking whichever reading justifies spending the ~$20 treatment battery.

### Why this is surprising given Finding 1's own narrative

The audit doc (`docs/superpowers/research/2026-07-28-codex-efficiency-audit.md`,
Finding 1) says: *"The small SDD control case shows the behavioral
consequence. Full-history 'implementers' saw the controller's SDD
instructions and recursively became SDD controllers..."* — i.e. the
audit's own corpus already contained a small-SDD example exhibiting the
fork-hygiene pathology this scenario was built to reproduce. Our
distilled `cx-sdd-small` scenario, run 4 times against current `dev`,
produced the opposite: 100% isolated forks, no recursive controllers,
every child terminated with `task_complete`. Sanity-checked directly
against raw rollout JSON (not just the scorer's output) — this is real
observed Codex behavior, not a parsing artifact.

Current `dev`'s `subagent-driven-development/SKILL.md` and
`using-superpowers/references/codex-tools.md` still don't mention
`fork_turns` at all (grepped both on the `/tmp/sp-arm-dev` worktree,
`bb2a34b` — zero matches), confirming Finding 1's diagnosis that the
Codex-specific routing tuple is genuinely undocumented on `dev`. Yet
Codex chose `fork_turns:"none"` unprompted for all 34 spawns here. The
model-omission pathology (Finding 1's other observation, "925 omitted
models") *did* reproduce at 100%, consistent with `SKILL.md`'s "always
specify the model explicitly" instruction (line 177) simply not being
followed for Codex dispatches.

Plausible explanations, none confirmed by this battery alone: (a) this
specific "3-task SDD plan via subagent-driven-development" shape isn't
the part of the corpus that produced Finding 1's full-history forking
— the corpus spans a much wider mix of skills/workflows than this one
distilled scenario; (b) Codex's own tool-level default for `spawn_agent`
may have shifted since the corpus window closed
(`2026-07-14T07:00:00Z`-`2026-07-28T16:50:29Z`) independent of any
Superpowers-side fix; (c) sampling variance that 4 reps aren't enough to
rule out, though 34/34 identical is a strong signal against pure chance.
Adjudication (re-plan vs. accept the model-omission-only finding vs.
widen the scenario) is for the controller/Jesse, not this scorer.

## Cost / budget

| | Coding | Gauntlet | Total |
|---|---:|---:|---:|
| Baseline battery (4 reps) | $19.43 | $1.16 | **$20.59** |

Subscription `used_percent` (`rate_limits.primary.used_percent`, last
`token_count` event of the controller rollout):

- First run of battery (rep1): **28.0%**
- Last run of battery (rep4): **31.0%**
- Delta: +3.0 points over the battery.

See `logs/2026-07-28-codex-efficiency.md` budget ledger for the
campaign-running total.

## Treatment battery: NOT RUN

Per the discrimination gate result above, the `codex-spinout-fixes`
(spinout) arm battery was not started. No `out/e1-cx-sdd-small-spinout.json`
exists. `run-quorum.sh spinout cx-sdd-small ...` is unchanged and ready
to run once the controller adjudicates whether/how to proceed (e.g.
re-scope the scenario to actually exercise full-history forking, accept
the model-omission-only finding as E1's baseline result, or treat E1 as
inconclusive-by-construction for this scenario shape).

## Success-criterion check (spec: 100% isolated + 100% explicit model + completion parity)

Not evaluated against treatment (none run). For reference, baseline
already meets the isolation leg (100% `fork_turns:"none"`) and the
completion-parity leg (100% child `task_complete`) trivially — it is
*only* the model-explicitness leg (0% explicit) where baseline fails the
spec's target, which is a different axis than the discrimination gate's
fork_turns clause.

## Deviations from the brief

1. **Treatment battery not run** — the discrimination gate's primary
   clause failed; running it anyway would have spent ~$20-25 and ~60-90
   min on a battery whose scientific value is unclear until the gate's
   AND/OR ambiguity and the Finding-1 tension above are resolved.
2. **rep1 kept, no replacement rep 5** — checked per the task
   instructions and found rep1 is not an outlier on any E1-relevant
   metric relative to reps 2-4 (see "rep1 / blinding-fix note" above).
3. **`run-quorum.sh` gained a `REP_START` 4th argument** (default 1) so
   baseline reps 2-4 could be appended without overwriting the existing
   rep1 smoke run — `bash run-quorum.sh dev cx-sdd-small 3 2` ran reps
   2, 3, 4. Documented in the script's header comment.
4. **`child_first_instruction_line` is `None` for all 34 spawns** — not
   a scorer bug; children receive their task via a `sub_agent_activity`
   payload rather than a `user_message` record, so
   `parse_session().first_instruction_line` structurally never fires for
   spawned children in this harness. Noted above and flagged for E6.
