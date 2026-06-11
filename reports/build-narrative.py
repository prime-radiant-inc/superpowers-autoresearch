#!/usr/bin/env python3
import html
E = []  # (id, title, badge, badgeclass, tested, method, prediction, result, sowhat)
E.append(("E02","Do Interfaces blocks cut implementer exploration?","REFUTED","dead",
 "Whether the per-task Interfaces blocks (exact signatures consumed/produced) reduce how much implementers poke around the codebase before editing.",
 "Mined per-subagent tool-call profiles from completed runs: elicited plans (with Interfaces) vs control plans (without), complete code held constant.",
 "Elicited implementers make fewer pre-edit reads.",
 "No reduction: 1.9 pre-edit explores with Interfaces vs 1.3–1.5 without. But the mining surfaced something bigger — the transcription effect quantified: implementers on complete-code plans run 17–24 turns with 1.3–1.9 explores, vs 36.7 turns and 5.6 explores on prose plans. The plan's code, not its interface annotations, is what keeps implementers on rails.",
 "Interfaces earn their keep elsewhere (fix-wave reduction, cross-task consistency) — not navigation."))
E.append(("E04","Does the controller waste money reading report files?","ALREADY OPTIMAL","neutral",
 "The brief/report file design intends to keep bulk text out of the controller's context. Does the controller defeat it by reading the reports anyway?",
 "Counted controller Read calls touching report files across five runs.",
 "Controller reads report files in under 30% of tasks.",
 "0–1 report-file reads per run across all five runs. The handoff design works exactly as intended.",
 "Lead closed — no saving available."))
E.append(("E07","Is the implementer self-review step worth its turns?","REFUTED (THE GREP LIED)","dead",
 "Implementers self-review before handoff. Does that step catch enough to justify its cost?",
 "Grepped 87 implementer transcripts for self-review findings — then manually read every match, per the methodology rule.",
 "Self-review catches something in >25% of tasks.",
 "The grep claimed 9 catches in 87. Manual inspection killed 8 of them as template echoes in dispatch prompts. True catch rate: 1 in 87 — an unanchored .gitignore entry that would have blocked staging. In the complete-code regime there is almost nothing for self-review to catch.",
 "Kept anyway: one averted fix wave (~$0.75) per ~87 tasks roughly pays for the turns, and catching before review is far cheaper than after. No change."))
E.append(("E08","Can fix subagents run on the cheapest tier?","CONFIRMED AS-IS","win",
 "Post-review fixes are usually mechanical. Do haiku fixers hold up?",
 "Mined every fix dispatch across the whole run corpus: model used, run outcome.",
 "Holds; small saving.",
 "34 haiku fix dispatches across passing runs — controllers already tier fixes down on their own. The one bad incident (a fixer's go mod tidy silently removed cobra) was caught by the existing fix-report contract.",
 "No skill change needed; the behavior already exists and the safety net already works."))
E.append(("E14","Is dispatch cache behavior healthy?","ALREADY OPTIMAL","neutral",
 "If subagent dispatches were cache-missing, reordering could save money.",
 "Mined token-usage records from controller transcripts.",
 "cache_read dwarfs uncached input; no win available.",
 "Cache reads 7.7–30.7M vs only 19–31k uncached input tokens. Cache health is excellent; the cost axis is resident-context size, not hit rate.",
 "Lead closed."))
E.append(("E15","Can reviewers be squeezed further?","ALREADY AT FLOOR","neutral",
 "The reviewer risk budget was tuned earlier. Is there anything left?",
 "Mined reviewer subagent profiles across complete-code runs.",
 "No win available; close the lead.",
 "Reviews run 4.7–5.0 turns / 2.7–3.0 tools everywhere packages exist (prose-plan runs: 10.1 turns / 6.8 tools). The package did the work; the budget binds.",
 "Lead closed."))
