"""Tests for the queue-execution campaign's Task 3 (item 14) dot-directory
glob audit: every `glob`/`rglob`/`Path.glob('**...')` call in
`campaigns/cost-pathologies/*.py` was audited for Python's documented
`glob.glob(pattern, recursive=True)` behavior -- a `**` wildcard segment
silently refuses to descend into a dot-prefixed directory (`.worktrees`,
`.superpowers`, `.codex`) UNLESS that segment is a LITERAL, non-wildcard
component of the pattern itself. This bug class was first disclosed in
`task9_extract_signals.py find_ledger()` (fixed with `os.walk`,
`logs/2026-07-31-cost-pathologies.md`) and independently re-hit by
`score_x4_forktax.fork_stats()` over a battery rep root (same log, Task 12
entry) -- `task9_extract_signals.root_rollout()`/`find_verdict()`,
`task10_extract_signals.root_rollout()`/`find_verdict()`, and
`task12_measure_forktax.resolve_session_dirs()` all carried the SAME
residual defect in their own leading `**` segment (the one BEFORE the
first literal dot-component), confirmed by direct `glob.glob` testing
before this fix (see this task's report). `bait_signature_in_tree()`
(score_x3_rider.py) and the two `x1*-review-verify.py` `ANSWERS.glob(...)`
call sites are single-level, non-recursive globs against non-dot-prefixed
filenames with literal path components -- audited, no dot-directory
traversal risk, left unchanged.

Every test below builds a fixture tree with `.worktrees`, `.superpowers`,
and `.codex` layers (item 14's explicit fixture requirement) and would
FAIL against the pre-fix `glob.glob(..., recursive=True)` call at each
site (verified manually with the standalone `glob` reproduction in this
task's report before writing the fix).
"""
import os
import tempfile
import unittest


def _build_dot_dir_tree(root, container="wt1"):
    """<root>/.worktrees/<container>/home/.codex/sessions/2026/07/
    rollout-<ts>-abc.jsonl (one record, has a "timestamp" so
    root_rollout()'s first_ts() sort works) plus a sibling
    rollout-<ts>-def.jsonl (second thread), and
    <root>/.superpowers/sdd/some-plan/verdict.json (valid empty JSON
    object) -- both dot-directory layers item 14 names, both nested two
    levels deep (.worktrees/<container>/... and .superpowers/sdd/...).
    Returns (rollout_path, second_rollout_path, verdict_path)."""
    sessions_dir = os.path.join(root, ".worktrees", container, "home",
                                 ".codex", "sessions", "2026", "07")
    os.makedirs(sessions_dir)
    rollout_a = os.path.join(sessions_dir, "rollout-2026-07-01T00-00-00-abc.jsonl")
    with open(rollout_a, "w") as f:
        f.write('{"timestamp": "2026-07-01T00:00:00", "type": "session_meta"}\n')
    rollout_b = os.path.join(sessions_dir, "rollout-2026-07-01T00-05-00-def.jsonl")
    with open(rollout_b, "w") as f:
        f.write('{"timestamp": "2026-07-01T00:05:00", "type": "session_meta"}\n')

    sdd_dir = os.path.join(root, ".superpowers", "sdd", "some-plan")
    os.makedirs(sdd_dir)
    verdict_path = os.path.join(sdd_dir, "verdict.json")
    with open(verdict_path, "w") as f:
        f.write('{"economics": {"total_est_cost_usd": 1.23}, "final": "APPROVED"}')

    return rollout_a, rollout_b, verdict_path


