"""Tests for score_e1.py's output-filename/collision handling (Task 6b fix
round 1). Task 6b's own scoring call overwrote Task 6's committed
out/e1-cx-sdd-small-{dev,spinout}.json: the output label was derived from
arm_scenario alone, so re-scoring a different rep range (REP_START-extended
battery) under the same arm_scenario collided silently. Fixture run dirs
here are synthetic -- fake rep-dir names, one minimal spawn_agent record
each -- no real rollouts, no client content."""
import json, os, pathlib, tempfile, unittest
import score_e1 as se


def L(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


SPAWN = L("2026-07-29T05:00:00.000Z", "response_item", {
    "type": "function_call", "id": "fc_1", "name": "spawn_agent",
    "namespace": "collaboration",
    "arguments": json.dumps({"task_name": "task1_implementer", "fork_turns": "none",
                             "model": "gpt-5.6-terra", "reasoning_effort": "high",
                             "message": "gAAAAABencrypted"}),
    "call_id": "call_A"})


def make_rundir(base, arm_scenario, rep):
    """Synthetic run dir matching run-quorum.sh's --out-root naming
    convention: <base>/cx-eff-<arm_scenario>-rep<rep>/leaf/home/.codex/
    sessions/**/*.jsonl, containing one synthetic spawn_agent call."""
    rundir = base / f"cx-eff-{arm_scenario}-rep{rep}" / "leaf"
    sess_dir = rundir / "home" / ".codex" / "sessions" / "2026" / "07" / "29"
    sess_dir.mkdir(parents=True)
    rollout = sess_dir / f"rollout-2026-07-29T05-00-0{rep}-000000-uuid{rep}.jsonl"
    rollout.write_text(SPAWN + "\n")
    return rundir


class TestOutLabel(unittest.TestCase):
    def test_label_includes_rep_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            runs = [se.score_run(str(make_rundir(base, "cx-sdd-small-spinout", r)))
                    for r in (5, 6, 7, 8)]
            self.assertEqual(se._out_label(runs), "cx-sdd-small-spinout-rep5-8")

    def test_label_single_rep(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            runs = [se.score_run(str(make_rundir(base, "cx-sdd-small-dev", 5)))]
            self.assertEqual(se._out_label(runs), "cx-sdd-small-dev-rep5")

    def test_label_non_contiguous_reps_uses_min_max(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            runs = [se.score_run(str(make_rundir(base, "cx-sdd-small-dev", r)))
                    for r in (1, 2, 4)]
            self.assertEqual(se._out_label(runs), "cx-sdd-small-dev-rep1-4")


class TestWriteOutputCollision(unittest.TestCase):
    def _runs(self, base, arm_scenario, reps):
        return [se.score_run(str(make_rundir(base, arm_scenario, r))) for r in reps]

    def test_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            battery = pathlib.Path(tmp) / "battery"
            out_dir = pathlib.Path(tmp) / "out"
            runs = self._runs(battery, "cx-sdd-small-dev", [1, 2])
            agg = se.summarize([s for r in runs for s in r["spawns"]])

            out_path, wrote = se.write_output(runs, agg, str(out_dir))
            self.assertTrue(wrote)
            self.assertTrue(os.path.exists(out_path))
            with open(out_path) as f:
                original = f.read()

            # Re-writing the SAME rep range without FORCE must refuse, not
            # silently clobber.
            out_path2, wrote2 = se.write_output(runs, agg, str(out_dir))
            self.assertFalse(wrote2)
            self.assertEqual(out_path, out_path2)
            with open(out_path2) as f:
                self.assertEqual(f.read(), original)

    def test_force_allows_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            battery = pathlib.Path(tmp) / "battery"
            out_dir = pathlib.Path(tmp) / "out"
            runs = self._runs(battery, "cx-sdd-small-dev", [1, 2])
            agg = se.summarize([s for r in runs for s in r["spawns"]])

            se.write_output(runs, agg, str(out_dir))
            out_path, wrote = se.write_output(runs, agg, str(out_dir), force=True)
            self.assertTrue(wrote)

    def test_different_rep_range_does_not_collide(self):
        """The Task 6b bug: scoring rep1-4 then later rep5-6 of the same
        arm_scenario must land in different files, not overwrite."""
        with tempfile.TemporaryDirectory() as tmp:
            battery = pathlib.Path(tmp) / "battery"
            out_dir = pathlib.Path(tmp) / "out"

            runs_1_4 = self._runs(battery, "cx-sdd-small-dev", [1, 2, 3, 4])
            agg_1_4 = se.summarize([s for r in runs_1_4 for s in r["spawns"]])
            out_path_1_4, wrote_1_4 = se.write_output(runs_1_4, agg_1_4, str(out_dir))
            self.assertTrue(wrote_1_4)

            runs_5_6 = self._runs(battery, "cx-sdd-small-dev", [5, 6])
            agg_5_6 = se.summarize([s for r in runs_5_6 for s in r["spawns"]])
            out_path_5_6, wrote_5_6 = se.write_output(runs_5_6, agg_5_6, str(out_dir))
            self.assertTrue(wrote_5_6)

            self.assertNotEqual(out_path_1_4, out_path_5_6)
            # The rep1-4 file must be untouched by the rep5-6 write.
            with open(out_path_1_4) as f:
                d = json.load(f)
            self.assertEqual(sorted(r["rep"] for r in d["runs"]), [1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
