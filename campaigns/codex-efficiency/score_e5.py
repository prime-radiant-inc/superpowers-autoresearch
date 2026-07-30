#!/usr/bin/env python3
"""E5 review-scope / seeded-defect recall scorer (Task 12).

For each RUNDIR (a single quorum run's coding-agent directory, i.e. the
directory containing `home/.codex/sessions/**` and `verdict.json` -- one
level below a `results/cx-eff-<scenario>-<arm>-repN/` battery dir), this
scores `cx-scope-review`'s seeded-defect battery against
`out/e5-defect-key.md`'s three planted defects (D1 local bug, D2 cross-
commit race, D3 clean-checkout break) plus the fourth, live-emerging one
(D4, scored structurally, not by keyword).

Five questions, per DESIGN.md's E5 package and Amendment 3's upgrade:

  1. **Recall matrix** (defect x which review pass caught it). Every
     session's own relayed text -- `task_complete.last_agent_message`
     (rollout_parser doesn't expose this directly as a dataclass field,
     so it's read here via the same event_msg/task_complete marker) AND
     `event_msg/agent_message` records (`rollout_parser.final_answers()`,
     phase=="final_answer") -- is searched for each defect's rubric
     keywords (`rubric_hit()`). A hit is attributed to a review PASS:
     for the ROOT session (which receives both the initial review
     request and, later, the mid-session repair request in the SAME
     rollout), pre-repair-request-timestamp hits are "review" and
     post-repair-request-timestamp hits are "fix_review"
     (`find_repair_request_timestamp()` locates the split point by the
     Gauntlet's own fixed repair-request text, scenarios/cx-scope-review/
     story.md's second scripted message -- our own scenario prompt text,
     not corpus content, same "fixed Gauntlet prompt is citable process
     text" precedent score_e2.py's `_root_matches_review_request` already
     established). For a DISPATCHED session, the pass is classified by
     its own PARENT-assigned task_name (`classify_pass_by_task_name()`),
     not by timestamp.
  2. **Scope accretion**: commits (specifically `git commit`, not every
     mutation_events() kind -- DESIGN.md's E5 package asks for
     "post-completion commits") strictly after the run's first
     `task_complete` timestamp (the first completion claim, root or
     otherwise -- whichever comes first tree-wide).
  3. **Same-scope duplicate review** (Amendment 3, reusing
     `score_e6.task_family()` unmodified, same as E6's own same-task-
     duplicate-review census): 2+ dispatched (non-root) sessions whose
     task_name reduces to the same family are flagged.
  4. **Serial-remediation cycles** (Amendment 3): count of test-command
     invocations (score_e3.test_command_events(), reused) strictly after
     the repair-request timestamp, minus 1 (each additional post-repair
     test run beyond the first is another discover/fix/re-verify round;
     clamped at 0, and 0 whenever there's no repair request or fewer
     than 2 post-repair test runs).
  5. **Wave-boundary violation** (Amendment 3): a `mutation_events()`
     (reused unmodified) timestamp, attributed to a session OTHER than
     the fix-review session itself (or the fix-review's own
     descendants), falling strictly within the fix-review session's own
     [start, task_complete] window -- the tree mutating out from under
     an active re-review.
  6. **D4 fix-review scope** (the live-emerging defect -- no keyword
     rubric, see out/e5-defect-key.md): whether any post-repair test
     command names no specific file (a whole-suite rerun, consistent
     with re-scoping to the whole branch) or every post-repair test
     command targets a specific file (consistent with examining only
     the repair's own diff) -- `fix_review_scope()`, one of
     "no_repair_request" | "no_post_repair_test_run" | "repair_scoped" |
     "full_branch_rescope". A coarse, purely structural proxy -- the
     campaign's standing discipline (manual verification before any
     verdict) applies here more than anywhere else in this file, since
     D4's actual content is never known until the battery runs.

PRIVACY: rubric_hit()/matching_context() only ever operate on and quote
THIS campaign's own scenario/battery output (Gauntlet-scripted prompts,
this fixture's own seeded defects, and the coding agent's own relayed
review text in response to them) -- never external/private corpus
content. This is the same distinction score_e3.py's module docstring and
this campaign's Drew/07-29-corpus handling draw throughout: quoting our
own fixture-derived text is fine; quoting a real private corpus's
content never is.

Usage:
    score_e5.py RUNDIR...

Prints a markdown report (per-run census + recall/accretion/duplicate/
remediation/wave-boundary tables, then an aggregate across all given
RUNDIRs) to stdout, and writes a JSON blob to
campaigns/codex-efficiency/out/e5-<label>.json (label convention
identical to score_e1.py/score_e2.py/score_e3.py/score_e6.py). Refuses
to overwrite an existing output file unless env FORCE=1 is set. Exits 0
on success, 1 on usage error, an existing-output-file collision without
FORCE, or a run with zero resolvable rollouts.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp
import score_e2 as e2
import score_e3 as e3
import score_e6 as e6

REP_DIR_RE = re.compile(r"^cx-eff-(?P<arm_scenario>.+)-rep(?P<rep>\d+)$")

# The Gauntlet's own SECOND scripted message (scenarios/cx-scope-review/
# story.md) -- fixed process text, not corpus content (same precedent as
# score_e2.REVIEW_REQUEST_MARKER). A short, still-distinctive substring
# of it is enough to locate the timestamp; the full text isn't needed as
# a marker.
REPAIR_REQUEST_MARKER = "only gave me back 1 item instead of the 5"

# --- D1/D2/D3 rubric keyword sets (out/e5-defect-key.md's own rubric,
# reproduced here as the actual matcher -- see that file for the
# rationale per defect and the crisp/greppable-over-subtle design
# principle behind each set, the direct lesson from Task 8's E2-FULL
# 0/4 coverage-gap-seed result). Each defect is a HIT if ANY ONE of its
# listed regexes matches (case-insensitive) -- matching the defect key's
# "any ONE is a hit" framing exactly.
DEFECT_RUBRICS = {
    "D1": [
        re.compile(r"DEFAULT_BATCH_SIZE", re.I),
        re.compile(r"drain_batch", re.I),
        re.compile(r"test_drain_batch_default_pulls_documented_batch_size", re.I),
    ],
    "D2": [
        re.compile(r"peek_batch.{0,80}(lock|race|thread.?safe|unsynchroniz)", re.I | re.S),
        re.compile(r"(lock|race|thread.?safe|unsynchroniz).{0,80}peek_batch", re.I | re.S),
        re.compile(r"self\._items.{0,40}(without|outside).{0,20}lock", re.I | re.S),
        re.compile(r"(without|outside).{0,20}lock.{0,40}self\._items", re.I | re.S),
    ],
    "D3": [
        re.compile(r"msgpack.{0,80}(pyproject|dependen|requirement|missing|undeclared)", re.I | re.S),
        re.compile(r"(pyproject|dependen|requirement|missing|undeclared).{0,80}msgpack", re.I | re.S),
        re.compile(r"ModuleNotFoundError", re.I),
        re.compile(r"No module named", re.I),
        re.compile(r"batch_codec.{0,60}(clean checkout|clean install|fresh venv|missing package)", re.I | re.S),
    ],
}


def rubric_hit(defect, text):
    """True if TEXT matches any of DEFECT's rubric regexes. `defect` is
    one of "D1"/"D2"/"D3" (D4 has no keyword rubric -- see module
    docstring and out/e5-defect-key.md)."""
    if not text:
        return False
    return any(rx.search(text) for rx in DEFECT_RUBRICS[defect])


def classify_pass_by_task_name(task_name):
    """Which review PASS a dispatched session's own task_name (assigned
    by its parent) indicates: "fix_review" (repair/fix-scoped),
    "branch_review" (whole-branch-scoped), "task_review" (single-
    commit/task-scoped), or "unclassified". Checked in that priority
    order since a real task_name could plausibly combine words (e.g.
    "fix_branch_review" -- a fix-scoped pass, checked first)."""
    if task_name in (None, rp.OMIT):
        return "unclassified"
    if re.search(r"fix|repair", task_name, re.I):
        return "fix_review"
    if re.search(r"branch", task_name, re.I):
        return "branch_review"
    if re.search(r"task|commit", task_name, re.I):
        return "task_review"
    return "unclassified"


def find_rollouts(rundir):
    pattern = os.path.join(rundir, "home", ".codex", "sessions", "**", "*.jsonl")
    return sorted(glob.glob(pattern, recursive=True))


def _parent_label(rundir):
    """Identical convention to score_e1.py/score_e2.py/score_e3.py/
    score_e6.py's helper of the same name."""
    parent = os.path.basename(os.path.dirname(os.path.abspath(rundir.rstrip("/"))))
    m = REP_DIR_RE.match(parent)
    if m:
        return m.group("arm_scenario"), int(m.group("rep"))
    return parent, None


