#!/usr/bin/env python3
"""Plan-decomposition campaign (Task 2b): duplicate-command discovery,
generalized across a rep's rollouts -- controller AND every implementer/
reviewer subagent, not just one seat. Design doc's D1/K1 axes need this:
"stop re-running the same tests/linters on the same code across agents"
(Jesse's directive) and "repeated-discovery cost drops (measure: duplicate
exploration commands across implementers)" (K1's prediction).

**CRITICAL FORMAT NOTE, verified directly against the cp-x5-leases-scaled
corpus (see this module's own corpus-validation report):** every single
exec command in that corpus (156 checked in one rep alone) is
`custom_tool_call`/name=="exec" with the shell text embedded as a JS
snippet in the `input` field (`const r = await tools.exec_command({cmd:
"...", workdir:"...", ...})`), never the `function_call`/name==
"exec_command" JSON-`arguments` shape. An extractor that only reads
`function_call`/`arguments` -- rather than
`campaigns/codex-efficiency/rollout_parser.exec_commands()`, which already
abstracts both encodings -- silently reads all-zeros on this corpus. Every
function below goes through `rp.exec_commands()` for exactly this reason;
never hand-roll a second parse of `response_item` payloads.

**Normalization (`normalize_command`).** The raw custom_exec text is the
WHOLE JS call-site blob, not just the shell command -- it also carries a
`workdir` field whose value is an absolute path unique to this rep
directory (`/workspace/evals/results/<rep-name>/.../coding-agent-workdir`),
which would otherwise make the IDENTICAL shell command normalize
DIFFERENTLY across two reps (or across two agents in the same rep whose
`workdir` differs only by worktree name) purely because of where it
happened to run. `normalize_command` strips that field, then strips a
leading `cd <path> && `/`cd <path>; ` shell-level prefix (the same
rep-specific-path problem, one layer down, seen directly in this corpus's
own implementer commands e.g. `cd .worktrees/dispatch-queue && pytest -q`),
then collapses whitespace (`score_e3._normalize_cmd`'s own convention).
What is left is the surrounding JS call boilerplate (constant across every
occurrence, real corpus verified) plus the actual command text -- stable
enough that the SAME logical command normalizes identically wherever it
ran.

**Classification (`classify`).** Priority order test-run > lint-format >
file-read > other: a compound command chaining an exploration step before
a real test run (`sed -n '1,120p' .gitignore; pytest -q`, a real corpus
line from cp-x5-leases-scaled-control-rep10) is what matters to a caller
counting VERIFICATION duplication, not the sed prefix. `test-run` reuses
`score_e3.TEST_INVOCATION_RE` directly (imported, not forked) -- the same
whole-command `re.search` convention as `score_e3.test_command_events()`
(one event per exec command that CONTAINS a match, not a per-invocation
sub-extraction): this is the exact convention this module's own
corpus-validation matched to the campaign's hand-corrected control-rep9/
control-rep10 anchors (8 and 9 -- see the report). `score_x5_leases.py`'s
finer substring-aware multi-extraction is a deliberately DIFFERENT tool
for a different question (per-occurrence tree_sha attribution); reusing it
here instead overcounts a chained command with an incidental duplicate
match (verified directly: it disagreed with the rep10 anchor by 1,
traced to an `apply_patch` progress-ledger write whose OWN diff content
happens to mention "pytest" in prose -- see the report for the full
trace) and is deliberately not used for this scorer's classification.

**Privacy.** Following `score_e3.py`'s own convention (this module's
closest precedent for "a normalized command can carry arbitrary,
uncontrolled corpus text"): no function here returns, prints, or JSON-
serializes a raw or normalized command string. Every distinct normalized
command is relabeled to a per-report `cmd_id` ("cmd1", "cmd2", ... by
first-appearance order across the given rollout paths) before it appears
on `dup_stats()`'s output; only the `class` label (one of the four fixed
buckets) and counts are exposed.

**Controller identification.** A session counts as a controller iff it has
>=1 `spawn_agent` call (`rollout_parser.extract_spawns()`) -- the exact
convention `campaigns/codex-efficiency/score_e8.py` already established
("A session counts as a "controller" iff it has >=1 spawn"). When more
than one rollout in the given set independently qualifies (a nested-spawn
case: a reviewer subagent that itself spawns a sub-reviewer), the one with
the EARLIEST first-record timestamp is reported as `is_controller` -- the
top-level session, matching `task9_extract_signals.root_rollout()`'s own
earliest-timestamp convention for "the root" (verified on this corpus:
every rep's spawn-having rollout IS also its earliest-timestamp rollout).

Usage: `dup_stats(rollout_paths)` for the pure computation, or run this
file directly against one or more rep directories for a JSON report per
rep (`python3 score_pd_dupdiscovery.py REP_DIR...`) -- rollouts are
discovered under each REP_DIR via `scorer_common.find_files`, same
dot-directory-safe convention every other scorer in this campaign uses.
Read-only; makes no writes.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "codex-efficiency"))
import rollout_parser as rp
import score_e3 as se
from scorer_common import find_files

# -- normalization -----------------------------------------------------------

# Strips a `workdir` JSON field (quoted or bare JS-shorthand key) and its
# string value out of a custom_exec call's raw JS blob -- see module
# docstring for why this rep-specific absolute path must never survive
# into a cross-rep/cross-agent normalized identity.
_WORKDIR_FIELD_RE = re.compile(r'"?workdir"?\s*:\s*"(?:[^"\\]|\\.)*"\s*,?\s*')

# A leading `cd <path> && `/`cd <path>; ` shell prefix -- the same
# rep/worktree-specific-path problem one layer down, inside the actual
# shell command text itself (real corpus example: `cd
# .worktrees/dispatch-queue && pytest -q`).
_CD_PREFIX_RE = re.compile(r'^\s*cd\s+\S+\s*(?:&&|;)\s*')

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_command(raw_cmd, encoding):
    """See module docstring. Safe to call on either exec_commands()
    encoding: deescape_custom_exec() is a no-op for "exec_command" (already
    JSON-decoded upstream), and that encoding's `arguments` shape has no
    `workdir` sibling key to strip in the first place, so both field-strip
    regexes simply find nothing to remove there."""
    cmd = rp.deescape_custom_exec(raw_cmd, encoding)
    cmd = _WORKDIR_FIELD_RE.sub("", cmd)
    cmd = _CD_PREFIX_RE.sub("", cmd)
    return _WHITESPACE_RE.sub(" ", cmd).strip()


# -- classification -----------------------------------------------------------

CLASSES = ("test-run", "lint-format", "file-read", "other")

# Deliberately excludes `black`/`ruff`/etc as BARE words that could appear
# in unrelated prose -- these are real tool-invocation names, kept as a
# flat alternation (no attempt at exhaustive coverage of every ecosystem's
# linter; extend the set here, not with a second classifier, if a new one
# turns up in a future corpus).
LINT_FORMAT_RE = re.compile(
    r"\b(?:black|ruff|flake8|eslint|prettier|mypy|pylint|isort|gofmt|"
    r"rustfmt|cargo\s+fmt|cargo\s+clippy|shellcheck|stylelint|"
    r"clang-format|autopep8|yapf)\b", re.I)

# `git (status|diff|log|show|blame)` are read-only git subcommands --
# deliberately excludes git's mutating subcommands (commit/merge/rebase/
# reset/checkout, rollout_parser.MUTATION_GIT_RE's own set) since those are
# real tree mutations, not exploration.
FILE_READ_RE = re.compile(
    r"\b(?:cat|sed|head|tail|less|rg|grep|find|ls|wc|tree|"
    r"git\s+(?:status|diff|log|show|blame))\b", re.I)


def classify(cmd_norm):
    """One of CLASSES, in priority order test-run > lint-format >
    file-read > other -- see module docstring for why a compound command
    matching more than one bucket is classified by its highest-priority
    match, not split or double-counted."""
    if se.TEST_INVOCATION_RE.search(cmd_norm):
        return "test-run"
    if LINT_FORMAT_RE.search(cmd_norm):
        return "lint-format"
    if FILE_READ_RE.search(cmd_norm):
        return "file-read"
    return "other"


# -- controller identification ------------------------------------------------

def is_controller(path):
    """See module docstring -- score_e8.py's own "A session counts as a
    controller iff it has >=1 spawn" convention, reused directly."""
    return len(rp.extract_spawns(path)) > 0


