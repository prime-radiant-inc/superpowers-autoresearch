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
storage as of the check below — and (fix round 2, §1b) absent from every
other Codex host reachable from here too. Every pre-registered claim is
therefore **UNVERIFIABLE**, not confirmed or refuted. Nothing here
contradicts Jesse's manual audit; it's independent tooling simply
arriving too late to see the same files he saw, wherever they were.

Tooling: `campaigns/codex-efficiency/audit0729_adapter.py` (new, this
task — a thin discovery/census adapter over the unmodified parser and
scorers, same pattern as `drew_adapter.py`; `AUDIT0729_SESSIONS_ROOT` env
override added fix round 2 so the same code can point at a corpus
rsynced elsewhere, not just live `~/.codex`). Reads no committed output
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

## 1b. Remote fetch attempt (fix round 2)

Coordinator/Jesse's lead: "the session likely lives on host
`remote-host-b`, reachable via ssh." SSH itself worked fine everywhere
it was tried (this is not an auth/route BLOCKED outcome for the two
hosts that actually run Codex) — the corpus still wasn't found. Read-only
throughout; nothing was modified on any remote host; nothing was fetched
because nothing matching was located to fetch.

**`remote-host-b`** (reachable, real activity: `goals`/`memories`/`logs`
sqlite files actively written today). `~/.codex/sessions/` tops out at
`2026/07/21` — no date dir for 07/22 through 07/29 exists at all, and a
read-only query against its own `state_5.sqlite` finds **no thread ever
created there after 2026-07-21 17:45:46 UTC** (`SELECT
MAX(datetime(created_at,'unixepoch'))`). Whatever this host is used for
today, it is not writing new Codex CLI/Desktop threads — the "likely
lives here" lead does not hold up.