def find_repair_request_timestamp(rollouts):
    """Earliest event_msg/user_message timestamp, across ALL rollouts,
    whose message text contains REPAIR_REQUEST_MARKER. None if never
    found. Same shape as score_e3.find_waiver_timestamp(), specialized
    to this scenario's fixed marker (no env-configurability needed --
    unlike E3's waiver marker, this scenario's repair-request text is
    fixed, not battery-specific)."""
    needle = REPAIR_REQUEST_MARKER.lower()
    hits = []
    for path in rollouts:
        for ts, typ, p in rp.iter_records(path):
            if typ == "event_msg" and p.get("type") == "user_message":
                msg = p.get("message")
                if isinstance(msg, str) and needle in msg.lower():
                    hits.append(ts)
    return min(hits) if hits else None


def _task_complete_events(path):
    """Every event_msg/task_complete record's (timestamp,
    last_agent_message), in file order. rollout_parser has no dedicated
    dataclass for this (parse_session() only counts it), so read
    directly here -- same precedent as score_e3.py's own small
    self-contained additions rather than growing rollout_parser for a
    single caller."""
    out = []
    for ts, typ, p in rp.iter_records(path):
        if typ == "event_msg" and p.get("type") == "task_complete":
            out.append((ts, p.get("last_agent_message", "")))
    return out


