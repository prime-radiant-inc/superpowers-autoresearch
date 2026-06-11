#!/usr/bin/env python3
"""Micro-test #3: writing-plans No Placeholders section variants.
Stage 1: generation — which variant yields fewest placeholders?"""
import json, os, re, urllib.request, pathlib

API="https://api.anthropic.com/v1/messages"; KEY=os.environ["ANTHROPIC_API_KEY"]
MODEL="claude-opus-4-8"; OUT=pathlib.Path(os.environ.get("OUT_DIR","/tmp/sdd-exp/micro3/out"))
SPEC=pathlib.Path(os.environ.get("SPEC_FILE","/tmp/sdd-exp/micro3/fixture-spec.md")).read_text()

POSITIVE_RECIPE = """## Step Completeness

Every step must contain the actual content an engineer needs. Before
finalizing a step, confirm it has: the literal code to write (not a
description of it), a runnable command with expected output, types and
function names defined within this plan, and error handling shown
explicitly as code. A step is complete when an engineer could implement it
without asking any follow-up questions."""

BANNED_LIST = """These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task"""

SCAN_LIST = """2. **Placeholder scan:** read each step looking for these patterns; each one you find marks an incomplete step to fix:
   - "TBD", "TODO", "implement later", "fill in details"
   - "Add appropriate error handling" / "add validation" / "handle edge cases"
   - "Write tests for the above" (without actual test code)
   - "Similar to Task N" (the engineer may be reading tasks out of order — the code must be repeated in place)
   - Steps that describe what to do without showing how
   - References to types, functions, or methods not defined in any task"""

VARIANTS = {
 "V0-current": (
   "## No Placeholders\n\nEvery step must contain the actual content an engineer needs. " + BANNED_LIST,
   "2. **Placeholder scan:** Search your plan for red flags — any of the patterns from the \"No Placeholders\" section above. Fix them."),
 "V1-checklist": (
   POSITIVE_RECIPE,
   "2. **Placeholder scan:** Search your plan for incomplete steps and fix them."),
 "V2-relocated": (
   POSITIVE_RECIPE,
   SCAN_LIST),
 "V3-control": (
   "## Step Completeness\n\nEvery step must contain the actual content an engineer needs.",
   "2. **Placeholder scan:** Search your plan for incomplete steps and fix them."),
}

SYSTEM = """You are writing an implementation plan using the superpowers writing-plans skill. Write comprehensive plans assuming the engineer has zero context for the codebase. Document everything: which files to touch for each task, the code, the tests, how to verify. Bite-sized steps (write failing test / run it / implement / run / commit), exact file paths, exact commands with expected output.

{composition}

## Self-Review
After writing the complete plan, check it yourself:
1. **Spec coverage:** can you point to a task for each requirement?
{selfreview}
3. **Type consistency:** do names used in later tasks match earlier definitions?
Fix any issues inline before delivering."""

USER = """Write the complete implementation plan for this spec: one task per command plus a storage task (10 tasks). The plan must stay economical — target about 2,500 words total, and it must still let an engineer with zero context implement every task. Output ONLY the plan document.

<spec>
{spec}
</spec>"""

def call_with_retry(comp, sr, tries=3):
    for i in range(tries):
        try: return call(comp, sr)
        except Exception as e:
            if i == tries-1: raise
            print(f"  retry {i+1} after {type(e).__name__}", flush=True)

def call(comp, sr):
    body={"model":MODEL,"max_tokens":8000,
      "system":SYSTEM.format(composition=comp, selfreview=sr),
      "messages":[{"role":"user","content":USER.format(spec=SPEC)}]}
    req=urllib.request.Request(API,json.dumps(body).encode(),
      {"x-api-key":KEY,"anthropic-version":"2023-06-01","content-type":"application/json"})
    with urllib.request.urlopen(req,timeout=600) as r: d=json.loads(r.read())
    return "".join(b.get("text","") for b in d.get("content",[]) if b.get("type")=="text")

BANNED = re.compile(r'\bTBD\b|\bTODO\b|implement later|fill in details|appropriate error handling|handle edge cases|add validation\b|[Ww]rite tests for the above|[Ss]imilar to [Tt]ask|[Ss]ame as [Tt]ask', )
N=int(os.environ.get("N","5"))
print(f"{'variant':14} {'rep':3} {'chars':>6} {'banned':>6} {'codeblocks':>10} {'expected:':>9} {'steps':>5}")
for name,(comp,sr) in VARIANTS.items():
    for i in range(N):
        f=OUT/f"{name}-{i}.txt"
        if not f.exists(): f.write_text(call_with_retry(comp,sr))
        t=f.read_text()
        banned=[m.group(0) for m in BANNED.finditer(t)]
        steps=len(re.findall(r'- \[ \]', t))
        print(f"{name:14} {i:3} {len(t):6} {len(banned):6} {t.count('```'):10} {len(re.findall('Expected', t)):9} {steps:5}  {banned[:4]}")
