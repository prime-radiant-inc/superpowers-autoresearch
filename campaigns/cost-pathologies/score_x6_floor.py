#!/usr/bin/env python3
"""X6 micro-dispatch floor scorer (cost-pathologies Task 2).

Design doc / hypothesis-log X6 section: "dispatching an agent costs a
context floor regardless of task size... Tiers: MINE (dispatch-floor
distribution from the mined corpora)." This scorer produces that
distribution: for every resolvable `spawn_agent` dispatch found across
ROLLOUT_PATHS (a flat list -- the caller supplies whatever rollout files
are in scope, e.g. one run's full session tree, or a mixed corpus slice;
resolution reuses `campaigns/codex-efficiency/rollout_parser.py`'s
`extract_spawns()`/`child_links()`, imported not forked), it reports:

  - `total_tokens`: the dispatch's own child rollout's LAST `token_count`
    event's `info.total_token_usage.total_tokens` value. **This is a
    CUMULATIVE counter, not a per-turn/exclusive spend** -- verified
    directly against a real rollout (`token_count` events climb
    monotonically turn over turn within one rollout file; see
    `campaigns/codex-efficiency/DESIGN.md`'s E6 calibration notes for an
    independently-observed real curve). Taking the LAST such event's
    cumulative total is correct and NON-double-counting for a single
    rollout file (it is simply "how many tokens had this session
    consumed by the time it finished"), which is exactly the floor cost
    of running that ONE dispatch. It must NOT be summed across multiple
    rollout files representing one logical chain (a later round's
    cumulative counter can already subsume an earlier round's cost if
    history was inherited on fork) -- `dispatch_floor()` never does this;
    each dispatch here is scored from exactly one child rollout. `None`
    if the child rollout has zero `token_count` events (observed in
    truncated/short-lived sessions).
  - `useful_output_tokens`: a rough token-count ESTIMATE (`len(text) //
    4`, the standard chars-per-token rule of thumb -- NOT a real
    tokenizer count) of the dispatch's own LAST `phase=="final_answer"`
    message (`rollout_parser.final_answers()`, phase-filtered). This is a
    proxy for "how much of the total cost was genuinely useful output"
    versus fixed overhead (tool-definition preamble, exploration, retries)
    -- deliberately structural (final-answer TEXT LENGTH only, never the
    text itself is read into any printed/committed output beyond its
    length). `0` if the dispatch produced no final_answer-phase message.
  - `floor_ratio`: `total_tokens / useful_output_tokens` -- the floor tax:
    how many total tokens were burned per token of delivered output. High
    for a trivial dispatch (fixed overhead dominates), lower for a
    substantial one. `None` if either operand is unavailable
    (`total_tokens is None` or `useful_output_tokens == 0`) -- an
    undefined ratio is reported as `None`, never coerced to 0 or an
    arbitrary sentinel.

Usage: `dispatch_floor(rollout_paths)`. Read-only; makes no writes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "codex-efficiency"))
import rollout_parser as rp
from scorer_common import cumulative_total_tokens as _cumulative_total_tokens
from scorer_common import resolve_child_path as _resolve_child_path


def _useful_output_tokens(path):
    """chars//4 estimate of the LAST phase=="final_answer" message in
    PATH, or 0 if none. See module docstring for the estimate's known
    imprecision (not a real tokenizer)."""
    finals = [f for f in rp.final_answers(path) if f.phase == "final_answer"]
    if not finals:
        return 0
    return len(finals[-1].message) // 4


def dispatch_floor(rollout_paths):
    """Every resolvable spawn_agent dispatch found across ROLLOUT_PATHS,
    scored from its own child rollout. `{"dispatches": []}` if no
    resolvable dispatch is found."""
    dispatches = []
    for parent_path in rollout_paths:
        spawns = rp.extract_spawns(parent_path)
        if not spawns:
            continue
        links = rp.child_links(parent_path)
        for s in spawns:
            thread_id = links.get(s.call_id)
            if not thread_id:
                continue
            child_path = _resolve_child_path(thread_id, rollout_paths)
            if not child_path:
                continue
            total_tokens = _cumulative_total_tokens(child_path)
            useful_output_tokens = _useful_output_tokens(child_path)
            floor_ratio = None
            if total_tokens is not None and useful_output_tokens:
                floor_ratio = total_tokens / useful_output_tokens
            dispatches.append({
                "task_name": s.task_name,
                "total_tokens": total_tokens,
                "useful_output_tokens": useful_output_tokens,
                "floor_ratio": floor_ratio,
            })
    return {"dispatches": dispatches}


def main(argv):
    if len(argv) < 2:
        print("usage: score_x6_floor.py ROLLOUT_PATH...", file=sys.stderr)
        return 1
    result = dispatch_floor(argv[1:])
    print(f"# X6 dispatch-floor -- {len(result['dispatches'])} dispatch(es)")
    for d in result["dispatches"]:
        ratio = f"{d['floor_ratio']:.1f}" if d["floor_ratio"] is not None else "n/a"
        print(f"  {d['task_name']}: total_tokens={d['total_tokens']} "
              f"useful_output_tokens={d['useful_output_tokens']} floor_ratio={ratio}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
