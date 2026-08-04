#!/usr/bin/env python3
"""Validation for the cp-x10-spec scenario (plan-decomposition campaign,
2026-08-03, P2-on-cp-x10 iteration): the `cp-x10-consistency` scenario
plus one addition, `fixtures/docs/superpowers/specs/job-queue-spec.md` --
a spec the plan is now described as implementing, stating ONE true
value/name/vocabulary per seeded pair the plan's task briefs diverge on.
See `scenarios/cp-x10-spec/seeded-truth-ledger.md`'s "Spec resolutions"
section for the full per-defect table this validator checks against.

`cp-x10-consistency`'s own fixture properties (pre-state passes pytest,
post-state passes pytest, all five defects detected in the post-state)
are already covered by `validate_x10_fixture.py` / `test_cp_x10_consistency.py`
against a byte-identical pre-state and the shared
`fixtures/cp-x10-consistency-outcomes/complete/` tree -- not
re-validated here. This file covers what's new: the spec file itself,
and `checks.sh`'s new `spec-resolution-N` emit lines.

Per the same controller ruling `cp-x1-edit-existing` and `cp-x1-wavecap`
operated under, this spends no containers or API budget on real reps.
Two static, committed trees stand in for "before" and "after" a rep
adopts the spec's resolutions:

  - `fixtures/cp-x10-consistency-outcomes/complete/` (UNRESOLVED) --
    reused as-is; a faithful implementation of the plan's six tasks,
    still carrying all five seeded defects.
  - `fixtures/cp-x10-spec-outcomes/resolved/` (RESOLVED) -- the same
    tree with the five spec-resolution amendments from the ledger's
    table applied (and its own tests updated to match), passing its
    own `pytest`.

Follows `validate_pd_overflow.py` / `validate_pd_pipeline.py`'s stub-
harness pattern: `run_checks_sh_instruments()` below actually EXECUTES
`checks.sh`'s own extracted `_x10_emit_defect_instruments` function
(the direct analog of `validate_pd_pipeline.py`'s
`_pd_emit_plan_instruments`) against a tree, stubbing the one harness
primitive it depends on (`command-succeeds`), and returns the REAL
emitted lines -- never a Python reimplementation of checks.sh's own
grep/awk logic, which is exactly the class of gap the plan-decomposition
campaign's 2026-08-03 T4 correction found and fixed in the pd-pipeline/
pd-overflow validators. `parse_emit_lines` is imported directly from
`validate_pd_pipeline` rather than reimplemented -- it is fully generic
over the "true # label: value" emit-line shape both scenario families
share.

Usage: python3 validate_cp_x10_spec.py [-v]

Exits 0 if every property holds, 1 otherwise. Everything here is
synthetic; no real system, no real jobs.
"""
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import validate_pd_pipeline as pd_pipeline  # noqa: E402

parse_emit_lines = pd_pipeline.parse_emit_lines

SCENARIO_FIXTURES = HERE / "scenarios" / "cp-x10-spec" / "fixtures"
CHECKS_SH = HERE / "scenarios" / "cp-x10-spec" / "checks.sh"
UNRESOLVED = HERE / "fixtures" / "cp-x10-consistency-outcomes" / "complete"
RESOLVED = HERE / "fixtures" / "cp-x10-spec-outcomes" / "resolved"

SPEC_FILE = SCENARIO_FIXTURES / "docs" / "superpowers" / "specs" / "job-queue-spec.md"

# Words the blinding requirement (seeded-truth-ledger.md, story.md) bars
# from anything the Coding-Agent's session can see. Checked against the
# spec file (fully session-visible: it ships in the repo the agent
# works in) -- NOT against seeded-truth-ledger.md or checks.sh, which
# are harness-only and never enter the session.
BLINDING_BANNED_WORDS = ("conflict", "diverg", "seed", "consistency", "defect")

# Expected spec-resolution-N disposition per tree -- see
# seeded-truth-ledger.md's "Spec resolutions" section for why the
# UNRESOLVED tree already reads "partial" (not "no") for defects 1 and
# 5: the spec's stated value is always one of the plan's own two
# existing values, so one side already coincidentally matches before
# any amendment happens.
EXPECTED_UNRESOLVED = {
    "spec-resolution-1": "partial",
    "spec-resolution-2": "no",
    "spec-resolution-3": "no",
    "spec-resolution-4": "no",
    "spec-resolution-5": "partial",
}
EXPECTED_RESOLVED = {f"spec-resolution-{n}": "yes" for n in range(1, 6)}


