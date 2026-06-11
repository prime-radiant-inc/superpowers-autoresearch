# Experiment batch A-E run mapping (2026-06-10, launched ~simultaneously, 7-way parallel)
# NOTE: wall-clock under 7-way parallel load — treat time numbers with suspicion; tokens/$ unaffected.
bwh4tztdu  A lean run 1   SUPERPOWERS_ROOT=/tmp/sdd-exp/lean  sdd-go-fractals
blxjrns34  A lean run 2   SUPERPOWERS_ROOT=/tmp/sdd-exp/lean  sdd-go-fractals
bin1o1nx1  A lean run 3   SUPERPOWERS_ROOT=/tmp/sdd-exp/lean  sdd-go-fractals
bndlnqu1m  A combo run    SUPERPOWERS_ROOT=/tmp/sdd-exp/combo sdd-go-fractals (combo now at 9a25a75 = branch HEAD, doubles as fe90d6c validation)
b4ahv2nnh  B crisp run 1  SUPERPOWERS_ROOT=/tmp/sdd-exp/combo sdd-go-fractals-crisp
bwbbie1ek  B crisp run 2  SUPERPOWERS_ROOT=/tmp/sdd-exp/combo sdd-go-fractals-crisp
brk354cby  E svelte n=2   SUPERPOWERS_ROOT=/tmp/sdd-exp/combo sdd-svelte-todo
# lean clone = 9a25a75 + f809deb (revert brief/report mechanism only)
# result dirs (launch order == timestamp order; verify lean/combo via SUPERPOWERS_ROOT grep in transcript before recording):
# 220654Z-e478 lean1 | 220656Z-ee4d lean2 | 220658Z-751f lean3 | 220659Z-d170 combo-fractals
# 220701Z-f21c crisp1 | 220703Z-45f0 crisp2 | 220704Z-c47f svelte-combo
bu26wxubs  C sonnet-controller run 1  SUPERPOWERS_ROOT=/tmp/sdd-exp/combo  sdd-go-fractals  --coding-agent claude-sonnet
# crisp run 2 (45f0) RESULT: PASS 38m00s coding / 12.1M / $9.51 coding ($10.30 total) — below combo band floor
b523e1al8  C sonnet-controller run 1 (retry; bu26wxubs died on cwd)  combo  sdd-go-fractals  claude-sonnet
# lean run 2 (blxjrns34/ee4d?) RESULT: PASS 43m10s coding / 13.8M / $11.61 coding ($12.57 total) — inside combo band 11.67-14.84
bfo54xv7u  C sonnet-controller run 1 attempt 3 (after 921e9ca seeding fix)  combo  sdd-go-fractals  claude-sonnet
# lean run 3 (bin1o1nx1) RESULT: PASS 48m34s coding / 15.8M / $12.27 coding ($13.41 total) — mid combo band
# crisp run 1 (b4ahv2nnh/f21c) RESULT: PASS 50m46s coding / 16.8M / $12.65 coding ($13.67 total) — inside combo band; crisp n=2 spread 9.51-12.65
bt8kyps5z  B crisp run 3  combo  sdd-go-fractals-crisp  claude
# lean run 1 (bwh4tztdu/e478) RESULT: PASS 50m43s coding / 17.0M / $13.25 coding ($14.72 total). LEAN n=3 COMPLETE: 11.61 / 12.27 / 13.25 (mean 12.38), all inside combo band 11.67-14.84
# combo control (bndlnqu1m/d170, HEAD 9a25a75) RESULT: PASS 59m38s coding / 18.4M / $14.10 coding ($15.51 total) — band top; also validates fe90d6c post-gate rewordings. EXPERIMENT A COMPLETE: lean 11.61/12.27/13.25 vs combo band 11.67-14.84 + tonight 14.10 → cost-neutral within noise; briefs justified by fidelity/durability, not dollars
# svelte n=2 (brk354cby/c47f) RESULT: PASS 69m09s coding / 24.1M / $20.30 coding ($22.36 total; opus $12.35!) — far above svelte n=1 (55.0/19.3M/$14.99). Svelte combo range now 14.99-20.30 vs baseline n=1 20.98 → PR svelte claim must become a range and weaken; check transcript for review loops before recording
# svelte-2 mechanism: 34 dispatches, 34/34 model-explicit (sonnet everywhere, opus only final review) — model line held.
# Cost driver: 9 fix dispatches across 12 tasks (75% fix rate; run 1 had fewer loops) — review-strictness variance, not mechanism failure.
# Deviation noted: no re-review dispatches after fixes (12 reviews total). Possible Minor-severity fixes; judgment-audit candidate.
# C sonnet-controller run 1 (bfo54xv7u) RESULT: PASS 30m58s coding / 12.6M / $6.68 coding ($7.74 total) — HALF the combo band, zero opus (final review also sonnet — judgment-tier note). Judgment audit pending.
b6plroxus  C sonnet-controller run 2  combo  sdd-go-fractals  claude-sonnet
# C1 judgment audit (narrative pass): caught fixer side-effect (go mod tidy removed cobra) and re-fixed BEFORE re-review;
# Minor/Important calibration sane; omnibus final fixer + re-review followed; MERGE_BASE adapted; ledger used.
# Gaps: zero BLOCKED/⚠️ events arose (audit cannot fully clear L2); final review ran sonnet not opus (tier note).
bq0881sxs  D planted-defect run 1  haiku-reviewer clone  claude
bwv0wqvb8  D planted-defect run 2  haiku-reviewer clone  claude
bfmasvanw  D planted-defect run 3  haiku-reviewer clone  claude
# D3 (bfmasvanw/be87) RESULT: PASS — haiku reviewer CAUGHT planted defect (assert-nothing test), fix + haiku re-review loop ran. 11m19s / 2.9M / $2.62
# D3 CORRECTION (gauntlet reasoning): run PASSED but the haiku per-task reviewer RATIONALIZED AWAY BOTH DEFECTS;
# survival came from the opus controller catching the rationalization (1 of 2) + final review flagging DRY as Minor.
# => Score D per-REVIEWER, not per-run verdict. Early L3 disproof signal.
# D 11cf RESULT: INDETERMINATE — haiku per-task reviewer missed BOTH defects; haiku final-branch review caught them. Per-task haiku: 0-for-4 across be87+11cf.
b358beefk  D planted-defect run 4  haiku-reviewer clone  claude
bvqoqxg4f  D planted-defect run 5  haiku-reviewer clone  claude
# D ed05 RESULT: FAIL — haiku reviewer rationalized assert-free test as "plan-compliant" AND praised DRY violation as YAGNI.
# D tally after 3 runs: per-task haiku 0-for-6 on planted defects (pass-by-controller-rescue / indeterminate / fail).
# Pattern: haiku doesn't miss silently — it ADVOCATES for defects (rationalization), worse than absence.
# crisp run 3 (bt8kyps5z/15a0) RESULT: PASS 49m57s / 17.1M / $12.65. B COMPLETE: crisp 9.51/12.65/12.65 (mean 11.60) vs combo band 11.67-14.84.
# B mechanism: crisp dispatches 20/21/24 (7 implementers each) vs combo 28 (10 impl, 13 reviews). Fix waves 5/6/9 vs combo 7 — loops flat.
# B VERDICT: L1 validated in effect (hand-crisped plan, -21% dispatches, ~-$1.5/run mean, gates 3/3). Elicitation via writing-plans = follow-up.
# D 4241 RESULT: PASS-by-adjudication — haiku reviewer FOUND assert-free test but DOWNGRADED to Minor ("brief explicitly
# specifies it") — the exact prohibited rationale; opus controller overrode citing the rubric + escalated plan conflict to human.
# DRY defect: per-task missed, final review flagged Minor/YAGNI.
# D tally after 4 runs / 8 defects: per-task haiku 0 cleanly-flagged-at-severity, 1 found-but-downgraded, 7 missed/rationalized.
# D 6a71 RESULT: FAIL — DRY dismissed by BOTH per-task and final haiku reviewers. D BATTERY COMPLETE: 2 pass / 1 indet / 2 fail (baseline 5/5). L3 DEAD.
bgaa528v0  D haiku-reviewer fractals run  haiku-reviewer clone  sdd-go-fractals  claude
# C2 (b6plroxus/2175) RESULT: PASS 40m46s / 16.1M / $8.05. C n=2: 6.68/8.05 (~-40% vs combo band). 31 dispatches (21 sonnet/10 haiku), 4 per-task Important→fix loops, omnibus final fixer + re-review. Zero BLOCKED/⚠️ in both runs = audit gap stands.
# D fractals (bgaa528v0) RESULT: PASS 39m12s / 14.1M / $9.61 — haiku reviewers save ~$2-3/run; the discount is bought by waving defects through (see battery). L3 stays dead.
# elicited run 2 (boimsf8vd) RESULT: PASS 20m22s / 7.1M / $6.34 coding ($6.96 total) — CHEAPEST fractals run ever; opus controller. Hypothesis: complete-code steps (real writing-plans output) + interfaces ≈ transcription-cost implementation. Hand fixtures (Do/Verify prose) were unrepresentative.
# elicited run 2 mechanism: 16 dispatches (7 impl + 7 rev + final + ONE fix: go.mod version floor), ZERO per-task fix waves, 16/16 model-explicit. Review-loop variance eliminated by complete-code+interfaces plan.
# elicited run 1 (bklppm2d9): PASS 27m59s / 9.8M / $8.49. ELICITED n=2: 6.34/8.49 mean 7.42 — ~-45% vs combo band, opus controller. Control needed: A-control plan (no guidance additions) end-to-end.
# E01 run 1 (a8d4): PASS 19m43s / 5.7M / $5.21 — CHEAPEST EVER. 10 dispatches (3 impl @ 35 turns each — prose-regime per-task effort, but only 3 tasks), 3 fix waves. Task count swamps code completeness at this scale; price = coarser gates.
# E03 run 2 (e7b4): PASS $6.34 / 24.9m / 9.2M. 7/7 impl haiku (30.3 turns avg — inflation real, net positive), reviewers sonnet, 1 fix (haiku committed binary — review caught). CAVEAT: final review drifted to sonnet
# E28 run 1 (6a65): PASS $7.78 / 28.4m — INSIDE with-code range. Impl turns 25.4 (vs 23.7 with bodies, +7%); fix waves 3 vs 1. Tests-as-code carry the spec; bodies marginal.
# E06 run 1 (ca39): PASS $7.15 in-band. CAP BACKFIRED mechanistically: ctrl msgs 92->128/138, output 66k->118-123k, visible thinking 0. Thinking buys turn efficiency.
# E27 gate1 (4ae1): FAIL — sonnet T2 reviewer clean-missed DRY (0 mentions; assert-free test caught as Critical + fix + re-review OK). Report 2620 chars w/ Strengths → terse contract NOT the suppressor. Same final-review-only-DRY shape PASSED in 4241 → gauntlet judge strictness variance contributes. Gate 2 needed.
# E27 fractals run1: PASS $6.60/22m — stack active (haiku impl $0.60, sonnet rev, opus ctrl). Gates pending.
# E24 run 2: PASS $12.40/41.7m/14.9M incl Playwright — below hand-fixture floor (14.99-20.30); prediction band hit
# E27 gates: fail(4ae1, variance+judge)/pass(fbd6)/pass(3047) = 2/3. Fractals run2 pending.