E.append(("E18","Does coding-agent verbosity drive QA-agent cost?","REFUTED","dead",
 "If the eval QA agent's cost tracked the coding agent's message volume, terse final messages would cut eval costs too.",
 "Correlated gauntlet token spend against coding-run duration across 30 fractals runs.",
 "QA tokens correlate with coding final-message volume.",
 "QA cost tracks duration (r=0.43) — the QA agent polls the screen. Message volume is irrelevant.",
 "Faster runs cut eval costs automatically; nothing else to do."))
E.append(("E19","Is TodoWrite + ledger double bookkeeping?","PREMISE REFUTED","dead",
 "The skill asks for todos and a progress ledger. Dropping todos might save controller calls.",
 "Counted TodoWrite calls in controller transcripts.",
 "Todos redundant with the ledger for ≤10-task plans.",
 "Zero TodoWrite calls in any measured run — controllers already run ledger-only. Bonus: controller tool calls scale with task count (49 on a 7-task plan vs 74 on a 10-task plan).",
 "No duplication exists to remove."))
E.append(("E20","Is the TDD-evidence block in reports load-bearing?","CONFIRMED","win",
 "Implementer reports carry RED/GREEN test transcripts. Do reviewers actually use them?",
 "Searched 87 reviewer transcripts for references to the TDD evidence.",
 "Reviewers cite it; keep.",
 "41% of reviewer transcripts reference the TDD evidence.",
 "Keep. Removing it would be felt."))
E.append(("E23","Does the controller still re-derive context per dispatch?","FIXED ALREADY","neutral",
 "Before this campaign, real sessions had 42k-char dispatch prompts of pasted history. Did the recipe + briefs actually fix it?",
 "Measured dispatch-prompt sizes across runs.",
 "Measurable but small.",
 "Implementer dispatch prompts now average 2.5k chars on elicited plans (4.6k on prose; 42k in the pathological pre-fix sessions). The remaining mass is the prompt template skeleton itself.",
 "Re-derivation is gone. Any further trim is a template-minification question (E13, backlog)."))
E.append(("E11","Can sonnet write the plans?","DIED ON STRUCTURE","dead",
 "Plan-writing is judgment-dense and pre-registered to stay at opus. How exactly does a cheaper planner fail?",
 "5 sonnet plans from the same design + guidance, scored against opus baselines.",
 "Sonnet plans miss constraints/interfaces fidelity.",
 "Fidelity held perfectly (constraints 5/5, gradient verbatim, interfaces on every task) — mechanical guidance adoption is model-robust. But 4 of 5 plans collapsed to 3 tasks (sonnet mean 3.6 vs opus 5.8): the planner chose coarser review gates. The judgment loss showed up in structure, not in copying.",
 "Plan-writing stays at opus, with sharper evidence for why."))
E.append(("E17","Do plan word-budgets help or hurt?","CONFIRMED HARMFUL","dead",
 "A length target might trim plan flab cheaply.",
 "5 plans with a 1,200-word prose budget (code explicitly exempted) vs 5 baseline.",
 "Test-assertion count falls before prose does.",
 "Severe: test signals fell 53.8 → 20.6 (−62%) and code fences 39 → 14 — even though baseline prose was already under the budget and code was exempted. The model read 'economy' as licence for austerity everywhere, cutting exactly the load-bearing content.",
 "Never add length targets to writing-plans. Same mechanism as the earlier nuance-clause regression."))
E.append(("E21","Can reviewer reports lose their preamble?","WIN −41%","win",
 "Reviewer final messages narrate process before delivering verdicts. A 'your final message IS the report' contract might trim that.",
 "Micro-test on a real brief+report+diff fixture, 5 reps per arm, sonnet. First attempt had a harness flaw (the diff never inlined) — verdict retracted and re-measured clean.",
 "−10–20% reviewer output tokens, verdicts intact.",
 "−41% (1,160 → 687 tokens), spec verdicts 5/5 in both arms. Accidental bonus: the fixture mispaired Task 2's brief with Task 3's diff — and both arms correctly flagged the mismatch. Reviewers genuinely cross-check brief against diff.",
 "Adopted into the E27 stack."))
