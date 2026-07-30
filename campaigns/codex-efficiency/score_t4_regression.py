#!/usr/bin/env python3
"""ATIF ceremony census scorer for the cross-harness T4 regression battery
(Task 10).

Harness-neutral: unlike score_e1.py..score_e10.py (which parse codex's raw
`~/.codex/sessions/**/*.jsonl` rollout format directly), this scorer reads
quorum's normalized ATIF v1.7 `trajectory.json` -- the same shape for every
coding agent (see `superpowers/evals/src/atif/types.ts`). Every harness's
normalizer (`superpowers/evals/src/normalize/*.ts`) canonicalizes native
tool names into a shared vocabulary (`Write`, `Edit`, `MultiEdit`,
`NotebookEdit`, `Read`, `Bash`, ...) before it ever reaches this scorer, so
"what counts as a file write" is decided ONCE upstream, not re-derived here
per harness.

For a single trajectory, computes a ceremony census:

  - spec_docs_written / plan_docs_written -- count of write-tool-call
    events (Write/Edit/MultiEdit/NotebookEdit) across the WHOLE
    trajectory whose path matches `docs/superpowers/specs/` /
    `docs/superpowers/plans/` respectively. Not gated to before the
    first code write -- these report ceremony volume overall.
  - doc_writes_before_first_code -- count of ceremony-doc write events
    (specs + plans combined) that occur in a step BEFORE the step
    containing the first code write. If no code write ever occurs, this
    falls back to counting ceremony-doc writes across the whole
    trajectory (no cutoff to gate on) -- the same no-T fallback
    convention score_e4.py uses for `docs_written_before_first_non_doc_patch`
    when its `T` is None.
  - first_code_file -- the path of the first write-tool-call whose path
    is a CODE path: not under any `docs/` subtree, and not a `*.md`
    file sitting at repo root (so README.md et al. don't get
    misclassified as "the code"). `None` if the trajectory never writes
    one.
  - user_turns_before_first_code -- count of ATIF steps with
    `source == "user"` at a step index before the first code write's
    step (whole-trajectory count when there is no code write).
  - writing_plans_invoked -- True iff any tool call anywhere in the
    trajectory references a path containing `skills/writing-plans`,
    wherever it appears in that call's arguments (a discrete
    `file_path` on a Read call, or embedded in a shell command string on
    a Bash call -- codex reads skill files via `sed`/`cat`, not a
    dedicated read tool, so the check is argument-content-wide rather
    than keyed to one argument name).

Granularity is deliberately STEP-level (not sub-step tool-call order,
unlike score_e4.py's timestamp-level cutoff) -- ATIF steps are the unit
the brief specifies ("count user turns from ATIF steps preceding the
first code write"), and every harness's normalizer already bundles one
LLM turn's tool calls onto one step.

Public API (no CLI/report generation at this layer -- Task 11 aggregates
census dicts across a battery and produces the report):
    score_trajectory(traj: dict) -> dict
    score_file(path: str) -> dict
"""
import json
import re

# Canonical (post-normalization) tool names that create or modify a file.
# Every quorum harness normalizer maps its native tool vocabulary onto this
# shared set (see e.g. GEMINI_TOOL_MAP, CODEX_TOOL_MAP, CLINE_TOOL_MAP in
# superpowers/evals/src/normalize/*.ts) before trajectory.json is written.
WRITE_TOOL_NAMES = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# Priority-ordered set of argument keys that carry a tool call's target
# file path, mirroring superpowers/evals/src/atif/project.ts's `toolPath`.
TOOL_PATH_KEYS = (
    "file_path", "path", "TargetFile", "target_file", "filePath",
    "AbsolutePath", "Path", "TargetPath",
)

CEREMONY_DOC_RE = re.compile(r"(^|/)docs/superpowers/(specs|plans)/")

WRITING_PLANS_NEEDLE = "skills/writing-plans"


def _normalize_path(path):
    norm = str(path).replace("\\", "/")
    if norm.startswith("./"):
        norm = norm[2:]
    return norm


def ceremony_doc_kind(path):
    """Return "specs", "plans", or None -- whether `path` is a ceremony
    doc under docs/superpowers/(specs|plans)/."""
    m = CEREMONY_DOC_RE.search(_normalize_path(path))
    return m.group(2) if m else None


def _is_docs_subtree(path):
    """True iff any path component (other than the final filename) is
    literally "docs" -- any docs/ subtree, not just docs/superpowers/."""
    parts = _normalize_path(path).split("/")
    return "docs" in parts[:-1]


def _is_root_md(path):
    norm = _normalize_path(path)
    return "/" not in norm and norm.lower().endswith(".md")


def is_code_path(path):
    """True iff `path` is a real code file: non-empty, outside any docs/
    subtree, and not a *.md file sitting at repo root."""
    if not path:
        return False
    if _is_docs_subtree(path):
        return False
    if _is_root_md(path):
        return False
    return True


def _tool_path(arguments):
    for key in TOOL_PATH_KEYS:
        value = arguments.get(key)
        if value:
            return str(value)
    return ""


def _step_write_paths(step):
    """Yield the target path of every write-tool-call in this step, in
    call order."""
    for call in step.get("tool_calls") or []:
        if call.get("function_name") not in WRITE_TOOL_NAMES:
            continue
        path = _tool_path(call.get("arguments") or {})
        if path:
            yield path


def _writing_plans_invoked(steps):
    for step in steps:
        for call in step.get("tool_calls") or []:
            blob = json.dumps(call.get("arguments") or {}, ensure_ascii=False)
            if WRITING_PLANS_NEEDLE in blob:
                return True
    return False


def score_trajectory(traj):
    """Compute the ceremony census dict for one already-parsed ATIF
    trajectory (a dict per superpowers/evals/src/atif/types.ts's
    AtifTrajectory shape)."""
    steps = traj.get("steps") or []

    first_code_file = None
    first_code_step_index = None
    for i, step in enumerate(steps):
        for path in _step_write_paths(step):
            if ceremony_doc_kind(path) is None and is_code_path(path):
                first_code_file = path
                first_code_step_index = i
                break
        if first_code_file is not None:
            break

    spec_docs_written = 0
    plan_docs_written = 0
    doc_writes_before_first_code = 0
    for i, step in enumerate(steps):
        for path in _step_write_paths(step):
            kind = ceremony_doc_kind(path)
            if kind == "specs":
                spec_docs_written += 1
            elif kind == "plans":
                plan_docs_written += 1
            if kind is not None and (
                first_code_step_index is None or i < first_code_step_index
            ):
                doc_writes_before_first_code += 1

    if first_code_step_index is None:
        turn_window = steps
    else:
        turn_window = steps[:first_code_step_index]
    user_turns_before_first_code = sum(
        1 for s in turn_window if s.get("source") == "user")

    return {
        "spec_docs_written": spec_docs_written,
        "plan_docs_written": plan_docs_written,
        "doc_writes_before_first_code": doc_writes_before_first_code,
        "first_code_file": first_code_file,
        "user_turns_before_first_code": user_turns_before_first_code,
        "writing_plans_invoked": _writing_plans_invoked(steps),
    }


def score_file(path):
    """Load a trajectory.json file and score it. `path` points directly
    at the trajectory.json file (not a run directory)."""
    with open(path) as f:
        return score_trajectory(json.load(f))
