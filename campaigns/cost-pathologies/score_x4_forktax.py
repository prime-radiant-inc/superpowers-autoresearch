#!/usr/bin/env python3
"""X4 fork-tax scorer (cost-pathologies Task 2).

Instruments the mined corpora's X4 signature -- "child/parent byte ratio;
inherited-prefix duplicate ratio" (design doc, campaigns/cost-pathologies
README + logs/2026-07-31-cost-pathologies.md's X4 section) -- into a
reusable MINE-tier scorer over `spawn_agent` parent/child pairs (the same
linkage `campaigns/codex-efficiency/score_e1.py` already resolves for
fork-hygiene: `extract_spawns()` + `child_links()`, imported here, never
forked).

**child_parent_byte_ratio** is the simple `child_bytes / parent_bytes`
(on-disk file size) score_e1.py already reports per-spawn, aggregated here.

**inherited_prefix_duplicate_ratio** measures how much of a CHILD rollout's
own on-disk content is a verbatim replay of its PARENT's prior turns
(the "full transcript replay, on disk" pathology named in
`_tmp/cost-pathologies-2026-07-31/local-host-report.md`'s method notes),
rather than genuinely new conversation. Verified directly against a real
`fork_turns="all"` spawn pair from this repo's own battery corpus
(`evals/results/cx-eff-cx-sdd-small-spinout-rep5/.../home/.codex/sessions/
2026/07/29/rollout-2026-07-29T05-39-20-...jsonl` -> its child
`rollout-2026-07-29T05-41-20-...jsonl`) before this algorithm was
finalized:

  - Rollout `timestamp` fields are bulk-rewritten on fork (a corpus
    property documented in `campaigns/codex-efficiency/DESIGN.md`'s recon
    notes and independently re-confirmed here), so byte-for-byte RAW LINE
    comparison between parent and child fails even for genuine replay.
    Records are instead compared by `(type, payload)` structural equality
    (`json.dumps(payload, sort_keys=True)` as the comparison key),
    ignoring `timestamp`.
  - A forked child's OWN first record (its own `session_meta`, carrying a
    `forked_from_id` key the parent's copy lacks) never matches the
    parent, and the replay is not always a PERFECT copy of the parent's
    entire prior sequence (one record was dropped mid-replay in the real
    pair inspected -- observed, not hypothesized). A naive from-index-0
    longest-common-prefix comparison therefore undercounts badly (3/64
    records in the real pair). This scorer instead finds the run of
    `difflib.SequenceMatcher` matching blocks that starts at the FIRST
    shared record and stays CONTIGUOUS on the CHILD side (gaps on the
    PARENT side are tolerated -- a dropped parent record mid-replay --
    but the moment the child interleaves anything of its own, the run
    ends). On the real pair this gives a 7/64-record, 32%-of-bytes replay
    run -- ending exactly where the child's own new turns begin -- versus
    0% for a real `fork_turns="none"` sibling child in the same battery
    rep. Both real-pair numbers are reproduced in this module's
    docstring for traceability; they are not re-asserted by the unit
    tests, which use small synthetic fixtures instead (no real session
    content is committed here) -- see this task's corpus-validation log
    entry (`logs/2026-07-31-cost-pathologies.md`) for the reconciliation.
  - The ratio is BYTE-weighted (the child's own raw on-disk line lengths
    for the lines covered by the matched run, divided by the child's
    total bytes), not record-count-weighted: a single record can be
    KB-to-MB sized (encrypted reasoning blobs, tool outputs), and the
    pathology this scorer targets is disk/token COST, not record count.
  - A record that happens to recur identically at MULTIPLE points in a
    session (e.g. an unchanged `turn_context`/`world_state` snapshot
    re-emitted every turn) is a known false-positive risk for a naive
    whole-file "is this child record ALSO present somewhere in the
    parent" set-membership check (measured 55% on the real pair, more
    than 7x the contiguous-run figure) -- this is exactly the
    "boilerplate-contamination" risk `local-host-report.md` warns future
    mechanical scorers about. Requiring the match to be part of one
    contiguous run starting at the top of the child avoids it: a
    recurring-but-coincidental match deep in the file, with nothing
    contiguous around it, contributes at most its own tiny size, not the
    whole match set.

Usage: `fork_stats(session_dir)` where SESSION_DIR is any directory whose
rollout files should be considered together -- a single run's
`home/.codex/sessions` tree, or a real corpus directory like
`~/.codex/sessions/2026/07/17/` (the walk is recursive and dot-directory
safe, matching either layout -- see `find_rollouts()`). Read-only; makes
no writes.
"""
import difflib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "codex-efficiency"))
import rollout_parser as rp
from scorer_common import find_files as _find_files
from scorer_common import resolve_child_path as _resolve_child_path


def find_rollouts(session_dir):
    # NOTE (queue-execution campaign, Task 3, item 14): this used to be
    # glob.glob(session_dir/**/*.jsonl, recursive=True), which silently
    # skips dot-prefixed directories under '**' -- calling fork_stats()
    # directly on a battery rep root (real content under a hidden
    # `.../home/.codex/sessions/...` path) returned 0 children with no
    # error (logs/2026-07-31-cost-pathologies.md's Task 12 entry, worked
    # around there with a resolve-then-call wrapper instead of fixing
    # this function). find_files uses os.walk, which has no such
    # restriction.
    return sorted(_find_files(session_dir, "*.jsonl"))


