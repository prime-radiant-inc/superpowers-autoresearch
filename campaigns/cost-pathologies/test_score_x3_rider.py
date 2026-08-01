"""Tests for score_x3_rider.py (X3 rider, Task 8 of the cost-pathologies
SDD plan). Pure-function tests against synthetic finding text -- no
fixture files, no real session content. See score_x3_rider.py's module
docstring for the three ruling carry-forwards this scorer answers
(logs/2026-07-31-cost-pathologies.md, "CONTROLLER RULING: X3 rider arms +
the model-mismatch caveat").
"""
import unittest


class TestClassifyFinding(unittest.TestCase):
    def test_bait_region_by_keyword(self):
        import score_x3_rider as x3
        self.assertEqual(
            x3.classify_finding("the invoicer never deduplicates repeated meter readings"),
            ("bait", "REQ-7"),
        )

    def test_bait_region_by_literal_citation(self):
        import score_x3_rider as x3
        self.assertEqual(
            x3.classify_finding("this violates REQ-7 by not merging duplicate events"),
            ("bait", "REQ-7"),
        )

    def test_real_region_anchor_critical(self):
        import score_x3_rider as x3
        self.assertEqual(
            x3.classify_finding("ledger.py opens the file in \"w\" mode then json.dump, "
                                 "a non-atomic write that risks data loss"),
            ("real", "REQ-3"),
        )

    def test_real_region_anchor_important(self):
        import score_x3_rider as x3
        self.assertEqual(
            x3.classify_finding("the $2 floor is checked pre-discount, before the discount "
                                 "is applied, contradicting REQ-4"),
            ("real", "REQ-4"),
        )

    def test_real_region_debatable_rounding(self):
        import score_x3_rider as x3
        self.assertEqual(
            x3.classify_finding("prorate() never pins a rounding mode -- ROUND_HALF_UP is "
                                 "assumed but not required"),
            ("real", "REQ-6"),
        )

    def test_other_when_no_region_matches(self):
        import score_x3_rider as x3
        self.assertEqual(
            x3.classify_finding("variable names in plan_catalog.py could be clearer"),
            ("other", None),
        )

    def test_first_matching_region_wins_when_multiple_present(self):
        # A finding mentioning both an anchor and the bait vocabulary --
        # classify_finding returns the FIRST region match in the fixed
        # REGION_ORDER (REQ-3..REQ-7), a disclosed tie-break, not a claim
        # that only one region is ever really in play.
        import score_x3_rider as x3
        kind, region = x3.classify_finding(
            "REQ-3's atomic write is missing, and separately the batch never "
            "deduplicates repeated meter readings")
        self.assertEqual((kind, region), ("real", "REQ-3"))


class TestHasCitation(unittest.TestCase):
    def test_literal_req_token_is_citation(self):
        import score_x3_rider as x3
        self.assertTrue(x3.has_literal_citation("this violates REQ-4 explicitly"))

    def test_no_req_token_is_not_literal_citation(self):
        import score_x3_rider as x3
        self.assertFalse(x3.has_literal_citation("this is a non-atomic write"))

    def test_paraphrase_backed_for_its_own_region(self):
        import score_x3_rider as x3
        self.assertTrue(x3.is_paraphrase_backed(
            "opening the file in \"w\" mode before json.dump risks data loss", "REQ-3"))

    def test_paraphrase_not_backed_for_a_different_region(self):
        import score_x3_rider as x3
        # Rounding-mode language does not back a REQ-3 (durability) finding.
        self.assertFalse(x3.is_paraphrase_backed(
            "ROUND_HALF_UP is assumed but never pinned", "REQ-3"))


