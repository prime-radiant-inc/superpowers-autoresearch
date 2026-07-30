# MINE: the 2026-07-29 fallback session tree (Amendment 3)

**Task:** reconcile the pre-registered claims in
`logs/2026-07-28-codex-efficiency.md`'s "EXTERNAL EVIDENCE: Jesse's audit
of the 07-29 fallback session" entry against the actual rollout tree,
using the trusted, unmodified `rollout_parser.py` / `score_e2.py` /
`score_e7.py` / `score_e8.py`.

**Headline result: the corpus is gone.** Root rollout
`019faf59-3a06-7f40-87e0-c8c84a5729ae` (per the plan's Amendment 3, also
cited in the pre-registration log entry — not audited-project content)
and every one of its 13 descendants are absent from this machine's Codex
storage as of the check below. Every pre-registered claim is therefore
**UNVERIFIABLE**, not confirmed or refuted. Nothing here contradicts
Jesse's manual audit; it's independent tooling simply arriving too late
to see the same files he saw.

Tooling: `campaigns/codex-efficiency/audit0729_adapter.py` (new, this
task — a thin discovery/census adapter over the unmodified parser and
scorers, same pattern as `drew_adapter.py`). Reads no committed output
of its own; this `.md` is the only durable artifact.

## 1. Discovery — methodology and evidence

Five independent, read-only legs, all exercised for real (not
theoretical) and all codified in `audit0729_adapter.py` — fix round 1
moved two legs that were originally only ad hoc shell commands (the
full-tree filename sweep and the `archived_sessions/` check) into the
reviewable script, alongside correcting the `archived_sessions/`
fact below (see §1's "Conclusion" and the fix-round note at the bottom
of this file):

