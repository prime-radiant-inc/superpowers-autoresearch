import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_grader import load_grader
from fixture_workdir import make_baseline_workdir

grader = load_grader("twenty-edits")


def _fix_all(wd):
    for i in range(1, 21):
        path = os.path.join(wd, "modules", f"mod{i:02d}.py")
        with open(path) as f:
            content = f.read()
        with open(path, "w") as f:
            f.write(content.replace("return 30", "return 60"))


class TestTwentyEditsGrader(unittest.TestCase):
    def test_all_twenty_fixed_passes(self):
        wd = make_baseline_workdir("twenty-edits", prefix="cml-te-wd.")
        _fix_all(wd)
        out = grader.grade("unused.jsonl", wd)
        self.assertTrue(out["pass_signal"])
        self.assertEqual(out["details"]["n_fixed"], 20)
        self.assertEqual(out["details"]["not_fixed"], [])

    def test_partial_completion_fails(self):
        wd = make_baseline_workdir("twenty-edits", prefix="cml-te-wd.")
        for i in range(1, 13):  # only fix 12 of 20
            path = os.path.join(wd, "modules", f"mod{i:02d}.py")
            with open(path) as f:
                content = f.read()
            with open(path, "w") as f:
                f.write(content.replace("return 30", "return 60"))
        out = grader.grade("unused.jsonl", wd)
        self.assertFalse(out["pass_signal"])
        self.assertEqual(out["details"]["n_fixed"], 12)
        self.assertEqual(len(out["details"]["not_fixed"]), 8)

    def test_corrupted_file_fails_even_if_rest_done(self):
        wd = make_baseline_workdir("twenty-edits", prefix="cml-te-wd.")
        _fix_all(wd)
        # simulate a blind sed/regex pass that mangled one file's syntax
        bad_path = os.path.join(wd, "modules", "mod07.py")
        with open(bad_path, "w") as f:
            f.write("def get_timeout(:\n    return 60\n")
        out = grader.grade("unused.jsonl", wd)
        self.assertFalse(out["pass_signal"])
        self.assertEqual(out["details"]["n_corrupted"], 1)

    def test_unmodified_baseline_fails(self):
        wd = make_baseline_workdir("twenty-edits", prefix="cml-te-wd.")
        out = grader.grade("unused.jsonl", wd)
        self.assertFalse(out["pass_signal"])
        self.assertEqual(out["details"]["n_fixed"], 0)


if __name__ == "__main__":
    unittest.main()
