#!/usr/bin/env python3
"""E04/E14: controller report-file reads + cache health."""
import json, glob, sys, os
for rd in sys.argv[1:]:
    mains = [p for p in glob.glob(rd+'/coding-agent-config/projects/*/*.jsonl') if '/subagents/' not in p]
    if not mains: continue
    report_reads, total_reads, tasks = 0, 0, set()
    cache_read = inp = 0
    for line in open(mains[0]):
        try: d=json.loads(line)
        except: continue
        if d.get('type')=='assistant':
            u=d.get('message',{}).get('usage',{})
            cache_read += u.get('cache_read_input_tokens',0); inp += u.get('input_tokens',0)
            for b in d.get('message',{}).get('content',[]) or []:
                if isinstance(b,dict) and b.get('type')=='tool_use' and b.get('name')=='Read':
                    fp=str(b.get('input',{}).get('file_path',''))
                    total_reads+=1
                    if 'report' in fp: report_reads+=1
                    if 'task-' in fp and 'report' in fp:
                        tasks.add(fp)
    print(f"{os.path.basename(rd)[:55]}: controller Reads={total_reads}, report-file reads={report_reads} (distinct {len(tasks)}); cache_read={cache_read/1e6:.1f}M vs uncached input={inp/1000:.0f}k")