1. **Filename match (narrow)**: `glob` for `*019faf59-3a06-7f40-87e0-c8c84a5729ae*.jsonl`
   under `~/.codex/sessions/2026/07/{28,29}` (07/30 doesn't exist yet).
2. **Content match (narrow)**: every rollout file under those same two
   date dirs read as raw bytes and searched for the root ID string (this
   would catch a *surviving child* rollout that still names the missing
   root as its `parent_thread_id`, even if the root's own file is gone).
   Reports file paths only — matched line content is never read or
   printed. Deliberately scoped to the narrow window, not the full
   ~8,000-rollout history, because byte-scanning at that scale isn't cheap.
3. **Filename match (full tree)**: `glob` for the same pattern across
   the ENTIRE `~/.codex/sessions/**/*.jsonl` tree (every date this
   machine has ever recorded) — filename-only, so cheap even unscoped.
4. **`archived_sessions/` match**: `~/.codex/archived_sessions/` is a
   separate, flat directory (no date subdirs) Codex moves some rollouts
   into; small enough (333 files) to both filename-glob and fully
   content-scan.
5. **DB match**: read-only query (`sqlite3` stdlib module,
   `file:~/.codex/state_5.sqlite?mode=ro`) against `thread_spawn_edges`
   for any row naming the root ID as `parent_thread_id` or
   `child_thread_id`.

Run (`python3 audit0729_adapter.py`), 2026-07-29 ~17:12 PDT (fix-round-1 rerun):

```
root_id searched: 019faf59-3a06-7f40-87e0-c8c84a5729ae
date dirs searched (legs 1-2, narrow window): ['.../2026/07/28', '.../2026/07/29']
leg 1 filename-match hits: 0 []
leg 2 content-match hits: 0 (scanned 36 rollout files) []
leg 3 full-tree filename-match hits: 0 []
leg 4 archived_sessions present: True (333 files); filename hits: 0 []; content hits: 0 []
leg 5 state_5.sqlite present: True (thread_spawn_edges total rows: 4724)
leg 5 thread_spawn_edges rows naming root_id: 0 []

RESULT: NOT_FOUND
```

`thread_spawn_edges` has 4,724 rows and is visibly live — the table
isn't empty or stale, it simply has no edge touching this root ID. 36
rollout files were opened and byte-scanned in the narrow window (12 from
07/28, 24 from 07/29) with zero content matches; the full-tree filename
sweep (leg 3, ~8k files) and the `archived_sessions/` filename+content
scan (leg 4, 333 files) both also came up empty.

**Corroborating detail — filename-timestamp timezone.** Rollout
filenames encode LOCAL time, not UTC (verified directly: rollout
`...T13-15-35-019faf84....jsonl`'s own first-line `session_meta.timestamp`
reads `2026-07-29T20:15:35Z` — exactly 7h later, i.e. PDT). So the
Amendment 3 claim "root started ~11:36" is 11:36 **local**, i.e.
`2026-07-29T18:36:xxZ`. A broad `threads` table query for anything
created between 17:00–21:00 UTC that day returns nothing earlier than
`019faf84` at 20:15:35 UTC (13:15:35 local) — consistent with (not an
artifact of) the discovery result above: nothing from the claimed
~11:36–13:15 local window exists in the DB either.

**What the 07/29 date dir does contain, for transparency (not the
target, not examined beyond structural `session_meta`):** 24 rollout
files belonging to two unrelated root sessions (different UUIDs,
unrelated working directories) with no bearing on Amendment 3's target
tree. Not the "plugin-agent-model-fallback" work Jesse described. Not
explored further — out of scope, and their own privacy applies too.

**Conclusion:** this is not a search-methodology gap. The target root's
rollout file, every one of its descendants' rollout files, and every DB
edge referencing it are gone from this machine. Plausible causes (not
established, no log evidence either way — `~/.codex/log/` is empty):
local Codex session storage being pruned/rotated on some schedule
shorter than a few hours, or the session having been manually
deleted/archived after Jesse's audit. `~/.codex/archived_sessions/` is
**not** empty — it holds 333 rollout files — but every one of them is
dated 2026-02-12 through 2026-06-24 (verified: filename-parsed date
range, zero files matching `2026-07`), so none could be July's target
session regardless; it neither confirms nor rules out "archived after
the audit" as the mechanism, it just isn't where a July rollout would
have landed if it were. `~/.codex/.Trash` equivalent has no match
either.

## 2. Per-claim reconciliation

Every claim below carries the identical evidence: §1's five-leg search
came up empty, so there is no rollout file to compute the claim's
left-hand side from. "Concrete rollout-line evidence" cannot be cited
(there is no line to cite); §1's discovery log — exact commands, paths,
and row counts — is the evidence in its place.

| # | Pre-registered claim | Status | Cause |
|---|---|---|---|
| 1 | 193 root `wait_agent` calls, mostly ~30s polls | UNVERIFIABLE | corpus absent (§1) |
| 2 | 24 `list_agents` calls | UNVERIFIABLE | corpus absent (§1) |
| 3 | 148 textual go-test invocations (per-agent split: root 15 / catalog 23 / model-selector 66 / direct 9 / durable 22 / final reviewer 13) | UNVERIFIABLE | corpus absent (§1). Also note: the per-agent split's bucket labels ("catalog", "model-selector", "direct", "durable") are audited-project task-name content, not generic role labels — even had the corpus been present, this report would only ever have reproduced the **total** (148) plus generic role/depth buckets, per the campaign's no-task-name-content rule. `audit0729_adapter.py`'s `census_node()` computes a total + a max-identical-repeat count per session for exactly this reason (never the per-task-name split). |
| 4 | 12x identical regression cluster (one command repeated 12 times within a session) | UNVERIFIABLE | corpus absent (§1) |
| 5 | Implementer-spawned reviewer at depth 2 (Task 1) + controller-dispatched duplicate review of the same task | UNVERIFIABLE | corpus absent (§1) |
| 6 | 9 reviewer agents vs 4 implementer agents | UNVERIFIABLE | corpus absent (§1) |
| 7 | Session count = 1 root + 13 descendants = 14 | UNVERIFIABLE | corpus absent (§1) |

(The audit's qualitative findings — plan/design contradiction, withdrawn
overly-broad finding, final-fix-wave boundary violation, waived-baseline
rerun — are narrative, not scorer-checkable counts; they were never in
scope for this MINE task's reconciliation table and remain exactly what
they were: Jesse's own manual read of the session, unconfirmed and
un-contradicted by tooling.)

## 3. Cross-corpus row

The wait-timeout-rate and depth-2-by-role columns this task was asked to
add cannot be populated — there is no session to compute `wait_outcomes()`
or a role-tagged depth-2 spawn census from. Row added as N/A, next to
the existing E7 (wait census) and E2 (subtree census) aggregates for
comparison of what a populated row looks like:

| Corpus / run | Sessions scored | wait_agent calls | Timeout rate (of paired) | max_depth | depth-2 spawns by role |
|---|---:|---:|---:|---:|---|
| E7 — audit corpus, high-wait Remux root | 1 | 1,058 | 74.5%* | n/a (E7 doesn't walk trees) | n/a |
| E7 — our battery, dev arm (6 reps) | 54 | 158 | 67.1% | n/a | n/a |
| E7 — our battery, spinout arm (8 reps) | 75 | 201 | 60.2% | n/a | n/a |
| E2 — cx-branch-review, dev arm (4 reps) | 2/rep | 2–3/rep | n/a (E2 doesn't compute timeout rate) | 1 (every rep) | 0/4 reps have any depth-2 spawn |
| E1-v611 — v6.1.1 battery (3 reps) | — | — | — | — | 1 depth-2 spawn / 22 total (model-omitted) |
| **07-29 fallback tree (this task's target)** | **0 (unresolvable)** | **N/A** | **N/A** | **N/A** | **N/A — corpus absent, see §1** |

\* rate/all_calls, matching `score_e7.py`'s own column (see `out/e7-report.md`).

## 4. Campaign-impact reassessment

Amendment 3's own "Campaign impact" paragraph (log, 2026-07-29 entry)
treats the pre-registered numbers as fresh-session confirmation for
three experiment upgrades (E3's duplicate-gate discrimination, E2/E6's
recursion signature, E5's rubric). That paragraph's basis is **still
only Jesse's original manual audit** — this MINE task could not add
independent tooling corroboration, because the corpus it was supposed to
corroborate against no longer exists. The experiment-upgrade decisions
in Amendment 3 stand on external evidence alone, same footing as before
this task ran; they are not now doubly-confirmed, and they are not
undermined either (nothing here contradicts them — the search simply
found no data, in either direction).

**Methodological note worth flagging for the campaign:** this is the
first MINE task in the campaign where the source corpus evaporated
between when it was described (same-day audit) and when it was mined
(hours later, same day). Every other MINE task in this campaign
(corpus validation, Drew cross-validation, E7/E8/E9) worked from a
corpus that was already durably captured (the audit's own
`session-manifest.json`/`metrics-all.jsonl` snapshot, or an externally
supplied, separately-preserved package). A live `~/.codex/sessions/`
directory is evidently not a stable audit source on this timescale —
future MINE tasks that plan to reconcile against a *live* local rollout
tree should copy/snapshot the relevant files immediately, not defer to
a later task.

## 5. Existing-tooling verification

No changes were made to `rollout_parser.py`, `score_e1.py`, `score_e2.py`,
`score_e7.py`, or `score_e8.py` — this task only added
`audit0729_adapter.py` (thin discovery/glue, same shape as
`drew_adapter.py`; no dedicated test file, matching that precedent).
**Fix round 1 correction:** an earlier draft of `census_node()`
reimplemented its own thinner wait/lifecycle census directly on
`rollout_parser.wait_outcomes()`/`lifecycle_calls()` instead of actually
calling `score_e7.py`/`score_e8.py` — meaning it would not have
reconciled the pre-registered wait-timeout-rate or closure/lifecycle
claims correctly on a future rerun, despite the module docstring listing
those scorers as reused. Fixed: `census_node()` now imports and calls
`score_e7.census_session()` and `score_e8.census_session()` directly
(unmodified) for those fields; only the go-test count and the
identical-repeat-cluster max remain this file's own counting/grouping
logic, built on `rollout_parser.exec_commands()`/`TEST_RE`. Verified by
rerunning `audit0729_adapter.py` after the fix (§1's Run block above) —
it still short-circuits to `NOT_FOUND` cleanly (exit 1, no traceback,
~0.6s) since the corpus is still absent; the census path itself
(`run_census()`/`census_node()`) remains untested against real data
because none exists here, but it now genuinely calls the scorers it
claims to, so a future rerun against a recovered corpus would exercise
real `score_e7`/`score_e8` logic rather than a silent reimplementation.
Existing suites re-run clean, unaffected by this fix (no scorer/parser
files touched): `test_rollout_parser.py` (15), `test_score_e1.py` (6),
`test_score_e2.py` (9), `test_score_e4.py` (19), `test_score_e9.py`
(7) — all OK.
