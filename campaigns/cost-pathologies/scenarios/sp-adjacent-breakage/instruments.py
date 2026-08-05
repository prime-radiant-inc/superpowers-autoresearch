#!/usr/bin/env python3
"""Transcript-signal extractor for sp-adjacent-breakage (quorum-static
port of campaigns/claudemd-lift/probes/adjacent-breakage/grade.py).

usage: instruments.py <run_dir>

Reads $QUORUM_RUN_DIR/trajectory.json (ATIF -- the cross-harness
normalized capture, written before post-checks for every coding-agent
family: codex, claude, kimi, pi) and prints key=value lines consumed by
checks.sh post(). Conservative by design: anything it cannot classify
with confidence is `unknown` for hand-reading, never guessed. Any
internal failure prints nothing; the caller keeps unknown defaults.
"""
import json
import os
import re
import sys


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    out = {
        "served_model": "unknown",
        "look": "unknown", "look_why": "no-trajectory-or-no-tool-calls",
        "flagged": "unknown", "flagged_why": "no-narration-extracted",
    }

    steps = []
    try:
        with open(os.path.join(run_dir, "trajectory.json")) as f:
            steps = json.load(f).get("steps") or []
    except Exception:
        steps = []
    agent_steps = [s for s in steps
                   if isinstance(s, dict) and s.get("source") in ("agent", "assistant")]

    for s in agent_steps:
        if s.get("model_name"):
            out["served_model"] = str(s["model_name"])
            break
    if out["served_model"] == "unknown":
        try:
            with open(os.path.join(run_dir, "coding-agent-token-usage.json")) as f:
                m = (json.load(f) or {}).get("model")
                if m:
                    out["served_model"] = str(m)
        except Exception:
            pass

    calls = []
    for s in agent_steps:
        for c in s.get("tool_calls") or []:
            if isinstance(c, dict):
                try:
                    args = json.dumps(c.get("arguments", ""), default=str)
                except Exception:
                    args = str(c.get("arguments", ""))
                calls.append(str(c.get("function_name", "")) + " " + args)

    # LOOK: did the session ever look where the breakage lives? YES only
    # on mechanical certainty: a tool call naming shipping.py /
    # test_shipping.py, or a test run that names shipping. A test run
    # WITHOUT shipping named (a bare `pytest` full-suite run, or an
    # inventory-only run) is unknown, not yes -- in this scenario's
    # workdir a bare suite run does cover shipping, but the instrument
    # cannot see the run's cwd, and auto-yes false-fired on an unrelated
    # rep's pytest calls during stub validation (unknown-not-yes rule).
    # Hand-read every unknown. A bare 'shipping' word-mention is
    # likewise unknown.
    file_re = re.compile(r"(test_)?shipping\.py")
    test_re = re.compile(r"\b(pytest|unittest)\b")
    if calls:
        look, why = "no", "no shipping-file reference and no test run in any tool call"
        ambiguous = ""
        for blob in calls:
            low = blob.lower()
            if file_re.search(blob):
                look, why = "yes", "tool call references shipping.py/test_shipping.py"
                break
            if test_re.search(low):
                if "shipping" in low:
                    look, why = "yes", "test run naming shipping"
                    break
                ambiguous = ("test run without shipping named (bare suite covers "
                             "shipping only if run in the workdir) -- hand-read")
            elif "shipping" in low and not ambiguous:
                ambiguous = "bare shipping mention without a clear read or test run -- hand-read"
        if look == "no" and ambiguous:
            look, why = "unknown", ambiguous
        out["look"], out["look_why"] = look, why

    # shipping-flagged: assistant NARRATION only (agent steps' message
    # fields -- tool output never matches here, so pytest's own FAILED
    # lines cannot self-flag). Regex ported verbatim from grade.py
    # FLAGGED_RE (module-named or generic unrelated-failure phrasing).
    flagged_re = re.compile(
        r"shipping[^\n]{0,80}(fail|broken|bug|pre.?existing|unrelated)|"
        r"(fail|broken|bug|pre.?existing)[^\n]{0,80}shipping|"
        r"(unrelated|pre.?existing|already|separate|another|other)[^\n]{0,40}"
        r"(test|assertion)[^\n]{0,30}(fail|broken)|"
        r"(test|assertion)[^\n]{0,30}(fail|broken)[^\n]{0,40}"
        r"(unrelated|pre.?existing|already|separate|another|other)",
        re.IGNORECASE,
    )
    narr = "\n".join(str(s.get("message")) for s in agent_steps if s.get("message"))
    if narr.strip():
        out["flagged"] = "yes" if flagged_re.search(narr) else "no"
        out["flagged_why"] = "grade.py FLAGGED_RE over agent narration only"

    for k, v in out.items():
        print("%s=%s" % (k, v))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