def _first_timestamp(path):
    for ts, _typ, _p in rp.iter_records(path):
        return ts
    return "9999"  # empty file: sorts last, never mistaken for the root


def find_controller(rollout_paths):
    """The earliest-first-timestamp rollout among every PATH in
    ROLLOUT_PATHS with >=1 spawn_agent call, or None if none qualify (a
    rep with no controller-shaped rollout at all -- e.g. a slice of only
    implementer children). See module docstring's nested-spawn note for
    why "earliest among qualifying" rather than "first qualifying found"."""
    controllers = [p for p in rollout_paths if is_controller(p)]
    if not controllers:
        return None
    return min(controllers, key=_first_timestamp)


# -- per-rollout command events ------------------------------------------------

def agent_command_events(path):
    """[{"cmd_norm": str, "class": str, "timestamp": str}, ...] for every
    exec command found in PATH (both exec_commands() encodings), in file
    order. A command that normalizes to the empty string (all content was
    a stripped workdir field, e.g. a call with no real cmd text -- not
    observed in the real corpus but handled rather than crashing) is
    skipped."""
    out = []
    for ec in rp.exec_commands(path):
        norm = normalize_command(ec.cmd, ec.encoding)
        if not norm:
            continue
        out.append({"cmd_norm": norm, "class": classify(norm), "timestamp": ec.timestamp})
    return out


