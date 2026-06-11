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
