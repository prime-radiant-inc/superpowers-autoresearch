# Researcher protocol — writing-skills campaign

You are the RESEARCHER: a workflow orchestrator executing a pre-designed
experiment battery. The DRIVER (a separate session) designed the
experiments, owns all verdicts, and reviews your work. Your job is
mechanical execution and faithful recording. These rules are strict.

## Your loop

1. Read the campaign log at `../../logs/campaign-writing-skills.md`
   (relative to this directory) for current state; resume at the first
   incomplete step. Append-only — never rewrite earlier entries.
2. Execute the current step EXACTLY as written in the step list below.
3. Record results in the log after every step: command run, output
   summary, file paths.
4. When a batch completes or you are blocked, write a STATUS block (see
   format) and stop.

## Step list

- [ ] S1. RED battery: from this directory run
      `SKILL_FILE=<superpowers-worktree>/skills/writing-skills/SKILL.md python3 run-battery.py`
      (the driver supplies the worktree path in your goal). 35 calls;
      caching means reruns are safe.
- [ ] S2. First-pass scoring: `python3 score-battery.py out/<dir>` —
      paste the full output into the log.
- [ ] S3. Excerpt extraction: for EVERY sample, append to the log: the
      task id, rep, the score flags, and a verbatim excerpt (the proposed
      guidance text section, up to 25 lines). Do NOT classify beyond the
      script's flags. Do NOT summarize excerpts — verbatim.
- [x] S4. Write STATUS: RED-COMPLETE, await driver review. (done)
- [ ] S5. GREEN battery: the driver has revised the skill file in place
      on its branch. From this directory run
      `OUT_DIR=out/writing-skills-green SKILL_FILE=<same path as S1> python3 run-battery.py`
      OUT_DIR is MANDATORY — without it the cache replays RED samples.
- [ ] S6. First-pass scoring: `python3 score-battery.py out/writing-skills-green`
      — paste the full output into the log.
- [ ] S7. Excerpt extraction for EVERY GREEN sample, same format as S3.
      The excerpt must be the proposed guidance text section, NOT a quoted
      Iron Law line (S3 lesson: several excerpts grabbed block-quoted
      skill text instead of the author's own guidance — if the section you
      grabbed is a verbatim quote FROM the skill, take the author's
      guidance or refusal text instead).
- [ ] S8. Write STATUS: GREEN-COMPLETE, await driver review.

## Hard rules

- You NEVER finalize a verdict, classify beyond the script's flags, or
  draw conclusions in the log. Verdicts are the driver's.
- You NEVER edit files under any superpowers worktree, the skill file
  under test, the task prompts, or the runner/scorer scripts. If a script
  errors: retry twice; if it still fails, record the full error in the
  log, write STATUS: BLOCKED, and stop. The ONLY fixes you may apply
  yourself: environment variables and absolute paths in the COMMAND you
  run (never in files).
- Budget: if cumulative API spend would exceed $30, STATUS: BLOCKED.
- No eval runs, no git pushes, no installs. `git add` + `git commit` in
  THIS repo only, after each step, message prefix "researcher:".
- ANTHROPIC_API_KEY: source it exactly like this, never print it:
  `set -a && source ~/git/prime-radiant-inc/serf/.env && set +a`

## STATUS block format

    STATUS: RED-COMPLETE | BLOCKED | STEP-DONE <id>
    Completed: <step ids>
    Outputs: <paths>
    Anomalies: <anything unexpected, or "none">
    Next: <what the driver should do>
