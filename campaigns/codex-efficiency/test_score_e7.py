"""Tests for score_e7.py (E7 wait-polling census, Amendment 1). Synthetic
rollout fixtures only -- hand-built wait_agent/function_call_output/
token_count records, no real rollouts, no corpus content.

Scope, deliberately narrow: the FORCE overwrite guard (score_e7 was the
only scorer of the ten writing its four corpus JSON blobs unconditionally)
plus one census regression test pinning `census_session()`'s pairing and
rate arithmetic against a fixture whose expected values are hand-derived.
The wait-pairing primitive itself is `rollout_parser.wait_outcomes()`,
already covered by test_rollout_parser.py, and the three corpus loaders
(`score_drew`/`score_audit`/`score_battery`) read external corpora that
cannot be fixtured -- their ground-truth reproduction is the corpus
reconciliation in out/e7-report.md, not a unit test."""
import json
import pathlib
import tempfile
import unittest

import score_e7 as se


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def wait_call(ts, call_id, timeout_ms=30000):
    return _rec(ts, "response_item", {
        "type": "function_call", "name": "wait_agent",
        "namespace": "collaboration", "call_id": call_id,
        "arguments": json.dumps({"target": "agent-1", "timeout_ms": timeout_ms})})


def wait_output(ts, call_id, timed_out):
    return _rec(ts, "response_item", {
        "type": "function_call_output", "call_id": call_id,
        "output": json.dumps({"message": "status", "timed_out": timed_out})})


def wait_error_output(ts, call_id):
    """The real argument-validation shape: a bare string, not a JSON object."""
    return _rec(ts, "response_item", {
        "type": "function_call_output", "call_id": call_id,
        "output": "timeout_ms must be at least 10000"})


def other_tool_call(ts, call_id, name="exec_command"):
    return _rec(ts, "response_item", {
        "type": "function_call", "name": name, "call_id": call_id,
        "arguments": json.dumps({"cmd": "true"})})


def token_count(ts, cached_input_tokens):
    return _rec(ts, "event_msg", {
        "type": "token_count",
        "info": {"last_token_usage": {"cached_input_tokens": cached_input_tokens}}})


class TestCensusSession(unittest.TestCase):
    """One regression fixture: 4 wait_agent calls, 3 of them resolvable
    (2 timed out, 1 not), 1 unresolvable (validation-error output). Every
    expected number below is hand-derived from these records."""

    def _fixture(self, tmp):
        path = pathlib.Path(tmp) / "rollout-2026-07-30T00-00-00-fixture.jsonl"
        path.write_text("\n".join([
            token_count("2026-07-30T00:00:00.000Z", 100),
            wait_call("2026-07-30T00:00:10.000Z", "c1"),
            wait_output("2026-07-30T00:00:40.000Z", "c1", True),
            wait_call("2026-07-30T00:00:50.000Z", "c2"),
            wait_output("2026-07-30T00:01:20.000Z", "c2", True),
            wait_call("2026-07-30T00:01:30.000Z", "c3"),
            wait_output("2026-07-30T00:01:35.000Z", "c3", False),
            wait_call("2026-07-30T00:01:40.000Z", "c4", timeout_ms=5000),
            wait_error_output("2026-07-30T00:01:41.000Z", "c4"),
            other_tool_call("2026-07-30T00:01:50.000Z", "x1"),
            token_count("2026-07-30T00:02:00.000Z", 400),
        ]) + "\n")
        return str(path)

    def test_counts_and_rates(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = se.census_session(self._fixture(tmp), label="fx")
            self.assertEqual(s["label"], "fx")
            # All four calls are counted as calls; only three pair to a
            # genuine outcome; the validation-error call is excluded, not
            # guessed at.
            self.assertEqual(s["n_wait_agent_calls"], 4)
            self.assertEqual(s["n_paired"], 3)
            self.assertEqual(s["n_excluded"], 1)
            self.assertEqual(s["n_timed_out"], 2)
            self.assertAlmostEqual(s["timeout_rate_of_paired"], 2 / 3)
            self.assertAlmostEqual(s["timeout_rate_of_all_calls"], 2 / 4)

    def test_inter_poll_intervals_come_from_all_calls(self):
        """Cadence is observable even for the unresolvable call -- the
        intervals must span all four call timestamps, not just paired ones."""
        with tempfile.TemporaryDirectory() as tmp:
            s = se.census_session(self._fixture(tmp))
            self.assertEqual(s["inter_poll_intervals_s"], [40.0, 40.0, 10.0])

    def test_no_wait_calls_yields_null_rates_not_zero_division(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "rollout-empty.jsonl"
            path.write_text(other_tool_call("2026-07-30T00:00:00.000Z", "x1") + "\n")
            s = se.census_session(str(path))
            self.assertEqual(s["n_wait_agent_calls"], 0)
            self.assertIsNone(s["timeout_rate_of_paired"])
            self.assertIsNone(s["timeout_rate_of_all_calls"])


class TestForceGuard(unittest.TestCase):
    """score_e7 writes four corpus blobs; the guard must be all-or-nothing
    so a refusal never leaves a half-updated out/ directory."""

    def _corpora(self):
        sessions = [{"path": "p", "label": "l", "n_wait_agent_calls": 0,
                     "n_paired": 0, "n_excluded": 0, "n_timed_out": 0,
                     "timeout_rate_of_paired": None,
                     "timeout_rate_of_all_calls": None,
                     "inter_poll_intervals_s": [], "cache_rebill_tokens": 0,
                     "cache_rebill_method": "proxy", "waits": []}]
        return (("alpha", {"g": sessions}), ("beta", {"g": sessions}))

    def test_writes_when_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths, wrote = se.write_outputs(self._corpora(), tmp, force=False)
            self.assertTrue(wrote)
            self.assertEqual([pathlib.Path(p).name for p in paths],
                             ["e7-alpha.json", "e7-beta.json"])
            for p in paths:
                self.assertTrue(pathlib.Path(p).exists())

    def test_strips_waits_from_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths, _ = se.write_outputs(self._corpora(), tmp, force=False)
            blob = json.loads(pathlib.Path(paths[0]).read_text())
            self.assertNotIn("waits", blob["g"]["sessions"][0])
            self.assertIn("aggregate", blob["g"])

    def test_refuses_existing_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = pathlib.Path(tmp) / "e7-beta.json"
            existing.write_text('{"sentinel": true}')
            paths, wrote = se.write_outputs(self._corpora(), tmp, force=False)
            self.assertFalse(wrote)
            self.assertEqual(json.loads(existing.read_text()), {"sentinel": True})

    def test_refusal_is_atomic_no_partial_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            (pathlib.Path(tmp) / "e7-beta.json").write_text('{"sentinel": true}')
            se.write_outputs(self._corpora(), tmp, force=False)
            self.assertFalse((pathlib.Path(tmp) / "e7-alpha.json").exists())

    def test_force_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = pathlib.Path(tmp) / "e7-beta.json"
            existing.write_text('{"sentinel": true}')
            paths, wrote = se.write_outputs(self._corpora(), tmp, force=True)
            self.assertTrue(wrote)
            self.assertNotIn("sentinel", json.loads(existing.read_text()))


if __name__ == "__main__":
    unittest.main()
