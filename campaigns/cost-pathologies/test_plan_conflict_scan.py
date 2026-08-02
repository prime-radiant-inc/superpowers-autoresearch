"""Regression tests for `plan-conflict-scan` (queue-execution campaign,
2026-08-01, item 16 of reports/2026-08-cost-pathologies-campaign.md §6):
the X7-B mechanical scanner, ratified as-built during the closed
cost-pathologies campaign (`campaigns/cost-pathologies/arm-manifest.md`'s
`plan-conflict-scan (X7-B) validation` section) but never pinned in a
test of its own.

The script itself lives on `cp/x7b` in the sibling `superpowers` repo
(`skills/subagent-driven-development/scripts/plan-conflict-scan`, the X7-B
treatment arm's own file -- see arm-manifest.md's X7-B row and
`scenarios/cp-x1-wavecap/seeded-truth-ledger.md`'s "run directly against
this plan" note). This file vendors a copy at
`campaigns/cost-pathologies/plan-conflict-scan` so the campaign's own test
suite can pin its behavior without a cross-repo test dependency.

Three parser-scope decisions were ratified as-built, per arm-manifest.md:

  (a) producer recognition reads `Produces:` lines only -- a produced
      interface named only in prose is missed (silently absent from the
      produced set, so a real consumer of it reports a false-positive
      "no task produces it").
  (b) prose `Consumes:` lines are not attempted by design -- a consumer
      named only in prose never registers, so a REAL missing-producer
      conflict on that name is invisible (a false negative: zero
      findings where the plan is genuinely broken).
  (c) multi-name backtick spans were not decomposed -- a single pair of
      backticks naming several identifiers as one comma-separated field
      list (e.g. `` `compactions, patch_applies` ``, the real shape found
      on `docs/plans/2026-07-28-codex-efficiency-evals.md:210-216` during
      X7-B's own corpus validation) failed the identifier regex whole and
      was silently dropped -- so NEITHER name registered as produced,
      producing a false positive for every consumer of either name.

arm-manifest.md explicitly named (c) as the trade "the X7 pre-registration"
should decide, not an unreviewed script change: "Decomposing multi-name
backtick spans would zero the first [false positive] out, at the cost of
tokenizing prose that happens to sit between backticks." This task's own
brief authorizes exactly that decision: implement (c) if it is a local
change to the span-parsing layer.

**(c) was a local change.** `addids()`'s backtick loop already isolates one
backtick span's text into `tok` (stripping the surrounding backticks and
any trailing `(args) -> type` suffix) before calling `addid()` once on the
whole string; decomposition is `split(tok, parts, /[ \\t]*,[ \\t]*/)` over
that same already-isolated string, followed by one `addid()` call per
non-empty piece -- four added lines, no change to any other function, no
change to how a single-name span (the overwhelmingly common case, and the
only shape `addid()`'s identifier regex ever accepted before) is parsed
(`split` on a comma-free string returns exactly the original string as its
one element). (a) and (b) stay tested-and-deferred: both are the parser
deliberately never looking at prose text at all, which is a scope decision,
not a bug with a local fix -- see arm-manifest.md's "Both trades belong in
the X7 pre-registration" note.

Every fixture below is a minimal, self-contained plan snippet -- no
scenario harness, no subagent, no API spend.
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "plan-conflict-scan"

NO_CONFLICTS_LINE = "no conflicts in the Files:/Interfaces: blocks or the task code"


def run_scan(plan_text):
    """Writes PLAN_TEXT to a temp file and runs the vendored
    plan-conflict-scan against it, returning the completed subprocess
    (stdout/stderr captured, text mode)."""
    with tempfile.TemporaryDirectory() as tmp:
        plan_path = Path(tmp) / "plan.md"
        plan_path.write_text(plan_text)
        return subprocess.run(
            ["bash", str(SCRIPT), str(plan_path)],
            capture_output=True,
            text=True,
        )


# ---------------------------------------------------------------------------
# (a) producer recognition reads Produces: lines only -- tested-and-deferred.
# ---------------------------------------------------------------------------

PROSE_PRODUCER_PLAN = """\
# Task 1

