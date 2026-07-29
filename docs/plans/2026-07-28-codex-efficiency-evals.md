# Codex Efficiency Eval Campaign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build six corpus-validated evals (E1 fork hygiene, E2 reviewer recursion, E3 evidence receipts, E4 proportional ceremony, E5 review scope, E6 compaction recovery) that fail on current `dev` and grade `codex-spinout-fixes`, per the approved spec `docs/2026-07-28-codex-efficiency-eval-campaign-design.md`.

**Architecture:** A shared stdlib-Python rollout parser (`rollout_parser.py`) turns Codex rollout JSONL into typed metrics; per-experiment scorers are thin layers on it. Scorers are validated against the 2026-07-28 audit corpus (known ground truth) before grading fresh runs. Fresh runs use quorum in `scripts/evals-container` with campaign-local scenarios via `--scenarios-root`; cheap micros use `codex exec` inside the same container.

**Tech Stack:** Python 3 stdlib only (autoresearch convention); quorum/Bun in `superpowers/evals`; Docker via `scripts/evals-container`; sqlite3 CLI read-only.

## Global Constraints

- All harness/scorer code: Python 3, stdlib only, parameterized via env vars (autoresearch convention).
- Raw rollout files and any client project content NEVER get committed. Only scorers, aggregates, and synthetic fixtures enter the repo.
- A scorer issues no verdict until validated against corpus ground truth AND its matches are manually inspected (print samples, eyeball, record in log).
- Discrimination rule: an eval counts only when its `dev` baseline exhibits the documented pathology; otherwise record inconclusive-by-zero and STOP that experiment.
- Quorum runs happen ONLY inside `scripts/evals-container` (host runs are confounded by global CLAUDE.md).
- Never edit a `SUPERPOWERS_ROOT` checkout while a run reads it — treatment arms use dedicated worktrees under `/tmp/`.
- Budget: $1000 Anthropic-side, itemized in the hypothesis log after every battery (`quorum costs <batch>`); also record Codex subscription `used_percent` before/after each battery (from any rollout's last `token_count.rate_limits.primary.used_percent`).
- Campaign home: `/Users/jesse/git/superpowers/superpowers-autoresearch/campaigns/codex-efficiency/`. Hypothesis log: `logs/2026-07-28-codex-efficiency.md` (append-only). Commit after every task.
- Key external paths (read-only): audit artifacts `/Users/jesse/.codex/visualizations/2026/07/28/019fa9a2-87b7-73b1-a76a-efb9f14abbea/` (aliased `$AUDIT` below); rollouts `/Users/jesse/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`; evals checkout `/Users/jesse/git/superpowers/superpowers/evals` (aliased `$EVALS`).

---

### Task 1: Campaign scaffold and pre-registered hypothesis log

**Files:**
- Create: `campaigns/codex-efficiency/DESIGN.md`
- Create: `logs/2026-07-28-codex-efficiency.md`

**Interfaces:**
- Produces: the append-only hypothesis log every later task appends verdicts to; DESIGN.md pointing at spec + recon facts.

- [ ] **Step 1: Write DESIGN.md**

Content: link to `docs/2026-07-28-codex-efficiency-eval-campaign-design.md`; one paragraph per experiment E1–E6 (copy the six packages from the spec verbatim); a "Recon facts" section recording: rollout line shape (`timestamp`/`type`/`payload`), spawn args are a JSON string with unstable key order and `"(omitted)"` markers, child linkage via `sub_agent_activity.event_id == spawn call_id`, compaction emits a `compacted` record plus an `event_msg/context_compacted` marker pair, skill reads are textual heuristics over exec input (audit regex: `/SKILL\.md|skills\.read|activate_skill/i`, false-positives on apply_patch), quorum invocation forms and `--scenarios-root`, `codex exec` micro pattern from `harnesses/codex-read-delivery-micro.py`.

- [ ] **Step 2: Write the hypothesis log with pre-registered predictions**

`logs/2026-07-28-codex-efficiency.md`, sections: Budget ledger (table: date, battery, $ cost, sub used_percent before/after), then one entry per experiment BEFORE any run, each with Prediction / Scorer / Success criterion. Predictions (register these exact numbers):

- E1 baseline: ≥40% of SDD spawns use `fork_turns:"all"`; ≥60% omit `model`. Treatment (`codex-spinout-fixes`): 100% `"none"`, 100% explicit model, task completion preserved.
- E2 baseline: a dispatched branch reviewer produces ≥1 descendant in ≥half of reps.
- E3 baseline: the full test suite runs ≥2× at an identical tree state across implementer→review→finishing.
- E4 baseline: ceremony census (docs written, approval gates, user turns before first code patch) is statistically indistinguishable across spike/bounded/architectural task classes.
- E5 baseline: the local-scope defect is caught; at least one of {cross-task race, clean-checkout break, repair-induced regression} is missed by the mis-matched scope or duplicated across same-scope reviewers.
- E6 baseline: after a forced compaction the controller re-reads ≥1 SKILL.md it had already read, and ≥1 post-compaction spawn drops isolation or model explicitness relative to pre-compaction spawns.

- [ ] **Step 3: Commit**

```bash
cd /Users/jesse/git/superpowers/superpowers-autoresearch
git add campaigns/codex-efficiency/DESIGN.md logs/2026-07-28-codex-efficiency.md
git commit -m "campaign(codex-efficiency): scaffold + pre-registered hypothesis log"
```

---

### Task 2: rollout_parser core — record iteration, spawns, child links

**Files:**
- Create: `campaigns/codex-efficiency/rollout_parser.py`
- Test: `campaigns/codex-efficiency/test_rollout_parser.py`

**Interfaces:**
- Produces:
  - `iter_records(path) -> Iterator[tuple[str, str, dict]]` — (timestamp, outer type, payload); skips lines >8MB (counts them via the returned iterator's `.oversized` attr is NOT used — instead see `parse_session` in Task 3; here just skip unparseable/oversized lines silently).
  - `@dataclass Spawn: call_id: str; task_name: str; fork_turns: str; model: str; reasoning_effort: str; timestamp: str` — missing arg fields become `"(omitted)"` (matching the audit convention).
  - `extract_spawns(path) -> list[Spawn]`
  - `child_links(path) -> dict[str, str]` — spawn call_id → child agent_thread_id, from `sub_agent_activity` payloads with `kind == "started"`.

- [ ] **Step 1: Write failing tests with synthetic fixture lines**

`test_rollout_parser.py` builds a temp .jsonl from synthetic records copied from the recon shapes (no client content):

```python
import json, tempfile, pathlib, unittest
import rollout_parser as rp

def L(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})

SPAWN_FULL = L("2026-07-28T16:59:22.815Z", "response_item", {
    "type": "function_call", "id": "fc_1", "name": "spawn_agent",
    "namespace": "collaboration",
    "arguments": json.dumps({"task_name": "t_one", "fork_turns": "none",
                             "model": "gpt-5.6-terra", "reasoning_effort": "high",
                             "message": "gAAAAABencrypted"}),
    "call_id": "call_A"})
SPAWN_BARE = L("2026-07-28T16:59:30.000Z", "response_item", {
    "type": "function_call", "id": "fc_2", "name": "spawn_agent",
    "arguments": json.dumps({"task_name": "t_two", "fork_turns": "all",
                             "message": "gAAAAABx"}),
    "call_id": "call_B"})
CHILD_STARTED = L("2026-07-28T16:59:23.116Z", "event_msg", {
    "type": "sub_agent_activity", "event_id": "call_A",
    "agent_thread_id": "019fa9aa-child-uuid", "agent_path": "/root/t_one",
    "kind": "started"})
NOT_A_SPAWN = L("2026-07-28T17:00:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_3", "name": "wait_agent",
    "arguments": "{}", "call_id": "call_C"})

def write_fixture(lines):
    f = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    f.write("\n".join(lines) + "\n")
    f.close()
    return pathlib.Path(f.name)

class TestSpawns(unittest.TestCase):
    def test_extract_spawns_full_and_omitted(self):
        p = write_fixture([SPAWN_FULL, CHILD_STARTED, SPAWN_BARE, NOT_A_SPAWN, "not json"])
        s = rp.extract_spawns(p)
        self.assertEqual(len(s), 2)
        self.assertEqual((s[0].call_id, s[0].fork_turns, s[0].model), ("call_A", "none", "gpt-5.6-terra"))
        self.assertEqual((s[1].fork_turns, s[1].model, s[1].reasoning_effort), ("all", "(omitted)", "(omitted)"))

    def test_child_links(self):
        p = write_fixture([SPAWN_FULL, CHILD_STARTED, SPAWN_BARE])
        self.assertEqual(rp.child_links(p), {"call_A": "019fa9aa-child-uuid"})

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests, verify failure**

Run: `cd campaigns/codex-efficiency && python3 test_rollout_parser.py`
Expected: FAIL (`ModuleNotFoundError` / `AttributeError`).

- [ ] **Step 3: Implement**

```python
"""Parse Codex rollout JSONL (three-key lines: timestamp/type/payload).
Shapes verified against the 2026-07-28 audit corpus recon."""
import json, dataclasses, pathlib
from typing import Iterator

MAX_LINE_BYTES = 8 * 1024 * 1024  # match audit scanner

def iter_records(path) -> Iterator[tuple[str, str, dict]]:
    with open(path, "rb") as f:
        for raw in f:
            if len(raw) > MAX_LINE_BYTES:
                continue
            try:
                rec = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(rec, dict):
                continue
            yield rec.get("timestamp", ""), rec.get("type", ""), rec.get("payload", {}) or {}

OMIT = "(omitted)"

@dataclasses.dataclass
class Spawn:
    call_id: str; task_name: str; fork_turns: str
    model: str; reasoning_effort: str; timestamp: str

def _spawn_calls(path):
    for ts, typ, p in iter_records(path):
        if typ == "response_item" and p.get("type") == "function_call" \
           and p.get("name") == "spawn_agent":
            yield ts, p

def extract_spawns(path) -> list[Spawn]:
    out = []
    for ts, p in _spawn_calls(path):
        try:
            args = json.loads(p.get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}
        out.append(Spawn(
            call_id=p.get("call_id", OMIT),
            task_name=str(args.get("task_name", OMIT)),
            fork_turns=str(args.get("fork_turns", OMIT)),
            model=str(args.get("model", OMIT)),
            reasoning_effort=str(args.get("reasoning_effort", OMIT)),
            timestamp=ts))
    return out

def child_links(path) -> dict[str, str]:
    links = {}
    for ts, typ, p in iter_records(path):
        if typ == "event_msg" and p.get("type") == "sub_agent_activity" \
           and p.get("kind") == "started":
            links[p["event_id"]] = p.get("agent_thread_id", "")
    return links
```

- [ ] **Step 4: Run tests, verify pass**

Run: `python3 test_rollout_parser.py` — Expected: OK.

- [ ] **Step 5: Commit**

```bash
git add campaigns/codex-efficiency/rollout_parser.py campaigns/codex-efficiency/test_rollout_parser.py
git commit -m "campaign(codex-efficiency): rollout parser core — spawns + child links (TDD)"
```

---

### Task 3: rollout_parser metrics — lifecycle, compactions, read/test heuristics, exec extraction

**Files:**
- Modify: `campaigns/codex-efficiency/rollout_parser.py`
- Test: `campaigns/codex-efficiency/test_rollout_parser.py`

**Interfaces:**
- Consumes: `iter_records` from Task 2.
- Produces:
  - `@dataclass ExecCmd: call_id: str; cmd: str; timestamp: str; encoding: str` (`encoding` ∈ {`"exec_command"`, `"custom_exec"`}).
  - `exec_commands(path) -> list[ExecCmd]` — from BOTH encodings: `function_call` named `exec_command` (JSON-string args, take `args["cmd"]`) and `custom_tool_call` named `exec` (freeform JS `input`; take the whole input string as `cmd`).
  - `@dataclass SessionMetrics` with int fields: `lines, oversized_lines, compactions, task_started, task_complete, skill_reads_compat, skill_reads_strict, memory_reads, spawn_calls, wait_calls, test_commands, user_messages, patch_applies` and `first_instruction_line: int | None` (0-based line index of the first `event_msg`/`user_message`).
  - `parse_session(path) -> SessionMetrics`.
- IMPORTANT: before implementing, READ `/Users/jesse/.codex/visualizations/2026/07/28/019fa9a2-87b7-73b1-a76a-efb9f14abbea/scan-rollouts.mjs` and copy its exact classifier regexes for skill reads, memory reads, wait detection, and test-command detection into Python (translate flags; keep semantics identical — corpus validation in Task 4 depends on parity). `skill_reads_compat` uses the audit regex verbatim; `skill_reads_strict` additionally requires the record be an exec-like input (never `apply_patch`) and the match be a read-shaped command (regex `(cat|sed|head|less|tail|rg|grep|open|read)[^\n]*SKILL\.md`).

- [ ] **Step 1: Extend tests (failing)**

Add synthetic records to the fixture builder: an `exec_command` function_call (args JSON string with `cmd`), a `custom_tool_call` named `exec` whose `input` contains `sed -n '1,240p' .../skills/x/SKILL.md`, an `apply_patch` custom_tool_call whose input mentions `SKILL.md` (must count in compat, NOT in strict), a `compacted` record + its `event_msg`/`context_compacted` marker (compactions must count the marker only → 1, not 2), `task_started`/`task_complete` event_msgs, one `user_message` event, a `wait_agent` function_call, and a `patch_apply_end` event. Assertions:

```python
def test_parse_session_counters(self):
    p = write_fixture([USER_MSG, SPAWN_FULL, EXEC_FC, CUSTOM_EXEC_SKILL_READ,
                       APPLY_PATCH_MENTIONS_SKILL, COMPACTED, COMPACTED_MARKER,
                       TASK_STARTED, TASK_COMPLETE, WAIT_CALL, PATCH_END])
    m = rp.parse_session(p)
    self.assertEqual(m.compactions, 1)
    self.assertEqual(m.task_started, 1)
    self.assertEqual(m.task_complete, 1)
    self.assertEqual(m.skill_reads_compat, 2)   # real read + apply_patch mention
    self.assertEqual(m.skill_reads_strict, 1)   # real read only
    self.assertEqual(m.spawn_calls, 1)
    self.assertEqual(m.wait_calls, 1)
    self.assertEqual(m.user_messages, 1)
    self.assertEqual(m.patch_applies, 1)
    self.assertEqual(m.first_instruction_line, 0)

def test_exec_commands_both_encodings(self):
    p = write_fixture([EXEC_FC, CUSTOM_EXEC_SKILL_READ])
    cmds = rp.exec_commands(p)
    self.assertEqual([c.encoding for c in cmds], ["exec_command", "custom_exec"])
    self.assertIn("pytest", cmds[0].cmd)
```

- [ ] **Step 2: Run tests, verify the new ones fail** — `python3 test_rollout_parser.py`

- [ ] **Step 3: Implement `exec_commands` and `parse_session`**

Single pass over `iter_records`, tracking line index manually (enumerate the file separately inside `parse_session` — reuse `iter_records` but add an internal variant `_iter_with_lineno` yielding `(lineno, ts, typ, payload)`; refactor `iter_records` to delegate to it). Counters per the interface. Wait detection: `function_call` names matching the audit's wait classifier (copied from scan-rollouts.mjs — includes at least `wait_agent`; copy exactly). Test-command detection: audit regex over exec cmd text.

- [ ] **Step 4: Run all tests, verify pass.**

- [ ] **Step 5: Smoke on one real rollout (do not commit output)**

```bash
python3 -c "import rollout_parser as rp, glob; p=sorted(glob.glob('/Users/jesse/.codex/sessions/2026/07/28/rollout-*.jsonl'))[0]; print(rp.parse_session(p))"
```
Expected: plausible nonzero counters, no traceback.

- [ ] **Step 6: Commit** — `git commit -am "campaign(codex-efficiency): parser metrics + exec extraction (TDD)"`

---

### Task 4: MINE — corpus validation of the parser

**Files:**
- Create: `campaigns/codex-efficiency/validate_corpus.py`
- Create: `campaigns/codex-efficiency/out/corpus-validation.md` (aggregates only — safe to commit)

**Interfaces:**
- Consumes: `extract_spawns`, `parse_session` (Tasks 2–3); `$AUDIT/session-manifest.json`, `$AUDIT/spawns-window.json`, `$AUDIT/metrics-all.jsonl`.
- Produces: a written validation verdict in the hypothesis log; the parser is thereafter trusted.

- [ ] **Step 1: Write `validate_corpus.py`**

Env: `AUDIT_DIR` (default the audit path above). Three phases, printed as a report:

Phase A (spawn parity, exact): load `spawns-window.json`; group records by `session_id`; resolve each session's `rollout_path` from `session-manifest.json`; for each such session run `extract_spawns` and compare (call_id, task_name, fork_turns, model, reasoning_effort) sets. Filter our extraction to the audit window (timestamps between `2026-07-14T07:00:00Z` and `2026-07-28T16:50:29.164Z`) before comparing. Report: sessions compared, exact-match sessions, and every mismatch with call_id + field diff. Also print the aggregate fork_turns and model distributions next to the audit's (574 all / 359 none / 18 omitted / partials; 925 omitted models).

Phase B (per-session metrics, stratified sample): from `metrics-all.jsonl` pick ~60 sessions: the 10 largest by `bytes`, 10 with `oversized_lines > 0`, 10 with `context_compacted > 0`, 10 with `spawn_calls > 0`, 20 random (seed fixed at 42 via `random.Random(42)`). For each, compare `parse_session` fields against the metrics row: `context_compacted, task_started, task_complete, skill_reads(→skill_reads_compat), memory_reads, spawn_calls, wait_calls, test_command_calls(→test_commands)`. Report per-field exact-match rates and every mismatch (session id, field, ours vs theirs).

Phase C (manual-inspection feed): print 10 random matched skill-read commands and 10 matched test commands (truncated to 160 chars) for eyeball review.

- [ ] **Step 2: Run it** — `python3 validate_corpus.py | tee out/corpus-validation-raw.txt`

Skip committing the raw output (may quote client commands); write `out/corpus-validation.md` by hand with match rates and mismatch *categories* only.

- [ ] **Step 3: Adjudicate mismatches**

Exact parity on Phase A is required (fix parser until match or document a proven audit-script bug, e.g. the known `developer_messages: null`). Phase B: require ≥95% exact per field; every remaining mismatch must have a written explanation. Manually eyeball Phase C output. If parity is unreachable for a field, that field's scorer downstream must not rely on it — record the restriction.

- [ ] **Step 4: Append verdict to hypothesis log + commit**

```bash
git add campaigns/codex-efficiency/validate_corpus.py campaigns/codex-efficiency/out/corpus-validation.md logs/2026-07-28-codex-efficiency.md
git commit -m "campaign(codex-efficiency): parser validated against audit corpus (MINE)"
```

---

### Task 5: Scenario infrastructure — SDD fixture, scenario root, container smoke

**Files:**
- Create: `campaigns/codex-efficiency/scenarios/cx-sdd-small/{story.md,setup.sh,checks.sh}`
- Create: `campaigns/codex-efficiency/fixtures/sdd-small/` (tiny repo skeleton + `plan.md`)
- Create: `campaigns/codex-efficiency/run-quorum.sh`

**Interfaces:**
- Consumes: quorum CLI forms from recon (Task 1 DESIGN.md records them).
- Produces: `run-quorum.sh ARM SCENARIO REPS` — runs `scripts/evals-container exec quorum run <scenario> --coding-agent codex` REPS times with `--out-root results/cx-eff-<scenario>-<ARM>-rep<n>`, where ARM selects the mounted superpowers root (see Step 4); scenario `cx-sdd-small` used by E1/E3/E6.

- [ ] **Step 1: Build the fixture**

`fixtures/sdd-small/`: a 3-task Python mini-project plan. Check `superpowers-autoresearch/fixtures/` first — if a plan-generation fixture plan already exists (used by `harnesses/plan-generation-micro.py`), reuse it. Otherwise generate `plan.md` WITH the system under test (fixture-realism rule): one `codex exec` in-container against the dev superpowers root, prompt = "Use your superpowers writing-plans skill to write docs/plans/plan.md for this spec" + a ~15-line spec for a string-utils CLI (3 tasks: core function w/ tests, CLI wrapper, README). Keep the resulting plan.md; strip any host paths.

- [ ] **Step 2: Write the scenario**

`story.md` frontmatter: `id: cx-sdd-small`, `title: SDD small-plan execution (codex efficiency campaign)`, `status: ready`, `quorum_tier: adhoc`, `quorum_max_time: 25m`. Body: Gauntlet-Agent types exactly: *"Please execute the plan in plan.md using your subagent-driven-development skill."* and answers any workflow questions with minimal-yes defaults. Acceptance criteria: agent attempted plan execution; at least one subagent was dispatched; session ended without error. (Scoring happens offline; the scenario only needs to complete.)

`setup.sh` (executable): copy `fixtures/sdd-small/` into `$QUORUM_WORKDIR`, `git init`, initial commit. Use `setup-helpers run symlink_superpowers` if the existing codex scenarios' setup.sh do (mirror `$EVALS/scenarios/codex-tool-mapping-comprehension/setup.sh` exactly on this point).

`checks.sh` (NOT executable), header comment `# coding-agents: codex`; `pre()` asserts git repo exists; `post()` asserts `check-transcript`-level minimal evidence mirroring the codex scenarios' style (at minimum: rollout file exists — `file-exists` on `home/.codex/sessions`).

- [ ] **Step 3: Write `run-quorum.sh`**

```bash
#!/usr/bin/env bash
# usage: run-quorum.sh ARM SCENARIO REPS   (ARM: dev | spinout)
set -euo pipefail
EVALS=/Users/jesse/git/superpowers/superpowers/evals
CAMP=/Users/jesse/git/superpowers/superpowers-autoresearch/campaigns/codex-efficiency
ARM=$1; SCEN=$2; REPS=${3:-1}
cd "$EVALS"
for r in $(seq 1 "$REPS"); do
  scripts/evals-container exec quorum run "$CAMP/scenarios/$SCEN" \
    --coding-agent codex \
    --out-root "results/cx-eff-$SCEN-$ARM-rep$r"
done
```
Note: verify `quorum run` accepts an absolute scenario path from inside the container — the campaign dir must be visible in-container. It is NOT mounted by default; so instead copy `campaigns/codex-efficiency/scenarios/*` into `$EVALS/scenarios/` prefixed `cx-` at run time (rsync in the script) and run `quorum run scenarios/cx-sdd-small`. Keep `$EVALS/scenarios/cx-*` out of the evals repo's git (they're gitignored? if not, add to `.git/info/exclude` in the evals checkout — do NOT commit to superpowers-evals).

- [ ] **Step 4: Prepare the two arms**

```bash
cd /Users/jesse/git/superpowers/superpowers
git worktree add /tmp/sp-arm-dev origin/dev
git worktree add /tmp/sp-arm-spinout origin/codex-spinout-fixes
```
Arm selection = container re-up: `scripts/evals-container down && scripts/evals-container --superpowers-root /tmp/sp-arm-$ARM up` (pattern from `harnesses/quorum-container-variants.sh`). Put this in `run-quorum.sh` keyed on ARM.

- [ ] **Step 5: Smoke run**

```bash
bash campaigns/codex-efficiency/run-quorum.sh dev cx-sdd-small 1
$EVALS/scripts/evals-container exec quorum show results/cx-eff-cx-sdd-small-dev-rep1
```
Expected: run completes (any verdict), and `results/cx-eff-cx-sdd-small-dev-rep1/*/home/.codex/sessions/` contains ≥1 rollout parseable by `rollout_parser`. Fix scenario until true.

- [ ] **Step 6: Commit** (scenario, fixture, script — not results)

```bash
git add campaigns/codex-efficiency/scenarios campaigns/codex-efficiency/fixtures campaigns/codex-efficiency/run-quorum.sh
git commit -m "campaign(codex-efficiency): sdd-small scenario + quorum runner + arm worktrees"
```

---

### Task 6: E1 fork hygiene — scorer, baseline battery, spinout treatment, verdict

**Files:**
- Create: `campaigns/codex-efficiency/score_e1.py`
- Create: `campaigns/codex-efficiency/out/e1-report.md`

**Interfaces:**
- Consumes: `extract_spawns`, `child_links`, `parse_session`; run dirs from Task 5.
- Produces: `score_e1.py RUNDIR...` → per-run and aggregate table: spawns, %`fork_turns=="none"`, %explicit model, per-child (bytes, `first_instruction_line`, `skill_reads_strict`); exits 0.

- [ ] **Step 1: Write `score_e1.py`**

For each run dir: root rollout = the earliest rollout under `home/.codex/sessions/**`; spawns from every rollout (controller may be any depth); children resolved via `child_links` + matching rollout filenames containing the child thread UUID. Emit a markdown table and a JSON blob (`out/e1-<label>.json`) of raw tuples.

- [ ] **Step 2: Baseline battery (4 reps, dev arm)** — `bash run-quorum.sh dev cx-sdd-small 4`

- [ ] **Step 3: Score + check discrimination**

`python3 score_e1.py $EVALS/results/cx-eff-cx-sdd-small-dev-rep*/*`. Manually inspect every spawn tuple (there will be <40). Discrimination gate: baseline must show non-isolated or model-omitted spawns (registered prediction). If it does not, STOP E1, record inconclusive-by-zero in the log, and re-plan with Jesse.

- [ ] **Step 4: Treatment battery (4 reps, spinout arm)** — `bash run-quorum.sh spinout cx-sdd-small 4`, score identically.

- [ ] **Step 5: Verdict + budget ledger**

Write `out/e1-report.md` (aggregate tables both arms, success-criterion check: 100% isolated + 100% explicit model + completion parity). Append verdict + `quorum costs` dollars + sub used_percent delta to hypothesis log. Commit all (not raw results):

```bash
git add campaigns/codex-efficiency/score_e1.py campaigns/codex-efficiency/out/e1-report.md logs/2026-07-28-codex-efficiency.md
git commit -m "campaign(codex-efficiency): E1 fork-hygiene verdict (baseline vs codex-spinout-fixes)"
```

---

### Task 7: E2 micro — reviewer non-delegation phrasing sweep (codex exec)

**Files:**
- Create: `campaigns/codex-efficiency/reviewer-recursion-micro.py`
- Create: `campaigns/codex-efficiency/out/e2-micro.md`

**Interfaces:**
- Consumes: the in-container `codex exec` pattern — copy the subprocess scaffold (throwaway `CODEX_HOME`, auth.json copy, container exec) from `harnesses/codex-read-delivery-micro.py`; `extract_spawns` for scoring.
- Produces: per-variant spawn rate table.

- [ ] **Step 1: Write the micro**

Variants (dict like `dispatch-composition-micro.py`): `A-control` = the current SDD code-review dispatch text from the dev skill (read it from `/tmp/sp-arm-dev/skills/subagent-driven-development/` at runtime — copy the reviewer dispatch template verbatim); `B-contract` = A + "You personally perform this review. Do not spawn, delegate to, or wait on any other agent; produce findings directly."; `C-budget` = A + "Hard budget: 0 subagents. Any delegation is a protocol violation reported as failure."; `Z-null` = review request with no dispatch guidance (negative control). Fixture: tiny repo + a 60-line diff containing one seeded bug (off-by-one in a loop bound). Each sample: `codex exec` the review prompt in a fresh throwaway home; REPS=5 per variant (cache per (variant, rep) like the existing micros). Score: per-sample `len(extract_spawns(rollout)) > 0`, plus whether the seeded bug is named in the answer file (findings-quality guard).

- [ ] **Step 2: Run** — `python3 reviewer-recursion-micro.py` (env: `REPS=5`).

- [ ] **Step 3: Report + log**

`out/e2-micro.md`: spawn-rate and bug-found-rate per variant. Manually read 3 answer files per variant. Append to hypothesis log (this informs the future treatment; verdict language: which phrasing eliminates delegation without losing the seeded bug). Commit.

---

### Task 8: E2 FULL — branch-review baseline + subtree scorer

**Files:**
- Create: `campaigns/codex-efficiency/scenarios/cx-branch-review/{story.md,setup.sh,checks.sh}`
- Create: `campaigns/codex-efficiency/fixtures/branch-review/` (repo with a reviewable feature branch)
- Create: `campaigns/codex-efficiency/score_e2.py`

**Interfaces:**
- Consumes: Task 5 runner and arm mechanism; parser.
- Produces: subtree census per run: total sessions, max depth (walk `child_links` transitively across rollout files), sessions missing `task_complete`, wait calls, spawns-by-nonroot.

- [ ] **Step 1: Build fixture** — reuse `fixtures/sdd-small` completed state: run the dev arm once through the plan manually via `codex exec` OR (cheaper) hand-author the 3-task implementation as commits on a `feature` branch with 2 seeded review-findable issues (a missing edge-case test and a docstring/behavior mismatch). Hand-authoring is acceptable here (the branch is the *input* to review, not skill output).

- [ ] **Step 2: Scenario** — Gauntlet types: *"Please do a final review of the feature branch using your superpowers review skills before we merge."* `quorum_max_time: 20m`.

- [ ] **Step 3: `score_e2.py`** — walk all rollouts in run `home/.codex/sessions`, build the spawn tree from every session's `child_links`, compute census fields above; assert root reviewer identity = session whose first instruction contains the review request.

- [ ] **Step 4: Baseline battery, 4 reps, dev arm** — run, score, manually inspect the tree of the worst rep. Discrimination gate as registered (≥1 descendant in ≥2/4 reps); if baseline never delegates, record inconclusive-by-zero and stop E2.

- [ ] **Step 5: Report `out/e2-report.md`, log verdict + costs, commit.**

---

### Task 9: E6 compaction recovery — forcing rig, scorer, baseline

**Files:**
- Create: `campaigns/codex-efficiency/scenarios/cx-compaction/{story.md,setup.sh,checks.sh}`
- Create: `campaigns/codex-efficiency/score_e6.py`

**Interfaces:**
- Consumes: parser (`compactions`, `skill_reads_strict`, `extract_spawns` timestamps vs compaction timestamps).
- Produces: per-run: compaction count; skill re-reads after first compaction of files already read before it; spawn-tuple quality before vs after compaction.

- [ ] **Step 1: Investigate compaction forcing (timebox: exploratory)**

In-container: `codex exec --help` and Codex config docs (`codex config --help` / config.toml keys; check `turn_context.model_context_window` overridability). Preferred: a config knob shrinking the context window. Fallback: `setup.sh` generates 8 files of ~200KB dense text and `story.md` has the Gauntlet ask the agent to read and summarize each file in sequence before dispatching the next plan task — calibrate file count until ≥1 `compacted` record appears reliably (use 2 calibration runs; these are cheap adhoc runs). Record the chosen mechanism in DESIGN.md.

- [ ] **Step 2: Scenario** — `cx-compaction`: sdd-small plan execution + the padding-read protocol between tasks (or the config knob). Acceptance: run completes with ≥1 compaction.

- [ ] **Step 3: `score_e6.py`** — timeline analysis per session: partition events at the first `context_compacted` marker; report (a) SKILL.md paths read both before AND after (the re-read set), (b) spawn tuples before vs after (fork_turns/model explicitness), (c) controller `user_messages`/`lines` growth.

- [ ] **Step 4: Baseline 3 reps dev arm; also score Task 6's spinout-arm runs with `score_e6.py`** (the compaction hook lives on that branch — its runs may already contain compactions; if none, run 2 spinout reps of `cx-compaction`).

- [ ] **Step 5: Discrimination gate (re-reads present in baseline), report `out/e6-report.md`, log, commit.**

---

### Task 10: E3 evidence receipts — duplicate-gate scorer, finishing scenario, invalidation probe

**Files:**
- Create: `campaigns/codex-efficiency/scenarios/cx-finishing/{story.md,setup.sh,checks.sh}`
- Create: `campaigns/codex-efficiency/score_e3.py`

**Interfaces:**
- Consumes: `exec_commands`, test-command classifier, `patch_apply_end` events (parser `patch_applies` + a new tiny helper `mutation_events(path) -> list[timestamp]` returning timestamps of successful patch applies and of exec cmds matching `\bgit (commit|merge|rebase|reset|checkout)\b` — add with a unit test).
- Produces: duplicate-gate report: pairs of identical normalized test commands (strip whitespace runs) across ALL sessions of a run with zero mutation events between them (merged event timeline across sessions, sorted by timestamp).

- [ ] **Step 1: Add `mutation_events` to parser (TDD: one fixture test), commit.**

- [ ] **Step 2: Scenario `cx-finishing`** — sdd-small fixture with the plan's 3 tasks ALREADY implemented as commits on a feature branch (reuse Task 8 fixture branch minus seeded issues) plus passing tests. Gauntlet types: *"The implementation is done and tests pass. Please verify completion and finish this development branch."* — driving verification-before-completion + finishing-a-development-branch. `quorum_max_time: 15m`.

- [ ] **Step 3: Baseline 4 reps dev arm; score.** Discrimination gate: ≥1 duplicate identical-state full-suite pair in ≥2/4 reps. Manually verify each flagged pair really had no intervening mutation (print the between-events window).

- [ ] **Step 4: Invalidation probe (correctness guard for FUTURE treatments):** document in `out/e3-report.md` the probe design — same scenario but Gauntlet introduces one edit after the first suite run ("please also fix this typo in README, then finish") and the scorer asserts the suite reruns after the mutation. Run it once on dev (expected: rerun happens — dev should PASS this probe; it becomes the regression guard when receipts land).

- [ ] **Step 5: Report, log verdict + costs, commit.**

---

### Task 11: E4 proportional ceremony — census scorer, three task classes, micro path-choice

**Files:**
- Create: `campaigns/codex-efficiency/scenarios/cx-ceremony-{spike,bounded,arch}/{story.md,setup.sh,checks.sh}` (three scenarios, shared setup fixture `fixtures/ceremony/` — an existing small working Flask-less stdlib HTTP JSON service with tests)
- Create: `campaigns/codex-efficiency/score_e4.py`
- Create: `campaigns/codex-efficiency/ceremony-path-micro.py`

**Interfaces:**
- Consumes: parser; `patch_apply_end` changes paths.
- Produces: census per run: user turns before first non-doc patch, docs written under `docs/` before first non-doc patch, total tool calls before first non-doc patch, wall-clock to first non-doc patch.

- [ ] **Step 1: Three story briefs** — spike: *"Can we detect whether the service's port is already in use before binding? Not sure it's possible portably — find out, quick and dirty is fine."*; bounded: *"Add a `--quiet` flag that suppresses request logging. The logging call sites are in server.py."*; arch: *"We need to split the service into a reusable library + thin CLI so another team can embed it."* Gauntlet persona: cooperative, answers questions tersely, never volunteers process preferences.

- [ ] **Step 2: `score_e4.py`** — census fields above from merged rollout timeline; "non-doc patch" = `patch_apply_end.changes` containing a path not under `docs/` and not `*.md`.

- [ ] **Step 3: Baseline: 3 reps × 3 classes, dev arm; score.** Discrimination gate: spike-class census within 25% of arch-class census (ceremony NOT proportional). 

- [ ] **Step 4: `ceremony-path-micro.py`** — Anthropic Messages API micro (copy scaffold from `harnesses/dispatch-composition-micro.py`; MODEL default `claude-opus-4-8`): variants of a hypothetical entry-decision paragraph for brainstorming (A-current: verbatim current hard-gate text; B-three-path: spike/bounded/architectural router; Z-null); task inputs = the three briefs; score = which path the model chooses (classify via regex on a forced one-word answer format). 5 reps. This pre-tests treatment phrasing only; no skill edits in this campaign.

- [ ] **Step 5: Report `out/e4-report.md`, log, commit.**

---

### Task 12: E5 review scope — seeded-defect fixture, recall-by-scope scorer, baseline

**Files:**
- Create: `campaigns/codex-efficiency/fixtures/scope-defects/` (repo + feature branch with 4 planted defects)
- Create: `campaigns/codex-efficiency/scenarios/cx-scope-review/{story.md,setup.sh,checks.sh}`
- Create: `campaigns/codex-efficiency/score_e5.py`
- Create: `campaigns/codex-efficiency/out/e5-defect-key.md` (the answer key)

**Interfaces:**
- Consumes: runner, parser; Gauntlet result files (`gauntlet-agent/results/<runId>/result.md`) and coding-agent workdir for review reports.
- Produces: recall matrix (defect × caught-by-which-review-pass) + accretion counts (commits after first completion claim).

- [ ] **Step 1: Build the fixture** — small two-module Python project (queue producer + consumer w/ threading), feature branch adding a batch API across 3 commits. Plant: D1 local bug (wrong default in new function, unit-testable); D2 cross-task race (consumer reads shared list without the lock the producer uses); D3 clean-checkout break (new module imports a package present in the repo venv notes but missing from `pyproject.toml` deps); D4 is created live: the scenario has the Gauntlet request one repair mid-session ("D1's fix broke the default-path test" — i.e. D4 = whatever regression the repair introduces; scorer treats "findings-scoped re-review examined only the repair diff" as the D4 measure). Write `out/e5-defect-key.md` with exact file:line and detection rubric (keyword sets per defect).

- [ ] **Step 2: Scenario** — Gauntlet: *"Please run your full review process on the feature branch and get it ready to merge."*; after first completion claim, Gauntlet reports D1's symptom and asks for a fix, then accepts. `quorum_max_time: 30m`.

- [ ] **Step 3: `score_e5.py`** — search all review artifacts (reports in workdir + final messages in rollouts via `task_complete.last_agent_message`) for each defect's rubric keywords; classify which review pass (task/branch/fix-review — identify by the dispatch text in the reviewer session's first instruction) caught it; count same-scope duplicate review sessions; count commits after the first completion-claim timestamp. EVERY rubric match is manually verified (print matching context).