E.append(("E25","Can reviewers work from the diff package alone?","DANGEROUS — BRIEF IS LOAD-BEARING","dead",
 "Dropping the brief and report from reviewer inputs would simplify dispatches.",
 "Micro-test: same fixture with brief and report removed, 5 reps.",
 "Both needed; close the lead.",
 "Package-only reviewers delivered confident spec verdicts 5/5 — but silently redefined 'spec' to mean just the global constraints. Zero of five flagged that the brief was missing. The confidence survived; the basis didn't.",
 "Keep all three inputs. Same failure family as cheap-reviewer rationalization: silent scope-shrinkage."))
E.append(("E26","Can a recipe shrink controller narration?","WORKS, SMALL","win",
 "46% of controller turns are thinking/narration. Message count is prompt-immune — but per-message length might not be.",
 "Micro-test of a mid-workflow controller moment with tools provided, with and without a one-line-narration recipe; opus, 5 reps each.",
 "Small win or nothing.",
 "162 → 74 narration chars per turn (−54%) with zero variance — and the healthy verify-the-implementer's-claims behavior survived inside the one line. Worth ~$0.1–0.3/run.",
 "A freebie; adopted into the E27 stack."))
E.append(("E01","What do critical-sections-only plans cost to execute?","REFUTED — CONFOUNDED","mixed",
 "Jesse's question: what if plans carry only the critical code instead of everything inline?",
 "Generated critical-only plans (only 1 in 5 genuinely complied — opus resists withholding code), executed the genuine specimen twice.",
 "Between complete-code and prose: $9–12, 3–6 fix waves.",
 "$5.21/$5.11 — the cheapest runs ever measured. But the genuine specimen had also self-merged to 3 tasks: per-implementer effort did double exactly as predicted (35 turns vs 17–24), there were just fewer implementers. Task count swamped code policy; the price is coarser review gates.",
 "Spawned E28 to isolate code policy at constant structure. Also: eliciting this regime at all is hard (1/5 compliance)."))
E.append(("E28","Code policy at constant structure","REFUTED — BODIES ARE MARGINAL","win",
 "The clean version of E01: the same 7-task elicited plan with implementation bodies stripped to one-line descriptions — tests, interfaces, and structure untouched.",
 "Controlled fixture edit (10 bodies stripped, 19 test assertions kept), 2 runs.",
 "Costlier than $6.34–8.49; implementer effort doubles across 7 tasks.",
 "$7.78/$8.54 — inside the with-bodies range. Implementer turns rose only 7%: the test code pins the work; writing code to satisfy given tests is nearly as guided as transcribing. Fix waves ticked up (1 → 3–4).",
 "The plan-content hierarchy, measured: tests + interfaces + structure are load-bearing; implementation bodies are ~40% of plan length for roughly nothing. A defensible writing-plans relaxation."))
E.append(("E03","Haiku implementers under complete-code plans","VIABLE, SMALLER THAN HOPED","mixed",
 "If implementation is transcription, the cheapest tier should manage it — with sonnet reviewers as the quality gate.",
 "Conditional guidance ('when the plan text contains the complete code…'), 2 runs on the elicited plan.",
 "Gates hold; −$2–3/run.",
 "$6.34/$7.33 vs sonnet implementers' $6.34/$8.49 — overlapping; the real saving is ~$0.5–1 because haiku's turn inflation (30 vs 17–24) ate half the price gap. Gates held; one classic haiku sloppiness (committed a build binary) was caught by review. One drift: the final review ran sonnet.",
 "Worth keeping in the stack with the final-review tier pinned; not the big rock."))
E.append(("E22","Does the conditional tier guidance discriminate?","CONFIRMED","win",
 "The E03 wording licenses haiku only when the plan carries complete code. On a prose plan, does the controller correctly refuse?",
 "Same config, prose 10-task fixture, 1 run.",
 "Controller picks sonnet implementers; if it picks haiku anyway, expect a blowup.",
 "9 of 10 implementers went to sonnet — the one haiku was the genuinely mechanical task. $12.59, normal prose band, gates green.",
 "The conditional wording is shippable: it gates on exactly the right condition."))
