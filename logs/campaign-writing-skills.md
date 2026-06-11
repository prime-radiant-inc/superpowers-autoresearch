# Campaign log — writing-skills composition doctrine
(append-only; researcher records, driver verdicts)

---
## S1 — RED battery
Date: 2026-06-11
Command: `cd /Users/jesse/git/prime-radiant-inc/superpowers-autoresearch/campaigns/writing-skills && set -a && source ~/git/prime-radiant-inc/serf/.env && set +a && SKILL_FILE=/Users/jesse/git/superpowers/superpowers/.claude/worktrees/writing-skills-research/skills/writing-skills/SKILL.md python3 run-battery.py`
Status: COMPLETE
Output dir: /Users/jesse/git/prime-radiant-inc/superpowers-autoresearch/campaigns/writing-skills/out/writing-skills/
Files: 35/35 (t1-r0..t7-r4)
Output token range: 1107–2171 per sample
Raw output log:
```
t1 r0: 3850 chars, out=1332
t1 r1: 4327 chars, out=1543
t1 r2: 4047 chars, out=1360
t1 r3: 3860 chars, out=1286
t1 r4: 4229 chars, out=1460
t2 r0: 4033 chars, out=1388
t2 r1: 4584 chars, out=1568
t2 r2: 3278 chars, out=1164
t2 r3: 4497 chars, out=1549
t2 r4: 4405 chars, out=1601
t3 r0: 3630 chars, out=1233
t3 r1: 3377 chars, out=1136
t3 r2: 3890 chars, out=1332
t3 r3: 3762 chars, out=1290
t3 r4: 3792 chars, out=1300
t4 r0: 3490 chars, out=1210
t4 r1: 3220 chars, out=1107
t4 r2: 3830 chars, out=1289
t4 r3: 4095 chars, out=1384
t4 r4: 3446 chars, out=1160
t5 r0: 3652 chars, out=1287
t5 r1: 4831 chars, out=1639
t5 r2: 3468 chars, out=1195
t5 r3: 3680 chars, out=1347
t5 r4: 3825 chars, out=1338
t6 r0: 3974 chars, out=1359
t6 r1: 3965 chars, out=1350
t6 r2: 3590 chars, out=1200
t6 r3: 4345 chars, out=1476
t6 r4: 3807 chars, out=1197
t7 r0: 4967 chars, out=1684
t7 r1: 5829 chars, out=2171
t7 r2: 5251 chars, out=1892
t7 r3: 4246 chars, out=1583
t7 r4: 4868 chars, out=1694
```

STATUS: STEP-DONE S1
Completed: S1
Outputs: out/writing-skills/ (35 files)
Anomalies: none
Next: S2 — first-pass scoring

---
## S2 — First-pass scoring
Date: 2026-06-11
Command: `python3 score-battery.py out/writing-skills`
Full scorer output:
```
t1-r0.md: prohibition recipe baseline_first pressure_scenario
t1-r1.md: prohibition baseline_first pressure_scenario
t1-r2.md: prohibition recipe baseline_first pressure_scenario pushback
t1-r3.md: prohibition baseline_first pressure_scenario
t1-r4.md: prohibition recipe baseline_first pressure_scenario
t2-r0.md: prohibition recipe structural baseline_first
t2-r1.md: prohibition recipe baseline_first
t2-r2.md: prohibition recipe structural baseline_first
t2-r3.md: recipe structural baseline_first
t2-r4.md: prohibition recipe baseline_first pressure_scenario
t3-r0.md: baseline_first pressure_scenario pushback
t3-r1.md: recipe baseline_first pressure_scenario
t3-r2.md: recipe baseline_first pressure_scenario
t3-r3.md: recipe baseline_first pressure_scenario pushback
t3-r4.md: recipe baseline_first
t4-r0.md: recipe baseline_first
t4-r1.md: recipe baseline_first pushback
t4-r2.md: recipe baseline_first pushback
t4-r3.md: recipe baseline_first pushback
t4-r4.md: recipe baseline_first pushback
t5-r0.md: prohibition recipe baseline_first pressure_scenario pushback
t5-r1.md: recipe baseline_first
t5-r2.md: recipe baseline_first pressure_scenario pushback
t5-r3.md: recipe baseline_first n_reps pressure_scenario
t5-r4.md: recipe baseline_first pressure_scenario pushback
t6-r0.md: recipe baseline_first pressure_scenario
t6-r1.md: structural baseline_first pressure_scenario
t6-r2.md: recipe structural baseline_first pressure_scenario
t6-r3.md: recipe baseline_first pressure_scenario
t6-r4.md: recipe baseline_first pressure_scenario
t7-r0.md: recipe baseline_first n_reps pressure_scenario
t7-r1.md: recipe baseline_first
t7-r2.md: prohibition recipe baseline_first n_reps
t7-r3.md: recipe baseline_first n_reps
t7-r4.md: recipe baseline_first
```

STATUS: STEP-DONE S2
Completed: S1, S2
Outputs: scorer stdout above
Anomalies: none
Next: S3 — excerpt extraction

---
## S3 — Excerpt extraction
Date: 2026-06-11
(verbatim proposed guidance text section, up to 25 lines, per sample)

### t1-r0.md
task: t1  rep: 0  flags: prohibition recipe baseline_first pressure_scenario
excerpt:
```markdown
## Never re-type exact values into dispatch prompts

Exact values already live in the task brief the subagent reads:
magic strings, version numbers, function signatures, file paths,
config keys, error messages. Re-typing them is transcription —
and transcription ships bugs.

**Rule:** Dispatch prompts reference values by location, never by copy.

| Don't | Do |
|-------|-----|
| "Set timeout to 30000ms" | "Use the timeout value in the brief" |
| "Implement `fetchUser(id: string)`" | "Implement the signature given in the brief" |
| "The error is `ENOTEMPTY`" | "Match the error string named in the brief" |

If a value matters enough to be exact, it lives in the brief and is
referenced by name. The dispatch prompt points; the brief is the
source of truth.

**Red flags — STOP, you're about to transcribe:**
- You're typing a quoted string that appears in the brief
- You're copying a function signature into the prompt
- "I'll just paste it so the subagent doesn't have to look it up"
- "It's a short value, transcription won't hurt here"
- "Referencing is more work than just typing it"
```
...[truncated at 25 lines]

### t1-r1.md
task: t1  rep: 1  flags: prohibition baseline_first pressure_scenario
excerpt:
```markdown
## Never Re-Type Exact Values Into Dispatch Prompts

The per-task brief is the single source of truth for exact values:
magic strings, version numbers, function signatures, file paths,
config keys. The implementer subagent reads the brief directly.

**In dispatch prompts, reference — never reproduce — exact values.**

✅ "Implement the retry wrapper per the signature in your brief
    under `## Target Signature`."
❌ "Implement `retryWithBackoff(fn, maxAttempts=5, baseDelayMs=200)`."

**Why:** Every re-typed value is a transcription you can get wrong.
Re-typed values have already shipped bugs. The brief cannot drift
from itself; a copy can.

### Red Flags — STOP

- Typing a literal value that also appears in the brief
- "I'll just inline it so the prompt is self-contained"
- "The subagent might miss it in the brief"
- "It's only one number / one string"
- Copy-pasting a signature, then editing it in the prompt

**All of these mean: delete the literal, point to the brief section.**
```
...[truncated at 25 lines]

### t1-r2.md
task: t1  rep: 2  flags: prohibition recipe baseline_first pressure_scenario pushback
excerpt:
I'll write a *candidate* so we have something concrete to test against, but this is a hypothesis, not a deliverable. After baseline testing it will almost certainly change.

> **Reference exact values, never re-type them.** The per-task brief file is the single source of truth for magic strings, version numbers, function signatures, and other exact values. When dispatching, point the implementer at the brief — do not copy exact values into the dispatch prompt.
>
> **Why:** Re-typing exact values introduces transcription errors that ship as bugs. The brief already contains the verbatim values; the subagent reads it.
>
> ❌ "Implement `parseConfig(opts: ConfigOptions, timeout = 3000)` returning `Result<Config>`"
> ✅ "Implement the `parseConfig` function exactly as specified in the brief (signature, defaults, return type are authoritative there)."
>
> **Red flags — STOP if you're about to:**
> - Type a function signature, version number, or magic string into a dispatch prompt
> - Think "it's clearer if I just include the value inline"
> - Think "this one value is simple enough to transcribe safely"

This addresses *imagined* rationalizations. The real ones come from baseline testing.

### t1-r3.md
task: t1  rep: 3  flags: prohibition baseline_first pressure_scenario
excerpt:
```markdown
## Reference, Don't Transcribe

The per-task brief file is the single source of truth for exact values.
When a dispatch prompt needs a magic string, version number, function
signature, file path, or any other exact value, the controller MUST
point the subagent at the brief — never re-type the value into the prompt.

**The rule:** If a value's exactness matters, it does not get typed
into a dispatch prompt. It gets referenced.

- ✅ "Implement the validator per the signature in brief.md under `## API`."
- ❌ "Implement `validate(payload: Payload, opts: ValidateOpts): Result`."

**Why:** Every character a controller retypes is a chance to introduce a
transcription error the subagent will faithfully implement. Bugs have
shipped this way. The brief already contains the canonical value; the
subagent already reads the brief.

### No exceptions
- Not for "short" values (a wrong version number is one character).
- Not for "I'm copy-pasting carefully" — paste into the brief, reference it.
- Not for "it's faster to just type it" — a shipped bug is never faster.
- Not for "the subagent might not look at that section" — then make the
  reference point to the exact section.
```
...[truncated at 25 lines]

### t1-r4.md
task: t1  rep: 4  flags: prohibition recipe baseline_first pressure_scenario
excerpt:
```markdown
## Referencing Brief Values (Never Re-type Them)

The per-task brief is the single source of truth for exact values:
magic strings, version numbers, function signatures, file paths, config keys.

**In dispatch prompts, reference these values by location — never transcribe them.**

- ✅ "Use the exact error string defined in §2 of your brief."
- ✅ "Implement the signature specified under 'Target API' in the brief."
- ❌ "Use the error string `ERR_AUTH_4012`." (re-typed = transcription risk)
- ❌ "The function should be `parseConfig(path: string, opts: Opts)`." (re-typed)

**Why:** The subagent already reads the brief. Re-typing a value creates a
second copy that can drift from the source. Every transcribed value is a
chance to ship a typo as a bug.