- [ ] **Step 4: Baseline 3 reps dev arm** (most expensive battery — check budget ledger headroom first; if Anthropic spend > $700 cumulative, cut to 2 reps). Discrimination gate: ≥1 of D2/D3 missed-or-misattributed OR same-scope duplicates present.

- [ ] **Step 5: Report `out/e5-report.md`, log verdict + costs, commit.**

---

### Task 13: Campaign closeout — report, promotion, budget

**Files:**
- Create: `reports/2026-07-codex-efficiency-campaign.md`
- Modify: `logs/2026-07-28-codex-efficiency.md` (final ledger)

**Interfaces:**
- Consumes: all `out/e*-report.md` + hypothesis log.

- [ ] **Step 1: Write the campaign report** — per experiment: registered prediction vs observed, discrimination status, baseline pathology numbers, E1 treatment verdict, total spend (dollars + subscription percent), and the ranked recommendation update for the fix cycles (which spec success-criteria are now enforceable by which scorer).

- [ ] **Step 2: Promotion** — copy durable experiment write-ups into the superpowers-evals checkout convention `docs/experiments/` — but DO NOT push/PR to superpowers-evals without Jesse's explicit merge confirmation; stage the files and note them in the report instead.

- [ ] **Step 3: Final commit; present summary + diff-stat of the whole campaign to Jesse.**

