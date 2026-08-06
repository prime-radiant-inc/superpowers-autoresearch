#!/usr/bin/env python3
"""Signal extractor for k1p-decision-consistency (the K1' cell).

usage: instruments.py <run_dir>          (cwd = coding-agent workdir)

Prints key=value lines consumed by checks.sh post(). Two signal
sources, both conservative — anything not classifiable with confidence
is `unknown` for hand-reading, never guessed; internal failures print
nothing and the caller keeps unknown defaults:

1. TREE (cwd): which envelope wire format Task 1 chose
   (dispatchqueue/envelope.py's WIRE_FORMAT constant, falling back to
   framing-marker classification) and which format the two envelope
   consumers implemented (eventlog.py = Task 3, replay.py = Task 5;
   `delegates` when a consumer imports envelope's helpers instead of
   framing locally — delegation is consistent by construction). Files
   missing at the root are looked up in worktree copies
   (.worktrees/*, .claude/worktrees/*) — stranded-tree reps — and the
   source is noted.

2. TRANSCRIPT ($QUORUM_RUN_DIR/trajectory.json, the cross-harness ATIF
   surface — same for codex and claude): handoff.md reads/writes
   (SDD deletes the plan workspace at finish, so the K1 verdict's
   lesson applies — the handoff's existence and content are visible
   only in tool-call records, not the final tree) and whether any
   handoff WRITE carries a format token (jsonl/lp32/json-lines/
   length-prefix) — the decision-recorded-in-handoff mechanism signal.
   On the base2 arm no handoff exists; writes=0 and the decision
   signal is n-a by construction.
"""
import json
import os
import re
import sys

FORMAT_TOKEN_RE = re.compile(
    r"\bjsonl\b|json[-_ ]?lines|\blp32\b|length[-_ ]?prefix", re.IGNORECASE
)
WIRE_CONST_RE = re.compile(r"""WIRE_FORMAT\s*=\s*["'](jsonl|lp32)["']""")
# Framing markers. LP32: 4-byte int framing calls or the format's name.
# JSONL: newline framing (a literal "\n"/b"\n" string or splitlines) or
# the format's name. json.dumps/sort_keys are payload-level and shared
# by both candidates, so they are deliberately NOT markers.
LP_MARK_RE = re.compile(
    r"to_bytes\s*\(\s*4|from_bytes\s*\(|struct\.(?:pack|unpack)\s*\(\s*['\"][<>!]?[IiLlQq]"
    r"|\blp32\b|length[-_ ]?prefix",
    re.IGNORECASE,
)
JSONL_MARK_RE = re.compile(
    r"\bjsonl\b|json[-_ ]?lines|\.splitlines\s*\(|b?['\"]\\n['\"]", re.IGNORECASE
)
DELEGATE_RE = re.compile(
    r"from\s+(?:dispatchqueue\s*\.\s*)?envelope\s+import"
    r"|from\s+\.\s*envelope\s+import"
    r"|import\s+(?:dispatchqueue\s*\.\s*)?envelope"
    r"|from\s+dispatchqueue\s+import\s+[^\n]*\benvelope\b"
    r"|\benvelope\s*\.\s*(?:encode_event|decode_stream|WIRE_FORMAT)",
)


def find_module(name):
    """Locate dispatchqueue/<name> at the root, else in worktree copies."""
    root = os.path.join("dispatchqueue", name)
    if os.path.isfile(root):
        return root, "root"
    for pat in (".worktrees", os.path.join(".claude", "worktrees")):
        if not os.path.isdir(pat):
            continue
        for wt in sorted(os.listdir(pat)):
            p = os.path.join(pat, wt, "dispatchqueue", name)
            if os.path.isfile(p):
                return p, "worktree"
    return None, "missing"


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def classify_markers(text):
    lp = bool(LP_MARK_RE.search(text))
    jl = bool(JSONL_MARK_RE.search(text))
    if lp and not jl:
        return "lp32"
    if jl and not lp:
        return "jsonl"
    if lp and jl:
        return "mixed-markers"
    return "no-markers"


