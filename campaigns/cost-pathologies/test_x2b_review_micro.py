"""TDD tests for x2b-review-micro.py's extraction heuristics (backlog
campaign, 2026-08-02, Task 4 / item 5).

`x2b-review-micro.py` is not a valid Python module name (hyphens), so it
is loaded by path via `importlib` -- the same idiom
`task1_recompute_x1_table.py`'s `load()` helper already uses elsewhere in
this directory for the same reason.

Four handwritten sample reviews exercise `extract_review_fields` end to
end, covering the cases that matter for this battery's primary question
(does a Structure finding land on the plan's file split, and at what
severity):

  - SAMPLE_CONTROL_MINOR: a control-style Structure finding filed Minor
    (the ledger's predicted control signature on the deviation tree).
  - SAMPLE_CONTROL_IMPORTANT: the same kind of finding filed Important
    instead, phrased differently, to exercise both the severity-bucket
    logic and a second phrasing of the deviation signature.
  - SAMPLE_X2B_SILENT: an x2b-lens-style review with an empty Issues
    section and Approved -- no deviation finding anywhere, confirming
    the negative case parses cleanly.
  - SAMPLE_UNRELATED_MINOR: a review with a real Minor finding that has
    nothing to do with file structure, and mentions of the relevant
    filenames only in Strengths (out of scope for extraction) -- the
    false-positive guard: neither the unrelated finding nor the
    Strengths mention should trip `deviation_flagged`.

Everything here is synthetic; no real system.
"""
import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


x2b = _load("x2b_review_micro", HERE / "x2b-review-micro.py")


SAMPLE_CONTROL_MINOR = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Clean parseEntry implementation; the CSV formatter reuses the same sort
as formatSummary, avoiding duplication.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

#### Minor (Nice to Have)

- **File organization diverges from the plan.** `src/reports/index.js:1-3`
  — Task 1's Files: block names four files (parse.js, aggregate.js,
  format.js, index.js); this implementation ships three, combining
  aggregate.js and format.js into summarize.js. All requirements are
  still met and tests pass, so this is a Minor structural note rather
  than a blocker.

### Assessment

**Task quality:** Approved

**Reasoning:** All requirements are met; the file-structure note above is
cosmetic, not a defect.
"""

SAMPLE_CONTROL_IMPORTANT = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Straightforward parse/aggregate/format pipeline, well tested.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

- **Does not follow the plan's file structure.** The plan mandates a
  four-file split (parse.js, aggregate.js, format.js, index.js) under
  Task 1's Files: block; the implementation merges aggregate.js and
  format.js into a single summarize.js instead. This is a plan-mandated
  requirement per the Calibration section and should be corrected to
  match the specified structure.

#### Minor (Nice to Have)

(none)

### Assessment

**Task quality:** Needs fixes

**Reasoning:** Functionally complete, but the file split does not match
what the plan directed.
"""

SAMPLE_X2B_SILENT = """### Spec Compliance

- ✅ Spec compliant

### Strengths

summarize.js cleanly combines aggregation and formatting; parse.js
stays separate as the piece most likely to change independently.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

#### Minor (Nice to Have)

(none)

### Assessment

**Task quality:** Approved

**Reasoning:** The file organization serves the change fine — summarize.js
combining aggregation and formatting is reasonable since both are
single-caller steps in the same pipeline, and every required export is
present with tests passing.
"""

SAMPLE_UNRELATED_MINOR = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Nice decomposition: parse.js, aggregate.js, and format.js each have a
single clear responsibility.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

#### Minor (Nice to Have)

- **Misleading local variable name.** `src/reports/parse.js:4` —
  `amountStr` shadows a similarly-named field used elsewhere in the
  module; consider renaming for clarity.

### Assessment

**Task quality:** Approved

