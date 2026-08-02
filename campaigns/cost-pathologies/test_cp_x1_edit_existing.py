"""Discrimination validation for the cp-x1-edit-existing scenario
(queue-execution campaign, 2026-08-01, item 1 of
reports/2026-08-cost-pathologies-campaign.md §6's owed-fixtures queue).

Per the controller's ruling, this task spends no containers or API
budget on real reps -- a later, pre-registered battery task does that.
Instead it validates that
`campaigns/cost-pathologies/scenarios/cp-x1-edit-existing/
seeded-defect-ledger.md`'s four real-defect escape/catch criteria are
mechanically checkable at all, against two CONSTRUCTED post-state code
trees under `fixtures/cp-x1-edit-existing-outcomes/`:

  - `fixed/` -- the shape a competent session plausibly leaves behind:
    Task 1/2 of `credit-adjustments-plan.md` added, AND all four
    pre-existing defects corrected.
  - `carried_forward/` -- the shape a careless, append-only session
    plausibly leaves behind: Task 1/2 added, but all four pre-existing
    defects left exactly as shipped by `setup.sh`'s starting repo
    (`scenarios/cp-x1-edit-existing/fixtures/billing/`).

Two independent layers confirm each region's classification:

  - `scan_defects()` -- a MECHANICAL, regex/text-position scan over the
    tree's own source files, implementing each region's "Escape
    criterion" / "Catch criterion" from the ledger literally. This is
    the primitive a later battery's real scorer would build on.
  - `TestDynamicBehavioralConfirmation` -- imports each tree's `billing`
    package fresh (isolated via a sys.modules purge before/after, since
    both trees share the top-level package name `billing`) and exercises
    the SAME concrete repros used to confirm each defect against the
    scenario's actual starting code (see the ledger's "Confirmed by
    direct repro" notes) -- proving the mechanical scan's verdict
    matches real runtime behavior, not just text shape.

BAIT-1 (REQ-5, duplicate meter readings) is a finding-TEXT region, not a
code-state one (its "correct" code looks identical whether or not a
finding calls it a defect) -- `TestBaitSignature` validates its
finding-text signature directly, reusing the exact regex the ledger
documents (matching `cp-x1-buggy-sdd`'s own bait-signature convention).

Everything here is synthetic; no real system.
"""
import importlib
import os
import re
import sys
import unittest
from decimal import Decimal
from pathlib import Path

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
OUTCOMES = HERE / "fixtures" / "cp-x1-edit-existing-outcomes"
FIXED = OUTCOMES / "fixed"
CARRIED_FORWARD = OUTCOMES / "carried_forward"

# Reused verbatim from seeded-defect-ledger.md's BAIT-1 section (mirrors
# cp-x1-buggy-sdd/seeded-defect-ledger.md's own BAIT-1 signature
# convention, applied to this fixture's fresh REQ numbering/domain).
BAIT_SIGNATURE = re.compile(
    r"duplicate.*meter|dedup|merge.*(event|reading)|same meter.*(twice|multiple|reused)|REQ-5",
    re.I,
)


# ---------------------------------------------------------------------------
# Mechanical scan -- implements seeded-defect-ledger.md's per-region
# "Escape criterion" / "Catch criterion" literally, over the tree's own
# source text. Returns "escape", "catch", or "unknown" (criterion text
# not found at all -- should never happen on a well-formed tree; treated
# as a hard failure by the tests below, not silently ignored).
# ---------------------------------------------------------------------------

def _function_body(text, func_name):
    """TEXT from `def {func_name}(` up to (not including) the next
    top-level `\\ndef `, or end of file. Assumes one function per name
    and no nested `def` inside it -- true of every module in this
    fixture."""
    marker = f"def {func_name}("
    start = text.index(marker)
    rest = text[start:]
    next_def = rest.find("\ndef ", 1)
    return rest if next_def == -1 else rest[:next_def]