def classify_task1():
    path, src = find_module("envelope.py")
    if path is None:
        return "missing", "none", "dispatchqueue/envelope.py absent"
    text = read_text(path)
    m = WIRE_CONST_RE.search(text)
    if m:
        return m.group(1), "wire-format-constant", "%s (%s)" % (path, src)
    marked = classify_markers(text)
    if marked in ("jsonl", "lp32"):
        return marked, "markers", "%s (%s)" % (path, src)
    return "unknown", marked, "%s (%s)" % (path, src)


def classify_consumer(name):
    path, src = find_module(name)
    if path is None:
        return "missing", "dispatchqueue/%s absent" % name
    text = read_text(path)
    delegates = bool(DELEGATE_RE.search(text))
    marked = classify_markers(text)
    where = "%s (%s%s)" % (path, src, "; also-imports-envelope" if delegates and marked in ("jsonl", "lp32") else "")
    if marked in ("jsonl", "lp32"):
        return marked, where
    if delegates:
        return "delegates", "%s (%s; imports envelope, no local framing)" % (path, src)
    return "unknown", "%s (%s; %s)" % (path, src, marked)


def consistency(t1, tc):
    if tc == "missing" or t1 == "missing":
        return "n-a"
    if t1 not in ("jsonl", "lp32"):
        return "unknown"
    if tc == "delegates":
        return "yes"
    if tc in ("jsonl", "lp32"):
        return "yes" if tc == t1 else "no"
    return "unknown"


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    out = {
        "served_model": "unknown",
        "t1_format": "unknown", "t1_src": "none", "t1_where": "not-scanned",
        "t3_format": "unknown", "t3_where": "not-scanned",
        "t5_format": "unknown", "t5_where": "not-scanned",
        "consist_t3": "unknown", "consist_t5": "unknown",
        "handoff_writes": "0", "handoff_reads": "0", "handoff_mentions": "0",
        "decision_in_handoff": "n-a",
    }

    # --- tree signals (cwd = workdir) --------------------------------
    try:
        t1, t1_src, t1_where = classify_task1()
        t3, t3_where = classify_consumer("eventlog.py")
        t5, t5_where = classify_consumer("replay.py")
        out.update(t1_format=t1, t1_src=t1_src, t1_where=t1_where,
                   t3_format=t3, t3_where=t3_where,
                   t5_format=t5, t5_where=t5_where,
                   consist_t3=consistency(t1, t3),
                   consist_t5=consistency(t1, t5))
    except Exception:
        pass

    # --- transcript signals ------------------------------------------
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

    mentions = writes = reads = 0
    decision = "n-a"
    write_re = re.compile(r"(>>|tee\s+-a)[^\n]*handoff\.md|handoff\.md[^\n]*\btee\s+-a")
    read_re = re.compile(r"\b(cat|sed|grep|head|tail|less|nl)\b[^\n]*handoff\.md")
    for s in agent_steps:
        for c in s.get("tool_calls") or []:
            if not isinstance(c, dict):
                continue
            try:
                blob = json.dumps(c, default=str)
            except Exception:
                blob = str(c)
            if "handoff.md" not in blob:
                continue
            mentions += 1
            fn = str(c.get("function_name", ""))
            is_write = fn in ("Write", "Edit") or write_re.search(blob) \
                or "Add File:" in blob or "Update File:" in blob \
                or "apply_patch" in blob
            if is_write:
                writes += 1
                if FORMAT_TOKEN_RE.search(blob):
                    decision = "yes"
                elif decision != "yes":
                    decision = "no"
            elif fn == "Read" or read_re.search(blob):
                reads += 1
    out["handoff_mentions"] = str(mentions)
    out["handoff_writes"] = str(writes)
    out["handoff_reads"] = str(reads)
    out["decision_in_handoff"] = decision

    for k, v in out.items():
        print("%s=%s" % (k, v))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
