"""Builds synthetic stream-json transcripts for grader unit tests.

No probe test in this package ever calls the real `claude` binary. These
helpers build handwritten event sequences shaped like `claude -p
--output-format stream-json` output, so graders can be TDD'd against known
inputs before any live run exists.
"""
from __future__ import annotations

import json
import os


def assistant_text(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def assistant_tool(tool, args):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": tool, "input": args}]}}


def tool_result(text):
    return {"type": "user", "message": {"content": [{"type": "tool_result", "content": text}]}}


def result(text, is_error=False):
    return {"type": "result", "result": text, "is_error": is_error, "num_turns": 1, "usage": {}}


def write_transcript(path, events):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    return path
