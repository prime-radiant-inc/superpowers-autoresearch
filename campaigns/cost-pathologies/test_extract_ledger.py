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
        self.assertEqual(calls[0].timestamp, "2026-08-01T00:00:00.000Z")
        self.assertEqual(calls[0].patch_text, patch_text)

    def test_ignores_unrelated_exec_calls(self):
        js = 'text(await exec_command({"cmd": "npm test"}));'
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "rollout-x.jsonl")
            with open(path, "w") as f:
                f.write(custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", js) + "\n")
            calls = el.find_apply_patch_calls(path)
        self.assertEqual(calls, [])


class TestFindApplyPatchCallsShapes(unittest.TestCase):
    """Round-1 review fix: PATCH_VAR_RE originally matched ONLY the plain
    `const patch = "...";` double-quoted shape. Independent review found
    (and I re-verified directly against the raw corpus, see
    task-4-report.md) at least 3 more real shapes that were silently
    dropped with zero warning: a backtick/template-literal `const patch =
    \\`...\\`;` (possibly with `${name}` interpolation of an earlier
    simple `const name = "...";`), an inline literal argument with NO
    intermediate variable at all (either quote style), a `"lit"+var+
    "lit"`-style concatenation expression, and a genuinely dynamic
    (loop-built, `+=`-mutated) patch variable that can't be resolved at
    all and must WARN, never silently vanish."""

    def _run(self, js, path_suffix="progress.md"):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "rollout-x.jsonl")
            with open(path, "w") as f:
                f.write(custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", js) + "\n")
            return el.find_apply_patch_calls(path)

    def test_backtick_literal_direct_argument_with_interpolation(self):
        # Real corpus shape (cp-x8-approvals-x8a-rep1): a template
        # literal passed straight to apply_patch, no `patch`-named
        # variable, interpolating a simple prior string const.
        js = ('const p="/p/progress.md";\n'
              'text(await tools.apply_patch(`*** Begin Patch\\n'
              '*** Add File: ${p}\\n+# SDD ledger\\n*** End Patch`));')
        calls = self._run(js)
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].patch_text,
            "*** Begin Patch\n*** Add File: /p/progress.md\n"
            "+# SDD ledger\n*** End Patch")

    def test_backtick_literal_via_named_variable(self):
        # Real corpus shape (cp-x8-approvals-x8a-rep2): `const patch =`
        # assigned a BACKTICK (not double-quoted) template literal.
        js = ('const ws="/p";\n'
              'const patch=`*** Begin Patch\\n*** Update File: ${ws}/progress.md\\n'
              '@@\\n Decision.\\n+Task 1: complete\\n*** End Patch`;\n'
              'text(await tools.apply_patch(patch));')
        calls = self._run(js)
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].patch_text,
            "*** Begin Patch\n*** Update File: /p/progress.md\n"
            "@@\n Decision.\n+Task 1: complete\n*** End Patch")

    def test_direct_double_quoted_literal_no_variable(self):
        # Real corpus shape (cp-x8-approvals-x8a-rep1): a plain
        # double-quoted literal passed straight to apply_patch.
        js = ('text(await tools.apply_patch('
              '"*** Begin Patch\\n*** Delete File: /p/progress.md\\n*** End Patch"));')
        calls = self._run(js)
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].patch_text,
            "*** Begin Patch\n*** Delete File: /p/progress.md\n*** End Patch")

    def test_concatenation_expression_via_named_variable(self):
        # Real corpus shape (cp-x8-approvals-x8a-rep3): a direct argument
        # built from "literal"+var+"literal" concatenation, no template
        # literal and no `const patch =` at all.
        js = ('const p="/p/progress.md";\n'
              'text(await tools.apply_patch('
              '"*** Begin Patch\\n*** Add File: "+p+'
              '"\\n+# SDD ledger\\n*** End Patch"));')
        calls = self._run(js)
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0].patch_text,
            "*** Begin Patch\n*** Add File: /p/progress.md\n"
            "+# SDD ledger\n*** End Patch")

    def test_dynamic_loop_built_patch_is_unresolved_not_dropped(self):
        # Real corpus shape (cp-x8-approvals-x8a-rep1): a patch built via
        # a loop and `+=` mutation -- genuinely not statically resolvable.
        # Must NOT be silently dropped: still returned, patch_text=None,
        # with the raw input preserved so a caller can decide relevance.
        js = ('const base="/p";\n'
              'const files=["a.md","progress.md"];\n'
              'let patch="*** Begin Patch\\n";\n'
              'for (const f of files) patch+=`*** Delete File: ${base}/${f}\\n`;\n'
              'patch+="*** End Patch";\n'
              'text(await tools.apply_patch(patch));')
        calls = self._run(js)
        self.assertEqual(len(calls), 1)
        self.assertIsNone(calls[0].patch_text)
        self.assertIn("progress.md", calls[0].raw_input)

    def test_unresolvable_call_still_recorded_when_irrelevant(self):
        # An unresolvable (dynamic) call that has NOTHING to do with the
        # recovery target must still be reported as unresolved (never
        # silently dropped at this layer) -- relevance filtering is
        # recover_files()'s job, not find_apply_patch_calls()'s.
        js = ('let patch="*** Begin Patch\\n*** Delete File: /p/unrelated.json\\n";\n'
              'patch+="*** End Patch";\n'
              'text(await tools.apply_patch(patch));')
        calls = self._run(js)
        self.assertEqual(len(calls), 1)
        self.assertIsNone(calls[0].patch_text)
        self.assertNotIn("progress.md", calls[0].raw_input)


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

    def test_unresolvable_relevant_apply_patch_call_warns_with_provenance(self):
        # Round-1 review fix: an apply_patch call that mentions the
        # target but can't be resolved (dynamic/loop-built) must produce
        # a warning naming the rep+file provenance, not vanish silently.
        js = ('const files=["progress.md"];\n'
              'let patch="*** Begin Patch\\n";\n'
              'for (const f of files) patch+=`*** Delete File: /p/${f}\\n`;\n'
              'patch+="*** End Patch";\n'
              'text(await tools.apply_patch(patch));')
        with tempfile.TemporaryDirectory() as tmp:
            rollout = os.path.join(tmp, "run1", "home", ".codex", "sessions",
                                    "2026", "08", "01", "rollout-x.jsonl")
            self._write_rollout(rollout, [
                custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", js),
            ])
            state, warnings = el.recover_files(tmp)
        self.assertEqual(state, {})
        self.assertEqual(len(warnings), 1)
        self.assertIn("could not be resolved", warnings[0])
        self.assertIn("rollout-x.jsonl@2026-08-01T00:00:00.000Z", warnings[0])

    def test_unresolvable_irrelevant_apply_patch_call_does_not_warn(self):
        # An unresolvable call with nothing to do with the target must
        # not spam a warning (avoid noise for every unrelated dynamic
        # delete elsewhere in a session).
        js = ('let patch="*** Begin Patch\\n*** Delete File: /p/unrelated.json\\n";\n'
              'patch+="*** End Patch";\n'
              'text(await tools.apply_patch(patch));')
        with tempfile.TemporaryDirectory() as tmp:
            rollout = os.path.join(tmp, "run1", "home", ".codex", "sessions",
                                    "2026", "08", "01", "rollout-x.jsonl")
            self._write_rollout(rollout, [
                custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", js),
            ])
            state, warnings = el.recover_files(tmp)
        self.assertEqual(state, {})
        self.assertEqual(warnings, [])