def _searchable_texts(path):
    """Every piece of THIS session's own relayed text worth rubric-
    matching, each tagged with its timestamp: every
    task_complete.last_agent_message plus every final_answers()
    phase=="final_answer" message. Order-preserving, not deduplicated
    (a defect could legitimately be re-stated at both markers)."""
    texts = [(ts, msg) for ts, msg in _task_complete_events(path) if msg]
    texts += [(fa.timestamp, fa.message) for fa in rp.final_answers(path)
              if fa.phase == "final_answer" and fa.message]
    return texts


def _pass_for_hit(node, ts, repair_ts):
    """Which review pass a hit at timestamp TS (in session NODE) belongs
    to: a dispatched (non-root) node is classified by its own task_name;
    the root is classified by TS relative to repair_ts (no repair
    request yet resolved to "review" -- root has no other pass to be)."""
    if not node["is_root"]:
        pass_label = classify_pass_by_task_name(node.get("task_name"))
        if pass_label != "unclassified":
            return pass_label
    if repair_ts is not None and ts >= repair_ts:
        return "fix_review"
    return "review"


def build_recall_matrix(nodes, path_by_basename, repair_ts):
    matrix = {"D1": [], "D2": [], "D3": []}
    for node in nodes:
        path = path_by_basename[node["rollout"]]
        for ts, text in _searchable_texts(path):
            for defect in matrix:
                if rubric_hit(defect, text):
                    matrix[defect].append({
                        "rollout": node["rollout"],
                        "timestamp": ts,
                        "pass": _pass_for_hit(node, ts, repair_ts),
                        "matched_text": text,
                    })
    return matrix


GIT_COMMIT_RE = re.compile(r"\bgit commit\b")


def _git_commit_events(rollouts):
    """Every `git commit` exec-command timestamp across ALL rollouts,
    merged and sorted -- narrower than rollout_parser.mutation_events()
    (which also counts merge/rebase/reset/checkout and successful patch
    applies): DESIGN.md's E5 package specifically asks for
    "post-completion commits", not every kind of mutation.

    Matches GIT_COMMIT_RE against the DE-ESCAPED command text
    (rp.deescape_custom_exec(), Task 10 fix round 1) -- this function
    calls rp.exec_commands() directly with its own regex, the same
    shape of call site rollout_parser.mutation_events() needed the fix
    for: a custom_exec command's raw JS-source `input` can carry a
    literal two-character backslash-n that defeats GIT_COMMIT_RE's
    leading \\b if left un-deescaped, silently dropping a real commit."""
    events = []
    for path in rollouts:
        for ec in rp.exec_commands(path):
            if GIT_COMMIT_RE.search(rp.deescape_custom_exec(ec.cmd, ec.encoding)):
                events.append(ec.timestamp)
    return sorted(events)


def scope_accretion(rollouts):
    """First task_complete timestamp tree-wide (the first completion
    claim, root or otherwise) and the count of `git commit` events
    strictly after it."""
    first_ts = None
    for path in rollouts:
        for ts, _ in _task_complete_events(path):
            if first_ts is None or ts < first_ts:
                first_ts = ts
    if first_ts is None:
        return {"first_completion_timestamp": None, "n_commits_after": 0}
    commits = _git_commit_events(rollouts)
    n_after = sum(1 for ts in commits if ts > first_ts)
    return {"first_completion_timestamp": first_ts, "n_commits_after": n_after}


