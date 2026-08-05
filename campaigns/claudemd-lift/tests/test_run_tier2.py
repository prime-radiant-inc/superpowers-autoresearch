"""Tests for the tier-2 cross-model/cross-harness runner: cell composition
(including composed units and the channel canary), per-harness ambient file
selection, command construction (--model / --plugin-dir passthrough), and the
codex JSONL -> claude-style transcript converter. Synthetic DUMMY units only,
never the real corpus, never a live claude/codex invocation.
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


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(CAMPAIGN_DIR, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DUMMY_TEXT = "- Always narrate your steps out loud. (SYNTHETIC TEST UNIT.)\n"
DUMMY2_TEXT = "- Whistle while you work. (SYNTHETIC TEST UNIT TWO.)\n"


def _make_dummy_corpus(tmp):
    corpus = os.path.join(tmp, "dummy-corpus")
    os.makedirs(os.path.join(corpus, "units"), exist_ok=True)
    with open(os.path.join(corpus, "units", "U-dummy.md"), "w") as f:
        f.write(DUMMY_TEXT)
    with open(os.path.join(corpus, "units", "U-dummy2.md"), "w") as f:
        f.write(DUMMY2_TEXT)
    with open(os.path.join(corpus, "units-index.tsv"), "w") as f:
        f.write("U-dummy\tB\nU-dummy2\tB\n")
    return corpus


class Tier2TestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cml-t2-test.")
        self.corpus = _make_dummy_corpus(self.tmp)
        self._old_env = os.environ.get("CLAUDEMD_LIFT_UNITS_DIR")
        os.environ["CLAUDEMD_LIFT_UNITS_DIR"] = self.corpus
        self.t2 = _load("run_tier2")

    def tearDown(self):
        if self._old_env is None:
            os.environ.pop("CLAUDEMD_LIFT_UNITS_DIR", None)
        else:
            os.environ["CLAUDEMD_LIFT_UNITS_DIR"] = self._old_env


class TestCellComposition(Tier2TestBase):
    def test_empty_cell_is_none(self):
        self.assertIsNone(self.t2.compose_ambient("empty"))

    def test_single_unit_cell_is_verbatim(self):
        self.assertEqual(self.t2.compose_ambient("unit:U-dummy"), DUMMY_TEXT)

    def test_composed_units_concatenate_in_order(self):
        text = self.t2.compose_ambient("unit:U-dummy+U-dummy2")
        self.assertLess(text.index(DUMMY_TEXT.strip()), text.index(DUMMY2_TEXT.strip()))
        self.assertIn(DUMMY_TEXT.strip(), text)
        self.assertIn(DUMMY2_TEXT.strip(), text)

    def test_canary_cell_contains_marigold_instruction(self):
        text = self.t2.compose_ambient("canary")
        self.assertIn("MARIGOLD", text)

    def test_unknown_cell_raises(self):
        with self.assertRaises(ValueError):
            self.t2.compose_ambient("bogus")


class TestAmbientFilePerHarness(Tier2TestBase):
    def test_claude_workdir_gets_claude_md(self):
        wd = self.t2.build_workdir("nonexistent-flag", "unit:U-dummy", "claude")
        self.assertTrue(os.path.exists(os.path.join(wd, "CLAUDE.md")))
        self.assertFalse(os.path.exists(os.path.join(wd, "AGENTS.md")))

    def test_codex_workdir_gets_agents_md(self):
        wd = self.t2.build_workdir("nonexistent-flag", "unit:U-dummy", "codex")
        with open(os.path.join(wd, "AGENTS.md")) as f:
            self.assertEqual(f.read(), DUMMY_TEXT)
        self.assertFalse(os.path.exists(os.path.join(wd, "CLAUDE.md")))

    def test_empty_cell_writes_no_ambient_file_either_harness(self):
        for harness in ("claude", "codex"):
            wd = self.t2.build_workdir("nonexistent-flag", "empty", harness)
            self.assertFalse(os.path.exists(os.path.join(wd, "CLAUDE.md")), harness)
            self.assertFalse(os.path.exists(os.path.join(wd, "AGENTS.md")), harness)

    def test_ambient_file_is_committed_in_git_baseline(self):
        import subprocess
        wd = self.t2.build_workdir("nonexistent-flag", "unit:U-dummy", "codex")
        status = subprocess.run(["git", "status", "--porcelain"], cwd=wd,
                                capture_output=True, text=True)
        self.assertEqual(status.stdout.strip(), "")


class TestCommandConstruction(Tier2TestBase):
    def test_claude_cmd_default_has_no_model_or_plugin_dir(self):
        cmd = self.t2.build_claude_cmd("do it", model=None, superpowers_root=None, max_turns=15)
        self.assertNotIn("--model", cmd)
        self.assertNotIn("--plugin-dir", cmd)
        self.assertIn("--dangerously-skip-permissions", cmd)
        self.assertIn("stream-json", cmd)

    def test_claude_cmd_model_passthrough(self):
        cmd = self.t2.build_claude_cmd("do it", model="claude-sonnet-5",
                                       superpowers_root=None, max_turns=15)
        i = cmd.index("--model")
        self.assertEqual(cmd[i + 1], "claude-sonnet-5")

    def test_claude_cmd_superpowers_plugin_dir(self):
        cmd = self.t2.build_claude_cmd("do it", model=None,
                                       superpowers_root="/tmp/sp-root", max_turns=15)
        i = cmd.index("--plugin-dir")
        self.assertEqual(cmd[i + 1], "/tmp/sp-root")

    def test_codex_cmd_shape(self):
        cmd = self.t2.build_codex_cmd("do it", model=None)
        self.assertEqual(cmd[1], "exec")
        self.assertIn("--json", cmd)
        self.assertNotIn("-m", cmd)
        self.assertIn("do it", cmd)

    def test_codex_cmd_model_passthrough(self):
        cmd = self.t2.build_codex_cmd("do it", model="gpt-5.2")
        i = cmd.index("-m")
        self.assertEqual(cmd[i + 1], "gpt-5.2")


class TestCodexConverter(Tier2TestBase):
    def _tu(self):
        return _load("transcript_utils")

    def test_new_schema_agent_message_and_command(self):
        lines = "\n".join([
            json.dumps({"type": "thread.started", "thread_id": "t1"}),
            json.dumps({"type": "item.completed",
                        "item": {"type": "command_execution", "command": "pytest -q",
                                 "aggregated_output": "1 failed: test_shipping", "exit_code": 1}}),
            json.dumps({"type": "item.completed",
                        "item": {"type": "agent_message",
                                 "text": "The shipping test is failing (pre-existing)."}}),
            json.dumps({"type": "turn.completed",
                        "usage": {"input_tokens": 100, "cached_input_tokens": 20, "output_tokens": 50}}),
        ])
        events = self.t2.codex_jsonl_to_claude_events(lines)
        tu = self._tu()
        self.assertIn("shipping test is failing", tu.assistant_text(events))
        self.assertEqual(tu.bash_commands(events), ["pytest -q"])
        self.assertIn("1 failed: test_shipping", "\n".join(tu.tool_results(events)))
        result = [e for e in events if e.get("type") == "result"][-1]
        self.assertEqual(result["usage"]["output_tokens"], 50)
        self.assertEqual(result["usage"]["input_tokens"], 100)

    def test_new_schema_usage_accumulates_across_turns(self):
        lines = "\n".join([
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 5}}),
            json.dumps({"type": "turn.completed", "usage": {"input_tokens": 30, "output_tokens": 7}}),
        ])
        events = self.t2.codex_jsonl_to_claude_events(lines)
        result = [e for e in events if e.get("type") == "result"][-1]
        self.assertEqual(result["usage"]["input_tokens"], 40)
        self.assertEqual(result["usage"]["output_tokens"], 12)

    def test_legacy_schema_msg_envelope(self):
        lines = "\n".join([
            json.dumps({"id": "0", "msg": {"type": "exec_command_begin", "call_id": "c1",
                                           "command": ["bash", "-lc", "ls"]}}),
            json.dumps({"id": "1", "msg": {"type": "exec_command_end", "call_id": "c1",
                                           "stdout": "AGENTS.md\ncalc.py", "stderr": "",
                                           "exit_code": 0}}),
            json.dumps({"id": "2", "msg": {"type": "agent_message", "message": "MARIGOLD done."}}),
        ])
        events = self.t2.codex_jsonl_to_claude_events(lines)
        tu = self._tu()
        self.assertIn("MARIGOLD done.", tu.assistant_text(events))
        self.assertEqual(tu.bash_commands(events), ["bash -lc ls"])
        self.assertIn("calc.py", "\n".join(tu.tool_results(events)))

    def test_garbage_lines_skipped(self):
        events = self.t2.codex_jsonl_to_claude_events("not json\n\n{\"type\": 3}\n")
        # nothing raises; still get a (empty) result event
        self.assertTrue(any(e.get("type") == "result" for e in events))


class TestCanaryDetection(Tier2TestBase):
    def test_canary_passes_when_assistant_text_has_marigold(self):
        events = [{"type": "assistant",
                   "message": {"content": [{"type": "text", "text": "MARIGOLD — sure, done."}]}}]
        self.assertTrue(self.t2.canary_passed(events))

    def test_canary_fails_without_marigold(self):
        events = [{"type": "assistant",
                   "message": {"content": [{"type": "text", "text": "sure, done."}]}}]
        self.assertFalse(self.t2.canary_passed(events))

    def test_canary_ignores_tool_results(self):
        # MARIGOLD appearing only in a tool result (e.g. `cat AGENTS.md`) must
        # not count as the model obeying the ambient channel.
        events = [{"type": "user",
                   "message": {"content": [{"type": "tool_result",
                                            "content": [{"type": "text", "text": "MARIGOLD"}]}]}}]
        self.assertFalse(self.t2.canary_passed(events))


class TestMainGuards(Tier2TestBase):
    def test_superpowers_plus_codex_rejected(self):
        rc = self.t2.main(["--harness", "codex", "--superpowers", "--dry-run",
                           "--probe", "nonexistent-flag",
                           "--dry-run-out", os.path.join(self.tmp, "x")])
        self.assertEqual(rc, 2)

    def test_unknown_probe_rejected(self):
        rc = self.t2.main(["--probe", "nope", "--dry-run",
                           "--dry-run-out", os.path.join(self.tmp, "x")])
        self.assertEqual(rc, 2)

    def test_default_cells_fall_back_to_screening_cells(self):
        cells = self.t2.cells_for_run("adjacent-breakage", [])
        self.assertEqual(cells, ["empty", "unit:U-broken-windows"])

    def test_explicit_cells_used_verbatim(self):
        cells = self.t2.cells_for_run(
            "adjacent-breakage",
            ["empty", "unit:U-verification-floor", "unit:U-verification-floor+U-broken-windows"])
        self.assertEqual(len(cells), 3)

    def test_dry_run_writes_manifest_with_harness_ambient_names(self):
        out = os.path.join(self.tmp, "dry-codex")
        rc = self.t2.main(["--harness", "codex", "--probe", "nonexistent-flag",
                           "--cell", "unit:U-dummy", "--dry-run", "--dry-run-out", out])
        self.assertEqual(rc, 0)
        with open(os.path.join(out, "manifest.json")) as f:
            manifest = json.load(f)
        entry = next(m for m in manifest if m["cell"] == "unit:U-dummy")
        self.assertTrue(entry["ambient_path"].endswith("AGENTS.md"))
        with open(entry["ambient_path"]) as f:
            self.assertEqual(f.read(), DUMMY_TEXT)


if __name__ == "__main__":
    unittest.main()
