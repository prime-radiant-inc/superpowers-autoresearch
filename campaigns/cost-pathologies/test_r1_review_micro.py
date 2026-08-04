"""TDD tests for r1-review-micro.py's extraction heuristics and prompt
assembly (plan-decomposition campaign, 2026-08-03, Task 5).

`r1-review-micro.py` is not a valid Python module name (hyphens), so it
is loaded by path via `importlib` -- same idiom `test_x2b_review_micro.py`
already uses for its own hyphenated sibling.

Two families of handwritten samples exercise `extract_review_fields` end
to end:

  - Structure-finding samples (reusing x2b's DEVIATION_RE, now checked
    across four possible sections instead of three -- Cleanup Wave is
    new): control-style Minor, a Cleanup-Wave routing (the cleanup-wave
    arm's own output shape), and a clean negative (x2b-lens-style
    silence) plus the false-positive guard from x2b's own suite.
  - Real-bug samples (the NEW `REAL_BUG_RE`, covering the seeded
    zero-amount-CSV defect in `micro-fixtures/r1/mixed/`): caught
    correctly at Important (two phrasings), the two adversarial
    misrouting cases this battery exists to detect (buried at Minor,
    buried in Cleanup Wave), and two false-positive guards (the bug's
    keywords appearing only in Strengths; "csv" and "zero" both present
    in an Issues section but unrelated to each other and >300 chars
    apart).

`TestPromptAssembly` sanity-checks the 8 assembled cells the same way
x2b's own suite sanity-checks its 4: no leftover placeholders, each
policy arm contains the text that makes it that arm and not another, and
the packed tree contents differ between `deviant` and `mixed` in exactly
the one file the seeded bug touches.

`TestUnsectionedFallback` covers the strict-extraction failure class code
review flagged (the 7th occurrence in this program): a real answer that
reports a real signal under an off-canonical heading, or no heading at
all, must never read as absent. Four samples: the reviewer's two named
adversarial phrasings verbatim (the CSV bug under an invented
"### Behavioral Findings" heading; the structure deviation under a bare
"### Cleanup" heading that must NOT swallow-and-discard via the
preceding "(none)" bucket's shortcut), plus two more constructed here
(the bug stated in a heading-less prose paragraph; the bug stated in a
markdown table row under a third off-canonical heading). All four must
extract as present (`*_flagged=True`), with `*_unsectioned=True` and
`*_section="none"` -- ambiguous, not absent.

Everything here is synthetic; no real system.
"""
import importlib.util
import pathlib
import re
import sys
import unittest

HERE = pathlib.Path(__file__).parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


r1 = _load("r1_review_micro", HERE / "r1-review-micro.py")


# ---------------------------------------------------------------------------
# Structure-finding samples
# ---------------------------------------------------------------------------

SAMPLE_STRUCTURE_MINOR = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Clean parseEntry implementation.

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

SAMPLE_STRUCTURE_CLEANUP_WAVE = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Reasonable split; parse.js stays independent.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

### Cleanup Wave (non-blocking)

- File organization diverges from the plan: three files ship instead of
  the plan's four (aggregate.js and format.js merged into summarize.js).
  All requirements are met; deferred, non-blocking.

### Assessment

**Task quality:** Approved

**Reasoning:** Spec-compliant; the structural note is deferred per the
cleanup-wave policy.
"""

SAMPLE_STRUCTURE_SILENT = """### Spec Compliance

- ✅ Spec compliant

### Strengths

summarize.js cleanly combines aggregation and formatting.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

#### Minor (Nice to Have)

(none)

### Assessment

**Task quality:** Approved

**Reasoning:** The file organization serves the change fine.
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


# ---------------------------------------------------------------------------
# Real-bug samples (the seeded formatSummaryCsv zero-amount defect)
# ---------------------------------------------------------------------------

SAMPLE_BUG_IMPORTANT_A = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Clean parse/aggregate/format split.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

