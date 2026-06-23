#!/usr/bin/env python3
"""Bootstrap-compression autoresearch loop driver.

Ties together the two primitives for the campaign in
`logs/2026-06-21-bootstrap-compression.md`:

  1. measure-bootstrap-tokens.py  -> token cost of each variant bootstrap
  2. triggering-harness.py         -> auto-trigger pass-rate of each variant

For every variant `using-superpowers/SKILL.md`, it builds a scratch plugin root
(a minimal copy of the superpowers plugin with that SKILL.md swapped in), measures
tokens, runs the triggering harness across models/scenarios, and prints a single
comparison table: tokens + Δ% vs baseline, and pass-rate per (scenario, model).

The scratch root is reused; only the one SKILL.md is swapped per variant, so the
SessionStart hook injects the variant bootstrap exactly as in a real session.

Variants:
  - "baseline" is ALWAYS the live `skills/using-superpowers/SKILL.md`.
  - Every `*.md` in VARIANTS_DIR (default ./variants/bootstrap/) is a candidate.

Usage:
    MODELS=opus,sonnet,haiku REPS=5 python3 harnesses/compression-loop.py
    VARIANTS=baseline,v1-no-digraph MODELS=sonnet REPS=3 python3 harnesses/compression-loop.py

Env:
    MODELS, REPS, SCENARIOS, MAX_TURNS, TIMEOUT  -> passed through to the harness
    VARIANTS_DIR   dir of candidate variant SKILL.md files (default ./variants/bootstrap)
    VARIANTS       csv to restrict which variants run (names without .md; "baseline" allowed)
    SCRATCH_ROOT   where to build the swappable plugin root (default ./out/scratch-plugin)
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AR_ROOT = os.path.dirname(HERE)
REPO_PARENT = os.path.dirname(AR_ROOT)
SUPERPOWERS_REPO = os.path.join(REPO_PARENT, "superpowers")
LIVE_SKILL = os.path.join(SUPERPOWERS_REPO, "skills", "using-superpowers", "SKILL.md")

# Minimal set of plugin dirs --plugin-dir needs to load skills + the SessionStart hook.
PLUGIN_DIRS = [".claude-plugin", "skills", "hooks", "commands", "agents"]


def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


meter = _load("meter", os.path.join(HERE, "measure-bootstrap-tokens.py"))


def measure_tokens(skill_md):
    blob = meter.injected_blob(skill_md)
    exact = meter.api_token_count(blob)
    return exact if exact is not None else meter.estimate_tokens(blob), (exact is not None)


def build_scratch_root(scratch):
    """One-time: copy the minimal plugin into `scratch` (idempotent refresh)."""
    if os.path.exists(scratch):
        shutil.rmtree(scratch)
    os.makedirs(scratch)
    for d in PLUGIN_DIRS:
        src = os.path.join(SUPERPOWERS_REPO, d)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(scratch, d), symlinks=True)
    # carry any top-level files the plugin manifest may want
    for f in ("README.md",):
        s = os.path.join(SUPERPOWERS_REPO, f)
        if os.path.isfile(s):
            shutil.copy2(s, os.path.join(scratch, f))


def swap_skill(scratch, skill_md):
    dst = os.path.join(scratch, "skills", "using-superpowers", "SKILL.md")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(skill_md, dst)


def discover_variants():
    variants = [("baseline", LIVE_SKILL)]
    vdir = os.environ.get("VARIANTS_DIR", os.path.join(AR_ROOT, "variants", "bootstrap"))
    if os.path.isdir(vdir):
        for fn in sorted(os.listdir(vdir)):
            if fn.endswith(".md"):
                variants.append((fn[:-3], os.path.join(vdir, fn)))
    only = os.environ.get("VARIANTS")
    if only:
        keep = {s.strip() for s in only.split(",")}
        variants = [v for v in variants if v[0] in keep]
    return variants


def variant_hash(skill_md):
    return hashlib.sha256(open(skill_md, "rb").read()).hexdigest()[:12]


def run_harness(scratch, skill_md):
    """Run the harness; let it use its default hash-keyed OUT_DIR so per-run
    results are cached and reused across the H0 sweep and loop reruns (a
    byte-identical baseline SKILL.md hashes the same -> its cache is reused)."""
    env = dict(os.environ)
    env["SUPERPOWERS_ROOT"] = scratch
    env.pop("OUT_DIR", None)
    subprocess.run([sys.executable, os.path.join(HERE, "triggering-harness.py")],
                   env=env, check=False)
    rp = os.path.join(AR_ROOT, "out", "triggering", variant_hash(skill_md), "results.json")
    if os.path.exists(rp):
        with open(rp) as f:
            return json.load(f)
    return []


def passrate(results):
    grid = {}
    for r in results:
        grid.setdefault((r["scenario"], r["model"]), []).append(1 if r.get("passed") else 0)
    return grid


def main():
    if not meter.api_token_count(meter.injected_blob(LIVE_SKILL)):
        print("(token counts are chars/3.7 ESTIMATES — no x-api-key for exact)\n")
    scratch = os.path.abspath(os.environ.get("SCRATCH_ROOT", os.path.join(AR_ROOT, "out", "scratch-plugin")))
    variants = discover_variants()
    print(f"variants: {[v[0] for v in variants]}")
    build_scratch_root(scratch)

    base_tokens = None
    rows = []
    for name, skill_md in variants:
        toks, exact = measure_tokens(skill_md)
        if name == "baseline":
            base_tokens = toks
        swap_skill(scratch, skill_md)
        print(f"\n##### VARIANT {name}  ({toks} tokens{'' if exact else ' est'}) #####")
        results = run_harness(scratch, skill_md)
        rows.append((name, toks, passrate(results)))

    # comparison table
    print("\n================= CAMPAIGN COMPARISON =================")
    all_keys = sorted({k for _, _, g in rows for k in g})
    print(f"{'variant':22s} {'tokens':>8s} {'Δ%':>7s}  pass-rates")
    for name, toks, grid in rows:
        d = f"{(toks - base_tokens) / base_tokens * 100:+.0f}%" if base_tokens else "—"
        cells = []
        for k in all_keys:
            v = grid.get(k)
            if v:
                cells.append(f"{k[0].replace('triggering-','').replace('superpowers-','')[:14]}/{k[1][:3]}={sum(v)}/{len(v)}")
        print(f"{name:22s} {toks:>8d} {d:>7s}  " + "  ".join(cells))
    with open(os.path.join(AR_ROOT, "out", "campaign-results.json"), "w") as f:
        json.dump([{"variant": n, "tokens": t,
                    "passrates": {f"{k[0]}|{k[1]}": v for k, v in g.items()}} for n, t, g in rows], f, indent=2)
    print("\nwrote out/campaign-results.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
