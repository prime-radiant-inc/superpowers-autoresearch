"""Tests for score_x1_chains.py (X1, Task 2 of the cost-pathologies SDD
plan). Two layers:

  - Pure-function tests (_stem, _extract_findings, _classify_severity_trend)
    against plain synthetic strings -- no fixture files, no real session
    content, exercises the text-parsing edge cases directly.
  - One integration test (chain_stats over fixtures/x1/) exercising the
    full spawn-grouping/resolution/aggregation wiring.

Fixture layout (fixtures/x1/), all synthetic, modeling the two-tier
`_chain_key()` grouping validated against a real mined session (see
score_x1_chains.py's module docstring):
  - parent.jsonl -- five spawn_agent calls, chronologically: call_IMPL
    (task1_implementer, fork_turns="none") -> thread-implimplimpl (the
    presumed implementer -- first in time under the "task1" prefix, must
    never appear as a round), call_R1 (task1_reviewer_r1, fork_turns=
    "none") -> thread-r1r1r1r1, call_R2 (task1_reviewer_r2, fork_turns=
    "all") -> thread-r2r2r2r2, call_R3 (task1_reviewer_r3, fork_turns=
    "none") -- deliberately has NO sub_agent_activity link (an
    unresolvable round, modeling either a still-pending dispatch or a
    corpus slice missing that child rollout), and call_AUTH
    (auth_path_review, fork_turns="none") -> thread-authauthauth -- does
    NOT start "task<N>", exercises tier 2 (stem-grouped, no numbered-task
    prefix) as its own one-entry chain.
  - rollout-thread-r1r1r1r1.jsonl -- round 1: cumulative token_count
    total=5000 (LAST event, not summed); final_answer using the real
    task-reviewer-prompt.md heading format (`#### Critical (Must Fix)`)
    with one Critical finding.
  - rollout-thread-r2r2r2r2.jsonl -- round 2: cumulative token_count
    total=9000; final_answer using the real re-review-prompt.md inline
    format (`### New Breakage in the Fix Diff` + an inline `(Important)`
    tag) with one Important finding, textually distinct from round 1's.
  - rollout-thread-authauthauth.jsonl -- the tier-2 chain's sole round:
    cumulative token_count total=1200; final_answer with one Minor
    finding (heading format).

Item 12's retask fixtures (retask_parent.jsonl +
rollout-thread-retaskretaskretask.jsonl) are a SEPARATE, self-contained
fixture pair (own FIXTURES-relative paths, never mixed into ALL_PATHS)
so they can't perturb the five-spawn scenario above. They construct the
fourth chain pattern -- a single review-shaped thread re-tasked in place
rather than fresh-spawned per round -- modeled directly on the one real
corpus exemplar found while building this fix (`durability_fix2_reviewer`
in `cp-x1-buggy-sdd-x1a-rep1`, cited in score_x1_chains.py's module
docstring and `_retask_envelope_count()`'s docstring): ONE spawn_agent
call (`config_review`, fork_turns="none") whose single resolved child
rollout carries TWO NEW_TASK envelopes addressed to itself (the initial
dispatch, then a re-task after the first verdict) and TWO
`phase=="final_answer"` entries -- round 1 cumulative tokens=4000 (one
Critical finding), round 2 cumulative tokens=7000 at its own final-answer
timestamp, climbing to a file-final 7500 after a bit of post-final-answer
wrap-up activity (one distinct Important finding) -- invisible to the
pre-fix scorer, which would have kept only round 2's finding and reported
`rounds=1`.
"""
import os
import unittest

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "x1")
PARENT = os.path.join(FIXTURES, "parent.jsonl")
CHILD_R1 = os.path.join(FIXTURES, "rollout-thread-r1r1r1r1.jsonl")
CHILD_R2 = os.path.join(FIXTURES, "rollout-thread-r2r2r2r2.jsonl")
CHILD_AUTH = os.path.join(FIXTURES, "rollout-thread-authauthauth.jsonl")
ALL_PATHS = [PARENT, CHILD_R1, CHILD_R2, CHILD_AUTH]

RETASK_PARENT = os.path.join(FIXTURES, "retask_parent.jsonl")
RETASK_CHILD = os.path.join(FIXTURES, "rollout-thread-retaskretaskretask.jsonl")
RETASK_PATHS = [RETASK_PARENT, RETASK_CHILD]


