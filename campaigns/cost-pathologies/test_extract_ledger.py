"""Tests for extract_ledger.py (queue-execution campaign, Task 4, item 23).

Item 23's problem: a battery rep's `.superpowers/sdd/<plan>/progress.md`
scratch ledger is deleted by the coding-agent's own SDD finishing step
before quorum captures results -- by design, this extractor does NOT
change any agent-visible behavior to preserve it (that would alter the
system under test). The recovery is post hoc: every write to progress.md
went through the codex `apply_patch` tool, whose invocation and outcome
ARE captured in the rep's raw rollout JSONL (never deleted). Real corpus
shape, verified directly against `evals/results/cp-x2-advisory-control-
rep1`'s root rollout before writing this module (see extract_ledger.py's
own module docstring for the exact records): apply_patch runs through the
`custom_tool_call`/name=="exec" encoding, as a JS snippet --

    const patch = "*** Begin Patch\\n*** Add File: <path>\\n+<line>\\n..."
      "*** End Patch";
    text(await tools.apply_patch(patch));

-- using codex's own V4A patch dialect (`*** Add/Delete/Update File:`,
`@@` hunks with ` `/`-`/`+`-prefixed lines). This module implements just
enough of that dialect to reconstruct one target file's content by
folding every apply_patch call touching it, in chronological order, NOT
a general-purpose patch engine (see extract_ledger.py's docstring for the
deliberate scope cut).

Fixtures here are synthetic (built inline, matching this campaign's
test_score_x5_leases.py style) -- the REAL 2-rep corpus validation (item
23's "must recover a real ledger from at least 2 real reps" requirement)
is run separately, directly against evals/results and evals-lane-b/
results (read-only), and reported in task-4-report.md, not encoded here
as a pytest test (those results dirs are outside this repo and not a
portable/committed fixture)."""
import json
import os
import tempfile
import unittest

import extract_ledger as el


def _rec(ts, typ, payload):
    return json.dumps({"timestamp": ts, "type": typ, "payload": payload})


def custom_exec_cmd(ts, call_id, raw_input):
    """custom_tool_call/"exec" encoding -- `input` is raw JS source, taken
    WHOLE, matching test_score_x5_leases.py's helper of the same name and
    rollout_parser.exec_commands()'s documented shape."""
    return _rec(ts, "response_item", {
        "type": "custom_tool_call", "id": call_id, "name": "exec",
        "input": raw_input, "call_id": call_id})


def apply_patch_js(patch_text):
    """Wrap PATCH_TEXT (real newlines/quotes) in the exact JS-string-
    literal + apply_patch-call shape the real corpus emits, JS-escaping
    `\\`, `"`, and newlines -- the inverse of extract_ledger's
    de-escaping, so tests build fixtures the way the real harness would
    have emitted them, not by hand-escaping strings."""
    escaped = (patch_text.replace("\\", "\\\\")
               .replace('"', '\\"')
               .replace("\n", "\\n"))
    return f'const patch = "{escaped}";\ntext(await tools.apply_patch(patch));'


