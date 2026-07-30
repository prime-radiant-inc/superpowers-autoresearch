#!/usr/bin/env python3
"""E3 evidence-receipts / duplicate-gate scorer (Task 10).

For each RUNDIR (a single quorum run's coding-agent directory, i.e. the
directory containing `home/.codex/sessions/**` and `verdict.json` -- one
level below a `results/cx-eff-<scenario>-<arm>-repN/` battery dir), this
scores the pathology from Finding 3 / DESIGN.md's E3 package: the same
test command run twice against an UNCHANGED tree -- wasted verification
that no evidence (a patch apply or a git commit/merge/rebase/reset/
checkout) justified.

Three census questions, across ALL sessions of a run (not scoped to the
spawn tree -- the duplicate-gate question spans implementer -> reviewer ->
finishing regardless of parent/child structure):

  1. **Duplicate-gate pairs** (the base E3 package): normalize every
     TEST_INVOCATION_RE-matching exec command (whitespace-collapsed),
     merge ALL sessions' occurrences into one chronological timeline, and
     for each CONSECUTIVE pair of identical-normalized-command occurrences
     count `rollout_parser.mutation_events()` timestamps strictly between
     them (also merged run-wide, via `mutation_timeline()`). Zero
     intervening mutations = `is_duplicate_gate: True` -- the second run
     verified nothing new.
  2. **Per-session identical-command repeat count** (Amendment 3): the
     max/distribution of how many times any ONE session ran the exact
     same normalized command -- the "9x identical cluster" census
     (`out/e-audit0729.md`'s reconciled figure), now per-run instead of
     the audit0729_adapter.py one-off.
  3. **Waiver-violation detection** (Amendment 3): when a Gauntlet/user
     explicitly waives a failing check ("ignore it and proceed"), does
     the SAME command get rerun afterward with zero intervening
     mutation? `find_waiver_timestamp()` locates the waiver by a
     configurable marker substring in any session's user_message text;
     `_waiver_violations()` flags reruns of a command that had already
     run at-or-before that timestamp.

PRIVACY: no function in this module ever returns, prints, or writes the
raw or normalized command TEXT on an output record. Every occurrence is
relabeled to an anonymized per-run `cmd_id` ("cmd1", "cmd2", ... by
first-appearance order) before being exposed in `duplicate_gate_pairs`,
`waiver.violations`, or `events_between()` -- counts, timestamps, and
rollout basenames only, matching this campaign's audit0729_adapter.py
precedent (never print exec command text extracted from a corpus this
scorer doesn't own the content of).

Usage:
    score_e3.py RUNDIR...            (env E3_WAIVER_MARKER optional)

Prints a markdown report (per-run census + duplicate-gate/waiver tables,
then an aggregate across all given RUNDIRs) to stdout, and writes a JSON
blob to campaigns/codex-efficiency/out/e3-<label>.json (label convention
identical to score_e1.py/score_e2.py/score_e6.py). Refuses to overwrite an
existing output file unless env FORCE=1 is set. Exits 0 on success, 1 on
usage error, an existing-output-file collision without FORCE, or a run
with zero resolvable rollouts.
"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp

REP_DIR_RE = re.compile(r"^cx-eff-(?P<arm_scenario>.+)-rep(?P<rep>\d+)$")

# Broader than rollout_parser.TEST_RE (ported from the audit's JS scanner,
# which has no Python `unittest` alternative) -- the same extension
# score_e10.py's TEST_INVOCATION_RE already established for this
# campaign's own sdd-small/strutils-derived fixtures, which invoke
# `python[3] -m unittest ...`. Kept as a small self-contained copy (same
# precedent as score_e6.py's TASK_NAME_REVIEW_RE) rather than a
# cross-scorer import.
TEST_INVOCATION_RE = re.compile(
    r"\b(?:go test|pytest|npm test|pnpm test|bun test|swift test|"
    r"xcodebuild test|make test|vitest|cargo test|python3?\s+-m\s+unittest)\b", re.I)

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_cmd(cmd):
    """Whitespace-collapsed, stripped form of an exec command string --
    the "identical normalized test command" DESIGN.md's E3 package
    specifies (strip whitespace runs)."""
    return _WHITESPACE_RE.sub(" ", cmd).strip()


def test_command_events(path):
    """Every exec command in PATH matching TEST_INVOCATION_RE, as a dict
    with `timestamp`/`call_id`/`cmd_norm`. Both exec_commands() encodings
    are covered (exec_commands() already abstracts them)."""
    out = []
    for ec in rp.exec_commands(path):
        if TEST_INVOCATION_RE.search(ec.cmd):
            out.append({"timestamp": ec.timestamp, "call_id": ec.call_id,
                        "cmd_norm": _normalize_cmd(ec.cmd)})
    return out


def mutation_timeline(rollouts):
    """Every rollout_parser.mutation_events() timestamp across ALL given
    rollouts, merged and sorted (ISO8601 strings sort chronologically)."""
    events = []
    for path in rollouts:
        events.extend(rp.mutation_events(path))
    return sorted(events)


def _all_test_occurrences(rollouts):
    """Every test_command_events() hit across ALL rollouts, each tagged
    with its rollout's basename, sorted by timestamp (ties broken by
    rollout basename for determinism)."""
    occs = []
    for path in rollouts:
        basename = os.path.basename(path)
        for ev in test_command_events(path):
            occs.append({**ev, "rollout": basename})
    occs.sort(key=lambda o: (o["timestamp"], o["rollout"]))
    return occs


def _assign_cmd_ids(occurrences):
    """Mutates each occurrence dict in place, adding a `cmd_id` label
    ("cmd1", "cmd2", ...) assigned by first-appearance order in the
    already-timestamp-sorted `occurrences` list -- the only identifier
    for a distinct normalized command that ever leaves this module's
    internal grouping."""
    ids = {}
    for occ in occurrences:
        norm = occ["cmd_norm"]
        if norm not in ids:
            ids[norm] = f"cmd{len(ids) + 1}"
        occ["cmd_id"] = ids[norm]
    return ids


def _mutations_between(mutations, start_ts, end_ts):
    """Count of mutation timestamps strictly between start_ts and end_ts."""
    return sum(1 for t in mutations if start_ts < t < end_ts)


def _duplicate_gate_pairs(occurrences, mutations):
    """Consecutive same-cmd_id occurrence PAIRS (not all pairwise
    combinations), grouped by cmd_id and sorted by timestamp within each
    group, each annotated with the count of mutation_timeline() events
    strictly between the pair's two timestamps. `is_duplicate_gate` is
    True when that count is zero -- an identical command run twice
    against an unchanged tree."""
    by_cmd = collections.defaultdict(list)
    for occ in occurrences:
        by_cmd[occ["cmd_id"]].append(occ)

    pairs = []
    for cmd_id, occs in by_cmd.items():
        occs = sorted(occs, key=lambda o: o["timestamp"])
        for i in range(len(occs) - 1):
            first, second = occs[i], occs[i + 1]
            n_mut = _mutations_between(mutations, first["timestamp"], second["timestamp"])
            pairs.append({
                "cmd_id": cmd_id,
                "first": {"timestamp": first["timestamp"], "rollout": first["rollout"]},
                "second": {"timestamp": second["timestamp"], "rollout": second["rollout"]},
                "mutations_between": n_mut,
                "is_duplicate_gate": n_mut == 0,
            })
    pairs.sort(key=lambda pr: pr["first"]["timestamp"])
    return pairs


def _per_session_repeat(occurrences):
    """Per-rollout Counter of cmd_id occurrences -> max_repeat +
    n_distinct_commands + n_test_occurrences. Returns (per_session dict
    keyed by rollout basename, run_max_repeat, sorted repeat_distribution
    list of each session's own max)."""
    by_rollout = collections.defaultdict(list)
    for occ in occurrences:
        by_rollout[occ["rollout"]].append(occ["cmd_id"])

    per_session = {}
    for rollout, cmd_ids in by_rollout.items():
        counts = collections.Counter(cmd_ids)
        per_session[rollout] = {
            "max_repeat": max(counts.values()) if counts else 0,
            "n_distinct_commands": len(counts),
            "n_test_occurrences": len(cmd_ids),
        }
    distribution = sorted(s["max_repeat"] for s in per_session.values())
    run_max = max(distribution) if distribution else 0
    return per_session, run_max, distribution


def find_waiver_timestamp(rollouts, marker):
    """Earliest event_msg/user_message timestamp, across ALL rollouts,
    whose message text contains MARKER (case-insensitive substring). None
    if marker is falsy or never found. Never returns or logs the message
    text itself -- only its timestamp."""
    if not marker:
        return None
    needle = marker.lower()
    hits = []
    for path in rollouts:
        for _ts, typ, p in rp.iter_records(path):
            if typ == "event_msg" and p.get("type") == "user_message":
                msg = p.get("message")
                if isinstance(msg, str) and needle in msg.lower():
                    hits.append(_ts)
    return min(hits) if hits else None


def _waiver_violations(occurrences, mutations, waiver_ts):
    """A violation: a cmd_id with >=1 occurrence at-or-before waiver_ts
    (the command that was running/failing when the waiver was issued)
    reruns AFTER waiver_ts with zero mutation_timeline() events strictly
    between waiver_ts and the rerun -- the 07-29 session's "rerun the
    waived baseline anyway" pattern. A cmd_id with no pre-waiver
    occurrence is never a candidate: its post-waiver appearance is an
    ordinary first run, not a waived rerun."""
    if waiver_ts is None:
        return []
    by_cmd = collections.defaultdict(list)
    for occ in occurrences:
        by_cmd[occ["cmd_id"]].append(occ)

    violations = []
    for cmd_id, occs in by_cmd.items():
        occs = sorted(occs, key=lambda o: o["timestamp"])
        if not any(o["timestamp"] <= waiver_ts for o in occs):
            continue  # never ran before the waiver -- not a waived command
        for occ in occs:
            if occ["timestamp"] <= waiver_ts:
                continue
            n_mut = _mutations_between(mutations, waiver_ts, occ["timestamp"])
            if n_mut == 0:
                violations.append({
                    "cmd_id": cmd_id,
                    "rerun_timestamp": occ["timestamp"],
                    "rerun_rollout": occ["rollout"],
                })
    violations.sort(key=lambda v: v["rerun_timestamp"])
    return violations


def events_between(rollouts, start_ts, end_ts):
    """Content-free manual-verification helper: every mutation and
    test-command event, across ALL rollouts, strictly between start_ts
    and end_ts, sorted by timestamp -- kind + timestamp + rollout only,
    never the raw/normalized command text. Used to eyeball a flagged
    duplicate-gate pair's "between-events window" (the standing rule:
    manually verify a flagged pair really had no intervening mutation)
    without ever printing corpus content."""
    events = []
    for path in rollouts:
        basename = os.path.basename(path)
        for ts in rp.mutation_events(path):
            if start_ts < ts < end_ts:
                events.append({"kind": "mutation", "timestamp": ts, "rollout": basename})
        for ev in test_command_events(path):
            if start_ts < ev["timestamp"] < end_ts:
                events.append({"kind": "test_cmd", "timestamp": ev["timestamp"], "rollout": basename})
    events.sort(key=lambda e: e["timestamp"])
    return events


def score_tree(rollouts, label=None, waiver_marker=None):
    """Core, reusable scoring pass over an already-discovered rollouts
    list (no root/tree-walk needed -- E3's duplicate-gate question spans
    ALL sessions of a run, not just the spawn tree). Same reuse seam as
    score_e2.build_tree()/score_e6.score_tree(): an external corpus with
    a different directory layout (e.g. the 07-29 audit corpus's flat
    ~/.codex/sessions/YYYY/MM/DD/*.jsonl, via audit0729_adapter.py-style
    discovery) can call this directly without going through
    find_rollouts()'s quorum-battery-layout assumption."""
    rollouts = sorted(rollouts)
    occurrences = _all_test_occurrences(rollouts)
    _assign_cmd_ids(occurrences)
    mutations = mutation_timeline(rollouts)

    duplicate_gate_pairs = _duplicate_gate_pairs(occurrences, mutations)
    per_session_repeat, run_max_repeat, repeat_distribution = _per_session_repeat(occurrences)

    waiver_ts = find_waiver_timestamp(rollouts, waiver_marker)
    violations = _waiver_violations(occurrences, mutations, waiver_ts)

    flagged = [pr for pr in duplicate_gate_pairs if pr["is_duplicate_gate"]]

    return {
        "label": label,
        "rollout_count": len(rollouts),
        "n_test_occurrences": len(occurrences),
        "n_mutation_events": len(mutations),
        "duplicate_gate_pairs": duplicate_gate_pairs,
        "n_duplicate_gate_pairs": len(duplicate_gate_pairs),
        "n_flagged_duplicate_gate_pairs": len(flagged),
        "has_duplicate_gate": len(flagged) > 0,
        "per_session_repeat": per_session_repeat,
        "run_max_repeat": run_max_repeat,
        "repeat_distribution": repeat_distribution,
        "waiver": {
            "marker_configured": bool(waiver_marker),
            "found": waiver_ts is not None,
            "timestamp": waiver_ts,
            "violations": violations,
            "n_violations": len(violations),
        },
    }


def find_rollouts(rundir):
    pattern = os.path.join(rundir, "home", ".codex", "sessions", "**", "*.jsonl")
    return sorted(glob.glob(pattern, recursive=True))


def _parent_label(rundir):
    """Identical convention to score_e1.py/score_e2.py/score_e6.py's
    helper of the same name."""
    parent = os.path.basename(os.path.dirname(os.path.abspath(rundir.rstrip("/"))))
    m = REP_DIR_RE.match(parent)
    if m:
        return m.group("arm_scenario"), int(m.group("rep"))
    return parent, None


def score_run(rundir, waiver_marker=None):
    rundir = rundir.rstrip("/")
    arm_scenario, rep = _parent_label(rundir)
    rollouts = find_rollouts(rundir)
    if not rollouts:
        raise SystemExit(f"score_e3: no rollout files found under {rundir}/home/.codex/sessions/**")
    label = f"{arm_scenario}-rep{rep}" if rep is not None else arm_scenario
    result = score_tree(rollouts, label=label, waiver_marker=waiver_marker)
    result["rundir"] = rundir
    result["arm_scenario"] = arm_scenario
    result["rep"] = rep
    return result


def print_run_report(run):
    label = f"{run['arm_scenario']} rep{run['rep']}" if run["rep"] is not None else run["arm_scenario"]
    print(f"### {label} -- `{run['rundir']}`")
    print()
    print(f"rollouts={run['rollout_count']}  test_occurrences={run['n_test_occurrences']}  "
          f"mutation_events={run['n_mutation_events']}")
    print()
    print(f"**duplicate-gate pairs: {run['n_flagged_duplicate_gate_pairs']}/{run['n_duplicate_gate_pairs']} "
          f"flagged (zero intervening mutation)**")
    for pr in run["duplicate_gate_pairs"]:
        mark = "FLAGGED" if pr["is_duplicate_gate"] else "ok"
        print(f"    [{mark}] {pr['cmd_id']}: {pr['first']['rollout']}@{pr['first']['timestamp']} "
              f"-> {pr['second']['rollout']}@{pr['second']['timestamp']} "
              f"(mutations_between={pr['mutations_between']})")
    print()
    print(f"per-session identical-command repeat: run_max={run['run_max_repeat']}  "
          f"distribution={run['repeat_distribution']}")
    for rollout, s in sorted(run["per_session_repeat"].items()):
        print(f"    {rollout}: max_repeat={s['max_repeat']}  "
              f"n_distinct_commands={s['n_distinct_commands']}  "
              f"n_test_occurrences={s['n_test_occurrences']}")
    print()
    w = run["waiver"]
    if w["marker_configured"]:
        print(f"waiver: found={w['found']}  timestamp={w['timestamp']}  "
              f"violations={w['n_violations']}")
        for v in w["violations"]:
            print(f"    VIOLATION {v['cmd_id']}: rerun at {v['rerun_rollout']}@{v['rerun_timestamp']} "
                  f"with zero mutation events since the waiver")
    print()


def _rep_range_suffix(runs):
    """Identical convention to score_e1.py/score_e2.py/score_e6.py's
    helper of the same name."""
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
    out_path = os.path.join(out_dir, f"e3-{label}.json")
    if os.path.exists(out_path) and not force:
        print(f"score_e3: refusing to overwrite existing {out_path} "
              f"-- set env FORCE=1 to overwrite", file=sys.stderr)
        return out_path, False
    with open(out_path, "w") as f:
        json.dump({"label": label, "runs": runs}, f, indent=2)
    return out_path, True


def main(argv):
    if len(argv) < 2:
        print("usage: score_e3.py RUNDIR...   (env E3_WAIVER_MARKER optional)", file=sys.stderr)
        return 1

    waiver_marker = os.environ.get("E3_WAIVER_MARKER")
    runs = [score_run(rd, waiver_marker=waiver_marker) for rd in argv[1:]]

    print(f"# E3 duplicate-gate scorer output ({len(runs)} run(s))")
    print()
    for run in runs:
        print_run_report(run)

    print("## Aggregate across all given RUNDIRs")
    print()
    n_runs = len(runs)
    n_with_gate = sum(1 for r in runs if r["has_duplicate_gate"])
    n_with_waiver_violation = sum(1 for r in runs if r["waiver"]["n_violations"] > 0)
    print(f"reps scored={n_runs}  reps with >=1 duplicate-gate pair={n_with_gate}/{n_runs}  "
          f"reps with >=1 waiver violation={n_with_waiver_violation}/{n_runs}")
    print(f"run_max_repeat across all reps: {max((r['run_max_repeat'] for r in runs), default=0)}")
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