class TestStem(unittest.TestCase):
    def test_strips_r_suffix(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._stem("task1_reviewer_r1"), "task1_reviewer")
        self.assertEqual(sx1._stem("task1_reviewer_r2"), "task1_reviewer")

    def test_strips_round_suffix(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._stem("task4_spec_round2"), "task4_spec")

    def test_bare_trailing_digit_without_delimiter_not_a_reliable_split_left_alone(self):
        # No underscore/hyphen before the trailing digit -- a genuine word
        # boundary the stripper can't safely guess at, so it's left as-is
        # (documented limitation: "reviewer2" style suffixes won't group).
        import score_x1_chains as sx1
        self.assertEqual(sx1._stem("task1reviewer2"), "task1reviewer2")

    def test_no_suffix_unchanged(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._stem("fp_task7_review"), "fp_task7_review")


class TestExtractFindings(unittest.TestCase):
    def test_heading_based_findings(self):
        import score_x1_chains as sx1
        text = (
            "### Issues\n\n"
            "#### Critical (Must Fix)\n"
            "- **Off-by-one in loop bound** — file.py:10\n\n"
            "#### Important (Should Fix)\n"
            "- **Missing null check** — file.py:20\n\n"
            "#### Minor (Nice to Have)\n"
            "- **Inconsistent naming** — file.py:30\n"
        )
        findings = sx1._extract_findings(text)
        severities = [s for s, _ in findings]
        self.assertEqual(severities, ["Critical", "Important", "Minor"])

    def test_inline_severity_in_new_breakage_section(self):
        import score_x1_chains as sx1
        text = (
            "### New Breakage in the Fix Diff\n\n"
            "- **Race condition on shared cache** (Important) — file.py:55\n"
        )
        findings = sx1._extract_findings(text)
        self.assertEqual(findings, [("Important", "race condition on shared cache (important) — file.py:55")])

    def test_finding_verdicts_section_never_counted(self):
        # ADDRESSED/NOT ADDRESSED bullets carry no severity word -- must
        # not be counted as findings (they're re-verifications, not new
        # findings; see module docstring).
        import score_x1_chains as sx1
        text = (
            "### Finding Verdicts\n\n"
            "- **Off-by-one in loop bound** — ADDRESSED, file.py:10 fixed\n"
            "- **Missing null check** — NOT ADDRESSED, file.py:20 still missing\n"
        )
        self.assertEqual(sx1._extract_findings(text), [])

    def test_heading_state_resets_on_unrelated_heading(self):
        # A non-severity heading (e.g. "### Strengths") must not let a
        # prior section's severity leak into bullets under it.
        import score_x1_chains as sx1
        text = (
            "#### Critical (Must Fix)\n"
            "- **A real bug** — file.py:1\n\n"
            "### Strengths\n"
            "- Good test coverage\n"
        )
        findings = sx1._extract_findings(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][0], "Critical")

    def test_no_findings_on_prose_only_text(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._extract_findings("Looks good, no issues found."), [])

    def test_bare_label_format_with_none_excludes_zero_findings(self):
        # A real corpus format found during Task 2's corpus validation
        # (2026-07-26 task6 chain, see logs/2026-07-31-cost-pathologies.md):
        # neither the task-reviewer-prompt.md heading format nor
        # re-review-prompt.md's inline-tag format -- a compact one-line
        # "Severity: <verdict-or-none>" summary instead.
        import score_x1_chains as sx1
        text = "Critical: none. Important: none. Minor: none."
        self.assertEqual(sx1._extract_findings(text), [])

    def test_bare_label_format_with_content_is_one_finding(self):
        import score_x1_chains as sx1
        text = "Critical: none. Minor: an unused import lingers in utils.py."
        findings = sx1._extract_findings(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][0], "Minor")
        self.assertIn("unused import", findings[0][1])

    # -- Item 11: NONE_VALUE_RE prose-none variants (corpus-derived) --
    # Both positive cases below are the ONLY two real "none"-prefixed,
    # non-exact bare-label values found across the full 16-rep-dir X1 FULL
    # corpus (evals-lane-b/results/cp-x1-buggy-sdd-* +
    # superpowers/evals/results/cp-x1-buggy-sdd-*) -- a minimal real pair:
    # one that must become zero findings, one that (despite also starting
    # "none") must NOT.

    def test_bare_label_none_identified_beyond_excludes_zero_findings(self):
        # Verbatim line from cp-x1-buggy-sdd-x1a-rep1's final reviewer
        # round (rollout-2026-08-01T04-22-18-...019fbb8e...jsonl): the
        # exact "none identified beyond the [already-counted] X" phrasing
        # named in this task's brief. Before the fix, NONE_VALUE_RE's
        # `^none\.?$` didn't match this value, so it was wrongly counted
        # as a real Critical finding.
        import score_x1_chains as sx1
        text = "- Critical: none identified beyond the unresolved original durability finding."
        self.assertEqual(sx1._extract_findings(text), [])

    def test_bare_label_none_beyond_excludes_zero_findings(self):
        # "none beyond X" -- the brief's other named prose variant.
        # Adapted from a real corpus line (cp-x1-buggy-sdd-x1c-rep1,
        # "None beyond the critical durability defect.") into bare-label
        # form to exercise NONE_VALUE_RE directly; the original appeared
        # as a plain list item, not a "Severity: <value>" line.
        import score_x1_chains as sx1
        text = "Critical: none beyond the critical durability defect."
        self.assertEqual(sx1._extract_findings(text), [])

    def test_bare_label_no_new_findings_excludes_zero_findings(self):
        # "no new findings" -- the third prose variant named verbatim in
        # this task's brief (not found verbatim in the archived corpus,
        # unlike the two cases above; included because the brief names it
        # explicitly as required NONE_VALUE_RE coverage).
        import score_x1_chains as sx1
        text = "Important: no new findings."
        self.assertEqual(sx1._extract_findings(text), [])

    def test_bare_label_none_blocking_is_a_real_finding_not_swallowed(self):
        # Verbatim line from cp-x1-buggy-sdd-x1c-rep3's reviewer round
        # (rollout-2026-08-01T08-40-48-...019fbc7b...jsonl): starts with
        # "None" but is a REAL minor suggestion ("not blocking, but
        # consider adding X"), not a zero-findings report. The broadened
        # NONE_VALUE_RE must NOT match this -- the exact boundary case
        # motivating the "at least two negative cases" requirement.
        import score_x1_chains as sx1
        text = (
            "- Minor: None blocking. A direct unit test that `reload_plans` "
            "removes stale IDs would strengthen catalog API coverage, though "
            "the implementation clearly performs replacement rather than "
            "update (`billing/plan_catalog.py:27`)."
        )
        findings = sx1._extract_findings(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][0], "Minor")
        self.assertIn("none blocking", findings[0][1])
        self.assertIn("reload_plans", findings[0][1])

    def test_bare_label_real_minor_finding_unrelated_to_none_not_swallowed(self):
        # Verbatim line from cp-x1-buggy-sdd-x1b-rep4's reviewer round
        # (rollout for the x1b-rep4 review chain): an ordinary real
        # finding with no "none" prefix at all -- a plain regression guard
        # that the broadened regex hasn't become so permissive it eats
        # unrelated bare-label content.
        import score_x1_chains as sx1
        text = (
            "- Minor: report’s historical pytest/TDD and whitespace-check "
            "results cannot be independently verified from the supplied diff "
            "alone; implementation claims themselves are substantiated."
        )
        findings = sx1._extract_findings(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][0], "Minor")
        self.assertIn("cannot be independently verified", findings[0][1])


