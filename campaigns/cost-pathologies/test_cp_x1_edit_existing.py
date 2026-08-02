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
# Fix round 1 (task-5-review.md's Important finding 2): single-file
# variants exercising the SECOND independently-valid catch shape the
# ledger documents for these two regions (append-only writes;
# lock-guarded clear()+update()), distinct from the shape `fixed/`
# happens to use (atomic-replace; atomic reference swap).
VARIANT_ANCHOR_CRITICAL_APPEND_ONLY = OUTCOMES / "variant-anchor-critical-append-only"
VARIANT_DEBATABLE_1_LOCK_GUARDED = OUTCOMES / "variant-debatable1-lock-guarded"
# Fix round 2 (task-5-review.md's Re-review round 1 new Important
# finding): the SAME lock-guarded catch shape, differently-named guard
# attributes -- `_LOCK_GUARD_RE` originally only recognized names
# containing the substring "lock"; these three exercise the other
# naming families the broadened recognizer must also catch.
VARIANT_DEBATABLE_1_MUTEX_GUARDED = OUTCOMES / "variant-debatable1-mutex-guarded"
VARIANT_DEBATABLE_1_GUARD_NAMED = OUTCOMES / "variant-debatable1-guard-named"
VARIANT_DEBATABLE_1_SEMAPHORE_GUARDED = OUTCOMES / "variant-debatable1-semaphore-guarded"

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
    dump. Catch: the ledger documents TWO independently valid shapes --
    an atomic-rename/temp-file staging pattern (`os.replace` +
    `tempfile`/`NamedTemporaryFile`), OR append-only per-event writes
    (`open(self.path, "a")`) that never truncate existing content.
    Fix round 1 (task-5-review.md's Important finding 2): the original
    version only recognized the first shape, scoring the second
    "unknown" instead of "catch" -- see
    `VARIANT_ANCHOR_CRITICAL_APPEND_ONLY`'s test."""
    text = (tree_root / "billing" / "usage_log.py").read_text()
    broken = bool(re.search(r'open\(self\.path,\s*["\']w["\']\)', text))
    atomic_replace = bool(re.search(r"os\.replace\(", text)) and bool(
        re.search(r"tempfile\.mkstemp|NamedTemporaryFile", text)
    )
    append_only = bool(re.search(r'open\(self\.path,\s*["\']a["\']\)', text))
    if broken:
        return "escape"
    if atomic_replace or append_only:
        return "catch"
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


# Recognized guard-attribute naming families, fix round 2
# (task-5-review.md's Re-review round 1 new Important finding): round 1
# only recognized attribute names containing the substring "lock"
# (`self._lock`, `self._catalog_lock`) -- a real, correctly guarded fix
# named `self._mutex` (or `self._guard`, `self._sem`/`self._semaphore`)
# scored "escape", the WRONG classification, not even "unknown".
# Broadened to the common synchronization-primitive naming families:
# lock, mutex, sem/semaphore, guard. RESIDUAL LIMITATION, disclosed
# rather than silently left (see seeded-defect-ledger.md's DEBATABLE-1
# entry for the same caveat): an attribute name OUTSIDE these four
# families (e.g. `self._critical_section`, a bare module-level lock
# never accessed via `self.`, or a non-`threading` synchronization
# primitive such as `asyncio`'s or `multiprocessing`'s) still scores
# "escape" even if it correctly closes the race -- a calibrated
# heuristic over the shapes actually specified, not a guarantee of full
# recall over every conceivable correct implementation. A future
# battery's hand-verification pass should check that class manually
# rather than trust this scan's "escape" verdict at face value.
_LOCK_GUARD_RE = re.compile(
    r"with\s+self\.\w*(?:lock|mutex|sem(?:aphore)?|guard)\w*\s*:"
    r"|self\.\w*(?:lock|mutex|sem(?:aphore)?|guard)\w*\.acquire\(",
    re.I,
)


def _scan_debatable_1(tree_root):
    """REQ-4 -- tier-catalog hot-reload race. Escape: `reload_tiers`
    still calls `.clear()` then `.update(...)` on the live dict, with no
    RECOGNIZED guard protecting it. Catch: the ledger documents TWO
    independently valid shapes -- a single atomic reference reassignment
    (`self._tiers = dict(...)`), OR a lock/mutex/semaphore/guard now
    protecting BOTH `reload_tiers` and `get_tier` (still textually
    `.clear()`+`.update()` on the live dict, which alone is
    indistinguishable from the broken shape -- the guard on both sides
    is what actually closes the race). Fix round 1 (task-5-review.md's
    Important finding 2): the original version only recognized the
    atomic-swap shape, scoring a lock-guarded fix "escape" -- the WRONG
    classification -- since `.clear()`/`.update()` are still present.
    Fix round 2 (Re-review round 1's new Important finding): the round-1
    fix's guard recognizer (`_LOCK_GUARD_RE`) only matched attribute
    names containing "lock" -- see that regex's own comment for the
    naming families now recognized and the RESIDUAL naming-convention
    limitation this function still carries. See
    `VARIANT_DEBATABLE_1_LOCK_GUARDED`/`_MUTEX_GUARDED`/`_GUARD_NAMED`/
    `_SEMAPHORE_GUARDED`'s tests."""
    text = (tree_root / "billing" / "tier_catalog.py").read_text()
    reload_body = _function_body(text, "reload_tiers")
    atomic_swap = bool(re.search(r"self\._tiers\s*=\s*dict\(", reload_body))
    clear_then_update = bool(re.search(r"\.clear\(\)", reload_body)) and bool(
        re.search(r"\.update\(", reload_body)
    )
    reload_lock_guarded = bool(_LOCK_GUARD_RE.search(reload_body))
    get_tier_lock_guarded = False
    if "def get_tier(" in text:
        get_tier_lock_guarded = bool(_LOCK_GUARD_RE.search(_function_body(text, "get_tier")))

    if atomic_swap and not clear_then_update:
        return "catch"
    if clear_then_update and reload_lock_guarded and get_tier_lock_guarded:
        return "catch"
    if clear_then_update:
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


def _import_single(tree_root, dotted_name):
    """Like `_import_billing()` but for a single-file VARIANT tree that
    only ships `billing/__init__.py` plus the ONE module under test
    (e.g. `billing.usage_log`) -- the fix-round-1 catch-shape variants
    don't need a full 5-module package, since neither `usage_log.py` nor
    `tier_catalog.py` imports any billing sibling."""
    root_str = str(tree_root)
    _purge_billing()
    sys.path.insert(0, root_str)
    try:
        return importlib.import_module(dotted_name)
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


def _simulate_crash_and_check_survival(usage_log_mod, tmp_path):
    """Record one event normally, then simulate a crash mid-write on a
    SECOND write (`json.dump`/`json.dumps` raise immediately when
    called -- implementation-agnostic across all three catch/escape
    shapes this module exercises: a truncate-mode writer has already
    emptied the real file by the time serialization runs; a temp-file-
    staging writer has not touched the real file at all yet; an
    append-only writer serializes BEFORE ever opening the file, so
    `f.write` never runs and append mode never truncates regardless).
    Returns True if the first event survived on disk, False if it was
    lost. USAGE_LOG_MOD is the `billing.usage_log` module itself (not
    the `billing` package), so this also works against the single-file
    variant trees `_import_single()` loads."""
    log = usage_log_mod.UsageLog(tmp_path / "usage.json")
    log.record_event(_event("e1"))

    original_dump = usage_log_mod.json.dump
    original_dumps = usage_log_mod.json.dumps

    def _crashing(*a, **kw):
        raise OSError("simulated crash mid-write")

    usage_log_mod.json.dump = _crashing
    usage_log_mod.json.dumps = _crashing
    try:
        try:
            log.record_event(_event("e2"))
        except OSError:
            pass
    finally:
        usage_log_mod.json.dump = original_dump
        usage_log_mod.json.dumps = original_dumps

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

    def test_anchor_critical_append_only_variant_is_caught(self):
        """Fix round 1 (task-5-review.md's Important finding 2): the
        ledger documents append-only writes as an INDEPENDENTLY valid
        catch shape for ANCHOR-CRITICAL, distinct from the temp-file/
        os.replace shape `fixed/` happens to use. Before the fix,
        `_scan_anchor_critical()` returned "unknown" for this shape
        (neither the truncate-mode nor the temp-file pattern matches) --
        this test is written to fail against that gap first."""
        self.assertEqual(_scan_anchor_critical(VARIANT_ANCHOR_CRITICAL_APPEND_ONLY), "catch")

    def test_debatable_1_lock_guarded_variant_is_caught(self):
        """Fix round 1 (task-5-review.md's Important finding 2): the
        ledger documents a lock guarding both `reload_tiers` and
        `get_tier` as an INDEPENDENTLY valid catch shape for DEBATABLE-1,
        distinct from the atomic-swap shape `fixed/` happens to use.
        Before the fix, `_scan_debatable_1()` returned "escape" for this
        shape (`.clear()`/`.update()` are still textually present) --
        the WRONG classification, not even "unknown" -- this test is
        written to fail against that gap first."""
        self.assertEqual(_scan_debatable_1(VARIANT_DEBATABLE_1_LOCK_GUARDED), "catch")

    def test_debatable_1_mutex_named_variant_is_caught(self):
        """Fix round 2 (task-5-review.md's Re-review round 1 new
        Important finding): the SAME lock-guarded catch shape, guard
        attribute named `self._mutex` instead of `self._lock` -- a real,
        plausible naming choice ("mutex" is a synonym for "lock").
        Before this fix, `_LOCK_GUARD_RE` only recognized attribute
        names containing the substring "lock", so this scored
        `"escape"` -- the WRONG classification -- exactly the
        re-reviewer's own adversarial probe. Written to fail against
        that gap first."""
        self.assertEqual(_scan_debatable_1(VARIANT_DEBATABLE_1_MUTEX_GUARDED), "catch")

    def test_debatable_1_guard_named_variant_is_caught(self):
        """Fix round 2: a second naming family beyond "mutex" -- guard
        attribute named `self._guard`. Same pre-fix "escape"
        misclassification; written to fail against that gap first."""
        self.assertEqual(_scan_debatable_1(VARIANT_DEBATABLE_1_GUARD_NAMED), "catch")

    def test_debatable_1_semaphore_named_variant_is_caught(self):
        """Fix round 2: a third naming family -- a binary
        `threading.Semaphore(1)` named `self._sem`. Same pre-fix
        "escape" misclassification; written to fail against that gap
        first."""
        self.assertEqual(_scan_debatable_1(VARIANT_DEBATABLE_1_SEMAPHORE_GUARDED), "catch")


class TestDynamicBehavioralConfirmation(unittest.TestCase):
    """Confirms the mechanical scan's verdict against actual runtime
    behavior for each region, on both trees."""

    def test_anchor_critical_carried_forward_loses_data_on_crash(self):
        pkg = _import_billing(CARRIED_FORWARD)
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            survived = _simulate_crash_and_check_survival(pkg.usage_log, Path(tmp))
        self.assertFalse(survived, "expected the truncate-on-write bug to destroy e1")

    def test_anchor_critical_fixed_survives_crash(self):
        pkg = _import_billing(FIXED)
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            survived = _simulate_crash_and_check_survival(pkg.usage_log, Path(tmp))
        self.assertTrue(survived, "expected the atomic-replace fix to preserve e1")

    def test_anchor_critical_append_only_variant_survives_crash(self):
        """The SECOND independently-valid catch shape (append-only
        writes) -- fix round 1 / task-5-review.md's Important finding 2."""
        mod = _import_single(VARIANT_ANCHOR_CRITICAL_APPEND_ONLY, "billing.usage_log")
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            survived = _simulate_crash_and_check_survival(mod, Path(tmp))
        self.assertTrue(survived, "expected the append-only shape to preserve e1")

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

    def test_debatable_1_lock_guarded_variant_never_raises_keyerror_under_concurrent_reload(self):
        """Fix round 1: the SECOND independently-valid catch shape (a
        lock guarding both `reload_tiers` and `get_tier`), confirmed
        with a REAL background thread -- deterministic, not
        timing-dependent, because a lock serializes access rather than
        merely narrowing a race window: the reader either runs before
        `reload_tiers` acquires the lock (sees the old, fully-populated
        dict) or after it releases (sees the new one), never during. A
        `dict` subclass whose `.clear()` sleeps widens the window the
        same way the ledger's own carried_forward repro does, so this
        test would flake/fail against an unguarded implementation but
        cannot against a correctly lock-guarded one."""
        mod = _import_single(VARIANT_DEBATABLE_1_LOCK_GUARDED, "billing.tier_catalog")
        import threading
        import time

        catalog = mod.TierCatalog(
            {"standard": {"rate_per_unit": Decimal("0.01")}, "premium": {"rate_per_unit": Decimal("0.02")}}
        )

        class _SlowClearDict(dict):
            def clear(self):
                super().clear()
                time.sleep(0.05)

        catalog._tiers = _SlowClearDict(catalog._tiers)
        observed = []

        def reader():
            time.sleep(0.01)
            try:
                catalog.get_tier("standard")  # present both before AND after reload
                observed.append("ok")
            except KeyError:
                observed.append("KeyError-transiently-empty")

        t = threading.Thread(target=reader)
        t.start()
        catalog.reload_tiers({"standard": {"rate_per_unit": Decimal("0.03")}, "enterprise": {"rate_per_unit": Decimal("0.04")}})
        t.join()

        self.assertEqual(observed, ["ok"])

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
