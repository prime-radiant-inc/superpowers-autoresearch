#!/usr/bin/env python3
"""First-pass classification of battery outputs. NOT a verdict engine —
every classification gets pasted with excerpts for driver review.
Usage: score-battery.py OUT_DIR"""
import re, sys, pathlib
OUT = pathlib.Path(sys.argv[1])
for f in sorted(OUT.glob('*.md')):
    m = f.read_text()
    sig = {
        'prohibition': bool(re.search(r'(?:do not|don\'t|never)\s+(?:re-?type|restate|repeat|copy|narrat|includ|add|write)', m, re.I)),
        'recipe': bool(re.search(r'(?:should contain|must (?:contain|include)|begin (?:directly )?with|consists of).{0,200}\(?1\)?', m, re.I|re.S)) or bool(re.search(r'^\s*(?:1\.|\(1\)).{10,}\n\s*(?:2\.|\(2\))', m, re.M)),
        'structural': bool(re.search(r'REQUIRED|template field|placeholder.{0,40}required|\[MODEL\]', m)),
        'word_budget': bool(re.search(r'\b(?:under|fewer than|at most|limit)\s+[\d,]+\s*(?:words|characters|lines)|word (?:budget|limit|count)', m, re.I)),
        'baseline_first': bool(re.search(r'baseline|RED|without the skill|watch.{0,20}fail|elicit', m, re.I)),
        'control': bool(re.search(r'no.?guidance control|control (?:group|arm|condition)|versus no guidance|against a control', m, re.I)),
        'n_reps': bool(re.search(r'\b(\d+)\s*(?:reps|samples|runs|trials|iterations)\b', m, re.I)),
        'pressure_scenario': bool(re.search(r'pressure scenario|subagent.{0,40}(?:scenario|test)', m, re.I)),
        'pushback': bool(re.search(r'(?:recommend against|would not add|caution|push back|instead of (?:a )?(?:length|word)|risk.{0,60}(?:test|content|cut))', m, re.I)),
    }
    flags = ' '.join(k for k, v in sig.items() if v)
    print(f"{f.name}: {flags}")
