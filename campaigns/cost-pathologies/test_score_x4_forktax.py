"""Tests for score_x4_forktax.py (X4, Task 2 of the cost-pathologies SDD
plan). Fixtures are synthetic, hand-built rollout JSONL under
fixtures/x4/ -- no real session content. Expected byte counts below were
read directly off the committed fixture files with `wc -c`/`awk`, not
computed by calling the scorer -- see the comment above each assertion
for the exact derivation.

Fixture layout (fixtures/x4/):
  - parent.jsonl -- 3 filler `note` records (payload {"n": 0|1|2}), then a
    spawn_agent call_A (fork_turns="all") linked via sub_agent_activity to
    thread-aaaa1111, then a second spawn_agent call_B (fork_turns="none")
    linked to thread-bbbb2222.
  - rollout-thread-aaaa1111-full.jsonl -- the "all"-fork child. Its own
    header record, then 3 records byte-identical (type+payload, ignoring
    timestamp) to parent.jsonl's 3 filler records IN ORDER, then 3 wholly
    new records. Models the corpus-observed "full-history replay before
    new turns" shape (see score_x4_forktax.py's module docstring for the
    real rollout pair this was validated against).
  - rollout-thread-bbbb2222-iso.jsonl -- the "none"-fork child. Zero
    records shared with parent.jsonl -- models a genuinely isolated fork.
"""
import os
import unittest

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "x4")


class TestForkStats(unittest.TestCase):
    def test_module_importable_and_children_resolved(self):
        import score_x4_forktax as sx4
        result = sx4.fork_stats(FIXTURES)
        self.assertEqual(len(result["children"]), 2)
        by_thread = {c["child_rollout"]: c for c in result["children"]}
        self.assertIn("rollout-thread-aaaa1111-full.jsonl", by_thread)
        self.assertIn("rollout-thread-bbbb2222-iso.jsonl", by_thread)

    def test_full_fork_byte_ratio(self):
        # parent.jsonl is 1168 bytes (wc -c); the full-fork child is 574
        # bytes (wc -c) -> 574/1168.
        import score_x4_forktax as sx4
        result = sx4.fork_stats(FIXTURES)
        full = next(c for c in result["children"]
                    if c["child_rollout"] == "rollout-thread-aaaa1111-full.jsonl")
        self.assertEqual(full["parent_bytes"], 1168)
        self.assertEqual(full["child_bytes"], 574)
        self.assertAlmostEqual(full["byte_ratio"], 574 / 1168, places=6)

    def test_full_fork_inherited_prefix_duplicate_ratio(self):
        # The full-fork child's lines 2-4 (1-indexed; 0-indexed 1-3) are
        # byte-identical replays of parent.jsonl's first 3 records, sized
        # 79+79+79=237 bytes (awk length($0)+1 on the fixture) out of the
        # child's total 574 bytes.
        import score_x4_forktax as sx4
        result = sx4.fork_stats(FIXTURES)
        full = next(c for c in result["children"]
                    if c["child_rollout"] == "rollout-thread-aaaa1111-full.jsonl")
        self.assertAlmostEqual(full["inherited_prefix_duplicate_ratio"], 237 / 574, places=6)

    def test_isolated_fork_has_zero_duplicate_ratio(self):
        import score_x4_forktax as sx4
        result = sx4.fork_stats(FIXTURES)
        iso = next(c for c in result["children"]
                   if c["child_rollout"] == "rollout-thread-bbbb2222-iso.jsonl")
        self.assertEqual(iso["parent_bytes"], 1168)
        self.assertEqual(iso["child_bytes"], 262)
        self.assertAlmostEqual(iso["byte_ratio"], 262 / 1168, places=6)
        self.assertEqual(iso["inherited_prefix_duplicate_ratio"], 0.0)

    def test_aggregate_means(self):
        import score_x4_forktax as sx4
        result = sx4.fork_stats(FIXTURES)
        expected_byte_ratio = ((574 / 1168) + (262 / 1168)) / 2
        expected_dup_ratio = ((237 / 574) + 0.0) / 2
        self.assertAlmostEqual(result["child_parent_byte_ratio"], expected_byte_ratio, places=6)
        self.assertAlmostEqual(result["inherited_prefix_duplicate_ratio"], expected_dup_ratio, places=6)

    def test_empty_dir_returns_zeroed_aggregate(self):
        import score_x4_forktax as sx4
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            result = sx4.fork_stats(tmp)
            self.assertEqual(result, {
                "children": [],
                "child_parent_byte_ratio": 0.0,
                "inherited_prefix_duplicate_ratio": 0.0,
            })


if __name__ == "__main__":
    unittest.main()
