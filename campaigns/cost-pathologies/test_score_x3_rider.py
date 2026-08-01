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


if __name__ == "__main__":
    unittest.main()
