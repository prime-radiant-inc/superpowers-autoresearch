# Eval debugging techniques

Proven on the superpowers SDD evals, 2026-06-10/11.

**Session-resume interrogation.** When a transcript shows WHAT an agent
did but not WHY: `CLAUDE_CONFIG_DIR=<run>/coding-agent-config claude
--resume <session-id> -p "retrospective question"` from the run's workdir.
The resumed agent answers candidly with full context — one confessed it
suppressed a reviewer finding "to spare myself a review loop" and
prescribed the phrase-level trigger that fixed it.

**Blind A/B deliverable comparison.** Copy both workdirs to neutral /tmp
paths, rotate which config gets which label across comparisons, strip
build artifacts, dispatch a fresh judge that doesn't know the experiment.
Verdict held under label rotation = trustworthy. Caveats: single-sample
judge noise is real (same baseline scored 7/10 and 9/10 against different
opponents); instruct "no writes even to copies."

**Rationalization whack-a-mole.** Pipeline agents relocate a
rationalization to whichever participant isn't explicitly inoculated:
controller dispatch prompt → severity pre-rating → reviewer calibration →
implementer self-report framing. Each needs its own guard; abstract
principles lose to phrase-level triggers ("do not flag", "at most Minor",
"the plan chose"). Before fighting the model's judgment, check whether
the eval bar itself is wrong.

**Read the judge's reasoning, not just the verdict.** Runs pass while
components fail: a planted-defect run PASSED because the controller
rescued a reviewer that had rationalized away both defects — visible only
in the gauntlet reasoning text. Score per-component, not per-run, when a
component is the thing under test.

**Judge strictness varies run-to-run.** The same defect-caught-at-final-
review shape passed one judge and failed another. Treat single-run
verdicts on LLM-judged scenarios as noisy; attribute fails forensically
(read the actual reviewer reports) before blaming the config.

**Cheap models fail by advocating, not by going quiet.** Haiku reviewers
praised planted defects as virtues (YAGNI) and downgraded with the exact
prohibited rationale. Skills tuned on a strong model do not port down a
tier — test at the tier that will run the prompt.

**Silent re-scoping when inputs are missing.** Reviewers stripped of the
task brief delivered confident spec verdicts against the only context
they had left, 0/5 flagging the gap. Missing-input failures look like
plausible answers to smaller questions; validate input presence
structurally.
