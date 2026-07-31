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

### 2026-07-30 — SHARED SDD BATTERY ROUND 3: smoke PASS, all 8 reps complete, all 8 Gauntlet-Agent PASS — round 2's anomaly does not recur (Task 8c)

**Smoke test (rep17, lane A): PASS.** Gauntlet verdict `status: pass`
($3.97). 8 rollout files (1 root + 7 children:
`task{1,2,3}_{implementer,reviewer}` + `task3_r1_reviewer` (a
`followup_task`-driven re-review, not a duplicate — see below) +
`final_reviewer`). Manual inspection of the raw root rollout JSONL
(direct `rp.extract_spawns`/`iter_records` calls, not a scorer
helper): all 8 `spawn_agent` calls issued by the ROOT session only
(every non-root file has 0 `spawn_agent` calls) — zero worker-issued
depth-2 spawns; all 8 carry explicit `model`+`reasoning_effort`. Every
one of the 9 `wait_agent` calls used `timeout_ms:300000` (the fix's
new 5-minute stretch floor, not round 2's 15-minute-plus long wait) —
**0/9 timed out, and the actual resolution durations ranged 20.8s-
156.9s (max 2.61 minutes)**, far under both the old 15-minute
recommendation and the new 12-minute gap criterion. The root used one
`followup_task` call (to re-dispatch `task3_implementer` after a
review finding) but 0 `list_agents` calls this rep — a real, if minor,
compliance gap against `43ec25f`'s literal "after each stretch... run
`list_agents`" instruction (every stretch here resolved well inside
its own timeout via the wake event, so the controller may not have
felt a stuck-child check was warranted) — noted below as a concern,
not gating, since the fix's outcome-level guarantees (bounded
duration, no completion loss) held regardless. No infra anomaly.
Proceeded to Step 3.

**Step 3 battery launch:** rep17 smoke on lane A, then `EVALS_ROOT=<lane
A> JOBS=2 bash run-quorum.sh fix cx-sdd-small 3 18` (reps 18-20) and
`EVALS_ROOT=<lane B> JOBS=2 bash run-quorum.sh fix cx-sdd-small 4 21`
(reps 21-24), launched concurrently as backgrounded processes, polled
in-session with foreground bounded-wait shell loops (`until <condition
met>; do sleep 20; done`, capped at the tool's own 590s-600s ceiling
per call — when a wait outlasted one call it simply continued as a
new foreground wait, never a dedicated monitor process). **All 8
pre-registered reps completed — zero reps lost to Docker.** `docker ps
-a` before, during (implicitly, via the containers never producing an
`exec` failure across ~15 `scripts/evals-container exec`-driven rep
runs), and after the battery showed both lane containers `Up`
continuously (~50 minutes wall-clock for the full battery, container
uptime confirmed unbroken at the end). Every rep produced a complete
`verdict.json` + `trajectory.json` + `coding-agent-token-usage.json`
(`partial: false` on all 8, confirmed by reading each rep's own
`verdict.json.economics` directly).

**Gauntlet-Agent verdict: 8/8 PASS (100%) — round 2's `indeterminate`/
`investigate` anomaly (3/8 reps) does not recur.** Every rep's
Gauntlet-Agent summary independently confirms the same shape: plan.md
read, per-task implementer/reviewer subagents dispatched, a
final-whole-branch review (with a genuine fix-and-re-review wave in
5/8 reps: rep17, 19, 20, 21, 23, 24 — 6/8 actually, see the per-rep
task-name census in the verdicts entry below), and a clean merge to
main with all tests passing. No crash, no clarification loop, no
premature abandonment, no `indeterminate` in any of the 8 Gauntlet
summaries this round.

**Minor, non-gating recurrence: rep24 (lane B) left a stray
`cx-sdd-small-fix-rep24` directory as a sibling of the real run
directory** (`results/cx-eff-cx-sdd-small-fix-rep24/cx-sdd-small-fix-
rep24/cx-sdd-small-codex-codex_sub-linux-*-3401/coding-agent-workdir/
.worktrees/strutils-plan/strutils`), the same shape round 2's concern
#3 flagged for reps 13/14 (a git-worktree path resolving oddly under
that container instance's bind mounts) — "flagging only in case it
recurs at higher rates in a future battery." It recurred, still at a
low rate (1/8 this round vs 2/8 round 2), still contains no
verdict/rollout data (confirmed via `find` — only a nested nested copy
of the real run's `coding-agent-workdir/.worktrees` tree, no
`verdict.json` of its own), and was excluded from scoring by
construction (the rundir-collection script only includes directories
containing their own `verdict.json`).

**Cost (8 completed reps, from each rep's own `verdict.json`
`economics.total_est_cost_usd`, all `partial: false`, read directly —
not the printed report):** rep17 $3.97, rep18 $3.33, rep19 $4.10,
rep20 $4.07, rep21 $4.64, rep22 $3.89, rep23 $4.71, rep24 $4.74 —
**$33.47 total, all 8 measured directly**, under the ~$40
pre-registered budget and above round 2's $24.89 (consistent with the
pre-registration's expectation of more, individually-cheap wait calls
replacing round 2's fewer, longer ones).

### 2026-07-30 — SHARED SDD BATTERY ROUND 3: T1/T2/T5 verdicts on n=8, round 2 → round 3 deltas (Task 8c)

Scored all 8 reps (17-24) with `score_e6.py` (T1), `score_e1.py` (T5),
and a new one-off script
(`score_e7_fix_battery_round3.py`, scratch — not committed, per the
pre-registration) that both reuses `score_e7.py`'s tested
`census_session()`/`aggregate()` functions for the timeout-rate
numbers (same reason as round 2: `score_e7.py` itself still hardcodes
`arms=("dev","spinout")`, confirmed unchanged since round 2) AND adds
the new silent-gap measurement: for each rep's root rollout, every
paired `wait_agent` call's duration (`function_call_output` timestamp
minus `function_call` timestamp, matched by `call_id`) plus a
whole-transcript max-consecutive-timestamp-gap cross-check. Outputs:
`out/e6-cx-sdd-small-fix-rep17-24.json`, `out/e1-cx-sdd-small-fix-
rep17-24.json`, `out/e7-battery-fix-round3.json` — none collide with
round 1/round 2's `rep1-8`/`rep9-16` files or the frozen corpus
(a)/(b) blobs; `FORCE` was never set.

**Manual inspection (non-circular — raw rollout JSONL via direct
`rollout_parser` calls, not scorer helpers), beyond the brief's 2-run
minimum:**
- **Depth-2 spawn census (T1) — exhaustive, not sampled:** `score_e6`'s
  own full-corpus walk reports `depth-2 spawns by spawner role: {}`
  (empty, i.e. zero) summed across all 8 reps, 0 compactions, 0
  same-task duplicate reviews. Independently re-verified by hand for 2
  reps (rep17 smoke — see above; rep22, chosen as the rep with the
  single largest silent gap, see below) by iterating every non-root
  rollout file's `extract_spawns()` result directly: 0/0 non-root
  spawns in both, matching the aggregate exactly.
