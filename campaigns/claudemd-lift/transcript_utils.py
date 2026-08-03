"""Shared helpers for parsing `claude -p --output-format stream-json` transcripts.

Every probe's grade.py needs the same three things out of a transcript: the
ordered list of tool calls, the plain-text assistant narration, and the bash
commands that were actually run. This module gives one shared, tested
implementation so each grader isn't re-deriving stream-json parsing.

Transcript format: one JSON object per line (as written by `claude -p
--output-format stream-json`). Relevant event types:
  - "assistant": message with `.message.content` = list of blocks, each
    either {"type": "text", "text": ...} or {"type": "tool_use", "name":
    ..., "input": {...}}.
  - "result": final turn summary (usage, result text, is_error, etc).
Unrecognized/malformed lines are skipped rather than raising, so a grader
never crashes on a truncated or logging-noise transcript.
"""
from __future__ import annotations

import json
import os


def load_events(transcript_path):
    """Read a stream-json transcript file into a list of event dicts."""
    events = []
    with open(transcript_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def tool_calls(events):
    """Ordered list of {tool, args} for every tool_use block across the transcript."""
    calls = []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []) or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                calls.append({"tool": block.get("name", ""), "args": block.get("input", {}) or {}})
    return calls


def assistant_text(events):
    """All assistant free-text (not tool calls), concatenated in order, one block per line."""
    chunks = []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []) or []:
            if isinstance(block, dict) and block.get("type") == "text":
                t = block.get("text", "")
                if t:
                    chunks.append(t)
    return "\n".join(chunks)


def final_result_text(events):
    """The `result` field of the last "result" event, or "" if none."""
    text = ""
    for ev in events:
        if ev.get("type") == "result":
            text = ev.get("result") or ""
    return text


def bash_commands(events):
    """List of command strings from every Bash/Shell tool_use call, in order."""
    cmds = []
    for c in tool_calls(events):
        if c["tool"] in ("Bash", "Shell"):
            cmd = c["args"].get("command", c["args"].get("cmd", ""))
            if cmd:
                cmds.append(str(cmd))
    return cmds


def calls_of(events, *tool_names):
    """Tool calls whose name is in tool_names, in order."""
    return [c for c in tool_calls(events) if c["tool"] in tool_names]


def file_write_contents(events):
    """Text content of every Write/Edit tool_use call (new_string/content), in order.

    Covers both whole-file Write (`content`) and Edit (`new_string`), the two
    ways a grader typically needs to see what text ended up in a file.
    """
    out = []
    for c in calls_of(events, "Write", "Edit"):
        args = c["args"]
        for key in ("content", "new_string"):
            if key in args:
                out.append(str(args[key]))
    return out


def tool_results(events):
    """Text content of every tool_result block (bash output, file contents, etc), in order."""
    out = []
    for ev in events:
        if ev.get("type") != "user":
            continue
        for block in ev.get("message", {}).get("content", []) or []:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                content = block.get("content", "")
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            out.append(c.get("text", ""))
                elif isinstance(content, str):
                    out.append(content)
    return out


def full_text(events):
    """Assistant narration + tool results + final result text, concatenated (grep-friendly)."""
    return "\n".join([assistant_text(events)] + tool_results(events) + [final_result_text(events)])


def git_diff(workdir, args=None):
    """`git diff` against the fixture baseline commit, including new files.

    Runners are expected to `git init` + commit the fixture baseline before
    invoking claude, so graders can always diff against that baseline. New
    (untracked) files are intent-to-added (`git add -N`) first so they show
    up as additions in the diff without actually staging their content.
    Returns the diff text, or "" if git isn't available/initialized
    (defensive; a grader should treat that as ungraded rather than crash).
    """
    import subprocess
    try:
        subprocess.run(["git", "add", "-A", "-N"], cwd=workdir, capture_output=True,
                       text=True, timeout=30)
        cmd = ["git", "diff", "HEAD"]
        if args:
            cmd += list(args)
        out = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=30)
        return out.stdout
    except Exception:
        return ""


def diff_numstat(workdir):
    """[(added, removed, path), ...] vs the fixture baseline commit (new files included).

    `added`/`removed` are ints (or None for binary files, per `git diff --numstat`).
    """
    import subprocess
    try:
        subprocess.run(["git", "add", "-A", "-N"], cwd=workdir, capture_output=True,
                       text=True, timeout=30)
        out = subprocess.run(["git", "diff", "--numstat", "HEAD"], cwd=workdir,
                             capture_output=True, text=True, timeout=30)
    except Exception:
        return []
    rows = []
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, removed, path = parts
        rows.append((
            None if added == "-" else int(added),
            None if removed == "-" else int(removed),
            path,
        ))
    return rows


def added_lines_text(workdir):
    """Concatenated text of every added line (`+...`, excluding `+++` file
    headers) across `git diff HEAD` in workdir -- i.e. just the new code,
    for keyword/pattern scans that shouldn't match unchanged context lines."""
    diff = git_diff(workdir)
    lines = []
    for line in diff.splitlines():
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            lines.append(line[1:])
    return "\n".join(lines)


def changed_files(workdir):
    """Names of files with any working-tree change vs the fixture baseline commit."""
    import subprocess
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=workdir,
                             capture_output=True, text=True, timeout=30)
    except Exception:
        return []
    files = []
    for line in out.stdout.splitlines():
        line = line.rstrip("\n")
        if len(line) > 3:
            files.append(line[3:].strip())
    return files


def read_transcript_from_dir(rep_dir):
    """Convenience: the runner writes `transcript.jsonl` per rep; resolve it."""
    p = os.path.join(rep_dir, "transcript.jsonl")
    return p if os.path.exists(p) else None