E.append(("E05","Narrower review-package context (-U3 vs -U10)","NEUTRAL","neutral",
 "Does shrinking diff context push reviewers back into reading files?",
 "review-package patched to -U3, 1 run.",
 "-U3 forces file reads back up; keep -U10.",
 "Reviewer profile byte-identical (5.0 turns / 3.0 tools), cost in-band. On small diffs the width doesn't matter — and the package is read once by sonnet, so there was no spend to recover anyway.",
 "Keep -U10 as large-diff insurance. Lead closed."))
E.append(("E06","Cap the controller's thinking budget","BACKFIRED","dead",
 "Mining showed ~2/3 of controller output tokens are invisible (redacted thinking) — the single biggest controller spend. Cap it?",
 "MAX_THINKING_TOKENS=1024 injected into the launcher (verified in the binary first; careful contamination window), 2 runs.",
 "−15–25% controller cost; judgment must stay clean.",
 "Costs in-band ($7.15/$8.10) but controller messages rose 92 → 128/138 and output tokens nearly doubled (66k → 118–123k). Thinking buys turn efficiency; suppress it and the controller compensates with more steps and re-derivation. Gates held — it isn't harmful, just useless.",
 "Do not cap thinking. The turn floor rises to meet you."))
E.append(("E09","Controller surveys the plan instead of reading it","PARTIAL — HABIT WON","mixed",
 "With briefs delivering tasks, the controller only needs headings + constraints: a task-brief --list mode.",
 "Implemented --list (smoke-tested on real plans), guidance added, 1 run.",
 "−$0.5–1/run of resident context.",
 "The controller ran --list once… then read plan.md twice anyway. Cost in-band, saving unrealized. The read-the-plan habit beat one guidance line.",
 "Dropped for now — the ceiling (~$1) doesn't justify more runs; phrasing iteration is future micro-work."))
E.append(("E24","Fixture realism at svelte scale","CONFIRMED −24%","win",
 "Fractals showed hand-written fixture plans execute ~2× costlier than real skill output. Does it replicate on the bigger scenario?",
 "Generated an elicited svelte plan — discovering first that the hand fixture had gold-plated an E2E suite the design never asked for; amended the design so scopes match. 2 runs incl. Playwright.",
 "$10–13 vs the hand fixture's $14.99–20.30.",
 "$12.40/$14.38 (mean $13.39) vs ~$17.6 — a −24% replication, milder than fractals' 2× because heavier intrinsic UI/E2E work dilutes plan effects.",
 "Fixture-realism finding stands across scales. Also: baseline svelte numbers always included unrequested scope."))
E.append(("E27","The integrated ship candidate","CANDIDATE ESTABLISHED","win",
 "Do the loop's wins compose? Opus controller + elicited plan + conditional haiku implementers + terse reviewer contract + narration recipe + final-review tier pin.",
 "Stack clone, 2 fractals runs + 3 planted-defect quality gates.",
 "All green; fractals ≤ $6.",
 "Fractals $6.24/$6.60 (combo on hand plans: $11.67–14.84). Quality gates 2 of 3 — the one fail was a clean reviewer miss on DRY plus a stricter judge reading; inspecting the reviewer's 2,620-char report exonerated the terse contract as the suppressor.",
 "The candidate exists and costs half the shipped config. The N=5 gate battery is still owed before any of it becomes skill text."))

BACKLOG = [("E10","Report contract 15→8 lines"),("E12","Coarser step granularity"),("E13","Prompt-template minification"),("E16","Best-stack composition on svelte")]