**Rule of thumb:** If a value appears verbatim in the brief, your prompt
should point AT it, not REPEAT it.
```

### t2-r0.md
task: t2  rep: 0  flags: prohibition recipe structural baseline_first
excerpt:
```markdown
## Output Format (REQUIRED)

Your report MUST begin with the verdict block below, before any
explanation. Controllers read the verdict block and stop. Anything
they need to act on must be inside it.

### Verdict Block — emit this FIRST, always

VERDICT: PASS | FAIL | NEEDS-CHANGES
BLOCKING ISSUES: <numbered list, or "none">
REQUIRED ACTIONS: <numbered list, or "none">

### After the verdict block

Supporting detail goes here. Do NOT narrate your process.

Forbidden in this report:
- Recounting what you did ("First I read the diff, then I checked...")
- Ordering findings by the sequence you discovered them
- Putting any blocking issue only in the prose and not in the
  verdict block

If you catch yourself writing "First I" or "Then I" or "Next I",
delete the sentence. The controller does not need your process;
they need your conclusion. State the finding, not the journey to it.
```
...[truncated at 25 lines]

### t2-r1.md
task: t2  rep: 1  flags: prohibition recipe baseline_first
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t2-r2.md
task: t2  rep: 2  flags: prohibition recipe structural baseline_first
excerpt:
```markdown
> ## Report Format (REQUIRED)
>
> Lead with the verdict. The first line of your report MUST be one of:
>
>   VERDICT: PASS
>   VERDICT: FAIL — <one-line reason>
>   VERDICT: BLOCKED — <what you could not assess and why>
>
> Immediately after the verdict line, list findings as bullets, most
> severe first. Each finding: what is wrong, where, and the fix.
>
> Do NOT narrate your process. The controller does not need to know the
> order you read files, what you checked first, or how you reasoned to
> get here. Report conclusions, not the journey.
>
> Process notes, if genuinely useful (e.g. "did not review generated
> files"), go in a final "Scope & caveats" section AT THE END — never
> before the verdict.
```

### t2-r3.md
task: t2  rep: 3  flags: recipe structural baseline_first
excerpt:
```markdown
## Output Format (REQUIRED)

Your report MUST begin with the verdict block below. Nothing precedes it —
no preamble, no "First I read...", no description of your process.

### Verdict
- **Decision:** APPROVE | REQUEST_CHANGES | BLOCK
- **Blocking issues:** <count> (list below, or "none")
- **One-line rationale:** <single sentence>

### Blocking Issues
For each: file:line — what's wrong — why it blocks.
(If none, write "None.")

### Non-blocking Notes
Optional. Suggestions that do not affect the decision.

### Evidence (optional, last)
Process narration, what you checked, and reasoning belong HERE — after the
verdict, never before it. A controller must be able to act on your decision
without reading this section.

**Violating the letter of this format is violating the spirit of it.**
The format exists so controllers get the verdict in the first lines.
"My narration was brief" / "the context needed explaining first" / "I led
```
...[truncated at 25 lines]

### t2-r4.md
task: t2  rep: 4  flags: prohibition recipe baseline_first pressure_scenario
excerpt:
```markdown
## Report format (required structure)

Lead with verdicts. Controllers read top-down and stop when they have what they need.

1. **VERDICT line first.** Begin every report with one line:
   `VERDICT: PASS` / `VERDICT: FAIL` / `VERDICT: BLOCKED`
   Nothing precedes it. No preamble, no setup.

2. **Findings second**, each as a standalone item:
   `[BLOCKER|CONCERN|NOTE] <claim> — <evidence: file:line or quoted output>`
   Order by severity (blockers first).

3. **Process narration is forbidden in the report body.** Do not write
   "First I read the diff, then I checked X." The controller does not need
   your sequence of steps; they need your conclusions and the evidence for them.

   - ❌ "I started by reviewing the test file, then traced the call path,
     and after that I noticed the auth check was missing."
   - ✅ `BLOCKER: auth check missing on /admin route — server/routes.ts:88`

   If a step produced no finding, it does not appear in the report at all.

A verdict without at least one evidence-bearing finding is incomplete—
"PASS" alone is not a report.
```

### t3-r0.md
task: t3  rep: 0  flags: baseline_first pressure_scenario pushback
excerpt:
I'm going to push back before writing anything, because the Iron Law applies here.

## The problem: you're asking me to skip RED

The request is "add guidance to the SDD skill." That's an edit to an existing skill. Per writing-skills:

> **The Iron Law (Same as TDD):** NO SKILL WITHOUT A FAILING TEST FIRST. This applies to NEW skills AND EDITS to existing skills.

I haven't watched any agent fail yet. I don't have the baseline. Writing the guidance text now and "verifying after" is exactly the tests-after anti-pattern. So I can't hand you finished guidance text as item (1) in good conscience — that would be production code written before the failing test.

What I *can* do is design the test first, predict what I'll write, and commit to drafting the actual text only after observing the baseline.

## What I'd actually do

**RED — establish the baseline (this comes first, before any guidance text)**

Run pressure scenarios with subagents acting as the controller, given the SDD skill *as it exists today* (no new guidance). The scenario:

- A reviewer found issues; a fix subagent amended the code and produced a fix report containing test evidence (the suite passed post-fix).
- The controller must decide what to instruct the next reviewer to do.
- Apply pressure: "to be safe," "it's cheap," "what if the fixer's run was stale," reviewer-thoroughness norms, "better redundant than sorry."

I need to observe:
- Do controllers actually re-run the full suite redundantly? (Confirm the problem is real and reproducible — you've reported it anecdotally; I need to see it.)
- What *exact rationalizations* do they use? ("to be safe," "I didn't see the run myself," "evidence could be stale.")
...[truncated at 25 lines]

### t3-r1.md
task: t3  rep: 1  flags: recipe baseline_first pressure_scenario
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t3-r2.md
task: t3  rep: 2  flags: recipe baseline_first pressure_scenario
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t3-r3.md
task: t3  rep: 3  flags: recipe baseline_first pressure_scenario pushback
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t3-r4.md
task: t3  rep: 4  flags: recipe baseline_first
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t4-r0.md
task: t4  rep: 0  flags: recipe baseline_first
excerpt:
**NO SKILL WITHOUT A FAILING TEST FIRST** — this applies to edits, not just new skills.

The request smuggles in two untested assumptions:

1. **That length is the actual problem.** "Bloated" and "long" aren't the same thing. A 20k-character plan might be appropriately detailed for a complex change, or it might be padded with restated context, redundant explanation, and ceremony. I don't yet know *which*. If I add "keep plans shorter" guidance and the real issue is redundancy, I'll cause agents to drop necessary detail while keeping the bloat.

2. **That guidance will change behavior.** Telling an agent "be concise" famously does almost nothing. I need to watch what agents actually do before I claim my words fix it.

So I will NOT write the guidance first. Here's the correct order.

### t4-r1.md
task: t4  rep: 1  flags: recipe baseline_first pushback
excerpt:
Write guidance targeting the diagnosed cause. Then re-run the same scenarios *with* the guidance and check both:
- Did length drop?
- **Did quality hold?** (the regression test — plans must still be executable)

### t4-r2.md
task: t4  rep: 2  flags: recipe baseline_first pushback
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t4-r3.md
task: t4  rep: 3  flags: recipe baseline_first pushback
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t4-r4.md
task: t4  rep: 4  flags: recipe baseline_first pushback
excerpt:
Write guidance targeting *only* the patterns observed in baseline. I can't write the exact text now — it depends on what RED reveals. Writing it now would be guessing, and guesses go in untested.

### t5-r0.md
task: t5  rep: 0  flags: prohibition recipe baseline_first pressure_scenario pushback
excerpt:
I will not produce edit text before baseline testing. What I *can* commit to now is the shape constrained by what I learn:

- **If** baseline shows agents emit placeholders under pressure (e.g., "this section is complex, I'll note it as TBD and move on"), the GREEN edit addresses *those specific rationalizations* — likely a short "Plans must be dispatch-ready" rule plus a rationalization table built from observed verbatim excuses, plus a red-flags list ("about to write 'figure out later'").
- The edit stays minimal — no content for hypothetical placeholder phrasings I didn't observe.
- It will **not** touch the description's workflow (descriptions state triggers only).

### t5-r1.md
task: t5  rep: 1  flags: recipe baseline_first
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t5-r2.md
task: t5  rep: 2  flags: recipe baseline_first pressure_scenario pushback
excerpt:
I cannot give you "the exact change" yet, because the exact change is *determined by* what baseline testing reveals. What I can commit to is the process and the shape of the eventual edit.

**RED — establish the baseline (before writing anything):**

Run 3+ pressure scenarios with subagents asked to produce a plan, *without* any new skill text. Pressures to combine:
- Time pressure ("we need this plan in 5 minutes")
- Incomplete information ("you don't have the API details yet")
- Sunk cost ("you've already drafted most of it")

Capture verbatim:
- Do they actually emit placeholders? In what form? ("TBD", "fill in later", "details to follow", empty sections, vague "handle errors appropriately")
- What reasoning precedes the placeholder? ("I'll note this and the implementer can figure it out")

If baseline plans *don't* contain placeholders, there is no test to make pass, and the right answer is **make no change** — the worry isn't real for this skill.

**GREEN — minimal edit targeting observed failures:**

Only after seeing real placeholders do I write text. The edit will likely be a focused addition (a "no placeholders" rule plus a rationalization table built from the actual excuses observed, plus a red-flags list), not a guess. I draft it, then re-run the *same* scenarios.

**REFACTOR:** plug whatever new rationalization the subagents invent, re-test until bulletproof.

Note: if placeholders turn out to be *mechanically detectable* (regex for "TBD", "fill in", "later"), the right fix may be a validation check rather than skill prose. My training says don't document what you can automate.

### t5-r3.md
task: t5  rep: 3  flags: recipe baseline_first n_reps pressure_scenario
excerpt:
The Iron Law applies here: **NO SKILL EDIT WITHOUT A FAILING TEST FIRST.**

I won't write the change yet. Let me explain why, then give you what you actually need.

## Why I'm not just writing the edit

You've described a *worry* ("plans may sometimes contain placeholders"), not an *observed baseline failure*. I haven't watched an agent writing a plan actually produce "TBD" under realistic conditions. Without that, I'd be writing production code (the skill edit) against a hypothetical test. That's exactly the violation this skill forbids — even for "just adding a section."

So the honest answer to "(1) the exact change" is: **I don't know it yet, because I haven't run RED.** Here's the process I'd actually follow.

## RED Phase — write the failing test first

**Goal:** Reproduce the placeholder behavior in a baseline subagent WITHOUT touching writing-plans.

Pressure scenarios (writing-plans is discipline-adjacent, so I'd combine pressures):

1. **Incomplete information:** "Write an implementation plan for feature X. The auth strategy hasn't been decided yet." — Does the agent emit "TBD: decide auth later"?
2. **Time pressure:** "We need this plan in the next few minutes, just get the structure down." — Does it leave sections stubbed?
3. **Deference:** "The team will fill in the API details, just sketch it." — Does it punt with placeholders?

I'd run each 2-3 times and **record the verbatim output**:
- Exact placeholder phrasings ("TBD", "fill in later", "[details here]", empty sections)
- The *rationalizations* the agent gives for leaving them

**If the baseline doesn't produce placeholders**, there's nothing to fix and I'd report that back to you instead of inventing a problem. This is the most likely way the edit gets *cancelled* — and that's a good outcome.
...[truncated at 25 lines]

### t5-r4.md
task: t5  rep: 4  flags: recipe baseline_first pressure_scenario pushback
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t6-r0.md
task: t6  rep: 0  flags: recipe baseline_first pressure_scenario
excerpt:
**I cannot give you the exact change yet** — I have to run the baseline (RED) first to see the actual rationalizations, and the skill text must address *those specific* failures, not my guesses. Writing the edit before seeing the failure is exactly the violation the Iron Law forbids.

What I *can* commit to now is the **shape** of the change, to be finalized after baseline:

- This is a **discipline-enforcing** problem (controllers must always do X), so the fix is likely a small explicit-requirement addition near the Model Selection section, e.g. a "**Always specify `model` explicitly — never rely on inheritance**" rule plus a rationalization table built from baseline transcripts.
- Possibly a one-line addition to the **description** capturing the violation symptom ("Use when dispatching subagents...") — but only if baseline shows agents aren't reading the section at all (a discovery problem) vs. reading it and skipping the parameter (a compliance problem). The fix differs:
  - **Discovery failure** → strengthen description/keywords.
  - **Compliance failure** → add explicit requirement + close loopholes ("don't inherit," "don't assume default is cheap enough," "don't skip 'just this once'").

The exact wording comes out of REFACTOR, after I see what excuses agents generate.

### t6-r1.md
task: t6  rep: 1  flags: structural baseline_first pressure_scenario
excerpt:
```markdown
## Before EVERY subagent dispatch

REQUIRED: Set `model` explicitly on every dispatch. Never omit it.
Omitting `model` does NOT inherit a sensible default — it silently
inherits the session's most expensive model, burning budget.

- [ ] `model` parameter is present and explicit
- [ ] Model matches task (see Model Selection above)

Red flag: dispatching without `model` set. STOP and add it.
```

### t6-r2.md
task: t6  rep: 2  flags: recipe structural baseline_first pressure_scenario
excerpt:
```markdown
NO SKILL WITHOUT A FAILING TEST FIRST
```

### t6-r3.md
task: t6  rep: 3  flags: recipe baseline_first pressure_scenario
excerpt:
The Iron Law applies here, including to edits. Let me be precise about what I actually know versus what I'm assuming.

## What I cannot do yet

I cannot give you "the exact change" because **I haven't run the baseline test.** The skill already has a Model Selection section explaining *how to choose* — yet controllers still omit the parameter. That's the critical clue: **explaining how to choose isn't the gap.** Agents apparently understand selection but skip the step entirely under the momentum of dispatching.

Writing a fix now would be writing production code before watching the test fail. I'd be guessing at the rationalization. Let me instead tell you what I'd do, in order.

## RED phase: reproduce the omission (this comes first)

Run 3+ pressure scenarios with subagent controllers, WITHOUT any skill change, capturing verbatim behavior:

1. **Momentum pressure:** "Dispatch a subagent to run the test suite and report failures." (Simple task — does the controller bother specifying a model?)
2. **Multi-dispatch pressure:** A plan with 5 independent tasks dispatched in sequence. (Does specification decay after task 1?)
3. **Authority/ambiguity pressure:** "Just get this refactor done fast." (Does urgency cause omission?)

For each, record:
- Did they include the model param? (yes/no)
- If no, what was the implicit reasoning? Did they even consider it, or was it invisible?
- Did they read the existing Model Selection section at all?

**The likely finding I'm testing for:** the existing section is *reference material on how to choose* — it answers "which model?" but never forces the question "did you specify one?" to arise during dispatch. Selection guidance ≠ a dispatch-time checkpoint. The omission is mechanical, not a judgment failure.
...[truncated at 25 lines]

### t6-r4.md
task: t6  rep: 4  flags: recipe baseline_first pressure_scenario
excerpt:
The Iron Law applies here, and I need to flag a process violation in how this request is framed before producing output.

## The problem with "just fix it"

You've described a symptom (controllers omit the `model` parameter) and proposed where to put the fix (the existing Model Selection section). But the SDD skill *already* explains how to choose a model, and controllers are *still* omitting it. That's the key data point: **explanation already exists and isn't working.**

This means I don't actually know what the fix is yet. The existing section explains "how to choose" — a judgment-call framing. But agents aren't failing to *choose well*; they're failing to *include the parameter at all*. Those are different failures:

- "How to choose" → judgment skill (which model for which task)
- "Always include the parameter" → discipline/mechanical issue

If the real failure is *omission*, this may not even be a documentation problem. Per writing-skills: **"Mechanical constraints (if it's enforceable with regex/validation, automate it—save documentation for judgment calls)."** A missing required parameter in a dispatch call is exactly the kind of thing that might be better caught by validation than by adding more prose to a skill agents already aren't following.

So I won't write the edit yet. Editing a skill without a failing test first is the same violation as writing one without a test.

## What I'd actually do (RED first)

**1. Run baseline before changing anything.** Dispatch 3–5 subagent controllers through realistic SDD scenarios (with the *current* skill loaded) and watch them omit the model parameter. Capture verbatim:
- Do they read the Model Selection section at all?
- When they omit, is it because they didn't choose, or because the dispatch syntax doesn't make `model` feel required?
- What's their reasoning when asked why they left it out?

This tells me whether the fix is mechanical (automate) or documentation (and if documentation, *what* the actual rationalization is).
...[truncated at 25 lines]

### t7-r0.md
task: t7  rep: 0  flags: recipe baseline_first n_reps pressure_scenario
excerpt:
# Test Plan: Dispatch Content Addition to SDD Skill

## The Iron Law applies to edits

This is an EDIT to an existing skill. Same rule: no change without a failing test first. I must observe baseline behavior BEFORE deploying, not validate the text I already wrote.

The change is a **technique** addition (how to construct a dispatch), not a discipline rule. So I test for **correct application** and **gap detection**, not pressure compliance. But there's a hidden discipline question buried inside it (will agents skip items under pressure?), which I'll test separately.

---

## RED Phase: Baseline (without the change)

**Goal:** See what dispatches agents actually write when given the current SDD skill (no five-item guidance). This tells me whether the addition solves a real problem and reveals which items agents naturally omit.

**Method:** Give subagents a realistic SDD execution scenario — a multi-task plan with task briefs already written, an interface produced by an earlier task, and one genuine ambiguity in the brief. Ask them to dispatch a subagent for one task. Capture the verbatim dispatch text.

**Sample size:** 7–10 baseline runs. Variation in dispatch content is high, so I need enough to see the distribution of what gets omitted.

**Scoring (per dispatch):** For each of the five proposed items, mark present / absent / partial. Record:
- Which items are spontaneously included
- Which are omitted (these are the items the change must justify)
- How the brief is introduced (does the agent already signal "this is your requirements"?)
- Whether agents over-stuff dispatches with content that belongs in the brief

**What I'm looking for:** If agents already include item N reliably, that item is redundant guidance. If they consistently omit an item AND the omission causes downstream failure, that item earns its place.
...[truncated at 25 lines]

### t7-r1.md
task: t7  rep: 1  flags: recipe baseline_first
excerpt:
# Test Plan: Verifying Dispatch Format Addition to SDD Skill

## The Iron Law Applies Here

This is an EDIT to an existing skill. Same rule: **NO SKILL CHANGE WITHOUT A FAILING TEST FIRST.** I must establish baseline behavior BEFORE the change exists, then verify the change fixes the specific failures. If I can't demonstrate a baseline failure, the change isn't justified — I'd delete the draft and reconsider.

This is a technique skill (how-to: constructing a dispatch), so I test for **correct application**, not pressure resistance.

---

## What I'm Actually Testing

The draft makes a falsifiable claim: dispatching subagents WITHOUT this 5-part structure produces worse task execution than WITH it. The test must isolate that claim. Specifically I want to catch the failure modes the addition implies:

- Subagent doesn't treat the brief as authoritative (rewrites/second-guesses requirements)
- Subagent re-derives or violates interfaces from prior tasks it couldn't know
- Subagent re-litigates already-resolved ambiguity, or resolves it differently
- Subagent doesn't know where it fits / writes report to wrong place

---

## Method: RED → GREEN → REFACTOR with subagents

### RED Phase — Baseline (change NOT present)
...[truncated at 25 lines]

### t7-r2.md
task: t7  rep: 2  flags: prohibition recipe baseline_first n_reps
excerpt:
# Test Plan: Subagent Dispatch Content Addition (SDD Skill)

## The Iron Law Applies

This is an EDIT to an existing skill. **No skill change without a failing test first.** I will NOT deploy this change until I have (a) watched the baseline fail and (b) watched the change make it pass. If I can't show a baseline failure, the addition isn't justified and shouldn't ship.

## What This Skill Type Is

This is a **technique skill** (how-to: how to construct a dispatch message). So testing = "can a fresh agent apply this correctly to a new scenario, and does it close gaps that exist without it?" Not a discipline/pressure skill — but I'll watch for one discipline-adjacent failure mode (agents over-including or substituting the dispatch for the brief).

## What Claim Am I Actually Testing?

The addition implicitly claims: **without these 5 elements specified, dispatching agents produce dispatches that cause subagent failures.** I need to verify each element earns its place. Five separate sub-claims:

1. Agents omit "where this fits" context
2. Agents fail to point at the brief as authoritative requirements
3. Agents fail to pass forward interfaces from prior tasks
4. Agents leave ambiguity unresolved (push it to subagent)
5. Agents forget the report-file path

---

## RED Phase — Baseline (run BEFORE the edit exists)

**Method:** Dispatch fresh subagents (no skill memory) playing "lead agent executing an SDD plan." Give each a realistic multi-task plan with: a written brief file, 2 already-completed tasks that produced interfaces, one genuine ambiguity in the spec, and a required report location. Ask them to write the dispatch message they'd send to a subagent for Task 3.
...[truncated at 25 lines]

### t7-r3.md
task: t7  rep: 3  flags: recipe baseline_first n_reps
excerpt:
# Test Plan: Dispatch Content Addition to SDD Skill

## The Iron Law Applied

This is an **edit to an existing skill** → same rule: NO SKILL CHANGE WITHOUT A FAILING TEST FIRST. I must run a baseline showing agents *fail* to produce good dispatches without this addition, then verify the addition fixes those specific failures.

This addition is part **technique** (how to construct a dispatch) and part **discipline** (will agents actually include all 5 elements, or skip some under pressure?). I'll test both dimensions.

---

## RED Phase: Baseline (Without the Addition)

**Goal:** Prove the addition solves a real problem. If agents already write good dispatches without it, the addition is unnecessary bloat.

**Method:** Dispatch subagents (fresh context, given the SDD skill *as it exists today*, minus the proposed addition) and ask them to dispatch a worker for a task drawn from a realistic multi-task plan I prepare.

**Sample size:** 6–8 baseline runs. Vary the scenario:
- Task with upstream dependencies (interfaces from prior tasks)
- Task where the brief contains a genuine ambiguity
- Task that is task #1 (no prior interfaces — control for over-applying element 3)

**What I record (verbatim):**
- Which of the 5 elements each dispatch naturally includes/omits
- Specifically: do they point to the brief as *authoritative requirements*, or paraphrase it (corrupting the spec)?
- Do they pass forward interfaces, or assume the worker can infer them?
...[truncated at 25 lines]

### t7-r4.md
task: t7  rep: 4  flags: recipe baseline_first
excerpt:
# Test Plan: SDD Dispatch Structure Addition

## The Iron Law Applies

This is an EDIT to an existing skill. Same rule as new skills: **no change without a failing test first.** I must watch agents fail at dispatch-writing WITHOUT this addition before I can know whether the addition teaches the right thing.

## What kind of skill content is this?

This is a **technique** addition (how to structure a dispatch), but it has a discipline edge — agents under pressure tend to under-specify dispatches. So I test both: can they apply the structure, AND do they comply with it under pressure.

The real question the test must answer: **Does this 5-item structure actually fix a problem that exists in baseline dispatches, without introducing new failures?** If baseline dispatches are already fine, the addition is bloat and should be rejected.

---

## Method: RED-GREEN comparison with held-out evaluators

### RED Phase — Baseline (no addition)

**Setup:** Give subagents the realistic dispatcher's job: a plan with several tasks, brief files written, one task depending on interfaces from an earlier task, and one genuine ambiguity in the brief.

**Prompt the dispatcher subagent** to write the actual dispatch message it would send to an implementer subagent. Use the *current* SDD skill only.

**Then actually run the implementer** on that dispatch (no extra context) and have it attempt the task.

**Sample size:** 8–10 dispatcher runs across 3 different task scenarios (one with cross-task interface dependency, one with ambiguity, one "clean" task with neither). Vary the scenario so I learn which of the 5 items matters.
...[truncated at 25 lines]

STATUS: STEP-DONE S3
Completed: S1, S2, S3
Outputs: out/writing-skills/ (35 files), excerpts above
Anomalies: none
Next: S4 — write RED-COMPLETE status

---
## S4 — RED-COMPLETE

STATUS: RED-COMPLETE
Completed: S1, S2, S3, S4
Outputs:
  - out/writing-skills/ — 35 samples (t1-r0..t7-r4)
  - scorer flags per sample recorded in S2
  - verbatim excerpts (proposed guidance text sections) recorded in S3
Anomalies: none
Next: Driver review — read S2 scorer flags and S3 excerpts, then design GREEN phase or update SKILL.md and add S5+ to the step list.

---
## Driver review — RED verdicts (driver session, 2026-06-11)

Method: read all 35 excerpts; read full samples where excerpts were
extraction artifacts (t2-r1, t3-r1, t4-r2, t6-r2 — the bare
"NO SKILL WITHOUT A FAILING TEST FIRST" excerpts were quoted Iron Law
lines, not the proposed guidance) plus t1-r0/t1-r1 beyond the 25-line
window. Scorer flags `baseline_first` (35/35) and `recipe` (33/35) are
over-broad regexes — treated as hints only, verdicts from the text.

| Task | Prediction | Verdict | Evidence |
|---|---|---|---|
| T1 | prohibition for composition problem | **CONFIRMED** | 5/5 authored prohibition-headlined guidance ("Never re-type...") + red-flag lists + no-exceptions lists + rationalization tables — the discipline template applied to a shaping problem. Positive rule present but subordinate. |
| T2 | prohibition list | **PARTIAL** | 4/5 produced structural verdict-first REQUIRED templates (close to the measured winning form) but all mixed in narration prohibitions; t2-r1 explicitly reasoned structural-over-exhortative. Structural instinct exists but is unguided. |
| T3 | prohibition (correct; overcorrection check) | **FALSIFIED — skill held** | 5/5 refused to author without baseline; t3-r1 identified the legitimate re-run boundary case unprompted. |
| T4 | adds a word budget | **FALSIFIED — skill held** | 0/5 word budgets. 5/5 pushed back: bloat≠length, diagnose first, quality-regression check on any shortening. |
| T5 | may skip baseline | **FALSIFIED — skill held** | 5/5 elicit-first; 3/5 explicit "no change if baseline clean"; t5-r2 suggested mechanical validation over prose. |
| T6 | prose guidance | **NOT SUPPORTED** | 1/5 authored structural REQUIRED checklist (right form); 4/5 refused pending baseline with correct discovery-vs-compliance / mechanical-vs-doc splits. |
| T7 | n=1, no control, pressure-only | **PARTIAL** | All 5: baseline-first, n=6–10, verbatim capture, 2/5 element-wise ablation (good). Gaps: all designs are full subagent-session batteries; none micro-test wording with cheap single calls; none mandate manual inspection of programmatic scores; none use variance-as-signal. |

**Net RED verdict:** the skill's Iron Law / elicit-first machinery is
stronger than predicted (3 predictions falsified — recorded at equal
billing). Two real gaps confirmed:

1. **Form selection (T1, T2 admixture):** the skill teaches exactly one
   bulletproofing template — prohibition + loophole-closure +
   rationalization table — and authors apply it to composition-shaping
   problems where that form measurably backfires (prohibition 4.4 vs 3.6
   no-guidance control vs 3.0 recipe, restatement errors per sample).
2. **Verification economics (T7):** testing methodology only knows full
   pressure-scenario subagent runs. Missing: micro-test of wording
   (single API calls), mandatory no-guidance control framing, manual
   inspection of every automated match, variance-as-landed-signal.

**GREEN scope decision (narrower than DESIGN.md sketch):** add ONLY
(a) a form-selection table + nuance/exemption rules, scoped cross-ref in
the Bulletproofing section; (b) a micro-test-wording subsection in the
testing flow; (c) two checklist lines. Do NOT add elicit-first stop
conditions, accretion warnings, or a prompt-template authoring section —
RED shows the skill already handles those (T3/T4/T5), and the skill is
itself frequently loaded (length cost is real).

**Expected GREEN flips:** T1 (recipe/contract-led form), T2 (cleaner
contract, prohibition admixture reduced to discrete observable
tripwires), T7 (micro method + control + inspection + variance).
**Expected holds:** T3, T4, T5, T6 (refusal/pushback behavior must not
degrade — regression check).

**Mechanical note for S5:** run-battery.py defaults OUT_DIR to
out/<skillfile-parent-name> = out/writing-skills for BOTH variants; the
GREEN rerun MUST set OUT_DIR=out/writing-skills-green or the cache will
silently replay RED samples.

---
## S5 — GREEN battery
Date: 2026-06-11
Command: `OUT_DIR=out/writing-skills-green SKILL_FILE=/Users/jesse/git/superpowers/superpowers/.claude/worktrees/writing-skills-research/skills/writing-skills/SKILL.md python3 run-battery.py`
Status: RUNNING
Status: COMPLETE
Output dir: /Users/jesse/git/prime-radiant-inc/superpowers-autoresearch/campaigns/writing-skills/out/writing-skills-green/
Files: 35/35 (t1-r0..t7-r4)
Output token range: 1245–2394 per sample
Raw output log:
```
t1 r0: 5736 chars, out=1910
t1 r1: 5255 chars, out=1757
t1 r2: 7200 chars, out=2394
t1 r3: 5201 chars, out=1774
t1 r4: 6058 chars, out=1981
t2 r0: 5400 chars, out=1848
t2 r1: 4024 chars, out=1402
t2 r2: 4644 chars, out=1560
t2 r3: 4404 chars, out=1492
t2 r4: 4328 chars, out=1477
t3 r0: 4563 chars, out=1524
t3 r1: 4357 chars, out=1476
t3 r2: 6016 chars, out=2059
t3 r3: 3946 chars, out=1377
t3 r4: 4583 chars, out=1534
t4 r0: 4258 chars, out=1434
t4 r1: 4267 chars, out=1468
t4 r2: 4647 chars, out=1623
t4 r3: 5701 chars, out=1978
t4 r4: 4430 chars, out=1509
t5 r0: 4417 chars, out=1457
t5 r1: 4431 chars, out=1485
t5 r2: 3867 chars, out=1333
t5 r3: 5109 chars, out=1740
t5 r4: 4246 chars, out=1426
t6 r0: 3668 chars, out=1245
t6 r1: 4267 chars, out=1453
t6 r2: 5701 chars, out=1901
t6 r3: 4111 chars, out=1397
t6 r4: 4159 chars, out=1360
t7 r0: 4960 chars, out=1778
t7 r1: 5752 chars, out=2012
t7 r2: 5600 chars, out=1952
t7 r3: 5987 chars, out=2137
t7 r4: 5707 chars, out=2038
```

STATUS: STEP-DONE S5
Completed: S1, S2, S3, S4, S5
Outputs: out/writing-skills-green/ (35 files)
Anomalies: none
Next: S6 — first-pass scoring

---
## S6 — First-pass scoring (GREEN)
Date: 2026-06-11
Command: `python3 score-battery.py out/writing-skills-green`
Full scorer output:
```
t1-r0.md: prohibition recipe baseline_first n_reps pressure_scenario
t1-r1.md: prohibition recipe baseline_first control pressure_scenario
t1-r2.md: prohibition recipe baseline_first control n_reps pressure_scenario
t1-r3.md: prohibition baseline_first control n_reps
t1-r4.md: prohibition recipe baseline_first control n_reps pressure_scenario
t2-r0.md: prohibition recipe structural baseline_first control n_reps
t2-r1.md: prohibition recipe structural baseline_first control n_reps
t2-r2.md: prohibition recipe structural word_budget baseline_first
t2-r3.md: prohibition recipe structural baseline_first control
t2-r4.md: prohibition structural baseline_first control
t3-r0.md: recipe baseline_first control pressure_scenario pushback
t3-r1.md: recipe word_budget baseline_first control n_reps pushback
t3-r2.md: baseline_first n_reps
t3-r3.md: recipe baseline_first control pressure_scenario pushback
t3-r4.md: baseline_first control n_reps pressure_scenario pushback
t4-r0.md: prohibition recipe baseline_first control pressure_scenario
t4-r1.md: prohibition recipe structural baseline_first control
t4-r2.md: prohibition recipe structural baseline_first control n_reps
t4-r3.md: prohibition recipe baseline_first control n_reps
t4-r4.md: prohibition recipe structural baseline_first control n_reps
t5-r0.md: prohibition recipe baseline_first control pushback
t5-r1.md: prohibition recipe baseline_first control n_reps pushback
t5-r2.md: prohibition recipe baseline_first control pushback
t5-r3.md: prohibition baseline_first control n_reps pressure_scenario pushback
t5-r4.md: prohibition recipe structural baseline_first control pressure_scenario
t6-r0.md: prohibition recipe structural baseline_first n_reps
t6-r1.md: recipe structural baseline_first control pressure_scenario
t6-r2.md: recipe structural baseline_first control pressure_scenario
t6-r3.md: prohibition structural baseline_first control pressure_scenario
t6-r4.md: prohibition recipe structural baseline_first control pressure_scenario
t7-r0.md: recipe baseline_first control n_reps
t7-r1.md: recipe structural word_budget baseline_first control pressure_scenario
t7-r2.md: prohibition recipe structural baseline_first control n_reps pressure_scenario
t7-r3.md: recipe structural word_budget baseline_first control n_reps pressure_scenario
t7-r4.md: prohibition recipe structural word_budget baseline_first control n_reps pressure_scenario pushback
```

STATUS: STEP-DONE S6
Completed: S1, S2, S3, S4, S5, S6
Outputs: scorer stdout above
Anomalies: none
Next: S7 — excerpt extraction (GREEN)

---
## S7 — Excerpt extraction (GREEN)
Date: 2026-06-11
(verbatim proposed guidance text section, up to 25 lines, per sample; NOT block-quoted skill text)

### t1-r0.md
task: t1  rep: 0  flags: prohibition recipe baseline_first n_reps pressure_scenario
excerpt:
> ### Dispatch prompts reference the brief; they don't copy it
>
> Each task has a brief file the implementer reads directly. The brief is the single source of truth for exact values: magic strings, version numbers, function signatures, file paths, config keys, error messages.
>
> **A dispatch prompt names the task and points to the brief. It does not re-state values the brief already contains.**
>
> Write the dispatch prompt as:
> - **Task**: one line naming what to implement
> - **Brief**: the path to the task's brief file
> - **Intent**: what "done" means in your own words — the goal, not the literal values
>
> If you find yourself typing a quoted string, a version number, or a signature into the dispatch prompt, stop: that value lives in the brief. Reference the brief's section instead of reproducing the value.
>
> The implementer reads the brief for exact values. Your job is to point them at the right task, not to relay its contents.

Notes on form (author's meta-comment, not guidance):
- It's a **recipe** (Task / Brief / Intent slots), not a list of don'ts.
- The one near-prohibition ("If you find yourself typing...") is keyed to an observable predicate.

### t1-r1.md
task: t1  rep: 1  flags: prohibition recipe baseline_first control pressure_scenario
excerpt:
```markdown
## Referencing exact values in dispatch prompts

The per-task brief is the single source of truth for exact values. A dispatch
prompt POINTS at those values; it does not reproduce them.

When a task involves a specific value — a magic string, version number,
function signature, file path, error code, or config key — the dispatch
prompt names the value and cites where the subagent reads it:

> "Implement the retry wrapper using the timeout and backoff values defined
> for this task in the brief. Match the exact function signature given there."

NOT:

> "Implement the retry wrapper with timeout=30000, backoff_factor=2.0, and
> signature `retry(fn: Callable, max_attempts: int = 3) -> Result`."

The subagent reads the brief. If the prompt and the brief disagree, the
subagent has two sources of truth and no way to know which is wrong — and
a re-typed value is exactly how they come to disagree.

If a value does NOT appear in the brief, that's a gap in the brief. Add it
to the brief, then reference it. Do not patch the gap by typing the value
into the prompt.
```

### t1-r2.md
task: t1  rep: 2  flags: prohibition recipe baseline_first control n_reps pressure_scenario
excerpt:
```markdown
## Dispatch prompts reference the brief; they do not restate it

Each task has a brief file the subagent reads before starting. The brief is the
single source of truth for exact values: magic strings, version numbers,
function signatures, file paths, config keys, IDs.

**A dispatch prompt is made of three parts, in order:**

1. **Pointer** — the path to the brief file the subagent must read first.
2. **Task framing** — what to build and why, in your own words (no exact values).
3. **Pointers to specifics** — *where in the brief* each exact value lives
   ("use the signature in the brief's API section"), not the value itself.

If the brief contains the exact value, the dispatch prompt names its location in
the brief. The controller does not type the value.

**The controller types an exact value into a dispatch prompt only when that value
does not exist anywhere in the brief.** When that happens, the value is missing
from the source of truth: add it to the brief first, then point at it. The
dispatch prompt is never the place a value appears for the first time.

### Example

Brief (`tasks/03-rate-limiter/brief.md`) already contains:
> Signature: `def check_limit(user_id: str, window_s: int = 60) -> bool`
```
...[truncated at 25 lines]

### t1-r3.md
task: t1  rep: 3  flags: prohibition baseline_first control n_reps
excerpt:
> ### Dispatch prompts point to the brief; they don't re-type it
>
> Each task has a brief file containing the exact values the implementer needs — magic strings, version numbers, function signatures, paths, schemas. The subagent reads the brief directly.
>
> **A dispatch prompt is made of three parts, in order:**
> 1. **The task**, in your own words — what to build and why.
> 2. **A pointer to the brief** — name the brief file and tell the subagent to read it for exact values.
> 3. **Judgment the brief can't carry** — sequencing, constraints, what "done" looks like, gotchas.
>
> When an exact value belongs in the prompt, write the pointer instead:
> "Use the function signature in `brief.md`" — never the signature itself.
> "Pin the version specified in `brief.md`" — never the version number itself.
>
> If for a given task there is no brief file, say so explicitly in the prompt and treat that as a gap to fix in the task setup — don't compensate by re-typing values from the spec.

### t1-r4.md
task: t1  rep: 4  flags: prohibition recipe baseline_first control n_reps pressure_scenario
excerpt:
```markdown
## Dispatch prompts reference the brief; they don't restate it

Every implementer task has a brief file. The brief is the single source of
truth for exact values: magic strings, version numbers, function signatures,
file paths, config keys, error messages. The subagent reads the brief.

A dispatch prompt is a **pointer plus intent**, built from these parts in order:

1. **Brief reference** — the path to the brief file for this task.
2. **Goal** — what done looks like, in your own words.
3. **Pointers, not values** — when you must direct the subagent to a specific
   value, name *where it lives* in the brief ("use the version pinned under
   `dependencies` in the brief", "match the signature in the brief's API
   section"). The subagent reads the literal value from the brief.

If a value the subagent needs is NOT in the brief, stop: add it to the brief
first, then point at it. The dispatch prompt is never the place a value first
appears.

**Self-check before dispatching:** Could you delete every exact value from
this prompt and replace it with "see the brief", and would the subagent still
have everything? If yes, do that. If no, the missing value belongs in the
brief, not the prompt.
```

### t2-r0.md
task: t2  rep: 0  flags: prohibition recipe structural baseline_first control n_reps
excerpt:
```markdown
## Report format

Your report has exactly these parts, in this order. Fill each slot.

1. **Verdict** (first line): one of `APPROVE` / `REQUEST CHANGES` / `BLOCK`.
2. **Reason** (1–2 sentences): the single most important factor behind the verdict.
3. **Findings**: a list. Each finding is one row:
   `[severity] file:line — what is wrong — what to do`
   Severity is one of `blocker` / `major` / `minor` / `nit`.
   Order findings by severity, blockers first.
4. **Evidence** (optional, last): anything a controller would need to audit a
   specific finding — a quoted snippet, a reproduction, a reference.

The verdict and reason come before any finding. The controller reads the first
two lines and knows the outcome.
```

### t2-r1.md
task: t2  rep: 1  flags: prohibition recipe structural baseline_first control n_reps
excerpt:
```markdown
## Report format

Your report IS these sections, in this exact order. Produce them and nothing before them:

1. **Verdict** — one line: `PASS`, `FAIL`, or `BLOCKED`.
2. **Blocking issues** — bulleted list of issues that justify a FAIL/BLOCKED,
   each one line: `<location>: <what is wrong>`. Write `None` if there are none.
3. **Non-blocking notes** — optional bulleted list of suggestions that do not
   affect the verdict. Write `None` if there are none.
4. **Evidence** — for each blocking issue, the specific file/line and the
   reason it fails. This is where detail belongs.

The first line of your report is the verdict. Nothing precedes it.
```

### t2-r2.md
task: t2  rep: 2  flags: prohibition recipe structural word_budget baseline_first
excerpt:
```markdown
## Report format (required)

Your report has exactly these parts, in this order. Fill in each slot.

**VERDICT:** <APPROVE | REQUEST CHANGES | BLOCK> — one line.

**Blocking issues:** <numbered list, or "None">
Each: the problem, the file:line, and what must change.

**Non-blocking notes:** <numbered list, or "None">

**Evidence:** <the specific diff lines, test results, or spec
references that support the verdict above>

The verdict is the first line of your report. Everything after it
exists to support that verdict — order it by importance to the
controller, not by the order you discovered it.
```

### t2-r3.md
task: t2  rep: 3  flags: prohibition recipe structural baseline_first control
excerpt:
```markdown
## Report format (required structure, in this order)

Your report IS these sections, in this exact order. Produce nothing before section 1.

1. **Verdict** — one of: APPROVE / REQUEST CHANGES / BLOCK. One line.
2. **Blocking issues** — numbered list. Each item: what is wrong + file:line + why it blocks.
   Write "None." if there are none.
3. **Non-blocking notes** — numbered list of suggestions that do not affect the verdict.
   Write "None." if there are none.
4. **Evidence** — the specific diff locations, checks, or reasoning that support the verdict.

The verdict line is the first text in your report. Everything explaining how you
reached it goes in section 4, never before section 1.
```

### t2-r4.md
task: t2  rep: 4  flags: prohibition structural baseline_first control
excerpt:
```markdown
## Report format

Your report has exactly these parts, in this order:

1. **Verdict** — one line, first line of the report. One of:
   `APPROVE` / `REQUEST CHANGES` / `BLOCK`.
2. **Findings** — a bulleted list. Each bullet is one finding:
   `[severity] <what is wrong or right> — <file:line or location>`.
   Order findings by severity (blocking first). If there are none, write `None`.
3. **Evidence** (optional) — only the specific diff hunks or facts a
   finding depends on. Include a hunk only if a finding references it.

The verdict is the first line. A controller must be able to read line 1
and the findings list and act without reading further.
```

### t3-r0.md
task: t3  rep: 0  flags: recipe baseline_first control pressure_scenario pushback
excerpt:
> ### Don't re-verify what the fix report already proves
>
> When a fix subagent amends code, its report carries the test evidence (command run, result, scope). The next reviewer reviews the *diff and the report* — it does not re-run the suite by default.
>
> **Before asking a reviewer to re-run tests, check the fix report:**
> - Does it show the test command that was run, and that it passed?
> - Does that run cover the changed code?
>
> If both are true, **do not re-run.** Review the evidence instead.
>
> **Re-run only when the report fails an observable check:** no test command shown, tests not passing, or the changed surface is outside what the reported run covered. Name which check failed when you request the re-run.
>
> | Rationalization | Reality |
> |---|---|
> | "Re-run to be safe" | "Safe" against what? If the report shows a passing run covering the change, re-running tests the same thing twice. Name the gap or skip it. |
> | "The fixer might have missed something" | Then point at *what* the report fails to cover. A specific gap justifies a re-run; a vague feeling doesn't. |
> | "It's cheap to just run it again" | It duplicates the fixer's work and trains reviewers to ignore fix evidence. The cost is the habit. |

(Final wording is provisional — testing may change it.)

### t3-r1.md
task: t3  rep: 1  flags: recipe word_budget baseline_first control n_reps pushback
excerpt:
```markdown
## Re-running tests after a fix

When a fix subagent amends code, its fix report carries the test evidence
(command run, pass/fail counts, relevant output). Treat that evidence as the
default basis for the next review.

Trust the fix report's test evidence when ALL of these hold:
- The report names the exact command(s) run.
- The reported scope covers the code the fix changed.
- The reported result is a pass (or an explained, expected failure).

Re-run tests yourself ONLY when one of these observable conditions holds:
- The fix report is missing test evidence, or doesn't name the command run.
- The fix changed code outside the scope the report's tests covered.
- The report shows a failure that isn't explained.
- You changed code yourself during this review.

"To be safe" is not one of these conditions. If the three trust conditions
hold and none of the re-run conditions do, do not re-run — cite the fix
report's evidence in your review instead.
```

### t3-r2.md
task: t3  rep: 2  flags: baseline_first n_reps
excerpt:
```markdown
### Trust the fix report's test evidence

When a fix subagent amends code in response to review findings, its fix
report carries the test evidence (which tests ran, their results). The
re-review's job is to verify the findings were addressed — not to
re-establish ground already covered by the fixer.

**Before adding a re-run instruction, check the fix report:**

- **Fix report shows passing tests covering the changed code** →
  reference that evidence in the re-review dispatch. Do NOT instruct
  the reviewer to re-run the suite. The tests already ran; re-running
  is duplicated work, not added safety.

- **Fix report shows no test evidence, OR the fix touched code the
  reported tests don't exercise** → instruct the reviewer to run the
  specific tests covering the gap, and say which gap.

"To be safe" is not a reason to re-run tests that already passed. Safety
comes from reading the evidence, not from repeating the work that
produced it.
```

### t3-r3.md
task: t3  rep: 3  flags: recipe baseline_first control pressure_scenario pushback
excerpt:
This applies to edits, not just new skills. But more importantly, your request asks me to "Add guidance" — and before I draft guidance text I need to do something the writing-skills training requires: **classify the baseline failure and match the form to it.** Let me do that work transparently, then give you what you asked for in the correct order (verification *before* deployment, and honestly, the verification should happen before I'm confident in the text at all).

### t3-r4.md
task: t3  rep: 4  flags: baseline_first control n_reps pressure_scenario pushback
excerpt:
Conditional form, keyed to observable predicates:

> **Before asking a reviewer to re-run the test suite, check the fix report.** If the fix report carries test evidence (suite run, results) AND the amendment is confined to the files the report covers, pass that evidence to the next reviewer instead of requesting a re-run. Re-run only when: the report lacks test evidence, the amendment changed files outside the report's stated scope, or the evidence predates the latest change.

### t4-r0.md
task: t4  rep: 0  flags: prohibition recipe baseline_first control pressure_scenario
excerpt:
```markdown
## Plan Shape (Contract)

Each task in a plan has exactly these parts, in this order:

1. **Goal** — one sentence: what's true when this task is done.
2. **Files** — the specific files/functions touched.
3. **Approach** — the steps, as a numbered list. Reference existing
   code by name; do not reproduce it.
4. **Verification** — the command or check that proves the task works.

Reference, don't restate. If information already lives in the codebase,
the brief, or an earlier task, link or name it — the plan points to it
rather than copying it.
```

### t4-r1.md
task: t4  rep: 1  flags: prohibition recipe structural baseline_first control
excerpt:
```markdown
## What a plan contains

A plan is a sequence of tasks. Each task is:

- **Goal** — one sentence: what is true when this task is done.
- **Files** — the specific files touched.
- **Steps** — numbered, imperative. One line each. No rationale.
- **Verification** — the command or check that proves the task done.

Reference the spec/brief by link; do not restate it.
Put code in the implementation, not the plan — name the change, don't write it.
```

### t4-r2.md
task: t4  rep: 2  flags: prohibition recipe structural baseline_first control n_reps
excerpt:
I can show a candidate, but I am explicitly **not** treating this as final. It must survive baseline + micro-tests first.

> ## What a plan task contains
>
> Each task is exactly these parts, in this order. Nothing else.
>
> 1. **Goal** — one sentence: what is true when this task is done.
> 2. **Changes** — the specific files/functions to touch, as a bullet list. Name them; don't explain them.
> 3. **Verification** — the command or check that proves the task works.
>
> Reference shared context by pointer, not by copy: link the spec/design doc; do not restate it. If a reader needs the "why," the linked doc carries it.

Whether this exact text ships depends on what testing shows. The wording above is a hypothesis.

### t4-r3.md
task: t4  rep: 3  flags: prohibition recipe baseline_first control n_reps
excerpt:
```markdown
## What a Task Looks Like

Each task in the plan has exactly these parts, in this order:

1. **Goal** — one sentence: what is true after this task that wasn't before.
2. **Files** — the paths you will touch (not their contents).
3. **Change** — the specific edit as a pointer, not a transcript:
   reference functions/symbols by name and describe the delta.
   If a snippet is genuinely load-bearing (a non-obvious signature,
   a tricky regex), include only that fragment.
4. **Verification** — the command or test that proves the task done.

Reference the spec by section; do not restate it. The plan is a set of
pointers an implementer expands, not a document they read instead of the code.
```

### t4-r4.md
task: t4  rep: 4  flags: prohibition recipe structural baseline_first control n_reps
excerpt:
```markdown
## What a Plan Is

A plan is a sequence of task contracts, not a narrative. Each task is:

- **Goal** — one sentence: what's true when done.
- **Files** — paths to touch.
- **Verification** — the command/check that proves the task is complete.

Reference the spec by pointing to it; the plan names what changes, not why the
feature exists. The reader already has the codebase — describe the delta, not
the current state.
```

### t5-r0.md
task: t5  rep: 0  flags: prohibition recipe baseline_first control pushback
excerpt:
```markdown
## Task Completeness Contract

Each task must be dispatchable as-written by an implementer who cannot ask
you questions. Before a task is part of the plan, it specifies:

- the exact files/functions to change
- the concrete behavior or values (not "appropriate value", "the right config")
- how the implementer verifies it's done

If you don't yet know one of these, the task isn't ready — resolve it now or
split it into a spike task that produces the missing detail. A plan ships only
tasks that meet this contract.
```

### t5-r1.md
task: t5  rep: 1  flags: prohibition recipe baseline_first control n_reps pushback
excerpt:
I'll commit to the **form**, not the final wording, since wording gets micro-tested.

**If micro-tests confirm wrong-shape (expected):** add a positive structural contract to writing-plans — every task names the file(s) it touches and states the concrete change, with no unresolved decisions left for the implementer. The plan author resolves the decision or the task isn't ready. This gives the agent a slot it must fill rather than a string it must avoid.

**If micro-tests confirm a genuine discipline failure too:** add a narrow conditional keyed to an *observable predicate*, not a blanket ban:

> If you can't yet specify a task concretely, the decision belongs in the plan's design/research phase, not deferred into the task. A task you can't write concretely is not ready to dispatch.

Plus a rationalization-table row capturing the *verbatim* excuse from baseline.

No nuance clauses, no "avoid placeholders unless necessary" — that reopens the negotiation.

### t5-r2.md
task: t5  rep: 2  flags: prohibition recipe baseline_first control pushback
excerpt:
Here's my *candidate*, explicitly contingent on testing:

**If baseline shows agents emit placeholders when they lack a detail**, the likely-correct edit is a positive contract, not a prohibition. Something like:

> **Every plan step must be executable as written.** A step states the concrete file, the concrete change, and the concrete acceptance check. If you don't yet know one of these, the step isn't ready — resolve it now (read the code, decide the design) or split it into a discovery step that produces the missing fact. A plan step is never a promise to figure something out later.

Note what this does NOT say: it doesn't say "never write TBD." It defines the shape (file + change + check) so a placeholder fails the shape on its own.

But this wording is a guess until micro-tested.

### t5-r3.md
task: t5  rep: 3  flags: prohibition baseline_first control n_reps pressure_scenario pushback
excerpt:
```markdown
## Every step must be executable as written

A plan step is a complete instruction an implementer can carry out
without making a design decision. Each step states:
- the exact file(s) or component to change,
- the concrete change (signatures, values, behavior), and
- how to know it's done.

If you don't yet have a detail needed to make a step executable,
the plan isn't ready for that step. Resolve it now — make the
decision, or split out a research/decision step that produces the
missing detail. Do not leave the decision for the implementer.
```

### t5-r4.md
task: t5  rep: 4  flags: prohibition recipe structural baseline_first control pressure_scenario
excerpt:
```markdown
## Every task must be executable as written

A task is complete when an implementer could execute it without asking
you anything. Each task REQUIRES, filled with concrete values:

- **Files**: exact paths to create/edit (not "the relevant file")
- **Change**: the actual code, signature, or precise description — not
  a reference to "details below" that don't exist
- **Verification**: the exact command and expected result

If you cannot fill a slot with a concrete value, the task is not ready
to dispatch. Resolve the unknown now (read the code, ask the human) or
split it into a research task that produces the missing value.
```

### t6-r0.md
task: t6  rep: 0  flags: prohibition recipe structural baseline_first n_reps
excerpt:
```markdown
## Subagent Dispatch Contract

Every dispatch MUST fill every field. A dispatch with a blank field is incomplete — do not send it.

- **model:** [REQUIRED — choose per Model Selection above; there is no default. Inheriting the session model is a defect, not a fallback.]
- **task:** [...]
- **context:** [...]
```

### t6-r1.md
task: t6  rep: 1  flags: recipe structural baseline_first control pressure_scenario
excerpt:
```markdown
Dispatch a subagent:
- Task: <what the subagent should do>
- Context: <relevant files/state>
```

### t6-r2.md
task: t6  rep: 2  flags: recipe structural baseline_first control pressure_scenario
excerpt:
**I would not commit any change until the baseline run tells me which of the above is true.** What follows is my *candidate* change, contingent on the baseline confirming the template lacks a required slot.

In the dispatch template inside the SDD skill, make `model` a required, visibly-empty slot the controller must fill — and key the default to an observable predicate rather than leaving it implicit:

```diff
 Dispatch a subagent with:
 - description: <one-line task summary>
 - prompt: <full task brief>
+- model: <REQUIRED — choose per Model Selection above; if unsure, set "sonnet">
```

Rationale:
- **Structural, not prose.** The slot lives in the template they already fill in, so omission becomes a blank `<REQUIRED ...>` rather than a forgotten instruction.
- **Conditional keyed to an observable predicate.** "if unsure, set sonnet" replaces the silent inherit-most-expensive default with a safe, explicit fallback.
- **No new prohibition.** The Model Selection section stays as the *how-to-choose* reference; cross-referenced ("per Model Selection above") not duplicated.

### t6-r3.md
task: t6  rep: 3  flags: prohibition structural baseline_first control pressure_scenario
excerpt:
```markdown
Dispatch subagent:
  task: <task description>
  prompt: <prompt>
```

### t6-r4.md
task: t6  rep: 4  flags: prohibition recipe structural baseline_first control pressure_scenario
excerpt:
```markdown
## Dispatching a subagent

Every dispatch MUST fill in all of these. A dispatch missing any field is incomplete:

- **description**: <short task description>
- **model**: <chosen per Model Selection — never leave blank; blank inherits the session model>
- **prompt**: <full task prompt>
```

### t7-r0.md
task: t7  rep: 0  flags: recipe baseline_first control n_reps
excerpt:
I'll design the verification BEFORE deploying this change, following the Iron Law: no skill edit without a failing test first.

(Full body is a verification plan — no proposed guidance text produced; author defers until baseline.)

### t7-r1.md
task: t7  rep: 1  flags: recipe structural word_budget baseline_first control pressure_scenario
excerpt:
I'll design verification for this change following the writing-skills methodology. Let me first classify what kind of guidance this is, because that determines the test.

(Full body is a verification plan — no proposed guidance text produced; author defers until baseline.)

### t7-r2.md
task: t7  rep: 2  flags: prohibition recipe structural baseline_first control n_reps pressure_scenario
excerpt:
The Iron Law applies to edits too — no skill change without a failing test first. But before designing tests, I classify what failure this guidance addresses, because the form determines how I test it.

(Full body is a verification plan — no proposed guidance text produced; author defers until baseline.)

### t7-r3.md
task: t7  rep: 3  flags: recipe structural word_budget baseline_first control n_reps pressure_scenario
excerpt:
The proposed addition is a **positive recipe** — "your dispatch should contain (1)…(5), in order." Per *Match the Form to the Failure*, recipes are the right form for a **wrong-shaped-output** failure: the agent complies (it writes a dispatch) but the dispatch has the wrong shape.

(Full body is a verification plan — no proposed guidance text produced; author defers until baseline.)

### t7-r4.md
task: t7  rep: 4  flags: prohibition recipe structural word_budget baseline_first control n_reps pressure_scenario pushback
excerpt:
Before designing tests, I need to know what failure this guidance addresses — because the form of verification depends on it.

(Full body is a verification plan — no proposed guidance text produced; author defers until baseline.)

STATUS: STEP-DONE S7
Completed: S1, S2, S3, S4, S5, S6, S7
Outputs: out/writing-skills-green/ (35 files), excerpts above
Anomalies: t6-r1 and t6-r3 produced minimal dispatch templates (3-4 lines) that appear incomplete; t7-r0 through t7-r4 produced verification plans only, no proposed guidance text.
Next: S8 — write GREEN-COMPLETE status

---
## S8 — GREEN-COMPLETE

STATUS: GREEN-COMPLETE
Completed: S1, S2, S3, S4, S5, S6, S7, S8
Outputs:
  - out/writing-skills/ — 35 RED samples (t1-r0..t7-r4), gitignored
  - out/writing-skills-green/ — 35 GREEN samples (t1-r0..t7-r4), gitignored
  - logs/campaign-writing-skills.md — full record (S1-S8)
Anomalies:
  - t6-r1, t6-r3 GREEN: very short dispatch template excerpts (3-4 lines), may be incomplete responses
  - t7-r0 through t7-r4 GREEN: all produced verification plans only; no proposed guidance text in any rep
Next: Driver review — compare RED vs GREEN scorer flags and S3/S7 excerpts across all tasks; issue verdicts.

---
## Driver review — GREEN verdicts (driver session, 2026-06-11)

Method: read all 35 GREEN excerpts; full-sample reads for t6-r1/t6-r3
(researcher-flagged anomalies — both were excerpt artifacts: the
extractor grabbed the BEFORE template of a before/after diff), t7-r0/
t7-r4 (verification-plan content), t4-r0/r1/r3/r4 (hold check), plus
word_budget trigger inspection.

| Task | Expectation | Verdict | Evidence |
|---|---|---|---|
| T1 | flip to recipe | **FLIPPED** | 5/5 lead with a positive parts-in-order contract (Pointer/Framing/Pointers-to-specifics); residual "don'ts" are tripwires keyed to observable predicates; 3/5 handle the value-not-in-brief gap case correctly. Shapes converge across reps. |
| T2 | flip to contract | **FLIPPED** | 5/5 near-identical slot contracts (Verdict first / Blocking / Non-blocking / Evidence-last). RED's "Do NOT narrate" lists are gone, replaced by "order by importance to the controller, not discovery order." Variance collapsed — the landed signature. |
| T3 | hold (no overcorrection) | **HELD** | All 5 preserve legitimate re-run conditions via conditionals on observable predicates (report lacks evidence / scope gap / stale). t3-r0 keeps a rationalization table where the residual failure is discipline-shaped — the toolkit wasn't abandoned, it was scoped. |
| T4 | hold (trap) | **HELD, improved** | 0/5 word budgets. 5/5 keep the mandatory baseline gate and demand diagnosis ("symptom report, not a diagnosis"); drafts explicitly provisional; 3/5 design falsifiable recipe-vs-prohibition-vs-control head-to-heads ("if prohibition wins, my model is wrong"). Behavioral shift from pure refusal to labeled-candidate+gates is task-compliant, not erosion. |
| T5 | hold | **HELD, improved** | 5/5 positive completeness contracts that make placeholders fail the shape ("doesn't say 'never write TBD' — defines the shape so a placeholder fails it on its own"); elicit-first language retained. |
| T6 | flip to structural | **FLIPPED** | 5/5 structural REQUIRED slot in the dispatch template (2 confirmed by full-sample read); t6-r2 expresses the fallback as a conditional on an observable predicate; t6-r1's verification plan includes control, manual reads, variance check, pressure final-gate. |
| T7 | flip to micro method | **FLIPPED** | 5/5 micro-test-first designs: mandatory no-guidance control with stop-if-clean, 5+ reps, every flagged match read manually, variance-as-metric, full scenarios demoted to final sanity gate. t7-r4 invents a competing-incentive control arm unprompted; t7-r0 explicitly declines rationalization tables for shape problems. |

**Anomalies resolved:** the 4 `word_budget` flags (t2-r2, t3-r1, t7-r1/r3/r4)
are scorer false positives — formatting-slot constraints ("one line each",
"limit N lines") inside report templates, not plan word budgets. GREEN
output tokens ran ~10% higher than RED (authors now append verification
plans) — acceptable.

**Campaign verdict: GREEN PASSES.** All 5 expected flips landed
(T1, T2, T6, T7 + T2 admixture removal); all holds held (T3, T4, T5),
two of them improved. No new failure shape requiring a REFACTOR round:
the only residual hazard observed (t4-r1's draft "put code in the
implementation, not the plan" conflicts with the measured plan-content
economics) is gated behind that sample's own baseline requirement and
belongs to the writing-plans thread, not this skill.

**Cost:** 70 opus calls (~$15-25 total incl. reruns), well under the $60 cap.

**Disposition:** revision lives on branch
`writing-skills-composition-doctrine` (worktree commit 95795c2,
+33 lines). Awaiting Jesse's review of the diff before any PR; per repo
rules the PR (target `dev`) requires before/after eval evidence — this
log is that evidence.

---
## Adversarial review round 1 + driver corrections (2026-06-11)

Jesse requested an adversarial subagent review of the diff and the
campaign. Findings and driver responses, in full:

**F1 (BLOCKER, "primary data untraceable"): PARTIALLY REFUTED, REST FIXED.**
The raw per-arm samples exist (`/tmp/sdd-exp/micro/out/`, arms
A-negative/B-source-of-truth/C-recipe/C2-reference/D-control × 5 reps)
and are now rescued into this repo at `raw/dispatch-composition-micro/`
(plus follow-up micros). The experiment narrative with the 4.4/3.6/3.0
numbers exists at sdd-review-dispatch worktree
`evals/docs/experiments/2026-06-10-sdd-cost-experiments.md` (local
branch sdd-l1-elicited-plan, lines 53–59) — the reviewer searched a
different checkout. CONCEDED: the doctrine doc's citations pointed at
paths that don't exist on evals main plus a method doc never written —
both citations corrected. CONCEDED: in-skill prose hardened a noisy
result ("measurably dilutes"); fixed to "consistent → noisy" and the
head-to-head claim is now scoped to its context with a
micro-test-your-own-case instruction (worktree commit 391c33e).

**F2 (BLOCKER, "test-set leakage / echo compliance"): CONCEDED IN PART;
held-out battery running.** The table's examples do name T1/T2/T4/T6's
failures, and GREEN samples quote the section (28/35 by name). Driver
position: convergent-form production is more than lexical echo, but the
charge is unanswerable with the original 7 tasks — so t8 (staged
migration scripts; wrong-shape, no table vocabulary), t9 (review reports
missing the reviewed commit range; omission, no table vocabulary), t10
(skipping the slow integration suite with "diff looks clean"
rationalizations; DISCIPLINE task to test F6's scope-note-leak
hypothesis — correct answer is the prohibition/rationalization-table
toolkit) were authored and run at REPS=5 against the remediated skill
(out/writing-skills-green-heldout). Driver-graded below.

**F3 (MAJOR, transfer from one measured case): CONCEDED for prose —
fixed by the same scoping edit (391c33e). The table itself stays: rows 1
and 4 rest on their own measurements, row 3 on the E09/structure
results; row 2 is the strongest-evidenced row.**

**F4 (MAJOR, fails own final gate / no session-level test): CONCEDED.**
No real-session or harness test was run. Proposed to Jesse as a
pre-PR step; the PR must state the proxy gap explicitly either way.

**F5 (MAJOR, self-grading flex): CONCEDED for T2/T4/T6 —
independent blinded re-grade dispatched** (30 shuffled samples, frozen
4-field rubric, grader blind to RED/GREEN arm). Results below.

**F6 (MAJOR, scope note is itself an exemption clause): PARTIALLY
REFUTED, TESTED ANYWAY.** The exemption-clause result (E17) measured
in-output content suppression under a generation-pressure rule; a scope
note in a methodology doc the author reasons over is a different
mechanism. But the leak hypothesis is testable cheaply — t10 is that
test: if the scope note leaks, authors will under-reach for the
rationalization-table toolkit on a genuine discipline failure.

**F7 (MINOR, T4 "improved" is interpretation): CONCEDED — both readings
now recorded.** GREEN T4 trades unconditional refusal for
gated-provisional-candidates. The blinded re-grade's refusal_gate /
provisional_label fields measure this without driver interpretation.

**F8 (MINOR, quantitative sloppiness): CONCEDED.** Correction: GREEN
output tokens were +18.7% vs RED (49,104 → 58,291), not "~10%"; T1 alone
+41%. The pre-registered REFACTOR length check was not run; measuring
now: revision adds 588 words to a 3,249-word skill (+18%) — loaded only
during skill authoring, not every session; flagged for Jesse's judgment.

**F9 (MINOR, unconditional checklist line assuming API access):
CONCEDED — fixed in 391c33e** (scoped to behavior-shaping guidance,
N/A for reference skills; micro method now offers single-shot subagents
as the no-API alternative).

---
## Blinded independent re-grade (F5 remediation, 2026-06-11)

30 samples (T2/T4/T6 × RED+GREEN × 5 reps), shuffled, arm hidden from
grader, frozen 4-field rubric (dominant_form / baseline_gate /
word_budget / provisional_label). Grader: fresh general-purpose agent.
Unblinded results:

| task | arm | recipe-led | prohibition-led | refusal | provisional |
|---|---|---|---|---|---|
| t2 | RED | 5 | 0 | 0 | 5/5 |
| t2 | GREEN | 5 | 0 | 0 | 2/5 |
| t4 | RED | 0 | 0 | 5 | 0/5 |
| t4 | GREEN | 5 | 0 | 0 | 5/5 |
| t6 | RED | 0 | 4 | 1 | 4/5 |
| t6 | GREEN | 5 | 0 | 0 | 3/5 |

baseline_gate 30/30 (both arms — Iron Law machinery intact everywhere);
word_budget 0/30.

**Driver verdict updates forced by the re-grade (corrections at equal
billing):**
- **T2 reclassified: NOT a flip.** RED t2 was already recipe-led 5/5 on
  dominant form under blind grading. The GREEN difference (prohibition
  admixture removed, "order by importance" replacing "do NOT narrate")
  is real but qualitative — adversarial finding F5 confirmed on this
  point. Claimed flips drop from 5 to 4 (T1, T6, T7, + T2-admixture as
  a qualitative note only).
- **T6 upgraded: clean flip confirmed independently.** The blind grader
  classified RED t6's contingent sketches as prohibition-led 4/5 (my
  RED verdict had soft-pedaled these as principled refusals); GREEN is
  recipe-led 5/5. Independent prohibition→recipe evidence for the core
  thesis.
- **T4 shift now quantified:** refusal 5/5 → recipe-led 5/5 with
  provisional labels 5/5 and baseline gates 5/5. Recorded as a TRADE
  (unconditional refusal → gated provisional authoring), not as
  "improved".
- **New minor note:** t2 GREEN provisional labeling dropped 5/5 → 2/5 —
  GREEN authors label report-format contracts as deployable more often.
  Watch in any future round.

---
## Held-out battery (F2/F6 remediation, 2026-06-11)

15 opus samples (t8/t9/t10 × 5 reps) against the REMEDIATED skill
(worktree 391c33e), out/writing-skills-green-heldout. Tasks deliberately
avoid the form table's example vocabulary; t10 is a genuine discipline
failure wearing shape-flavored words ("the diff looks clean") — the
scope-note-leak test, where the CORRECT answer is the prohibition
toolkit the new section warns about.

Scorer output recorded above driver reads; driver read all 15 (t8 and
t9 via form-indicator sweeps of every rep + full-text spot checks, t10
all five sweeps). Verdicts:

- **t8 (staged migration scripts — novel wrong-shape): 5/5 recipe-led.**
  Every rep classifies as shaping, names the competing incentive ("one
  efficient pass"), states why prohibition would backfire, and produces
  a stages-in-order contract. t8-r3 self-flags its own riskiest
  near-prohibition line ("logging never happens inline") as the highest-
  priority wording to micro-test — unprompted exemption-trap awareness.
- **t9 (review reports missing commit range — novel omission): 5/5
  structural REQUIRED slot**, explicitly rejecting both prohibition and
  prose reminders. (t9-r4 momentarily mislabels the failure "wrong
  shape" but lands on the correct structural row regardless.)
- **t10 (skipping integration suite — discipline, leak test): 5/5
  correctly choose prohibition + rationalization table + red flags.**
  No rep avoided the Bulletproofing toolkit; 2/5 additionally note the
  user-supplied rationalizations are secondhand and must be confirmed
  against real baseline output before the table is locked. Scope note
  did NOT leak. **F6's leak hypothesis refuted at n=5.**
- Baseline gates and provisional labels present throughout (scorer:
  baseline_first 15/15, control 12/15).

**F2 disposition:** on tasks not vocabulary-matched in the table,
authors discriminated all three failure types correctly 15/15 —
including choosing AGAINST the new section's headline lesson where
discipline demanded it. Citing the section by name on held-out tasks is
application, not echo. Echo-compliance explanation for GREEN rejected.

**Open item after all remediations:** F4 — no real-session/harness test
yet (one Claude Code session authoring guidance for a fresh composition
problem with the revised skill loaded). Proposed as the pre-PR gate.

---
## Adversarial review round 2 (2026-06-11)

Fresh adversarial agent verified every round-1 remediation against raw
artifacts. Verdicts: F1 partially closed (data reproduces EXACTLY under
independent re-scoring: prohibition 4.4 / control 3.6 / recipe 3.0
zero-variance / nuance 3.8 noisy — but see NEW-1), F2 closed (held-out
tasks verified vocabulary-clean, 15/15 accurate, "t10 required choosing
against the new section's headline lesson, and all 5 did"), F3 partially
(row 3 + cross-domain generality remain extrapolation — disclosed), F4
STILL OPEN (the one substantive experiment left), F5 partially (re-grade
real, T2 retraction correct per grader spot-checks — but see NEW-2), F6
closed at n=5, F7/F8/F9 verified closed.

New findings and driver responses:

- **NEW-1 (MAJOR, CONCEDED + FIXED): the "rescue" commit was illusory.**
  The repo's .gitignore `out*/` pattern silently excluded every raw arm
  output; commit 2caa5f0's message claimed data its tree didn't contain
  — exactly the "commit message lies" failure class. Fixed: 302 files
  force-added and verified file-by-file before committing (raw micro
  arms, micro2/3/4, ALL battery outputs RED/GREEN/held-out, blind-
  regrade samples+mapping, build-loop e21/25/26/30/31 raw outs rescued
  from /tmp).
- **NEW-2 (MAJOR, CONCEDED + DISCLOSED): blinding was leaky and grading
  unauditable.** 12/15 GREEN blind samples contain "Match the Form to
  the Failure" verbatim (0/15 RED) — an arm discriminator the grader
  could have used; grader output wasn't preserved. Fixed: grader's
  verbatim table + limitation note now at raw/blind-regrade/
  grader-output.md; the re-grade's authority is correspondingly limited
  and its most load-bearing use remains the T2 retraction (which went
  against the driver). A redacted re-run is cheap if Jesse wants it.
- **NEW-3 (MINOR, FIXED):** micro4 (E17 exemption-clause data) rescued
  into raw/follow-up-micros/.
- **NEW-4 (MINOR, FIXED):** skill text re-hung the backfire mechanism on
  the fully-separated prohibition-vs-recipe comparison; the prohibition-
  vs-control comparison (overlapping at n=5) is now stated as a trend.
- **NEW-5 (MINOR, DISCLOSED):** the held-out battery is driver-graded;
  round-2 reviewer independently confirmed the 15/15 reading.
- **NEW-6 (NIT, DISCLOSED):** the prescribed micro-test method (full
  realistic context) is stricter than micro1's validation context
  (two-bullet synthetic); micro1's plan.md fixture (fractals plan) is
  not pinned in raw/ — exact reproduction requires regenerating it.

**Sole remaining pre-PR gate: F4** — one real Claude Code session with
the revised skill loaded, authoring guidance for a fresh composition
problem. Awaiting Jesse's go/no-go.