- **`formatSummaryCsv` silently drops zero-total categories.**
  `src/reports/summarize.js:20` — the CSV formatter filters out any
  category whose amount is 0 before rendering rows
  (`.filter(([, amount]) => amount !== 0)`), but `formatSummary` renders
  every category regardless of total, and the plan requires
  `formatSummaryCsv` to use "the same category/amount pairs
  `formatSummary` uses." A category that nets to zero (an equal charge
  and refund, say) silently disappears from the CSV output only.

#### Minor (Nice to Have)

(none)

### Assessment

**Task quality:** Needs fixes

**Reasoning:** The CSV/text-summary parity requirement is broken for
zero-total categories.
"""

SAMPLE_BUG_IMPORTANT_B = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Well tested otherwise.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

- **CSV output omits rows that the text summary still shows.**
  `summarize.js` — `formatSummaryCsv` excludes any entry whose total is
  0, unlike `formatSummary`. This breaks parity between the two
  renderers and would silently lose data for any net-zero category.

### Assessment

**Task quality:** Needs fixes

**Reasoning:** Functional defect in the CSV path.
"""

# Adversarial case 1: the bug is real but a triage policy has buried it at
# Minor -- the failure mode this battery's real_bug_blocking metric exists
# to catch.
SAMPLE_BUG_BURIED_MINOR = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Otherwise solid.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

#### Minor (Nice to Have)

- CSV rows are skipped for categories with a zero amount total, unlike
  the plain-text summary. Probably worth a follow-up.

### Assessment

**Task quality:** Approved

**Reasoning:** Nothing blocking.
"""

# Adversarial case 2: the bug has been misrouted into the cleanup-wave
# arm's non-blocking section.
SAMPLE_BUG_BURIED_CLEANUP_WAVE = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Otherwise solid.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

### Cleanup Wave (non-blocking)

- CSV output silently drops zero-amount categories while the text
  summary keeps them (`summarize.js`'s `.filter()` call) -- flagged here
  as a polish item.

### Assessment

**Task quality:** Approved

**Reasoning:** Nothing blocking.
"""

# False-positive guard 1: bug keywords appear only in Strengths (praising
# the CSV feature and separately noting zero handling elsewhere), never in
# an Issues section.
SAMPLE_BUG_FALSE_POSITIVE_STRENGTHS = """### Spec Compliance

- ✅ Spec compliant

### Strengths

The new CSV export is clean, and parseEntry correctly rejects a zero-length
line as invalid input.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

#### Minor (Nice to Have)

- **Misleading local variable name.** `src/reports/parse.js:4` —
  `amountStr` shadows a similarly-named field; consider renaming.

### Assessment

**Task quality:** Approved

**Reasoning:** Minor polish only.
"""

# False-positive guard 2: "csv" and "zero" both appear in an Issues
# section, but far apart (>300 chars) and unrelated to each other.
SAMPLE_BUG_FALSE_POSITIVE_UNRELATED_ISSUES = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Solid overall.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

#### Minor (Nice to Have)

- **CSV output has no trailing newline.** `src/reports/summarize.js:22` —
  minor formatting nit, most tools handle it fine either way, purely
  cosmetic and not worth blocking on, consider adding one in a later
  pass if a downstream consumer ever complains about it, but there is no
  evidence today that anything depends on the trailing newline being
  present, so this is filed at the lowest possible priority for now.
- **Off-by-one risk in an unrelated helper.** `src/reports/parse.js:9` —
  if `amountStr` were ever an empty string after trimming, `Number("")`
  evaluates to zero rather than throwing, which could in principle mask
  a malformed line as a legitimate zero-amount entry; worth a follow-up
  test even though the current fixture data never exercises it.

### Assessment

**Task quality:** Approved

