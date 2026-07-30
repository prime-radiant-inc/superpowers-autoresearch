#!/usr/bin/env python3
"""E9 workspace-leak census (Amendment 1, Tasks E7-E9 -- MINE tier, no new
run spend). Pre-registered prediction: `logs/2026-07-28-codex-efficiency.md`,
"E9 PRE-REGISTRATION" entry.

Unlike E7/E8, E9 scores GIT REPOS (run workdirs), not rollout JSONL -- there
is no `rollout_parser.py` involvement at all. For each repo it runs
read-only `git` subprocesses with `cwd=repo_dir` (never a mutating command)
to answer three questions about paths under `.superpowers/`:

  (a) ever added in history:      `git log --all --diff-filter=A ...`
  (b) present in HEAD:            `git ls-tree -r --name-only HEAD ...`
  (c) added in a commit reachable from HEAD: same as (a) without `--all`.

Every path in (a) is classified against (b)/(c):
  - "shipped"      -- present in HEAD (still shipped today).
  - "removed"      -- added in a commit reachable from HEAD, but not in
                       HEAD (leaked, then self-cured on the same branch).
  - "unreachable"  -- added only on a ref/commit NOT reachable from the
                       repo's current HEAD.

A directory is scored only if it has its OWN `.git` entry (dir or file)
directly inside it (`is_scorable_git_repo`). This is deliberate, not an
oversight: `git rev-parse --is-inside-work-tree` (or any other git
subprocess) run with `cwd` set to a directory that has no `.git` of its own
does NOT fail -- it walks upward and silently resolves to whatever ancestor
repo it finds. Verified live while grounding this task: one of our own
battery run dirs (a duplicated/retried-run artifact under
`evals/results/cx-eff-cx-sdd-small-spinout-rep6/`) has no `.git` of its own
and resolves straight through to the `evals` checkout's OWN git history
(`--show-toplevel` -> `.../superpowers/evals`, `--git-dir` -> the submodule
gitdir `.../superpowers/.git/modules/evals`). Scoring that directory under
its battery label would silently report an unrelated repo's full history.

**Second surface (fix round 1): review-package workspace-in-diff.** The
plan's E9 bullet is two clauses, not one: git-history leaks (above) "plus
workspace-in-diff at review packages." A review package is a diff artifact
following the SDD skill's own `review-<sha>..<sha>.diff` naming convention
(and any other `*review*.diff`-shaped filename); "workspace-in-diff" means
the diff ITSELF has a `.superpowers/` path in one of its header lines
(`diff --git a/... b/...`, `--- a/...`, `+++ b/...`) -- i.e. a review
package that would trip the reviewer's own "any workspace path in the diff
is an automatic finding" rule (the exact rule Drew Ritter's own
`analysis/report.md`/`cross-run-comparison.md` describe his review prompts
using). `score_review_packages()` looks for review-package files in two
places per repo: the current working tree (a plain filesystem walk,
excluding `.git/`) and anywhere in git history (`git log --all
--diff-filter=A --name-only`, UNrestricted by the `.superpowers` pathspec
this time, since a review package need not live under `.superpowers/` --
filtered client-side by filename instead), reading each one's content
(working-tree files directly off disk; historical ones via `git show
<commit>:<path>`, still read-only, no checkout) ONLY to extract header
lines -- `_extract_diff_header_paths()` matches exclusively lines starting
with `diff --git `, `--- `, or `+++ `, and never touches a hunk body (`@@`
context or `+`/`-` content) line.

Only path names, commit SHAs, and commit SUBJECT LINES are ever read or
printed -- never a diff's hunk-body content, never a reviewed file's actual
contents. Workspace paths (task-N-brief.md etc.), review-package
filenames, and their commit subjects are process/fixture text, not user
content -- safe to print per this task's brief.

Usage: score_e9.py [--force]
Prints a markdown report to stdout. Writes aggregates-only JSON blobs
(paths/commits/subjects/counts, no file contents) to
campaigns/codex-efficiency/out/e9-<corpus>.json (refuses to overwrite an
existing file unless --force or env FORCE=1 is set, matching
score_e1.py/score_e8.py's convention). Read-only on every scored repo.
"""
import dataclasses
import glob
import json
import os
import re
import subprocess
import sys

