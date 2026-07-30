"""Tests for score_t4_regression.py's ATIF ceremony census scorer (Task 10).
Synthetic ATIF v1.7 trajectory fixtures only -- fake agent name/version,
minimal hand-built steps -- no real trajectory content, no client data.

Covers: the three required fixtures (full-ceremony, bounded-lean,
doc-only-readme) loaded from fixtures/atif-ceremony/*.json, the
docs/superpowers/(specs|plans)/ vs. docs/ vs. root-*.md path
classifiers, writing_plans_invoked detection (both a discrete Read
tool-call path and a path embedded in a Bash-style command string),
root-only... (there is no root/child distinction here -- this scorer is
single-trajectory), user-turn counting, and the no-code-write fallback."""
import json
import pathlib
import unittest

import score_t4_regression as st

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "atif-ceremony"


def load_fixture(name):
    with open(FIXTURES / f"{name}.json") as f:
        return json.load(f)


def traj(steps, agent_name="synthetic", agent_version="0.0.0"):
    return {
        "schema_version": "ATIF-v1.7",
        "agent": {"name": agent_name, "version": agent_version},
        "steps": steps,
    }


def user_step(step_id, message):
    return {"step_id": step_id, "source": "user", "message": message}


def write_step(step_id, path, call_id="c", content="x"):
    return {"step_id": step_id, "source": "agent", "tool_calls": [
        {"tool_call_id": call_id, "function_name": "Write",
         "arguments": {"file_path": path, "content": content}}]}


def read_step(step_id, path, call_id="c"):
    return {"step_id": step_id, "source": "agent", "tool_calls": [
        {"tool_call_id": call_id, "function_name": "Read",
         "arguments": {"file_path": path}}]}


def bash_step(step_id, command, call_id="c"):
    return {"step_id": step_id, "source": "agent", "tool_calls": [
        {"tool_call_id": call_id, "function_name": "Bash",
         "arguments": {"command": command}}]}


class TestRequiredFixtures(unittest.TestCase):
    def test_full_ceremony(self):
        """(a) spec doc, then plan doc, then code -- both ceremony docs
        counted, both land before the code write, writing-plans skill
        read is detected."""
        census = st.score_trajectory(load_fixture("full-ceremony"))
        self.assertEqual(census["spec_docs_written"], 1)
        self.assertEqual(census["plan_docs_written"], 1)
        self.assertEqual(census["doc_writes_before_first_code"], 2)
        self.assertEqual(census["first_code_file"], "src/app.py")
        self.assertEqual(census["user_turns_before_first_code"], 1)
        self.assertTrue(census["writing_plans_invoked"])

    def test_bounded_lean(self):
        """(b) code file written first, no docs at all -- zero ceremony,
        no writing-plans invocation."""
        census = st.score_trajectory(load_fixture("bounded-lean"))
        self.assertEqual(census["spec_docs_written"], 0)
        self.assertEqual(census["plan_docs_written"], 0)
        self.assertEqual(census["doc_writes_before_first_code"], 0)
        self.assertEqual(census["first_code_file"], "src/app.py")
        self.assertEqual(census["user_turns_before_first_code"], 1)
        self.assertFalse(census["writing_plans_invoked"])

    def test_doc_only_readme(self):
        """(c) README.md written, then code -- README is NOT a ceremony
        doc (doesn't match docs/superpowers/(specs|plans)/) and, being a
        root-level *.md file, is also not classified as code."""
        census = st.score_trajectory(load_fixture("doc-only-readme"))
        self.assertEqual(census["spec_docs_written"], 0)
        self.assertEqual(census["plan_docs_written"], 0)
        self.assertEqual(census["doc_writes_before_first_code"], 0)
        self.assertEqual(census["first_code_file"], "src/app.py")
        self.assertEqual(census["user_turns_before_first_code"], 1)
        self.assertFalse(census["writing_plans_invoked"])


