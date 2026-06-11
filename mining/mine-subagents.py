#!/usr/bin/env python3
"""Mine per-subagent tool-call profiles from run dirs (E02/E15 etc.)."""
import json, glob, sys, os, re

def subagent_profile(path):
    role, turns, tools, explore, edits = '?', 0, 0, 0, 0
    seen_edit = False
    for line in open(path):
        try: d = json.loads(line)
        except: continue
        t = d.get('type')
        if t == 'user' and role == '?':
            c = d.get('message', {}).get('content', '')
            if isinstance(c, list): c = ' '.join(str(x.get('text','')) for x in c if isinstance(x,dict))
            c = str(c)
            if 'You are implementing' in c or 'implementing Task' in c: role = 'impl'
            elif 'You are reviewing' in c or 'reviewing one task' in c: role = 'review'
            elif 'fix' in c[:200].lower(): role = 'fix'
            else: role = 'other'
        if t == 'assistant':
            turns += 1
            for b in d.get('message', {}).get('content', []) or []:
                if isinstance(b, dict) and b.get('type') == 'tool_use':
                    tools += 1
                    name = b.get('name', '')
                    if name in ('Edit', 'Write', 'MultiEdit', 'NotebookEdit'): seen_edit = True; edits += 1
                    elif name in ('Read', 'Grep', 'Glob', 'LS') and not seen_edit: explore += 1
    return role, turns, tools, explore, edits

for rd in sys.argv[1:]:
    subs = glob.glob(rd + '/coding-agent-config/projects/*/*/subagents/agent-*.jsonl')
    rows = [subagent_profile(p) for p in subs]
    from collections import defaultdict
    agg = defaultdict(lambda: [0,0,0,0,0])
    for role, turns, tools, explore, edits in rows:
        a = agg[role]; a[0]+=1; a[1]+=turns; a[2]+=tools; a[3]+=explore; a[4]+=edits
    label = os.path.basename(rd)[:60]
    print(f"\n{label}: {len(rows)} subagents")
    for role, (n, turns, tools, explore, edits) in sorted(agg.items()):
        print(f"  {role:7s} n={n:2d}  avg turns {turns/n:5.1f}  avg tools {tools/n:5.1f}  avg pre-edit explores {explore/n:4.1f}  avg edits {edits/n:4.1f}")