- **Review coverage (T1):** re-read every rep's full `task_name`
  sequence from `score_e1`'s raw per-spawn table (not just an
  aggregate count): all 8 reps show exactly
  `task{1,2,3}_{implementer,reviewer}` (one reviewer per task, no
  duplicates) + `final_reviewer`, with 6/8 reps (19, 20, 21, 23, 24,
  plus rep17's `task3_r1_reviewer` re-review) additionally dispatching
  a normal SDD fix-and-re-review wave after `final_reviewer` flagged a
  real issue (naming varies by controller phrasing —
  `final_fixer`/`final_fix`/`final_fix_reviewer`/`final_rereviewer` —
  but always exactly one fixer + one re-reviewer per wave, never a
  duplicate of an already-reviewed task). No task anywhere got more or
  fewer than exactly one review pass before merge.
- **Wait-call classification (T2) — independently re-parsed 2 full
  sessions' raw `wait_agent`/`function_call_output` pairs** (rep17: 9
  calls; rep22: 7 calls — 16 of the corpus's 73 total calls, more than
  double the brief's 2-run minimum) with fresh `json.loads`/`call_id`
  pairing, not `rollout_parser.wait_outcomes()`. Every count,
  `timed_out` value, and per-call duration matches
  `out/e7-battery-fix-round3.json`'s per-session numbers exactly
  (rep17 max 156.9s/2.61min; rep22 max 234.3s/3.91min — the battery's
  overall maximum). All re-parsed calls used `timeout_ms:300000`
  (5 minutes, the bounded stretch's floor) and all resolved
  `timed_out:false` well inside that window, not at the ceiling.
- **Explicit-model claims (T5):** the raw per-rep spawn dumps used for
  the review-coverage check above double as independent T5
  verification — all 67 spawns across all 8 reps carry non-null
  `model` and `reasoning_effort` keys directly in the raw `arguments`
  JSON, matching `score_e1`'s 67/67 (100%) `explicit_model` exactly.
- **Advisory config backstop:** checked lane A's container
  `/root/.codex/config.toml` this round (previous rounds checked a
  rep's own container-relative copy; same file, same result) — no
  `[agents]`/`default_subagent_*` keys. Still unprovisioned in this
  eval environment, still untested by any battery to date.

**Aggregate numbers (8 reps, from the three JSON blobs):**
- T1: **0 worker-issued depth-2 spawns across 8 reps** (0/8 reps
  affected), 0 same-task duplicate-review families — identical shape
  to round 2's clean result, now on a fresh arm SHA.
- T2: **73 wait_agent calls, 73 paired, 0 excluded, 0 timed out — 0.0%
  timeout rate** (paired and all-calls, matching round 2's mechanism-
  level result exactly). `score_e1`'s aggregate shows **67/67
  (100.0%) resolved child rollouts with `task_complete` present** —
  round 2's 1/51 loss does not recur. **New silent-gap metric: max
  paired-wait duration across all 8 reps is 234.3s (3.91 minutes,
  rep22) — every rep's maximum is under 4 minutes, all 8 comfortably
  under the pre-registered 720s (12-minute) threshold** (per-rep
  maxima: 156.9s, 145.6s, 131.9s, 122.1s, 134.9s, 234.3s, 137.5s,
  151.8s). The whole-transcript cross-check gap matches the wait-
  duration gap exactly in every rep (no silence attributable to
  anything other than a `wait_agent` call was found). Gauntlet
  verdict: **8/8 pass (100%)** — round 2's 3/8 `indeterminate` anomaly
  does not recur.
- T5: **67/67 spawns (100.0%) carry explicit model; 0 model_omitted.**
  All 67/67 are root-issued (depth-1) — T1 held at 0 depth-2 spawns
  again this round, so there is still no depth-2 population to grade.
  `fork_turns:"none"` on all 67/67 spawns (isolation unaffected).

**Verdicts against the pre-registered criteria, each with its round 2
→ round 3 delta:**

- **T2 (timeout rate < 25% AND no completion loss AND no silent gap
  over 12 minutes): PASS — full conjunction, first clean PASS across
  all three rounds. Delta: FAIL (completion-loss clause only) → PASS
  (all three clauses).** Timeout-rate clause: 0.0% (unchanged from
  round 2's clean win). Completion-loss clause: 67/67 (100%) children
  resolved with `task_complete`, vs round 2's 50/51 (98.0%) — the one
  lost child (rep15's cut-off `task3_implementer`) does not recur in
  any of this round's 8 reps. Silent-gap clause (new this round): max
  234.3s (3.91min) across all 8 reps, vs round 2's 22-38 minute
  silences in 3/8 reps — commit `43ec25f`'s bounded 5-10 minute
  stretches (observed here consistently issued at the 300000ms floor)
  plus the reconciliation instruction closed the exact gap round 2's
  anomaly identified, without reopening round 1's original short-poll
  timeout pathology (0.0% both rounds). Gauntlet-Agent verdict
  (8/8 pass) independently corroborates: the QA judge's own
  testing-time budget was never at risk this round because no wait
  stretch came close to consuming it.
- **T1 (regression guard): PASS, unchanged. Delta: PASS → PASS.** 0/67
  depth-2 spawns across all 8 reps (round 2: 0/51) — `43ec25f`
  (wait-stretch wording only) and `6faceb2` (brainstorming-only,
  doesn't touch SDD role prompts) did not reopen the gap `c07cf7e`
  closed in round 2. Review coverage preserved cleanly across all 8
  reps, including the 6/8 reps with a genuine fix-and-re-review wave —
  no duplicate reviews, no task skipped.
- **T5 (regression guard, inconclusive-by-zero branch): unchanged.
  Delta: inconclusive-by-zero at depth-2 → inconclusive-by-zero at
  depth-2 (same branch, re-confirmed).** T1 held at 0 depth-2 spawns
  again, so there is still no depth-2 population to grade for
  model/effort omission. Depth-1 backstop: 67/67 (100%) explicit,
  matching round 2's 51/51 (100%) — no regression at the depth that
  was already working. The advisory config backstop remains
  unprovisioned in this eval environment, same as rounds 1-2 — still
  untested by any battery to date.

**Ledger row:** 2026-07-30 | Shared SDD battery ROUND 3 T2 bounded-wait
revision, T1/T5 regression guards (fix arm @ `6faceb2`, cx-sdd-small,
n=8 of 8 pre-registered — no Docker loss, no Gauntlet-Agent
indeterminate) | $33.47 (8/8 measured, `partial: false` on all) | T1
PASS, T2 PASS (all three clauses — first clean PASS across all three
rounds), T5 inconclusive-by-zero at depth-2 / PASS on backstop.

**Status: all three treatments resolve cleanly this round.** T2 is
the headline: commit `43ec25f`'s bounded 5-10 minute wait stretches
with `list_agents`/status-line reconciliation closed round 2's
Gauntlet-Agent-testing-budget anomaly (3/8 indeterminate → 0/8) and
its 1-child completion loss (1/51 → 0/67) without reopening round 1's
original timeout pathology (0.0% both rounds) — the new silent-gap
sub-criterion this round's pre-registration added specifically to
make round 2's finding measurable comes in at a maximum of 3.91
minutes across all 8 reps, nowhere near the 12-minute bar. T1 and T5
hold their round 2 results unchanged, confirming `43ec25f` (SDD/codex
wait-wording only) and `6faceb2` (brainstorming-only) did not disturb
the no-subagents contract or spawn-hygiene mechanisms those two
treatments measure. One minor observation carried forward as a
concern, not a gate: the smoke rep's controller issued 0 `list_agents`
calls despite the fix's literal "after each stretch... run
`list_agents`" instruction — every stretch resolved via the wake event
well inside its own timeout, so the reconciliation step went unused in
practice this round, not because it was skipped under pressure. Net:
3 of 3 treatments are clean wins this round, with the T2 fix's
mechanism now validated end-to-end (timeout rate, completion, AND
observability) across three full battery rounds.

### 2026-07-30 — CORRECTION to the round 3 battery entries above (task-reviewer audit, Task 8c)

This is a correction entry, per the log's append-only rule — the two
entries above are left as originally written; this entry states what
in them was wrong and what the true numbers are.

**1. IMPORTANT — factual overclaim on `timeout_ms` uniformity.** Both
entries above, and `task-8c-report.md`, state or imply that all 73
`wait_agent` calls this round used `timeout_ms:300000` ("observed here
consistently issued at the 300000ms floor" in the T2 verdict
paragraph; "All 73 re-observed `wait_agent` calls used
`timeout_ms:300000`" in the report). **This is false.** The claim was
only ever independently verified for the 2 manually-inspected reps
(rep17: 9/9 @300000; rep22: 7/7 @300000 — both of those two
narrower, correctly-scoped statements, at log lines "Every one of the
9 `wait_agent` calls used `timeout_ms:300000`" (smoke entry) and "All
re-parsed calls used `timeout_ms:300000`" (manual-inspection bullet,
scoped explicitly to "rep17: 9 calls; rep22: 7 calls"), remain
accurate as written) and was then wrongly generalized to the full
8-rep/73-call corpus without re-checking the other 6 reps' committed
data. Re-derived directly from the already-committed
`out/e7-battery-fix-round3.json`'s `silent_gap_analysis[].
wait_durations[].timeout_ms` field (python, `collections.Counter`,
independent of any prior script run this task):

```
overall: {300000: 55, 600000: 7, 360000: 10, 120000: 1}  (73 total)
rep17 {300000: 9}
rep18 {600000: 7}
rep19 {360000: 10}
rep20 {300000: 9}
rep21 {300000: 10}
rep22 {300000: 7}
rep23 {300000: 9, 120000: 1}
rep24 {300000: 11}
```

So: **55/73 (75.3%) at 300000ms, rep18 used 600000ms for all 7 of its
calls, rep19 used 360000ms for all 10 of its calls, and rep23 issued 9
calls at 300000ms plus 1 at 120000ms — that single 120000ms call is
BELOW `43ec25f`'s stated 300000-600000ms (5-10 minute) range, an
undisclosed compliance deviation the rep17/rep22 spot-check could not
have caught** (neither of the 2 manually-inspected reps happens to be
18, 19, or 23). This is a real, previously unreported spread in how
literally different controller sessions followed the bounded-stretch
instruction's specific numeric range — three of eight reps didn't use
the 300000ms value at all (rep18, rep19), and one (rep23) went under
the floor for a single call. **The T2 verdict itself is unaffected:**
the pre-registered silent-gap criterion is about measured wait
*duration* (actual `function_call_output` minus `function_call`
timestamps), not requested `timeout_ms`, and every one of those
duration numbers in both entries above was already computed and
reported correctly from the same file — rep23's 120000ms call actually
resolved in 10.5s, and rep18/rep19's longer requested ceilings never
caused their actual max durations (145.6s and 131.9s respectively) to
exceed any other rep's. The defect is confined to the "consistently at
the 300000ms floor" / "all 73 ... used timeout_ms:300000" narrative
claims, not to any pass/fail determination or the underlying
gap/timeout/completion numbers.

**2. MINOR — smoke-test rollout-file/child count.** The smoke-test
entry above says "8 rollout files (1 root + 7 children" and then goes
on to name 8 children (`task{1,2,3}_{implementer,reviewer}` +
`task3_r1_reviewer` + `final_reviewer` = 8). The correct count,
confirmed by re-running the original `find .../home/.codex/sessions
-name '*.jsonl'` listing for rep17, is **9 rollout files total: 1 root
+ 8 children.** "8 spawn_agent calls" and "all 8 carry explicit
model+reasoning_effort" elsewhere in the same paragraph were already
correct (8 children = 8 spawns); only the file-count arithmetic in the
opening sentence was wrong.

**3. MINOR — provenance of the 12-minute silent-gap threshold.** The
pre-registration entry above attributes the "no silent gap over 12
minutes" sub-criterion to "the delta brief," which is not a
file-based, independently auditable artifact in this repo or the SDD
task directory — it does not correspond to a committed document this
log or a future reader could go re-open. **Actual provenance: the
720-second (12-minute) figure was relayed verbatim in the
coordinator's dispatch message that assigned Task 8c** (the same
message that specified rep17-24, scorers e6/e7/e1, and the T1/T5
regression-guard framing), not derived from any file this task read or
computed. Recorded here so a future reader auditing this criterion's
origin knows to ask the dispatching coordinator/task history rather
than search the repo for a "delta brief" document.

No numbers in the aggregate tables, the per-treatment verdicts, or the
ledger row above require revision — this correction is confined to
the three items listed.

### 2026-07-30 — T4 LAYER 2 PRE-REGISTRATION ROUND 2: Codex ceremony battery — bounded-path approval hard stop (Task 9b)

Round 1 (commits `d64cc78`/`cd59cdc` above) found bounded's doc/plan
ritual cleanly fixed (0/3 docs, PASS) but its approval-gate compliance
only 1/3 under a strict pre-implementation reading — 2/3 reps
implemented before any approval turn landed, receiving the scripted
confirmation phrase only as a post-hoc rubber stamp afterward. Commit
`6faceb2` ("fix(brainstorming): bounded-path approval is a hard stop")
is the fix under test this round: it rewrites the bounded path's step
4 from "Get approval — explicit, before any implementation" to an
explicit STOP ("Implementation starts only after your human partner
says yes to that design — a bounded task's approval is as hard a gate
as an architectural one"), adds a Red Flags row ("It's bounded and the
design is obvious — I'll start while they read it" / "The gate is the
approval, not the design's length. Present, then stop until you hear
yes."), and rewords the numbered-steps list's step 4 accordingly.
Commits `43ec25f` (bounded wait stretches with reconciliation) and
`433184c` (prefer non-blocking child-result delivery over any wait)
also landed on top since round 1 but target SDD/codex wait discipline,
not the ceremony router text directly — this round's arch class is the
regression guard confirming those two didn't disturb the two-doc-flow
finding.

**Arm SHA (verified this task, refreshed since round 1):** `git -C
/tmp/sp-arm-fix log --oneline -1` → `433184c` — carries `6faceb2`
(bounded-approval hard stop), `43ec25f` (bounded wait stretches), and
`433184c` (non-blocking wait preference) on top of round 1's graded
tip `3da65fb`.

**Battery config:**
- Arm: `fix` (`/tmp/sp-arm-fix` @ `433184c`)
- Scenarios: `cx-ceremony-bounded` (3 reps), `cx-ceremony-arch` (3
  reps), `cx-ceremony-spike` (1 smoke rep only) — 7 runs total, down
  from round 1's 9. Spike's own router text is untouched since round 1
  (the fix commits touch the bounded path and SDD/codex wait text, not
  the spike path); the shared Red Flags table addition is the only
  edit common to all three paths, so 1 smoke rep is enough to guard
  against a regression there without re-measuring spike's already-PASS
  round-1 finding at full n=3.
- Rep numbering: round 1 already used rep1-3 for
  `cx-ceremony-{bounded,spike}-fix` (lane A) and `cx-ceremony-arch-fix`
  (lane B) — this round uses rep4-6 for bounded and arch, rep4 (single)
  for spike, so round 2's `results/` directories never collide with
  round 1's already-scored data.
- Lane split: lane A (`superpowers/evals`) runs the spike smoke rep
  (rep4) first, then bounded reps 4-6. Lane B (`evals-lane-b`) runs
  arch reps 4-6, concurrently with lane A's queue — unchanged from
  round 1's split.
- Scorer: `score_e4.py`, invoked directly against the 7 new RUNDIRs
  once the battery completes (no arm-hardcoding workaround needed,
  confirmed again by reading `main()`'s `RUNDIR...` signature, same as
  round 1).
- **Harness-budget accommodation, NOT a treatment change:**
  `cx-ceremony-arch/story.md`'s `quorum_max_time` is bumped from **30m
  to 45m** before this round's reps run. This responds to round 1's
  rep3 anomaly (a genuine `subagent-driven-development` SDD flow hit
  the old 30-minute budget and got an `investigate`/`indeterminate`
  Gauntlet-Agent verdict despite complete, non-infra rollout data) —
  the same character of scenario-budget side effect Task 8b documented
  and handled by NOT stopping the battery. This is a scenario-harness
  change, edited on the HOST campaign scenarios directory
  (`campaigns/codex-efficiency/scenarios/cx-ceremony-arch/story.md`,
  synced into each container by `run-quorum.sh` before every run), not
  a change to any router/skill text under test. **Old value: 30m. New
  value: 45m.**

**Criteria (round 2, per this task's dispatch — Amendment 2, Task 9b
section):**
- **Bounded:** 0 ceremony docs (unchanged from round 1's "0 committed
  spec/plan docs") AND strict pre-implementation approval 3/3 —
  **definition, stated explicitly per the dispatch's instruction:** the
  approval turn (a Gauntlet-Agent message conveying approval, e.g.
  "looks good, that's what I wanted") must precede the first
  implementation patch in the raw rollout timeline. This is round 1's
  own hand-verified method (independent `json.loads` + `patch_apply_end`
  timestamp sort, cross-checked against the approval-message
  timestamp), not a re-derivation — round 1's rep3 (design presented
  21:45:34Z, approval 21:45:58Z, "Approved..." 21:46:06Z, first patch
  21:46:29Z) is the worked example of what "precedes" means here. Round
  1 scored 1/3 on this reading (rep1/rep2 implemented first, approval
  arrived only afterward).
- **Arch:** two-doc flow 3/3 (unchanged from round 1) AND gauntlet task
  completion 3/3 (round 1 scored 2/3 — rep3's scenario-timeout anomaly,
  the exact case the `quorum_max_time` bump above targets).
- **Spike:** smoke rep healthy — no docs, minimal ceremony (a
  single-rep health check, not a 3-rep statistical claim; round 1
  already PASSed 3/3 on this unchanged router text).

**Budget estimate:** ~$30 (per the dispatch). Anchor: round 1's 9-rep
battery cost $15.23 total (bounded $2.30/3 reps, spike $1.72/3 reps,
arch $11.21/3 reps, the last driven up by rep3's timeout). This
round's 7 reps (3 bounded + 1 spike + 3 arch) at round 1's per-class
rates would be roughly bounded $2.30 + spike ~$0.6 (1 rep) + arch ~$11
(3 reps, possibly higher given the 45m budget lets a slow rep run
longer before cutoff rather than cheaper) ≈ $14-16. Budgeting ~$30 for
headroom against that arch uncertainty.

**No run yet — this is the pre-registration.** Smoke test (the spike
rep doubles as the smoke, per this round's instructions), full
battery, scoring, and hand-recount (one rep per class from raw
patch/approval timestamps, non-circular) follow in later log entries.

### 2026-07-30 — T4 LAYER 2 RESULT ROUND 2: bounded-path approval hard stop closes round 1's gap 3/3; arch two-doc flow and completion both hold 3/3 under the bumped budget, margin razor-thin on one rep; spike smoke healthy (Task 9b)

**Smoke test (spike rep4, lane A): PASS, scenario health confirmed.**
`gauntlet.status: pass`, `economics.partial: false`. Scenario-identity
marker present ("port is already in use" appears twice in the raw
rollout — the correct spike stimulus, not a stale/wrong scenario sync).
Bootstrap loaded and reachable (5 `SKILL.md` mentions, 7 `superpowers`
mentions, 4 `using-superpowers` mentions in the raw rollout — the skill
system is live, not a silent no-op). Zero `patch_apply_end` events —
the same "genuine ephemeral investigation, no patch" shape 2/3 of round
1's spike reps showed; unsurprising since spike's own router text is
unchanged since round 1 and this is a single-rep sample, not a new
3-rep claim. Proceeded to the full battery.

**Battery launch:** lane A (`superpowers/evals`) ran `cx-ceremony-bounded`
reps 4-6 (`JOBS=3`, one concurrent batch, ~90s total); lane B
(`evals-lane-b`) ran `cx-ceremony-arch` reps 4-6 (`JOBS=3`, one
concurrent batch, ~44 minutes total — up against the round's bumped
45-minute `quorum_max_time`) concurrently with lane A. All launched as
disowned background processes, polled via repeated foreground
`until grep -q "^EXIT:"` loops against a written sentinel (the harness
auto-backgrounded a few individual poll calls once they exceeded its own
600s per-call ceiling on the long arch wait, surfacing as ordinary
task-completion notifications rather than a Monitor tool invocation —
no `Monitor` tool call was made this task). `docker ps -a` checked
repeatedly through the run: both lane containers stayed `Up` for the
entire ~50-minute battery, no `Exited` transition — no Docker loss.

**All 7 pre-registered reps produced usable, complete rollout data**,
`economics.partial: false` on all 7, `gauntlet.status: pass` on all
7/7 — **no anomaly this round**, unlike round 1's arch rep3
`investigate`. `run-quorum.sh` exited 0 for both lanes.

**Scoring:** `score_e4.py`, invoked directly against all 7 new RUNDIRs
in one call (rep4-6 for bounded/arch, rep4 for spike — fresh rep
numbers, no collision with round 1's rep1-3 dirs, which remain
untouched on disk). Output: `out/e4-mixed-cx-ceremony-arch-fix-
cx-ceremony-bounded-fix-cx-ceremony-spike-fix-rep4-6.json`.

**Results (scorer's own per-run table):**

```
class     rep  no-patch  user turns  docs written  tool calls  wall-clock(s)
bounded    4      no          2           0             5          72
bounded    5      no          2           0             5         104
bounded    6      no          2           0             5          81
spike      4     YES         N/A          0            N/A         N/A
arch       4      no          5           2            14         515
arch       5      no          8           2            11         489
arch       6      no          7           2            21         701
```

Per-class means: bounded 5.0 tool calls, 2.0 user turns, 0.0 docs
(n=3); arch 15.3 tool calls, 6.7 user turns, 2.0 docs (n=3); spike N/A
(n=1, no-patch). Discrimination gate (spike vs. arch mean
tool-calls-before-T): **inconclusive-by-zero this round** (spike's
single smoke rep has no measurable patch) — a sampling-size artifact of
running spike at n=1 this round, not a regression from round 1's thin
n=1-with-a-patch data point; spike's router text and behavior are
unchanged.

**Manual hand-verification (non-circular — independent `json.loads` +
own event-stream scan via a one-off script reusing round 1's
`patch_apply_end`-timestamp-sort method, not `rollout_parser`), all 3
bounded reps (the headline class) plus 2 of 3 arch reps (root-rollout
identification required first, since arch rep4 spawned an 11-child SDD
subtree same as round 1's rep3):**

- **bounded rep4:** raw event stream — design presented in chat at
  `00:42:20.773Z` ("This is a bounded change. Proposed design: ...
  Gate all explicit per-request stderr log lines behind the handler's
  quiet setting..."), approval `"looks good, that's what I wanted"` at
  `00:42:49.510Z`, agent's `"Approved. I'll now follow the TDD
  cycle..."` at `00:42:54.626Z`, first patch (`tests/test_server.py`)
  at `00:43:04.821Z`. **Approval precedes the first patch by ~15
  seconds — the gate held.** Independently recomputed: T =
  `00:43:04.821Z` (already non-doc), user_turns_before_T=2,
  tool_calls_before_T=5, wall_clock=session_start(`00:41:52.965Z`) to T
  = 71.856s ≈ 72s. **Matches the scorer's row exactly (2 / 0 docs / 5
  / 72).**
- **bounded rep5:** design at `00:41:57.820Z`, approval at
  `00:42:33.817Z`, `"Approved. I'm now applying the test-driven
  workflow..."` at `00:42:44.319Z`, first patch at `00:43:05.664Z`.
  **Approval precedes first patch by ~32 seconds.** Recomputed wall
  clock ≈ 104s — **matches the scorer's row (2 / 0 docs / 5 / 104).**
- **bounded rep6:** design at `00:42:18.407Z`, approval at
  `00:42:47.576Z`, `"Approved—moving into TDD now..."` at
  `00:42:51.501Z`, first patch at `00:43:09.017Z`. **Approval precedes
  first patch by ~21 seconds.** Recomputed wall clock ≈ 81s — **matches
  the scorer's row (2 / 0 docs / 5 / 81).** All 3 bounded reps this
  round show the identical shape round 1's rep3 alone showed: design
  in chat → explicit approval-shaped message → agent's own "Approved"
  acknowledgment → only then a patch. Round 1's rep1/rep2 pattern
  (implement first, approval as a post-hoc rubber stamp after code
  already exists) **does not recur anywhere in this round's 3 reps.**
- **arch rep4 (root rollout identified via `session_meta.cwd` matching
  the run's top-level `coding-agent-workdir`, distinguishing it from
  the 11 spawned children sharing container filesystem paths — this
  rep chose the `subagent-driven-development` path, same choice round
  1's rep3 made):** raw event stream — spec doc
  (`docs/superpowers/specs/2026-07-31-reusable-notes-library-design.md`)
  at `00:44:57.224Z`, plan doc
  (`docs/superpowers/plans/2026-07-31-reusable-notes-library.md`,
  written twice — `00:47:42.517Z` and `00:47:53.220Z`, a revision) at
  `00:47:42.517Z`, first non-doc patch (`.gitignore`, worktree setup —
  same edge case round 1 already flagged) at `00:49:52.959Z`. T =
  `00:49:52.959Z`. Independently recomputed: user_turns_before_T=5 (5
  root `user_message` events before T: the initial ask, an API-choice
  answer, two "looks good, keep going" approvals, and the
  subagent-driven-vs-solo choice), tool_calls_before_T=14,
  wall_clock=session_start(`00:41:18.272Z`) to T = 514.687s ≈ 515s.
  **Matches the scorer's row exactly (5 / 2 docs / 14 / 515), and the 2
  distinct doc paths are exactly one `specs/*.md` and one `plans/*.md`
  — the two-document ritual, unchanged shape from round 1.**
- **arch rep5 (single-session, no subagent spawns — matching round 1's
  rep1/rep2 pattern):** spec doc
  (`docs/superpowers/specs/2026-07-31-library-cli-split-design.md`) at
  `00:45:06.670Z`, plan doc
  (`docs/superpowers/plans/2026-07-31-library-cli-split.md`) at
  `00:47:30.456Z`, first non-doc patch (`.gitignore`) at
  `00:49:30.186Z`. T = `00:49:30.186Z`. Recomputed wall_clock =
  session_start(`00:41:21.181Z`) to T = 489.005s ≈ 489s. **Matches the
  scorer's row exactly (489s), two-doc flow confirmed again.**

**Arch budget margin — flagged as a concern, not a failure.** Arch
rep4's own `verdict.json.economics` reports Gauntlet duration 43m55s
(2635s) and Coding duration 42m08s (2528s) against this round's bumped
45-minute (2700s) `quorum_max_time` — **only ~65 seconds (2.4%) of
headroom before this exact rep would have repeated round 1's rep3
timeout.** This rep independently chose the same
`subagent-driven-development` path round 1's rep3 chose (11 spawned
children, a full spec→plan→implement→whole-branch-review→fix-wave→
re-review cycle), and it completed cleanly and scored `pass` this
round — the bump from 30m to 45m was necessary and, this one time,
barely sufficient. This is a real signal that the margin is thin, not
generous: a future battery, or a slightly slower model/network day,
could still reproduce round 1's timeout at the new ceiling. Recorded
as a concern for any future round of this scenario, not a gating
failure of this round's own criteria (completion 3/3 is unambiguous:
`gauntlet.status: pass`, `economics.partial: false` on all 3 arch
reps).

**Verdicts against the round-2 pre-registered criteria (verbatim from
the pre-registration entry above):**

- **Bounded — "0 ceremony docs": PASS, 3/3, unchanged from round 1.**
  Every bounded rep's `doc_paths_written_before_first_non_doc_patch` is
  empty — confirmed by the scorer and independently by the raw event
  scan of all 3 reps.
- **Bounded — "strict pre-implementation approval 3/3": PASS, 3/3.**
  **Round 1 → round 2 delta: FAIL (1/3) → PASS (3/3).** Every rep's
  approval-shaped message ("looks good, that's what I wanted") and the
  agent's own explicit "Approved..." acknowledgment both land BEFORE
  the first patch in the raw timeline, by margins of 15-32 seconds —
  the same shape round 1's lone compliant rep (rep3) showed, now
  showing in all 3 reps. Commit `6faceb2`'s explicit STOP instruction
  ("Implementation starts only after your human partner says yes...
  Present, then stop until you hear yes") closes the exact gap round
  1's headline finding identified.
- **Arch — "two-doc flow 3/3": PASS, 3/3, unchanged from round 1.**
  Every arch rep writes exactly one `docs/superpowers/specs/*.md` and
  one `docs/superpowers/plans/*.md` before its first non-doc patch —
  confirmed by the scorer and independently hand-verified for 2 of 3
  reps (rep4's SDD-subagent path and rep5's single-session path), both
  matching. `43ec25f`/`433184c` (SDD/codex wait-discipline commits
  layered on top since round 1) did not disturb this shape.
- **Arch — "gauntlet task completion 3/3": PASS, 3/3.** **Round 1 →
  round 2 delta: FAIL (2/3, rep3's scenario-timeout `investigate`) →
  PASS (3/3, all `gauntlet.status: pass`).** The pre-registered
  `quorum_max_time` bump (30m → 45m, a disclosed harness-budget
  accommodation, not a treatment change) closed the exact gap round 1's
  anomaly identified — but see the razor-thin-margin flag above: this
  is a real fix at this round's actual measured durations, not proof
  the new ceiling has comfortable headroom going forward.
- **Spike — "smoke rep healthy": PASS.** Single rep, correct scenario
  marker, bootstrap loaded, clean no-patch investigation matching round
  1's majority shape, `gauntlet.status: pass`. Not re-measured at n=3
  per this round's reduced scope (spike's own router text is untouched
  since round 1).

**Cost (7 reps, from each rep's own
`verdict.json.economics.total_est_cost_usd`, all `partial: false`):**
bounded $0.68 + $0.77 + $0.80 = $2.26; spike $0.60; arch $8.21 + $2.96
+ $2.84 = $14.01 (rep4's $8.21 is the highest single rep in the
battery — consistent with its 11-child SDD subtree running close to
the full bumped budget). **Total: $16.87**, under the ~$30
pre-registered budget.

**Ledger row:** 2026-07-30 | T4 layer-2 Codex ceremony battery ROUND 2
(fix arm @ `433184c`, `cx-ceremony-{bounded,arch}` n=3 each +
`cx-ceremony-spike` n=1 smoke, 7 of 7 pre-registered — no Docker loss,
no anomaly) | $16.87 (7/7 measured, `partial: false` on all) | bounded:
0 docs PASS 3/3, strict approval-gate PASS 3/3 (round1→round2: FAIL
1/3 → PASS 3/3) | arch: two-doc flow PASS 3/3 (unchanged), completion
PASS 3/3 (round1→round2: FAIL 2/3 → PASS 3/3, via the disclosed
`quorum_max_time` 30m→45m bump; margin on the one SDD-subagent rep was
only ~65s/2.4%) | spike: smoke PASS (n=1, unchanged router text).

**Status: DONE, clean wins on both treatments this round, with one
honestly-flagged margin concern.** The two gaps round 1 left open are
both closed: bounded's approval gate, round 1's headline finding (1/3
strict compliance, 2/3 reps implementing before approval), is now 3/3
— commit `6faceb2`'s explicit hard-stop wording fixed exactly the
failure mode round 1 hand-verified. Arch's scenario-timeout anomaly
(round 1's rep3, 2/3 completion) is also now 3/3 — the pre-registered,
disclosed `quorum_max_time` bump (a harness accommodation, not a
router-text change) fixed it, though this round's own data shows the
fix has very little margin (one rep finished with roughly 65 seconds
to spare out of a 45-minute budget while running the same
subagent-driven SDD path that timed out at 30 minutes in round 1).
Bounded's doc/plan ritual (round 1's clean PASS) and arch's two-doc
flow (round 1's clean PASS) both hold with no regression under the
additional wait-discipline commits (`43ec25f`, `433184c`) layered on
top. Recommend treating the arch budget margin as a live risk, not a
closed question, if any future round reuses this scenario without
re-checking actual rep durations against whatever ceiling is in
force.

### 2026-07-30 — T4 LAYER 3 PRE-REGISTRATION: global regression battery on Claude Code + Gemini (Task 11)

Layer 2 (immediately above) validated the fix arm's ceremony behavior on
Codex specifically. Layer 3 asks whether the SAME router text (Task 5's
commit `5ea8821`, unchanged since layer 1/2) produces the SAME ceremony
shape on two other harnesses -- Claude Code and Gemini -- and whether the
fix arm regresses gauntlet completion relative to `dev` on either. This is
cross-harness regression evidence, not a new treatment: the router text
under test is identical to layer 2's; only the Coding-Agent driving it
changes.

**Arm SHAs (verified this task, per this task's explicit instruction --
NOT refreshed):**
- `dev`: `git -C /tmp/sp-arm-dev log --oneline -1` -> `bb2a34b` (matches
  `origin/dev` tip as supplied).
- `fix`: `git -C /tmp/sp-arm-fix log --oneline -1` -> `433184c` (matches
  the SHA already graded by layer 2 round 2, immediately above -- this
  battery adds no new commits on top).

**Scenario porting (Step 1, committed with this entry):** copied
`scenarios/cx-ceremony-{spike,bounded,arch}/{story.md,setup.sh,checks.sh}`
to new `scenarios/cc-ceremony-{spike,bounded,arch}/` directories (the
`cx-` scenarios are left untouched -- still codex-only, still used by
other batteries in this campaign). Changes made during the port, all
disclosed:
- `story.md`: `id`/`title`/`tags` updated to the `cc-` name and a
  "cross-harness" tag; task prose, Acceptance Criteria, and (for arch)
  the round-2-bumped `quorum_max_time: 45m` carried over VERBATIM
  otherwise -- the arch budget bump is kept for the cc- variants too, per
  this task's brief, and is disclosed here rather than silently inherited.
- `setup.sh`: dropped `symlink_superpowers` from the helper chain (now
  just `setup-helpers run init_repo_from_fixtures`). Confirmed
  codex-only by grepping every scenario that calls this helper in the
  evals scenario library: every one of them (`cx-ceremony-*`,
  `cx-compaction`, `cx-branch-review`, `cx-scope-review`,
  `cx-sdd-small*`, `codex-tool-mapping-comprehension`,
  `codex-subagent-wait-mapping`) is `# coding-agents: codex`-gated; no
  cross-harness scenario in the library (e.g. the
  `coding-agents: claude,codex,gemini,kimi` family) calls it. Reading
  `symlinkSuperpowers` (`src/setup-helpers/worktree.ts`) confirms why: it
  symlinks `<workdir>/.agents/skills/superpowers` -> `<superpowersRoot>/
  skills`, which is specifically how Codex's own skill-loading convention
  (grep the workdir's `.agents/skills/`) finds the plugin -- Claude and
  Gemini are provisioned separately, at the agent-adapter level (isolated
  `$HOME/.claude` / `$HOME/.gemini` seeding), not through this workdir
  symlink. Confirmed via a THIRD signal beyond "codex-only story tag" and
  "handler reads codex-shaped path": `link_gemini_extension` is Gemini's
  own analogous helper and no scenario in the library calls it either --
  every cross-harness scenario relies on quorum's automatic per-agent
  provisioning and calls neither helper.
- `checks.sh`: `# coding-agents: codex` -> `# coding-agents: claude,gemini`
  (Gemini needs `GEMINI_API_KEY`, present in both lanes' `.env.container`
  -- confirmed by name only, `grep -oE '^[A-Z_]+'`, value never printed).
  `post()`'s codex-specific `file-exists
  "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"` check
  (meaningless for claude/gemini, which write session logs to different
  paths entirely -- `.claude/projects/**/*.jsonl` /
  `.gemini/tmp/**/chats/**/*.json*` per `coding-agents/{claude,gemini}
  .yaml`) is replaced with `check-transcript investigated`: a
  cross-harness transcript verb (`src/check/verbs.ts` `verbInvestigated`)
  that passes on a native `Read`/`Grep` call OR a shell `grep`/`rg` via
  `Bash`. Confirmed cross-harness-safe by reading
  `src/normalize/gemini.ts`'s `GEMINI_TOOL_MAP`: `read_file` -> `Read`,
  `grep_search` -> `Grep`, so Gemini's native investigation tools
  normalize onto the same verb Claude's native `Read`/`Grep` do. This is
  deliberately NOT a doc-count or writing-plans assertion -- per this
  task's brief ("post-checks must never assert the measured doc
  behavior"), the post-check corroborates only that the agent visibly
  engaged with the existing code before changing it (the same fact each
  story's own Acceptance Criteria already require in prose: "visibly
  engaged with the existing code's structure," "visibly located the
  service's existing... code," "visibly investigated"), leaving the
  ceremony census itself entirely to the scorer, ungated by `checks.sh`
  and therefore incapable of biasing pass/fail toward either arm's
  ceremony behavior.
- `fixtures/cc-ceremony-{spike,bounded,arch}` symlinks added (-> `ceremony`,
  identical to the pre-existing `fixtures/ceremony-{spike,bounded,arch} ->
  ceremony` symlinks the `cx-` scenarios use) -- required because
  `run-quorum.sh`'s fixture-resolution line strips only a literal `cx-`
  prefix (`${SCEN#cx-}`); for a `cc-` scenario name that strip is a no-op,
  so the symlink is named to match the UNSTRIPPED scenario name instead of
  changing that line's stripping behavior (documented inline in
  `run-quorum.sh` at the point of use).
- Validated with `bun run quorum check cc-ceremony-spike cc-ceremony-bounded
  cc-ceremony-arch` in BOTH lanes after syncing the new scenario dirs in
  (the same rsync `run-quorum.sh` performs before every run) -- `ok` for
  all three scenarios plus `ok credentials` in both lanes. Also ran the
  full unscoped `bun run quorum check` in lane A (every other scenario in
  the library) to confirm nothing else regressed -- all `ok`.

**`run-quorum.sh` change (Step 1, committed with this entry, disclosed
per the brief's explicit instruction):** the script hardcoded
`--coding-agent codex` with no way to select another harness. Added two
new env vars, both backward-compatible (unset = old behavior exactly):
`CODING_AGENT` (default `codex`, passed straight through as
`--coding-agent`) and `CREDENTIAL` (unset by default; when set, adds
`--credential <name>`). This is the "extend the script minimally" option
from the brief's Step 1, not the `bun run quorum run` direct-invocation
alternative -- chosen because it preserves the script's existing
arm-selection/container-reup/rsync/exclude machinery, which this battery
still needs unchanged.

**Credential note (why `CREDENTIAL=opus` for Claude runs):**
`coding-agents/claude.yaml`'s `default_credential` is `opus_bedrock`
(`api_key_env: AWS_BEARER_TOKEN_BEDROCK`, per `credentials.yaml`).
Checked both lanes' `.env.container` (`grep -oE '^[A-Z_]+'`, names only):
neither defines `AWS_BEARER_TOKEN_BEDROCK` -- only `ANTHROPIC_API_KEY`,
`GEMINI_API_KEY`, `KIMI_MODEL_API_KEY`. The `opus` credential
(`api: anthropic`, `api_key_env: ANTHROPIC_API_KEY`, same
`claude-opus-4-8` model) is provisioned and harness-eligible
(`harnesses: [claude]`). All Claude cells in this battery therefore run
with `CREDENTIAL=opus` (`--credential opus`), disclosed here rather than
silently relying on a default that would fail auth. Gemini cells use
`gemini_default` unmodified (`GEMINI_API_KEY`, present in both lanes).

**Battery matrix:** `{dev, fix}` arms x `{claude, gemini}` harnesses x
`{cc-ceremony-spike, cc-ceremony-bounded, cc-ceremony-arch}` x 3 reps =
**36 runs**, 12 cells of 3 reps each. Lane split: lane A
(`superpowers/evals`, default `EVALS_ROOT`) runs all 6 Claude cells (18
runs: dev x 3 scenarios + fix x 3 scenarios); lane B (`evals-lane-b`)
runs all 6 Gemini cells (18 runs), concurrently with lane A. This is an
operational choice, not a scoring dependency -- `verdict.json`'s own
`coding_agent` field is what `score_t4_regression_report.py` (this
task's new aggregator, see below) actually keys cells on, so a lane/agent
mismatch would be caught, not silently misattributed; the split simply
avoids two different harnesses fighting over one lane's container at
once. Within each lane, cells run scenario-by-scenario grouped by arm
(all of one arm's 3 scenarios before switching arms) to minimize
container re-up churn -- `run-quorum.sh` always re-ups on every
invocation regardless of whether the arm actually changed.

**Scorer:** `score_t4_regression.py` (Task 10, library-only --
`score_trajectory()`/`score_file()`, no CLI) plus a new committed
aggregator this task adds, `score_t4_regression_report.py`: walks a list
of `--out-root` RUNDIRs, resolves each rep's single run subdirectory,
reads `verdict.json` (`coding_agent`, `gauntlet.status`, `final`,
`economics.total_est_cost_usd`) and `trajectory.json` (via
`score_t4_regression.score_file()`), groups into `(arm, coding_agent,
scenario_class)` cells, and prints/writes the per-run and per-cell
tables. Covered by `test_score_t4_regression_report.py` (16 synthetic-
fixture tests, no real quorum output) -- both this new test file and the
pre-existing `test_score_t4_regression.py` (17 tests, Task 10) pass.
Output: `out/t4-layer3-<arms>-<agents>-rep<range>.json`; `FORCE` never
set on the real battery's invocation (a collision is an anomaly, not a
flag to suppress).

**Doc-count reconciliation note (carried over from this task's brief, so
verdicts below don't misapply `score_e4.py`'s convention by habit):**
`score_t4_regression.py`'s `spec_docs_written`/`plan_docs_written` are
WHOLE-TRAJECTORY counts (every matching write anywhere in the run, not
gated to before the first code write); `doc_writes_before_first_code` is
the ONE census field actually gated to before the first code write, and
is the field this battery's criteria (b)/(c) below are checked against
alongside the raw `spec_docs_written`/`writing_plans_invoked` fields.
Separately, and unlike `score_e4.py` (which classifies ANY `*.md` file,
anywhere, as a doc, and anything under a `docs/` directory as a doc):
`score_t4_regression.py` classifies a path as a ceremony doc ONLY under
`docs/superpowers/(specs|plans)/`, and its `is_code_path()` counts a
NESTED (non-root) `*.md` file as CODE, not doc -- only a bare root-level
`*.md` (e.g. `README.md`) is excluded from "code." A file such as
`docs/api.md` (outside `docs/superpowers/`) or `src/README.md` would be
classified differently by the two scorers. This battery uses
`score_t4_regression.py` exclusively (per the brief and per Task 10's
design), so this note is here to keep any cross-battery comparison to the
layer-2 Codex results (scored by `score_e4.py`) honest about the
classification difference, not to flag a bug in either scorer.

**Criteria (verbatim from the brief / this log's T4 pre-registered-
criteria section, layer 3):**
- (a) **Per-cell gauntlet pass rate, fix >= dev** -- compared per
  `(harness, scenario_class)` pair across the 3 reps each arm contributes
  (6 pairs: claude x {spike,bounded,arch}, gemini x {spike,bounded,arch}),
  using `verdict.json`'s `gauntlet.status == "pass"` rate, matching layer
  2's own "gauntlet task completion" framing.
- (b) **Fix-arm arch cells** (`fix x {claude,gemini} x arch`, 2 cells)
  keep `spec_docs_written >= 1` (i.e. the spec-doc half of the two-doc
  ritual is written) on every rep, AND `writing_plans_invoked` true on
  3/3 reps in each cell.
- (c) **Fix-arm bounded cells** (`fix x {claude,gemini} x bounded`, 2
  cells) show `spec_docs_written == 0` on every rep, AND
  `writing_plans_invoked` false on all 3 reps in each cell (no rep in
  either cell shows a writing-plans skill read).
- (d) **Dev-arm bounded cells** (`dev x {claude,gemini} x bounded`, 2
  cells) are recorded as the baseline, not gated against a pass/fail bar
  -- expected shape (per the dev-arm Codex baseline cited in layer 2's
  pre-registration) is the unconditional two-doc ritual (spec + plan doc
  before any code, `writing_plans_invoked` true), and this battery checks
  whether that shape replicates cross-harness or diverges.

**Budget estimate:** ~$40-80 per the brief, anchored on layer 2's Codex
measurement ($16.87 for 7 ceremony reps, ~$2.41/rep average) with the
brief's own framing that "Claude/Gemini runs are the cheap side" (no
codex subscription-auth overhead; Claude/Gemini token pricing on these
small ceremony scenarios has historically undercut codex's on this
campaign's other cross-harness measurements). 36 reps at even 2x the
Codex per-rep rate would be ~$85, at the money at the top of the
pre-registered range; actual cost is reported from each rep's own
`verdict.json.economics.total_est_cost_usd`, not estimated after the
fact.

**Operational risk flagged before spending:** `df -h
/System/Volumes/Data` immediately before this entry shows **53Gi free of
1.8Ti (98% capacity)** -- WORSE than the 103Gi-free/95%-capacity state
that was a documented contributing factor in the SDD battery round 1
Docker Desktop crash (Task 8, above). Per that entry's standing
mitigation, this battery avoids repeating the JOBS=2-per-lane x 2-lanes
(4-concurrent-agent-session) configuration that preceded the crash;
concurrency and exact JOBS values are decided per-cell at run time based
on each scenario class's realistic session count, disclosed in the
result entry rather than fixed in advance here. Per this task's standing
operational instruction, a Docker anomaly stops the battery immediately
or upon a second unrecoverable failure -- honestly reported, not
retried through a crashing daemon, matching the precedent both the SDD
round-1 and this log's other batteries already established.

**No run yet -- this is the pre-registration.** Smoke test (1 rep per
harness, Step 3), full 36-run matrix, scoring, and manual hand-inspection
of one trajectory per harness per arm (4 total, non-circular -- reading
`trajectory.json` directly, not through the scorer) follow in later log
entries.

### 2026-07-30 — T4 LAYER 3 SMOKE TEST: both harnesses healthy; ANOMALY caught and fixed -- score_t4_regression.py never detected native Skill-tool writing-plans invocations (Task 11)

**Smoke test (Step 3, fix arm, `cc-ceremony-bounded` rep1, both
harnesses): PASS.** `claude`: `gauntlet.status: pass`, `final: pass`,
$0.99 (opus). `gemini`: `gauntlet.status: pass`, `final: pass`, $2.08
(model self-reports as `gemini-3.5-flash` -- `gemini_default`'s
`credentials.yaml` entry pins no model, "Gemini CLI defaults its own
model," so this is expected, not an anomaly). Both post-checks
(`investigated`) passed. Hand-inspected both `trajectory.json` files
directly (non-circular):
- `claude`: `agent.name: "claude-code"`, 23 steps, tool census
  `{Bash:6, Read:2, Edit:8}`. `first_code_file` is an ABSOLUTE path
  (`/workspace/evals/.../coding-agent-workdir/tests/test_server.py`) --
  Claude's normalizer records absolute `file_path` values, unlike
  Codex's repo-relative paths. Verified `score_t4_regression.py`'s
  `ceremony_doc_kind()`/`is_code_path()` are robust to this: both anchor
  on the `(^|/)docs/superpowers/(specs|plans)/` pattern as a substring
  match, not a strict path prefix, so absolute vs. relative paths score
  identically. Census: 0 spec docs, 0 plan docs, `writing_plans_invoked:
  false` -- correct for bounded.
- `gemini`: `agent.name: "gemini"`, 29 steps, tool census
  `{update_topic:2, Skill:4, Read:8, Bash:9, Edit:3,
  read_background_output:1}`. Census: 0 spec docs, 0 plan docs,
  `writing_plans_invoked: false` -- also correct for bounded.

**Caveat discovered, disclosed, not gated (does not affect this
battery's criteria, all of which are `spec_docs_written`/
`writing_plans_invoked`-based, not `user_turns`-based):** the gemini
trajectory's `sources` census is `{'agent': 29}` -- ZERO `source:
"user"` steps, so `user_turns_before_first_code` is structurally 0 for
this rep regardless of how many clarifying exchanges actually happened.
Root-caused by reading `superpowers/evals/src/normalize/gemini.ts`
directly: its per-message loop is `if (message['type'] !== 'gemini')
continue` -- it only ever processes the agent's own `'gemini'`-typed
messages from the raw session log; any `'user'`-typed message is
silently skipped, and the `source: 'user'` fallback step it does emit
only fires when the WHOLE trajectory has zero steps (not this rep's
case). This is a genuine gap in quorum's own Gemini normalizer, not
something in scope for this task's scenario/scorer files to fix -- flagged
here so any future battery reading `user_turns_before_first_code` for a
Gemini cell knows the field is not meaningfully comparable to Claude's or
Codex's for that harness.

**ANOMALY caught by the required hand-inspection, before the expensive
part of the matrix ran:** neither smoke rep's agent happened to invoke
the writing-plans skill (correct for bounded, per criterion (c)), so
this specific gap did not surface in the smoke reps' own numbers -- it
was caught by inspecting the RAW tool-call vocabulary each harness
actually used, not by a wrong smoke-test number. `score_t4_regression.py`
's `_writing_plans_invoked()` (Task 10) only recognized two patterns:
a `Read`-type call, or a `Bash` command string, both containing the path
substring `skills/writing-plans`. Both patterns describe how CODEX loads
skill content (`sed`/`cat`-ing `SKILL.md` via the shell, or reading it via
a discrete Read call) -- but per `superpowers/evals/src/detect/skill.ts`'s
`isSkillInvocation` (the already-tested detector behind `check-transcript
skill-called`), Claude Code and Gemini instead invoke a NATIVE `Skill`
tool call whose `arguments.skill` is the fully-qualified skill id (e.g.
`"superpowers:writing-plans"`) -- confirmed directly from the gemini
smoke rep's own raw `Skill` tool calls (`{"name": "brainstorming",
"skill": "superpowers:brainstorming"}` and 3 others, none for
writing-plans on this bounded rep, but the SHAPE is unambiguous). Neither
of `score_t4_regression.py`'s two recognized patterns matches a `Skill`
tool call at all, so **every genuine writing-plans invocation by Claude
or Gemini via the native tool would have scored `writing_plans_invoked:
false`** -- a false negative that would have silently failed criterion
(b) (fix-arm arch cells, `writing_plans_invoked` 3/3) for BOTH
cross-harness cells regardless of whether the fix arm's router text
actually worked, making the battery's headline arch criterion
unmeasurable as originally scored.

**Fix (committed with this entry, before any further battery spend):**
added a third pattern to `_writing_plans_invoked()` -- a native `Skill`
tool call whose `skill` argument equals exactly `"superpowers:
writing-plans"` -- mirroring `isSkillInvocation`'s own pattern 1 exactly
(same argument key, same exact-match semantics, deliberately not a
substring match so a `Skill` call for a different skill, e.g.
`brainstorming`, is never mistaken for writing-plans). Two new unit
tests added to `test_score_t4_regression.py` (positive: a `Skill` call
with `skill: "superpowers:writing-plans"` detected; negative: a `Skill`
call with `skill: "superpowers:brainstorming"` NOT detected) -- both
pass, and the full suite (`test_score_t4_regression.py` 19 tests +
`test_score_t4_regression_report.py` 16 tests) passes clean, 35/35.

**Independent, non-circular confirmation against REAL data (not just the
synthetic unit tests):** rather than trust the fix on synthetic fixtures
alone, ran one additional diagnostic rep beyond the pre-registered 2-run
smoke -- `fix` arm, `claude`, `cc-ceremony-arch`, rep1 (the scenario
class criterion (b) actually gates). Read the RAW `.claude/projects/**/
*.jsonl` session log directly (not through any normalizer or scorer)
mid-run and found three native `Skill` tool_use blocks: `{"skill":
"superpowers:brainstorming"}`, `{"skill": "superpowers:writing-plans"}`,
`{"skill": "superpowers:subagent-driven-development"}` -- exactly the
predicted shape, confirming the fix targets a real, live behavior, not a
hypothetical one. Let the rep run to completion (36m13s coding time,
$7.25, `gauntlet.status: pass`, subagent-driven-development path chosen,
14/14 tests passing on the merged branch). Re-scored its
`trajectory.json` with the FIXED scorer: `spec_docs_written: 1,
plan_docs_written: 1, doc_writes_before_first_code: 2,
writing_plans_invoked: true` -- exactly what criterion (b) requires, and
exactly what the OLD (unfixed) scorer would have missed
(`writing_plans_invoked: false` under the old code, since this rep's only
writing-plans signal is the native `Skill` call). **This diagnostic rep
is itself a legitimate, complete `fix x claude x arch` rep1 (same
`results/cx-eff-cc-ceremony-arch-fix-rep1` RUNDIR the real matrix would
have produced for rep1 of that cell) -- it is retained and counted as
that cell's rep1 in the full matrix below, not discarded, so this
diagnostic spend is not wasted budget.**

**Cost so far (3 reps: 2 pre-registered smoke + 1 additional
diagnostic):** claude bounded rep1 $0.99, gemini bounded rep1 $2.08,
claude arch rep1 $7.25 -- **$10.32**, all three retained as real reps
toward the 36-run matrix (fix x claude x bounded rep1, fix x gemini x
bounded rep1, fix x claude x arch rep1 respectively).

**Status: smoke test PASSED on both harnesses; one real scorer defect
found and fixed BEFORE it could silently invalidate the arch criterion
across the whole matrix, confirmed against live data, not merely
inferred from a code read.** Proceeding to the remaining matrix: 33 more
reps (dev x claude x 3 scenarios x 3 reps = 9; dev x gemini x 3 x 3 = 9;
fix x claude x {bounded: 2 more, arch: 2 more, spike: 3} = 7; fix x
gemini x {bounded: 2 more, arch: 3, spike: 3} = 8).

### 2026-07-30 — T4 LAYER 3 RESULT: full 36-run matrix complete; criteria (a)-(d) all PASS/recorded; two real ANOMALIES found and handled (run-quorum.sh silent-truncation bug; a pre-existing Claude+spike investigation-scoping pathology present on BOTH arms) (Task 11)

**All 36 pre-registered reps completed and scored** (`{dev,fix} x
{claude,gemini} x {spike,bounded,arch} x 3 reps`), via two lane driver
scripts (claude on lane A, gemini on lane B) launched concurrently,
plus a small backfill batch (below). `docker ps -a` checked repeatedly
through the ~5-hour battery: both lane containers stayed `Up` for every
segment, only re-upping on ARM switches as `run-quorum.sh` always does
-- no Docker loss, unlike the SDD-battery round-1 crash.

**ANOMALY 1 -- `run-quorum.sh` silently truncates a REPS>1 invocation on
the FIRST measured fail/indeterminate rep, not just on an infra
crash.** Discovered when `dev cc-ceremony-spike 3 1` (lane A, JOBS=2)
returned cell-exit 1 and `results/cx-eff-cc-ceremony-spike-dev-rep3/`
never appeared on disk at all -- not partially written, not attempted.
Root cause (read from source, `src/cli/run-command.ts`
`exitCodeFor`): `quorum run` exits **1 on a measured `fail` verdict**
and **2 on `indeterminate`**, not only on a genuine crash. Because
`run-quorum.sh` has `set -euo pipefail`, ANY rep in a batch (JOBS>1) or
in the sequential loop (JOBS=1) returning nonzero aborts the WHOLE
remaining rep range immediately -- a batch-internal `wait "$pid" ||
failed=1` triggers the script's own `exit 1` before the next batch
starts, and under JOBS=1 `set -e` kills the `for` loop outright. This
had never surfaced in this campaign's prior batteries by coincidence:
every fail/indeterminate/`investigate` verdict on record so far
happened to land in the LAST batch of its invocation (nothing left to
truncate). `dev cc-ceremony-spike` (rep1 indeterminate, rep2 fail --
both in batch1 of a JOBS=2/REPS=3 split) is the first battery in this
campaign where a mid-sequence failure actually hit the bug. Same
mechanism separately truncated `fix cc-ceremony-spike` (rep1
indeterminate, in batch1). **No data was lost** -- every rep that DID
run wrote a complete `verdict.json`/`trajectory.json` before the script
noticed the failure and exited; only the NEVER-ATTEMPTED reps are
missing. **Fix:** documented as a known limitation directly in
`run-quorum.sh`'s header comment (committed with this entry) rather
than re-architected (would need redesigning both loops' failure
handling, out of this task's scope) -- future batteries must diff the
requested rep range against what actually landed on disk. **Handled
operationally this task:** backfilled the exact two missing reps
(`dev cc-ceremony-spike rep3`, `fix cc-ceremony-spike rep3`) with two
separate `REPS=1` calls (immune to the bug by construction -- no "next
rep" to truncate).

**ANOMALY 2 -- a real, pre-existing Claude+`cc-ceremony-spike`
investigation-scoping pathology, present on BOTH arms (not a fix-vs-dev
regression signal).** Of Claude's 6 total spike reps (3 dev + 3 fix,
including the 2 backfilled), only 1 (`fix` rep2) passed cleanly. The
other 5 fail in two distinct, both hand-read directly from the
Gauntlet-Agent's own verdict summary (not inferred):
- **3 reps (`dev` rep1, `fix` rep1, `fix` rep3): ZERO tool calls.** The
  agent answered the port-in-use question fluently but never opened
  `server.py` (the Python stdlib service the story is about) --
  instead it answered in Node.js/TypeScript/Bun terms
  (`http.createServer`, `Bun.serve`, `EADDRINUSE`), which the
  Gauntlet-Agent's own independent `jq`/`grep` pass against the raw
  session JSONL confirmed contains no `tool_use` entries at all. quorum's
  composer maps this to `final: indeterminate` (empty-capture rule,
  `STRICT_CAPTURE_NAMES` includes `claude`) even though the
  Gauntlet-Agent's own underlying verdict is `fail` in every case --
  `gauntlet.status` (the field this battery's "gauntlet pass rate"
  criterion actually grades) correctly reads `fail`, not masked by the
  `final` field's indeterminate wrinkle.
- **2 reps (`dev` rep2, `dev` rep3): investigated the WRONG codebase.**
  The agent ran `grep`/`Read` against
  `/workspace/evals/packages/dashboard/src/index.ts` -- a
  TypeScript/Bun file belonging to the EVALS HARNESS ITSELF, visible on
  disk as a sibling of the scenario's own mounted tree -- and built its
  entire answer around that unrelated dashboard service, never
  referencing `server.py` at all despite it sitting in the correct cwd
  the whole time (confirmed present via `find` in both Gauntlet-Agent
  transcripts).
This is symmetric across arms (dev 0/3 gauntlet-pass, fix 1/3) and is
therefore NOT attributable to the fix arm's router-text change -- it
reads as a pre-existing weakness specific to (a) Claude, (b) this
particular spike-class story ("quick and dirty is fine" plus a
port-in-use question that pattern-matches strongly to generic
Node.js/web-server training examples), and (c) this container's mounted
`/workspace/evals` tree exposing the harness's own unrelated source
alongside the scenario fixture. Gemini shows none of this (6/6 spike
reps clean, always grounded in `server.py`). Flagged here as a
methodological caveat for any future reuse of `cc-ceremony-spike`
against Claude specifically -- not a T4 fix regression, and not gated
by any pre-registered criterion (none of (a)-(d) require a spike pass
rate above the trivial fix>=dev comparison).

**Full per-cell results** (from `score_t4_regression_report.py`,
invoked once across all 36 RUNDIRs from both lanes; output committed at
`out/t4-layer3-dev-fix-claude-gemini-rep1-3.json`):

| arm | agent | class | n | gauntlet pass | spec docs (mean) | plan docs (mean) | writing-plans invoked | cost ($) |
|---|---|---|---:|---|---:|---:|---|---:|
| dev | claude | arch | 3 | 3/3 | 1.00 | 1.00 | 3/3 | 23.11 |
| dev | claude | bounded | 3 | 3/3 | 0.00 | 0.00 | 0/3 | 2.72 |
| dev | claude | spike | 3 | 0/3 | 0.00 | 0.00 | 0/2* | 0.88 |
| dev | gemini | arch | 3 | 3/3 | 1.00 | 1.00 | 3/3 | 40.15 |
| dev | gemini | bounded | 3 | 3/3 | 1.00 | 1.00 | 3/3 | 8.35 |
| dev | gemini | spike | 3 | 3/3 | 0.00 | 0.00 | 0/3 | 1.24 |
| fix | claude | arch | 3 | 3/3 | 1.00 | 1.33 | 3/3 | 20.05 |
| fix | claude | bounded | 3 | 3/3 | 0.00 | 0.00 | 0/3 | 3.00 |
| fix | claude | spike | 3 | 1/3 | 0.00 | 0.00 | 0/1* | 0.48 |
| fix | gemini | arch | 3 | 3/3 | 1.00 | 1.00 | 3/3 | 33.41 |
| fix | gemini | bounded | 3 | 3/3 | 0.00 | 0.00 | 0/3 | 5.54 |
| fix | gemini | spike | 3 | 3/3 | 0.00 | 0.00 | 0/3 | 2.13 |

\* `writing_plans_invoked_n` is 2 (dev/claude/spike) and 1 (fix/claude/spike),
not 3 -- the indeterminate/zero-tool-call reps produce no `trajectory.json`
census at all (`n_scored` < `n`), so they're excluded from the census
mean/rate denominators; `gauntlet pass` (from `verdict.json` directly,
not the census) still counts all 3 reps correctly.

`fix/claude/arch`'s plan-docs mean of 1.33 (not 1.00) is a genuine plan
REVISION on rep2, hand-verified directly against the raw trajectory
(one `Write` then one `Edit` to the identical
`docs/superpowers/plans/2026-07-31-notes-service-library-cli-split.md`
path) -- the same "plan doc written twice" shape the layer-2 Codex
battery already documented as expected variance, not a scorer defect.

**Manual, non-circular hand-inspection (reading `trajectory.json`/raw
session JSONL directly, one rep per harness per arm, 4 total, beyond
the smoke-test hand-inspection already logged above):**
- `dev/claude/arch/rep1`: raw `Write`/`Edit` tool-call scan shows
  exactly one `docs/superpowers/specs/*.md` and one
  `docs/superpowers/plans/*.md` write, both before the first code file
  -- matches the scorer's `spec_docs_written:1, plan_docs_written:1`
  exactly. Also independently confirms this task's own doc-count
  reconciliation note: `.superpowers/sdd/**/task-N-report.md` files
  (written by the SDD subagent path this rep took) are NOT under
  `docs/` and are correctly NOT counted as ceremony docs by
  `score_t4_regression.py`.
- `dev/gemini/bounded/rep1`: raw tool-call scan shows
  `Skill(superpowers:using-superpowers)` ->
  `Skill(superpowers:brainstorming)` -> `Write(specs/...)` ->
  `Skill(superpowers:writing-plans)` -> `Write(plans/...)` ->
  `Skill(superpowers:executing-plans)` -> `Edit(server.py)` x4 ->
  `Edit(tests/test_server.py)` x2 ->
  `Skill(superpowers:verification-before-completion)` -- the
  unconditional two-doc ritual, fully replicated on Gemini's DEV arm
  even for a bounded-scoped task, matching the scorer's
  `spec_docs_written:1, writing_plans_invoked:True` exactly.
- `fix/claude/bounded/rep1` and `fix/claude/arch/rep1`: already
  hand-inspected in the smoke-test entry above (raw JSONL, zero docs
  for bounded; native `Skill(superpowers:writing-plans)` call
  confirmed live for arch).
- `fix/gemini/bounded/rep1`: already hand-inspected in the smoke-test
  entry above (zero docs, matches).

**A genuinely surprising, disclosed-not-gated finding under criterion
(d):** the dev-arm "unconditional two-doc ritual" baseline does NOT
replicate identically across harnesses. Gemini's `dev` arm reproduces
it exactly (bounded: 3/3 reps, 1 spec + 1 plan doc each, matching the
original Codex dev-arm baseline this campaign measured in the prior
cycle). **Claude's `dev` arm does NOT** -- `dev/claude/bounded` shows
**zero** ceremony docs on all 3 reps, identical in shape to
`fix/claude/bounded`. This means, for Claude specifically, the
before/after doc-ceremony DELTA on bounded is nil (0 -> 0) -- this
battery cannot show a Claude-side ceremony reduction on bounded because
Claude's dev arm apparently never had the "always write 2 docs even for
a one-file flag" pathology to begin with (on this scenario, in this
container). Per the pre-registration, criterion (d) is explicitly "not
gated against a pass/fail bar," so this is recorded as the honest
finding, not a failure -- but it means this battery's cross-harness
regression evidence for the FIX's marginal contribution on
`bounded`-class doc ceremony is really a Gemini-only before/after story
(3/3 ceremony docs on dev -> 0/3 on fix); Claude's contribution is
better read as "confirmed clean on both arms" than "measurably fixed."

**Criteria verdicts (verbatim against the pre-registration above):**

- **(a) Per-cell gauntlet pass rate, fix >= dev -- PASS, all 6
  `(harness, scenario_class)` pairs.** claude/spike: dev 0/3 -> fix 1/3
  (fix >= dev, though both are weak -- see Anomaly 2, a pre-existing
  pathology on both arms, not a regression). claude/bounded: 3/3 ->
  3/3 (tied). claude/arch: 3/3 -> 3/3 (tied). gemini/spike: 3/3 -> 3/3
  (tied). gemini/bounded: 3/3 -> 3/3 (tied). gemini/arch: 3/3 -> 3/3
  (tied). No cell shows fix < dev anywhere.
- **(b) Fix-arm arch cells keep `spec_docs_written >= 1` (every rep)
  AND `writing_plans_invoked` 3/3 -- PASS, both cells.**
  `fix/claude/arch`: 1,1,1 spec docs (all >=1); `writing_plans_invoked`
  True on 3/3, hand-confirmed live via the native `Skill` tool-call fix
  from the smoke-test entry. `fix/gemini/arch`: 1,1,1 spec docs;
  `writing_plans_invoked` True on 3/3.
- **(c) Fix-arm bounded cells show `spec_docs_written == 0` (every
  rep) AND `writing_plans_invoked` false on all 3 reps -- PASS, both
  cells.** `fix/claude/bounded`: 0,0,0 spec docs, `writing_plans_invoked`
  False on 3/3. `fix/gemini/bounded`: 0,0,0 spec docs,
  `writing_plans_invoked` False on 3/3.
- **(d) Dev-arm bounded cells recorded as baseline -- RECORDED, not
  gated.** `dev/gemini/bounded` replicates the expected unconditional
  two-doc ritual (3/3 reps, 1 spec + 1 plan doc each,
  `writing_plans_invoked` True 3/3) -- matches the original Codex
  dev-arm baseline this campaign established. `dev/claude/bounded`
  does NOT replicate it (0/3 ceremony docs, identical in shape to its
  own fix-arm counterpart) -- a genuine, disclosed cross-harness
  divergence in the dev-arm baseline itself (see finding above), not a
  criterion failure.

**Cost -- real, disclosed overrun against the pre-registered ~$40-80
estimate.** **Total measured: $141.04** across 33 of 36 reps with
captured economics (the 3 zero-tool-call/indeterminate Claude-spike
reps have `verdict.json.economics: null` -- genuinely unmeasured, not
estimated, per this log's standing "no figure exists" convention, same
as the SDD-battery round-1 Docker-crash reps). By agent: claude $50.24,
gemini $90.80. By arm: dev $76.44, fix $64.60. By scenario class:
**arch $116.72 (82.7% of the whole battery), bounded $19.60, spike
$4.72.** The overrun is entirely explained by Gemini's arch cells:
`dev/gemini/arch` rep2 alone cost **$26.38** (8.8M+ tokens on
`gemini-3.5-flash`, the model `gemini_default` floats to since its
`credentials.yaml` entry pins no model), `fix/gemini/arch` rep2 cost
$21.18 -- both multiples of any single Claude arch rep ($5.80-$8.31) or
any Codex arch rep from layer 2 (max $8.21). The brief's own framing
("Claude/Gemini runs are the cheap side") held for Claude but was WRONG
for Gemini specifically on the arch scenario class -- Gemini's
token-per-turn cost on a long, multi-subagent SDD-path arch run is
substantially higher than either Claude's or Codex's on the same
scenario shape, not lower.

**Ledger row:** 2026-07-30 | T4 layer-3 global regression battery (T4
layer 3, `{dev,fix} x {claude,gemini} x {spike,bounded,arch}`, 36 of 36
pre-registered reps, no Docker loss) | $141.04 (33/36 reps measured; 3
Claude-spike indeterminate reps have no economics block, unmeasured) |
(a) PASS all 6 pairs | (b) PASS both fix-arch cells | (c) PASS both
fix-bounded cells | (d) recorded -- Gemini dev-arm replicates the
two-doc-ritual baseline, Claude dev-arm does not.

**Status: DONE. All four pre-registered criteria met their bar** -- (a)
no cell regresses fix-vs-dev on gauntlet completion; (b) the arch
two-doc/writing-plans ritual holds cross-harness on the fix arm; (c)
the bounded ceremony-suppression holds cross-harness on the fix arm;
(d) the dev-arm baseline is recorded honestly, including the surprising
cross-harness divergence in what that baseline even looks like. Two
real anomalies were found and handled, not hidden: a `run-quorum.sh`
tooling defect (documented, worked around, not deeply fixed) and a
pre-existing Claude+spike investigation-scoping pathology (present on
both arms, explicitly not attributed to the fix). The battery ran
**$61-101 over its own pre-registered estimate**, driven entirely by
Gemini's arch-scenario token cost, disclosed rather than smoothed over.