def same_scope_duplicates(nodes):
    """2+ dispatched (non-root) REVIEWER sessions (role classified by
    score_e6.classify_role_by_task_name(), reused unmodified) whose
    task_name reduces to the SAME score_e6.task_family() family are
    flagged as a same-scope duplicate review. Scoped to reviewer-role
    sessions only -- an ordinary task1_implementer + task1_reviewer pair
    shares family "task1" but is the NORMAL single-review SDD shape, not
    a duplicate; only 2+ REVIEWER dispatches of the same family are a
    genuine same-scope duplicate (same grouping+role split E6's own
    duplicate_review_families census uses)."""
    by_family = {}
    for node in nodes:
        if node["is_root"]:
            continue
        if e6.classify_role_by_task_name(node.get("task_name")) != "reviewer":
            continue
        fam = e6.task_family(node.get("task_name"))
        if fam is None:
            continue
        by_family.setdefault(fam, []).append(node["rollout"])
    return [{"family": fam, "rollouts": sorted(rollouts)}
            for fam, rollouts in sorted(by_family.items()) if len(rollouts) > 1]


def serial_remediation_cycles(rollouts, repair_ts):
    """Count of test-command invocations (score_e3.test_command_events(),
    reused unmodified) strictly after repair_ts, minus 1 (each ADDITIONAL
    post-repair test run beyond the first re-verification is another
    discover/fix/re-verify round), clamped at 0. 0 when there's no
    repair request at all."""
    if repair_ts is None:
        return 0
    n_post = 0
    for path in rollouts:
        for ev in e3.test_command_events(path):
            if ev["timestamp"] > repair_ts:
                n_post += 1
    return max(0, n_post - 1)


# A post-repair test command that names no specific `.py` file is a
# whole-suite rerun ("pytest", "pytest tests/", "python -m pytest tests")
# -- re-verifying the WHOLE branch, not just the repair. Anything that
# names a specific test file is scoped to (at most) that file.
WHOLE_SUITE_TEST_RE = re.compile(r"\.py\b")


def fix_review_scope(rollouts, repair_ts):
    """D4 (the live-emerging defect, no keyword rubric -- see
    out/e5-defect-key.md) is scored structurally: does the post-repair
    re-review run only file-scoped tests (consistent with examining just
    the repair's own diff), or does at least one post-repair test
    command re-run the whole suite with no specific file target
    (consistent with re-scoping to the whole branch)? Returns one of
    "no_repair_request" | "no_post_repair_test_run" | "repair_scoped" |
    "full_branch_rescope"."""
    if repair_ts is None:
        return "no_repair_request"
    post_repair_cmds = []
    for path in rollouts:
        for ev in e3.test_command_events(path):
            if ev["timestamp"] > repair_ts:
                post_repair_cmds.append(ev["cmd_norm"])
    if not post_repair_cmds:
        return "no_post_repair_test_run"
    if any(not WHOLE_SUITE_TEST_RE.search(cmd) for cmd in post_repair_cmds):
        return "full_branch_rescope"
    return "repair_scoped"


def wave_boundary_violations(nodes, path_by_basename, repair_ts):
    """For every session classified as a "fix_review" pass (a dispatched
    fix-scoped reviewer, or the root itself acting post-repair),
    find its own active-lifetime window [start, task_complete] and flag
    any rollout_parser.mutation_events() timestamp inside that window
    that belongs to a DIFFERENT session which is not that fix-review's
    own descendant -- the tree mutating out from under an active
    re-review."""
    descendants = {}
    for node in nodes:
        descendants.setdefault(node["parent_rollout"], []).append(node["rollout"])

    def _is_descendant(ancestor, candidate):
        stack = list(descendants.get(ancestor, []))
        seen = set()
        while stack:
            r = stack.pop()
            if r == candidate:
                return True
            if r in seen:
                continue
            seen.add(r)
            stack.extend(descendants.get(r, []))
        return False

    violations = []
    for node in nodes:
        if node["is_root"]:
            if repair_ts is None:
                continue
            path = path_by_basename[node["rollout"]]
            window_start = repair_ts
            tcs = [ts for ts, _ in _task_complete_events(path) if ts > repair_ts]
            window_end = min(tcs) if tcs else None
        else:
            pass_label = classify_pass_by_task_name(node.get("task_name"))
            if pass_label != "fix_review":
                continue
            path = path_by_basename[node["rollout"]]
            tcs = sorted(ts for ts, _ in _task_complete_events(path))
            window_start = node.get("dispatch_timestamp")
            window_end = tcs[0] if tcs else None
        if window_end is None:
            continue
        for other in nodes:
            if other["rollout"] == node["rollout"]:
                continue
            if _is_descendant(node["rollout"], other["rollout"]):
                continue
            other_path = path_by_basename[other["rollout"]]
            for ts in rp.mutation_events(other_path):
                if window_start is not None and window_start < ts < window_end:
                    violations.append({
                        "fix_review_rollout": node["rollout"],
                        "mutating_rollout": other["rollout"],
                        "mutation_timestamp": ts,
                    })
    return violations


