#!/usr/bin/env python3
"""Aggregate the bootstrap-compression campaign into one matrix.

Scans out/triggering/<hash>/ run dirs, maps each hash back to a variant name
(baseline + variants/bootstrap/*.md), and prints pass-rate per
variant × scenario × model, plus token cost. Read-only; no API calls.

Usage: python3 harnesses/report.py
"""
import glob
import hashlib
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
AR_ROOT = os.path.dirname(HERE)
REPO_PARENT = os.path.dirname(AR_ROOT)
LIVE = os.path.join(REPO_PARENT, "superpowers", "skills", "using-superpowers", "SKILL.md")

import importlib.util
spec = importlib.util.spec_from_file_location("meter", os.path.join(HERE, "measure-bootstrap-tokens.py"))
meter = importlib.util.module_from_spec(spec); spec.loader.exec_module(meter)


def vh(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]


def tokens(p):
    blob = meter.injected_blob(p)
    return meter.api_token_count(blob) or meter.estimate_tokens(blob)


def variant_map():
    m = {vh(LIVE): ("baseline", LIVE)}
    for f in sorted(glob.glob(os.path.join(AR_ROOT, "variants", "bootstrap", "*.md"))):
        name = os.path.basename(f)[:-3]
        m[vh(f)] = (name, f)
    return m


def main():
    vm = variant_map()
    base_tok = tokens(LIVE)
    # gather: (variant, scenario, model) -> [pass ints]
    data = defaultdict(list)
    scen_set, model_set = set(), set()
    for d in glob.glob(os.path.join(AR_ROOT, "out", "triggering", "*")):
        h = os.path.basename(d)
        if h not in vm:
            continue
        vname = vm[h][0]
        for x in glob.glob(os.path.join(d, "*.json")):
            if x.endswith("results.json"):
                continue
            r = json.load(open(x))
            data[(vname, r["scenario"], r["model"])].append(1 if r.get("passed") else 0)
            scen_set.add(r["scenario"]); model_set.add(r["model"])

    models = [m for m in ["opus", "sonnet", "haiku"] if m in model_set]
    # order scenarios: probes first
    order = ["triggering-systematic-debugging", "superpowers-bootstrap",
             "brainstorming-resists-jump-to-implementation", "cost-checkbox-over-trigger",
             "triggering-executing-plans", "triggering-finishing-a-development-branch",
             "triggering-dispatching-parallel-agents", "triggering-requesting-code-review",
             "triggering-test-driven-development", "triggering-writing-plans"]
    scenarios = [s for s in order if s in scen_set] + sorted(scen_set - set(order))

    # variant order by token size desc
    vnames = sorted({k[0] for k in data}, key=lambda n: -tokens(dict(vm.values()).get(n, LIVE)) if n in dict((v[0], v[1]) for v in vm.values()) else 0)
    name_to_path = {v[0]: v[1] for v in vm.values()}

    print("BOOTSTRAP COMPRESSION CAMPAIGN — RESULTS MATRIX")
    print(f"(token mode: {'EXACT' if meter.api_token_count(meter.injected_blob(LIVE)) else 'chars/3.7 ESTIMATE'}; baseline={base_tok} tok)\n")
    for s in scenarios:
        note = "  [over-trigger: pass = NOT fired]" if s == "cost-checkbox-over-trigger" else ""
        print(f"### {s}{note}")
        header = "  " + f"{'variant':26s} {'tokens':>7s} {'Δ%':>6s}  " + " ".join(f"{m:>7s}" for m in models)
        print(header)
        for vn in sorted(name_to_path, key=lambda n: -tokens(name_to_path[n])):
            cells = []
            any_data = False
            for m in models:
                v = data.get((vn, s, m), [])
                if v:
                    any_data = True
                    cells.append(f"{sum(v)}/{len(v)}")
                else:
                    cells.append("—")
            if not any_data:
                continue
            tk = tokens(name_to_path[vn])
            d = f"{(tk-base_tok)/base_tok*100:+.0f}%" if base_tok else "—"
            print("  " + f"{vn:26s} {tk:>7d} {d:>6s}  " + " ".join(f"{c:>7s}" for c in cells))
        print()


if __name__ == "__main__":
    main()
