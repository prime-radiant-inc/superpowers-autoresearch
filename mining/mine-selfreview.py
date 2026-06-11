#!/usr/bin/env python3
"""E07: implementer self-review catch rate; E20: reviewers citing TDD evidence."""
import json, glob, sys, os, re
tot_impl, caught, cites = 0, 0, 0
tot_rev = 0
for rd in sys.argv[1:]:
    for p in glob.glob(rd+'/coding-agent-config/projects/*/*/subagents/agent-*.jsonl'):
        text = open(p).read()
        is_impl = 'You are implementing' in text[:8000]
        is_rev = 'You are reviewing' in text[:8000]
        if is_impl:
            tot_impl += 1
            # final message self-review content
            m = re.findall(r'[Ss]elf-review[^"]{0,400}', text)
            found = any(re.search(r'(found|caught|fixed|missed|added|notice)', x, re.I) and not re.search(r'(no issues|all good|clean|nothing|no findings|none)', x, re.I) for x in m)
            if found: caught += 1
        if is_rev:
            tot_rev += 1
            if re.search(r'(RED|GREEN).{0,80}(evidence|output|test)', text) or 'TDD Evidence' in text.split('You are reviewing')[-1][:6000]:
                cites += 1
print(f"E07: implementers={tot_impl}, self-review caught something: {caught} ({caught/max(tot_impl,1)*100:.0f}%)")
print(f"E20: reviewers={tot_rev}, referencing TDD evidence: {cites} ({cites/max(tot_rev,1)*100:.0f}%)")