**Reasoning:** No blocking issues.
"""


# ---------------------------------------------------------------------------
# Unsectioned-fallback samples (code review's Important finding: a real
# signal reported under an off-canonical heading, or no heading at all,
# must never extract as absent). Two are the reviewer's own named
# phrasings; two are constructed here per the reviewer's "e.g." examples.
# ---------------------------------------------------------------------------

# Reviewer's adversarial phrasing 1: the CSV bug under an invented
# "### Behavioral Findings" heading -- never prompted for by any arm, so
# no bucket in SECTION_RE/_BUCKET_NAMES recognizes it.
SAMPLE_BUG_UNRECOGNIZED_HEADING = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Otherwise solid, well tested.

### Behavioral Findings

- `formatSummaryCsv` silently drops zero-total categories
  (`src/reports/summarize.js`'s `.filter(([, amount]) => amount !== 0)`),
  unlike `formatSummary` which keeps them -- breaks the plan's "same
  category/amount pairs" parity requirement for any category netting to
  zero.

### Assessment

**Task quality:** Needs fixes

**Reasoning:** Functional defect in the CSV path.
"""

# Reviewer's adversarial phrasing 2: the structure deviation under a bare
# "### Cleanup" heading (missing "Wave (non-blocking)"). This is the
# exact shape that broke the OLD lookahead-based SECTION_RE: "#### Important
# (Should Fix)" is immediately followed by "(none)", and the old design's
# lookahead only stopped at a RECOGNIZED heading -- so "### Cleanup"'s
# body got absorbed into Important's captured text, where split_findings'
# leading-"(none)" shortcut then discarded it. The new heading-position
# split stops Important's block at "### Cleanup" (any heading, recognized
# or not), so "### Cleanup"'s own body is available to the full-text
# fallback.
SAMPLE_STRUCTURE_UNRECOGNIZED_HEADING = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Reasonable split; parse.js stays independent.

### Issues

#### Critical (Must Fix)

(none)

#### Important (Should Fix)

(none)

### Cleanup

- File organization diverges from the plan: three files ship instead of
  the plan's four (aggregate.js and format.js merged into summarize.js).
  All requirements are met; deferred, non-blocking.

### Assessment

**Task quality:** Approved
"""

# Constructed here (reviewer's own "e.g."): the bug stated in a
# heading-less prose paragraph -- the model didn't follow Output Format
# at all, so `_heading_blocks` finds zero headings and the entire answer
# is available to the fallback.
SAMPLE_BUG_NO_HEADINGS_PROSE = """This implementation looks solid overall, with a clean split between
parsing and formatting. One thing worth flagging: formatSummaryCsv
filters out any category with a zero amount total before writing CSV
rows, so those categories silently vanish from the CSV export even
though the plain-text summary still lists them -- the plan calls for the
CSV to use the same category/amount pairs the text summary uses, so this
is a real gap, not a style question. Everything else checks out and the
tests pass.

**Task quality:** Needs fixes
"""

# Constructed here (reviewer's own "e.g."): the bug stated in a markdown
# table row, under a third off-canonical heading ("### Comparison") so
# this exercises both "table, not a bullet/paragraph" AND "unrecognized
# heading" at once.
SAMPLE_BUG_TABLE_ROW = """### Spec Compliance

- ✅ Spec compliant

### Strengths

Nice decomposition overall.

### Comparison

| Renderer | Zero-amount categories |
| --- | --- |
| formatSummary | included |
| formatSummaryCsv | dropped (`.filter()` in summarize.js) |

### Assessment