class TestFindFilesDotSafe(unittest.TestCase):
    """scorer_common.find_files -- the shared helper item 14's fixes route
    through."""

    def test_finds_files_under_nested_dot_directories(self):
        import scorer_common as sc
        with tempfile.TemporaryDirectory() as d:
            rollout_a, rollout_b, verdict_path = _build_dot_dir_tree(d)
            hits = sc.find_files(d, "rollout-*.jsonl")
            self.assertEqual(sorted(hits), sorted([rollout_a, rollout_b]))
            self.assertEqual(sc.find_files(d, "verdict.json"), [verdict_path])

    def test_path_contains_filters_like_a_literal_glob_component_would(self):
        import scorer_common as sc
        with tempfile.TemporaryDirectory() as d:
            rollout_a, rollout_b, _ = _build_dot_dir_tree(d)
            # A decoy rollout-shaped file OUTSIDE home/.codex/sessions --
            # path_contains must exclude it, same specificity the original
            # literal-component glob pattern had.
            decoy_dir = os.path.join(d, "some-other-dir")
            os.makedirs(decoy_dir)
            decoy = os.path.join(decoy_dir, "rollout-2026-01-01T00-00-00-decoy.jsonl")
            open(decoy, "w").close()

            hits = sc.find_files(d, "rollout-*.jsonl",
                                  path_contains=os.path.join("home", ".codex", "sessions"))
            self.assertEqual(sorted(hits), sorted([rollout_a, rollout_b]))
            self.assertNotIn(decoy, hits)

    def test_reproduces_glob_recursive_blind_spot_for_contrast(self):
        # Documents WHY find_files exists: glob.glob(..., recursive=True)
        # returns nothing for the exact same tree.
        import glob
        with tempfile.TemporaryDirectory() as d:
            _build_dot_dir_tree(d)
            pattern = os.path.join(d, "**", "rollout-*.jsonl")
            self.assertEqual(glob.glob(pattern, recursive=True), [])


class TestScoreX4ForktaxFindRollouts(unittest.TestCase):
    """score_x4_forktax.find_rollouts() -- the exact call site documented
    in logs/2026-07-31-cost-pathologies.md's Task 12 entry as silently
    returning 0 children when fork_stats() is pointed at a battery rep
    root with a `.worktrees`-shaped path above `home/.codex/sessions`."""

    def test_finds_rollouts_under_a_worktrees_layer(self):
        import score_x4_forktax as x4
        with tempfile.TemporaryDirectory() as d:
            rollout_a, rollout_b, _ = _build_dot_dir_tree(d)
            hits = x4.find_rollouts(d)
            self.assertEqual(hits, sorted([rollout_a, rollout_b]))


class TestTask9ExtractSignalsDotSafe(unittest.TestCase):
    def test_root_rollout_under_worktrees_layer(self):
        import task9_extract_signals as t9
        with tempfile.TemporaryDirectory() as d:
            rollout_a, rollout_b, _ = _build_dot_dir_tree(d)
            root_path, all_rollouts = t9.root_rollout(d)
            self.assertEqual(root_path, rollout_a)  # earlier timestamp
            self.assertEqual(sorted(all_rollouts), sorted([rollout_a, rollout_b]))

    def test_find_verdict_under_superpowers_sdd_layer(self):
        import task9_extract_signals as t9
        with tempfile.TemporaryDirectory() as d:
            _, _, verdict_path = _build_dot_dir_tree(d)
            self.assertEqual(t9.find_verdict(d), verdict_path)


class TestTask10ExtractSignalsDotSafe(unittest.TestCase):
    def test_root_rollout_under_worktrees_layer(self):
        import task10_extract_signals as t10
        with tempfile.TemporaryDirectory() as d:
            rollout_a, rollout_b, _ = _build_dot_dir_tree(d)
            root_path, all_rollouts = t10.root_rollout(d)
            self.assertEqual(root_path, rollout_a)
            self.assertEqual(sorted(all_rollouts), sorted([rollout_a, rollout_b]))

    def test_find_verdict_under_superpowers_sdd_layer(self):
        import task10_extract_signals as t10
        with tempfile.TemporaryDirectory() as d:
            _, _, verdict_path = _build_dot_dir_tree(d)
            self.assertEqual(t10.find_verdict(d), verdict_path)


class TestTask12ResolveSessionDirs(unittest.TestCase):
    """task12_measure_forktax.resolve_session_dirs() -- this wrapper's own
    "literal .codex component" workaround still had a leading `**` before
    "home" that a `.worktrees`-shaped rep-root path defeats (confirmed by
    direct glob.glob reproduction, see this task's report)."""

    def test_resolves_session_dir_under_worktrees_layer(self):
        import task12_measure_forktax as t12
        with tempfile.TemporaryDirectory() as d:
            _build_dot_dir_tree(d)
            expected = os.path.join(d, ".worktrees", "wt1", "home", ".codex", "sessions")
            self.assertEqual(t12.resolve_session_dirs(d), [expected])

    def test_no_session_dir_when_none_present(self):
        import task12_measure_forktax as t12
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".worktrees", "wt1", "home"))
            self.assertEqual(t12.resolve_session_dirs(d), [])


if __name__ == "__main__":
    unittest.main()
