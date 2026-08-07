# Deferred Experiments

Specified but unfunded. Each entry names its TRIGGER — the observation or
decision that should revive it — and where its full spec lives. Entries
leave this list by being run (verdict in a campaign log) or by being
retired with a dated note. Add new deferrals here at close of campaign.

## x9a2 — escape-hatch tightening for rule-and-continue

**What:** "a written ruling is never a guess; confirm-asks on made rulings
are stalls" — tightens the stop clause that shipped in superpowers PR
#2077. Arm `cp/x9a2` @ f42d72a (battery-run verbatim; applies cleanly to
merged dev as of 2026-08-05).
**Why deferred:** the ride-along bundling failure it targets was observed
(3/4 adjudicated gpt-5.6 eval sessions; interrogation-convergent
mechanism) but is cheap when it occurs (extra questions on a legitimate
stop; recovered by one deflection every time), and x9a2's own battery
couldn't attribute a reduction — the base rate didn't reproduce that day
(0/3 treatment vs 0/2 control). One model family, eval fixtures only.
**Trigger:** any real-world report of a rule-and-continue session bundling
ruling-confirmations onto a stop (any model), or the bundling base rate
reproducing in a future battery.
**Refs:** logs/2026-08-01-queue-campaign.md (composed-battery finding),
logs/2026-08-02-backlog-campaign.md (T3 verdict),
logs/2026-08-03-plan-decomposition-campaign.md (ride-along
interrogation).
**Est.:** $0 to revive the text; ~$35 for a fresh attribution battery
gated on the trigger reproducing the base rate.

## K1' — knowledge-forwarding as decision-consistency
> **Series answer 2026-08-07 (K1g verdict):** Jesse's live case —
> Task 1 discovers the plan is wrong about reality; later tasks must
> not re-discover it — is HANDLED by shipped superpowers on the K1g
> fixture: the controller rules on the mismatch and carries the
> ruling into later dispatches (11/12 later-task seats show no
> firsthand runtime re-discovery — a bound, per the 2026-08-07 audit;
> dispatch-carry verified by hand-read sampling on codex and by the
> readable dispatch channel on sonnet). All 8 reps converged on the real
> API with zero drift. The handoff arm added nothing over the
> dispatch channel. Verdict:
> logs/2026-08-05-adjudication-battery.md. Revive only on a
> real-world re-discovery trace or a cross-model controller cell.

**What:** K1's handoff mechanism bound fully (read 5-6/6, appended every
task) but bought no re-read reduction. The unmeasured axis where observed
"## Task N integration decisions" blocks suggest value: whether a
cross-task BINDING DECISION seeded in an early task survives into later
tasks' implementations with vs without the handoff.
**Trigger:** funding a correctness-axis battery with a fixture where
centralization is IMPOSSIBLE (two consumers in different languages or
across a process boundary, no shared module). The 2026-08-07 K1'
battery (k1p-decision-consistency) went null-by-headroom: given a
shareable constant, every control rep centralized it and delegated,
so the drift class was empty. Mechanism-binding confirmed twice
(handoff written/read every task); outcome untestable on
shared-module fixtures.
**Refs:** logs/2026-08-03-plan-decomposition-campaign.md (K1 verdict);
arm `cp/pd-k1` @ 76884ac.
**Est.:** fixture ~1 session + ~$60 battery (6 reps, two arms).

## P3 — walking-skeleton ordering, integration-trap fixture

**What:** current fixtures complete at ceiling regardless of plan shape,
so ordering rules are untestable on them. Needed: a spec with a seeded
integration trap — two subsystems whose contract fails only when
composed — so horizontal plans hit rework at the last task and skeleton
plans at slice one. Metric: rework commits/tokens after first
integration failure.
**Trigger:** a fixture where the integration mistake COMPOUNDS — the
wrong convention baked into many call sites by the time a late
integrator finds it — or a real-world trace of expensive late rework.
The 2026-08-07 P3 battery (p3-integration-trap) was
INCONCLUSIVE-BY-CEILING one level up (CORRECTED per the 2026-08-07
audit): sessions harmonized the seeded contract at spec/plan-writing
time, the runtime trap fired 0/8, and no ordering effect of any size
was measurable. The skeleton arm's one e2e-first plan still cost
2-3×. A trap harmonizable at plan time cannot discriminate ordering
rules.
**Refs:** logs/2026-08-03-plan-decomposition-campaign.md (P3/P4
disposition).
**Est.:** fixture ~1 focused session (cp-x10-class effort) + ~$70
battery.

## T9 — tooling-ask placement A/B (interactive) — RETIRED 2026-08-07

**Run and shipped.** The interactive cell ran 2026-08-06 (9 reps,
t9-tooling-ask scenario): control 0/3 ever asked, both placements
fired 3/3 before any code with constraints landing 6/6. Jesse chose
Draft A (brainstorming design-presentation) → superpowers draft PR
#2101. Verdict: logs/2026-08-05-adjudication-battery.md.

