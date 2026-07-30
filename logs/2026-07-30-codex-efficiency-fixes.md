# Codex efficiency fix cycle — hypothesis log

**Started:** 2026-07-30
**Spec:** `superpowers/docs/superpowers/specs/2026-07-30-codex-efficiency-fixes-design.md`
**Branch:** `codex-efficiency-fixes` (off `dev`)
**Arm:** `/tmp/sp-arm-fix` (detached worktree; refresh before any later
battery with `git -C /tmp/sp-arm-fix checkout --detach codex-efficiency-fixes`)

This is an append-only log, from its first entry onward. Predictions are
written before a battery runs and are never edited after the fact; verdicts
get appended under each entry as batteries complete.

Standing rules carried over from the campaign log
(`2026-07-28-codex-efficiency.md`):
- **Pre-registration before batteries** — every battery gets a hypothesis-log
  entry (prediction, scorer, criterion) written before it runs.
- **Manual match inspection** — scorer matches on fix-arm runs get manually
  inspected, not trusted blind (non-circular verification).
- **No raw rollouts committed.**
- **Discrimination rule** — inconclusive-by-zero is a stop, not a pass.

## Pre-registered criteria (from the approved spec)

### T1. SDD worker-review prohibition

**Criterion:** 0 worker-issued depth-2 spawns AND review coverage preserved
(every task still gets exactly one controller-dispatched task review).

### T2. Event-driven waiting

**Criterion:** timeout rate < 25% with no loss of task completion.

### T3. codex-tools.md corrections

**Graded by:** source citation (already verified); no scorer regressions on
the shared battery. `score_e8.py` is retained as a V1/V2 schema detector,
not a hygiene grader — no `close_agent` checklist ships.

### T4. Brainstorming three-path router (variant C: approval always)

**Graded by (three layers):**
1. **Micro** (`ceremony-path-micro.py`, adapted): variant C literal text,
   plus adversarially ambiguous briefs the campaign never tested (a task
   that pattern-matches bounded but hides a public interface change).
   Criteria: spike/bounded/arch differentiate (≥4/5 per cell); ambiguous
   briefs escalate to FULL (≥4/5); arch never downgrades (5/5).
2. **Codex ceremony battery:** `cx-ceremony-{spike,bounded,arch}` on the fix
   arm, 3 reps each, `score_e4.py` census. Criteria: bounded reps show an
   approval turn but zero committed spec files and zero writing-plans
   ritual; arch reps keep the full two-doc flow; spike reps stay minimal.
3. **Global regression battery:** the same three ceremony scenarios on
   Claude Code and Gemini (rig work: those scenarios are currently
   codex-gated), 3 reps each; plus the triggering acceptance check ("Let's
   make a react todo list" auto-triggers brainstorming into the
   full/architectural path) on all three harnesses.

### T5. Explicit model on child-issued spawns

**Criterion:** every spawn at every depth carries explicit model + effort.
Pre-registered caveat: if T1 eliminates depth-2 spawns entirely, T5 grades
as root-spawn regression (hold 100%) plus doc correctness and is recorded
inconclusive-by-zero at depth-2 — the config backstop is then the operative
mechanism.

### 2026-07-30 — T4 layer 1 MICRO PRE-REGISTRATION: C-approval + adversarial briefs (Task 7)

Extends the original E4 ceremony-path MICRO (`ceremony-path-micro.py`,
`logs/2026-07-28-codex-efficiency.md` Task 1 baseline / Task 11
pre-registration) for T4 layer 1 above. Two changes to the script, both
made this task (not yet committed — bundled with the results entry per
this task's two-stage commit convention: predictions locked in now via
this log entry's own commit, script + results land together in a second
commit once the sweep has actually run):

**Taxonomy change (within-run comparisons only):** the shared SYSTEM
answer definitions for SPIKE/BOUNDED/FULL are neutralized from
"approval-gate present/absent" to "artifact produced." The shipped
`## Three Paths` router text (C-approval, below) has EVERY path end in
human approval, so the original A/B micro's SPIKE/BOUNDED definitions
("no approval step before starting" / "no approval gate") would make
C-approval unscoreable by construction — a model correctly applying the
shipped text could never legitimately answer SPIKE or BOUNDED under
those old definitions, since every path in the real skill text requires
approval. New definitions:
- SPIKE means: dive straight into a minimal throwaway investigation —
  no design document.
- BOUNDED means: make the change after at most brief clarification and
  a short in-chat design — no design document, no implementation plan.
- FULL means: run the complete design process — written design document
  and implementation plan before touching code.

These results are therefore **not comparable cell-by-cell** to the
original campaign micro's A-current/B-three-path numbers (registered
2026-07-29, Task 11) — a different question is being asked of the model
now (artifact ceremony, not approval-gate presence). Any comparison
below is within THIS run only.

**Variant change:** B-three-path (a drafted router paragraph, never
shipped) is replaced by **C-approval**: the shipped
`skills/brainstorming/SKILL.md` `## Three Paths` section (Task 5's
commit `5ea8821`) — the lead-in sentence, the three bullets (Spike /
Bounded / Architectural), and the doubt/ratchet paragraph, verbatim (no
heading, no surrounding Anti-Pattern / Red-Flags sections). Verified by
script: the embedded C-approval body, whitespace-collapsed, is
character-identical to the whitespace-collapsed source block extracted
directly from `skills/brainstorming/SKILL.md` (i.e. only the source
markdown's line-wrap whitespace differs — no word added, dropped, or
changed). Z-null and A-current are unchanged from the original micro.

**New adversarial briefs (verbatim, per the task brief):**
- `ambig-interface`: "Add a --json flag to our export CLI command so
  output can be piped to jq. The current text output of export is
  parsed line-by-line by three downstream scripts in tools/ that other
  teams run in their pipelines."
- `ambig-crosscut`: "Fix the timezone bug in report_generator.py where
  daily rollups are off by one day for users west of UTC. Rollup
  boundaries are also computed independently in the billing exporter
  and the retention job, which must stay consistent with reports."

Both read as surface-bounded (a flag, a one-file bug fix) but hide a
public-interface or cross-cutting dependency that should ratchet
classification up to FULL under the shipped text's "when in doubt, take
the heavier one" rule.

**Matrix:** 3 variants (Z-null, A-current, C-approval) x 5 briefs
(spike, bounded, arch, ambig-interface, ambig-crosscut) x 5 reps = 75
Anthropic Messages API calls, MODEL `claude-opus-4-8`, one-word
SPIKE/BOUNDED/FULL regex scoring, answer files cached one-per-sample
under `campaigns/codex-efficiency/out/micro-c/` (git-ignored, not
committed).

**Predictions:**
- **C-approval** — spike -> SPIKE >= 4/5; bounded -> BOUNDED >= 4/5;
  arch -> FULL 5/5 (never downgrades — the one-way ratchet is the
  highest-stakes claim in the shipped text); ambig-interface -> FULL
  >= 4/5; ambig-crosscut -> FULL >= 4/5 (the router text's "when in
  doubt, take the heavier one" line correctly escalates both
  adversarial briefs).
- **A-current** — bounded -> FULL persists (the original pathology:
  the absolute HARD-GATE wording still produces FULL on a well-scoped
  bounded task under the new artifact-level taxonomy, same as it did
  under the old approval-gate taxonomy).
- **Z-null on the two ambiguous briefs** — recorded as an observation,
  not gated: does unguided model judgment escalate ambig-interface /
  ambig-crosscut to FULL on its own, with no router text present at
  all? No criterion either way; reported descriptively alongside the
  gated cells.