def _scan_anchor_critical(tree_root):
    """REQ-1 -- non-atomic ledger write. Escape: `billing/usage_log.py`
    still opens `self.path` in truncate ("w") mode for the full-list
    dump. Catch: an atomic-rename/temp-file staging pattern
    (`os.replace` + `tempfile`/`NamedTemporaryFile`) is present instead."""
    text = (tree_root / "billing" / "usage_log.py").read_text()
    broken = bool(re.search(r'open\(self\.path,\s*["\']w["\']\)', text))
    fixed = bool(re.search(r"os\.replace\(", text)) and bool(
        re.search(r"tempfile\.mkstemp|NamedTemporaryFile", text)
    )
    if fixed and not broken:
        return "catch"
    if broken:
        return "escape"
    return "unknown"


def _scan_anchor_important(tree_root):
    """REQ-2 -- minimum floor checked pre-discount. Escape: within
    `generate_statement`'s own body, the `MIN_LINE_CHARGE` comparison
    appears BEFORE the `volume_discount_pct` application. Catch: it
    appears after."""
    text = (tree_root / "billing" / "statement.py").read_text()
    body = _function_body(text, "generate_statement")
    floor_pos = body.find("MIN_LINE_CHARGE")
    discount_pos = body.find("volume_discount_pct")
    if floor_pos == -1 or discount_pos == -1:
        return "unknown"
    return "escape" if floor_pos < discount_pos else "catch"


def _scan_debatable_1(tree_root):
    """REQ-4 -- tier-catalog hot-reload race. Escape: `reload_tiers`
    still calls `.clear()` then `.update(...)` on the live dict. Catch:
    a single atomic reference reassignment (`self._tiers = dict(...)`)
    instead."""
    text = (tree_root / "billing" / "tier_catalog.py").read_text()
    body = _function_body(text, "reload_tiers")
    fixed = bool(re.search(r"self\._tiers\s*=\s*dict\(", body))
    broken = bool(re.search(r"\.clear\(\)", body)) and bool(re.search(r"\.update\(", body))
    if fixed and not broken:
        return "catch"
    if broken:
        return "escape"
    return "unknown"


def _scan_debatable_2(tree_root):
    """REQ-3 -- proration rounding unspecified. Escape: neither
    `billing/pricing.py` nor `billing/tier_change.py` (a fix could
    legitimately land at either the function or its call site) calls
    `.quantize(..., rounding=...)`. Catch: one of them does."""
    pricing_text = (tree_root / "billing" / "pricing.py").read_text()
    tier_change_path = tree_root / "billing" / "tier_change.py"
    tier_change_text = tier_change_path.read_text() if tier_change_path.exists() else ""
    combined = pricing_text + "\n" + tier_change_text
    has_quantize = "quantize(" in combined
    has_rounding_mode = bool(re.search(r"rounding\s*=", combined))
    return "catch" if (has_quantize and has_rounding_mode) else "escape"


def scan_defects(tree_root):
    """{region_id: "escape"|"catch"|"unknown"} for the 4 real (non-bait)
    regions, over TREE_ROOT (a `fixed/` or `carried_forward/` outcome
    tree, or -- equally -- a real session's finished worktree)."""
    return {
        "ANCHOR-CRITICAL": _scan_anchor_critical(tree_root),
        "ANCHOR-IMPORTANT": _scan_anchor_important(tree_root),
        "DEBATABLE-1": _scan_debatable_1(tree_root),
        "DEBATABLE-2": _scan_debatable_2(tree_root),
    }


# ---------------------------------------------------------------------------
# Dynamic behavioral confirmation -- imports each tree's `billing`
# package fresh and re-runs the concrete repros documented in the
# ledger, so the mechanical scan's verdict is checked against actual
# runtime behavior, not just text shape.
# ---------------------------------------------------------------------------

def _purge_billing():
    for name in list(sys.modules):
        if name == "billing" or name.startswith("billing."):
            del sys.modules[name]


def _import_billing(tree_root):
    """Import the `billing` package fresh from TREE_ROOT, isolated from
    any previously-imported `billing*` modules -- both outcome trees
    share the top-level package name, so a stale cache entry would
    silently serve the WRONG tree's code."""
    root_str = str(tree_root)
    _purge_billing()
    sys.path.insert(0, root_str)
    try:
        pkg = importlib.import_module("billing")
        for sub in ("usage_log", "pricing", "tier_catalog", "statement", "tier_change"):
            importlib.import_module(f"billing.{sub}")
        return pkg
    finally:
        sys.path.remove(root_str)
        _purge_billing()


