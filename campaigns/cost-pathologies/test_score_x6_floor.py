"""Tests for score_x6_floor.py (X6, Task 2 of the cost-pathologies SDD
plan). Fixtures are synthetic, hand-built rollout JSONL under
fixtures/x6/ -- no real session content.

Fixture layout (fixtures/x6/):
  - parent.jsonl -- three spawn_agent calls: call_A (task1_small_edit) ->
    thread-cccc3333, call_B (task2_big_feature) -> thread-dddd4444,
    call_C (task3_no_token_events) -> thread-eeee5555.
  - rollout-thread-cccc3333.jsonl -- two token_count events, LAST
    cumulative total_token_usage.total_tokens=8000; final_answer message
    "Done." (5 chars -> 5//4=1 estimated token of useful output).
  - rollout-thread-dddd4444.jsonl -- same token_count shape, LAST
    cumulative total=8000; final_answer message "Implemented the full
    feature end to end with tests." (51 chars -> 51//4=12). Same total
    cost as A, much more useful output -- illustrates the floor-tax
    pathology (A's floor_ratio should be far worse than B's despite
    identical total_tokens).
  - rollout-thread-eeee5555.jsonl -- NO token_count events at all (tests
    the total_tokens=None / floor_ratio=None fallback), but a real
    final_answer ("Some output here nonetheless.", 30 chars -> 30//4=7).
"""
import os
import unittest

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "x6")
PARENT = os.path.join(FIXTURES, "parent.jsonl")
CHILD_A = os.path.join(FIXTURES, "rollout-thread-cccc3333.jsonl")
CHILD_B = os.path.join(FIXTURES, "rollout-thread-dddd4444.jsonl")
CHILD_C = os.path.join(FIXTURES, "rollout-thread-eeee5555.jsonl")
ALL_PATHS = [PARENT, CHILD_A, CHILD_B, CHILD_C]


class TestDispatchFloor(unittest.TestCase):
    def test_module_importable_and_all_dispatches_found(self):
        import score_x6_floor as sx6
        result = sx6.dispatch_floor(ALL_PATHS)
        task_names = {d["task_name"] for d in result["dispatches"]}
        self.assertEqual(task_names, {"task1_small_edit", "task2_big_feature",
                                       "task3_no_token_events"})

    def test_cumulative_token_count_uses_last_event_not_sum(self):
        # LAST token_count event's total_token_usage.total_tokens=8000, not
        # the sum of both events' totals (5000+8000=13000) -- see module
        # docstring's cumulative-vs-exclusive note.
        import score_x6_floor as sx6
        result = sx6.dispatch_floor(ALL_PATHS)
        a = next(d for d in result["dispatches"] if d["task_name"] == "task1_small_edit")
        self.assertEqual(a["total_tokens"], 8000)

    def test_useful_output_tokens_is_chars_over_4_of_final_answer(self):
        import score_x6_floor as sx6
        result = sx6.dispatch_floor(ALL_PATHS)
        a = next(d for d in result["dispatches"] if d["task_name"] == "task1_small_edit")
        b = next(d for d in result["dispatches"] if d["task_name"] == "task2_big_feature")
        self.assertEqual(a["useful_output_tokens"], 1)   # len("Done.")=5 -> 5//4
        self.assertEqual(b["useful_output_tokens"], 12)  # 51 chars -> 51//4

    def test_floor_ratio_is_total_over_useful(self):
        import score_x6_floor as sx6
        result = sx6.dispatch_floor(ALL_PATHS)
        a = next(d for d in result["dispatches"] if d["task_name"] == "task1_small_edit")
        b = next(d for d in result["dispatches"] if d["task_name"] == "task2_big_feature")
        self.assertAlmostEqual(a["floor_ratio"], 8000 / 1, places=6)
        self.assertAlmostEqual(b["floor_ratio"], 8000 / 12, places=6)
        # Same total cost, wildly different floor tax: the small edit's
        # ratio is 12x worse than the big feature's (useful_output_tokens
        # 1 vs 12, same total_tokens=8000).
        self.assertAlmostEqual(a["floor_ratio"] / b["floor_ratio"], 12, places=6)

    def test_missing_token_count_events_gives_none_total_and_ratio(self):
        import score_x6_floor as sx6
        result = sx6.dispatch_floor(ALL_PATHS)
        c = next(d for d in result["dispatches"] if d["task_name"] == "task3_no_token_events")
        self.assertIsNone(c["total_tokens"])
        self.assertEqual(c["useful_output_tokens"], 7)  # 30 chars -> 30//4
        self.assertIsNone(c["floor_ratio"])

    def test_no_spawns_returns_empty_dispatches(self):
        import score_x6_floor as sx6
        result = sx6.dispatch_floor([CHILD_A])  # a leaf with no spawn_agent calls of its own
        self.assertEqual(result, {"dispatches": []})


if __name__ == "__main__":
    unittest.main()
