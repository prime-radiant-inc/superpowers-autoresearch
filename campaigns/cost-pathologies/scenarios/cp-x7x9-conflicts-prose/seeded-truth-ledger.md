# Seeded-truth ledger — cp-x7x9-conflicts-prose

Answer key for X7's blind-spot probe (Task 9). NEVER surfaced to the
Coding-Agent or the Gauntlet-Agent. Everything here is synthetic.

Per the binding carry-forward: "include one prose-Interfaces variant
plan (blind-spot probe)." This is that plan. Same domain and the same
delete-vs-need Files/verb shape as `cp-x7x9-conflicts`, but every
Interfaces block is written as plain prose — no backticks, no
paren-touching identifiers — instead of the backticked
single-identifier convention the other two siblings use.

## Conflict A — delete-vs-need sequencing (still mechanically visible)

**Location:** Task 2's Files block deletes `legacylib/legacy_store.py`;
Task 4's Files block modifies it. **Why it still registers:** Files
blocks use backticked paths regardless of how the Interfaces blocks in
this variant are written — `plan-conflict-scan`'s file-verb parsing is
independent of the Interfaces-block convention.

## Conflict B — cross-task interface gap (the blind spot)

**Location:** Task 3's Interfaces block (prose): "Consumes: the
entry-shape check Task 1's parser already exposes alongside its
parsing helper." **Ground truth:** Task 1's own Interfaces block (also
prose) only claims to produce "the entry-parsing helper... turning one
pipe-delimited log line into a structured record" — it says nothing
about a validation/shape-check helper. Task 3's Implementation text
compounds this: "calling the validation check named above rather than
re-implementing the shape check here" — so Task 3 neither produces the
check itself nor gets it from anywhere that actually provides it. This
is a genuine cross-task interface gap (the shape it names is asserted
to exist and is never declared anywhere), not a self-production
blind spot.

**Why X7-B cannot see it:** because both Task 1's Produces and Task
3's Consumes are written in prose with no backticked name and no
paren-touching identifier, `plan-conflict-scan`'s interface parser
extracts **zero** consumed and **zero** produced identifiers from
either block, so it has nothing to compare and cannot flag the gap.

**Verified against the committed plan:**

```
conflicts:
- Task 2 deletes `legacylib/legacy_store.py`; Task 4 still lists it (modify)
checked: 4 tasks, 8 file entries, 0 consumed and 0 produced interfaces, 0 in-task definitions
```

Only Conflict A (file-based) is found; Conflict B (interface-based,
prose-only) is silently missed — reproducing exactly the arm-manifest's
documented blind spot: "plans whose Interfaces blocks are pure prose
get a near-empty check."

**Expected handling per arm:** X7-B alone should surface only Conflict
A here and miss Conflict B — that is not a bug in the fixture, it is
the fixture doing its job. X7-A (prose-capable evidence-bearing scan)
is expected to have a real chance at Conflict B since it is not
limited to the mechanical script's parsing. A battery result where
X7-B's evidence table claims to have checked Task 3's interface
consumption is itself a finding (the arm is asserting evidence its own
mechanism cannot produce). Grading this fixture is about the CONTRAST
between X7-A and X7-B on the SAME plan, not about whether either arm
"passes" outright.