class TestClassifySeverityTrend(unittest.TestCase):
    def test_insufficient_data_below_two_rounds(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._classify_severity_trend([]), "insufficient_data")
        self.assertEqual(sx1._classify_severity_trend([3]), "insufficient_data")

    def test_no_findings_all_zero(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._classify_severity_trend([0, 0, 0]), "no_findings")

    def test_decreasing(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._classify_severity_trend([3, 2, 0]), "decreasing")

    def test_increasing(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._classify_severity_trend([1, 3]), "increasing")

    def test_flat(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._classify_severity_trend([2, 2, 2]), "flat")

    def test_mixed(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._classify_severity_trend([1, 3, 2]), "mixed")


class TestChainStats(unittest.TestCase):
    def test_two_chains_found_implementer_excluded(self):
        # Tier 1 ("task1", implementer excluded) + tier 2
        # ("auth_path_review", standalone) -- task1_implementer itself
        # never surfaces as its own chain under either tier.
        import score_x1_chains as sx1
        result = sx1.chain_stats(ALL_PATHS)
        root_ids = {c["root_id"] for c in result["chains"]}
        self.assertEqual(root_ids, {"parent.jsonl:task1", "parent.jsonl:auth_path_review"})

    def _task1_chain(self, result):
        return next(c for c in result["chains"] if c["root_id"] == "parent.jsonl:task1")

    def test_dispatch_count_exceeds_rounds_when_a_round_is_unresolvable(self):
        import score_x1_chains as sx1
        chain = self._task1_chain(sx1.chain_stats(ALL_PATHS))
        self.assertEqual(chain["dispatch_count"], 3)  # r1, r2, r3 (implementer excluded)
        self.assertEqual(chain["rounds"], 2)           # r3 never resolved

    def test_novel_finding_rate_per_round(self):
        import score_x1_chains as sx1
        chain = self._task1_chain(sx1.chain_stats(ALL_PATHS))
        self.assertEqual(chain["novel_finding_rate_per_round"], [1.0, 1.0])

    def test_severity_trend_decreasing_critical_to_important(self):
        import score_x1_chains as sx1
        chain = self._task1_chain(sx1.chain_stats(ALL_PATHS))
        self.assertEqual(chain["severity_trend"], "decreasing")

    def test_tokens_est_uses_max_when_any_round_inherited_history(self):
        # round1 fork_turns=none (5000 cumulative), round2 fork_turns=all
        # (9000 cumulative, which already re-embeds round1's own history
        # per X4's finding) -- summing would double-count, so tokens_est
        # must be the max (9000), not the sum (14000).
        import score_x1_chains as sx1
        chain = self._task1_chain(sx1.chain_stats(ALL_PATHS))
        self.assertEqual(chain["tokens_est"], 9000)

    def test_tier2_standalone_review_chain(self):
        import score_x1_chains as sx1
        result = sx1.chain_stats(ALL_PATHS)
        chain = next(c for c in result["chains"] if c["root_id"] == "parent.jsonl:auth_path_review")
        self.assertEqual(chain["dispatch_count"], 1)
        self.assertEqual(chain["rounds"], 1)
        self.assertEqual(chain["novel_finding_rate_per_round"], [1.0])
        self.assertEqual(chain["severity_trend"], "insufficient_data")
        self.assertEqual(chain["tokens_est"], 1200)

    def test_no_rollouts_returns_empty_chains(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1.chain_stats([]), {"chains": []})


