"""Tests the runner's cell-composition logic (cells, CLAUDE.md writing,
workdir assembly, dry-run manifest) against a synthetic DUMMY unit corpus --
never the real one, and never a live `claude` invocation.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN_DIR = os.path.dirname(HERE)
sys.path.insert(0, CAMPAIGN_DIR)


def _load_run_screening():
    spec = importlib.util.spec_from_file_location("run_screening", os.path.join(CAMPAIGN_DIR, "run_screening.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DUMMY_UNIT_TEXT = "- Always narrate your steps out loud before doing them. (SYNTHETIC TEST UNIT, not real.)\n"


def _make_dummy_corpus(tmp):
    corpus = os.path.join(tmp, "dummy-corpus")
    os.makedirs(os.path.join(corpus, "units"), exist_ok=True)
    with open(os.path.join(corpus, "units", "U-dummy.md"), "w") as f:
        f.write(DUMMY_UNIT_TEXT)
    with open(os.path.join(corpus, "units-index.tsv"), "w") as f:
        f.write("U-dummy\tB\n")
    return corpus


class TestRunScreeningCellComposition(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cml-rs-test.")
        self.corpus = _make_dummy_corpus(self.tmp)
        self._old_env = os.environ.get("CLAUDEMD_LIFT_UNITS_DIR")
        os.environ["CLAUDEMD_LIFT_UNITS_DIR"] = self.corpus
        self.rs = _load_run_screening()

    def tearDown(self):
        if self._old_env is None:
            os.environ.pop("CLAUDEMD_LIFT_UNITS_DIR", None)
        else:
            os.environ["CLAUDEMD_LIFT_UNITS_DIR"] = self._old_env

    def test_all_probes_have_a_registered_target_unit(self):
        for probe_id in self.rs.all_probes():
            self.assertIn(probe_id, self.rs.PROBE_UNIT)

    def test_every_probe_dir_has_fixture_prompt_and_grader(self):
        for probe_id in self.rs.all_probes():
            pdir = self.rs.probe_dir(probe_id)
            self.assertTrue(os.path.isdir(os.path.join(pdir, "fixture")), probe_id)
            self.assertTrue(os.path.isfile(os.path.join(pdir, "prompt.txt")), probe_id)
            self.assertTrue(os.path.isfile(os.path.join(pdir, "grade.py")), probe_id)

    def test_cells_for_probe_default_is_empty_plus_its_own_unit(self):
        cells = self.rs.cells_for_probe("nonexistent-flag")
        self.assertEqual(cells, ["empty", "unit:U-honesty"])

    def test_cells_for_probe_unit_override(self):
        cells = self.rs.cells_for_probe("nonexistent-flag", unit_override="U-dummy")
        self.assertEqual(cells, ["empty", "unit:U-dummy"])

    def test_compose_claude_md_empty_is_none(self):
        self.assertIsNone(self.rs.compose_claude_md("empty"))

    def test_compose_claude_md_unit_reads_verbatim_dummy_text(self):
        text = self.rs.compose_claude_md("unit:U-dummy")
        self.assertEqual(text, DUMMY_UNIT_TEXT)

    def test_build_workdir_empty_cell_has_no_claude_md(self):
        wd = self.rs.build_workdir("nonexistent-flag", "empty")
        self.assertFalse(os.path.exists(os.path.join(wd, "CLAUDE.md")))
        # fixture files present
        self.assertTrue(os.path.exists(os.path.join(wd, "README.md")))
        # git baseline committed
        import subprocess
        status = subprocess.run(["git", "status", "--porcelain"], cwd=wd,
                                capture_output=True, text=True)
        self.assertEqual(status.stdout.strip(), "")

    def test_build_workdir_unit_cell_writes_verbatim_claude_md(self):
        wd = self.rs.build_workdir("nonexistent-flag", "unit:U-dummy")
        with open(os.path.join(wd, "CLAUDE.md")) as f:
            content = f.read()
        self.assertEqual(content, DUMMY_UNIT_TEXT)

    def test_dry_run_writes_manifest_and_zero_claude_invocations(self):
        out_dir = os.path.join(self.tmp, "dry-out")
        # Patch the probe's unit to the dummy one via override so this test
        # never touches the real corpus dir contents.
        rc = self.rs.dry_run(["nonexistent-flag"], "U-dummy", 2, out_dir)
        self.assertEqual(rc, 0)
        with open(os.path.join(out_dir, "manifest.json")) as f:
            manifest = json.load(f)
        self.assertEqual(len(manifest), 2)
        cells = {m["cell"] for m in manifest}
        self.assertEqual(cells, {"empty", "unit:U-dummy"})
        unit_entry = next(m for m in manifest if m["cell"] == "unit:U-dummy")
        with open(unit_entry["claude_md_path"]) as f:
            self.assertEqual(f.read(), DUMMY_UNIT_TEXT)
        empty_entry = next(m for m in manifest if m["cell"] == "empty")
        self.assertIsNone(empty_entry["claude_md_path"])

    def test_unknown_probe_rejected_by_main(self):
        rc = self.rs.main(["--dry-run", "--probe", "not-a-real-probe",
                           "--dry-run-out", os.path.join(self.tmp, "x")])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
