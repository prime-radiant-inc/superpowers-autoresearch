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