## R1 — triage-classes text, verbatim battery

**What:** the R1 micro showed downgrade-to-deferred / cleanup-wave triage
achieves non-blocking structure-noise handling with zero guard cost
(8/8 seeded-bug protection under every policy). Shipping it as SDD text
requires the standing rule: the exact text must run a full battery first.
**Trigger:** drafting the SDD triage-classes text for a PR.
**Refs:** logs/2026-08-03-plan-decomposition-campaign.md (R1 verdict).
**Est.:** ~$35 (4 reps, one arm vs existing controls).

## d1s — structural evidence lease (review-package emits TEST-EVIDENCE)

**What:** arm built (`cp/pd-d1s` @ f4af30b): review-package prints the
tree-identity lease + exact check command. Parked because the split
scorer showed truly-redundant same-tree controller runs are ~1/rep in
every arm — no headroom at current fixture scale.
**Trigger:** a scenario (or real-world trace) showing a redundant-run
class materially above ~1/rep.
**Refs:** logs/2026-08-03-plan-decomposition-campaign.md (d1 reframe);
campaigns/cost-pathologies/score_d1_split.py.
**Est.:** $0 to revive; ~$35 battery.

## Campaign-3 tier 2 — CLAUDE.md-lift promotions

**What:** (a) U-simple-first: −31% tokens at n=24 in screening; tier 2 =
marginal cells over the superpowers baseline (does it still buy anything
with the plugin loaded?). (b) Verification-floor unit from the C3
interrogation ("a scope statement bounds the deliverable, not your
verification") — predicted to move the adjacent-breakage look rate where
U-broken-windows alone stayed 0/8; 3-arm micro, n=8.
**Trigger:** RESOLVED 2026-08-07 (Jesse: "run that now"). (b) ran
positive — verification-floor moves sonnet's flag rate 0/8 → 3/8
(+37% rep cost); promoted into the vfloor-tdd quorum battery. (a) ran
null-by-fixture-shape — with the plugin loaded, one-shot probes stall
at brainstorming's gate and write no code, so overbuild is
unobservable at the host tier; the marginal question needs a
quorum-static scenario with a scripted approval reply if ever funded.
Verdicts: logs/2026-08-03-claudemd-lift.md.

## Adversarial-runtime-findings fixture — exercises rebut + r1t + vfinish

**What:** the adjudication battery graded rebut/r1t SAFE but their
primary triggers never arose on cp-x1-edit-existing (no layout
divergences; no contested unreachable-runtime findings — internal
reviewers accept-and-fix real defects instead of contesting
theoretical ones). The vfinish text (final-reply names any watched
test failure) joined the same bucket 2026-08-07: at quorum-static
probe scale no saw-and-stayed-silent was observed (11/11 reps with
an observed saw event mentioned it — corrected count per the
2026-08-07 audit; the whole arm effect is at LOOK, which is vfloor's
lever), so vfinish's trigger needs SDD-scale
sessions where suites run mid-workflow and failures scroll past.
One fixture serves all three: a scenario whose review channel seeds
plausible-but-unreachable RUNTIME findings (the serf Roborev shape),
plus a behavior-preserving layout divergence, plus an internal suite
whose pre-existing failure scrolls past mid-session.
**Trigger:** funding the fixture build (~1 session, cp-x10-class), or
a real-world report of any of the three failure classes under the
merged skills.
**Refs:** logs/2026-08-05-adjudication-battery.md (final verdict +
2026-08-07 slate verdict); arms cp/r1t 08972e6, cp/rebut 52df997,
cp/r1t-rebut 77ec054, cp/vfinish b870fb6.
**Est.:** fixture ~1 session + ~$70 battery.

## Cross-model validation cells — kimi / glm — RETIRED 2026-08-07

**Run.** The kimi (oauth = kimi-for-coding; openrouter =
moonshotai/kimi-k2.7-code) and glm-5.2 (pi/openrouter) lanes were
wired 2026-08-06 via the quorum credential seam. The priority cell —
the #2086 spec contrast — replicated on both: spec-present 5/5×4,
specless 0/5×4, posted to merged PR #2086. sp-adjacent-breakage also
ran full kimi/glm columns. Verdicts:
logs/2026-08-05-adjudication-battery.md (2026-08-07 slate entry).
Future cross-model asks are ordinary battery config now, not a
deferred experiment.

## Aged-session replay — first consumer

**What:** the replay-harness design (commit-boundary cuts,
compacted-replay primary, in-distribution + fresh-prefix negative
controls) has no consumer since its intended first user (X3-B) was
ruled unreachable on constructible fixtures.
**Trigger:** a hypothesis that specifically needs aged/compacted-context
sessions (e.g. late-session skill-compliance decay).
**Refs:** docs/2026-08-03-aged-session-replay-design.md.