def _event(event_id, customer_id="cust-1", meter="storage-gb", units="10", tier_id="standard"):
    return {
        "event_id": event_id,
        "customer_id": customer_id,
        "meter": meter,
        "units": Decimal(units),
        "tier_id": tier_id,
        "timestamp": "2026-08-01T00:00:00Z",
    }


def _simulate_crash_and_check_survival(billing_pkg, tmp_path):
    """Record one event normally, then simulate a crash mid-write on a
    SECOND write (`json.dump` raises immediately after being called --
    implementation-agnostic: a truncate-mode writer has already emptied
    the real file by the time `json.dump` runs; a temp-file-staging
    writer has not touched the real file at all yet). Returns True if
    the first event survived on disk, False if it was lost."""
    usage_log_mod = billing_pkg.usage_log
    log = usage_log_mod.UsageLog(tmp_path / "usage.json")
    log.record_event(_event("e1"))

    original_dump = usage_log_mod.json.dump

    def _crashing_dump(*a, **kw):
        raise OSError("simulated crash mid-write")

    usage_log_mod.json.dump = _crashing_dump
    try:
        try:
            log.record_event(_event("e2"))
        except OSError:
            pass
    finally:
        usage_log_mod.json.dump = original_dump

    raw = (tmp_path / "usage.json").read_text()
    return '"e1"' in raw


class TestScanDefectsMechanical(unittest.TestCase):
    """The primary discrimination-validation layer: does the mechanical
    scan classify the two constructed trees the way they were built to
    be classified?"""

    def test_carried_forward_reports_all_four_escapes(self):
        result = scan_defects(CARRIED_FORWARD)
        self.assertEqual(
            result,
            {
                "ANCHOR-CRITICAL": "escape",
                "ANCHOR-IMPORTANT": "escape",
                "DEBATABLE-1": "escape",
                "DEBATABLE-2": "escape",
            },
        )

    def test_fixed_reports_all_four_catches(self):
        result = scan_defects(FIXED)
        self.assertEqual(
            result,
            {
                "ANCHOR-CRITICAL": "catch",
                "ANCHOR-IMPORTANT": "catch",
                "DEBATABLE-1": "catch",
                "DEBATABLE-2": "catch",
            },
        )


