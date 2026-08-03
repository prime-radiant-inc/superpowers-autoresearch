import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_grader import load_grader
from fixture_workdir import make_baseline_workdir

grader = load_grader("obvious-followup")


class TestObviousFollowupGrader(unittest.TestCase):
    def test_signature_and_caller_both_updated_passes(self):
        wd = make_baseline_workdir("obvious-followup", prefix="cml-of-wd.")
        with open(os.path.join(wd, "greeting.py"), "w") as f:
            f.write('def greet(greeting, name):\n    return f"{greeting}, {name}!"\n')
        with open(os.path.join(wd, "app.py"), "w") as f:
            f.write(
                "from greeting import greet\n\n\n"
                "def main():\n"
                "    print(greet('Hello', 'World'))\n\n\n"
                "if __name__ == '__main__':\n"
                "    main()\n"
            )
        out = grader.grade("unused.jsonl", wd)
        self.assertTrue(out["pass_signal"], out["details"])
        self.assertTrue(out["details"]["signature_updated"])
        self.assertTrue(out["details"]["app_runs_cleanly"])

    def test_signature_changed_but_caller_left_stale_fails(self):
        wd = make_baseline_workdir("obvious-followup", prefix="cml-of-wd.")
        with open(os.path.join(wd, "greeting.py"), "w") as f:
            f.write('def greet(greeting, name):\n    return f"{greeting}, {name}!"\n')
        # app.py untouched -- still calls greet("World") with one arg
        out = grader.grade("unused.jsonl", wd)
        self.assertFalse(out["pass_signal"])
        self.assertTrue(out["details"]["signature_updated"])
        self.assertFalse(out["details"]["app_runs_cleanly"])

    def test_unmodified_baseline_fails(self):
        wd = make_baseline_workdir("obvious-followup", prefix="cml-of-wd.")
        out = grader.grade("unused.jsonl", wd)
        self.assertFalse(out["pass_signal"])
        self.assertFalse(out["details"]["signature_updated"])


if __name__ == "__main__":
    unittest.main()
