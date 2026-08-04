#!/usr/bin/env python3
"""Metric-split scorer for the d1-family verification-dedupe batteries
(pre-registered with pd/d1s: scorer first, baselines from existing reps,
then the battery).

Classifies each CONTROLLER full-suite pytest run as:
  redundant   no tree-changing controller action since the last
              full-suite run whose output was green — the class the
              d1 arms target ("run again to be safe")
  fresh       first full-suite run, or a tree-changing action (merge,
              patch, file write, checkout/reset) happened since the
              last full run, or the last run was not green
Focused runs (a named test file/node) are counted separately and never
against the bar — they are the compliant "specific doubt" class.

The controller's checkout only changes through its own exec/patch
events (subagents work in .worktrees until merged), so intervening
tree change is detectable from the controller rollout alone. Output is
JSON per rep; spot hand-reads stay mandatory for verdicts.

Usage: score_d1_split.py REP_DIR [REP_DIR ...]
"""
import json
import os
import re
import sys

FULL_SUITE_RX = re.compile(
    r"pytest\s+tests/?(?:\s|;|\"|$)|pytest\s*(?:;|\"|$)|-m\s+pytest\s+tests/?(?:\s|;|\"|$)|-m\s+pytest\s*(?:;|\"|$)")
PYTEST_RX = re.compile(r"\bpytest\b")
# git commit / git add are deliberately NOT tree changes: they move the
# commit ID / index over an unchanged working tree, and "fresh commit →
# rerun to be safe" is exactly the redundant class the d1 arms target
# (both X11 and d1p no-uptake elicitations named the post-commit habit).
# File writes count only on code-ish paths: ledger/report/doc writes
# (.md, .txt — the controller's progress ledger churns constantly) do
# not invalidate test evidence and must not launder a following rerun
# into "fresh".
#
# git merge is deliberately NOT invalidating: in SDD the merged branch
# was just implementer-tested (and reviewer-approved) on exactly the
# tree the merge adopts, so evidence exists for the post-merge tree —
# a post-merge "confirm it still passes" run is the X11/d1p redundant
# class, not a fresh need. Cherry-pick/rebase DO compose a new tree
# no seat has tested; they stay invalidating.
_CODE_EXT = r"\.(?:py|js|ts|tsx|jsx|toml|cfg|ini|yaml|yml|json)"
TREE_CHANGE_RX = re.compile(
    r"git\s+(?:cherry-pick|apply|checkout|reset|revert|rebase|pull|rm|mv)"
    rf"|sed\s+-i[^|;]*{_CODE_EXT}|tee\s+[^|;]*{_CODE_EXT}"
    rf"|>\s*[A-Za-z0-9_./-]+{_CODE_EXT}"
    rf"|\bmv\s+[^|;]*{_CODE_EXT}|\brm\s+[^|;]*{_CODE_EXT}")
GREEN_RX = re.compile(r"\bpassed\b")
RED_RX = re.compile(r"\bfailed\b|\berror\b", re.I)


def controller_rollout(rep):
    rolls = []
    for root, _d, files in os.walk(rep):
        rolls += [os.path.join(root, f) for f in files
                  if f.startswith("rollout-") and f.endswith(".jsonl")]
    return max(rolls, key=os.path.getsize) if rolls else None


def score_rep(rep):
    ctrl = controller_rollout(rep)
    if not ctrl:
        return {"rep": os.path.basename(rep), "error": "no rollouts"}
    redundant = fresh = focused = 0
    pending_output_for = None   # "full" when awaiting a full run's result
    tree_changed = True         # first run is always fresh
    last_full_green = False
    for line in open(ctrl, errors="replace"):
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        p = j.get("payload") or {}
        t = p.get("type")
        if t == "patch_apply_end" or j.get("type") == "patch_apply_end":
            tree_changed = True
            continue
        if t == "custom_tool_call":
            cmd = p.get("input") or ""
            if PYTEST_RX.search(cmd) and "--version" not in cmd:
                if FULL_SUITE_RX.search(cmd):
                    if tree_changed or not last_full_green:
                        fresh += 1
                    else:
                        redundant += 1
                    pending_output_for = "full"
                    tree_changed = False
                else:
                    focused += 1
                    pending_output_for = None
            elif TREE_CHANGE_RX.search(cmd):
                tree_changed = True
                pending_output_for = None
            else:
                pending_output_for = None
        elif t == "custom_tool_call_output" and pending_output_for == "full":
            out = p.get("output")
            if isinstance(out, list):
                out = " ".join(x.get("text", "") for x in out if isinstance(x, dict))
            out = out or ""
            last_full_green = bool(GREEN_RX.search(out)) and not RED_RX.search(out)
            pending_output_for = None
    return {"rep": os.path.basename(rep), "redundant": redundant,
            "fresh": fresh, "focused": focused,
            "controller": os.path.basename(ctrl)[:40]}


def main():
    for rep in sys.argv[1:]:
        print(json.dumps(score_rep(rep)))


if __name__ == "__main__":
    main()
