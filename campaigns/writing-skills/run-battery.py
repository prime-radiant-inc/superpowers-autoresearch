#!/usr/bin/env python3
"""writing-skills authoring battery. Env:
  SKILL_FILE  — path to the writing-skills SKILL.md variant under test (REQUIRED)
  OUT_DIR     — results dir (default ./out/<skillfile-stem>)
  TASKS       — comma list (default t1..t7)
  REPS        — default 5
  MODEL       — default claude-opus-4-8 (the model that authors skills)
Caches per (task, rep); reruns fill gaps."""
import json, os, pathlib, time, urllib.request

API = "https://api.anthropic.com/v1/messages"
KEY = os.environ["ANTHROPIC_API_KEY"]
HERE = pathlib.Path(__file__).parent
SKILL = pathlib.Path(os.environ["SKILL_FILE"]).read_text()
MODEL = os.environ.get("MODEL", "claude-opus-4-8")
REPS = int(os.environ.get("REPS", "5"))
stem = pathlib.Path(os.environ["SKILL_FILE"]).resolve().parent.name
OUT = pathlib.Path(os.environ.get("OUT_DIR", HERE / "out" / stem))
TASKS = os.environ.get("TASKS", "t1,t2,t3,t4,t5,t6,t7").split(",")

SYSTEM = """You maintain the superpowers skill library. You author and edit
skills following your writing-skills training, reproduced in full below.
Apply it faithfully.

<writing-skills>
""" + SKILL + """
</writing-skills>"""

def call(payload, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(API, json.dumps(payload).encode(),
                {"x-api-key": KEY, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read())
        except Exception as e:
            if i == tries - 1: raise
            print(f"  retry {i+1}: {type(e).__name__}"); time.sleep(20 * (i + 1))

OUT.mkdir(parents=True, exist_ok=True)
for t in TASKS:
    user = (HERE / "tasks" / f"{t}.md").read_text()
    for rep in range(REPS):
        f = OUT / f"{t}-r{rep}.md"
        if f.exists() and f.stat().st_size > 200:
            print(f"cached {f.name}"); continue
        resp = call({"model": MODEL, "max_tokens": 4000, "system": SYSTEM,
                     "messages": [{"role": "user", "content": user}]})
        text = "".join(b.get("text", "") for b in resp["content"])
        f.write_text(text)
        print(f"{t} r{rep}: {len(text)} chars, out={resp['usage']['output_tokens']}")
print("battery complete:", OUT)
