#!/usr/bin/env python3
"""E7 wait-polling census (Amendment 1, Tasks E7-E9 -- MINE tier, no new
run spend). Pre-registered prediction:
`logs/2026-07-28-codex-efficiency.md`, "E7 PRE-REGISTRATION" entry.

Scores three corpora with the same `rollout_parser.wait_outcomes()` logic:

  (a) Drew Ritter's external SDD head-to-head corpus (read-only, never
      committed -- reuses drew_adapter.py's RUNS/discover() for layout).
  (b) The 2026-07-28 audit corpus: the known 1,058-`wait_agent`-call Remux
      root (Finding 7), plus a "direct human gpt-5.6-sol task" sample --
      see `_direct_human_sol_candidates()`'s docstring for why this is OUR
      OWN derived proxy for that population, not a reproduction of the
      audit's own (manually curated) Finding 8 selection.
  (c) Our own `cx-eff-cx-sdd-small-{dev,spinout}-rep*` battery runs (Tasks
      6/6b) -- reuses score_e1.py's find_rollouts() for layout.

Per session: paired wait_agent outcomes (via `wait_outcomes()`), timeout
rate, inter-poll interval seconds (from ALL raw wait_agent call
timestamps, not just paired ones -- the polling cadence is a real
observable regardless of whether we can classify the outcome), and a
cache-read rebill estimate (token_count events attributed to the
intervals between consecutive polls where that's cleanly possible, else
the coarser proxy -- session total cache-read tokens x (wait calls /
total tool calls), labeled "proxy").

No message/instruction/task-name text is ever read or printed by this
script or by `sample_marker_texts()` -- the manual-inspection sampler
reads only the matched wait_agent `function_call_output.output` string
(a short JSON status envelope, not session content) for a small random
sample, per the campaign's "numbers only" rule for the audit/Drew
corpora.

Usage: score_e7.py [--samples N]
Prints a markdown report to stdout. Writes aggregates-only JSON blobs to
campaigns/codex-efficiency/out/e7-<corpus>.json. Refuses to overwrite any
existing one of those blobs unless env FORCE=1 is set, and the check is
all-or-nothing (the four blobs are one census; a partial write would mix a
fresh run with a stale one). Read-only otherwise. Exits 0 on success, 1 on
an existing-output collision without FORCE.
"""
import bisect
import datetime
import glob
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp
import drew_adapter as da
import score_e1 as e1

AUDIT_DIR = os.environ.get(
    "AUDIT_DIR",
    "/Users/jesse/.codex/visualizations/2026/07/28/019fa9a2-87b7-73b1-a76a-efb9f14abbea")
EVALS_RESULTS = os.environ.get(
    "EVALS_RESULTS", "/Users/jesse/git/superpowers/superpowers/evals/results")

# The audit's own Finding 7 figure ("one Remux root made 1,058 wait_agent
# calls, 788 of which timed out") -- root identified during E7's
# pre-registration by cross-referencing session-manifest.json (depth 0,
# thread_source:"user") against metrics-all.jsonl's per-session
# tool_counts.wait_agent (exactly one session anywhere in the corpus has
# tool_counts.wait_agent == 1058).
HIGH_WAIT_ROOT_ID = "019f95af-9a8e-7cb3-bc01-edcfe8b343e8"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


# --- per-session census -----------------------------------------------