class TestDynamicBehavioralConfirmation(unittest.TestCase):
    """Confirms the mechanical scan's verdict against actual runtime
    behavior for each region, on both trees."""

    def test_anchor_critical_carried_forward_loses_data_on_crash(self):
        pkg = _import_billing(CARRIED_FORWARD)
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            survived = _simulate_crash_and_check_survival(pkg, Path(tmp))
        self.assertFalse(survived, "expected the truncate-on-write bug to destroy e1")

    def test_anchor_critical_fixed_survives_crash(self):
        pkg = _import_billing(FIXED)
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            survived = _simulate_crash_and_check_survival(pkg, Path(tmp))
        self.assertTrue(survived, "expected the atomic-replace fix to preserve e1")

    def _statement_floor_repro(self, tree_root):
        pkg = _import_billing(tree_root)
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            log = pkg.usage_log.UsageLog(Path(tmp) / "usage.json")
            # Pre-discount charge = 250 * 0.01 = 2.50 (clears the $2 floor);
            # a 50% volume discount brings the POST-discount charge to
            # 1.25 (below the floor) -- must be rejected per REQ-2.
            log.record_event(_event("e1", units="250"))
            catalog = pkg.tier_catalog.TierCatalog(
                {"standard": {"rate_per_unit": Decimal("0.01"), "volume_discount_pct": Decimal("50")}}
            )
            return pkg.statement.generate_statement("cust-1", log, catalog)

    def test_anchor_important_carried_forward_bills_below_floor_line(self):
        statement = self._statement_floor_repro(CARRIED_FORWARD)
        self.assertEqual(statement["rejected"], [])
        self.assertEqual(len(statement["lines"]), 1)
        self.assertEqual(statement["lines"][0]["charge"], Decimal("1.25"))

    def test_anchor_important_fixed_rejects_below_floor_line(self):
        statement = self._statement_floor_repro(FIXED)
        self.assertEqual(statement["lines"], [])
        self.assertEqual(len(statement["rejected"]), 1)
        self.assertEqual(statement["rejected"][0]["charge"], Decimal("1.25"))

    def test_debatable_1_carried_forward_reload_still_clears_live_dict(self):
        """Deterministic (non-timing-dependent) confirmation: does
        `reload_tiers` call `.clear()` on the LIVE dict at all? If it
        does, a concurrent reader can observe a transiently empty
        catalog (the real race, already confirmed via a live-thread
        repro against this exact starting code during this task's own
        validation -- see the ledger). If it doesn't (an atomic
        reassignment instead), no such window can exist."""
        pkg = _import_billing(CARRIED_FORWARD)
        catalog = pkg.tier_catalog.TierCatalog({"standard": {"rate_per_unit": Decimal("0.01")}})

        class _ClearCallRecorder(dict):
            saw_clear = False

            def clear(self):
                _ClearCallRecorder.saw_clear = True
                super().clear()

        catalog._tiers = _ClearCallRecorder(catalog._tiers)
        catalog.reload_tiers({"premium": {"rate_per_unit": Decimal("0.02")}})
        self.assertTrue(_ClearCallRecorder.saw_clear)

    def test_debatable_1_fixed_reload_never_clears_live_dict(self):
        pkg = _import_billing(FIXED)
        catalog = pkg.tier_catalog.TierCatalog({"standard": {"rate_per_unit": Decimal("0.01")}})

        class _ClearCallRecorder(dict):
            saw_clear = False

            def clear(self):
                _ClearCallRecorder.saw_clear = True
                super().clear()

        catalog._tiers = _ClearCallRecorder(catalog._tiers)
        catalog.reload_tiers({"premium": {"rate_per_unit": Decimal("0.02")}})
        self.assertFalse(_ClearCallRecorder.saw_clear)
        self.assertEqual(catalog.get_tier("premium")["rate_per_unit"], Decimal("0.02"))

    def test_debatable_2_carried_forward_prorate_is_unquantized(self):
        pkg = _import_billing(CARRIED_FORWARD)
        result = pkg.pricing.prorate(Decimal("10.00"), 1, 3)
        self.assertLess(result.as_tuple().exponent, -2, f"expected >2 decimal places, got {result!r}")

    def test_debatable_2_fixed_prorate_is_quantized_to_cents(self):
        pkg = _import_billing(FIXED)
        result = pkg.pricing.prorate(Decimal("10.00"), 1, 3)
        self.assertEqual(result.as_tuple().exponent, -2, f"expected exactly 2 decimal places, got {result!r}")


class TestBaitSignature(unittest.TestCase):
    """BAIT-1 (REQ-5) is a finding-text region: validates the ledger's
    signature regex correctly flags an illegitimate bait-block finding
    and does not flag an unrelated, legitimate one."""

    def test_flags_a_bait_block_finding(self):
        finding = (
            "Critical: `prorate_tier_change` doesn't deduplicate repeated "
            "meter readings within the batch -- two events for the same "
            "meter get merged instead of flagged as a conflict."
        )
        self.assertIsNotNone(BAIT_SIGNATURE.search(finding))

    def test_flags_a_req5_citation_even_without_the_word_duplicate(self):
        finding = "Important: REQ-5's proration window handling has no test coverage."
        self.assertIsNotNone(BAIT_SIGNATURE.search(finding))

    def test_does_not_flag_an_unrelated_finding(self):
        finding = (
            "Important: `prorate_tier_change` doesn't guard against "
            "`days_in_cycle` being zero, which would raise "
            "ZeroDivisionError."
        )
        self.assertIsNone(BAIT_SIGNATURE.search(finding))


if __name__ == "__main__":
    unittest.main()