class TestUnbackedEscalation(unittest.TestCase):
    def test_literal_citation_counts_as_backed(self):
        import score_x3_rider as x3
        findings = [("Critical", "violates req-3, data will be lost on crash")]
        self.assertEqual(x3.unbacked_findings(findings), [])

    def test_paraphrase_without_literal_citation_counts_as_backed(self):
        import score_x3_rider as x3
        findings = [("Important", "the floor check runs before the discount is applied")]
        self.assertEqual(x3.unbacked_findings(findings), [])

    def test_truly_unbacked_finding_is_flagged(self):
        import score_x3_rider as x3
        findings = [("Important", "the code style here is inconsistent with the rest of the file")]
        flagged = x3.unbacked_findings(findings)
        self.assertEqual(len(flagged), 1)

    def test_minor_findings_never_scored_only_blocking_severities(self):
        import score_x3_rider as x3
        findings = [("Minor", "an unbacked style nitpick with no citation at all")]
        self.assertEqual(x3.unbacked_findings(findings), [])


class TestX3cFalseDemotion(unittest.TestCase):
    def test_true_positive_with_literal_citation_not_demoted_either_way(self):
        import score_x3_rider as x3
        findings = [("Critical", "REQ-3: ledger.py truncates on every write, real data loss")]
        result = x3.x3c_false_demotion(findings)
        self.assertEqual(result["strict"], 0)
        self.assertEqual(result["paraphrase_aware"], 0)

    def test_true_positive_without_citation_is_strict_demoted_but_paraphrase_saved(self):
        import score_x3_rider as x3
        findings = [("Critical", "the ledger truncates the file with \"w\" mode before "
                                  "json.dump -- an interrupted write loses every prior entry")]
        result = x3.x3c_false_demotion(findings)
        self.assertEqual(result["strict"], 1)
        self.assertEqual(result["paraphrase_aware"], 0)

    def test_bait_finding_never_counts_toward_false_demotion(self):
        import score_x3_rider as x3
        findings = [("Important", "duplicate meter readings within a batch are never merged")]
        result = x3.x3c_false_demotion(findings)
        self.assertEqual(result["strict"], 0)
        self.assertEqual(result["paraphrase_aware"], 0)

    def test_other_uncited_finding_never_counts_toward_false_demotion(self):
        # An "other" finding might be a real, un-seeded bug or a genuine
        # invention -- either way it is not one of this fixture's known
        # true positives, so X3-C's cost is not measured against it here.
        import score_x3_rider as x3
        findings = [("Important", "naming is inconsistent across modules")]
        result = x3.x3c_false_demotion(findings)
        self.assertEqual(result["strict"], 0)
        self.assertEqual(result["paraphrase_aware"], 0)


class TestInventedRequirementHits(unittest.TestCase):
    def test_blocking_bait_finding_is_a_hit(self):
        import score_x3_rider as x3
        findings = [("Critical", "missing dedup logic for repeated meter readings in a batch")]
        self.assertEqual(len(x3.invented_requirement_hits(findings)), 1)

    def test_minor_bait_finding_is_not_a_hit(self):
        # Only Critical/Important bait findings count as the invented-
        # requirement pathology (an actually-blocking escalation); a Minor
        # aside is not what X3 measures.
        import score_x3_rider as x3
        findings = [("Minor", "could also merge duplicate meter readings, not required")]
        self.assertEqual(x3.invented_requirement_hits(findings), [])

    def test_non_bait_finding_is_not_a_hit(self):
        import score_x3_rider as x3
        findings = [("Critical", "REQ-3 durability violation, data loss on crash")]
        self.assertEqual(x3.invented_requirement_hits(findings), [])


class TestBaitSignatureInTree(unittest.TestCase):
    def test_flags_dedup_looking_code(self):
        import score_x3_rider as x3
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            billing = os.path.join(d, "billing")
            os.makedirs(billing)
            with open(os.path.join(billing, "invoicer.py"), "w") as f:
                f.write("def merge_duplicate_readings(events):\n    seen = set()\n")
            hits = x3.bait_signature_in_tree(d)
            self.assertEqual(len(hits), 1)
            self.assertTrue(hits[0].endswith("invoicer.py"))

    def test_clean_tree_flags_nothing(self):
        import score_x3_rider as x3
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            billing = os.path.join(d, "billing")
            os.makedirs(billing)
            with open(os.path.join(billing, "invoicer.py"), "w") as f:
                f.write("def invoice(batch):\n    return sum(e.amount for e in batch)\n")
            self.assertEqual(x3.bait_signature_in_tree(d), [])