def matching_context(hit):
    """Content-free-by-default manual-verification helper: returns the
    hit's own already-captured matched_text (our own scenario/fixture
    output -- see module docstring's PRIVACY note) so a caller can print
    it for manual verification without re-reading any rollout."""
    return hit["matched_text"]


def score_tree(root, rollouts, label=None):
    """Core, reusable scoring pass over an already-discovered (root,
    rollouts) pair -- same reuse seam as score_e2.build_tree()/
    score_e3.score_tree()/score_e6.score_tree()."""
    nodes = e2.build_tree(root, rollouts)
    path_by_basename = {os.path.basename(p): p for p in rollouts}
    spawn_info_by_basename = _spawn_info_by_rollout_basename(rollouts)
    for n in nodes:
        task_name, dispatch_ts = spawn_info_by_basename.get(n["rollout"], (None, None))
        n["task_name"] = task_name
        n["dispatch_timestamp"] = dispatch_ts

    repair_ts = find_repair_request_timestamp(rollouts)
    recall_matrix = build_recall_matrix(nodes, path_by_basename, repair_ts)
    accretion = scope_accretion(rollouts)
    duplicates = same_scope_duplicates(nodes)
    cycles = serial_remediation_cycles(rollouts, repair_ts)
    fix_scope = fix_review_scope(rollouts, repair_ts)
    violations = wave_boundary_violations(nodes, path_by_basename, repair_ts)

    return {
        "label": label,
        "root_rollout": os.path.basename(root),
        "total_sessions": len(nodes),
        "max_depth": max((n["depth"] for n in nodes), default=0),
        "repair_request_timestamp": repair_ts,
        "recall_matrix": recall_matrix,
        "recall_summary": {d: sorted({h["pass"] for h in hits}) for d, hits in recall_matrix.items()},
        "scope_accretion": accretion,
        "same_scope_duplicates": duplicates,
        "serial_remediation_cycles": cycles,
        "fix_review_scope": fix_scope,
        "wave_boundary_violations": violations,
        "nodes": nodes,
    }


def _spawn_info_by_rollout_basename(rollouts):
    """Maps each session's own rollout basename to (task_name, timestamp)
    of its PARENT's spawn_agent call -- task_name per score_e6.py's
    helper of the same name; timestamp additionally, needed to bound a
    dispatched fix-review session's active-lifetime window
    (wave_boundary_violations) since a spawned child's own first record
    isn't necessarily at the dispatch instant. One walk instead of two
    separate near-identical ones over the same spawn/child-link data."""
    mapping = {}
    for p in rollouts:
        spawns_by_call_id = {s.call_id: (s.task_name, s.timestamp) for s in rp.extract_spawns(p)}
        for call_id, thread_id in rp.child_links(p).items():
            if call_id not in spawns_by_call_id:
                continue
            child_path = e2._resolve_child_path(thread_id, rollouts)
            if child_path:
                mapping[os.path.basename(child_path)] = spawns_by_call_id[call_id]
    return mapping


def score_run(rundir):
    rundir = rundir.rstrip("/")
    arm_scenario, rep = _parent_label(rundir)
    rollouts = find_rollouts(rundir)
    if not rollouts:
        raise SystemExit(f"score_e5: no rollout files found under {rundir}/home/.codex/sessions/**")
    root = rollouts[0]
    result = score_tree(root, rollouts, label=f"{arm_scenario}-rep{rep}" if rep is not None else arm_scenario)
    result["rundir"] = rundir
    result["arm_scenario"] = arm_scenario
    result["rep"] = rep
    return result


