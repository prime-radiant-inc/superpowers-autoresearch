#!/usr/bin/env python3
"""E26: controller narration economy — does a one-line-narration recipe shrink
text-between-tool-calls? Opus, tools provided, measure text chars in response."""
import json, os, time, urllib.request, pathlib

API="https://api.anthropic.com/v1/messages"; KEY=os.environ["ANTHROPIC_API_KEY"]
OUT=pathlib.Path("/tmp/sdd-exp/autoresearch/e26-out"); OUT.mkdir(exist_ok=True)

TOOLS=[{"name":"Bash","description":"Run a shell command","input_schema":{"type":"object","properties":{"command":{"type":"string"},"description":{"type":"string"}},"required":["command"]}},
       {"name":"Agent","description":"Dispatch a subagent","input_schema":{"type":"object","properties":{"description":{"type":"string"},"model":{"type":"string"},"prompt":{"type":"string"}},"required":["description","prompt"]}}]

BASE_SYS = """You are the controller in subagent-driven development, executing a 7-task
plan. Per task: dispatch implementer (with brief+report files), then generate a
review package (scripts/review-package BASE HEAD prints the file path), then
dispatch the task reviewer with that path, adjudicate, record to the progress
ledger, move on. You have just received the Task 3 implementer's final message:

Status: DONE
Commits: 59edb67 feat: mandelbrot renderer
Tests: 9/9 passing, output pristine
Concerns: none
Report: .git/sdd/task-3-report.md

Base commit recorded before dispatch: 3d909bb. Continue the workflow."""

TERSE = """

Between tool calls, narrate at most one short line; the ledger and the tool
results carry the record."""

def call(payload, tries=3):
    for i in range(tries):
        try:
            req=urllib.request.Request(API, json.dumps(payload).encode(),
                {"x-api-key":KEY,"anthropic-version":"2023-06-01","content-type":"application/json"})
            with urllib.request.urlopen(req, timeout=300) as r: return json.loads(r.read())
        except Exception as e:
            if i==tries-1: raise
            time.sleep(15*(i+1))

for vname, sys_p in (("V0-none", BASE_SYS), ("V1-terse", BASE_SYS+TERSE)):
    for rep in range(5):
        f=OUT/f"{vname}-r{rep}.json"
        if f.exists(): continue
        resp=call({"model":"claude-opus-4-8","max_tokens":2000,"system":sys_p,
                   "tools":TOOLS,
                   "messages":[{"role":"user","content":"(continue)"}]})
        text="".join(b.get("text","") for b in resp["content"] if b.get("type")=="text")
        ncalls=sum(1 for b in resp["content"] if b.get("type")=="tool_use")
        f.write_text(json.dumps({"chars":len(text),"tools":ncalls,"text":text[:300]}))
        print(vname, rep, len(text), "narration chars,", ncalls, "tool calls")