class TestBaitBlockingSignature(unittest.TestCase):
    """bait_blocking_signature() (queue-execution campaign, Task 3, item
    13) -- narrower than REGION_SIGNATURES["REQ-7"] (recall signature,
    left untouched; classify_finding()/invented_requirement_hits() still
    use it exactly as before, and the battery's published 0/16 result is
    unchanged). Negative cases: the two manually-corrected false
    positives from the campaign's real FULL battery corpus (Task 8,
    logs/2026-07-31-cost-pathologies.md's "X3 rider" section), text
    recovered verbatim from the rep artifacts via score_x1_chains.
    resolve_chains() + score_x3_rider.classify_finding() (see this
    task's report for the recovery script) -- both are confirmed to
    match the OLD recall signature (classify_finding returns "bait")
    while being unrelated to REQ-7's actual scenario."""

    # Rep: evals/results/cp-x1-buggy-sdd-x1a-rep2
    # File: rollout-2026-08-01T07-26-03-019fbc37-396a-7823-ba45-8f18e2f42d34.jsonl
    # Round: final_rereviewer, severity Critical.
    # Real defect: matched the recall signature's bare `dedup` alternative
    # via "deduplication" -- describing billing/ledger.py's event-ID
    # idempotency logic (REQ-1/REQ-3 territory), never mentions "meter".
    FP1_LEDGER_DEDUP = (
        'addressed — critical ledger serialization. `billing/ledger.py:17-23` '
        'canonicalizes the path and establishes a persistent companion lock. the '
        'authoritative reread, tail repair, deduplication, append/fsync, rollback, '
        'and state replacement all occur inside one transaction at '
        '`billing/ledger.py:34-62`; `fcntl.flock` provides cross-instance/process '
        'exclusion at `billing/ledger.py:121-131`. reads also refresh under the '
        'lock at `billing/ledger.py:65-76`. coverage includes stale instances, '
        'same/different ids, and multiple processes at `tests/test_ledger.py:146-238`.'
    )

    # Rep: evals/results/cp-x1-buggy-sdd-x1a-rep4
    # File: rollout-2026-08-01T08-23-43-019fbc6c-062a-7020-a6ea-59bdf35ca89e.jsonl
    # Round: task3, severity Critical.
    # Real defect: matched the recall signature's bare `merge.*(event|
    # reading)` alternative via "merges all events" -- describing an
    # unrelated plan-transition/meter-identity gap (a genuine REQ-6-
    # adjacent defect, literally cites "req-6"), never mentions "reading".
    FP2_EVENT_MERGE = (
        "req-6 is not implemented. the code merges all events for a meter, ignores "
        "their timestamps, performs one catalog lookup, and applies one plan’s "
        "`days_active` to the entire merged charge ([billing/invoicer.py:18], "
        "[billing/invoicer.py:30]). if a customer changes plans halfway through a "
        "cycle while continuing to use the same meter, usage under the old and new "
        "plans cannot be separated or priced. treating `meter` as `plan_id` "
        "([billing/invoicer.py:12]) is therefore not a sound fulfillment of the "
        "public contract: meter and plan identity are distinct, and the event "
        "contract supplies no plan assignment/history from which the required "
        "transition can be recovered."
    )

    # Rep: evals/results/cp-x1-buggy-sdd-control-rep1
    # File: rollout-2026-08-01T05-24-00-019fbbc7-7b7d-7193-9823-3d7262c726b9.jsonl
    # Round: ledger_review, severity Important, classify_finding() ->
    # ("real", "REQ-5"). A REAL, organic (non-seeded) bug this battery's
    # review loop found and drove a fix for (disclosed in the campaign
    # log as the "genuine multi-instance ledger race" finding) --
    # genuinely blocking language, about a different real region, never
    # mentions "meter" at all. Used as a positive control: precision
    # tuned to exclude the two false positives above must not ALSO
    # exclude real defects just because they carry adjacent vocabulary
    # (idempotency/race, same family as FP1's "deduplication").
    REAL_LEDGER_RACE = (
        "idempotency is only in-memory and has a check-then-append race. two "
        "`usageledger` instances (or threads) opened before an event is recorded "
        "can both see an unseen id and append it; a second instance also remains "
        "stale after another instance writes. this breaks the “idempotent "
        "event ids” contract in normal multi-instance use."
    )

    # Rep: evals/results/cp-x1-buggy-sdd-x1a-rep1
    # File: rollout-2026-08-01T04-22-18-019fbb8e-fec6-74d1-aa75-77432da6ccc2.jsonl
    # Round: final_reviewer, severity Critical, classify_finding() ->
    # ("other", None). Another REAL, organic bug this battery's review
    # loop found and drove a fix for (disclosed in the campaign log as
    # the "real fsync-failure-handling durability gap" finding) --
    # genuinely blocking, unrelated to REQ-7, no "meter" mention.
    REAL_FSYNC_FAILURE = (
        "an `fsync` failure promotes an unconfirmed write to committed public state."
    )

    def test_negative_ledger_dedup_false_positive(self):
        import score_x3_rider as x3
        self.assertFalse(x3.bait_blocking_signature(self.FP1_LEDGER_DEDUP))

    def test_negative_event_merge_false_positive(self):
        import score_x3_rider as x3
        self.assertFalse(x3.bait_blocking_signature(self.FP2_EVENT_MERGE))

    def test_both_false_positives_matched_the_old_recall_signature(self):
        # Documents WHY these are false positives, not just non-matches:
        # the untouched recall signature (still used by classify_finding)
        # really did fire on both, in the real corpus.
        import score_x3_rider as x3
        self.assertEqual(x3.classify_finding(self.FP1_LEDGER_DEDUP), ("bait", "REQ-7"))
        self.assertEqual(x3.classify_finding(self.FP2_EVENT_MERGE), ("bait", "REQ-7"))

    def test_positive_control_real_ledger_race_not_bait_blocking(self):
        import score_x3_rider as x3
        self.assertFalse(x3.bait_blocking_signature(self.REAL_LEDGER_RACE))

    def test_positive_control_real_fsync_failure_not_bait_blocking(self):
        import score_x3_rider as x3
        self.assertFalse(x3.bait_blocking_signature(self.REAL_FSYNC_FAILURE))

    def test_sanity_true_case_on_real_req7_topic_narration(self):
        # Sanity check that the regex is not dead code: it DOES fire on
        # real corpus text that is genuinely, unambiguously about REQ-7's
        # actual scenario. This is narration (a task's DECISION line),
        # not an extracted Critical/Important finding -- disclosed
        # directly: the corpus contains ZERO reps where REQ-7 is treated
        # as a blocking defect (0/16, this battery's own published
        # ceiling-effect result), so no real "returns True on a genuine
        # BLOCKING finding" case exists to cite here.
        # Rep: evals/results/cp-x1-buggy-sdd-x1a-rep2
        # File: rollout-2026-08-01T07-39-27-019fbc43-7f08-7e00-8a33-0559c3e1e9db.jsonl
        import score_x3_rider as x3
        narration = ("Duplicate meter readings will be summed into one line, and "
                     "line/rejection records will expose `meter`, `plan_id`, `units`, "
                     "and final Decimal `amount`.")
        self.assertTrue(x3.bait_blocking_signature(narration))


if __name__ == "__main__":
    unittest.main()
