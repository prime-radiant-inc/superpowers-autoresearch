#!/usr/bin/env python3
"""Validate rollout_parser.py (Tasks 2-3) against the 2026-07-28 audit
corpus's known ground truth (session-manifest.json / spawns-window.json /
metrics-all.jsonl). This is the gate that lets every later codex-efficiency
scorer trust the parser -- see task-4-brief.md.

Three phases, printed as a report:
  A. Spawn parity (exact): spawns-window.json vs extract_spawns(), grouped
     by session, compared field-by-field per call_id.
  B. Per-session metrics (stratified ~60-session sample): metrics-all.jsonl
     vs parse_session(), per-field exact-match rates.
  C. Manual-inspection feed: real matched skill-read / test-command strings
     (truncated to 160 chars) for human eyeball review.

Usage:
    AUDIT_DIR=/path/to/audit python3 validate_corpus.py | tee out/corpus-validation-raw.txt

The raw output may quote real client rollout commands -- NEVER commit it.
Only campaigns/codex-efficiency/out/corpus-validation.md (hand-written,
aggregates + mismatch categories only) is meant to be committed.
"""
import json
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp

AUDIT_DIR = os.environ.get(
    "AUDIT_DIR",
    "/Users/jesse/.codex/visualizations/2026/07/28/019fa9a2-87b7-73b1-a76a-efb9f14abbea",
)
# Verbatim from scan-rollouts.mjs (windowStart/windowEnd), millisecond-
# precision so lexicographic string comparison agrees with the real
# chronological order of rollout timestamps (which are always .mmmZ).
WINDOW_START = "2026-07-14T07:00:00.000Z"
WINDOW_END = "2026-07-28T16:50:29.164Z"


def in_window(ts):
    return bool(ts) and WINDOW_START <= ts < WINDOW_END


def load_json(name):
    with open(os.path.join(AUDIT_DIR, name)) as f:
        return json.load(f)


def load_jsonl(name):
    out = []
    with open(os.path.join(AUDIT_DIR, name)) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


# ---------------------------------------------------------------- Phase A --

SPAWN_FIELDS = ("task_name", "fork_turns", "model", "reasoning_effort")


def _audit_spawn_value(rec, field):
    # extract-spawns.mjs sets fork_turns/model/reasoning_effort to the
    # literal string "(omitted)" when absent, but leaves task_name simply
    # unset (JSON.stringify drops it) -- normalize both cases the same way
    # extract_spawns()'s str(args.get(field, OMIT)) does on our side.
    v = rec.get(field)
    return "(omitted)" if v is None else str(v)


def phase_a(manifest_by_id):
    print("=" * 78)
    print("PHASE A: spawn parity (spawns-window.json vs extract_spawns)")
    print("=" * 78)
    spawns = load_json("spawns-window.json")
    by_session = defaultdict(list)
    for rec in spawns:
        by_session[rec["session_id"]].append(rec)

    sessions_compared = 0
    exact_match_sessions = 0
    missing = []
    mismatches = []

    our_fork_turns, our_model = defaultdict(int), defaultdict(int)
    audit_fork_turns, audit_model = defaultdict(int), defaultdict(int)
    for rec in spawns:
        audit_fork_turns[_audit_spawn_value(rec, "fork_turns")] += 1
        audit_model[_audit_spawn_value(rec, "model")] += 1

    for session_id in sorted(by_session):
        audit_records = by_session[session_id]
        manifest_row = manifest_by_id.get(session_id)
        if manifest_row is None:
            missing.append((session_id, "session_id not in session-manifest.json"))
            continue
        path = manifest_row["rollout_path"]
        if not os.path.exists(path):
            missing.append((session_id, f"rollout_path missing on disk (archived?): {path}"))
            continue

        sessions_compared += 1
        ours = rp.extract_spawns(path)
        ours_in_window = [s for s in ours if in_window(s.timestamp)]
        for s in ours_in_window:
            our_fork_turns[s.fork_turns] += 1
            our_model[s.model] += 1

        ours_by_callid = {s.call_id: s for s in ours_in_window}
        audit_by_callid = {r["call_id"]: r for r in audit_records}

        session_ok = True
        for call_id in sorted(set(ours_by_callid) | set(audit_by_callid)):
            o = ours_by_callid.get(call_id)
            a = audit_by_callid.get(call_id)
            if o is None:
                session_ok = False
                mismatches.append(
                    f"session {session_id} call_id={call_id}: in audit only "
                    f"(missing from our in-window extraction)")
                continue
            if a is None:
                session_ok = False
                mismatches.append(
                    f"session {session_id} call_id={call_id}: in ours only "
                    f"(not in spawns-window.json)")
                continue
            for field in SPAWN_FIELDS:
                ov = getattr(o, field)
                av = _audit_spawn_value(a, field)
                if ov != av:
                    session_ok = False
                    mismatches.append(
                        f"session {session_id} call_id={call_id}: "
                        f"field={field} ours={ov!r} audit={av!r}")
        if session_ok:
            exact_match_sessions += 1

    print(f"distinct sessions referenced in spawns-window.json: {len(by_session)}")
    print(f"sessions compared (rollout resolved + present)    : {sessions_compared}")
    print(f"missing rollout files (excluded, not a mismatch)  : {len(missing)}")
    for sid, reason in missing:
        print(f"  - {sid}: {reason}")
    print(f"exact-match sessions                              : {exact_match_sessions} / {sessions_compared}")
    print()
    print(f"fork_turns distribution -- ours (in-window)    : {dict(sorted(our_fork_turns.items()))}")
    print(f"fork_turns distribution -- audit(spawns-window): {dict(sorted(audit_fork_turns.items()))}")
    print(f"model omitted -- ours (in-window)    : {our_model.get('(omitted)', 0)} / {sum(our_model.values())}")
    print(f"model omitted -- audit(spawns-window): {audit_model.get('(omitted)', 0)} / {sum(audit_model.values())}")
    print()
    print(f"mismatches ({len(mismatches)} total):")
    for m in mismatches:
        print(f"  {m}")
    print()
    return {
        "sessions_compared": sessions_compared,
        "exact_match_sessions": exact_match_sessions,
        "mismatches": mismatches,
        "missing": missing,
    }