WORKSPACE_PATHSPEC = ".superpowers"
COMMIT_MARKER = "@@E9COMMIT@@"

# Review-package filename convention: the SDD skill's own
# `review-<sha>..<sha>.diff` naming, plus any other `*review*.diff`-shaped
# name (Drew's corpus uses varying conventions -- match broadly by filename,
# never by location).
REVIEW_PACKAGE_RE = re.compile(r"review.*\.diff$", re.IGNORECASE)

# Unified-diff HEADER lines only -- deliberately excludes any hunk line
# (`@@ ... @@` or a `+`/`-` content line). See module docstring.
DIFF_GIT_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+)$")
DIFF_MINUS_HEADER_RE = re.compile(r"^--- (?:a/(.+)|/dev/null)$")
DIFF_PLUS_HEADER_RE = re.compile(r"^\+\+\+ (?:b/(.+)|/dev/null)$")

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

DEFAULT_DREW_FRACTALS_ROOT = (
    "/Users/jesse/git/superpowers/_tmp/drew-sdd-head-to-head-2026-07-27/"
    "sdd-testing-fresh"
)
DEFAULT_EVALS_RESULTS = os.environ.get(
    "EVALS_RESULTS", "/Users/jesse/git/superpowers/superpowers/evals/results")

BATTERY_REP_RE = re.compile(r"^cx-eff-cx-sdd-small-(?P<arm>dev|spinout)-rep(?P<rep>\d+)$")


# --- low-level, read-only git access --------------------------------------

def is_scorable_git_repo(repo_dir):
    """True iff repo_dir has its OWN .git entry (dir or file) directly
    inside it. See module docstring for why this is checked on the
    filesystem rather than via a git subprocess."""
    return os.path.exists(os.path.join(repo_dir, ".git"))


def _run_git(repo_dir, args):
    """Read-only git invocation, cwd=repo_dir. Raises RuntimeError on a
    nonzero exit (a caller must have already confirmed is_scorable_git_repo
    before calling this)."""
    result = subprocess.run(["git", *args], cwd=repo_dir,
                             capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} in {repo_dir} failed: {result.stderr.strip()}")
    return result.stdout


def _head_exists(repo_dir):
    result = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"],
                             cwd=repo_dir, capture_output=True, text=True)
    return result.returncode == 0


@dataclasses.dataclass
class AddEvent:
    path: str
    commit: str
    subject: str


def _parse_added_log(output):
    """Parse `git log --reverse --diff-filter=A --name-only
    --pretty=format:'MARKER%H<TAB>%s'` output (oldest commit first, per
    --reverse) into a flat list of AddEvent, one per (commit, path) pair in
    that commit's added-files list."""
    events = []
    commit = subject = None
    for line in output.splitlines():
        if line.startswith(COMMIT_MARKER):
            rest = line[len(COMMIT_MARKER):]
            commit, _, subject = rest.partition("\t")
        elif line.strip():
            if commit is None:
                continue  # defensive: a path line before any marker seen
            events.append(AddEvent(path=line, commit=commit, subject=subject))
    return events


def added_events(repo_dir, all_refs):
    """Every (commit, path) pair where `path` under WORKSPACE_PATHSPEC was
    Added (diff-filter=A), oldest first (--reverse). all_refs=True scans
    every ref (--all); all_refs=False scans only commits reachable from the
    current HEAD."""
    args = ["log", "--reverse"]
    if all_refs:
        args.append("--all")
    args += ["--diff-filter=A", "--name-only",
             f"--pretty=format:{COMMIT_MARKER}%H\t%s",
             "--", WORKSPACE_PATHSPEC]
    return _parse_added_log(_run_git(repo_dir, args))


def head_paths(repo_dir):
    if not _head_exists(repo_dir):
        return []
    output = _run_git(repo_dir, ["ls-tree", "-r", "--name-only", "HEAD",
                                  "--", WORKSPACE_PATHSPEC])
    return sorted(line for line in output.splitlines() if line.strip())


def _first_add_by_path(events):
    """First (chronologically earliest, since `events` is queried with
    --reverse) AddEvent per path."""
    first = {}
    for e in events:
        if e.path not in first:
            first[e.path] = e
    return first


