#!/usr/bin/env python3
"""Recompute the X1 FULL cross-arm table with old vs new score_x1_chains.

Usage: task1_recompute_x1_table.py OLD_GIT_REF   (e.g. '1bf7035^')
The old scorer is materialized from git; the new one is the working tree.

Tests three candidate definitions of "mean novel-finding-rate" against the
published means (D .483 / A .679 / B .652 / C .577) using the OLD scorer,
then reports corrected values under the matching definition with the NEW.
"""
import importlib.util
import os
import sys
from statistics import mean

CAMP = "/Users/jesse/git/superpowers/superpowers-autoresearch/campaigns/cost-pathologies"
SCRATCH = None  # unused in committed form
LANES = [
    "/Users/jesse/git/superpowers/superpowers/evals/results",
    "/Users/jesse/git/superpowers/evals-lane-b/results",
]
ARMS = {"control": [], "x1a": [], "x1b": [], "x1c": []}
for lane in LANES:
    for d in sorted(os.listdir(lane)):
        if not d.startswith("cp-x1-buggy-sdd-"):
            continue  # excludes the stray cp-cp-* dir
        arm = d[len("cp-x1-buggy-sdd-"):].rsplit("-rep", 1)[0]
        if arm in ARMS:
            ARMS[arm].append(os.path.join(lane, d))

def rollouts(rep_dir):
    out = []
    for root, _dirs, files in os.walk(rep_dir):
        out.extend(os.path.join(root, f) for f in files if f.startswith("rollout-") and f.endswith(".jsonl"))
    return sorted(out)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

sys.path.insert(0, CAMP)  # for scorer_common
sys.path.insert(0, os.path.join(CAMP, "..", "codex-efficiency"))  # for rollout_parser
import subprocess, tempfile
with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
    tf.write(subprocess.check_output(["git", "-C", CAMP, "show", sys.argv[1] + ":campaigns/cost-pathologies/score_x1_chains.py"], text=True))
    old_path = tf.name
old = load("score_x1_old", old_path)
new = load("score_x1_new", os.path.join(CAMP, "score_x1_chains.py"))

for label, mod in [("OLD", old), ("NEW", new)]:
    print(f"== {label} ==")
    for arm, reps in ARMS.items():
        assert len(reps) == 4, (arm, reps)
        per_rep_rounds, per_rep_dispatch = [], []
        flat_rates, per_rep_means, per_chain_means = [], [], []
        for rep in reps:
            chains = mod.chain_stats(rollouts(rep))["chains"]
            per_rep_rounds.append(sum(c["rounds"] for c in chains))
            per_rep_dispatch.append(sum(c["dispatch_count"] for c in chains))
            rates = [r for c in chains for r in c["novel_finding_rate_per_round"]]
            flat_rates.extend(rates)
            if rates:
                per_rep_means.append(mean(rates))
            per_chain_means.extend(
                mean(c["novel_finding_rate_per_round"]) for c in chains if c["novel_finding_rate_per_round"]
            )
        print(
            f"{arm:8s} meanΣrounds={mean(per_rep_rounds):.2f} meanΣdispatch={mean(per_rep_dispatch):.2f} "
            f"rate[flat]={mean(flat_rates):.3f} rate[per-rep]={mean(per_rep_means):.3f} "
            f"rate[per-chain]={mean(per_chain_means):.3f}"
        )