# ---------------------------------------------------------------- Phase B --

# (rollout_parser.SessionMetrics field, metrics-all.jsonl field)
METRIC_FIELDS = [
    ("compactions", "context_compacted"),
    ("task_started", "task_started"),
    ("task_complete", "task_complete"),
    ("skill_reads_compat", "skill_reads"),
    ("memory_reads", "memory_reads"),
    ("spawn_calls", "spawn_calls"),
    ("wait_calls", "wait_calls"),
    ("test_commands", "test_command_calls"),
]


def _sample_buckets(recs):
    """~60-session stratified sample. Sort order for the four 'top 10' edge-
    case buckets isn't specified by the brief beyond 'largest by bytes' (the
    first one) -- for the other three, sort by the bucket's own defining
    count descending (most oversized/compacted/spawn-heavy first), tie-break
    on bytes then path, for a deterministic 'most interesting case' pick.
    The 20-random bucket draws from the full population with a fixed seed.
    """
    by_bytes = sorted(recs, key=lambda r: (-r["bytes"], r["path"]))
    top10_bytes = by_bytes[:10]

    oversized = [r for r in recs if r.get("oversized_lines", 0) > 0]
    top10_oversized = sorted(
        oversized, key=lambda r: (-r["oversized_lines"], -r["bytes"], r["path"]))[:10]

    compacted = [r for r in recs if r.get("context_compacted", 0) > 0]
    top10_compacted = sorted(
        compacted, key=lambda r: (-r["context_compacted"], -r["bytes"], r["path"]))[:10]

    spawning = [r for r in recs if r.get("spawn_calls", 0) > 0]
    top10_spawn = sorted(
        spawning, key=lambda r: (-r["spawn_calls"], -r["bytes"], r["path"]))[:10]

    random20 = random.Random(42).sample(recs, 20)

    return {
        "top10_bytes": top10_bytes,
        "top10_oversized": top10_oversized,
        "top10_compacted": top10_compacted,
        "top10_spawn": top10_spawn,
        "random20": random20,
    }