---

## Self-Review (done at planning time)

- Spec coverage: E1→Task 6, E2→Tasks 7–8, E3→Task 10, E4→Task 11, E5→Task 12, E6→Task 9; shared parser→Tasks 2–4; discrimination + budget + no-raw-rollouts rules are Global Constraints; ordering matches spec (parser → E1/E2 → E6 → E3 → E4 → E5).
- Known deviations from spec text: none material. Spec's "MICRO for E2" is a codex-exec micro (Task 7) not an Anthropic-API micro — matches spec intent (observe real spawn behavior).
- Type consistency: `Spawn`, `ExecCmd`, `SessionMetrics`, `child_links` signatures used identically across Tasks 2–12.
- Open risk carried: `quorum run` scenario-path visibility inside the container (Task 5 Step 3 carries the rsync fallback); compaction forcing (Task 9 Step 1 is explicitly exploratory with fallback).

---

## Amendment 1 (2026-07-28, post-Task-6, Jesse-approved)

Three scope changes, each grounded in evidence that arrived mid-campaign:

### Task 6b: Container Codex CLI upgrade + E1 axis-A re-test

The eval container pins `@openai/codex@0.144.4`; the field (audit corpus, Drew's
runs) is on 0.146, and the spinout branch's `model`/`reasoning_effort` spawn
params require ≥0.145. Every remaining Codex battery must run on the field
version. Steps: bump the version in `evals/container/Dockerfile` (local change
in the evals checkout; do not push), `scripts/evals-container build` + re-up,
verify `session_meta.cli_version` ≥0.145 in a fresh run, then re-run E1: 2
baseline reps on dev (does fork_turns stay 100% "none" at 0.146? — CLI version
is now a registered confound for the Task 6 baseline result) + 4 treatment reps
on spinout scored on axis A. Budget ≈ $32.