class TestParsePatchSections(unittest.TestCase):
    def test_add_file(self):
        patch = ("*** Begin Patch\n"
                  "*** Add File: /work/.superpowers/sdd/plan/progress.md\n"
                  "+# SDD ledger\n"
                  "+Decision: use integers.\n"
                  "*** End Patch")
        sections = el.parse_patch_sections(patch)
        self.assertEqual(len(sections), 1)
        sec = sections[0]
        self.assertEqual(sec.action, "add")
        self.assertEqual(sec.path, "/work/.superpowers/sdd/plan/progress.md")
        self.assertEqual(sec.lines, ["# SDD ledger", "Decision: use integers."])

    def test_update_file_single_hunk(self):
        patch = ("*** Begin Patch\n"
                  "*** Update File: /work/.superpowers/sdd/plan/progress.md\n"
                  "@@\n"
                  " Decision: use integers.\n"
                  "+Task 1: complete\n"
                  "*** End Patch")
        sections = el.parse_patch_sections(patch)
        self.assertEqual(len(sections), 1)
        sec = sections[0]
        self.assertEqual(sec.action, "update")
        self.assertEqual(len(sec.hunks), 1)
        self.assertEqual(sec.hunks[0], [
            (" ", "Decision: use integers."),
            ("+", "Task 1: complete"),
        ])

    def test_delete_and_add_combined_real_corpus_shape(self):
        # Verified directly against evals/results/cp-x2-advisory-control-
        # rep1's root rollout: codex sometimes bundles an unrelated Delete
        # File (e.g. package-lock.json) in the SAME patch call as the
        # Add File that first creates progress.md.
        patch = ("*** Begin Patch\n"
                  "*** Delete File: /work/package-lock.json\n"
                  "*** Add File: /work/.superpowers/sdd/plan/progress.md\n"
                  "+# SDD ledger\n"
                  "*** End Patch")
        sections = el.parse_patch_sections(patch)
        self.assertEqual([s.action for s in sections], ["delete", "add"])
        self.assertEqual(sections[0].path, "/work/package-lock.json")
        self.assertEqual(sections[1].path,
                          "/work/.superpowers/sdd/plan/progress.md")
        self.assertEqual(sections[1].lines, ["# SDD ledger"])

    def test_update_file_multiple_hunks(self):
        patch = ("*** Begin Patch\n"
                  "*** Update File: /work/progress.md\n"
                  "@@\n"
                  " line one\n"
                  "+line two\n"
                  "@@\n"
                  " line two\n"
                  "+line three\n"
                  "*** End Patch")
        sections = el.parse_patch_sections(patch)
        self.assertEqual(len(sections), 1)
        self.assertEqual(len(sections[0].hunks), 2)
        self.assertEqual(sections[0].hunks[1], [
            (" ", "line two"), ("+", "line three"),
        ])


class TestApplySections(unittest.TestCase):
    def test_add_then_update_appends_in_order(self):
        state = {}
        warnings = []
        add_patch = ("*** Begin Patch\n"
                      "*** Add File: /p/progress.md\n"
                      "+Decision: use integers.\n"
                      "*** End Patch")
        upd1 = ("*** Begin Patch\n"
                "*** Update File: /p/progress.md\n"
                "@@\n"
                " Decision: use integers.\n"
                "+Task 1: complete\n"
                "*** End Patch")
        upd2 = ("*** Begin Patch\n"
                "*** Update File: /p/progress.md\n"
                "@@\n"
                " Task 1: complete\n"
                "+Task 2: complete\n"
                "*** End Patch")
        for patch in (add_patch, upd1, upd2):
            el.apply_sections(state, el.parse_patch_sections(patch), warnings)
        self.assertEqual(state["/p/progress.md"], [
            "Decision: use integers.", "Task 1: complete", "Task 2: complete",
        ])
        self.assertEqual(warnings, [])

    def test_context_miss_falls_back_to_append_with_warning(self):
        state = {"/p/progress.md": ["Decision: use integers."]}
        warnings = []
        upd = ("*** Begin Patch\n"
               "*** Update File: /p/progress.md\n"
               "@@\n"
               " this context line was never actually in the file\n"
               "+Task 1: complete\n"
               "*** End Patch")
        el.apply_sections(state, el.parse_patch_sections(upd), warnings,
                           source_desc="test-rollout@ts1")
        # Not dropped: the addition still lands, appended.
        self.assertEqual(state["/p/progress.md"],
                          ["Decision: use integers.", "Task 1: complete"])
        self.assertEqual(len(warnings), 1)
        self.assertIn("context not found", warnings[0])
        self.assertIn("test-rollout@ts1", warnings[0])

    def test_update_with_no_prior_add_starts_from_empty_and_warns(self):
        state = {}
        warnings = []
        upd = ("*** Begin Patch\n"
               "*** Update File: /p/progress.md\n"
               "@@\n"
               "+Task 1: complete\n"
               "*** End Patch")
        el.apply_sections(state, el.parse_patch_sections(upd), warnings,
                           source_desc="test-rollout@ts1")
        self.assertEqual(state["/p/progress.md"], ["Task 1: complete"])
        self.assertTrue(any("no prior recovered content" in w for w in warnings))

    def test_delete_section_clears_tracked_path(self):
        state = {"/p/progress.md": ["x"]}
        warnings = []
        patch = ("*** Begin Patch\n"
                  "*** Delete File: /p/progress.md\n"
                  "*** End Patch")
        el.apply_sections(state, el.parse_patch_sections(patch), warnings)
        self.assertNotIn("/p/progress.md", state)


