"""Tests for the quorum adapter seam (quorum_seam.py) and the kimi/pi tier-2
harness adapters in run_tier2.py: YAML-subset parsing, credential/.env
resolution, provisioning file shapes (pi models/settings/auth trio; kimi
env-model construction), session-log resolution, ambient-file selection,
command construction, and the kimi/pi output -> claude-style transcript
converters. All offline -- no live agent invocations, no network, no secrets.
Fixture shapes for the converters are transcriptions of the 2026-08-05 format
probes (kimi-code 0.15.0, pi 0.80.1)."""
import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN_DIR = os.path.dirname(HERE)
sys.path.insert(0, CAMPAIGN_DIR)

QUORUM_ROOT = "/Users/jesse/git/superpowers/evals-lane-b"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(CAMPAIGN_DIR, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DUMMY_TEXT = "- Always narrate your steps out loud. (SYNTHETIC TEST UNIT.)\n"


def _make_dummy_corpus(tmp):
    corpus = os.path.join(tmp, "dummy-corpus")
    os.makedirs(os.path.join(corpus, "units"), exist_ok=True)
    with open(os.path.join(corpus, "units", "U-dummy.md"), "w") as f:
        f.write(DUMMY_TEXT)
    with open(os.path.join(corpus, "units-index.tsv"), "w") as f:
        f.write("U-dummy\tB\n")
    return corpus


class SeamTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cml-seam-test.")
        self.qs = _load("quorum_seam")


class TestYamlSubsetParser(SeamTestBase):
    def _parse(self, text):
        path = os.path.join(self.tmp, "x.yaml")
        with open(path, "w") as f:
            f.write(text)
        return self.qs.load_simple_yaml(path)

    def test_flat_scalars_quotes_and_ints(self):
        got = self._parse("name: kimi\n"
                          "# a comment\n"
                          "binary: kimi\n"
                          "home_config_subdir: \".kimi-code\"\n"
                          "max_concurrency: 6\n"
                          "session_log_glob: \"**/wire.jsonl\"\n")
        self.assertEqual(got["binary"], "kimi")
        self.assertEqual(got["home_config_subdir"], ".kimi-code")
        self.assertEqual(got["max_concurrency"], 6)
        self.assertEqual(got["session_log_glob"], "**/wire.jsonl")

    def test_nested_map_and_flow_list(self):
        got = self._parse("cred:\n"
                          "  model: z-ai/glm-5.2\n"
                          "  harnesses: [pi, opencode, hermes]\n"
                          "  compat:\n"
                          "    thinking_format: zai\n"
                          "other:\n"
                          "  model: gpt-5.5\n")
        self.assertEqual(got["cred"]["model"], "z-ai/glm-5.2")
        self.assertEqual(got["cred"]["harnesses"], ["pi", "opencode", "hermes"])
        self.assertEqual(got["cred"]["compat"]["thinking_format"], "zai")
        self.assertEqual(got["other"]["model"], "gpt-5.5")

    def test_block_list(self):
        got = self._parse("required_env:\n  - SUPERPOWERS_ROOT\n  - OTHER\nmax_time: 10m\n")
        self.assertEqual(got["required_env"], ["SUPERPOWERS_ROOT", "OTHER"])
        self.assertEqual(got["max_time"], "10m")

    def test_empty_block_stays_empty_dict(self):
        got = self._parse("a:\nb: 1\n")
        self.assertEqual(got["a"], {})
        self.assertEqual(got["b"], 1)


class TestEnvFileAndKeyResolution(SeamTestBase):
    def test_env_file_values_strip_quotes_and_skip_comments(self):
        root = os.path.join(self.tmp, "root")
        os.makedirs(root)
        with open(os.path.join(root, ".env"), "w") as f:
            f.write("# comment\nA_KEY=abc123\nB_KEY='quoted'\n\nnot a pair\n")
        got = self.qs.env_file_values(root)
        self.assertEqual(got, {"A_KEY": "abc123", "B_KEY": "quoted"})

    def test_resolve_api_key_prefers_process_env(self):
        root = os.path.join(self.tmp, "root2")
        os.makedirs(root)
        with open(os.path.join(root, ".env"), "w") as f:
            f.write("SOME_KEY=fromfile\n")
        os.environ["SOME_KEY"] = "fromenv"
        try:
            self.assertEqual(self.qs.resolve_api_key("SOME_KEY", root), "fromenv")
        finally:
            os.environ.pop("SOME_KEY")
        self.assertEqual(self.qs.resolve_api_key("SOME_KEY", root), "fromfile")
        self.assertIsNone(self.qs.resolve_api_key("ABSENT_KEY", root))


class TestKimiProvisioning(SeamTestBase):
    def test_kimi_model_env_overlays_model_and_key(self):
        env = self.qs.kimi_model_env("kimi-for-coding", "sekret")
        self.assertEqual(env["KIMI_MODEL_NAME"], "kimi-for-coding")
        self.assertEqual(env["KIMI_MODEL_API_KEY"], "sekret")
        self.assertEqual(env["KIMI_MODEL_BASE_URL"], "https://api.kimi.com/coding/v1")
        self.assertEqual(env["KIMI_DISABLE_TELEMETRY"], "1")
        self.assertEqual(env["KIMI_DISABLE_CRON"], "1")

    def test_kimi_model_env_none_model_keeps_default(self):
        env = self.qs.kimi_model_env(None, "sekret")
        self.assertEqual(env["KIMI_MODEL_NAME"], "kimi-for-coding")


class TestPiProvisioning(SeamTestBase):
    CRED = {"model": "z-ai/glm-5.2", "api": "openai-chat",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key_env": "OPENROUTER_API_KEY",
            "compat": {"thinking_format": "zai"}}

    def test_seed_pi_home_writes_quorum_provider_trio(self):
        home = os.path.join(self.tmp, "pihome")
        provider, model = self.qs.seed_pi_home(home, self.CRED, "sekret")
        self.assertEqual((provider, model), ("quorum", "z-ai/glm-5.2"))
        cfg = os.path.join(home, ".pi", "agent")
        with open(os.path.join(cfg, "models.json")) as f:
            models = json.load(f)
        entry = models["providers"]["quorum"]
        self.assertEqual(entry["baseUrl"], "https://openrouter.ai/api/v1")
        self.assertEqual(entry["api"], "openai-completions")  # openai-chat mapped
        self.assertEqual(entry["apiKey"], "sekret")
        m = entry["models"][0]
        self.assertEqual(m["id"], "z-ai/glm-5.2")
        self.assertEqual(m["compat"], {"thinkingFormat": "zai"})
        self.assertTrue(m["reasoning"])
        with open(os.path.join(cfg, "settings.json")) as f:
            settings = json.load(f)
        self.assertEqual(settings["defaultProvider"], "quorum")
        self.assertEqual(settings["defaultModel"], "z-ai/glm-5.2")
        with open(os.path.join(cfg, "auth.json")) as f:
            auth = json.load(f)
        self.assertEqual(auth["quorum"], {"type": "api_key", "key": "sekret"})
        self.assertTrue(os.path.isdir(os.path.join(cfg, "sessions")))
        for secret_file in ("models.json", "auth.json"):
            mode = stat.S_IMODE(os.stat(os.path.join(cfg, secret_file)).st_mode)
            self.assertEqual(mode, 0o600, secret_file)

    def test_seed_pi_home_requires_base_url(self):
        cred = dict(self.CRED)
        del cred["base_url"]
        with self.assertRaises(ValueError):
            self.qs.seed_pi_home(os.path.join(self.tmp, "h2"), cred, "k")

    def test_seed_pi_home_rejects_non_openai_chat_api(self):
        cred = dict(self.CRED, api="openai-responses")
        with self.assertRaises(ValueError):
            self.qs.seed_pi_home(os.path.join(self.tmp, "h3"), cred, "k")

    def test_seed_pi_home_no_compat_omits_reasoning(self):
        cred = {"model": "m", "api": "openai-chat", "base_url": "http://x"}
        self.qs.seed_pi_home(os.path.join(self.tmp, "h4"), cred, "k")
        with open(os.path.join(self.tmp, "h4", ".pi", "agent", "models.json")) as f:
            m = json.load(f)["providers"]["quorum"]["models"][0]
        self.assertNotIn("compat", m)
        self.assertNotIn("reasoning", m)


class TestSessionLogPaths(SeamTestBase):
    def test_resolves_agent_home_token_and_recursive_glob(self):
        home = os.path.join(self.tmp, "khome")
        deep = os.path.join(home, ".kimi-code", "sessions", "wd_x", "s1", "agents", "main")
        os.makedirs(deep)
        with open(os.path.join(deep, "wire.jsonl"), "w") as f:
            f.write("{}\n")
        agent = {"session_log_dir": "${QUORUM_AGENT_HOME}/.kimi-code/sessions",
                 "session_log_glob": "**/wire.jsonl"}
        paths = self.qs.session_log_paths(agent, home)
        self.assertEqual(len(paths), 1)
        self.assertTrue(paths[0].endswith("wire.jsonl"))


@unittest.skipUnless(os.path.isdir(QUORUM_ROOT), "evals-lane-b checkout not present")
class TestRealQuorumDefinitions(SeamTestBase):
    """The seam's whole point: these assert against the LIVE checked-in quorum
    definitions, so drift in evals-lane-b that would break the adapters is
    caught here (offline -- parsing only)."""

    def test_kimi_agent_def(self):
        agent = self.qs.agent_def("kimi", QUORUM_ROOT)
        self.assertEqual(agent["binary"], "kimi")
        self.assertEqual(agent["home_config_subdir"], ".kimi-code")
        self.assertEqual(agent["session_log_glob"], "**/wire.jsonl")
        self.assertEqual(agent["default_credential"], "kimi_default")

    def test_pi_agent_def(self):
        agent = self.qs.agent_def("pi", QUORUM_ROOT)
        self.assertEqual(agent["binary"], "pi")
        self.assertEqual(agent["home_config_subdir"], ".pi/agent")

    def test_glm_credential(self):
        cred = self.qs.credential("openrouter_glm_5_2", QUORUM_ROOT)
        self.assertEqual(cred["model"], "z-ai/glm-5.2")
        self.assertEqual(cred["api"], "openai-chat")
        self.assertEqual(cred["base_url"], "https://openrouter.ai/api/v1")
        self.assertEqual(cred["api_key_env"], "OPENROUTER_API_KEY")
        self.assertEqual(cred["compat"]["thinking_format"], "zai")
        self.assertIn("pi", cred["harnesses"])

    def test_kimi_credential(self):
        cred = self.qs.credential("kimi_default", QUORUM_ROOT)
        self.assertEqual(cred["model"], "kimi-for-coding")
        self.assertEqual(cred["auth"], "oauth")

    def test_unknown_credential_raises_with_known_names(self):
        with self.assertRaises(KeyError):
            self.qs.credential("nope_not_real", QUORUM_ROOT)


class AdapterTestBase(unittest.TestCase):
    """run_tier2 kimi/pi adapter surface: converters, commands, ambient files."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cml-t2seam-test.")
        self.corpus = _make_dummy_corpus(self.tmp)
        self._old_env = os.environ.get("CLAUDEMD_LIFT_UNITS_DIR")
        os.environ["CLAUDEMD_LIFT_UNITS_DIR"] = self.corpus
        self.t2 = _load("run_tier2")
        self.tu = _load("transcript_utils")

    def tearDown(self):
        if self._old_env is None:
            os.environ.pop("CLAUDEMD_LIFT_UNITS_DIR", None)
        else:
            os.environ["CLAUDEMD_LIFT_UNITS_DIR"] = self._old_env


class TestKimiConverter(AdapterTestBase):
    LINES = "\n".join([
        json.dumps({"role": "assistant", "tool_calls": [
            {"type": "function", "id": "tool_1",
             "function": {"name": "Bash", "arguments": "{\"command\": \"echo hello\"}"}},
            {"type": "function", "id": "tool_2",
             "function": {"name": "Write",
                          "arguments": "{\"path\": \"hello.txt\", \"content\": \"hi\"}"}}]}),
        json.dumps({"role": "tool", "tool_call_id": "tool_1", "content": "hello\n"}),
        json.dumps({"role": "tool", "tool_call_id": "tool_2",
                    "content": "Wrote 2 bytes to hello.txt"}),
        json.dumps({"role": "assistant", "content": "MARIGOLD DONE"}),
        json.dumps({"role": "meta", "type": "session.resume_hint",
                    "session_id": "session_x", "content": "To resume ..."}),
    ])

    def test_tool_calls_text_and_results(self):
        events = self.t2.kimi_stream_to_claude_events(self.LINES)
        self.assertEqual(self.tu.bash_commands(events), ["echo hello"])
        self.assertIn("MARIGOLD DONE", self.tu.assistant_text(events))
        self.assertIn("hello", "\n".join(self.tu.tool_results(events)))
        self.assertEqual(self.tu.file_write_contents(events), ["hi"])
        self.assertEqual(events[-1]["converted_from"], "kimi")
        self.assertEqual(events[-1]["result"], "MARIGOLD DONE")
        self.assertEqual(events[-1]["unknown_lines"], 0)

    def test_canary_detected_from_assistant_text_only(self):
        events = self.t2.kimi_stream_to_claude_events(self.LINES)
        self.assertTrue(self.t2.canary_passed(events))
        no_canary = self.t2.kimi_stream_to_claude_events(
            json.dumps({"role": "tool", "tool_call_id": "t", "content": "MARIGOLD"}))
        self.assertFalse(self.t2.canary_passed(no_canary))

    def test_garbage_lines_counted_not_fatal(self):
        events = self.t2.kimi_stream_to_claude_events("not json\n[1,2]\n")
        self.assertEqual(events[-1]["unknown_lines"], 2)

    def test_wire_summary_sums_usage_and_reads_alias(self):
        home = os.path.join(self.tmp, "khome")
        deep = os.path.join(home, ".kimi-code", "sessions", "wd", "s", "agents", "main")
        os.makedirs(deep)
        with open(os.path.join(deep, "wire.jsonl"), "w") as f:
            f.write(json.dumps({"type": "config.update",
                                "modelAlias": "__kimi_env_model__"}) + "\n")
            f.write(json.dumps({"type": "usage.record", "model": "__kimi_env_model__",
                                "usage": {"inputOther": 100, "output": 10,
                                          "inputCacheRead": 50}}) + "\n")
            f.write(json.dumps({"type": "usage.record", "model": "__kimi_env_model__",
                                "usage": {"inputOther": 30, "output": 5}}) + "\n")
        agent = {"session_log_dir": "${QUORUM_AGENT_HOME}/.kimi-code/sessions",
                 "session_log_glob": "**/wire.jsonl"}
        usage, alias = self.t2.kimi_wire_summary(agent, home)
        self.assertEqual(usage, {"inputOther": 130, "output": 15, "inputCacheRead": 50})
        self.assertEqual(alias, "__kimi_env_model__")


class TestPiConverter(AdapterTestBase):
    @staticmethod
    def _msg_end(message):
        return json.dumps({"type": "message_end", "message": message})

    def _lines(self):
        return "\n".join([
            json.dumps({"type": "session", "version": 3, "id": "s1", "cwd": "/tmp/x"}),
            self._msg_end({"role": "user",
                           "content": [{"type": "text", "text": "do the thing"}]}),
            self._msg_end({"role": "assistant", "model": "z-ai/glm-5.2",
                           "usage": {"input": 100, "output": 10, "cacheRead": 5,
                                     "cost": {"total": 0.0}},
                           "content": [
                               {"type": "thinking", "thinking": "hmm"},
                               {"type": "toolCall", "id": "c1", "name": "bash",
                                "arguments": {"command": "ls"}}]}),
            self._msg_end({"role": "toolResult", "toolCallId": "c1", "toolName": "bash",
                           "content": [{"type": "text", "text": "AGENTS.md\ncalc.py"}]}),
            self._msg_end({"role": "assistant", "model": "z-ai/glm-5.2",
                           "usage": {"input": 200, "output": 20},
                           "content": [{"type": "text", "text": "MARIGOLD all done"}]}),
            # a partial update that must NOT double-count
            json.dumps({"type": "message_update",
                        "message": {"role": "assistant",
                                    "content": [{"type": "text", "text": "MARIGOLD all done"}],
                                    "usage": {"input": 999, "output": 999}}}),
        ])

    def test_messages_tools_model_and_usage(self):
        events = self.t2.pi_json_to_claude_events(self._lines())
        self.assertEqual(self.tu.bash_commands(events), ["ls"])  # bash -> Bash mapping
        self.assertIn("MARIGOLD all done", self.tu.assistant_text(events))
        self.assertNotIn("hmm", self.tu.assistant_text(events))  # thinking excluded
        self.assertIn("calc.py", "\n".join(self.tu.tool_results(events)))
        result = events[-1]
        self.assertEqual(result["model"], "z-ai/glm-5.2")
        self.assertEqual(result["usage"]["input"], 300)
        self.assertEqual(result["usage"]["output"], 30)
        self.assertEqual(result["usage"]["cacheRead"], 5)
        self.assertNotIn("cost_usd", result)  # zero cost -> omitted, not $0
        self.assertTrue(self.t2.canary_passed(events))

    def test_session_file_style_message_events_also_accepted(self):
        line = json.dumps({"type": "message",
                           "message": {"role": "assistant", "model": "m",
                                       "content": [{"type": "text", "text": "hi"}]}})
        events = self.t2.pi_json_to_claude_events(line)
        self.assertIn("hi", self.tu.assistant_text(events))

    def test_string_tool_result_and_garbage(self):
        lines = "\n".join([
            self._msg_end({"role": "toolResult", "toolCallId": "c", "content": "plain"}),
            "garbage",
        ])
        events = self.t2.pi_json_to_claude_events(lines)
        self.assertIn("plain", "\n".join(self.tu.tool_results(events)))
        self.assertEqual(events[-1]["unknown_lines"], 1)


class TestSeamCommandsAndAmbient(AdapterTestBase):
    def test_kimi_cmd_shape(self):
        cmd = self.t2.build_kimi_cmd("/x/bin/kimi", "do it")
        self.assertEqual(cmd, ["/x/bin/kimi", "-p", "do it",
                               "--output-format", "stream-json"])
        self.assertNotIn("--yolo", cmd)  # rejected in print mode (probed)

    def test_pi_cmd_shape(self):
        cmd = self.t2.build_pi_cmd("pi", "quorum", "z-ai/glm-5.2", "do it")
        self.assertEqual(cmd[:5], ["pi", "--provider", "quorum", "--model", "z-ai/glm-5.2"])
        self.assertIn("--no-extensions", cmd)
        self.assertIn("--no-skills", cmd)
        self.assertNotIn("--no-context-files", cmd)  # AGENTS.md channel stays on
        self.assertEqual(cmd[-4:], ["--mode", "json", "-p", "do it"])

    def test_kimi_and_pi_ambient_file_is_agents_md(self):
        for harness in ("kimi", "pi"):
            self.assertEqual(self.t2.AMBIENT_FILE[harness], "AGENTS.md")
            wd = self.t2.build_workdir("nonexistent-flag", "unit:U-dummy", harness)
            with open(os.path.join(wd, "AGENTS.md")) as f:
                self.assertEqual(f.read(), DUMMY_TEXT)
            self.assertFalse(os.path.exists(os.path.join(wd, "CLAUDE.md")))

    def test_credential_flag_rejected_for_non_seam_harness(self):
        rc = self.t2.main(["--harness", "claude", "--credential", "kimi_default",
                           "--dry-run", "--probe", "nonexistent-flag",
                           "--dry-run-out", os.path.join(self.tmp, "x")])
        self.assertEqual(rc, 2)

    def test_kimi_dry_run_writes_agents_md_manifest(self):
        out = os.path.join(self.tmp, "dry-kimi")
        rc = self.t2.main(["--harness", "kimi", "--probe", "nonexistent-flag",
                           "--cell", "unit:U-dummy", "--dry-run", "--dry-run-out", out])
        self.assertEqual(rc, 0)
        with open(os.path.join(out, "manifest.json")) as f:
            manifest = json.load(f)
        entry = next(m for m in manifest if m["cell"] == "unit:U-dummy")
        self.assertTrue(entry["ambient_path"].endswith("AGENTS.md"))


if __name__ == "__main__":
    unittest.main()