**Task quality:** Needs fixes
"""


class TestStructureExtraction(unittest.TestCase):
    def test_control_minor_flags_structure_at_minor(self):
        fields = r1.extract_review_fields(SAMPLE_STRUCTURE_MINOR)
        self.assertTrue(fields["structure_flagged"])
        self.assertEqual(fields["structure_section"], "Minor")

    def test_cleanup_wave_flags_structure_at_cleanup_wave(self):
        fields = r1.extract_review_fields(SAMPLE_STRUCTURE_CLEANUP_WAVE)
        self.assertTrue(fields["structure_flagged"])
        self.assertEqual(fields["structure_section"], "Cleanup Wave")

    def test_silent_does_not_flag_structure(self):
        fields = r1.extract_review_fields(SAMPLE_STRUCTURE_SILENT)
        self.assertFalse(fields["structure_flagged"])
        self.assertEqual(fields["structure_section"], "none")

    def test_unrelated_minor_does_not_false_positive_structure(self):
        fields = r1.extract_review_fields(SAMPLE_UNRELATED_MINOR)
        self.assertFalse(fields["structure_flagged"])


class TestRealBugExtraction(unittest.TestCase):
    def test_bug_caught_at_important_is_blocking_phrasing_a(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_IMPORTANT_A)
        self.assertTrue(fields["real_bug_flagged"])
        self.assertEqual(fields["real_bug_section"], "Important")
        self.assertTrue(fields["real_bug_blocking"])

    def test_bug_caught_at_important_is_blocking_phrasing_b(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_IMPORTANT_B)
        self.assertTrue(fields["real_bug_flagged"])
        self.assertEqual(fields["real_bug_section"], "Important")
        self.assertTrue(fields["real_bug_blocking"])

    def test_bug_buried_at_minor_is_flagged_but_not_blocking(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_BURIED_MINOR)
        self.assertTrue(fields["real_bug_flagged"])
        self.assertEqual(fields["real_bug_section"], "Minor")
        self.assertFalse(fields["real_bug_blocking"])

    def test_bug_buried_in_cleanup_wave_is_flagged_but_not_blocking(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_BURIED_CLEANUP_WAVE)
        self.assertTrue(fields["real_bug_flagged"])
        self.assertEqual(fields["real_bug_section"], "Cleanup Wave")
        self.assertFalse(fields["real_bug_blocking"])

    def test_bug_keywords_in_strengths_only_do_not_false_positive(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_FALSE_POSITIVE_STRENGTHS)
        self.assertFalse(fields["real_bug_flagged"])
        self.assertEqual(fields["real_bug_section"], "none")
        self.assertFalse(fields["real_bug_blocking"])

    def test_unrelated_csv_and_zero_mentions_do_not_false_positive(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_FALSE_POSITIVE_UNRELATED_ISSUES)
        self.assertFalse(fields["real_bug_flagged"])
        self.assertEqual(fields["real_bug_section"], "none")
        self.assertFalse(fields["real_bug_blocking"])


class TestVerdictLanguage(unittest.TestCase):
    def test_verdict_language_extracted(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_IMPORTANT_A)
        self.assertIsNotNone(fields["verdict_language"])
        self.assertIn("Needs fixes", fields["verdict_language"])

    def test_no_task_quality_line_returns_none_verdict_language(self):
        fields = r1.extract_review_fields("### Issues\n\n#### Critical (Must Fix)\n\n(none)\n")
        self.assertIsNone(fields["verdict_language"])


class TestUnsectionedFallback(unittest.TestCase):
    """A real signal reported outside every recognized bucket -- an
    off-canonical heading, or no heading at all -- must read as present
    (unsectioned) not absent. Covers code review's Important finding: the
    old lookahead-based SECTION_RE let an unrecognized heading's body get
    absorbed into a preceding empty ("(none)") recognized bucket and then
    discarded by split_findings' leading-"(none)" shortcut."""

    def test_bug_under_invented_heading_reads_present_not_absent(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_UNRECOGNIZED_HEADING)
        self.assertTrue(fields["real_bug_flagged"])
        self.assertEqual(fields["real_bug_section"], "none")
        self.assertTrue(fields["real_bug_unsectioned"])
        self.assertFalse(fields["real_bug_blocking"])

    def test_structure_under_bare_cleanup_heading_reads_present_not_absent(self):
        fields = r1.extract_review_fields(SAMPLE_STRUCTURE_UNRECOGNIZED_HEADING)
        self.assertTrue(fields["structure_flagged"])
        self.assertEqual(fields["structure_section"], "none")
        self.assertTrue(fields["structure_unsectioned"])
        # The regression this guards: with the old lookahead design, this
        # sample's deviation text was absorbed into Important's "(none)"
        # body and discarded, so both structure_flagged and
        # structure_section silently read as absent/"none". Also confirm
        # Important itself still reads correctly as empty, proving the
        # fix didn't just stop looking at Important at all.
        sections = r1.extract_sections(SAMPLE_STRUCTURE_UNRECOGNIZED_HEADING)
        self.assertTrue(
            re.match(r"^\(none\)$", sections["Important"].strip(), re.I),
            f"Important section body corrupted: {sections['Important']!r}",
        )

    def test_bug_in_heading_less_prose_reads_present_not_absent(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_NO_HEADINGS_PROSE)
        self.assertTrue(fields["real_bug_flagged"])
        self.assertEqual(fields["real_bug_section"], "none")
        self.assertTrue(fields["real_bug_unsectioned"])
        self.assertFalse(fields["real_bug_blocking"])

    def test_bug_in_table_row_reads_present_not_absent(self):
        fields = r1.extract_review_fields(SAMPLE_BUG_TABLE_ROW)
        self.assertTrue(fields["real_bug_flagged"])
        self.assertEqual(fields["real_bug_section"], "none")
        self.assertTrue(fields["real_bug_unsectioned"])
        self.assertFalse(fields["real_bug_blocking"])

    def test_sectioned_hits_never_also_set_unsectioned(self):
        # A signal correctly found in a recognized bucket is certain, not
        # ambiguous -- *_unsectioned must stay False so the two states
        # never overlap on the same field.
        fields = r1.extract_review_fields(SAMPLE_BUG_IMPORTANT_A)
        self.assertEqual(fields["real_bug_section"], "Important")
        self.assertFalse(fields["real_bug_unsectioned"])

        fields = r1.extract_review_fields(SAMPLE_STRUCTURE_MINOR)
        self.assertEqual(fields["structure_section"], "Minor")
        self.assertFalse(fields["structure_unsectioned"])