class TestPathClassifiers(unittest.TestCase):
    def test_ceremony_doc_kind_specs(self):
        self.assertEqual(st.ceremony_doc_kind("docs/superpowers/specs/2026-01-01-x.md"), "specs")

    def test_ceremony_doc_kind_plans(self):
        self.assertEqual(st.ceremony_doc_kind("docs/superpowers/plans/2026-01-01-x.md"), "plans")

    def test_ceremony_doc_kind_none_for_other_docs(self):
        self.assertIsNone(st.ceremony_doc_kind("docs/README.md"))
        self.assertIsNone(st.ceremony_doc_kind("docs/superpowers/reports/x.md"))
        self.assertIsNone(st.ceremony_doc_kind("README.md"))

    def test_is_code_path_excludes_docs_subtree(self):
        self.assertFalse(st.is_code_path("docs/superpowers/specs/x.md"))
        self.assertFalse(st.is_code_path("docs/notes.txt"))

    def test_is_code_path_excludes_root_md(self):
        self.assertFalse(st.is_code_path("README.md"))
        self.assertFalse(st.is_code_path("CHANGELOG.MD"))

    def test_is_code_path_includes_nested_non_docs_files(self):
        self.assertTrue(st.is_code_path("src/app.py"))
        self.assertTrue(st.is_code_path("tests/test_app.py"))
        # A *.md file that is NOT at repo root is still, per the literal
        # rule ("not *.md at repo root"), a code path.
        self.assertTrue(st.is_code_path("src/README.md"))

    def test_is_code_path_empty_string_is_false(self):
        self.assertFalse(st.is_code_path(""))


class TestWritingPlansInvoked(unittest.TestCase):
    def test_detected_via_discrete_read_path(self):
        t = traj([
            user_step(1, "hi"),
            read_step(2, "/workspace/superpowers/skills/writing-plans/SKILL.md"),
            write_step(3, "src/app.py"),
        ])
        self.assertTrue(st.score_trajectory(t)["writing_plans_invoked"])

    def test_detected_via_command_embedded_path(self):
        """Some harnesses (e.g. codex) read a skill file via a shell
        command rather than a discrete Read tool call -- the path lives
        inside the Bash tool's `command` string, not a `file_path`
        argument. Detection must still find it."""
        t = traj([
            user_step(1, "hi"),
            bash_step(2, "sed -n '1,200p' /workspace/superpowers/skills/writing-plans/SKILL.md"),
            write_step(3, "src/app.py"),
        ])
        self.assertTrue(st.score_trajectory(t)["writing_plans_invoked"])

    def test_not_detected_when_absent(self):
        t = traj([
            user_step(1, "hi"),
            bash_step(2, "sed -n '1,200p' /workspace/superpowers/skills/brainstorming/SKILL.md"),
            write_step(3, "src/app.py"),
        ])
        self.assertFalse(st.score_trajectory(t)["writing_plans_invoked"])

    def test_not_detected_from_write_call_content_mentioning_the_path(self):
        """A Write call's `content` merely mentioning the skill path in
        prose (e.g. a plan doc that narrates "used the writing-plans
        skill") is not a READ -- writing that text must not itself set
        writing_plans_invoked. Only read-shaped calls (Read-type tools,
        Bash command strings) count."""
        t = traj([
            user_step(1, "hi"),
            write_step(2, "docs/superpowers/plans/x.md",
                       content="This plan says we used the skills/writing-plans skill."),
            write_step(3, "src/app.py"),
        ])
        self.assertFalse(st.score_trajectory(t)["writing_plans_invoked"])


class TestUserTurnsAndNoCodeFallback(unittest.TestCase):
    def test_counts_multiple_clarifying_turns_before_code(self):
        t = traj([
            user_step(1, "build the thing"),
            user_step(2, "clarification: use sqlite"),
            write_step(3, "src/app.py"),
        ])
        census = st.score_trajectory(t)
        self.assertEqual(census["user_turns_before_first_code"], 2)

    def test_no_code_write_reports_null_and_falls_back_to_whole_trajectory(self):
        """A run that never writes a real code file (pure investigation,
        or docs-only) must report first_code_file=None rather than
        crashing or misattributing a doc path as code; the other counts
        fall back to covering the whole trajectory (no cutoff to gate
        on), mirroring score_e4.py's no_non_doc_patch convention."""
        t = traj([
            user_step(1, "investigate"),
            user_step(2, "still investigating"),
            write_step(3, "docs/superpowers/specs/x.md"),
        ])
        census = st.score_trajectory(t)
        self.assertIsNone(census["first_code_file"])
        self.assertEqual(census["spec_docs_written"], 1)
        self.assertEqual(census["doc_writes_before_first_code"], 1)
        self.assertEqual(census["user_turns_before_first_code"], 2)


class TestScoreFile(unittest.TestCase):
    def test_score_file_loads_and_scores(self):
        census = st.score_file(str(FIXTURES / "bounded-lean.json"))
        self.assertEqual(census["first_code_file"], "src/app.py")


if __name__ == "__main__":
    unittest.main()