# --- review-package discovery ("workspace-in-diff") -------------------------
#
# A review package is a diff artifact (SDD's `review-<sha>..<sha>.diff`
# convention). "workspace-in-diff" means the diff itself has a
# `.superpowers/` path in a HEADER line -- never inspected via hunk-body
# content. See module docstring for the full rationale.

def _extract_diff_header_paths(text):
    """Every path named in a unified diff's HEADER lines only (`diff --git
    a/X b/Y`, `--- a/X`, `+++ b/X`) -- never a hunk (`@@`) or content
    (`+`/`-`) line. `text` may be an entire diff file's content; this never
    returns or retains anything from a non-header line."""
    paths = set()
    for line in text.splitlines():
        m = DIFF_GIT_HEADER_RE.match(line)
        if m:
            paths.add(m.group(1))
            paths.add(m.group(2))
            continue
        m = DIFF_MINUS_HEADER_RE.match(line)
        if m and m.group(1):
            paths.add(m.group(1))
            continue
        m = DIFF_PLUS_HEADER_RE.match(line)
        if m and m.group(1):
            paths.add(m.group(1))
    return paths


def _workspace_paths(paths):
    return sorted(p for p in paths
                  if p == WORKSPACE_PATHSPEC or p.startswith(WORKSPACE_PATHSPEC + "/"))


def find_working_tree_review_packages(repo_dir):
    """Every file anywhere under repo_dir (excluding .git/) whose basename
    matches REVIEW_PACKAGE_RE. Plain filesystem walk, read-only, no git
    subprocess -- this is how a review package left in an ignored workspace
    directory (the normal case: .superpowers/sdd/<plan>/ is gitignored) is
    found at all."""
    found = []
    for root, dirs, files in os.walk(repo_dir):
        if ".git" in dirs:
            dirs.remove(".git")
        for fname in files:
            if REVIEW_PACKAGE_RE.search(fname):
                found.append(os.path.relpath(os.path.join(root, fname), repo_dir))
    return sorted(found)


def find_history_review_packages(repo_dir):
    """Every (commit, subject, path) Added anywhere in history (--all)
    whose basename matches REVIEW_PACKAGE_RE. Reuses the same
    log --diff-filter=A --name-only query shape as added_events(), but
    WITHOUT the .superpowers pathspec restriction -- a review package need
    not live under .superpowers/ -- filtered client-side by filename
    instead."""
    args = ["log", "--reverse", "--all", "--diff-filter=A", "--name-only",
            f"--pretty=format:{COMMIT_MARKER}%H\t%s"]
    events = _parse_added_log(_run_git(repo_dir, args))
    return [e for e in events if REVIEW_PACKAGE_RE.search(os.path.basename(e.path))]


def _read_working_tree_file(repo_dir, relpath):
    with open(os.path.join(repo_dir, relpath), "r", errors="replace") as f:
        return f.read()


def _read_git_blob(repo_dir, commit, path):
    """Read-only: `git show <commit>:<path>` -- reads a historical blob
    without touching the working tree or index at all."""
    result = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=repo_dir,
                             capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    return result.stdout


@dataclasses.dataclass
class ReviewPackageFinding:
    path: str
    source: str  # "working-tree" | "history"
    commit: str  # commit sha ("" for working-tree source)
    subject: str  # commit subject ("" for working-tree source)
    workspace_paths_in_diff: list  # sorted list[str], possibly empty

    @property
    def workspace_in_diff(self):
        return len(self.workspace_paths_in_diff) > 0


def score_review_packages(repo_dir):
    """Locates every review-package artifact in repo_dir (working tree +
    git history) and reports whether each one's diff touches a
    `.superpowers/` path in a header line. Read-only throughout."""
    findings = []
    for relpath in find_working_tree_review_packages(repo_dir):
        content = _read_working_tree_file(repo_dir, relpath)
        findings.append(ReviewPackageFinding(
            path=relpath, source="working-tree", commit="", subject="",
            workspace_paths_in_diff=_workspace_paths(_extract_diff_header_paths(content))))
    for e in find_history_review_packages(repo_dir):
        content = _read_git_blob(repo_dir, e.commit, e.path)
        findings.append(ReviewPackageFinding(
            path=e.path, source="history", commit=e.commit, subject=e.subject,
            workspace_paths_in_diff=_workspace_paths(_extract_diff_header_paths(content))))
    return findings


