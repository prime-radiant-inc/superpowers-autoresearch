import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import transcript_utils as tu
from synth import assistant_text, assistant_tool, tool_result, result, write_transcript


class TestTranscriptUtils(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cml-tu-test.")
        self.path = os.path.join(self.tmp, "transcript.jsonl")

    def test_tool_calls_ordered(self):
        write_transcript(self.path, [
            assistant_text("thinking"),
            assistant_tool("Bash", {"command": "ls"}),
            assistant_tool("Write", {"file_path": "a.py", "content": "x=1"}),
        ])
        events = tu.load_events(self.path)
        calls = tu.tool_calls(events)
        self.assertEqual([c["tool"] for c in calls], ["Bash", "Write"])
        self.assertEqual(calls[0]["args"]["command"], "ls")

    def test_assistant_text_concatenates(self):
        write_transcript(self.path, [
            assistant_text("first"),
            assistant_tool("Bash", {"command": "ls"}),
            assistant_text("second"),
        ])
        events = tu.load_events(self.path)
        self.assertEqual(tu.assistant_text(events), "first\nsecond")

    def test_final_result_text_takes_last_result_event(self):
        write_transcript(self.path, [
            assistant_text("hi"),
            result("done"),
        ])
        events = tu.load_events(self.path)
        self.assertEqual(tu.final_result_text(events), "done")

    def test_bash_commands_extracts_command_field(self):
        write_transcript(self.path, [
            assistant_tool("Bash", {"command": "pytest --help"}),
            assistant_tool("Read", {"file_path": "README.md"}),
        ])
        events = tu.load_events(self.path)
        self.assertEqual(tu.bash_commands(events), ["pytest --help"])

    def test_calls_of_filters_by_name(self):
        write_transcript(self.path, [
            assistant_tool("Write", {"file_path": "a.py", "content": "1"}),
            assistant_tool("Edit", {"file_path": "b.py", "old_string": "0", "new_string": "1"}),
            assistant_tool("Bash", {"command": "ls"}),
        ])
        events = tu.load_events(self.path)
        self.assertEqual(len(tu.calls_of(events, "Write", "Edit")), 2)
        self.assertEqual(len(tu.calls_of(events, "Bash")), 1)

    def test_file_write_contents_covers_write_and_edit(self):
        write_transcript(self.path, [
            assistant_tool("Write", {"file_path": "a.py", "content": "hello=1"}),
            assistant_tool("Edit", {"file_path": "b.py", "old_string": "0", "new_string": "world=2"}),
        ])
        events = tu.load_events(self.path)
        self.assertEqual(tu.file_write_contents(events), ["hello=1", "world=2"])

    def test_tool_results_extracts_text_blocks(self):
        write_transcript(self.path, [
            assistant_tool("Bash", {"command": "pytest --help"}),
            tool_result("usage: pytest [options]"),
        ])
        events = tu.load_events(self.path)
        self.assertEqual(tu.tool_results(events), ["usage: pytest [options]"])

    def test_full_text_includes_narration_results_and_final(self):
        write_transcript(self.path, [
            assistant_text("narration"),
            assistant_tool("Bash", {"command": "echo hi"}),
            tool_result("hi"),
            result("final answer"),
        ])
        events = tu.load_events(self.path)
        text = tu.full_text(events)
        self.assertIn("narration", text)
        self.assertIn("hi", text)
        self.assertIn("final answer", text)

    def test_load_events_skips_malformed_lines(self):
        with open(self.path, "w") as f:
            f.write("not json\n")
            f.write('{"type": "assistant", "message": {"content": []}}\n')
            f.write("\n")
        events = tu.load_events(self.path)
        self.assertEqual(len(events), 1)

    def test_git_diff_and_changed_files_against_baseline(self):
        import subprocess
        wd = tempfile.mkdtemp(prefix="cml-tu-git.")
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=wd, check=True)
        subprocess.run(["git", "-c", "user.email=t@t.local", "-c", "user.name=t",
                        "commit", "--allow-empty", "-qm", "baseline"], cwd=wd, check=True)
        with open(os.path.join(wd, "f.txt"), "w") as f:
            f.write("changed\n")
        diff = tu.git_diff(wd)
        self.assertIn("f.txt", diff)
        self.assertIn("f.txt", tu.changed_files(wd))

    def test_diff_numstat_reports_added_lines_for_new_file(self):
        import subprocess
        wd = tempfile.mkdtemp(prefix="cml-tu-numstat.")
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=wd, check=True)
        subprocess.run(["git", "-c", "user.email=t@t.local", "-c", "user.name=t",
                        "commit", "--allow-empty", "-qm", "baseline"], cwd=wd, check=True)
        with open(os.path.join(wd, "new.txt"), "w") as f:
            f.write("a\nb\nc\n")
        rows = tu.diff_numstat(wd)
        self.assertEqual(len(rows), 1)
        added, removed, path = rows[0]
        self.assertEqual(added, 3)
        self.assertEqual(removed, 0)
        self.assertEqual(path, "new.txt")

    def test_added_lines_text_excludes_file_headers_and_context(self):
        import subprocess
        wd = tempfile.mkdtemp(prefix="cml-tu-added.")
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=wd, check=True)
        with open(os.path.join(wd, "f.py"), "w") as f:
            f.write("def a():\n    return 1\n")
        subprocess.run(["git", "-c", "user.email=t@t.local", "-c", "user.name=t",
                        "add", "-A"], cwd=wd, check=True)
        subprocess.run(["git", "-c", "user.email=t@t.local", "-c", "user.name=t",
                        "commit", "-qm", "baseline"], cwd=wd, check=True)
        with open(os.path.join(wd, "f.py"), "w") as f:
            f.write("def a():\n    return 1\n\n\nclass Widget:\n    pass\n")
        added = tu.added_lines_text(wd)
        self.assertIn("class Widget", added)
        self.assertNotIn("+++", added)
        self.assertNotIn("def a():", added)  # unchanged context line, not an addition


if __name__ == "__main__":
    unittest.main()