class TestPromptAssembly(unittest.TestCase):
    """Sanity checks on the assembled prompts -- not the scoring
    heuristics, but cheap enough and load-bearing enough (a silent
    placeholder leak or a missing policy paragraph would corrupt every
    rep) to guard directly. Mirrors test_x2b_review_micro.py's own
    TestPromptAssembly."""

    def test_eight_cells(self):
        self.assertEqual(
            r1.CELLS,
            [
                "deviant--plain", "deviant--lens-suppress",
                "deviant--lens-downgrade", "deviant--cleanup-wave",
                "mixed--plain", "mixed--lens-suppress",
                "mixed--lens-downgrade", "mixed--cleanup-wave",
            ],
        )

    def test_no_unresolved_placeholders(self):
        import re
        for name, text in r1.PROMPT_VARIANTS.items():
            leftover = re.findall(r"\{[a-z_]+\}|\[[A-Z_]+\]", text)
            self.assertEqual(leftover, [], f"{name} has unresolved placeholders: {leftover}")

    def test_plain_is_byte_identical_to_x2b_plain(self):
        self.assertEqual(r1.PROMPT_VARIANTS["plain"], r1.X2B.PROMPT_VARIANTS["plain"])

    def test_lens_suppress_is_byte_identical_to_x2b_lens(self):
        self.assertEqual(r1.PROMPT_VARIANTS["lens-suppress"], r1.X2B.PROMPT_VARIANTS["x2b-lens"])

    def test_lens_downgrade_contains_its_own_text_not_suppress_text(self):
        downgrade = r1.PROMPT_VARIANTS["lens-downgrade"]
        self.assertIn("Cleanup Ledger", downgrade)
        self.assertIn("Does the file organization serve this change on its own terms?", downgrade)
        self.assertNotIn(
            "none of those is a finding while the requirement is\nmet", downgrade
        )

    def test_cleanup_wave_replaces_minor_with_cleanup_wave_section(self):
        cleanup = r1.PROMPT_VARIANTS["cleanup-wave"]
        self.assertIn("### Cleanup Wave (non-blocking)", cleanup)
        self.assertNotIn("Minor (Nice to Have)", cleanup)
        self.assertIn("Is the implementation following the file structure from the plan?", cleanup)

    def test_deviant_and_mixed_trees_are_not_duplicated(self):
        # deviant must be referenced from x2b's fixture dir, not copied
        # into micro-fixtures/r1/.
        self.assertEqual(r1.TREE_DIRS["deviant"], r1.X2B_FIXTURE_DIR / "deviant")
        self.assertEqual(r1.TREE_DIRS["mixed"], r1.R1_FIXTURE_DIR / "mixed")
        self.assertNotIn("r1", str(r1.TREE_DIRS["deviant"]))

    def test_tree_contents_differ_only_in_the_seeded_bug_file(self):
        deviant_tree = r1.USER_MESSAGE["deviant"].split("## Tree Contents", 1)[1]
        mixed_tree = r1.USER_MESSAGE["mixed"].split("## Tree Contents", 1)[1]
        self.assertIn("### src/reports/summarize.js", deviant_tree)
        self.assertIn("### src/reports/summarize.js", mixed_tree)
        self.assertNotIn(".filter(([, amount]) => amount !== 0)", deviant_tree)
        self.assertIn(".filter(([, amount]) => amount !== 0)", mixed_tree)
        # parse.js and index.js are byte-identical between the two trees.
        self.assertIn("### src/reports/parse.js", deviant_tree)
        self.assertIn("### src/reports/parse.js", mixed_tree)


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Corpus regression (local-only: out/ is gitignored, so these skip on a
# fresh clone). Locks the 2026-08-04 DEVIATION_RE expansion to the
# 104-answer corpus at PRESENCE level: conformant answers stay at zero
# (precision), deviant-tree answers are detected (recall). The
# raised-vs-reasoned-away SEMANTIC split is deliberately not asserted --
# per-answer hand labels were not persisted, and the standing rule keeps
# hand-rescore mandatory for verdicts.
# ---------------------------------------------------------------------------

import glob

_CORPUS_X2B = HERE / "out" / "x2b-review-micro" / "answers"
_CORPUS_R1 = HERE / "out" / "r1-review-micro" / "answers"


@unittest.skipUnless(_CORPUS_X2B.is_dir(), "local corpus absent")
class TestCorpusX2B(unittest.TestCase):
    def test_conformant_noise_floor(self):
        for f in glob.glob(str(_CORPUS_X2B / "conformant--*.txt")):
            self.assertIsNone(r1.DEVIATION_RE.search(open(f).read()),
                              f"false positive: {f}")

    def test_deviant_plain_presence(self):
        hits = [bool(r1.DEVIATION_RE.search(open(f).read()))
                for f in glob.glob(str(_CORPUS_X2B / "deviant--plain-*.txt"))]
        self.assertTrue(hits and all(hits),
                        f"presence recall regressed: {sum(hits)}/{len(hits)}")


@unittest.skipUnless(_CORPUS_R1.is_dir(), "local corpus absent")
class TestCorpusR1(unittest.TestCase):
    def test_deviant_presence_floor(self):
        for cell, floor in [("deviant--plain", 8), ("deviant--lens-downgrade", 8),
                            ("deviant--cleanup-wave", 8), ("deviant--lens-suppress", 7)]:
            n = sum(r1.extract_review_fields(open(f).read())["structure_flagged"]
                    for f in glob.glob(str(_CORPUS_R1 / f"{cell}-*.txt")))
            self.assertGreaterEqual(n, floor,
                                    f"{cell}: presence {n} below corpus floor {floor}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