# --- per-repo scoring -------------------------------------------------------

@dataclasses.dataclass
class LeakedPath:
    path: str
    commit: str
    subject: str
    status: str  # "shipped" | "removed" | "unreachable"


@dataclasses.dataclass
class RepoReport:
    repo_dir: str
    label: str
    ever_added_count: int
    reachable_added_count: int
    head_count: int
    leaked: list  # list[LeakedPath], sorted by path
    review_packages: list  # list[ReviewPackageFinding]


def score_repo(repo_dir, label=""):
    """Scores one repo, read-only. Returns None (not a scoring failure) if
    repo_dir has no .git of its own -- see is_scorable_git_repo."""
    if not is_scorable_git_repo(repo_dir):
        return None

    ever_first = _first_add_by_path(added_events(repo_dir, all_refs=True))
    reachable_first = _first_add_by_path(added_events(repo_dir, all_refs=False))
    head_set = set(head_paths(repo_dir))

    leaked = []
    for path in sorted(ever_first):
        ev = ever_first[path]
        if path in head_set:
            status = "shipped"
        elif path in reachable_first:
            status = "removed"
        else:
            status = "unreachable"
        leaked.append(LeakedPath(path=path, commit=ev.commit,
                                  subject=ev.subject, status=status))

    return RepoReport(
        repo_dir=repo_dir,
        label=label,
        ever_added_count=len(ever_first),
        reachable_added_count=len(reachable_first),
        head_count=len(head_set),
        leaked=leaked,
        review_packages=score_review_packages(repo_dir),
    )


# --- corpus discovery --------------------------------------------------------

def find_drew_fractals_repos(root=None):
    """Drew Ritter's four `awesome-fractals-fcu-*` repos (external, never
    committed -- read-only)."""
    root = root or DEFAULT_DREW_FRACTALS_ROOT
    for path in sorted(glob.glob(os.path.join(root, "awesome-fractals-fcu-*"))):
        if os.path.isdir(path):
            yield os.path.basename(path), path


def find_battery_workdirs(results_dir=None):
    """Every `coding-agent-workdir` under our own
    cx-eff-cx-sdd-small-{dev,spinout}-rep*/*/ battery run dirs. Yields
    (label, path, scorable) -- scorable is False for a directory with no
    .git of its own (see module docstring); callers must not score those."""
    results_dir = results_dir or DEFAULT_EVALS_RESULTS
    pattern = os.path.join(results_dir, "cx-eff-cx-sdd-small-*-rep*",
                            "*", "coding-agent-workdir")
    for path in sorted(glob.glob(pattern)):
        rep_dir_name = os.path.basename(os.path.dirname(os.path.dirname(path)))
        m = BATTERY_REP_RE.match(rep_dir_name)
        label = f"{m.group('arm')}-rep{m.group('rep')}" if m else rep_dir_name
        yield label, path, is_scorable_git_repo(path)


# --- report / JSON output ---------------------------------------------------

def _leaked_to_dict(lp):
    return dataclasses.asdict(lp)


def _review_package_to_dict(rp):
    d = dataclasses.asdict(rp)
    d["workspace_in_diff"] = rp.workspace_in_diff  # a @property, not a dataclass field
    return d


def _report_to_dict(r):
    return {
        "repo_dir": r.repo_dir,
        "label": r.label,
        "ever_added_count": r.ever_added_count,
        "reachable_added_count": r.reachable_added_count,
        "head_count": r.head_count,
        "leaked": [_leaked_to_dict(lp) for lp in r.leaked],
        "review_packages": [_review_package_to_dict(rp) for rp in r.review_packages],
    }


def write_json(data, out_path, force=False):
    if os.path.exists(out_path) and not force:
        print(f"score_e9: refusing to overwrite existing {out_path} "
              f"-- set env FORCE=1 or pass --force to overwrite", file=sys.stderr)
        return False
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    return True