def _load(path):
    """Raw lines plus their parsed record (None for an unparseable line),
    aligned 1:1 -- so byte-weighting below can index the SAME line whose
    (type, payload) key it compared."""
    with open(path, "rb") as f:
        raw_lines = f.readlines()
    records = []
    for raw in raw_lines:
        try:
            records.append(json.loads(raw))
        except (json.JSONDecodeError, UnicodeDecodeError):
            records.append(None)
    return records, raw_lines


def _record_key(rec):
    """(type, payload) structural identity, ignoring `timestamp` -- see
    module docstring for why raw-line/timestamp comparison doesn't work on
    this corpus. None for an unparseable record (never matches anything,
    including another unparseable record, since None != None is False in
    Python but we want an unparseable line to never spuriously "match")."""
    if rec is None:
        return object()  # unique per call -- never equals another key
    return (rec.get("type"), json.dumps(rec.get("payload"), sort_keys=True, default=str))


def _prefix_duplicate_bytes(parent_path, child_path):
    """Returns (duplicate_bytes, total_child_bytes) -- see module
    docstring for the contiguous-run-from-the-first-match algorithm."""
    parent_records, _ = _load(parent_path)
    child_records, child_lines = _load(child_path)
    total_bytes = sum(len(line) for line in child_lines)

    parent_keys = [_record_key(r) for r in parent_records]
    child_keys = [_record_key(r) for r in child_records]
    sm = difflib.SequenceMatcher(None, parent_keys, child_keys, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size > 0]
    if not blocks:
        return 0, total_bytes

    run = [blocks[0]]
    for b in blocks[1:]:
        last = run[-1]
        if b.b == last.b + last.size:
            run.append(b)
        else:
            break

    covered = set()
    for b in run:
        covered.update(range(b.b, b.b + b.size))
    duplicate_bytes = sum(len(child_lines[i]) for i in covered)
    return duplicate_bytes, total_bytes


def fork_stats(session_dir):
    """Every resolvable spawn_agent parent/child pair found anywhere under
    SESSION_DIR (recursive glob), with per-child byte_ratio and
    inherited_prefix_duplicate_ratio, plus the mean of each across all
    resolved children. `{"children": [], "child_parent_byte_ratio": 0.0,
    "inherited_prefix_duplicate_ratio": 0.0}` if nothing resolves."""
    rollouts = find_rollouts(session_dir)
    children = []
    for parent_path in rollouts:
        spawns = rp.extract_spawns(parent_path)
        if not spawns:
            continue
        links = rp.child_links(parent_path)
        for s in spawns:
            thread_id = links.get(s.call_id)
            if not thread_id:
                continue
            child_path = _resolve_child_path(thread_id, rollouts)
            if not child_path:
                continue
            parent_bytes = os.path.getsize(parent_path)
            child_bytes = os.path.getsize(child_path)
            dup_bytes, total_bytes = _prefix_duplicate_bytes(parent_path, child_path)
            children.append({
                "parent_rollout": os.path.basename(parent_path),
                "child_rollout": os.path.basename(child_path),
                "call_id": s.call_id,
                "task_name": s.task_name,
                "fork_turns": s.fork_turns,
                "parent_bytes": parent_bytes,
                "child_bytes": child_bytes,
                "byte_ratio": (child_bytes / parent_bytes) if parent_bytes else 0.0,
                "inherited_prefix_duplicate_ratio": (dup_bytes / total_bytes) if total_bytes else 0.0,
            })

    if not children:
        return {"children": [], "child_parent_byte_ratio": 0.0,
                "inherited_prefix_duplicate_ratio": 0.0}

    n = len(children)
    return {
        "children": children,
        "child_parent_byte_ratio": sum(c["byte_ratio"] for c in children) / n,
        "inherited_prefix_duplicate_ratio":
            sum(c["inherited_prefix_duplicate_ratio"] for c in children) / n,
    }


def main(argv):
    if len(argv) < 2:
        print("usage: score_x4_forktax.py SESSION_DIR...", file=sys.stderr)
        return 1
    for session_dir in argv[1:]:
        result = fork_stats(session_dir)
        print(f"# X4 fork-tax -- {session_dir}")
        print(f"children resolved: {len(result['children'])}")
        print(f"mean child/parent byte ratio: {result['child_parent_byte_ratio']:.3f}")
        print(f"mean inherited-prefix duplicate ratio: "
              f"{result['inherited_prefix_duplicate_ratio']:.3f}")
        for c in result["children"]:
            print(f"  {c['parent_rollout']} -> {c['child_rollout']} "
                  f"(fork_turns={c['fork_turns']}) byte_ratio={c['byte_ratio']:.3f} "
                  f"dup_ratio={c['inherited_prefix_duplicate_ratio']:.3f}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
