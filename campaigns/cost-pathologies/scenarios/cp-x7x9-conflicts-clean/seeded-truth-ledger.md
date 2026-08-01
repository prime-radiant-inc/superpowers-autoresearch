# Seeded-truth ledger — cp-x7x9-conflicts-clean

Answer key for X7's false-positive guard (Task 9). NEVER surfaced to
the Coding-Agent or the Gauntlet-Agent. Everything here is synthetic.

Sibling of `cp-x7x9-conflicts` (seeded conflicts) and
`cp-x7x9-conflicts-prose` (prose-Interfaces blind-spot probe) — same
domain (a log parser/store/summary/archive pipeline), deliberately
conflict-free.

## Guard purpose

Per the design doc: fixture includes "(c) NO conflict (false-positive
guard — an arm that blocks clean plans on invented conflicts fails)."
Every X7 arm run against this plan should report zero conflicts and
let Task 1 dispatch proceed uninterrupted.

**X7-B (mechanical scan), verified against the committed plan:**

```
no conflicts in the Files:/Interfaces: blocks or the task code
checked: 4 tasks, 8 file entries, 3 consumed and 4 produced interfaces, 1 in-task definitions
```

## Parser-gap probe (disclosed) — Task 3's multi-name backtick span

**Location:** Task 3's Interfaces block: `- Produces: \`count, total,
average\`` — three names inside ONE pair of backticks, comma-separated.
**What happens, mechanically:** `plan-conflict-scan`'s per-span
tokenizer takes the whole span between backticks as one token; a
multi-word, comma-and-space-containing token fails the identifier
regex (`^[A-Za-z_][A-Za-z0-9_]*$`) and is silently dropped — none of
`count`, `total`, or `average` registers as a produced interface. This
is the documented KNOWN parser gap (`campaigns/cost-pathologies/arm-manifest.md`,
"Multi-name backtick spans"), reproduced here deliberately as a single
disclosed probe spot, not as an accidental fixture-authoring mistake.

**Why this is safe to leave in a "clean" plan:** nothing downstream
consumes `count`, `total`, or `average` by name (Task 3 is a leaf;
nothing lists these as Consumes anywhere), so the silent drop produces
no spurious conflict and no missed real one — it exists purely so
Task 9's grading can observe whether an arm's checked-interface count
matches this fixture's known parser-visible total (4 produced, not 7)
as a calibration signal, and, for X7-A (prose-capable evidence-bearing
scan) specifically, whether it notices and reports the three names a
purely mechanical reading would miss.

**Expected handling:** no arm should raise a conflict finding
attributable to this span. X7-B's own printed "checked:" line naming 4
produced interfaces (not 7) is the expected, verified baseline a
battery run should reproduce; a battery run that gets a different
produced count here has a script or plan drift to investigate before
grading anything else.

## Self-produce shape — avoided

Every Consumes entry in this plan (`parse_entry` in Task 2,
`read_entry` in Tasks 3 and 4) is declared under a DIFFERENT, earlier
task's Produces block (Task 1 produces `parse_entry`; Task 2 produces
`read_entry`) — no task consumes a name only it itself implements
without a corresponding Produces declaration (the round-1 blind spot
documented in the arm-manifest, e.g. `mutation_events`). This fixture
deliberately does not exercise that shape, so a "no producer" finding
anywhere in this plan is unambiguously a false positive, not a
legitimate blind-spot hit.