def print_repo_table(reports):
    print("| repo | ever added | reachable-from-HEAD added | in HEAD | shipped | removed | unreachable |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for r in reports:
        n_shipped = sum(1 for lp in r.leaked if lp.status == "shipped")
        n_removed = sum(1 for lp in r.leaked if lp.status == "removed")
        n_unreach = sum(1 for lp in r.leaked if lp.status == "unreachable")
        print(f"| {r.label} | {r.ever_added_count} | {r.reachable_added_count} | "
              f"{r.head_count} | {n_shipped} | {n_removed} | {n_unreach} |")
    print()


def print_leak_listing(reports):
    any_leak = False
    for r in reports:
        for lp in r.leaked:
            any_leak = True
            print(f"- [{r.label}] `{lp.path}` -- status={lp.status}, "
                  f"commit={lp.commit[:12]} \"{lp.subject}\"")
    if not any_leak:
        print("(no leaked paths found)")
    print()


def print_review_package_section(corpus_name, reports):
    """Second E9 surface (fix round 1): review-package census +
    workspace-in-diff flags. Explicitly states a scored zero -- a corpus
    with no review-package artifacts at all prints that fact, not a bare
    empty table (per the fix instruction: 'a scored zero, not an
    omission')."""
    all_findings = [(r, rp) for r in reports for rp in r.review_packages]
    print(f"Review-package census (corpus: {corpus_name}): "
          f"{len(all_findings)} review-package artifact(s) found across "
          f"{len(reports)} repo(s) scored (working tree + git history).")
    print()
    if not all_findings:
        print(f"SCORED ZERO: no file anywhere (working tree or git "
              f"history, any ref) in the {corpus_name} corpus matches the "
              f"review-package naming convention (`review*.diff` / "
              f"`*review*.diff`). This is a census result, not a gap in "
              f"the search.")
        print()
        return
    print("| repo | path | source | commit | workspace-in-diff | workspace paths in diff |")
    print("|---|---|---|---|---|---|")
    n_flagged = 0
    for r, rp in all_findings:
        if rp.workspace_in_diff:
            n_flagged += 1
        commit_disp = rp.commit[:12] if rp.commit else "-"
        ws_disp = ", ".join(f"`{p}`" for p in rp.workspace_paths_in_diff) or "-"
        print(f"| {r.label} | `{rp.path}` | {rp.source} | {commit_disp} | "
              f"{'YES' if rp.workspace_in_diff else 'no'} | {ws_disp} |")
    print()
    print(f"{n_flagged}/{len(all_findings)} review-package artifact(s) in "
          f"the {corpus_name} corpus are workspace-in-diff.")
    print()


def main(argv):
    force = "--force" in argv or os.environ.get("FORCE") == "1"

    print("# E9 workspace-leak census (Amendment 1, MINE tier)")
    print()

    print("## Corpus (a): Drew Ritter's four `awesome-fractals-fcu-*` repos")
    print()
    drew_reports = []
    for label, path in find_drew_fractals_repos():
        r = score_repo(path, label=label)
        if r is None:
            print(f"- SKIPPED {label} ({path}): no .git of its own")
            continue
        drew_reports.append(r)
    print_repo_table(drew_reports)
    print("Leaked paths (every one found, commit subject that added it):")
    print()
    print_leak_listing(drew_reports)
    print_review_package_section("drew", drew_reports)

    print("## Corpus (b): our own `cx-eff-cx-sdd-small-{dev,spinout}` battery workdirs")
    print()
    battery_reports = []
    skipped = []
    for label, path, scorable in find_battery_workdirs():
        if not scorable:
            skipped.append((label, path))
            continue
        r = score_repo(path, label=label)
        battery_reports.append(r)
    if skipped:
        print(f"Skipped {len(skipped)} candidate dir(s) with no .git of their own "
              f"(not scored, not counted below):")
        for label, path in skipped:
            print(f"- {label}: `{path}`")
        print()
    print_repo_table(battery_reports)
    print("Leaked paths (every one found, commit subject that added it):")
    print()
    print_leak_listing(battery_reports)
    print_review_package_section("battery", battery_reports)

    os.makedirs(OUT_DIR, exist_ok=True)
    wrote_all = True
    for corpus_name, reports in (("drew", drew_reports), ("battery", battery_reports)):
        blob = {"reports": [_report_to_dict(r) for r in reports]}
        out_path = os.path.join(OUT_DIR, f"e9-{corpus_name}.json")
        if not write_json(blob, out_path, force=force):
            wrote_all = False
            continue
        print(f"wrote {out_path}", file=sys.stderr)

    return 0 if wrote_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