**`remote-host-a`** — **Jesse subsequently confirmed this, not
`remote-host-b`, is the actual intended host** (found independently
first, before that correction arrived, via cross-referencing this
machine's own `~/.codex/.codex-global-state.json`, which names
`remote-host-a` under a `remote-ssh-codex-managed` key next to a
UUID — `019faf59-1735-...` — sharing our target's exact 8-hex-char
UUIDv7 time-prefix, i.e. created within about a minute of it). This host
is heavily active on 2026-07-29 (129 rollout files that day alone,
00:29–16:55 local). Given Jesse's confirmation, this host got the
deepest search of any: filename glob (narrow window, full tree, and
`archived_sessions/` — which doesn't exist on this host), content grep,
a `thread_spawn_edges` query (767 total rows, zero matching), AND
(second pass, post-correction) a content search of `logs_2.sqlite`
(a separate `logs` table, `thread_id`-indexed, holding this host's own
CLI/Desktop diagnostic log stream — not rollout/conversation data) across
its full 254,662-row history (`SELECT COUNT(*) FROM logs`) via both an
indexed `thread_id` lookup (0 rows) and an unindexed
`feedback_log_body LIKE '%...%'` scan (1 row —
see below) — plus confirming no second `~/.codex`, no `CODEX_HOME`
override, and no other user account on the host that could hold a
second, separate session store. **All of it still came up empty for the
root ID itself.** Decoding the target UUID's own embedded UUIDv7
timestamp (`019faf59-3a06...` → 2026-07-29 19:28:08 UTC / **12:28:08 PDT
local** — NOT the "~11:36" Amendment 3 estimated; that figure appears to
have been approximate) places it squarely inside this host's 12:19–12:35
burst of near-simultaneous session starts — strong circumstantial
support for "this is the right host," yet the file specifically isn't
there. Two independent, corroborating (not new) incidental hits: the
same single unrelated session on this host (different project, different
UUID, not examined beyond its structural `type` fields) contains the
literal string `019faf59-3a06-7f40-87e0-c8c84a5729ae` both in its
rollout file (an `agent_message`/chat `message`/`task_complete` record,
not a `session_meta`/`sub_agent_activity` structural link) and in
`logs_2.sqlite`'s corresponding `DEBUG codex_core::stream_events_utils`
log line (the app logging that same streamed content) — i.e., something
discussed or referenced that ID by name in an unrelated session on
2026-07-29, not a child rollout naming it as parent, and not a second
independent source (the log row is downstream of the same rollout
content, not new evidence). This does confirm the ID is real, typed by
a real person into a real session on the confirmed-correct host, not a
typo or fabrication — but it supplies no rollout to census.

**`remote-host-c`, `remote-host-d`** (reachable): neither has a
`~/.codex/sessions/2026/07/{28,29}` directory at all — `remote-host-d` has no
`~/.codex/sessions` path whatsoever. Not Codex hosts for this date
range; ruled out immediately, not searched further.

**`remote-host-e`** — unreachable: `Connection timed out during banner exchange`.
**`remote-host-f`** — unreachable: `ssh: connect to host
fe80::18bb:62c2:9121:4bdf port 22: No route to host` (link-local address;
reads as a local test VM that isn't currently up).

**`remote-host-g`** (a `jesse@` macOS device, found live via `tailscale status`,
not in `~/.ssh/config`) — **BLOCKED**: `Host key verification failed.`
Did not bypass `StrictHostKeyChecking` to force past this — that's a
real trust decision, not something to wave through unilaterally. This is
the one lead left genuinely open: if Jesse trusts this host's key (or
confirms it's expected/rotated), it's worth the same three-leg search
the other hosts got.

(For completeness: this machine's own `logs_2.sqlite`, 8.8GB, was also
checked the same way — 0 rows by `thread_id`, 0 rows by
`feedback_log_body` content match. Matches the local §1 result exactly.)

**Net result:** the corpus was not fetched — including from
`remote-host-a`, the host Jesse specifically confirmed. Every reachable
host that actually runs Codex for this date range (`remote-host-b`,
`remote-host-a`, `remote-host-c`, `remote-host-d`) was searched exhaustively —
`remote-host-a` most of all, with a second, deeper pass after Jesse's
correction — and came up empty, exactly as this machine did. `remote-host-g` is
BLOCKED on host key trust, pending Jesse. This is worth Jesse's
attention specifically because it's *not* the "wrong host" outcome the
correction anticipated: the confirmed-correct host's own timestamp
math lines up with a real gap in its session-start burst, yet the file
isn't there and no DB or log trace of it exists either — something
beyond simple host-misidentification is going on (aggressive
pruning/rotation even on the "real" host, a manual deletion, or a
storage location neither of us has considered yet). §2's reconciliation
table below is therefore still built on §1/§1b's absence-of-evidence,
not on fetched data — no verdict was upgraded from UNVERIFIABLE.

## 2. Per-claim reconciliation

Every claim below carries the identical evidence: §1's five-leg local
search AND §1b's remote search across four reachable Codex hosts came up
empty, so there is no rollout file to compute the claim's left-hand side
from. "Concrete rollout-line evidence" cannot be cited (there is no line
to cite); §1/§1b's discovery logs — exact commands, hosts, paths, and
row counts — are the evidence in their place.

| # | Pre-registered claim | Status | Cause |
|---|---|---|---|
| 1 | 193 root `wait_agent` calls, mostly ~30s polls | UNVERIFIABLE | corpus absent locally and on every reachable remote host (§1, §1b) |
| 2 | 24 `list_agents` calls | UNVERIFIABLE | corpus absent locally and on every reachable remote host (§1, §1b) |
| 3 | 148 textual go-test invocations (per-agent split: root 15 / catalog 23 / model-selector 66 / direct 9 / durable 22 / final reviewer 13) | UNVERIFIABLE | corpus absent locally and on every reachable remote host (§1, §1b). Also note: the per-agent split's bucket labels ("catalog", "model-selector", "direct", "durable") are audited-project task-name content, not generic role labels — even had the corpus been present, this report would only ever have reproduced the **total** (148) plus generic role/depth buckets, per the campaign's no-task-name-content rule. `audit0729_adapter.py`'s `census_node()` computes a total + a max-identical-repeat count per session for exactly this reason (never the per-task-name split). |
| 4 | 12x identical regression cluster (one command repeated 12 times within a session) | UNVERIFIABLE | corpus absent locally and on every reachable remote host (§1, §1b) |
| 5 | Implementer-spawned reviewer at depth 2 (Task 1) + controller-dispatched duplicate review of the same task | UNVERIFIABLE | corpus absent locally and on every reachable remote host (§1, §1b) |
| 6 | 9 reviewer agents vs 4 implementer agents | UNVERIFIABLE | corpus absent locally and on every reachable remote host (§1, §1b) |
| 7 | Session count = 1 root + 13 descendants = 14 | UNVERIFIABLE | corpus absent locally and on every reachable remote host (§1, §1b) |

(The audit's qualitative findings — plan/design contradiction, withdrawn
overly-broad finding, final-fix-wave boundary violation, waived-baseline
rerun — are narrative, not scorer-checkable counts; they were never in
scope for this MINE task's reconciliation table and remain exactly what
they were: Jesse's own manual read of the session, unconfirmed and
un-contradicted by tooling.)

## 3. Cross-corpus row

The wait-timeout-rate and depth-2-by-role columns this task was asked to
add cannot be populated — there is no session to compute `wait_outcomes()`
or a role-tagged depth-2 spawn census from, even after the fix-round-2
remote fetch attempt (§1b) — no corpus was located anywhere reachable.
Row added as N/A, next to the existing E7 (wait census) and E2 (subtree
census) aggregates for comparison of what a populated row looks like:

| Corpus / run | Sessions scored | wait_agent calls | Timeout rate (of paired) | max_depth | depth-2 spawns by role |
|---|---:|---:|---:|---:|---|
| E7 — audit corpus, high-wait Remux root | 1 | 1,058 | 74.5%* | n/a (E7 doesn't walk trees) | n/a |
| E7 — our battery, dev arm (6 reps) | 54 | 158 | 67.1% | n/a | n/a |
| E7 — our battery, spinout arm (8 reps) | 75 | 201 | 60.2% | n/a | n/a |
| E2 — cx-branch-review, dev arm (4 reps) | 2/rep | 2–3/rep | n/a (E2 doesn't compute timeout rate) | 1 (every rep) | 0/4 reps have any depth-2 spawn |
| E1-v611 — v6.1.1 battery (3 reps) | — | — | — | — | 1 depth-2 spawn / 22 total (model-omitted) |
| **07-29 fallback tree (this task's target)** | **0 (unresolvable)** | **N/A** | **N/A** | **N/A** | **N/A — corpus absent, see §1/§1b** |

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

**Fix round 2 correction (root_path IndexError):** re-review found that
`main()`'s inline root-path fallback chain (added in the original task)
only checked 3 of the 5 discovery legs
(`filename_hits`/`full_tree_filename_hits`/`content_hits`) — a rerun
that located the corpus solely via one of the fix-round-1
`archived_sessions` legs (`archived_filename_hits`/`archived_content_hits`)
would hit `disc["content_hits"][0]` on an empty list and raise
`IndexError` in the FOUND branch, despite `found()` correctly
considering all 5 legs. Fixed with a new `_pick_root(disc)` helper
covering every file-producing leg (all except `spawn_edge_rows`, a DB
row rather than a file path — `_pick_root` returns `None` for that
DB-only case and `main()` now reports it distinctly instead of
crashing). `test_audit0729_adapter.py` (new) covers every single-leg-hit
case, the priority order, the nothing-found case, and the DB-only-returns-
None case (9 unit tests), plus a full-pipeline subprocess test that
builds a synthetic 2-session root+child tree, runs the actual CLI
against it via the new `AUDIT0729_SESSIONS_ROOT` env override, and
asserts on real output (tree size, wait/list_agents/test-exec counts,
role distribution) — the first time this file's `run_census()`/
`census_node()` (and therefore its calls into `score_e7.census_session()`/
`score_e8.census_session()`) has actually executed, closing the "census
path untested" gap fix round 1 flagged (against synthetic data, not the
real corpus — none exists to test against). `AUDIT0729_SESSIONS_ROOT`
also lets this same code point at a corpus rsynced elsewhere (additive;
default unchanged) — exercised by the same subprocess test. Reran
`audit0729_adapter.py` against the real (still-absent) target after the
fix: unchanged `NOT_FOUND`. All 11 new tests pass; existing suites
(56 tests) still clean.