def phase_b():
    print("=" * 78)
    print("PHASE B: per-session metrics (metrics-all.jsonl vs parse_session), stratified sample")
    print("=" * 78)
    recs = load_jsonl("metrics-all.jsonl")
    buckets = _sample_buckets(recs)

    selected = {}  # session id -> (record, {bucket names})
    for bname, blist in buckets.items():
        for r in blist:
            sid = r["id"]
            selected.setdefault(sid, (r, set()))[1].add(bname)

    print("bucket sizes (pre-dedup): " + ", ".join(f"{k}={len(v)}" for k, v in buckets.items()))
    print(f"distinct sessions after de-dup: {len(selected)}")
    print()

    field_match = {f: 0 for f, _ in METRIC_FIELDS}
    field_total = {f: 0 for f, _ in METRIC_FIELDS}
    mismatches = []
    missing = []

    for sid in sorted(selected):
        rec, bnames = selected[sid]
        path = rec["path"]
        if not os.path.exists(path):
            missing.append((sid, f"rollout path missing on disk (archived?): {path}"))
            continue
        m = rp.parse_session(path)
        for our_field, audit_field in METRIC_FIELDS:
            ours_v = getattr(m, our_field)
            audit_v = rec.get(audit_field, 0)
            field_total[our_field] += 1
            if ours_v == audit_v:
                field_match[our_field] += 1
            else:
                mismatches.append(
                    f"session {sid} buckets={sorted(bnames)} "
                    f"field={our_field}({audit_field}) ours={ours_v} audit={audit_v} "
                    f"created_at={rec.get('created_at')} updated_at={rec.get('updated_at')} "
                    f"bytes={rec.get('bytes')}")

    print("per-field exact-match rate:")
    for our_field, audit_field in METRIC_FIELDS:
        t = field_total[our_field]
        mm = field_match[our_field]
        pct = (mm / t * 100) if t else 0.0
        print(f"  {our_field:20s} ({audit_field:20s}): {mm}/{t} ({pct:.1f}%)")
    print()
    print(f"missing rollout files (excluded, not a mismatch): {len(missing)}")
    for sid, reason in missing:
        print(f"  - {sid}: {reason}")
    print()
    print(f"mismatches ({len(mismatches)} total):")
    for mm in mismatches:
        print(f"  {mm}")
    print()
    return {
        "field_match": field_match,
        "field_total": field_total,
        "mismatches": mismatches,
        "selected": selected,
    }


# ---------------------------------------------------------------- Phase C --

def _collect_matches(path, regex, limit=None):
    out = []
    for _, typ, p in rp.iter_records(path):
        if typ != "response_item" or p.get("type") not in rp.TOOL_CALL_TYPES:
            continue
        text = rp._tool_input(p)
        if regex.search(text):
            out.append(text)
            if limit and len(out) >= limit:
                break
    return out


def phase_c():
    print("=" * 78)
    print("PHASE C: manual-inspection feed (matched skill-read / test commands)")
    print("=" * 78)
    recs = load_jsonl("metrics-all.jsonl")

    skill_pool = [r for r in recs if r.get("skill_reads", 0) > 0]
    test_pool = [r for r in recs if r.get("test_command_calls", 0) > 0]

    skill_sessions = random.Random(42).sample(skill_pool, min(15, len(skill_pool)))
    test_sessions = random.Random(42).sample(test_pool, min(15, len(test_pool)))

    skill_matches = []
    for r in skill_sessions:
        if not os.path.exists(r["path"]):
            continue
        for text in _collect_matches(r["path"], rp.SKILL_READ_RE, limit=5):
            skill_matches.append((r["id"], text))
        if len(skill_matches) >= 30:
            break

    test_matches = []
    for r in test_sessions:
        if not os.path.exists(r["path"]):
            continue
        for text in _collect_matches(r["path"], rp.TEST_RE, limit=5):
            test_matches.append((r["id"], text))
        if len(test_matches) >= 30:
            break

    picked_skill = random.Random(42).sample(skill_matches, min(10, len(skill_matches)))
    picked_test = random.Random(42).sample(test_matches, min(10, len(test_matches)))

    print(f"10 random matched skill-read commands "
          f"(from {len(skill_matches)} candidates across {len(skill_sessions)} sessions):")
    for i, (sid, text) in enumerate(picked_skill, 1):
        print(f"  [{i}] session {sid}: {text[:160]!r}")
    print()
    print(f"10 random matched test commands "
          f"(from {len(test_matches)} candidates across {len(test_sessions)} sessions):")
    for i, (sid, text) in enumerate(picked_test, 1):
        print(f"  [{i}] session {sid}: {text[:160]!r}")
    print()


# -------------------------------------------------------------------- main --

def main():
    manifest = load_json("session-manifest.json")
    manifest_by_id = {m["id"]: m for m in manifest}

    print(f"AUDIT_DIR = {AUDIT_DIR}")
    print(f"window    = [{WINDOW_START}, {WINDOW_END})")
    print()

    a = phase_a(manifest_by_id)
    b = phase_b()
    phase_c()

    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"Phase A: {a['exact_match_sessions']}/{a['sessions_compared']} sessions exact-match, "
          f"{len(a['mismatches'])} call_id/field mismatches, {len(a['missing'])} missing files")
    for our_field, audit_field in METRIC_FIELDS:
        t = b["field_total"][our_field]
        mm = b["field_match"][our_field]
        pct = (mm / t * 100) if t else 0.0
        print(f"Phase B {our_field:20s}: {mm}/{t} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