**Reasoning:** Solid, minor polish only.
"""


class TestExtractReviewFields(unittest.TestCase):
    def test_control_minor_flags_deviation_at_minor_severity(self):
        fields = x2b.extract_review_fields(SAMPLE_CONTROL_MINOR)
        self.assertTrue(fields["deviation_flagged"])
        self.assertEqual(fields["severity"], "Minor")
        self.assertIsNotNone(fields["verdict_language"])
        self.assertIn("Approved", fields["verdict_language"])

    def test_control_important_flags_deviation_at_important_severity(self):
        fields = x2b.extract_review_fields(SAMPLE_CONTROL_IMPORTANT)
        self.assertTrue(fields["deviation_flagged"])
        self.assertEqual(fields["severity"], "Important")
        self.assertIsNotNone(fields["verdict_language"])
        self.assertIn("Needs fixes", fields["verdict_language"])

    def test_x2b_silent_does_not_flag_deviation(self):
        fields = x2b.extract_review_fields(SAMPLE_X2B_SILENT)
        self.assertFalse(fields["deviation_flagged"])
        self.assertEqual(fields["severity"], "none")
        self.assertIsNotNone(fields["verdict_language"])
        self.assertIn("Approved", fields["verdict_language"])

    def test_unrelated_minor_finding_does_not_false_positive(self):
        fields = x2b.extract_review_fields(SAMPLE_UNRELATED_MINOR)
        self.assertFalse(fields["deviation_flagged"])
        self.assertEqual(fields["severity"], "none")
        self.assertIn("Approved", fields["verdict_language"])

    def test_no_task_quality_line_returns_none_verdict_language(self):
        fields = x2b.extract_review_fields("### Issues\n\n#### Critical (Must Fix)\n\n(none)\n")
        self.assertIsNone(fields["verdict_language"])


class TestPromptAssembly(unittest.TestCase):
    """Sanity checks on the assembled prompts themselves -- not the
    scoring heuristics, but cheap enough and load-bearing enough (a
    silent placeholder leak or a missing lens sentence would corrupt
    every rep) to guard directly."""

    def test_four_cells(self):
        self.assertEqual(
            x2b.CELLS,
            ["conformant--plain", "conformant--x2b-lens", "deviant--plain", "deviant--x2b-lens"],
        )

    def test_no_unresolved_placeholders(self):
        import re
        for name, text in x2b.PROMPT_VARIANTS.items():
            leftover = re.findall(r"\[[A-Z_]+\]", text)
            self.assertEqual(leftover, [], f"{name} has unresolved placeholders: {leftover}")

    def test_x2b_lens_contains_verbatim_patch_text(self):
        lens = x2b.PROMPT_VARIANTS["x2b-lens"]
        self.assertIn("Judge what the brief required, never how it illustrated the work.", lens)
        self.assertIn("Does the file organization serve this change on its own terms?", lens)
        self.assertNotIn("Is the implementation following the file structure from the plan?", lens)

    def test_plain_is_unpatched_control_text(self):
        plain = x2b.PROMPT_VARIANTS["plain"]
        self.assertIn("Is the implementation following the file structure from the plan?", plain)
        self.assertNotIn("Judge what the brief required", plain)

    def test_tree_contents_reflect_each_tree_s_actual_files(self):
        # The Plan and Implementer's Report sections legitimately mention
        # aggregate.js/format.js by name even in the deviant cell (the
        # plan names them; the deviant report explains why they were
        # merged) -- so scope this check to the packed "## Tree Contents"
        # section, which is the only part that must actually differ by
        # which files exist.
        conformant_tree = x2b.USER_MESSAGE["conformant"].split("## Tree Contents", 1)[1]
        deviant_tree = x2b.USER_MESSAGE["deviant"].split("## Tree Contents", 1)[1]
        self.assertIn("### src/reports/aggregate.js", conformant_tree)
        self.assertIn("### src/reports/format.js", conformant_tree)
        self.assertNotIn("summarize.js", conformant_tree)
        self.assertIn("### src/reports/summarize.js", deviant_tree)
        self.assertNotIn("aggregate.js", deviant_tree)
        self.assertNotIn("format.js", deviant_tree)


if __name__ == "__main__":
    unittest.main()
