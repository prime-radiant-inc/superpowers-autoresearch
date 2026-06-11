#!/usr/bin/env python3
"""Score micro4 plans. Print per-sample metrics + task titles for the
mandatory manual inspection pass."""
import re, pathlib, statistics
OUT = pathlib.Path("/tmp/sdd-exp/micro4/out")
GRADIENT = '" .:-=+*#%@"'

def score(p):
    m = p.read_text()
    tasks = re.findall(r'^#{2,3} Task \d+[:.]?\s*(.*)', m, re.M)
    n = len(tasks)
    has_gc = bool(re.search(r'^#{1,3} Global Constraints', m, re.M))
    gc_fidelity = sum([' .:-=+*#%@' in m, 'cobra' in m.lower(), '1.21' in m])
    ifc = len(re.findall(r'\*\*Interfaces:?\*\*|^Interfaces:', m, re.M))
    return n, tasks, has_gc, gc_fidelity, ifc

rows = {}
for p in sorted(OUT.glob('*.md')):
    v = p.name.rsplit('-r', 1)[0]
    n, tasks, gc, fid, ifc = score(p)
    rows.setdefault(v, []).append((p.name, n, gc, fid, ifc, tasks))

for v, rs in rows.items():
    ns = [r[1] for r in rs]
    print(f"\n=== {v}: tasks mean {statistics.mean(ns):.1f} range {min(ns)}-{max(ns)} | "
          f"GC header {sum(1 for r in rs if r[2])}/{len(rs)} | "
          f"interfaces-block count avg {statistics.mean(r[4] for r in rs):.1f}")
    for name, n, gc, fid, ifc, tasks in rs:
        print(f"  {name}: {n} tasks, GC={'Y' if gc else 'n'}(fid {fid}/3), ifc-blocks={ifc}")
        for t in tasks: print(f"      - {t}")
