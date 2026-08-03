"""Copies a probe's fixture/ into a throwaway git-initialized workdir, the
same setup the real runner does before invoking claude, so grader tests can
exercise `git diff`-based grading against realistic before/after states."""
import os
import shutil
import subprocess
import tempfile

PROBES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "probes")
GIT_IDENT = ["-c", "user.email=t@t.local", "-c", "user.name=t"]


def _copy_tree_files_only(src, dst):
    for name in os.listdir(src):
        s = os.path.join(src, name)
        d = os.path.join(dst, name)
        if os.path.isdir(s):
            os.makedirs(d, exist_ok=True)
            _copy_tree_files_only(s, d)
        elif os.path.isfile(s):
            shutil.copy(s, d)


def make_baseline_workdir(probe_id, prefix="cml-wd."):
    fixture_dir = os.path.join(PROBES_DIR, probe_id, "fixture")
    wd = tempfile.mkdtemp(prefix=prefix)
    _copy_tree_files_only(fixture_dir, wd)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=wd, check=True)
    subprocess.run(["git", *GIT_IDENT, "add", "-A"], cwd=wd, check=True)
    subprocess.run(["git", *GIT_IDENT, "commit", "-qm", "fixture baseline"], cwd=wd, check=True)
    return wd