class TestFindApplyPatchCalls(unittest.TestCase):
    def test_extracts_and_deescapes_real_shape(self):
        patch_text = ('*** Begin Patch\n'
                       '*** Add File: /p/progress.md\n'
                       '+# SDD ledger\n'
                       '+A line with a "quoted word" in it.\n'
                       '*** End Patch')
        js = apply_patch_js(patch_text)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "rollout-x.jsonl")
            with open(path, "w") as f:
                f.write(custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", js) + "\n")
            calls = el.find_apply_patch_calls(path)
        self.assertEqual(len(calls), 1)
        ts, recovered = calls[0]
        self.assertEqual(ts, "2026-08-01T00:00:00.000Z")
        self.assertEqual(recovered, patch_text)

    def test_ignores_unrelated_exec_calls(self):
        js = 'text(await exec_command({"cmd": "npm test"}));'
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "rollout-x.jsonl")
            with open(path, "w") as f:
                f.write(custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", js) + "\n")
            calls = el.find_apply_patch_calls(path)
        self.assertEqual(calls, [])


class TestRecoverFiles(unittest.TestCase):
    def _write_rollout(self, path, records):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            for r in records:
                f.write(r + "\n")

    def test_end_to_end_single_rollout(self):
        add_patch = ("*** Begin Patch\n"
                      "*** Add File: /p/.superpowers/sdd/plan/progress.md\n"
                      "+# SDD ledger\n"
                      "+Decision: use integers.\n"
                      "*** End Patch")
        upd_patch = ("*** Begin Patch\n"
                     "*** Update File: /p/.superpowers/sdd/plan/progress.md\n"
                     "@@\n"
                     " Decision: use integers.\n"
                     "+Task 1: complete\n"
                     "*** End Patch")
        with tempfile.TemporaryDirectory() as tmp:
            # Dot-directory-nested like a real rep dir: <rep>/<run>/home/
            # .codex/sessions/2026/08/01/rollout-...jsonl (item 23's own
            # "dot-directory warning" -- must be found via find_files, not
            # a bare glob).
            rollout = os.path.join(
                tmp, "run1", "home", ".codex", "sessions", "2026", "08", "01",
                "rollout-2026-08-01T00-00-00-abc.jsonl")
            self._write_rollout(rollout, [
                custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1",
                                 apply_patch_js(add_patch)),
                custom_exec_cmd("2026-08-01T00:01:00.000Z", "c2",
                                 apply_patch_js(upd_patch)),
            ])
            state, warnings = el.recover_files(tmp)
        self.assertEqual(warnings, [])
        self.assertEqual(len(state), 1)
        content = state["/p/.superpowers/sdd/plan/progress.md"]
        self.assertEqual(
            content,
            "# SDD ledger\nDecision: use integers.\nTask 1: complete")

    def test_global_timestamp_order_across_two_rollout_files(self):
        # Root and a subagent each get their own rollout file; the
        # subagent's update is timestamped BEFORE the root's second
        # update finishes, so per-FILE order (root file fully, then
        # subagent file) would splice this wrong -- only GLOBAL
        # timestamp order produces "Decision.\nFrom subagent.\nFrom root."
        add_patch = ("*** Begin Patch\n"
                      "*** Add File: /p/progress.md\n"
                      "+Decision.\n"
                      "*** End Patch")
        subagent_patch = ("*** Begin Patch\n"
                           "*** Update File: /p/progress.md\n"
                           "@@\n"
                           " Decision.\n"
                           "+From subagent.\n"
                           "*** End Patch")
        root_patch2 = ("*** Begin Patch\n"
                       "*** Update File: /p/progress.md\n"
                       "@@\n"
                       " From subagent.\n"
                       "+From root.\n"
                       "*** End Patch")
        with tempfile.TemporaryDirectory() as tmp:
            root_dir = os.path.join(tmp, "run1", "home", ".codex", "sessions",
                                     "2026", "08", "01")
            self._write_rollout(
                os.path.join(root_dir, "rollout-2026-08-01T00-00-00-root.jsonl"),
                [
                    custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1",
                                     apply_patch_js(add_patch)),
                    # root's second update is written to file FIRST (lower
                    # position in ITS OWN file) but happens LATER in real
                    # time than the subagent's update below.
                    custom_exec_cmd("2026-08-01T00:05:00.000Z", "c3",
                                     apply_patch_js(root_patch2)),
                ])
            self._write_rollout(
                os.path.join(root_dir, "rollout-2026-08-01T00-01-00-child.jsonl"),
                [
                    custom_exec_cmd("2026-08-01T00:02:00.000Z", "c2",
                                     apply_patch_js(subagent_patch)),
                ])
            state, warnings = el.recover_files(tmp, path_suffix="progress.md")
        self.assertEqual(warnings, [])
        self.assertEqual(state["/p/progress.md"],
                          "Decision.\nFrom subagent.\nFrom root.")

    def test_ignores_paths_not_matching_suffix(self):
        patch = ("*** Begin Patch\n"
                  "*** Add File: /p/README.md\n"
                  "+hello\n"
                  "*** End Patch")
        with tempfile.TemporaryDirectory() as tmp:
            rollout = os.path.join(tmp, "run1", "home", ".codex", "sessions",
                                    "2026", "08", "01", "rollout-x.jsonl")
            self._write_rollout(rollout, [
                custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1",
                                 apply_patch_js(patch)),
            ])
            state, _ = el.recover_files(tmp, path_suffix="progress.md")
        self.assertEqual(state, {})

    def test_finishing_step_deletion_of_target_survives_recovery(self):
        # Real-corpus-discovered case (evals/results/cp-x2-advisory-x2a-
        # rep1): the SDD finishing step's own apply_patch DELETES
        # progress.md as its last write -- exactly the deletion this tool
        # exists to see past. A naive replay (apply_sections' own general,
        # correct delete semantics) would erase the recovered content;
        # recover_files() must NOT do that for the target path.
        add_patch = ("*** Begin Patch\n"
                      "*** Add File: /p/progress.md\n"
                      "+Decision: use integers.\n"
                      "*** End Patch")
        upd_patch = ("*** Begin Patch\n"
                     "*** Update File: /p/progress.md\n"
                     "@@\n"
                     " Decision: use integers.\n"
                     "+Task 1: complete\n"
                     "*** End Patch")
        # Real shape: the finishing step's delete patch also deletes OTHER
        # SDD scratch files in the SAME apply_patch call.
        delete_patch = ("*** Begin Patch\n"
                         "*** Delete File: /p/progress.md\n"
                         "*** Delete File: /p/review-1.diff\n"
                         "*** End Patch")
        with tempfile.TemporaryDirectory() as tmp:
            rollout = os.path.join(tmp, "run1", "home", ".codex", "sessions",
                                    "2026", "08", "01", "rollout-x.jsonl")
            self._write_rollout(rollout, [
                custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1",
                                 apply_patch_js(add_patch)),
                custom_exec_cmd("2026-08-01T00:01:00.000Z", "c2",
                                 apply_patch_js(upd_patch)),
                custom_exec_cmd("2026-08-01T00:02:00.000Z", "c3",
                                 apply_patch_js(delete_patch)),
            ])
            state, warnings = el.recover_files(tmp)
        self.assertEqual(state["/p/progress.md"],
                          "Decision: use integers.\nTask 1: complete")
        self.assertTrue(any("was deleted by the session" in w for w in warnings))

    def test_no_matches_returns_empty_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            rollout = os.path.join(tmp, "run1", "home", ".codex", "sessions",
                                    "2026", "08", "01", "rollout-x.jsonl")
            self._write_rollout(rollout, [
                custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", "true"),
            ])
            state, warnings = el.recover_files(tmp)
        self.assertEqual(state, {})
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