### Tasks E7–E9: Drew-derived MINE-tier scorers (no new run spend)

- **E7 wait-polling**: parser gains wait-call outcome pairing (call → its
  function_call_output; timeout detection from output text); scorer reports
  poll counts, timeout rate, inter-poll interval. Pre-registered priors from
  Drew: 78% timeout rate on the stress run's 805 polls; audit: 788/1058 on one
  root.
- **E8 close_agent hygiene**: per-controller census of spawned vs closed
  children (close_agent calls; also followup/interrupt). Priors: Drew sol
  0/86 closed; codex-5.5 18/18.
- **E9 workspace leaks**: scorer over run workdir git history — any
  `.superpowers/sdd/` path ever committed (git log --all --diff-filter=A),
  plus workspace-in-diff at review packages. Priors: 3 leak runs in Drew's
  fractals set.

Each scores three corpora: Drew's (external), the audit corpus, our battery
runs. Validation follows the standing rules (manual inspection before verdicts).

### Task: Drew-corpus cross-validation and evidence ingestion

Run rollout_parser + E1/E2 scorers over Drew's Codex rollouts
(`/Users/jesse/git/superpowers/_tmp/drew-sdd-head-to-head-2026-07-27`,
external, never committed); reconcile against his script-emitted metrics;
register his treatment-arm evidence (103/103 dispatch tuples at 0.146,
reviewer no-recursion 0/53, compaction hook 18/18 with compliant-controller
caveat) in the hypothesis log as external evidence with provenance.

Ordering: 6b first (container down for rebuild blocks all quorum work), then
Drew cross-validation, then E7–E9, then resume the original sequence at Task 7
(E2 micro).