class TestShellRedirects(unittest.TestCase):
    """Round-1 review fix: a rep's real progress.md writes can go through
    a plain shell `printf ... >> target` redirect (real corpus shape,
    `cp-x8-approvals-control-rep2`: the SDD skill's own `sdd-workspace`/
    task machinery creates and appends to progress.md via shell, never
    apply_patch at all) -- a violation of extract_ledger's originally
    stated assumption ("every write... went through apply_patch"), found
    by independent review, not by this module's own original corpus
    read."""

    def test_printf_create_single_arg(self):
        # `if [ ! -f "$ws/progress.md" ]; then printf '...\n' > "$ws/progress.md"; fi;`
        text = ('if [ ! -f "$ws/progress.md" ]; then printf '
                '\'# SDD ledger — plan: x\\n\' > "$ws/progress.md"; fi;')
        hits = list(el._find_printf_redirects(text, "progress.md"))
        self.assertEqual(len(hits), 1)
        mode, target, lines = hits[0]
        self.assertEqual(mode, "create")
        self.assertEqual(target, "$ws/progress.md")
        self.assertEqual(lines, ["# SDD ledger — plan: x"])

    def test_printf_append_multi_arg(self):
        # `printf '%s\n' 'line one' 'line two' >> target;` (already
        # JS-de-escaped text, one backslash -- see module docstring).
        text = ("printf '%s\\n' 'Task 1: complete (commits a..b, review clean)' "
                "'Task 2: complete (commits b..c, review clean)' "
                ">> .superpowers/sdd/subscriptions-plan/progress.md;")
        hits = list(el._find_printf_redirects(text, "progress.md"))
        self.assertEqual(len(hits), 1)
        mode, target, lines = hits[0]
        self.assertEqual(mode, "append")
        self.assertEqual(target, ".superpowers/sdd/subscriptions-plan/progress.md")
        self.assertEqual(lines, [
            "Task 1: complete (commits a..b, review clean)",
            "Task 2: complete (commits b..c, review clean)",
        ])

    def test_printf_unrecognized_format_yields_none_lines(self):
        text = "printf '%d\\n' '3' >> progress.md;"
        hits = list(el._find_printf_redirects(text, "progress.md"))
        self.assertEqual(len(hits), 1)
        mode, target, lines = hits[0]
        self.assertIsNone(lines)

    def test_printf_ignores_unrelated_target(self):
        text = "printf '%s\\n' 'hi' >> other-file.txt;"
        hits = list(el._find_printf_redirects(text, "progress.md"))
        self.assertEqual(hits, [])

    def test_find_shell_redirects_end_to_end(self):
        js = ('const wt="/p";\n'
              'const r=await tools.exec_command({cmd:`printf \'%s\\\\n\' '
              "'Task 1: complete' >> .superpowers/sdd/plan/progress.md`,"
              'workdir:wt});')
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "rollout-x.jsonl")
            with open(path, "w") as f:
                f.write(custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", js) + "\n")
            hits = el.find_shell_redirects(path, "progress.md")
        self.assertEqual(len(hits), 1)
        ts, mode, target, lines, _raw = hits[0]
        self.assertEqual(ts, "2026-08-01T00:00:00.000Z")
        self.assertEqual(mode, "append")
        self.assertEqual(target, ".superpowers/sdd/plan/progress.md")
        self.assertEqual(lines, ["Task 1: complete"])


class TestRecoverFilesShellRedirect(unittest.TestCase):
    def _write_rollout(self, path, records):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            for r in records:
                f.write(r + "\n")

    def test_create_then_append_recovers_full_ledger(self):
        # Real-corpus-shaped end-to-end: `cp-x8-approvals-control-rep2`'s
        # actual mechanism (create-if-missing, then two appends), never
        # touching apply_patch at all.
        create_js = ('const r=await tools.exec_command({cmd:`if [ ! -f "$ws/progress.md" ]; '
                     "then printf '# SDD ledger\\\\n' > \"$ws/progress.md\"; fi;`});")
        append1_js = ("const r=await tools.exec_command({cmd:`printf '%s\\\\n' "
                      "'Task 1: complete' >> .superpowers/sdd/plan/progress.md`});")
        append2_js = ("const r=await tools.exec_command({cmd:`printf '%s\\\\n' "
                      "'Task 2: complete' >> .superpowers/sdd/plan/progress.md`});")
        with tempfile.TemporaryDirectory() as tmp:
            rollout = os.path.join(tmp, "run1", "home", ".codex", "sessions",
                                    "2026", "08", "01", "rollout-x.jsonl")
            self._write_rollout(rollout, [
                custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", create_js),
                custom_exec_cmd("2026-08-01T00:01:00.000Z", "c2", append1_js),
                custom_exec_cmd("2026-08-01T00:02:00.000Z", "c3", append2_js),
            ])
            state, warnings = el.recover_files(tmp)
        self.assertEqual(warnings, [])
        self.assertEqual(state["$ws/progress.md"], "# SDD ledger")
        self.assertEqual(state[".superpowers/sdd/plan/progress.md"],
                          "Task 1: complete\nTask 2: complete")

    def test_unresolved_printf_format_warns_with_provenance(self):
        js = ("const r=await tools.exec_command({cmd:`printf '%d\\\\n' '3' "
              ">> .superpowers/sdd/plan/progress.md`});")
        with tempfile.TemporaryDirectory() as tmp:
            rollout = os.path.join(tmp, "run1", "home", ".codex", "sessions",
                                    "2026", "08", "01", "rollout-x.jsonl")
            self._write_rollout(rollout, [
                custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1", js),
            ])
            state, warnings = el.recover_files(tmp)
        self.assertEqual(state, {})
        self.assertEqual(len(warnings), 1)
        self.assertIn("printf format", warnings[0])
        self.assertIn("rollout-x.jsonl@2026-08-01T00:00:00.000Z", warnings[0])

    def test_shell_and_apply_patch_events_merge_in_global_timestamp_order(self):
        add_patch = ("*** Begin Patch\n*** Add File: /p/progress.md\n"
                     "+Decision.\n*** End Patch")
        append_js = ("const r=await tools.exec_command({cmd:`printf '%s\\\\n' "
                     "'Task 1: complete' >> /p/progress.md`});")
        with tempfile.TemporaryDirectory() as tmp:
            rollout = os.path.join(tmp, "run1", "home", ".codex", "sessions",
                                    "2026", "08", "01", "rollout-x.jsonl")
            self._write_rollout(rollout, [
                custom_exec_cmd("2026-08-01T00:01:00.000Z", "c2", append_js),
                custom_exec_cmd("2026-08-01T00:00:00.000Z", "c1",
                                 apply_patch_js(add_patch)),
            ])
            state, warnings = el.recover_files(tmp)
        self.assertEqual(warnings, [])
        self.assertEqual(state["/p/progress.md"], "Decision.\nTask 1: complete")


if __name__ == "__main__":
    unittest.main()
