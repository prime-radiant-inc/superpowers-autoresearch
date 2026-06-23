#!/usr/bin/env python3
"""Headless validation of the two new tool-mapping eval scenarios on Claude.

These are quorum scenarios (in superpowers/evals/scenarios/), but quorum FULL
needs an x-api-key (gauntlet). This validates the DETERMINISTIC behavior on the
subscription via the same isolated headless `claude -p` machinery as the
triggering harness, so we know the scenarios aren't vacuous:

  - global-tool-mapping-comprehension: agent dispatches a subagent (Agent/Task)
    AND (graded by gauntlet, diagnosed here) reads its *-tools.md.
  - claude-tool-mapping-applied: agent resolves "dispatch a subagent" -> Agent
    without being told; loading of claude-code-tools.md recorded as a diagnostic.

Usage: MODELS=sonnet,haiku REPS=3 OAUTH_TOKEN_FILE=/tmp/token \
         python3 harnesses/validate-toolmap-evals.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("th", os.path.join(HERE, "triggering-harness.py"))
th = importlib.util.module_from_spec(spec); spec.loader.exec_module(th)

ROOT = th.DEFAULT_ROOT
TOKEN = th.read_token()

EVALS = {
    "global-tool-mapping-comprehension": (
        "Superpowers skills are written in platform-neutral action language — "
        "for example, 'dispatch a subagent'. Find YOUR platform's Superpowers "
        "tool-mapping reference (the platform-specific *-tools.md file under the "
        "using-superpowers skill's references/ directory) and treat it as "
        "authoritative for translating an action into the concrete tool to call. "
        "Using the tool that file maps to the action 'dispatch a subagent', "
        "dispatch exactly one subagent whose entire job is to reply with exactly "
        "the token GLOBALMAP_OK. Then report that token back to me. Do not edit files.",
        "GLOBALMAP_OK",
    ),
    "claude-tool-mapping-applied": (
        "A Superpowers skill step says: 'Dispatch a subagent whose entire job is "
        "to reply with exactly the token CLAUDEMAP_OK, then report its result.' "
        "Carry out that step now. Do not edit files.",
        "CLAUDEMAP_OK",
    ),
}
SUBAGENT_TOOLS = {"Agent", "Task"}


def run(name, prompt, token_str, model, rep, timeout=300):
    home = tempfile.mkdtemp(prefix="sp-tm-home.")
    wd = tempfile.mkdtemp(prefix="sp-tm-wd.")
    th.seed_home(home)
    th.fixture_base_repo(wd)
    env = dict(os.environ)
    for k in ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "ANTHROPIC_API_KEY"):
        env.pop(k, None)
    env["HOME"] = home
    env["CLAUDE_CODE_OAUTH_TOKEN"] = token_str
    env["CLAUDE_CODE_FORCE_SESSION_PERSISTENCE"] = "1"
    env["DISABLE_AUTOUPDATER"] = "1"
    cmd = [th.CLAUDE_BIN, "-p", prompt, "--plugin-dir", ROOT, "--model", th.MODEL_IDS[model],
           "--output-format", "stream-json", "--verbose", "--dangerously-skip-permissions",
           "--max-turns", "12"]
    try:
        proc = subprocess.run(cmd, cwd=wd, env=env, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"dispatched": None, "read_mapping": None, "reported": None, "timeout": True}
    calls, final = th.parse_stream(proc.stdout)
    dispatched = any(c["tool"] in SUBAGENT_TOOLS for c in calls)
    read_mapping = any(
        c["tool"] in ("Read", "Bash") and "claude-code-tools.md" in str(c["args"])
        for c in calls)
    result_text = (final.get("result") or "")
    return {"dispatched": dispatched, "read_mapping": read_mapping,
            "reported": None, "tools": [c["tool"] for c in calls][:20],
            "num_turns": final.get("num_turns")}


def main():
    if not TOKEN:
        sys.stderr.write("no OAuth token (OAUTH_TOKEN_FILE)\n"); return 2
    models = os.environ.get("MODELS", "sonnet,haiku").split(",")
    reps = int(os.environ.get("REPS", "3"))
    for name, (prompt, tok) in EVALS.items():
        print(f"\n### {name}")
        for m in models:
            disp = rdm = 0; n = 0
            for r in range(reps):
                res = run(name, prompt, TOKEN, m.strip(), r)
                n += 1
                disp += 1 if res.get("dispatched") else 0
                rdm += 1 if res.get("read_mapping") else 0
                print(f"  {m:7s} rep{r}: dispatched_subagent={res.get('dispatched')} "
                      f"read_mapping_file={res.get('read_mapping')} tools={res.get('tools')}")
            print(f"  => {m}: dispatched {disp}/{n} (the pass signal) | read claude-code-tools.md {rdm}/{n} (loading diagnostic)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