def _parse_ts(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _wait_agent_call_timestamps(path):
    """All wait_agent function_call timestamps, sorted -- regardless of
    whether the call's outcome could be paired/classified. Used for the
    raw-call count and the inter-poll interval distribution."""
    out = []
    for ts, typ, p in rp.iter_records(path):
        if typ == "response_item" and p.get("type") == "function_call" \
           and p.get("name") == rp.WAIT_AGENT_NAME:
            out.append(ts)
    out.sort()
    return out


def _token_count_deltas(path):
    """(timestamp, cached_input_tokens delta, input_tokens delta) for
    every token_count event, sorted by timestamp. Deltas (last_token_usage)
    rather than cumulative totals, so a sub-window sum is meaningful."""
    out = []
    for ts, typ, p in rp.iter_records(path):
        if typ == "event_msg" and p.get("type") == "token_count":
            info = p.get("info") or {}
            last = info.get("last_token_usage") or {}
            out.append((ts, last.get("cached_input_tokens", 0) or 0,
                        last.get("input_tokens", 0) or 0))
    out.sort(key=lambda x: x[0])
    return out


def _total_tool_calls(path):
    n = 0
    for ts, typ, p in rp.iter_records(path):
        if typ == "response_item" and p.get("type") in rp.TOOL_CALL_TYPES:
            n += 1
    return n


def _cache_rebill_estimate(call_ts, token_deltas, total_tool_calls):
    """Returns (tokens, method). method is "attributed" when at least 90%
    of the intervals between consecutive wait_agent calls contain >=1
    token_count event (so the sum genuinely reflects cache-read cost paid
    while polling); otherwise "proxy" (session total cache-read tokens x
    wait-call share of all tool calls, per the task spec's documented
    fallback); "n/a" when there's nothing to attribute (fewer than 2
    calls, or no token_count events at all)."""
    if len(call_ts) < 2:
        return 0.0, "n/a"
    tc_ts = [t[0] for t in token_deltas]
    attributed = 0
    intervals_with_tc = 0
    n_intervals = len(call_ts) - 1
    for i in range(n_intervals):
        a, b = call_ts[i], call_ts[i + 1]
        lo = bisect.bisect_left(tc_ts, a)
        hi = bisect.bisect_left(tc_ts, b)
        if hi > lo:
            intervals_with_tc += 1
            attributed += sum(token_deltas[j][1] for j in range(lo, hi))
    if n_intervals and intervals_with_tc / n_intervals >= 0.9:
        return float(attributed), "attributed"
    total_cache_read = sum(c for _, c, _ in token_deltas)
    if not total_tool_calls:
        return 0.0, "n/a"
    wait_fraction = len(call_ts) / total_tool_calls
    return total_cache_read * wait_fraction, "proxy"


def census_session(path, label=""):
    waits = rp.wait_outcomes(path)
    call_ts = _wait_agent_call_timestamps(path)
    token_deltas = _token_count_deltas(path)
    total_tool_calls = _total_tool_calls(path)

    n_timed_out = sum(1 for w in waits if w.timed_out)
    intervals_s = []
    for i in range(len(call_ts) - 1):
        intervals_s.append((_parse_ts(call_ts[i + 1]) - _parse_ts(call_ts[i])).total_seconds())

    cache_rebill, method = _cache_rebill_estimate(call_ts, token_deltas, total_tool_calls)

    return {
        "path": path,
        "label": label,
        "n_wait_agent_calls": len(call_ts),
        "n_paired": len(waits),
        "n_excluded": len(call_ts) - len(waits),
        "n_timed_out": n_timed_out,
        "timeout_rate_of_paired": (n_timed_out / len(waits)) if waits else None,
        "timeout_rate_of_all_calls": (n_timed_out / len(call_ts)) if call_ts else None,
        "inter_poll_intervals_s": intervals_s,
        "cache_rebill_tokens": cache_rebill,
        "cache_rebill_method": method,
        "waits": waits,  # kept for the manual-inspection sampler; stripped before JSON dump
    }


def _percentile(sorted_values, pct):
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * (pct / 100)
    f, c = int(k), int(-(-k // 1))  # floor, ceil without importing math
    if f == c:
        return sorted_values[f]
    return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)


def aggregate(sessions):
    total_calls = sum(s["n_wait_agent_calls"] for s in sessions)
    total_paired = sum(s["n_paired"] for s in sessions)
    total_excluded = sum(s["n_excluded"] for s in sessions)
    total_timed_out = sum(s["n_timed_out"] for s in sessions)
    all_intervals = sorted(v for s in sessions for v in s["inter_poll_intervals_s"])
    attributed_sessions = [s for s in sessions if s["cache_rebill_method"] == "attributed"]
    proxy_sessions = [s for s in sessions if s["cache_rebill_method"] == "proxy"]
    return {
        "n_sessions": len(sessions),
        "n_sessions_with_waits": sum(1 for s in sessions if s["n_wait_agent_calls"] > 0),
        "total_wait_agent_calls": total_calls,
        "total_paired": total_paired,
        "total_excluded": total_excluded,
        "total_timed_out": total_timed_out,
        "timeout_rate_of_paired": (total_timed_out / total_paired) if total_paired else None,
        "timeout_rate_of_all_calls": (total_timed_out / total_calls) if total_calls else None,
        "n_intervals": len(all_intervals),
        "interval_p50_s": _percentile(all_intervals, 50),
        "interval_p95_s": _percentile(all_intervals, 95),
        "cache_rebill_attributed_tokens": sum(s["cache_rebill_tokens"] for s in attributed_sessions),
        "cache_rebill_attributed_n_sessions": len(attributed_sessions),
        "cache_rebill_proxy_tokens": sum(s["cache_rebill_tokens"] for s in proxy_sessions),
        "cache_rebill_proxy_n_sessions": len(proxy_sessions),
    }


def _strip_for_json(sessions):
    return [{k: v for k, v in s.items() if k != "waits"} for s in sessions]


# --- corpus (a): Drew's external head-to-head corpus --------------------

def score_drew(corpus_root=None):
    corpus_root = corpus_root or da.DEFAULT_CORPUS_ROOT
    groups = {}
    for label, rel_dir in da.RUNS.items():
        run_dir = os.path.join(corpus_root, rel_dir)
        paths = da.discover(run_dir)
        if not paths:
            continue
        sessions = [census_session(p, label=label) for p in paths]
        groups[label] = sessions
    return groups


# --- corpus (b): audit corpus ------------------------------------------

def _resolve_manifest_path(session_id, manifest=None):
    manifest = manifest if manifest is not None else _load_manifest()
    for r in manifest:
        if r.get("id") == session_id:
            return r.get("rollout_path")
    return None


_MANIFEST_CACHE = None


def _load_manifest():
    global _MANIFEST_CACHE
    if _MANIFEST_CACHE is None:
        with open(os.path.join(AUDIT_DIR, "session-manifest.json")) as f:
            _MANIFEST_CACHE = json.load(f)
    return _MANIFEST_CACHE


def _direct_human_sol_candidates(audit_dir, exclude_ids, max_family_size=20):
    """OUR OWN derived proxy for "direct human gpt-5.6-sol task roots" --
    NOT a reproduction of the audit report's Finding 8 population (whose
    own methodology section describes it as manual deep-reading: "deep-read
    every ... direct human gpt-5.6-sol task", not an algorithmic filter).
    We could not reconstruct that exact selection from session-manifest.json
    alone, so this documents a mechanical stand-in instead of guessing at
    the original one:

        depth == 0 (root session) AND thread_source == "user" (human-
        initiated, not a subagent) AND model == "gpt-5.6-sol" AND the
        session's root_id family has <= max_family_size total sessions
        (excludes the four/five multi-hundred-session dominant families --
        Scantastic, Serf/AIX, Fantastty, Remux -- leaving small,
        standalone, human-directed tasks) AND the session's own
        tool_counts.wait_agent > 0 (a pre-filter using the audit's
        pre-existing per-session counter, purely to avoid opening ~200
        rollout files that provably have zero wait_agent activity --
        the actual pairing/classification below still runs
        rollout_parser.wait_outcomes() independently on every candidate
        that passes).

    Returns (candidates, pool_size) where pool_size is the count of
    sessions matching every filter above except the wait_agent>0 one (so
    the caller can report "N of POOL_SIZE direct-task roots had any
    wait_agent activity at all")."""
    manifest = _load_manifest()
    by_id = {r["id"]: r for r in manifest}
    sess_count = {}
    metrics_by_id = {}
    with open(os.path.join(audit_dir, "metrics-all.jsonl")) as f:
        for line in f:
            try:
                m = json.loads(line)
            except json.JSONDecodeError:
                continue
            metrics_by_id[m["id"]] = m
            sess_count[m.get("root_id")] = sess_count.get(m.get("root_id"), 0) + 1

    pool = []
    for r in manifest:
        if r.get("depth") != 0:
            continue
        if r.get("thread_source") != "user":
            continue
        if r.get("model") != "gpt-5.6-sol":
            continue
        if r["id"] in exclude_ids:
            continue
        fam_size = sess_count.get(r["root_id"], 1)
        if fam_size > max_family_size:
            continue
        pool.append(r)

    candidates = []
    for r in pool:
        m = metrics_by_id.get(r["id"])
        wait_agent_count = (m or {}).get("tool_counts", {}).get("wait_agent", 0)
        if wait_agent_count > 0:
            candidates.append(r)
    return candidates, len(pool)


def score_audit():
    manifest = _load_manifest()
    high_wait_path = _resolve_manifest_path(HIGH_WAIT_ROOT_ID, manifest)
    if not high_wait_path or not os.path.exists(high_wait_path):
        raise SystemExit(f"score_e7: could not resolve high-wait root {HIGH_WAIT_ROOT_ID} "
                          f"via session-manifest.json")
    high_wait_session = census_session(high_wait_path, label="audit-high-wait-root")

    candidates, pool_size = _direct_human_sol_candidates(AUDIT_DIR, {HIGH_WAIT_ROOT_ID})
    direct_sessions = [
        census_session(c["rollout_path"], label="audit-direct-human-sol")
        for c in candidates
    ]
    return {
        "high_wait_root": [high_wait_session],
        "direct_human_sol_sample": direct_sessions,
        "direct_human_sol_pool_size": pool_size,
    }


# --- corpus (c): our own battery runs -----------------------------------

def score_battery(results_dir=None):
    results_dir = results_dir or EVALS_RESULTS
    groups = {}
    for arm in ("dev", "spinout"):
        rep_dirs = sorted(glob.glob(os.path.join(results_dir, f"cx-eff-cx-sdd-small-{arm}-rep*")))
        sessions = []
        for rep_dir in rep_dirs:
            rundirs = sorted(glob.glob(os.path.join(rep_dir, "*")))
            for rundir in rundirs:
                if not os.path.isdir(rundir):
                    continue
                rollouts = e1.find_rollouts(rundir)
                for path in rollouts:
                    sessions.append(census_session(path, label=f"battery-{arm}"))
        groups[arm] = sessions
    return groups


# --- manual-inspection sampler ------------------------------------------

def sample_marker_texts(all_sessions, n=10, seed=42):
    """Randomly sample N paired wait outcomes across every scored session
    and re-read each one's raw function_call_output.output text (a short
    JSON status envelope -- never message/task content) directly from its
    rollout file, for eyeball classification review. Returns a list of
    dicts: corpus label, timed_out, duration_hint, and the raw marker
    text (already short; no truncation needed for these shapes)."""
    universe = []
    for s in all_sessions:
        for w in s["waits"]:
            universe.append((s["path"], s["label"], w))
    rng = random.Random(seed)
    sample = rng.sample(universe, min(n, len(universe)))

    out = []
    for path, label, w in sample:
        raw_output = None
        for ts, typ, p in rp.iter_records(path):
            if typ == "response_item" and p.get("type") == "function_call_output" \
               and p.get("call_id") == w.call_id:
                raw_output = p.get("output")
                break
        out.append({
            "label": label,
            "timed_out": w.timed_out,
            "duration_hint": w.duration_hint,
            "raw_output": raw_output,
        })
    return out


# --- report printing ------------------------------------------------------

def _fmt_pct(v):
    return f"{v * 100:.1f}%" if v is not None else "n/a"


def _fmt_s(v):
    return f"{v:.2f}s" if v is not None else "n/a"


def print_group_line(name, sessions):
    agg = aggregate(sessions)
    print(f"- **{name}**: {agg['n_sessions']} session(s) scored, "
          f"{agg['n_sessions_with_waits']} with >=1 wait_agent call. "
          f"calls={agg['total_wait_agent_calls']} paired={agg['total_paired']} "
          f"excluded={agg['total_excluded']} timed_out={agg['total_timed_out']} "
          f"(rate/paired={_fmt_pct(agg['timeout_rate_of_paired'])}, "
          f"rate/all_calls={_fmt_pct(agg['timeout_rate_of_all_calls'])}). "
          f"inter-poll p50={_fmt_s(agg['interval_p50_s'])} "
          f"p95={_fmt_s(agg['interval_p95_s'])} (n={agg['n_intervals']} intervals). "
          f"cache-rebill: attributed={agg['cache_rebill_attributed_tokens']:.0f} tok "
          f"({agg['cache_rebill_attributed_n_sessions']} sessions), "
          f"proxy={agg['cache_rebill_proxy_tokens']:.0f} tok "
          f"({agg['cache_rebill_proxy_n_sessions']} sessions)")
    return agg


def write_outputs(corpora, out_dir, force=False):
    """Write one aggregates-only JSON blob per corpus, refusing to clobber
    existing output unless FORCE=1. Returns (target_paths, wrote).

    The check is all-or-nothing on purpose: this scorer writes four blobs
    that are read together as one census, so a partial refusal would leave
    out/ mixing a fresh run with a stale one -- the exact failure mode the
    other nine scorers' single-file guards can't produce."""
    os.makedirs(out_dir, exist_ok=True)
    targets = [(os.path.join(out_dir, f"e7-{name}.json"), groups)
               for name, groups in corpora]
    existing = [p for p, _ in targets if os.path.exists(p)]
    if existing and not force:
        print(f"score_e7: refusing to overwrite existing output "
              f"({', '.join(existing)}) -- set env FORCE=1 to overwrite",
              file=sys.stderr)
        return [p for p, _ in targets], False
    for out_path, groups in targets:
        blob = {name: {"aggregate": aggregate(sessions),
                       "sessions": _strip_for_json(sessions)}
                for name, sessions in groups.items()}
        with open(out_path, "w") as f:
            json.dump(blob, f, indent=2)
        print(f"wrote {out_path}", file=sys.stderr)
    return [p for p, _ in targets], True


def main(argv):
    n_samples = 10
    if "--samples" in argv:
        n_samples = int(argv[argv.index("--samples") + 1])

    print("# E7 wait-polling census (Amendment 1, MINE tier)")
    print()

    all_sessions = []

    print("## Corpus (a): Drew Ritter's external SDD head-to-head corpus")
    print()
    drew_groups = score_drew()
    for label, sessions in drew_groups.items():
        print_group_line(label, sessions)
        all_sessions.extend(sessions)
        root_only = [s for s in sessions if s["path"] == da.discover(
            os.path.join(da.DEFAULT_CORPUS_ROOT, da.RUNS[label]))[0]]
        if root_only:
            print("  ", end="")
            print_group_line(f"{label} (root file only)", root_only)
    print()

    print("## Corpus (b): 2026-07-28 audit corpus")
    print()
    audit = score_audit()
    print_group_line("high-wait Remux root (Finding 7)", audit["high_wait_root"])
    all_sessions.extend(audit["high_wait_root"])
    print(f"- direct-human-gpt-5.6-sol proxy pool: {audit['direct_human_sol_pool_size']} "
          f"candidate roots (depth 0, thread_source=user, model=gpt-5.6-sol, "
          f"root-family size <= 20), of which {len(audit['direct_human_sol_sample'])} "
          f"have any wait_agent activity -- see `_direct_human_sol_candidates()` "
          f"docstring for the derivation and its limits")
    if audit["direct_human_sol_sample"]:
        print_group_line("direct-human-sol sample (wait-active subset)", audit["direct_human_sol_sample"])
        all_sessions.extend(audit["direct_human_sol_sample"])
    print()

    print("## Corpus (c): our own cx-eff-cx-sdd-small battery runs (Tasks 6/6b)")
    print()
    battery = score_battery()
    for arm, sessions in battery.items():
        print_group_line(f"battery-{arm}", sessions)
        all_sessions.extend(sessions)
    print()

    print("## Manual inspection sample "
          f"(n={n_samples}, seed=42, classification + raw marker text only)")
    print()
    samples = sample_marker_texts(all_sessions, n=n_samples, seed=42)
    for i, s in enumerate(samples, 1):
        print(f"{i}. [{s['label']}] timed_out={s['timed_out']} "
              f"duration_hint={s['duration_hint']}ms  raw_output={s['raw_output']!r}")
    print()

    corpora = (
        ("drew", drew_groups),
        ("audit-high-wait-root", {"high_wait_root": audit["high_wait_root"]}),
        ("audit-direct-sol", {"direct_human_sol_sample": audit["direct_human_sol_sample"]}),
        ("battery", battery),
    )
    _, wrote = write_outputs(corpora, OUT_DIR, force=os.environ.get("FORCE") == "1")
    if not wrote:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