Creates the ingest module. This task's own implementation defines a
function named `emit_event` that later tasks will call directly.

**Files:**
- Create: `ingest.py`

# Task 2

Wires the dispatcher to the event emitter Task 1 built.

**Files:**
- Create: `dispatch.py`

**Interfaces:**
- Consumes: `emit_event`
"""


class TestProducerRecognitionIsConfinedToProducesLinesLimit(unittest.TestCase):
    """(a), ratified and deferred: Task 1 genuinely produces `emit_event`
    (stated in prose), and Task 2's structured `Consumes:` line correctly
    registers the consumption -- but since the producer is never declared
    in a `Produces:` line, the scan reports a false-positive missing
    producer. This pins the documented miss; it is not a bug to fix."""

    def test_prose_only_producer_yields_a_false_positive_missing_producer(self):
        result = run_scan(PROSE_PRODUCER_PLAN)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Task 2 consumes `emit_event`; no task produces it", result.stdout
        )


# ---------------------------------------------------------------------------
# (b) prose Consumes: lines are not attempted by design -- tested-and-deferred.
# ---------------------------------------------------------------------------

PROSE_CONSUMES_PLAN = """\
# Task 1

Creates the notifier stub, deliberately without a send implementation.

**Files:**
- Create: `notifier.py`

# Task 2

This task's own implementation consumes the `send_alert` callable from
Task 1 to deliver messages -- described here in prose only, with no
Interfaces: block naming it.

**Files:**
- Create: `alerts.py`
"""


class TestProseConsumesLinesAreNotAttemptedLimit(unittest.TestCase):
    """(b), ratified and deferred: `send_alert` is a genuine missing
    producer -- Task 1 never creates it, Task 2 genuinely needs it -- but
    because Task 2 names its consumption only in prose (no structured
    Consumes: line), the scan never registers the consumption at all and
    reports zero conflicts. This pins the documented miss on a REAL
    conflict; it is not a bug to fix."""

    def test_prose_only_consumer_makes_a_real_missing_producer_invisible(self):
        result = run_scan(PROSE_CONSUMES_PLAN)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(NO_CONFLICTS_LINE, result.stdout)
        self.assertNotIn("send_alert", result.stdout)


# ---------------------------------------------------------------------------
# (c) multi-name backtick spans -- fixed (a local change to addids()).
# ---------------------------------------------------------------------------

MULTI_NAME_SPAN_PLAN = """\
# Task 1

Creates the tracker.

**Files:**
- Create: `tracker.py`

**Interfaces:**
- Produces: `compactions, patch_applies`

# Task 2

Reads compaction events.

**Files:**
- Create: `reader.py`

**Interfaces:**
- Consumes: `compactions`

# Task 3

Reads patch-apply events.

**Files:**
- Create: `applier.py`

**Interfaces:**
- Consumes: `patch_applies`
"""


class TestMultiNameBacktickSpansAreDecomposed(unittest.TestCase):
    """(c), fixed: Task 1's single `` `compactions, patch_applies` ``
    backtick span names two producers, and Tasks 2/3 each consume one of
    them via their own single-name Consumes: lines. Before the fix, the
    whole comma-joined span failed the identifier regex and was silently
    dropped -- producing two false-positive "no task produces it"
    findings (see this file's module docstring for the pre-fix
    transcript). After the fix, both names register as produced and the
    plan is genuinely conflict-free."""

    def test_both_names_in_the_span_register_as_produced_and_the_plan_is_clean(self):
        result = run_scan(MULTI_NAME_SPAN_PLAN)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(NO_CONFLICTS_LINE, result.stdout)
        self.assertNotIn("no task produces it", result.stdout)
        self.assertIn("2 consumed and 2 produced interfaces", result.stdout)

    def test_single_name_spans_are_unaffected_by_the_split(self):
        # A one-name span (the overwhelmingly common real shape) must
        # still register as exactly one identifier, not be perturbed by
        # decomposition logic that only matters when a comma is present.
        result = run_scan(PROSE_PRODUCER_PLAN)
        self.assertIn("1 consumed and 0 produced interfaces", result.stdout)


if __name__ == "__main__":
    unittest.main()
