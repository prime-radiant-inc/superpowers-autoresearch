#!/usr/bin/env python3
"""E21: reviewer final-message economy — current template vs no-preamble contract."""
import json, os, time, urllib.request, pathlib

API="https://api.anthropic.com/v1/messages"; KEY=os.environ["ANTHROPIC_API_KEY"]
MODEL="claude-sonnet-4-6"
OUT=pathlib.Path("/tmp/sdd-exp/autoresearch/e21-out"); OUT.mkdir(exist_ok=True)
SDD="/Users/jesse/git/superpowers/superpowers/.claude/worktrees/sdd-review-dispatch/evals/results/sdd-go-fractals-elicited-claude-20260611T034341Z-54de/coding-agent-workdir/.git/sdd"
BRIEF=open(SDD+"/task-2-brief.md").read()
REPORT=open(SDD+"/task-2-report.md").read()
DIFF=open(SDD+"/review-3d909bb..59edb67.diff").read()

TMPL = pathlib.Path("/tmp/sdd-exp/combo/skills/subagent-driven-development/task-reviewer-prompt.md").read_text()
core = TMPL.split("prompt: |",1)[1].split("```",1)[0]
core = core.replace("Read the task brief: [BRIEF_FILE]", "<task-brief>\n"+BRIEF+"\n</task-brief>")
core = core.replace("[GLOBAL_CONSTRAINTS]", "Go 1.21+; only external dep cobra; Mandelbrot gradient exactly \" .:-=+*#%@\"; output to stdout, errors to stderr non-zero exit")
core = core.replace("Read the implementer's report: [REPORT_FILE]", "<implementer-report>\n"+REPORT+"\n</implementer-report>")
core = core.replace("**Diff file:** [DIFF_FILE]", "**Diff (inline):**\n<review-package>\n"+DIFF+"\n</review-package>")
core = core.replace("[BASE_SHA]","3d909bb").replace("[HEAD_SHA]","59edb67")

TERSE = "\n\n    Your final message is the report itself: begin directly with the spec-compliance verdict line. Do not restate what you reviewed, describe your process, or add a closing summary — every line is either a verdict, a finding with file:line, or a check you ran.\n"
core = core.replace("Read the diff file once", "Read the inline diff once")
VARIANTS = {"V0-current": core, "V1-terse": core + TERSE}

def call(payload, tries=3):
    for i in range(tries):
        try:
            req=urllib.request.Request(API, json.dumps(payload).encode(),
                {"x-api-key":KEY,"anthropic-version":"2023-06-01","content-type":"application/json"})
            with urllib.request.urlopen(req, timeout=300) as r: return json.loads(r.read())
        except Exception as e:
            if i==tries-1: raise
            time.sleep(15*(i+1))

for vname, prompt in VARIANTS.items():
    for rep in range(5):
        f=OUT/f"{vname}-r{rep}.json"
        if f.exists(): print("cached", f.name); continue
        resp=call({"model":MODEL,"max_tokens":4000,
                   "messages":[{"role":"user","content":prompt}]})
        text="".join(b.get("text","") for b in resp["content"])
        f.write_text(json.dumps({"out_tokens":resp["usage"]["output_tokens"],"text":text}))
        print(vname, rep, resp["usage"]["output_tokens"], "out-tokens")