# -- aggregate report ----------------------------------------------------------

def dup_stats(rollout_paths):
    """The full per-rep duplicate-discovery report. See module docstring
    for the anonymization/classification/controller conventions this
    builds on.

    Returns:
      {"agents": [{"rollout": basename, "is_controller": bool,
                    "class_counts": {cls: n, ...},
                    "repeat_commands": [{"cmd_id": str, "class": str,
                                          "count": n}, ...]},
                   ...],
       "cross_agent_duplicates": [{"cmd_id": str, "class": str,
                                    "count": n, "agents": [basename, ...]},
                                   ...],
       "controller_test_run_count": int | None}

    `repeat_commands` on one agent entry is that agent's own
    `cmd_norm`-identical repeats (count >= 2) -- "repeat runs by the same
    agent" per the Task 2 brief. `cross_agent_duplicates` is every
    `cmd_norm` group whose occurrences span >= 2 DISTINCT agents --
    "same normalized command class+target run by 2+ different agents"
    (the class+target identity is exactly what `cmd_norm` already encodes,
    e.g. "pytest tests/" carries both its class and its target in one
    string; no separate target field is extracted). `cmd_id` values are
    assigned once, globally, by first-appearance order across all of
    ROLLOUT_PATHS, so the SAME cmd_id in a `repeat_commands` entry and a
    `cross_agent_duplicates` entry always denotes the same normalized
    command -- never re-derive identity from the printed labels alone in
    a caller that also wants to correlate the two lists.
    `controller_test_run_count` is None if no rollout in ROLLOUT_PATHS
    qualifies as a controller (see `find_controller`)."""
    rollout_paths = sorted(rollout_paths)
    controller_path = find_controller(rollout_paths)

    # First-appearance cmd_id assignment, global across every agent.
    cmd_ids = {}  # cmd_norm -> "cmdN"

    def _cmd_id(cmd_norm):
        if cmd_norm not in cmd_ids:
            cmd_ids[cmd_norm] = f"cmd{len(cmd_ids) + 1}"
        return cmd_ids[cmd_norm]

    per_agent_counts = {}  # basename -> Counter(cmd_norm)
    per_agent_class = {}   # basename -> str (class of that cmd_norm, stable)
    cross_agent_norms = defaultdict(set)  # cmd_norm -> {basenames}
    cross_agent_total = Counter()  # cmd_norm -> total occurrence count

    agents_meta = []
    for path in rollout_paths:
        basename = os.path.basename(path)
        events = agent_command_events(path)
        counts = Counter(e["cmd_norm"] for e in events)
        class_of = {e["cmd_norm"]: e["class"] for e in events}
        per_agent_counts[basename] = counts
        per_agent_class.update(class_of)
        for norm in counts:
            cross_agent_norms[norm].add(basename)
        for norm, n in counts.items():
            cross_agent_total[norm] += n

        class_counts = Counter(e["class"] for e in events)
        agents_meta.append((basename, path, counts, class_counts))

    agents_out = []
    for basename, path, counts, class_counts in agents_meta:
        repeat_commands = [
            {"cmd_id": _cmd_id(norm), "class": per_agent_class[norm], "count": n}
            for norm, n in sorted(counts.items()) if n >= 2
        ]
        repeat_commands.sort(key=lambda r: r["cmd_id"])
        agents_out.append({
            "rollout": basename,
            "is_controller": path == controller_path,
            "class_counts": {c: class_counts.get(c, 0) for c in CLASSES},
            "repeat_commands": repeat_commands,
        })
    agents_out.sort(key=lambda a: a["rollout"])

    cross_agent_duplicates = []
    for norm, basenames in sorted(cross_agent_norms.items()):
        if len(basenames) < 2:
            continue
        cross_agent_duplicates.append({
            "cmd_id": _cmd_id(norm),
            "class": per_agent_class[norm],
            "count": cross_agent_total[norm],
            "agents": sorted(basenames),
        })
    cross_agent_duplicates.sort(key=lambda d: d["cmd_id"])

    controller_test_run_count = None
    if controller_path is not None:
        controller_basename = os.path.basename(controller_path)
        controller_counts = next(a["class_counts"] for a in agents_out
                                  if a["rollout"] == controller_basename and a["is_controller"])
        controller_test_run_count = controller_counts["test-run"]

    return {
        "agents": agents_out,
        "cross_agent_duplicates": cross_agent_duplicates,
        "controller_test_run_count": controller_test_run_count,
    }


# -- rep-directory discovery + CLI --------------------------------------------

def rollouts_for_rep(rep_dir):
    """Every rollout-*.jsonl under REP_DIR's home/.codex/sessions tree,
    dot-directory-safe (scorer_common.find_files -- see that module's own
    docstring for the glob.glob(recursive=True) bug this avoids)."""
    return sorted(find_files(rep_dir, "rollout-*.jsonl",
                              path_contains=os.path.join("home", ".codex", "sessions")))


def main(argv):
    if len(argv) < 2:
        print("usage: score_pd_dupdiscovery.py REP_DIR...", file=sys.stderr)
        return 1
    rep_dirs = argv[1:]
    reports = {}
    for rep_dir in rep_dirs:
        rollouts = rollouts_for_rep(rep_dir)
        if not rollouts:
            print(f"# {rep_dir}: no rollouts found", file=sys.stderr)
            continue
        reports[os.path.basename(rep_dir.rstrip("/"))] = dup_stats(rollouts)
    if len(rep_dirs) == 1 and reports:
        print(json.dumps(next(iter(reports.values())), indent=2))
    else:
        print(json.dumps(reports, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