BCLASS={"win":"#14532d/#86efac","dead":"#7f1d1d/#fca5a5","neutral":"#374151/#d1d5db","mixed":"#713f12/#fcd34d"}
parts=["""<!doctype html><html><head><meta charset="utf-8"><title>Build-Loop Autoresearch — 25 Experiments</title><style>
body{background:#0f172a;color:#e2e8f0;font:15px/1.6 -apple-system,system-ui,sans-serif;margin:0;padding:36px auto;max-width:860px;margin:auto;padding:36px 24px}
h1{font-size:24px;margin:0 0 6px} .sub{color:#94a3b8;margin-bottom:8px;font-size:14px}
.intro{color:#cbd5e1;font-size:14px;border-left:3px solid #7dd3fc;padding:10px 16px;background:#1e293b;border-radius:6px;margin:18px 0 30px}
.exp{margin:0 0 30px;background:#1e293b;border-radius:12px;padding:20px 24px}
.exp h2{font-size:17px;margin:0 0 2px;color:#f1f5f9} .eid{color:#7dd3fc;font-weight:700;margin-right:8px}
.badge{display:inline-block;padding:2px 11px;border-radius:10px;font-size:11.5px;font-weight:700;letter-spacing:.03em;vertical-align:2px;margin-left:10px}
dt{color:#7dd3fc;font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-top:12px}
dd{margin:3px 0 0;color:#d8e0ea} .pred dd{color:#94a3b8;font-style:italic}
h3{color:#7dd3fc;font-size:14px;text-transform:uppercase;letter-spacing:.08em;margin:40px 0 12px}
.backlog{color:#94a3b8;font-size:14px}
</style></head><body>
<h1>Build-Loop Autoresearch — the 25 Experiments</h1>
<div class="sub">2026-06-11 · opus as coordinator throughout · every hypothesis pre-registered with a prediction · ~$165</div>
<div class="intro">Method: mine existing run artifacts first (free), micro-test phrasings with controls next (~$1–5), spend full eval runs only where the cheaper tiers couldn't answer (~$7–15 each). Every automated score got a manual inspection pass — which caught and corrected three measurement bugs mid-loop (a grep counting template echoes as findings, a harness that never inlined the diff it claimed to test, a scorer regex blind across newlines). One retracted verdict was re-measured clean. Quality gates (planted-defect scenario) guard every config change; negative results get equal billing.</div>
"""]
SECTIONS=[("Mining the corpus — ten experiments from runs we already had",["E02","E04","E07","E08","E14","E15","E18","E19","E20","E23"]),
          ("Micro-tests — phrasings against controls, dollars at a time",["E11","E17","E21","E25","E26"]),
          ("Full runs — where only real execution answers",["E01","E28","E03","E22","E05","E06","E09","E24"]),
          ("The composition",["E27"])]
by={e[0]:e for e in E}
for sect, ids in SECTIONS:
    parts.append(f"<h3>{html.escape(sect)}</h3>")
    for i in ids:
        eid,title,badge,bc,tested,method,pred,result,sowhat=by[i]
        bg,fg=BCLASS[bc].split('/')
        parts.append(f"""<div class="exp"><h2><span class="eid">{eid}</span>{html.escape(title)}<span class="badge" style="background:{bg};color:{fg}">{html.escape(badge)}</span></h2>
<dl>
<dt>What it tested</dt><dd>{html.escape(tested)}</dd>
<dt>How</dt><dd>{html.escape(method)}</dd>
<div class="pred"><dt>Pre-registered prediction</dt><dd>{html.escape(pred)}</dd></div>
<dt>What happened</dt><dd>{html.escape(result)}</dd>
<dt>So what</dt><dd>{html.escape(sowhat)}</dd>
</dl></div>""")
parts.append("<h3>Backlog — registered, not run (the 25 minimum was reached without them)</h3><p class='backlog'>"+" · ".join(f"<b>{i}</b> {html.escape(t)}" for i,t in BACKLOG)+"</p>")
parts.append("""<div class="intro" style="margin-top:30px"><b>Where it nets out:</b> the ship-candidate stack runs go-fractals at $6.24–6.60 against the shipped config's $11.67–14.84 — but most of that gap belongs to executing real, complete plans rather than the hand-written prose fixtures all earlier numbers were measured on. The durable lessons: tests+interfaces+structure are what make a plan cheap to execute; thinking is load-bearing, don't cap it; word budgets eat tests; cheap models fail by advocating, not by going quiet; and half of all leads close as "the current design already had this right" — which is exactly what the log is for.</div>
</body></html>""")
open('/tmp/sdd-exp/autoresearch/experiments-narrative.html','w').write('\n'.join(parts))
print('written')