class TestRetaskEnvelopeCount(unittest.TestCase):
    def test_zero_on_a_child_with_no_inter_agent_messages(self):
        # Regression guard: none of the pre-existing fixture children
        # (CHILD_R1/R2/AUTH) carry any response_item/agent_message
        # records at all -- confirms item 12's detector adds zero new
        # signal on ordinary, non-retasked chains.
        import score_x1_chains as sx1
        self.assertEqual(sx1._retask_envelope_count(CHILD_R1), 0)

    def test_two_on_the_constructed_retask_fixture(self):
        import score_x1_chains as sx1
        self.assertEqual(sx1._retask_envelope_count(RETASK_CHILD), 2)


class TestChainStatsRetask(unittest.TestCase):
    # Item 12: a single review-shaped thread re-tasked in place (NEW_TASK
    # envelopes to itself, no fresh spawn_agent) must surface as TWO
    # resolved rounds, not one -- see RETASK_PATHS' fixture docstring
    # above for the exact scenario these assert against.

    def test_two_rounds_resolved_from_one_spawn(self):
        import score_x1_chains as sx1
        result = sx1.chain_stats(RETASK_PATHS)
        self.assertEqual(len(result["chains"]), 1)
        chain = result["chains"][0]
        self.assertEqual(chain["root_id"], "retask_parent.jsonl:config_review")
        self.assertEqual(chain["rounds"], 2)

    def test_dispatch_count_bumped_by_the_extra_round(self):
        # One spawn_agent call, but the fourth pattern found a second real
        # round inside it -- dispatch_count must reflect that (and must
        # keep rounds <= dispatch_count holding), not stay pinned at 1.
        import score_x1_chains as sx1
        chain = sx1.chain_stats(RETASK_PATHS)["chains"][0]
        self.assertEqual(chain["dispatch_count"], 2)

    def test_both_rounds_findings_present_not_just_the_last(self):
        # The pre-fix behavior would keep ONLY round 2's Important finding
        # and silently discard round 1's Critical one.
        import score_x1_chains as sx1
        chain = sx1.chain_stats(RETASK_PATHS)["chains"][0]
        self.assertEqual(chain["novel_finding_rate_per_round"], [1.0, 1.0])

    def test_severity_trend_uses_both_rounds(self):
        # Critical (round 1) -> Important (round 2) is a real decreasing
        # trend, visible only once both rounds are resolved separately;
        # pre-fix this collapsed to "insufficient_data" (a single round).
        import score_x1_chains as sx1
        chain = sx1.chain_stats(RETASK_PATHS)["chains"][0]
        self.assertEqual(chain["severity_trend"], "decreasing")

    def test_tokens_est_uses_max_not_sum_across_retasked_rounds(self):
        # Round 1's cumulative reading (4000) and round 2's share ONE
        # continuous counter -- summing would double-count round 1's
        # spend into the total. tokens_est must be the thread's real file-
        # final total (7500, after a bit of post-final-answer wrap-up
        # activity), not 4000+7000=11000 -- and not 7000 either (round 2's
        # OWN final-answer-timestamp reading, which would under-credit
        # that trailing wrap-up; only NON-last rounds are bounded to their
        # own timestamp, see resolve_chains()'s retask branch).
        import score_x1_chains as sx1
        chain = sx1.chain_stats(RETASK_PATHS)["chains"][0]
        self.assertEqual(chain["tokens_est"], 7500)


if __name__ == "__main__":
    unittest.main()
