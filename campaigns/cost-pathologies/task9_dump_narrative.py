#!/usr/bin/env python3
"""Dump a rollout's root-thread narration + key tool calls in order, for
hand-verification (Task 9's pre-registered non-circular check). Prints
every event_msg/agent_message and every response_item/message (assistant),
plus a one-line marker for every Bash/exec function_call whose command text
is short enough to summarize, and every sub_agent_activity started/stopped
event -- enough to read the session's actual arc without loading raw JSONL.
"""
import json, sys, re

def load_jsonl(path):
    out = []
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out

def main():
    path = sys.argv[1]
    recs = load_jsonl(path)
    for r in recs:
        p = r.get("payload", {})
        t = r.get("type")
        ts = r.get("timestamp", "")[11:19]
        if t == "event_msg" and p.get("type") == "agent_message":
            print(f"[{ts}] NARRATION({p.get('phase')}): {p.get('message')}")
        elif t == "response_item" and p.get("type") == "message" and p.get("role") == "assistant":
            texts = [c.get("text", "") for c in p.get("content", []) if isinstance(c, dict)]
            if texts:
                print(f"[{ts}] ASSISTANT: {' '.join(texts)}")
        elif t == "event_msg" and p.get("type") == "sub_agent_activity":
            print(f"[{ts}] SUBAGENT {p.get('kind')}: {p.get('agent_path')}")
        elif t == "response_item" and p.get("type") == "function_call":
            name = p.get("name", "")
            args = p.get("arguments", "")
            if isinstance(args, str) and len(args) < 300:
                print(f"[{ts}] CALL {name}: {args}")
            else:
                print(f"[{ts}] CALL {name}: <{len(str(args))} chars>")
        elif t == "response_item" and p.get("type") == "agent_message":
            # inter-agent message observed in this thread's transcript
            content = p.get("content", [])
            txt = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
            print(f"[{ts}] INTER-AGENT {p.get('author')}->{p.get('recipient')}: {txt[:400]}")

if __name__ == "__main__":
    main()