**Success criterion for T4 layer 1 (from the spec, reproduced in this
log's Pre-registered criteria section above):** "spike/bounded/arch
differentiate (>=4/5 per cell); ambiguous briefs escalate to FULL
(>=4/5); arch never downgrades (5/5)." Per this task's hard rule: if
C-approval fails ANY of these cells, the honest result is still recorded
in the verdict entry below and this work still gets committed — but the
controller is told to STOP spending on the layer-2/layer-3 T4 batteries
(Codex ceremony battery, global regression battery) until the router
text is revisited. A pass on every C-approval cell is required before
those heavier batteries spend any budget.

**No run yet — this is the pre-registration.** Results + verdict follow
in a separate log entry once the sweep has run and the answer files have
been independently verified (one word each, via a command outside the
scorer's own parser).

### 2026-07-30 — T4 layer 1 MICRO RESULT: C-approval passes every pre-registered cell; Z-null/C-approval ceiling-effect caveat (Task 7)

Ran the pre-registered sweep: 75 Anthropic Messages API calls, MODEL
`claude-opus-4-8`, REPS=5, `campaigns/codex-efficiency/
ceremony-path-micro.py`. Exit code 0, no rate-limit errors encountered,
zero unparseable answers (no `(?N)` markers in the script's own printed
table).

**Independent verification (non-circular — outside the scorer's own
regex, per this log's standing rule):**
- `awk 'NF!=1' out/micro-c/*.txt` (75 files) → no output — every record
  is exactly one field.
- `wc -w out/micro-c/*.txt` → every individual file reports word count
  1 (the only line not matching `1` is the `75 total` summary).
- `od -c` on a sample file confirms raw content is the bare word only
  (e.g. `FULL`), no trailing newline, no stray whitespace.
- File-derived tallies cross-checked against the script's own
  `out/micro-c/results.json` — identical. (`results.json` and the raw
  `*.txt` answer files live under the git-ignored `out/`; not
  committed, per this task's convention.)

**Results (SPIKE/BOUNDED/FULL counts out of 5 reps):**

```
variant                    spike           bounded              arch   ambig-interface    ambig-crosscut
--------------------------------------------------------------------------------------------------------
Z-null                     5/0/0             0/5/0             0/0/5             0/0/5             0/0/5
A-current                  5/0/0             0/2/3             0/0/5             0/0/5             0/0/5
C-approval                 5/0/0             0/5/0             0/0/5             0/0/5             0/0/5
```

**Criteria check (against the pre-registration above):**
- C-approval spike -> SPIKE >=4/5: **5/5 — PASS**
- C-approval bounded -> BOUNDED >=4/5: **5/5 — PASS**
- C-approval arch -> FULL 5/5: **5/5 — PASS**
- C-approval ambig-interface -> FULL >=4/5: **5/5 — PASS**
- C-approval ambig-crosscut -> FULL >=4/5: **5/5 — PASS**
- A-current bounded -> FULL persists (observation, not gated): BOUNDED
  2, FULL 3 — the pathology persists as a 3/5 plurality, weaker than a
  unanimous signature.
- Z-null on ambig-interface / ambig-crosscut (observation, not gated):
  both 5/5 FULL — unguided judgment escalates BOTH adversarial briefs
  to FULL unanimously, with zero extra guidance text present.

**Verdict: PASS. Every pre-registered C-approval cell meets its
criterion.** Per this task's hard rule, this is not a stop condition —
T4 layer 2 (Codex ceremony battery) and layer 3 (global regression
battery) are cleared to proceed on router-text grounds.

**Caveat that travels with this PASS, not buried under it:** Z-null and
C-approval produce **identical** tallies on every one of the 5 briefs
(5/0/0, 0/5/0, 0/0/5, 0/0/5, 0/0/5 — both variants, all five columns).
The router text made zero measurable difference versus no extra
guidance at all on this battery; both hit the target classification
100% of the time. This is not a new anomaly — it reproduces the
original E4 micro's own finding almost exactly (`logs/
2026-07-28-codex-efficiency.md`, "E4 RESULT" entry, Task 11: "Z-null and
the drafted B-three-path both differentiate path choice perfectly and
identically across all 3 task classes... A-current... is the only
variant that fails to differentiate"). The same shape holds again here
with the real shipped router text and two new adversarial briefs:
Z-null/C-approval both perfect, A-current the sole outlier — though
A-current's bounded-class drift is weaker this time (3/5 FULL here vs.
5/5 FULL in the original run; not a clean apples-to-apples comparison
per the taxonomy-change caveat registered above, since the SPIKE/
BOUNDED/FULL definitions themselves changed between runs). Two live,
non-exclusive explanations, neither resolved by this MICRO alone: (a)
the neutralized SYSTEM template's own baked-in one-line definitions
(present verbatim in every condition, Z-null included) are themselves
sufficient guidance for a model this capable on task briefs this clear,
so the router text's marginal contribution over "definitions alone" is
untested by this battery; or (b) these five briefs are not hard enough
to discriminate "no extra guidance" from "shipped router text," even
though they were hard enough to discriminate A-current from the
Z-null/C-approval ceiling on `bounded`. Per this log's standing
discrimination rule ("inconclusive-by-zero is a stop, not a pass"), the
zero gap between Z-null and C-approval specifically is flagged as
inconclusive-by-zero for the narrower claim "the router TEXT (as
opposed to the neutralized definitions alone) is what produces correct
classification" — that narrower claim is NOT established by this
battery. Nothing pre-registered required beating Z-null (only
A-current's `bounded -> FULL persists` was framed as a contrast, and it
DOES diverge from both Z-null and C-approval on `bounded` — the one
cell where the hard-gate's absolute wording still pulls weight the
router text and no-guidance condition don't), so the PASS verdict
stands exactly as registered. Recommendation for the layer 2/3
batteries: additionally track whether a bare/no-brainstorming-skill
Codex control already classifies comparably well, so the live battery
doesn't inherit this MICRO's blind spot unexamined.

**Cost:** not reported by the script — it records no token/cost totals
and none were read from the API response at run time, so no figure is
reconstructible after the fact. Same limitation noted for this same
script in the original campaign log's budget ledger (`logs/
2026-07-28-codex-efficiency.md` row: "E4 ceremony MICRO... unmeasured —
API cost not captured").

### 2026-07-30 — SHARED SDD BATTERY PRE-REGISTRATION: T1/T2/T5 on the fix arm (Task 8)

**Arm SHA (refreshed this task):** `git -C /tmp/sp-arm-fix checkout
--detach codex-efficiency-fixes` -> `5ea882124a6c50751fc53b3b2578b7f1c67abca4`
— matches the `codex-efficiency-fixes` branch tip in the working worktree
(`superpowers/.worktrees/codex-efficiency-fixes`), i.e. Task 7's
brainstorming-router commit is included. This is the same SHA already
recorded at the top of this log ("Arm: `/tmp/sp-arm-fix`").

**Runner change (committed with this entry):** `run-quorum.sh` only
wired `ARM: dev | spinout | v611`. Added a `fix -> /tmp/sp-arm-fix` case
(and updated the usage/comment text) — the arm directory already existed
at the correct SHA (confirmed above); only the script's ARM dispatch was
missing.

**Battery config:**
- Arm: `fix` (`/tmp/sp-arm-fix` @ `5ea8821`)
- Scenario: `cx-sdd-small`
- Reps: 8 total — 1-rep smoke test first (Step 2), then 7 more split
  across lanes: reps 2-4 on lane A (`EVALS_ROOT=superpowers/evals`),
  reps 5-8 on lane B (`EVALS_ROOT=evals-lane-b`), `JOBS=2` on the
  multi-rep lane B batch (lane A's batch is 3 reps, run either
  sequentially or JOBS=2 depending on what's cheapest to babysit — not
  gated either way, this doesn't change what gets measured).
- Scorers: `score_e6.py` (T1 — depth-2 spawns by spawner role,
  same-task duplicate-review families), `score_e7.py` (T2 — wait_agent
  timeout census; only corpus (c), our own battery runs, is new spend —
  corpora (a)/(b) are the existing external/audit corpora, not re-run),
  `score_e1.py` (T5 — per-spawn fork_turns/model/reasoning_effort
  tuples at every depth).
- Rep-range output filenames per each scorer's own convention (e.g.
  `e1-cx-sdd-small-fix-rep1-8`); `FORCE` is never set — a collision is
  treated as an anomaly, not worked around.

**Criteria (verbatim from this log's "Pre-registered criteria" section
above):**
- **T1:** 0 worker-issued depth-2 spawns AND review coverage preserved
  (every task still gets exactly one controller-dispatched task review).
- **T2:** timeout rate < 25% with no loss of task completion.
- **T5:** every spawn at every depth carries explicit model + effort.
  Caveat: if T1 eliminates depth-2 spawns entirely, T5 grades as
  root-spawn regression (hold 100%) plus doc correctness and is recorded
  inconclusive-by-zero at depth-2.

**Dev baselines (cited from `logs/2026-07-28-codex-efficiency.md`, NOT
re-run this task):**
- **T1 reference point:** the campaign's depth-2/worker-issued-review
  pathology is real and reproduced 9 times across 4 corpora (E6
  correction entry, 2026-07-30), but on `cx-sdd-small` specifically the
  `dev` arm shows **0/0 depth-2 spawns across 6 reps** (E6's free
  re-score table) and the CLI-0.146 re-test's 2-rep dev sample also
  shows zero depth-2 forking — the pathology on THIS scenario/arm
  combination is comparatively rare even unfixed, which is exactly why
  the pre-registered criterion is an absolute bar (0 depth-2 spawns AND
  review coverage preserved) rather than a relative dev-vs-fix
  comparison, and exactly why T1 landing at 0/0 here is a plausible
  outcome that doesn't by itself prove the fix (see the T5
  inconclusive-by-zero caveat, which exists for this reason).
- **T2 reference point:** dev arm `cx-eff-cx-sdd-small-dev-rep*` timeout
  rate 67.1%/69.3% (E7 RESULT entry, 2026-07-29) — well above the <25%
  bar, confirming the pathology is present pre-fix on this exact
  scenario/arm.
- **T5 reference point:** at CLI 0.146.0, dev root-controller spawns on
  `cx-sdd-small` are already 100% explicit-model (14/14, E1 RE-TEST
  entry) — the CLI unlock plus `dev`'s pre-existing generic
  "always specify the model" instruction already covers root spawns.
  The model-omission pathology T5's fix targets is specifically at
  depth-2 (worker-issued spawns), which is the same population T1 is
  trying to eliminate — hence the two treatments' criteria interact,
  and why a T1 win can leave T5 without anything to grade at depth-2.

**Budget estimate:** ~$40 for 8 reps of `cx-sdd-small` (dev's own
6-rep + 2-rep CLI-0.146 baseline batteries on this scenario cost
$20.59 + $7.27 = $27.86 for 8 reps combined in the old campaign: ~$3.5/
rep -> ~$28 for 8 reps at that rate; budgeting ~$40 for headroom given
the fix arm's changes may add turns, e.g. event-driven waiting changing
session shape).

**No run yet — this is the pre-registration.** Smoke test, full
battery, scoring, manual inspection, and verdicts follow in later log
entries.

### 2026-07-30 — SHARED SDD BATTERY: smoke test PASS; ANOMALY — Docker Desktop crash mid-battery costs 2 of 8 reps (Task 8)

**Smoke test (rep1, lane A): PASS.** Gauntlet verdict `status: pass`.
7 rollout files (1 root + 6 task implementer/reviewer pairs + 1
`final_reviewer`). Manual inspection of the raw root rollout JSONL
(not scorer output): all 7 `spawn_agent` calls issued by the ROOT
session only (`grep -c` of every non-root rollout file for
`spawn_agent` = 0) — zero worker-issued depth-2 spawns. Every one of
the 7 spawns carries explicit `model` + `reasoning_effort`
(`gpt-5.6-terra`/`medium` x6, `gpt-5.6-sol`/`high` for
`final_reviewer`), and `fork_turns:"none"` throughout. Task coverage:
`task{1,2,3}_{implementer,reviewer}` + `final_reviewer` — every task
gets exactly one reviewer. Root session's `wait_agent` calls (n=26,
manually parsed from the raw rollout, paired against
`function_call_output`): timeout_ms escalates 1000 -> 10000 -> 20000 ->
30000 (never reaching the fix's own recommended >=900000ms single long
wait), 18/25 paired calls (72.0%) still time out — **well above the
T2 <25% criterion on this single rep**, a first, honest signal that
the docs-only fix (`codex-tools.md` guidance to issue one long wait)
did not change this rep's actual polling behavior. Flagged here for
the full battery's verdict, not adjudicated on n=1.

No infra anomaly on the smoke rep. Proceeded to Step 3.

**Step 3 battery launch:** `EVALS_ROOT=<lane A> JOBS=2 bash
run-quorum.sh fix cx-sdd-small 3 2` (reps 2-4) and `EVALS_ROOT=<lane B>
JOBS=2 bash run-quorum.sh fix cx-sdd-small 4 5` (reps 5-8), launched
concurrently. Batch 1 of each lane (reps 2+3, reps 5+6) completed
cleanly — 5 more full passes, verdict.json + full rollout trees
present, matching the smoke rep's shape (spawns root-only, explicit
model+effort, `fork_turns:"none"`).

**ANOMALY — Docker Desktop crashed mid-battery, killing 2 in-flight
reps.** Batch 2 of each lane (rep4 alone on lane A; reps 7+8
concurrent on lane B) started around 18:49-18:50Z. Both lanes' logs
end with `run-quorum.sh: a parallel rep failed (JOBS=2)`; rep8 (lane
B) completed and printed a normal verdict, but **rep4 (lane A) and
rep7 (lane B) both stop mid-session with no verdict.json, no
`trajectory.json`, no `coding-agent-token-usage.json`** — only
`phase.json` (stuck at `"phase":"agent"`) and a `gauntlet-agent/`
directory whose `run.jsonl` cuts off mid-turn (~19:05:2xZ, no
`tool_result` for the last-issued `wake_on_idle_log`/`read_screen`
call) with no error message, in the middle of otherwise normal
gauntlet-agent activity (rep7's last visible line: "Final review found
a defect, now doing a fix wave. Continuing to monitor." — a routine
in-progress status, not a crash message).

**Root cause, confirmed:** `docker ps` immediately after (while
investigating) failed with `cannot connect to the Docker API... no
such file or directory` — the Docker Desktop daemon itself was down.
`docker ps -a` (once briefly reachable) showed both lane containers
`Exited (255)` at the same wall-clock moment despite running in two
independent Docker containers on two independent evals checkouts —
the simultaneity across independent containers rules out a
scenario/treatment-side cause and points at a host-level VM crash.
Restarted Docker Desktop (`open -a Docker`); it came up once
(`docker info` succeeded, ~10s), but **crashed again within seconds of
`scripts/evals-container up`** on the very next command (`docker ps`
immediately after: connection refused again). A second 2-minute poll
confirmed the daemon stayed down. **Likely contributing factor:** host
disk (`/System/Volumes/Data`) at **95% capacity, 103Gi free** of 1.8Ti
at the time of the crash — Docker Desktop's own VM disk image alone is
30G, and a nearly-full host disk is a known Docker Desktop VM
instability trigger. Not proven (no crash-report/panic log located via
`log show` — the unified log query for `com.docker.docker` returned no
usable output, and no explicit OOM/panic string appeared in a 1-hour
`log show` window), but consistent with the evidence and the only
concrete anomaly on the host at the time. Four concurrent `codex`
sessions were in flight system-wide at the crash moment (JOBS=2 x 2
lanes), which is also consistent with a resource-pressure trigger,
though this campaign has run JOBS=2 batteries before
(`2026-07-28-codex-efficiency.md`'s E1-v611 and E6 treatment rows)
without a recorded crash.

**Decision (per this log's standing rule and this task's operational
instructions — anomalies stop the battery, record honestly, report
BLOCKED rather than improvising around infrastructure problems):**
stopped attempting further Docker restarts after the second crash
recurred immediately. Did NOT re-launch reps 4/7 a third time, did NOT
substitute other reps, did NOT use `FORCE`. **6 of the pre-registered
8 reps are valid, complete, real runs** (rep1/2/3 lane A, rep5/6/8
lane B) with full verdict.json + rollout trees, unaffected by the
later crash (they finished and were written to disk before the
daemon died). Proceeding to score and manually inspect those 6 valid
reps against the pre-registered T1/T2/T5 criteria, honestly reporting
n=6 rather than the pre-registered n=8, and flagging this task
**BLOCKED** on Docker Desktop infrastructure for completing the full
battery (reps 4 and 7 need a re-run once the host's Docker/disk
situation is confirmed stable — not attempted further by this task).

**Cost so far (6 completed reps, from each rep's own printed Economics
block):** rep1 $3.69 ($3.36 coding + $0.33 gauntlet), rep2 $4.40
($3.98 + $0.42), rep3 $4.77 ($4.42 + $0.35), rep5 $4.62 ($4.28 +
$0.34), rep6 $6.32 ($5.94 + $0.38), rep8 $3.02 ($2.74 + $0.27) —
**$26.82 total, all 6 measured directly from each verdict's own
Economics table.** Rep4/rep7's partial spend before the crash is
**unmeasured** — no `coding-agent-token-usage.json` was ever written
for either (the crash pre-empted it), so no dollar figure is
reconstructible, consistent with this log's "no figure exists" rule
rather than an estimate.

### 2026-07-30 — SHARED SDD BATTERY: T1/T2/T5 verdicts on n=6 (Task 8)

Scored the 6 valid reps (1/2/3/5/6/8; 4/7 lost to the Docker crash
above) with `score_e6.py` (T1), a small one-off script reusing
`score_e7.py`'s own tested `census_session()`/`aggregate()` functions
against the fix-arm RUNDIRs across both lanes (T2 — `score_e7.py`
itself hardcodes `arms=("dev","spinout")` and a single results dir,
neither of which fits `fix` split across two lane checkouts; rather
than modify score_e7.py's tested discovery logic or risk colliding
with its four frozen census blobs, the one-off script
(`/private/tmp/.../scratchpad/score_e7_fix_battery.py`, not committed —
scratch, not a campaign artifact) writes only a new
`out/e7-battery-fix.json`, untouched otherwise), and `score_e1.py`
(T5). Outputs: `out/e6-cx-sdd-small-fix-rep1-8.json`,
`out/e7-battery-fix.json`, `out/e1-cx-sdd-small-fix-rep1-8.json` (the
"rep1-8" filename suffix is `score_e1`/`score_e6`'s own
min-rep-to-max-rep naming convention — it does NOT mean reps 4/7 are
included; every one of the three JSON blobs lists exactly 6 runs with
explicit `rep` fields 1,2,3,5,6,8).

**Manual inspection (non-circular — raw rollout JSONL, not scorer
helpers), beyond the brief's 2-run minimum:**
- **Depth-2 spawn census (T1):** `grep -c '"name":"spawn_agent"'`
  against every rollout file in all 6 reps' session trees (not a
  sample — the full corpus, cheap enough to do exhaustively). Confirms
  score_e6's finding exactly: rep1/2/3/5/8 have `spawn_agent` calls
  ONLY in their root rollout file (0 elsewhere); rep6 has 2 additional
  `spawn_agent` calls in a NON-root file
  (`rollout-...18-39-46...jsonl`). Traced that file's identity via
  `score_e1`'s own `parent_rollout`/`child_rollout` linkage (data, not
  trusted classification) and independently confirmed by re-reading
  the raw JSONL: root spawned it as `final_reviewer`
  (`model=gpt-5.6-sol`, `reasoning_effort=xhigh`), and that
  `final_reviewer` session ITSELF issued 2 more `spawn_agent` calls —
  `behavior_tests_review` and `packaging_docs_review` — confirmed via
  direct `json.loads` of the raw `arguments` string: both call sites'
  argument dict has keys `['fork_turns','message','task_name']` only —
  no `model` or `reasoning_effort` key present at all (not
  present-but-null; genuinely absent from the tool call). **A real
  worker-issued depth-2 spawn, from a reviewer role.**
- **Root cause, confirmed from source:** commit `62c0180`'s
  "no-subagents" contract (`## You Do Not Dispatch Subagents`) was
  added ONLY to `skills/subagent-driven-development/
  implementer-prompt.md`. `task-reviewer-prompt.md` and
  `re-review-prompt.md` (`grep -n
  'dispatch\|subagent\|spawn'` on both) contain **zero** matching
  contract language — reviewers were never told not to dispatch. This
  directly explains rep6: the controller-dispatched `final_reviewer`
  found a defect area needing deeper investigation and, with no rule
  against it, spawned two specialized sub-reviewers itself instead of
  reporting back to the controller.
- **Wait-timeout classification (T2):** independently re-parsed two
  full sessions' raw `wait_agent`/`function_call_output` pairs with a
  fresh from-scratch script (own `json.loads` + call_id pairing, not
  `rollout_parser.wait_outcomes()`): rep1's root session (26 calls) —
  MANUAL: 25 paired, 18 timed out (72.0%); rep2's root session (9
  calls) — MANUAL: 9 paired, 0 timed out (0.0%). Both **exactly** match
  `out/e7-battery-fix.json`'s per-session numbers for the same two
  rollout files. High per-rep variance (72% vs 0%) is itself notable —
  not every rep polls the same way — but the 6-rep aggregate (below)
  is what the pre-registered criterion grades.
- **Explicit-model claims (T5):** independently re-parsed rep3's root
  session's 9 raw `spawn_agent` argument blobs — all 9 carry explicit
  `model`+`reasoning_effort`, matching `score_e1`'s table exactly.
  Cross-checked against rep6's 2 depth-2 spawns above (already
  manually confirmed model-omitted from the raw argument keys, not
  scorer inference).
- **Review coverage:** every one of the 6 reps' root sessions spawns
  exactly one `task{1,2,3}_reviewer` per task (verified in the same
  raw `spawn_agent` argument dumps used for the T5 check above) plus
  one whole-branch `final_reviewer`; `score_e6`'s aggregate confirms
  `reps with >=1 same-task duplicate review=0/6` — the rep6 depth-2
  spawns cover NEW areas (behavior tests, packaging docs) that no
  depth-1 reviewer already covered, not a duplicate of an
  already-reviewed task.

**Aggregate numbers (6 reps, from the three JSON blobs):**
- T1: **2 worker-issued depth-2 spawns** across 6 reps (1/6 reps
  affected), both `reviewer`-role-spawned, 0 same-task duplicate-review
  families.
- T2: **150 wait_agent calls, 146 paired, 95 timed out — 65.1%
  timeout rate (paired), 63.3% (of all calls).** All 6 reps' gauntlet
  verdict = `pass`; `score_e1`'s aggregate shows 50/50 (100%) resolved
  child rollouts with `task_complete` present — no loss of task
  completion.
- T5: **48/50 spawns (96.0%) carry explicit model; 2/50 (4.0%)
  omitted — both the T1 depth-2 pair.** 48/48 root-issued (depth-1)
  spawns are explicit (100% — the pre-existing root-controller
  guarantee holds). `fork_turns:"none"` on all 50/50 spawns (isolation
  unaffected).

**T5's pre-registered zero-depth-2 caveat does NOT apply.** The
caveat was: "if T1 eliminates depth-2 spawns entirely, T5... is
recorded inconclusive-by-zero at depth-2." T1 did NOT eliminate
depth-2 spawns — 2 real ones exist, in 1/6 reps — so T5 is directly
gradable at depth-2, and both real depth-2 spawns fail its criterion.
**Additional context, not part of the pre-registered criterion but
relevant to interpreting the miss:** T5's fix (`2a4c11b`) also
documents an advisory config-level backstop
(`~/.codex/config.toml`'s `[agents] default_subagent_model` /
`default_subagent_reasoning_effort`) as the safety net for exactly
this kind of slip — checked rep6's actual container
`home/.codex/config.toml`: no `[agents]`/`default_subagent_*` keys
present. **The backstop was never provisioned in this eval
environment**, so this battery cannot speak to whether it would have
caught rep6's omission; only the docs-only guidance was live, and it
did not prevent the miss.

**Verdicts against the pre-registered criteria:**

- **T1 (0 worker-issued depth-2 spawns AND review coverage
  preserved): FAIL.** The "review coverage preserved" clause passes
  cleanly (6/6 reps, every task gets exactly one controller-dispatched
  reviewer, 0/6 same-task duplicates). The "0 worker-issued depth-2
  spawns" clause fails: 2 found, in 1/6 reps (16.7%), both from a
  reviewer role. Root cause is a real, fixable gap, not noise: the
  fix's own no-subagents contract was scoped to
  `implementer-prompt.md` only and never reached
  `task-reviewer-prompt.md`/`re-review-prompt.md`. The pathology this
  fix targeted (9/9 same-task duplicate reviews across 4 corpora, per
  commit `62c0180`'s own message) is gone in this battery — 0/6
  same-task duplicates — but a related, previously-undocumented
  pathology (reviewer-initiated depth-2 fan-out, not
  same-task-duplicate in shape) surfaced in its place.
- **T2 (timeout rate < 25% with no loss of task completion): FAIL.**
  65.1%/63.3% vs the <25% bar — not close, and barely distinguishable
  from the dev baseline this exact scenario measured in the prior
  campaign (67.1%/69.3%, `logs/2026-07-28-codex-efficiency.md` E7
  RESULT entry): a 2-6 point shift, not the order-of-magnitude
  reduction the fix aimed for. "No loss of task completion" clause
  passes (6/6 gauntlet pass, 100% child task_complete) but the overall
  conjunction fails on the timeout-rate clause. The fix is docs-only
  (`codex-tools.md` guidance to issue one long `timeout_ms>=900000`
  wait instead of short polls); the smoke rep's own root session shows
  the model still escalating short timeouts (1000/10000/20000/30000ms)
  rather than adopting the recommended single long wait — the
  documentation did not change the behavior it targeted.
- **T5 (every spawn at every depth carries explicit model + effort):
  FAIL, not inconclusive-by-zero** (caveat doesn't apply — see above).
  48/50 (96.0%) explicit; the 2 misses are exactly the T1 depth-2
  pair, i.e. the same fix-coverage gap (reviewer role never told to
  set model/effort on its own spawns, mirroring never being told not
  to spawn at all) produces both the T1 and T5 misses from the same 2
  events. Root-controller (depth-1) spawns hold 100% (48/48), matching
  the "root-spawn regression" backstop framing from the caveat even
  though the caveat's trigger condition didn't fire. The advisory
  config backstop that's supposed to catch exactly this slip was not
  provisioned in this eval environment (see above) — untested here.

**Ledger row:** 2026-07-30 | Shared SDD battery T1/T2/T5 (fix arm,
cx-sdd-small, n=6 of pre-registered 8 — Docker crash cost reps 4/7) |
$26.82 (6 measured reps; rep4/rep7 partial spend unmeasured, no
token-usage file written before the crash) | sub used_percent not
read this task.

**Status: T1/T2/T5 verdicts delivered on n=6. Task remains BLOCKED on
Docker Desktop infrastructure for the 2 missing reps (4 and 7) — not
re-attempted after the second immediate crash (see the anomaly entry
above). All three verdicts are FAILs against their absolute
pre-registered criteria; none of the three would plausibly flip to
PASS with 2 more reps given how large each miss is (a 2-6x gap for T2,
a real and root-caused-not-noise miss for T1/T5) — but the
pre-registered n=8 was not reached and that shortfall is reported
honestly rather than silently backfilled.**

### 2026-07-30 — SHARED SDD BATTERY ROUND 2 PRE-REGISTRATION: T1/T2/T5 on the fix arm post-fix-commits (Task 8b)

This is round 2 of the shared SDD battery. Round 1 (the three entries
directly above — "SHARED SDD BATTERY PRE-REGISTRATION," the smoke-test/
Docker-crash anomaly entry, and "T1/T2/T5 verdicts on n=6") ran the
five original treatments' arm and FAILed all three gated criteria: T1
(2/6 reps had a worker-issued depth-2 spawn from a controller-dispatched
`final_reviewer` role, because commit `62c0180`'s no-subagents contract
was scoped only to `implementer-prompt.md`), T2 (65.1% wait-timeout
rate vs the <25% bar — the docs-only `codex-tools.md` polling guidance
changed nothing measurable), and T5 (2/50 spawns, exactly the T1
depth-2 pair, omitted explicit model/effort — the reviewer role was
never told to set them any more than it was told not to spawn).

**Two fix commits landed on top of the arm since round 1, both on
`codex-efficiency-fixes`:**
- `c07cf7e` — "reviewers never dispatch subagents either": extends the
  "You Do Not Dispatch Subagents" contract (previously
  implementer-prompt.md only) verbatim into
  `skills/requesting-code-review/code-reviewer.md`,
  `skills/subagent-driven-development/re-review-prompt.md`, and
  `skills/subagent-driven-development/task-reviewer-prompt.md` — every
  dispatched review role now carries the same "never spawn a subagent
  to review part of the diff, and never spawn another reviewer" text
  that `implementer-prompt.md` already had. Directly targets round 1's
  T1/T5 root cause (the reviewer-role gap).
- `3da65fb` — "controllers wait long or not at all": adds an eight-line
  "Waiting on dispatched subagents" paragraph to
  `skills/subagent-driven-development/SKILL.md` §1 (the controller loop
  the session actually re-reads on every turn) instructing "never poll
  a wait interface with short timeouts... wait only when you are
  genuinely idle, and then issue one long wait (fifteen minutes or
  more...) instead of many short ones." Directly targets round 1's T2
  finding that the platform-reference-only guidance (`codex-tools.md`)
  never got re-read mid-session and changed nothing.

**Arm SHA (verified this task):** `git -C /tmp/sp-arm-fix log --oneline
-1` → `3da65fb` — matches the `codex-efficiency-fixes` branch tip in
the working worktree. The arm worktree was already refreshed to this
SHA before this task started (no `checkout --detach` needed this time).
Both fix commits are present on top of the original five treatments
(confirmed via `git -C /tmp/sp-arm-fix log --oneline -5`: `3da65fb` →
`c07cf7e` → `3ef84f0` (Amendment 1 plan doc) → `5ea8821` (T4 router) →
`2a4c11b` (T5 original fix) — i.e. this arm is the round-1 arm plus
exactly these two commits, nothing else changed underneath it).

**Battery config (unchanged from round 1 except rep numbering — see
below):**
- Arm: `fix` (`/tmp/sp-arm-fix` @ `3da65fb`)
- Scenario: `cx-sdd-small`
- Reps: 8 total, same lane split as round 1 (4 reps/lane) — **but
  renumbered reps 9-16, not 1-8**, specifically so this round's
  `--out-root` RUNDIRs (`results/cx-eff-cx-sdd-small-fix-rep{9..16}`)
  and this round's scorer output files (`out/e1-cx-sdd-small-fix-
  rep9-16.json` etc., derived automatically by `score_e1.py`/
  `score_e6.py`'s own `_rep_range_suffix()` from the rep number embedded
  in the RUNDIR name) cannot collide with round 1's already-committed
  `rep1-8`-suffixed aggregates or round 1's still-present on-disk
  `rep1`..`rep8` run directories (round 1's raw rundirs, including the
  crash-orphaned rep4/rep7, were left in place — not deleted, not
  reused). `FORCE` is never set on any scorer invocation this round
  either; a collision is an anomaly to report, not a flag to
  suppress. Rep9 = smoke (lane A), reps 10-12 = lane A batch (JOBS
  TBD by what's cheapest to babysit, not gated), reps 13-16 = lane B
  batch (`JOBS=2`), mirroring round 1's 1+3 / 4 split exactly.
- Scorers: `score_e6.py` (T1), `score_e7.py`'s tested
  `census_session()`/`aggregate()` functions via a fresh one-off script
  (round 1's `score_e7.py` still hardcodes `arms=("dev","spinout")` and
  a single results dir — confirmed unchanged this task — so the fix arm
  split across two lane checkouts still doesn't fit its CLI; the
  one-off script again writes only a new, non-colliding
  `out/e7-battery-fix-round2.json`, never touching `e7-battery-fix.json`
  (round 1) or any of the four frozen corpus (a)/(b) blobs) (T2),
  `score_e1.py` (T5).

**Criteria (verbatim from this log's "Pre-registered criteria" section
above — unchanged from round 1):**
- **T1:** 0 worker-issued depth-2 spawns AND review coverage preserved
  (every task still gets exactly one controller-dispatched task review).
- **T2:** timeout rate < 25% with no loss of task completion.
- **T5:** every spawn at every depth carries explicit model + effort.
  Caveat: if T1 eliminates depth-2 spawns entirely, T5 grades as
  root-spawn regression (hold 100%) plus doc correctness and is recorded
  inconclusive-by-zero at depth-2.

**Round-1 result, cited as the comparison baseline this round's verdicts
are measured against (not re-run):** T1 FAIL (2/6 reps, both
reviewer-role depth-2 spawns, 0 same-task duplicates); T2 FAIL (65.1%
paired-timeout rate, 63.3% of all calls, vs dev baseline 67.1%/69.3% —
a 2-6 point shift only); T5 FAIL (48/50 explicit, 96.0%, the 2 misses
identical to the T1 pair) — all three from
`logs/2026-07-30-codex-efficiency-fixes.md`'s "SHARED SDD BATTERY:
T1/T2/T5 verdicts on n=6" entry above, n=6 of the pre-registered 8 (reps
4/7 lost to the Docker crash, not backfilled).

**Docker status (verified this task, before any spend):** the daemon
had been in a crash loop and was just restored; `docker ps -a`
immediately before this entry showed both lane containers
`Exited (255)`. Cycled per `scripts/evals-container`'s own commands in
each lane checkout — `scripts/evals-container down` then
`scripts/evals-container --superpowers-root /tmp/sp-arm-fix up` — both
lanes came up clean (`status` → `exists, running` for both container
names, `docker ps -a` shows both `Up`, no `--force`/manual container
surgery). Per this task's operational instructions: if Docker crashes
again mid-battery, stop immediately, record the anomaly, and report
BLOCKED rather than retrying through a crashing daemon — same standing
rule round 1 already established.

**Budget estimate:** ~$40 for 8 reps, same figure as round 1's
pre-registration, now anchored to round 1's own measured actuals rather
than the pre-campaign estimate it originally cited: 6 valid round-1 reps
cost $26.82 total ($4.47/rep average) → ~$35.76 projected for 8 reps at
that rate; budgeting ~$40 for headroom given the two new fix commits
add a small amount of prompt text every dispatched role/turn re-reads
(negligible per-rep, but not zero).

**No run yet — this is the pre-registration.** Docker cycle above was
verification, not the smoke rep. Smoke test, full battery, scoring,
manual inspection, and verdicts (each verdict stating its round 1 →
round 2 delta) follow in later log entries.

### 2026-07-30 — SHARED SDD BATTERY ROUND 2: smoke PASS, all 8 reps complete (no Docker loss); ANOMALY — Gauntlet-Agent testing-budget exhaustion on 3/8 reps (Task 8b)

**Smoke test (rep9, lane A): PASS.** Gauntlet verdict `status: pass`.
8 rollout files (1 root + 7 children: `task{1,2,3}_{implementer,reviewer}`
+ `final_reviewer`). Manual inspection of the raw root rollout JSONL:
all 7 `spawn_agent` calls issued by the ROOT session only (every
non-root file has 0 `spawn_agent` calls) — zero worker-issued depth-2
spawns, all 7 carry explicit `model`+`reasoning_effort`
(`gpt-5.6-terra` x6 at low/medium, `gpt-5.6-sol`/`xhigh` for
`final_reviewer`), `fork_turns:"none"` throughout. **Root's
`wait_agent` calls (n=7, manually paired against
`function_call_output`): every single one used `timeout_ms:900000`
(the fix's recommended 15-minute long wait) and 0/7 timed out** — a
complete behavioral reversal from round 1's smoke rep (26 calls,
escalating 1000→30000ms, 72.0% timeout rate). No infra anomaly.
Proceeded to Step 3.

**Step 3 battery launch:** rep9 smoke on lane A, then `EVALS_ROOT=<lane
A> JOBS=2 bash run-quorum.sh fix cx-sdd-small 3 10` (reps 10-12) and
`EVALS_ROOT=<lane B> JOBS=2 bash run-quorum.sh fix cx-sdd-small 4 13`
(reps 13-16), launched concurrently via disowned background processes,
polled in-session with repeated foreground `kill -0`/`sleep 30` loops
(never a detached monitor). **All 8 pre-registered reps completed —
zero reps lost to Docker this round** (`docker ps -a` checked
repeatedly through the run: both lane containers stayed `Up` the
entire ~80-minute battery, no `Exited` transition, no daemon
disconnect). Every rep produced a complete `verdict.json` +
`trajectory.json` + `coding-agent-token-usage.json` (`partial: false`
on all 8, confirmed by reading each rep's own `verdict.json.economics`
directly) — a clean, fully-measured n=8, unlike round 1's Docker-crash
shortfall.

**ANOMALY — 3/8 reps (rep12, rep15, rep16) got Gauntlet-Agent
`indeterminate`/`investigate` verdicts, NOT because of Docker, a
wait_agent timeout, or a coding-agent hang, but because a genuinely
long single wait exhausted the Gauntlet-Agent's own testing-time
budget before real (slow but legitimate) work finished.** Root-caused
by direct inspection of all 3 reps' raw root rollouts (`function_call`/
`function_call_output` pairs, manually parsed, not via a scorer):

- **rep12:** `task1_implementer` dispatched 20:40:51Z, its `wait_agent`
  (`timeout_ms:3600000`) resolves cleanly 96s later. `task1_reviewer`
  dispatched 20:42:55Z; its `wait_agent` (`timeout_ms:3600000`) is
  issued 20:42:58Z and does not resolve until **21:13:46Z — 30m48s of
  total silence in the transcript** — `{"message":"Wait completed.",
  "timed_out":false}` (the review genuinely took that long; the
  timeout itself was never hit). The reviewer's `FINAL_ANSWER` surfaces
  a real, legitimate finding (a plan-sequencing conflict: Task 1's
  `pyproject.toml` references `README.md`, which Task 3 doesn't create
  until later) and root asks the Gauntlet-Agent a genuine clarifying
  question. Root's own turn ends cleanly with a `task_complete` event
  at 21:13:56Z — **this is not a stall or a crash; the coding session
  reached a normal, well-formed stopping point** (a question awaiting
  a human/Gauntlet-Agent reply). `phase.json` shows `"phase":"checks"`
  at 21:14:13Z — i.e. quorum's overall run budget expired essentially
  simultaneously and moved the pipeline to post-checks before any
  reply could arrive. Gauntlet-Agent's own verdict summary confirms the
  mechanism independently: "the session went idle for over 22 minutes
  ... and I ran out of my allotted testing time budget while waiting."
  1 commit only (Task 1's core utilities); Task 2/3 never dispatched.
- **rep15:** same shape. `task2_reviewer` dispatched 20:46:03Z; its
  `wait_agent` (`timeout_ms:900000`) issued at 20:46:03Z, resolves
  `timed_out:false` at 21:08:35Z (~22m32s silent) — again well past
  its own nominal 15-minute `timeout_ms`, confirming `wait_agent`'s
  `timeout_ms` is not a hard ceiling on this platform; it waits for
  real completion or its ceiling, whichever is later observed, not a
  strict cutoff. `task3_implementer` is then dispatched 21:14:06Z and
  its own `wait_agent` call (21:14:08Z) is issued but **never paired
  with an output before the run was cut off** — this is the one
  genuinely lost unit of work this round (see T5/T2 numbers below). 2
  commits (Task 1, Task 2); Task 3 implementer mid-flight, uncommitted,
  when cut off.
- **rep16:** same shape again. `task2_implementer` dispatched
  20:42:30Z; its `wait_agent` (`timeout_ms:900000`) resolves
  `timed_out:false` at 21:20:06Z (~37m34s silent) — the single longest
  silent span across the round. Its report ("# Task 2 Report") prints
  cleanly right after; the run is cut off before `task2_reviewer` could
  even be dispatched. 2 commits (Task 1, Task 2); Task 2 review
  never started.

**Mechanism, stated plainly:** the T2 fix (commit `3da65fb`) works
exactly as intended at the `wait_agent` level — see the T2 verdict
below, 0% timeout rate, a complete elimination of round 1's pathology.
But converting dozens of short, visible polls into one long, silent
wait means the Gauntlet-Agent (a separate LLM watching a live terminal
to grade the run) now sees extended stretches — in these 3 cases,
22-38 minutes — of **zero new transcript content** while a review or
implementation genuinely keeps working underneath. Gauntlet-Agent's
own testing-time budget (not configured or controlled by this task) is
finite; when a review or implementation step legitimately takes
20-40 minutes, the silence alone can consume that whole budget, and
Gauntlet-Agent reasonably (from its own vantage point, per its
`investigate` reasoning field in all 3 cases) cannot distinguish
"working silently for a long time, per instructions" from "stalled."
This was invisible under round 1's short-poll behavior specifically
*because* short polls kept refreshing the visible transcript every
10-30s regardless of how long the underlying review actually took.

**Not a Docker anomaly, not covered by this task's Docker-crash STOP
instruction** — the daemon and both containers stayed healthy and
running for the entire battery; this is confirmed by direct, repeated
`docker ps -a` checks during the run. Per this log's standing rule
(record honestly, do not smooth over), this is reported as a real,
fix-caused, second-order side effect discovered during the battery
itself, not a pre-existing pathology and not an artifact of the
scoring tooling — the battery was allowed to run to completion (all 8
reps finished; nothing was stopped mid-flight) because the anomaly is
about Gauntlet-Agent's grading, not about infrastructure integrity.

**Cost (8 completed reps, from each rep's own `verdict.json`
`economics.total_est_cost_usd`, all `partial: false`):** rep9 $3.55,
rep10 $4.61, rep11 $4.17, rep12 $1.16, rep13 $3.82, rep14 $3.85, rep15
$2.01, rep16 $1.72 — **$24.89 total, all 8 measured directly**, well
under the ~$40 pre-registered budget (the 3 cut-short reps are cheaper,
not more expensive, since less coding-agent work happened before the
cutoff).

### 2026-07-30 — SHARED SDD BATTERY ROUND 2: T1/T2/T5 verdicts on n=8, round 1 → round 2 deltas (Task 8b)

Scored all 8 reps (9-16) with `score_e6.py` (T1), a fresh one-off
script reusing `score_e7.py`'s tested `census_session()`/`aggregate()`
functions against the fix-arm RUNDIRs across both lanes (T2 —
`score_e7.py` still hardcodes `arms=("dev","spinout")`, confirmed
unchanged since round 1, so it still doesn't fit `fix` split across two
lane checkouts; the one-off script, `/private/tmp/.../scratchpad/
round2/score_e7_fix_battery_round2.py`, not committed — scratch, not a
campaign artifact — writes only a new `out/e7-battery-fix-round2.json`,
untouched otherwise), and `score_e1.py` (T5). Outputs:
`out/e6-cx-sdd-small-fix-rep9-16.json`,
`out/e7-battery-fix-round2.json`, `out/e1-cx-sdd-small-fix-rep9-16.json`
— none collide with round 1's `rep1-8`-suffixed files or the frozen
corpus (a)/(b) blobs; `FORCE` was never set.

**Manual inspection (non-circular — raw rollout JSONL, not scorer
helpers), beyond the brief's 2-run minimum:**
- **Depth-2 spawn census (T1) — exhaustive, not sampled:** `grep -c
  '"name":"spawn_agent"'` against every one of the 59 rollout files
  across all 8 reps (`find .../home/.codex/sessions -name '*.jsonl'`
  per rep, root vs non-root). Every non-root file in every rep: 0
  `spawn_agent` calls. Root-only spawn totals per rep: 7/8/9/2/9/8/5/3
  (reps 9-16) = **51, matching `score_e1`'s total spawn count exactly**
  and `score_e6`'s `depth-2 spawns by spawner role: {}` (empty dict —
  zero, across all 8 reps, not just the reps that finished cleanly).
- **Review coverage (T1):** independently re-read every root session's
  raw `spawn_agent` argument dump (task_name/model/reasoning_effort).
  The 4 fully-completed reps (10, 11, 13, 14) each show
  `task{1,2,3}_{implementer,reviewer}` (one reviewer per task, no
  duplicates) + `final_reviewer` + a fix-cycle reviewer
  (`final_fix_reviewer`, 2 reps also dispatch `final_fix_implementer`)
  — normal SDD defect-fix-wave flow, entirely root-issued. The 3
  cut-short reps (12, 15, 16) each show exactly one reviewer per task
  actually reached (rep12: task1 impl+rev only; rep15: task1 impl+rev,
  task2 impl+rev, task3 impl-only — reviewer never dispatched, cut off
  first; rep16: task1 impl+rev, task2 impl-only) — **no duplicate
  reviews anywhere, and no task that reached review got more or fewer
  than exactly one reviewer.**
- **Wait-timeout classification (T2):** independently re-parsed 4 full
  sessions' raw `wait_agent`/`function_call_output` pairs (rep9: 7
  calls; rep12: 2 calls; rep15: 5 calls; rep16: 3 calls — 17 of the
  corpus's 55 total calls, more than double the brief's 2-run minimum)
  with fresh `json.loads`/call_id pairing, not `rollout_parser`. Every
  count and `timed_out` value matches `out/e7-battery-fix-round2.json`'s
  per-session numbers exactly, including the single excluded
  (unpaired) call — confirmed to be rep15's cut-off `task3_implementer`
  wait via direct JSON inspection of the scorer's own `sessions[]`
  array (`n_wait_agent_calls:5 n_paired:4 n_excluded:1 n_timed_out:0`,
  path matches rep15's root rollout).
- **Explicit-model claims (T5):** the raw per-rep spawn dumps used for
  the review-coverage check above double as independent T5
  verification — all 51 spawns across all 8 reps carry non-null
  `model` and `reasoning_effort` keys directly in the raw `arguments`
  JSON (not scorer inference), matching `score_e1`'s 51/51 (100%)
  `explicit_model` exactly.
- **Advisory config backstop:** checked rep9's container
  `home/.codex/config.toml` — no `[agents]`/`default_subagent_*` keys,
  same as round 1. Still unprovisioned in this eval environment;
  untested by this battery, as before.

**Aggregate numbers (8 reps, from the three JSON blobs):**
- T1: **0 worker-issued depth-2 spawns across 8 reps** (0/8 reps
  affected), 0 same-task duplicate-review families.
- T2: **55 wait_agent calls, 54 paired, 1 excluded (rep15's cut-off
  call), 0 timed out — 0.0% timeout rate (paired and all-calls).**
  Gauntlet verdict: **5/8 pass (62.5%), 3/8 indeterminate (37.5%)** —
  rep12/15/16, per the anomaly entry above. `score_e1`'s aggregate
  shows **50/51 (98.0%) resolved child rollouts with `task_complete`
  present** — the 1 miss is rep15's cut-off `task3_implementer` (raw
  rollout confirms it started work but the file ends before any
  `task_complete` event).
- T5: **51/51 spawns (100.0%) carry explicit model; 0 model_omitted.**
  All 51/51 are root-issued (depth-1) — T1 eliminated depth-2 entirely
  this round, so there is no depth-2 population left to grade.
  `fork_turns:"none"` on all 51/51 spawns (isolation unaffected).

**Verdicts against the pre-registered criteria, each with its round 1
→ round 2 delta:**

- **T1 (0 worker-issued depth-2 spawns AND review coverage preserved):
  PASS. Delta: FAIL → PASS.** Round 1: 2 depth-2 spawns in 1/6 reps
  (16.7%), both from a controller-dispatched reviewer role that the
  original no-subagents contract never reached. Round 2: 0 depth-2
  spawns in 0/8 reps (0.0%) — an exhaustive, full-corpus grep across
  all 59 rollout files, not a sample. Review coverage preserved
  cleanly on both rounds (6/6 round 1, 8/8 round 2 for every task that
  reached the review stage). Commit `c07cf7e` (reviewer no-subagents
  contract, extended to `code-reviewer.md`/`re-review-prompt.md`/
  `task-reviewer-prompt.md`) directly targeted this gap and closed it
  completely at n=8, with zero new depth-2 leaks appearing from any
  other role.
- **T2 (timeout rate < 25% with no loss of task completion): FAIL on
  the strict conjunction, but a categorically different and far
  smaller miss than round 1. Delta: FAIL (dominant-metric miss) → FAIL
  (secondary-clause miss only).** The timeout-rate clause is now a
  clean, dramatic PASS: 0.0% vs round 1's 65.1% — commit `3da65fb`
  (controller wait discipline) eliminated the original pathology
  entirely; total wait_agent call volume also dropped from ~25/rep
  (150 calls / 6 reps, round 1) to ~6.9/rep (55 calls / 8 reps, round
  2). The "no loss of task completion" clause, however, is not cleanly
  met this round: round 1 was 100%/100% on both operationalizations
  this log uses (6/6 gauntlet pass, 50/50 child `task_complete`);
  round 2 is 62.5% gauntlet pass (5/8) and 98.0% child `task_complete`
  (50/51). Per the anomaly entry above, this is not the same failure
  mode as round 1 (no hangs, no wait_agent timeouts, no Docker loss,
  no coding-agent bug) — it is a newly surfaced, directly-traced
  interaction between the fix's own recommended long-wait behavior and
  the Gauntlet-Agent's fixed testing-time budget. Recorded as FAIL
  because the pre-registered criterion is an explicit conjunction and
  1/51 dispatched children genuinely never reported completion (not
  zero, as the criterion requires) — but flagged clearly that this
  FAIL reflects the fix working exactly as designed on the metric it
  targeted, at the cost of an unanticipated harness-visibility
  trade-off, not a regression in the underlying coding-agent behavior.
- **T5 (every spawn at every depth carries explicit model + effort):
  the pre-registered zero-depth-2 caveat now applies (it did not in
  round 1). Delta: FAIL (real depth-2 miss found and graded) →
  INCONCLUSIVE-BY-ZERO at depth-2 (no depth-2 population exists to
  grade), PASS on the root-spawn-regression backstop.** T1 eliminated
  depth-2 spawns entirely this round (0/51), so per the pre-registered
  caveat, T5 is recorded inconclusive-by-zero at depth-2 rather than
  graded — there is nothing left to check for model/effort omission at
  that depth. The backstop clause (root-controller depth-1 spawns hold
  100% explicit) passes cleanly: 51/51, matching round 1's 48/48
  (100%) depth-1 rate — no regression at the depth that was already
  working. The advisory config backstop
  (`~/.codex/config.toml`'s `[agents] default_subagent_*`) remains
  unprovisioned in this eval environment, same as round 1 — still
  untested by any battery to date.

**Ledger row:** 2026-07-30 | Shared SDD battery ROUND 2 T1/T2/T5 (fix
arm @ `3da65fb`, cx-sdd-small, n=8 of 8 pre-registered — no Docker loss
this round) | $24.89 (8/8 measured, `partial: false` on all) | T1 PASS,
T2 FAIL (timeout clause PASS, completion clause FAIL — see anomaly),
T5 inconclusive-by-zero at depth-2 / PASS on backstop.

**Status: T1/T2/T5 verdicts delivered on the full pre-registered n=8 —
no Docker loss this round (contrast round 1's n=6 shortfall). T1 fully
flips FAIL→PASS: the reviewer-scoped no-subagents contract closed the
exact gap round 1 found, with zero new leaks anywhere else. T2's core
mechanism (wait_agent timeout rate) also fully flips FAIL→PASS
(65.1%→0.0%), but the pre-registered criterion's second clause
surfaces a new, honestly-reported side effect: 3/8 reps didn't reach a
clean Gauntlet-Agent pass because the same long-wait behavior that
fixed the timeout rate also produces silent stretches long enough to
exhaust the QA harness's own testing-time budget on genuinely slow
reviews — a harness-visibility trade-off, not a coding-agent
regression, but real enough that the strict criterion is not met. T5's
caveat condition flipped (T1's win removed the depth-2 population T5
was grading), so T5 moves from a real FAIL to inconclusive-by-zero
plus a clean backstop PASS. Net: 1 of 3 treatments (T1) is an
unqualified win; T2 is a mechanism-level win with an honestly-reported
new side effect; T5's FAIL was contingent on T1's prior failure and
resolves along with it.**

### 2026-07-30 — T4 LAYER 2 PRE-REGISTRATION: Codex ceremony battery on the fix arm (Task 9)

Layer 1 (MICRO, previous entry) PASSed every pre-registered C-approval
cell, clearing this heavier battery to spend per that entry's hard rule.
This is layer 2: the real Codex-agent ceremony census
(`cx-ceremony-{spike,bounded,arch}`) against the fix arm, using
`score_e4.py` (built and validated in the original campaign — see
`logs/2026-07-28-codex-efficiency.md`'s E4 entries) rather than the
Anthropic-API micro.

**Arm SHA (verified this task, NOT refreshed):** `git -C /tmp/sp-arm-fix
log --oneline -1` → `3da65fb` — matches the `codex-efficiency-fixes`
branch tip in the working worktree and the SHA already graded by Task
8b's shared SDD battery round 2 (T1 PASS / T2 mechanism-PASS-but-
completion-FAIL / T5 inconclusive-by-zero-plus-backstop-PASS). This
battery adds no new commits on top — it is measuring the same graded
tip against a different scenario family (ceremony, not SDD).

**`score_e4.py` arm-hardcoding check (per this task's brief, which
flagged this as a possible repeat of the `score_e7.py` problem):**
confirmed by reading the script — `main()` takes `RUNDIR...` positional
arguments directly and infers `arm_scenario`/`scenario_class` from each
RUNDIR's own parent directory name (`cx-eff-<scenario>-<arm>-repN`
convention, via `_parent_label()`/`_scenario_key()`). No hardcoded arm
list, no hardcoded results directory, unlike `score_e7.py`'s
`score_battery()`. **No one-off workaround script is needed this task**
— `score_e4.py` is invoked directly against the fix-arm RUNDIRs from
both lanes' `results/` trees in one call, exactly as it already handles
the dev arm's 5-arch/3-bounded/3-spike mixed corpus on disk
(`out/e4-mixed-...json`).

**Battery config:**
- Arm: `fix` (`/tmp/sp-arm-fix` @ `3da65fb`)
- Scenarios: `cx-ceremony-spike`, `cx-ceremony-bounded`, `cx-ceremony-arch`
  — 3 reps each, 9 runs total. Each scenario has its own independent
  rep counter in `run-quorum.sh`'s `results/cx-eff-<SCEN>-<ARM>-repN`
  naming (unlike the shared-SDD battery's single shared scenario across
  two rounds), and no `cx-eff-cx-ceremony-*-fix-*` directory exists yet
  in either lane's `results/` (checked before this entry) — so all
  three scenarios start fresh at rep1, no round-2-style renumbering
  needed.
- Lane split: lane A (`superpowers/evals`, default `EVALS_ROOT`) runs
  `cx-ceremony-bounded` (rep1 = Step 2 smoke, then reps 2-3) and
  `cx-ceremony-spike` (reps 1-3) — 6 reps. Lane B (`evals-lane-b`) runs
  `cx-ceremony-arch` (reps 1-3) — 3 reps, run concurrently with lane
  A's queue since the two lanes are independent containers; `arch`'s
  30-minute `quorum_max_time` against `spike`/`bounded`'s 15-minute
  budget is why arch gets its own lane rather than splitting reps
  within a scenario across lanes.
- Scorer: `score_e4.py`, invoked once across all 9 RUNDIRs (both lanes'
  `results/` trees) once the battery completes. Output:
  `out/e4-<label>-rep1-3.json` (or whatever `_out_label()` derives from
  the mixed arm_scenario set — not forced in advance).
- `FORCE` never set; a collision is an anomaly, not a flag to suppress.

**Criteria (from this log's "Pre-registered criteria" section above,
T4 layer 2, reproduced verbatim from the brief):**
- **Bounded:** approval turn present (a human-approval exchange visible
  in the root rollout before implementation starts), 0 committed
  spec/plan docs (nothing under `docs/superpowers/specs/` or
  `docs/superpowers/plans/` — NOT the same as `score_e4.py`'s raw
  `docs_written_before_first_non_doc_patch` count, which flags ANY
  `docs/`-path or `*.md` file; hand verification must filter the
  scorer's `doc_paths_written_before_first_non_doc_patch` list down to
  the `docs/superpowers/{specs,plans}/` subset specifically, since a
  scenario could legitimately touch some other `.md`/`docs/` path
  without that being ceremony), 0 writing-plans ritual (no
  `docs/superpowers/plans/*.md` path written at all).
- **Arch:** two-doc flow intact 3/3 — every rep writes exactly one
  `docs/superpowers/specs/*.md` AND one `docs/superpowers/plans/*.md`
  before its first non-doc patch (the same shape the dev-arm baseline
  showed unconditionally; see below).
- **Spike:** no docs, minimal ceremony (low tool-call/user-turn counts
  before any real investigation output; the dev baseline's spike class
  produced no non-doc patch at all in any of 3 reps — this fix-arm
  battery must independently check whether that structural
  unmeasurability persists or whether C-approval's spike path, which
  explicitly says "No design doc, no spec file," changes the shape).
- **Cross-cutting:** gauntlet task completion preserved per cell (no
  cell regresses from the dev baseline's pass rate on session-completion
  grounds, independent of the ceremony-shape findings above).

**Dev-arm ceremony baseline — CITED, NOT RE-RUN this task** (per this
task's explicit instruction). Full detail:
`logs/2026-07-28-codex-efficiency.md`, "E4 RESULT" entry (Task 11,
2026-07-29/30) and `campaigns/codex-efficiency/out/e4-report.md`:
- Spike: all 3 dev reps show `no_non_doc_patch=True` (zero
  `patch_apply_end` events of any kind) — the primary discrimination
  gate (spike vs. arch tool-calls) was inconclusive-by-zero on the dev
  arm for a structural reason (a correctly-executed spike investigates
  via ephemeral inline shell/Python, never touching a tracked file), not
  a scenario-design failure.
- Bounded vs. arch: mean tool-calls-before-T 16.7 (bounded) vs. 24.0
  (arch), a 30.4% gap — just outside the pre-registered 25% band, so
  ceremony volume was NOT flat on the dev arm, but every single rep in
  BOTH classes wrote exactly 2 docs before any code (design spec, then
  plan) — the two-document ritual ran unconditionally regardless of
  task complexity, hand-verified for bounded rep1 against raw
  `patch_apply_end` timestamps (docs at 19:24:58/19:26:04, first
  non-doc patch at 19:27:22.703; user_turns=4, tool_calls=13,
  wall_clock=246s — matched the scorer's own output exactly).
- This is exactly the pathology C-approval's shipped router text (Task
  5's commit `5ea8821`) targets: bounded should route to "short design
  IN CHAT... No spec file, no implementation plan document," not the
  dev arm's unconditional two-doc ritual. This battery is the first
  REAL-Codex-agent (not Anthropic-API-micro) test of whether the shipped
  text actually changes that behavior, as opposed to layer 1's
  literal-instruction-following-only micro result.

**Budget estimate:** ~$40 (per the brief). Anchor point: the dev arm's
original 3-reps/class ceremony battery (9 clean + 2 outage-tainted
reps, lane A only, JOBS=2) cost $21.39 total for 11 runs (~$1.94/run
average including the outage-tainted pair); 9 reps at that rate would
be ~$17.50. Budgeting ~$40 for headroom given C-approval's shipped text
adds a small amount of prompt content every brainstorming invocation
re-reads (negligible per-rep but not zero), and given the smaller
ceremony scenarios have historically been far cheaper per rep than the
shared SDD scenario the last two batteries measured.

**No run yet — this is the pre-registration.** Smoke test, full
battery, scoring, and manual hand-verification (one rep per class
against raw `patch_apply_end` timestamps, the same non-circular method
used for the dev-arm bounded-rep1 citation above) follow in later log
entries.

### 2026-07-30 — T4 LAYER 2 RESULT: Codex ceremony battery — bounded's doc/plan pathology cleanly fixed, its approval-gate compliance only partial; arch two-doc flow intact 3/3; spike minimal; one scenario-timeout anomaly (Task 9)

**Smoke test (bounded rep1, lane A): PASS, scenario health confirmed.**
`gauntlet.status: pass`. Root-identity marker match confirmed
("suppresses request logging" present in the first `user_message`).
Bootstrap loaded and reachable: raw rollout shows 173 `SKILL.md`
mentions, 139 `superpowers` mentions, and a full `using-superpowers`
skill-body read via the `host_skills` world-state mechanism — the
skill system is live for Codex in this container, not a silent no-op.
Deterministic checks and Economics block both present, no infra
anomaly. One important behavioral observation flagged for the full
battery rather than adjudicated on n=1: the smoke rep's agent invoked
systematic-debugging + test-driven-development directly, never
brainstorming, and applied both patches (`tests/test_server.py` then
`server.py`) BEFORE the Gauntlet-Agent's "looks good, that's what I
wanted" confirmation — i.e. approval arrived after implementation, not
gating it. Proceeded to Step 3.

**Step 3 battery launch:** lane A ran `cx-ceremony-bounded` reps 2-3
(`JOBS=2`, one batch) then, once that finished cleanly, `cx-ceremony-spike`
reps 1-3 (`JOBS=2`, two batches); lane B ran `cx-ceremony-arch` reps 1-3
(`JOBS=2`, two batches) concurrently with lane A's queue. All launched as
disowned background processes, polled in-session via repeated foreground
`sleep 30` loops checking for a written `EXIT:` sentinel (never a detached
monitor). `docker ps -a` checked repeatedly through the run: both lane
containers stayed `Up` for the entire ~50-minute battery, no `Exited`
transition — **no Docker loss this task**, unlike round 1 of the shared
SDD battery.

**ANOMALY — arch rep3 hit the scenario's own 30-minute `quorum_max_time`
budget before the Gauntlet-Agent could render a clean verdict; NOT a
Docker/infra failure.** Confirmed directly: `docker ps -a` showed both
containers healthy throughout: rep3's own `verdict.json` has
`economics.partial: false` (a complete, non-crash-orphaned run, unlike
the shared-SDD battery's Docker-crash casualties which never got a
`verdict.json` at all) and 12 rollout files (root + an implementer/reviewer
tree — this rep's agent chose to run the architectural split through
`subagent-driven-development`, unlike rep1/rep2 which each stayed a single
un-spawned session). `final: indeterminate`, `gauntlet.status: investigate`.
The Gauntlet-Agent's own verdict text states the mechanism plainly: "every
checkpoint showed forward progress (new commits, new task completions, a
real bug found in review)... It's more likely that this scenario's very
thorough 'spec → plan → subagent implementation → whole-branch review →
fix wave → re-review' ceremony simply takes longer wall-clock time than
the 1800s budget allowed." Per this task's operational rule, a genuine
infra crash stops the battery; this is not that — it is the same
character of side effect Task 8b already documented (a scenario-shape
constraint interacting with how long a legitimate SDD-style ceremony
takes), and the run produced complete, scoreable rollout data despite
the non-`pass` verdict, so **the battery was allowed to run to
completion, not stopped** — consistent with Task 8b's own precedent for
exactly this distinction (infra-integrity anomalies stop the battery;
harness/scenario-budget anomalies on an otherwise-healthy run get
recorded and scored). `run-quorum.sh`'s own exit code for lane B was 1
(`a parallel rep failed (JOBS=2)`, because `quorum run` itself exits
nonzero on a non-`pass` verdict) — this is the shell script's batch-level
signal, not evidence of data loss; rep3's RUNDIR is complete and was
scored normally below.

**All 9 pre-registered reps produced usable, complete rollout data** (1
smoke + 8 remaining, no reps lost) — bounded 1-3, spike 1-3, arch 1-3, all
with `economics.partial: false`. `gauntlet.status`: 8/9 `pass`, 1/9
(`arch rep3`) `investigate` (the anomaly above).

**Scoring:** `score_e4.py`, invoked directly against all 9 RUNDIRs in one
call (no arm-hardcoding workaround needed — confirmed by reading the
script before this task's pre-registration: `main()` takes `RUNDIR...`
positional args and infers scenario/arm from each RUNDIR's own parent
directory name, unlike `score_e7.py`'s hardcoded arm list). Output:
`out/e4-mixed-cx-ceremony-arch-fix-cx-ceremony-bounded-fix-cx-ceremony-spike-fix-rep1-3.json`.

**Results (from the scorer's own per-run table):**

```
class     rep  no-patch  user turns  docs written  tool calls  wall-clock(s)
bounded    1      no          1           0             4          31
bounded    2      no          1           0             4          35
bounded    3      no          2           0             5          84
spike      1      no          1           0             5          45
spike      2     YES         N/A          0            N/A         N/A
spike      3     YES         N/A          0            N/A         N/A
arch       1      no          7           2            13         528
arch       2      no          7           2            18         630
arch       3      no          8           2            19         770
```

Per-class means: spike 5.0 tool calls (n=1 rep with a measurable patch;
0.0 docs); bounded 4.3 tool calls, 0.0 docs; arch 16.7 tool calls, 2.0
docs. Discrimination gate (spike vs. arch mean tool-calls-before-T):
ratio 0.30, NOT within 25% → **"ceremony scales with task complexity"**
— in direct contrast to the dev-arm baseline, where the same gate was
inconclusive-by-zero because ALL 3 dev spike reps had zero patches of
any kind. This fix-arm spike class has 1/3 reps with a measurable
patch, giving the gate an actual (if thin, n=1) data point instead of
an undefined one.

**Manual hand-verification (non-circular — independent `json.loads` +
own `patch_apply_end` timestamp sort, not `rollout_parser`), one rep
per class plus both no-patch spike reps and both non-smoke bounded
reps (beyond the brief's 1-rep-per-class minimum):**

- **bounded rep1:** raw patches — `tests/test_server.py` at
  `21:40:13.660Z`, `server.py` at `21:40:39.672Z`. T = `21:40:13.660Z`
  (first is already non-doc — no docs preceded it). Independently
  recomputed: user_turns_before_T=1, tool_calls_before_T=4,
  wall_clock=session_start(`21:39:43.069Z`) to T = 30.591s ≈ 31s.
  **Matches the scorer's row exactly (1 / 0 docs / 4 / 31).**
- **arch rep1:** raw patches, chronological —
  `docs/superpowers/specs/2026-07-30-reusable-notes-library-design.md`
  (`21:48:11.062Z`), `docs/superpowers/plans/2026-07-30-reusable-notes-library.md`
  (written twice, `21:50:36.421Z` and `21:50:53.081Z` — a revision, still
  one distinct path), then `.gitignore` (`21:53:25.754Z`, the first
  NON-doc patch — same edge case the dev-arm baseline already flagged:
  a worktree-setup `.gitignore`, not real service code, but correctly
  classified non-doc under the registered rule), then a long sequence of
  real implementation files under `.worktrees/reusable-notes-library/`.
  T = `21:53:25.754Z`. Independently recomputed:
  user_turns_before_T=7, tool_calls_before_T=13,
  wall_clock=session_start(`21:44:37.542Z`) to T = 528.212s ≈ 528s.
  **Matches the scorer's row exactly (7 / 2 docs / 13 / 528), and the 2
  distinct doc paths are exactly one `docs/superpowers/specs/*.md` and
  one `docs/superpowers/plans/*.md` — the two-document ritual, not two
  arbitrary `.md` files.**
- **spike rep1:** raw patches — `tests/test_server.py`
  (`21:56:39.529Z`, already non-doc, T here) then `server.py`
  (`21:56:53.954Z`). Independently recomputed: user_turns_before_T=1,
  tool_calls_before_T=5, wall_clock=session_start(`21:55:55.000Z`) to
  T = 44.529s ≈ 45s. **Matches the scorer's row exactly (1 / 0 docs / 5
  / 45).**
- **spike rep2/rep3 (the two no-patch reps):** raw transcripts read in
  full (not just the scorer's boolean). Both show the exact scripted
  spike shape: agent reads the bind path, proposes a throwaway probe
  ("Sound good?" / a description of the plan), Gauntlet-Agent gives a
  nod (`"Yes, go ahead."` / `"Sounds good."`) BEFORE the probe runs, the
  probe executes via ephemeral shell/Python only (confirmed: zero
  `patch_apply_end` events of any kind in either rollout, matching
  `no_non_doc_patch: true`), and the session ends cleanly after the
  Gauntlet-Agent's "thanks, that answers it." Genuinely minimal,
  genuinely healthy runs — not truncated or broken.
- **bounded rep2/rep3 (the approval-timing check — the finding that
  drives this battery's verdict below):** raw transcripts read in full.
  **Rep2** matches the smoke rep's shape exactly: task at `21:46:11Z`,
  immediate systematic-debugging+TDD narration, patch to
  `tests/test_server.py` at `21:46:46Z`, patch to `server.py` at
  `21:47:14Z`, THEN "looks good, that's what I wanted" at `21:48:32Z` —
  approval arrives after both patches, not before. **Rep3 is different:**
  task at `21:45:05Z`, the agent explicitly says "This is a bounded
  change. Proposed design: add `--quiet` to the CLI..." at `21:45:34Z`,
  Gauntlet-Agent replies "looks good, that's what I wanted" at
  `21:45:58Z`, the agent says "Approved. I'll now follow the TDD
  cycle..." at `21:46:06Z`, and ONLY THEN does the first patch land
  (`21:46:29Z`). Rep3 genuinely gates implementation behind a
  pre-implementation approval turn, exactly as the router's HARD-GATE
  text mandates ("Do NOT invoke any implementation skill, write any
  code... until you have told your human partner what you intend and
  they have approved it. This applies to EVERY task on EVERY path").
  Rep1 and rep2 do not: both implement first, both receive an
  approval-shaped message only afterward as a post-hoc confirmation, not
  a gate.

**Verdicts against the pre-registered criteria (verbatim from this log's
T4-layer-2 pre-registration entry above):**

- **Bounded — "0 committed spec/plan docs": PASS, 3/3.** Every bounded
  rep's `doc_paths_written_before_first_non_doc_patch` is the empty
  list — confirmed by the scorer's JSON and independently by the raw
  `patch_apply_end` scan of all 3 reps (only `tests/test_server.py` and
  `server.py` ever get touched). This is a clean, complete fix of the
  dev-arm pathology (which wrote exactly 2 docs unconditionally on
  every bounded rep).
- **Bounded — "0 writing-plans ritual": PASS, 3/3.** No
  `docs/superpowers/plans/*.md` path appears in any bounded rep's patch
  history — the writing-plans skill's own artifact never appears,
  consistent with "0 committed spec/plan docs" above (a plan file would
  itself be a spec/plan doc).
- **Bounded — "approval turn present": MIXED, not a clean pass — real
  and honestly reported, not collapsed to a single number.** Under a
  loose reading (some approval-shaped Gauntlet-Agent message exists
  anywhere in the transcript), 3/3 — the scripted stimulus phrase
  ("looks good, that's what I wanted") appears in all 3 reps. Under the
  strict reading the router's own HARD-GATE text actually specifies
  (approval must come BEFORE any implementation action, on EVERY path,
  no exception), only **1/3 (rep3)** complies: rep1 and rep2 both
  implement first and receive the approval-shaped message only after
  code already exists. **This is a genuine, real gap in live Codex-agent
  compliance with the shipped router text's mandatory gate** — one the
  layer-1 MICRO (literal one-word classification against a static
  prompt, no live multi-turn session) structurally could not detect,
  since it only tested whether the model NAMES the right path, not
  whether it actually ENFORCES the gate across a real multi-turn
  session where jumping straight into familiar skills
  (systematic-debugging, TDD) is an easy, plausible-looking shortcut
  around the approval step.
- **Arch — "two-doc flow intact 3/3": PASS, 3/3.** Every arch rep writes
  exactly one `docs/superpowers/specs/*.md` and one
  `docs/superpowers/plans/*.md` before its first non-doc patch —
  confirmed by the scorer's JSON and independently hand-verified for
  rep1 against raw timestamps. Matches the dev-arm baseline's own
  unconditional two-doc shape on this class (the fix targets bounded's
  over-ceremony, not arch's correctly-heavy ceremony, and arch shows no
  regression). Same minor edge case as the dev baseline: all 3 reps'
  first NON-doc patch is a `.gitignore` addition (worktree setup),
  seconds-to-tens-of-seconds before real implementation files — noted,
  not qualitatively significant.
- **Spike — "no docs, minimal ceremony": PASS, 3/3.** Zero doc paths in
  any spike rep. 2/3 reps produce no patch at all (pure ephemeral
  investigation, hand-verified as genuinely healthy above); the 1/3 rep
  with a measurable patch shows the lowest tool-call count of any class
  (5, vs. bounded's 4.3 mean and arch's 16.7 mean) and a 45-second
  wall-clock — minimal by every measure available.
- **Cross-cutting — "gauntlet task completion preserved per cell":
  PASS for bounded (3/3) and spike (3/3); FAIL for arch (2/3, rep3
  `investigate` on the scenario-timeout anomaly above) — an honest,
  scenario-budget-driven miss, not a router-text pathology. Rep3's own
  ceremony shape (2 docs, T at 528s-equivalent scale... actually 770s
  wall-clock to T) is itself still consistent with the two-doc-flow
  PASS above; only the FULL task's completion, not the ceremony
  question this battery targets, is affected.

**Cost (9 reps, from each rep's own `verdict.json.economics.total_est_cost_usd`,
all `partial: false`):** bounded $0.71 + $0.91 + $0.67 = $2.30; spike
$0.62 + $0.55 + $0.55 = $1.72; arch $3.02 + $2.43 + $5.76 = $11.21 (arch
rep3's cost is the highest of any rep in the battery — consistent with
it running the full scenario-timeout budget before being cut off).
**Total: $15.23**, well under the ~$40 pre-registered budget.

**Ledger row:** 2026-07-30 | T4 layer-2 Codex ceremony battery (fix arm
@ `3da65fb`, `cx-ceremony-{spike,bounded,arch}`, n=9 of 9 pre-registered
— no Docker loss) | $15.23 (9/9 measured, `partial: false` on all) |
bounded: doc/plan ritual PASS 3/3, approval-gate compliance 1/3 strict
(3/3 loose) | arch: two-doc flow PASS 3/3, completion FAIL 2/3
(scenario-timeout, not infra) | spike: PASS 3/3 | discrimination gate:
ceremony scales with complexity (ratio 0.30, thin n=1 spike sample).

**Status: DONE, mixed result, honestly reported in both directions —
the same character as the original campaign's E4 finding, not a clean
win.** The router text's most measurable, mechanical claim — bounded
tasks should produce NO spec/plan documents and NO writing-plans
ritual — is now **cleanly fixed**: 0/3 docs on the fix arm vs. the dev
arm's unconditional 2/3 docs every single bounded rep. Arch's
two-document ceremony (the scenario class where heavy ceremony IS
correct) is fully intact at 3/3, matching the dev baseline with no
regression. But the router text's OTHER core claim — the HARD-GATE's
"approval never scales down, not on any path" — is only 1/3 compliant
under a strict live-session reading; 2/3 bounded reps route correctly
(no doc ceremony) but skip the mandatory pre-implementation approval
turn entirely, jumping straight from task receipt into
systematic-debugging/TDD execution and only requesting confirmation
after the code already exists. **This is a new finding this layer-2
battery was specifically positioned to catch and layer-1's micro
structurally could not:** removing unnecessary DOCUMENT ceremony
(fixed) is not the same claim as preserving the APPROVAL gate (only
partially fixed), and a router text whose bounded-path instructions
read "Ask the clarifying questions that matter, present a short design
IN CHAT... and get approval" can still get literally-correctly
skipped by a capable model that treats "no spec file needed" as
license to skip presenting a design at all, not just skip writing one
to a file. Recommend flagging this specific gap (bounded-path
approval-before-implementation compliance) for a future fix iteration
if the campaign continues past this cycle — out of scope for this
task's own mandate, which was to measure the shipped text as-is, not
to patch it further.

### 2026-07-30 — SHARED SDD BATTERY ROUND 3 PRE-REGISTRATION: T2's bounded-wait revision, T1/T5 regression guards (Task 8c)

This is round 3 of the shared SDD battery. Round 1 (this log's first
three "SHARED SDD BATTERY" entries) FAILed T1/T2/T5 on the original
five-treatment arm (n=6, 2 Docker-lost reps). Round 2 ("SHARED SDD
BATTERY ROUND 2," three entries above) re-ran on the arm plus
`c07cf7e`/`3da65fb`: T1 flipped FAIL → PASS (0/51 depth-2 spawns, 8/8
reps), T5's real FAIL resolved to inconclusive-by-zero at depth-2 (T1
ate its population) plus a clean depth-1 backstop PASS, and T2's core
mechanism flipped too (65.1% → 0.0% wait-timeout rate) but the
criterion's "no loss of task completion" clause still FAILed: 3/8 reps
(rep12/15/16) got Gauntlet-Agent `indeterminate` verdicts and 1/51
dispatched children never reported `task_complete`, because a single
long (15+ minute) `wait_agent` call — exactly `3da65fb`'s recommended
behavior — can leave the controller transcript silent for 20-38 minutes
while a review genuinely keeps working underneath, long enough to
exhaust the Gauntlet-Agent QA judge's own testing-time budget before it
observes completion. Root-caused by direct rollout inspection in round
2's anomaly entry; not a Docker crash, not a `wait_agent` timeout (all
3 cases resolved `timed_out:false`), not a coding-agent hang.

**Two fix commits landed on top of the arm since round 2, both on
`codex-efficiency-fixes`:**
- `43ec25f` — "bounded wait stretches with reconciliation": replaces
  `3da65fb`'s "one long wait (fifteen minutes or more)" guidance, in
  both `skills/subagent-driven-development/SKILL.md` §1 and
  `skills/using-superpowers/references/codex-tools.md`, with "wait in
  bounded stretches (five to ten minutes... `timeout_ms` 300000-600000)
  ... after each stretch — wake or timeout — post one status line, run
  `list_agents`, and chase any child that finished without reporting."
  Directly targets round 2's T2 anomaly: keep the long-wait mechanism's
  measured win (0% timeout rate, ~86% fewer calls than round 1's short
  polls) while capping any single silence to ~10 minutes and forcing a
  periodic reconciliation check that would have caught rep15's lost
  child.
- `6faceb2` — "bounded-path approval is a hard stop": a brainstorming
  three-path-router fix (T4, not T1/T2/T5) — makes bounded-path
  approval an explicit STOP-and-wait gate. Unrelated to this battery's
  scenario (`cx-sdd-small` doesn't invoke brainstorming) but included
  because it's the current arm tip; noted for completeness, not graded
  by this task.

**Arm SHA (verified this task, both on host and via mounted-file
content check in each lane container):** `git -C /tmp/sp-arm-fix log
--oneline -1` → `6faceb2` ("fix(brainstorming): bounded-path approval
is a hard stop"), with `43ec25f` immediately beneath it (`git -C
/tmp/sp-arm-fix log --oneline -3` → `6faceb2` → `43ec25f` → `2302bb9`
(Amendment 2 plan doc) — i.e. round 2's arm (`3da65fb` tip) plus
exactly the plan-doc commit and these two fixes, nothing else changed
underneath it). The container mount check (`git log` doesn't resolve
inside the container for a worktree checkout — `.git/worktrees/
sp-arm-fix` lives on the host, outside the bind mount — so content, not
`git log`, is the container-side check) confirmed
`skills/subagent-driven-development/SKILL.md` line 204 reads "When you
are genuinely idle, wait in bounded stretches (five to ten" in both
lane containers after the up-cycle below.

**Docker status (verified this task, before any spend):** the daemon
was down at task start (`docker ps` failed to connect to the socket);
started via `open -a Docker`, polled in-session (foreground loop, no
monitor) until `docker ps` succeeded (~10s). Both lane containers were
then found `Exited (255)` (stale from a prior session). Cycled per
`scripts/evals-container`'s own commands in each lane checkout —
`down` then `--superpowers-root /tmp/sp-arm-fix up` — both lanes came
up clean (`status` → `exists, running` for both container names,
`docker ps -a` shows both `Up`). No `rep17`-`rep24` directories existed
in either lane's `results/` before this task started, and no
`out/*rep17-24*` files existed in the campaign's `out/` dir — a clean
rep-range slot, confirmed before any run.

**Battery config:**
- Arm: `fix` (`/tmp/sp-arm-fix` @ `6faceb2`, carrying `43ec25f` and
  `6faceb2` on top of round 2's `3da65fb` tip)
- Scenario: `cx-sdd-small`
- Reps: 8 total, same lane split convention as rounds 1-2 (roughly
  half/half) — renumbered reps 17-24 (not 9-16 or 1-8), so this
  round's `--out-root` RUNDIRs (`results/cx-eff-cx-sdd-small-fix-
  rep{17..24}`) and scorer output files (`out/e1-cx-sdd-small-fix-
  rep17-24.json` etc., derived by each scorer's own
  `_rep_range_suffix()`/equivalent from the rep number embedded in the
  RUNDIR name) cannot collide with round 1's `rep1-8` or round 2's
  `rep9-16` aggregates, committed or on-disk. `FORCE` is never set on
  any scorer invocation this round; a collision is an anomaly to
  report, not a flag to suppress. Rep17 = smoke (lane A); remaining
  reps split lane A / lane B, `JOBS=2` per lane where used, mirroring
  rounds 1-2's 1+3/4 pattern.
- Scorers: `score_e6.py` (T1), a fresh one-off script reusing
  `score_e7.py`'s tested `census_session()`/`aggregate()` functions
  against the fix-arm RUNDIRs across both lanes (T2 aggregate
  timeout/paired numbers — `score_e7.py` itself still hardcodes
  `arms=("dev","spinout")`, confirmed unchanged since round 2, so it
  still doesn't fit `fix` split across two lane checkouts; writes only
  a new, non-colliding `out/e7-battery-fix-round3.json`, never
  touching round 1/round 2's files or the frozen corpus (a)/(b)
  blobs), `score_e1.py` (T5). **New this round:** a second one-off
  script (scratch, not committed — this task's method for the new
  silent-gap sub-criterion below) computes, per root rollout, every
  paired `wait_agent` call's duration (`function_call_output`
  timestamp minus `function_call` timestamp, matched by `call_id`,
  reusing `rp.iter_records`/the same pairing logic `wait_outcomes()`
  already implements) and reports the max such duration per session
  and across the battery — this is the direct, rollout-timestamp-based
  measurement of "silent gap during idle waiting" the delta brief
  asks for, chosen because it is exactly what round 2's anomaly entry
  already hand-measured for its 3 flagged reps (22-38 minutes) and
  is a strict subset of "any inter-event gap" that isolates the
  specific window `43ec25f` targets (a `wait_agent` call open with no
  resolution yet) rather than conflating it with ordinary tool-call
  latency elsewhere in the transcript. Cross-checked against a
  whole-transcript "max gap between any two consecutive timestamped
  records in the root rollout" pass as a robustness sanity check (if
  the two numbers diverge significantly for a session, that would flag
  silence NOT attributable to a `wait_agent` call, worth its own
  anomaly note).

**Criteria (T2 restated per the delta brief; T1/T5 verbatim from this
log's "Pre-registered criteria" section, unchanged, graded as
regression guards against round 2's PASS / inconclusive-by-zero):**
- **T2 (this round's primary target):** timeout rate < 25% AND no
  completion loss AND no silent gap over 12 minutes (720s) in any
  controller transcript, where "silent gap" is measured as described
  above (max paired `wait_agent` call duration per root session, from
  raw rollout timestamps).
- **T1 (regression guard):** 0 worker-issued depth-2 spawns AND review
  coverage preserved. Round 2 was a clean PASS (0/51); this round
  checks `43ec25f`/`6faceb2` didn't reopen the gap `c07cf7e` closed.
- **T5 (regression guard, inconclusive-by-zero branch already
  established):** every spawn at every depth carries explicit model +
  effort. If T1 holds at 0 depth-2 spawns again, T5 remains
  inconclusive-by-zero at depth-2 (as round 2 recorded) and is graded
  only on the depth-1 backstop (round 2: 51/51).

**Budget estimate:** ~$40 for 8 reps, same figure as rounds 1-2's
pre-registrations. Anchored to round 2's own measured actuals ($24.89
for 8 reps, $3.11/rep average) with headroom for the bounded-stretch
fix's extra per-stretch overhead (a status line plus a `list_agents`
call every 5-10 minutes during idle waits, in place of round 2's single
long wait) — more calls than round 2 but each individually cheap, and
still far fewer than round 1's short-poll baseline (~25 `wait_agent`
calls/rep).

**No run yet — this is the pre-registration.** Docker cycle and arm
verification above were preparation, not the smoke rep. Smoke test,
full battery, scoring, manual inspection, and verdicts (each verdict
stating its round 2 → round 3 delta) follow in later log entries.
