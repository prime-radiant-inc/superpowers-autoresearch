# Rationalization Interrogation — Method Note (2026-08-04)

When a treatment fails or a session misbehaves, the transcript tells
you WHAT happened; it rarely tells you the operative reasoning. This
method (Jesse's directive, first applied to the X11 null) recovers
that reasoning and turns it into skill text — usually a
rationalization-table row whose trigger and counter come from the
model itself.

## The loop

1. **Locate the wrong act** in the rollout: the event where behavior
   diverged from the skill's instruction (a redundant test run, a
   dismissed real conflict, a missed defect, a turn-1 bundled ask).
2. **Extract the surrounding context**: the 5-8 events before the act
   (reasoning summaries, messages, exec calls, tool outputs) — enough
   that the situation is recognizable, small enough to present
   cleanly.
3. **Elicit from the same model family**: present the excerpt plus
   the rule that was in force, and ask for three fields in first
   person: RATIONALIZATION (the thought that made the act feel right),
   TRIGGER (what feature of the situation activated it), COUNTER (the
   one-sentence reply that would have stopped it at that moment).
4. **Look for convergence across reps.** One rep's answer is an
   anecdote; four reps eliciting the same class (as X11 did — the
   post-merge "new HEAD, run the suite" habit, 4/4) is a mechanism.
5. **Encode and re-test.** The convergent trigger and counter become
   skill text — a rationalization-table row in the trigger's own
   vocabulary, plus any mechanical check the counter implies — and
   the new arm goes through a normal pre-registered battery. The
   elicitation is hypothesis generation, never the verdict.

## Caveats (bind every use)

- **Post-hoc confabulation**: the elicited reasoning is the model's
  reconstruction, not a log of its forward pass. Treat it as a
  hypothesis that must survive a battery; disclose the caveat in the
  log entry that transcribes the elicitation.
- **Model match matters, loosely**: elicit from the same family the
  session ran on (exact snapshot when servable; nearest sibling
  otherwise, disclosed). Cross-family elicitations answer a different
  question.
- **The letter-vs-intent check**: before writing new text, re-read
  the FAILED text against the elicited trigger. X11's lesson: the
  prohibition said "same commit," the behavior lived at the
  post-merge moment where the commit ID changes over an identical
  tree — the null was a mis-specified trigger, not an immovable
  behavior. Interrogation distinguishes "text can't reach this" from
  "text aimed at the wrong moment," which no outcome metric can.
- **Cost**: pennies. Run it BEFORE designing a successor arm to any
  behavioral null, not after.

## Instrument

`campaigns/cost-pathologies/interrogate-rollout.py` — general
elicitation runner: takes a rep dir, an event selector, and an
elicitation frame; prints the three fields per rep for controller
transcription. Session-scratch prototypes get promoted here once a
frame proves out.

## Standing rule (added to campaign discipline)

Every behavioral-null verdict gets an interrogation pass before its
successor arm is designed, and the elicited fields are transcribed in
the log beside the verdict they explain.