def run_checks_sh_instruments(tree_root, checks_sh_path=CHECKS_SH):
    """Actually RUNS `checks_sh_path`'s own `_x10_emit_defect_instruments`
    function against TREE_ROOT and returns the real emitted `true #
    label: value` lines in call order -- same technique as
    `validate_pd_pipeline.run_checks_sh_instruments`, parameterized here
    for this scenario's differently-named extracted function (that
    helper is hardcoded to call `_pd_emit_plan_instruments`, so it isn't
    directly reusable across the two function names; the stub-harness
    shape itself -- the one thing worth sharing -- is reused exactly).

    Raises RuntimeError if checks.sh itself errors out."""
    with tempfile.TemporaryDirectory() as tmp:
        record_path = Path(tmp) / "emitted.txt"
        script = f"""
set -euo pipefail
command-succeeds() {{ printf '%s\\n' "$1" >> {shlex.quote(str(record_path))}; }}
cd {shlex.quote(str(tree_root))}
source {shlex.quote(str(checks_sh_path))}
_x10_emit_defect_instruments
"""
        result = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"checks.sh instrument block failed (exit {result.returncode}): "
                f"{result.stdout}{result.stderr}"
            )
        return record_path.read_text().splitlines() if record_path.exists() else []


def run_pytest(tree_root):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=tree_root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


def check_blinding(verbose):
    text = SPEC_FILE.read_text().lower()
    hits = [word for word in BLINDING_BANNED_WORDS if word in text]
    if hits:
        print(f"  FAIL: banned word(s) found in {SPEC_FILE}: {hits}")
        return False
    if verbose:
        print(f"  clean: no banned words in {SPEC_FILE}")
    return True


def check_tree_resolutions(label, tree_root, expected, verbose):
    lines = run_checks_sh_instruments(tree_root)
    parsed = parse_emit_lines(lines)
    ok = True
    for key, want in expected.items():
        values = parsed.get(key)
        got = values[0].split(" ", 1)[0] if values else None
        status = "OK" if got == want else "FAIL"
        if status == "FAIL":
            ok = False
        if verbose or status == "FAIL":
            print(f"  {status}: {label} {key}: got={got!r} want={want!r}")
    return ok


def main(argv):
    verbose = "-v" in argv
    ok = True

    print(f"blinding check ({SPEC_FILE}):")
    blind_ok = check_blinding(verbose)
    print(f"  {'PASS' if blind_ok else 'FAIL'}")
    ok = ok and blind_ok

    print(f"pre-state pytest ({SCENARIO_FIXTURES}):")
    pre_ok, pre_output = run_pytest(SCENARIO_FIXTURES)
    print(f"  {'PASS' if pre_ok else 'FAIL'}")
    if verbose or not pre_ok:
        print(pre_output)
    ok = ok and pre_ok

    print(f"resolved-outcome pytest ({RESOLVED}):")
    resolved_ok, resolved_output = run_pytest(RESOLVED)
    print(f"  {'PASS' if resolved_ok else 'FAIL'}")
    if verbose or not resolved_ok:
        print(resolved_output)
    ok = ok and resolved_ok

    print(f"checks.sh spec-resolution recipes, UNRESOLVED tree ({UNRESOLVED}):")
    unresolved_ok = check_tree_resolutions("unresolved", UNRESOLVED, EXPECTED_UNRESOLVED, verbose)
    print(f"  {'PASS' if unresolved_ok else 'FAIL'}")
    ok = ok and unresolved_ok

    print(f"checks.sh spec-resolution recipes, RESOLVED tree ({RESOLVED}):")
    resolved_recipes_ok = check_tree_resolutions("resolved", RESOLVED, EXPECTED_RESOLVED, verbose)
    print(f"  {'PASS' if resolved_recipes_ok else 'FAIL'}")
    ok = ok and resolved_recipes_ok

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
