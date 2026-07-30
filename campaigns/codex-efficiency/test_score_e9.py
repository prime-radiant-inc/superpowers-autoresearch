#!/usr/bin/env python3
"""Tests for score_e9.py (E9 workspace-leak census, Amendment 1). Builds a
real synthetic git repo via subprocess (git init/add/commit) -- no rollouts,
no client content, no fixture from any scored corpus. Exercises both ways a
`.superpowers/` path can land in history (a normal `git add` before any
.gitignore rule exists, and a `git add -f` past one that was added later)
and both terminal states a leaked path can end up in (still present at HEAD
vs. removed by a later commit on the same branch) -- see
score_e9.score_repo()'s LeakedPath.status values.

Also regression-tests a real bug found while grounding this task: a
directory with no `.git` of its own must never be treated as a scorable
repo, even when it sits nested inside a DIFFERENT git repo's working tree --
`git rev-parse --is-inside-work-tree` (and any git subprocess call) run with
cwd set to such a directory silently resolves upward to that ancestor
repo's history instead of failing. Verified live against one of our own
battery run dirs (`evals/results/.../coding-agent-workdir` with no `.git`
resolves to the `evals` checkout's own submodule gitdir) before writing this
test -- see the E9 pre-registration entry in
`logs/2026-07-28-codex-efficiency.md`.
"""
import json
import os
import subprocess
import tempfile
import unittest

import score_e9 as se


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True,
                    capture_output=True, text=True)