def print_run_report(run):
    label = f"{run['arm_scenario']} rep{run['rep']}" if run["rep"] is not None else run["arm_scenario"]
    print(f"### {label} -- `{run['rundir']}`")
    print()
    print(f"root rollout: `{run['root_rollout']}`  total_sessions={run['total_sessions']}  "
          f"max_depth={run['max_depth']}  repair_request_timestamp={run['repair_request_timestamp']}")
    print()
    print("**Recall matrix (defect -> passes that caught it):**")
    for defect in ("D1", "D2", "D3"):
        hits = run["recall_matrix"][defect]
        passes = run["recall_summary"][defect]
        status = "CAUGHT" if hits else "MISSED"
        print(f"  {defect}: {status}  passes={passes}  n_hits={len(hits)}")
        for h in hits:
            print(f"    [{h['rollout']}@{h['timestamp']}, pass={h['pass']}] {matching_context(h)!r}")
    print()
    acc = run["scope_accretion"]
    print(f"**Scope accretion:** first_completion_timestamp={acc['first_completion_timestamp']}  "
          f"commits_after={acc['n_commits_after']}")
    print()
    if run["same_scope_duplicates"]:
        print(f"**Same-scope duplicate reviews: {len(run['same_scope_duplicates'])}**")
        for d in run["same_scope_duplicates"]:
            print(f"    family={d['family']}  rollouts={d['rollouts']}")
    else:
        print("**Same-scope duplicate reviews: 0**")
    print()
    print(f"**Serial-remediation cycles (post-repair): {run['serial_remediation_cycles']}**")
    print()
    print(f"**D4 fix-review scope: {run['fix_review_scope']}**")
    print()
    if run["wave_boundary_violations"]:
        print(f"**Wave-boundary violations: {len(run['wave_boundary_violations'])}**")
        for v in run["wave_boundary_violations"]:
            print(f"    fix_review={v['fix_review_rollout']}  "
                  f"mutated_by={v['mutating_rollout']}@{v['mutation_timestamp']}")
    else:
        print("**Wave-boundary violations: 0**")
    print()


def _rep_range_suffix(runs):
    """Identical convention to score_e1.py/score_e2.py/score_e3.py/
    score_e6.py's helper of the same name."""
    reps = sorted({r["rep"] for r in runs if r["rep"] is not None})
    if not reps:
        return "unknown-reps"
    if len(reps) == 1:
        return f"rep{reps[0]}"
    return f"rep{reps[0]}-{reps[-1]}"


def _out_label(runs):
    arm_scenarios = sorted({r["arm_scenario"] for r in runs})
    base = arm_scenarios[0] if len(arm_scenarios) == 1 else "mixed-" + "-".join(arm_scenarios)
    return f"{base}-{_rep_range_suffix(runs)}"


def write_output(runs, out_dir, force=False):
    label = _out_label(runs)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"e5-{label}.json")
    if os.path.exists(out_path) and not force:
        print(f"score_e5: refusing to overwrite existing {out_path} "
              f"-- set env FORCE=1 to overwrite", file=sys.stderr)
        return out_path, False
    with open(out_path, "w") as f:
        json.dump({"label": label, "runs": runs}, f, indent=2)
    return out_path, True


def main(argv):
    if len(argv) < 2:
        print("usage: score_e5.py RUNDIR...", file=sys.stderr)
        return 1

    runs = [score_run(rd) for rd in argv[1:]]

    print(f"# E5 review-scope scorer output ({len(runs)} run(s))")
    print()
    for run in runs:
        print_run_report(run)

    print("## Aggregate across all given RUNDIRs")
    print()
    n_runs = len(runs)
    for defect in ("D1", "D2", "D3"):
        n_caught = sum(1 for r in runs if r["recall_matrix"][defect])
        print(f"{defect} caught in {n_caught}/{n_runs} reps")
    n_with_dup = sum(1 for r in runs if r["same_scope_duplicates"])
    n_with_violation = sum(1 for r in runs if r["wave_boundary_violations"])
    print(f"reps with >=1 same-scope duplicate review={n_with_dup}/{n_runs}  "
          f"reps with >=1 wave-boundary violation={n_with_violation}/{n_runs}")
    print(f"total commits_after (scope accretion) across all reps: "
          f"{sum(r['scope_accretion']['n_commits_after'] for r in runs)}")
    print(f"total serial-remediation cycles across all reps: "
          f"{sum(r['serial_remediation_cycles'] for r in runs)}")
    print()

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    force = os.environ.get("FORCE") == "1"
    out_path, wrote = write_output(runs, out_dir, force=force)
    if not wrote:
        return 1
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