def _write(repo, relpath, content=""):
    path = os.path.join(repo, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def make_repo(tmp):
    """A synthetic repo mirroring the real leak pattern found in Drew's
    fractals corpus and structurally exercised in our own battery repos:
    initial commit -> a workspace file committed normally (before any
    .gitignore exists) -> a .gitignore added covering .superpowers/ ->
    a second workspace file force-added past that rule -> the first file
    removed on a later commit (self-cure), the second left shipped."""
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")

    _write(repo, "README.md", "hello\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "initial commit")

    # normal-pathed leak: no .gitignore rule exists yet, so a plain `git
    # add` tracks it.
    _write(repo, ".superpowers/sdd/task-1-brief.md", "brief\n")
    _git(repo, "add", ".superpowers/sdd/task-1-brief.md")
    _git(repo, "commit", "-q", "-m", "feat: accidentally track task 1 brief")

    _write(repo, ".gitignore", ".superpowers/\n")
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-q", "-m", "chore: ignore development workspaces")

    # force-added leak: past the .gitignore rule added just above.
    _write(repo, ".superpowers/sdd/task-2-report.md", "report\n")
    _git(repo, "add", "-f", ".superpowers/sdd/task-2-report.md")
    _git(repo, "commit", "-q", "-m", "docs: force-commit task 2 report")

    # self-cure: untrack the first leak, leave the second shipped.
    _git(repo, "rm", "-q", ".superpowers/sdd/task-1-brief.md")
    _git(repo, "commit", "-q", "-m", "chore: untrack task 1 brief")

    return repo


class TestScoreRepo(unittest.TestCase):
    def test_classifies_shipped_vs_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp)
            report = se.score_repo(repo, label="synthetic")
            self.assertEqual(report.ever_added_count, 2)
            self.assertEqual(report.reachable_added_count, 2)
            self.assertEqual(report.head_count, 1)

            by_path = {lp.path: lp for lp in report.leaked}
            self.assertEqual(set(by_path), {
                ".superpowers/sdd/task-1-brief.md",
                ".superpowers/sdd/task-2-report.md",
            })
            self.assertEqual(
                by_path[".superpowers/sdd/task-1-brief.md"].status, "removed")
            self.assertEqual(
                by_path[".superpowers/sdd/task-2-report.md"].status, "shipped")
            # commit subject line that ADDED each path (not the removal).
            self.assertIn("task 1 brief",
                           by_path[".superpowers/sdd/task-1-brief.md"].subject)
            self.assertIn("task 2 report",
                           by_path[".superpowers/sdd/task-2-report.md"].subject)

    def test_clean_repo_has_no_leaks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = os.path.join(tmp, "clean")
            os.makedirs(repo)
            _git(repo, "init", "-q", "-b", "main")
            _git(repo, "config", "user.email", "test@example.com")
            _git(repo, "config", "user.name", "Test")
            _write(repo, "README.md", "hello\n")
            _git(repo, "add", "README.md")
            _git(repo, "commit", "-q", "-m", "initial commit")

            report = se.score_repo(repo, label="clean")
            self.assertEqual(report.ever_added_count, 0)
            self.assertEqual(report.head_count, 0)
            self.assertEqual(report.leaked, [])

    def test_non_repo_dir_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            not_a_repo = os.path.join(tmp, "not-a-repo")
            os.makedirs(not_a_repo)
            self.assertIsNone(se.score_repo(not_a_repo, label="bogus"))

    def test_nested_dir_without_own_git_is_not_scorable(self):
        """Regression test for the real bug found while grounding this task
        (see module docstring): a directory with no .git of its own must
        never be treated as scorable, even nested inside another repo."""
        with tempfile.TemporaryDirectory() as tmp:
            outer = os.path.join(tmp, "outer-repo")
            os.makedirs(outer)
            _git(outer, "init", "-q", "-b", "main")
            _git(outer, "config", "user.email", "test@example.com")
            _git(outer, "config", "user.name", "Test")
            _write(outer, "README.md", "outer\n")
            _git(outer, "add", "README.md")
            _git(outer, "commit", "-q", "-m", "outer initial commit")

            inner = os.path.join(outer, "nested", "coding-agent-workdir")
            os.makedirs(inner)

            self.assertFalse(se.is_scorable_git_repo(inner))
            self.assertIsNone(se.score_repo(inner, label="nested"))

    def test_review_package_workspace_in_diff_is_flagged(self):
        """Fix round 1: the plan's E9 bullet requires a second surface
        beyond git-history leaks -- 'workspace-in-diff at review packages'
        (a review diff, per the SDD `review-<sha>..<sha>.diff` convention,
        that itself includes a `.superpowers/` path in its diff headers --
        the thing Drew's own report.md cites as the reviewer's own
        automatic-finding rule). Only diff HEADER lines (`diff --git`,
        `---`, `+++`) are ever read for path extraction -- never a hunk
        body line -- so this test's fake diff's placeholder content line
        is deliberately named to make that failure mode obvious if broken."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = os.path.join(tmp, "repo")
            os.makedirs(repo)
            _git(repo, "init", "-q", "-b", "main")
            _git(repo, "config", "user.email", "test@example.com")
            _git(repo, "config", "user.name", "Test")
            _write(repo, "README.md", "hello\n")
            _git(repo, "add", "README.md")
            _git(repo, "commit", "-q", "-m", "initial commit")

            # A review-package artifact left in the workspace (matching the
            # real SDD convention: review diffs live under
            # .superpowers/sdd/<plan>/, normally gitignored, never
            # committed) whose diff itself touches a workspace path.
            diff_text = (
                "diff --git a/.superpowers/sdd/task-1-report.md b/.superpowers/sdd/task-1-report.md\n"
                "index 0000000..1111111 100644\n"
                "--- a/.superpowers/sdd/task-1-report.md\n"
                "+++ b/.superpowers/sdd/task-1-report.md\n"
                "@@ -0,0 +1 @@\n"
                "+HUNK_BODY_MUST_NEVER_BE_READ_FOR_PATH_EXTRACTION\n"
            )
            _write(repo, ".superpowers/sdd/review-abc123..def456.diff", diff_text)

            report = se.score_repo(repo, label="synthetic")
            self.assertEqual(len(report.review_packages), 1)
            rp = report.review_packages[0]
            self.assertEqual(rp.path, ".superpowers/sdd/review-abc123..def456.diff")
            self.assertEqual(rp.source, "working-tree")
            self.assertTrue(rp.workspace_in_diff)
            self.assertEqual(rp.workspace_paths_in_diff,
                              [".superpowers/sdd/task-1-report.md"])


class TestWriteJsonForceGuard(unittest.TestCase):
    def test_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "out", "e9-test.json")
            self.assertTrue(se.write_json({"a": 1}, out_path))
            self.assertFalse(se.write_json({"a": 2}, out_path))
            with open(out_path) as f:
                self.assertEqual(json.load(f), {"a": 1})

    def test_force_allows_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "out", "e9-test.json")
            se.write_json({"a": 1}, out_path)
            self.assertTrue(se.write_json({"a": 2}, out_path, force=True))
            with open(out_path) as f:
                self.assertEqual(json.load(f), {"a": 2})


if __name__ == "__main__":
    unittest.main()
