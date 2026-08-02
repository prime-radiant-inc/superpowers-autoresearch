#!/usr/bin/env python3
"""Recovers a battery rep's `.superpowers/sdd/<plan>/progress.md` (or any
other apply_patch-touched file, via --path-suffix) content from the rep's
raw rollout JSONL, POST HOC (queue-execution campaign, Task 4, item 23).

WHY. The SDD scratch workspace (`.superpowers/sdd/<plan>/progress.md`
inside the coding-agent's working clone) is deleted by the coding-agent's
own SDD finishing step before quorum captures results -- by design, this
script does NOT change any agent-visible behavior to preserve it (that
would alter the system under test). Instead: every write to progress.md
went through codex's own `apply_patch` tool, and BOTH the apply_patch
invocation and its `patch_apply_end` outcome are captured in the rep's
raw rollout JSONL, which is never deleted. This module reconstructs the
file's final content by replaying every apply_patch call that touched it,
in chronological order.

REAL CORPUS SHAPE (verified directly against `evals/results/cp-x2-
advisory-control-rep1`'s root rollout before writing this module -- see
task-4-report.md for the exact lines cited). apply_patch runs through the
`custom_tool_call`/name=="exec" encoding (see rollout_parser.py's
exec_commands() docstring for the two known exec encodings), as a JS
snippet of the shape:

    const patch = "*** Begin Patch\\n*** Add File: <path>\\n"
      "+<line>\\n...*** End Patch";
    text(await tools.apply_patch(patch));

using codex's own "V4A" patch dialect: `*** Begin Patch` / `*** End
Patch` bracket one or more per-file directives (`*** Add File: <path>`,
`*** Delete File: <path>`, `*** Update File: <path>` optionally followed
by `*** Move to: <newpath>`); an Add File's body is `+`-prefixed content
lines (the WHOLE file); an Update File's body is one or more `@@`-headed
hunks of ` `/`-`/`+`-prefixed lines (context / removed / added).

SCOPE CUT (deliberate). This is NOT a general-purpose V4A/patch engine --
it implements just enough of the dialect to reconstruct ONE target file's
content from this campaign's own real corpus, which (checked directly,
every progress.md hunk across the validation reps) never uses removed
("-") lines: progress.md is an append-only ledger. Update-hunk context
matching and a removed-line code path are still implemented (never just
assumed away) since the dialect allows them and a future corpus could use
them, but there is no real-corpus evidence exercising deletion within a
hunk. A hunk whose context can't be located in the currently-recovered
content is NOT silently dropped -- its added lines are appended instead,
and a warning is recorded, so a caller can see the recovery degraded
without either crashing or losing the content (see recover_files()).
"""
import argparse
import dataclasses
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "codex-efficiency"))
import rollout_parser as rp
from scorer_common import find_files

# Matches the JS wrapper's apply_patch invocation -- present iff this
# custom_exec call is an apply_patch, not some other exec-encoded script.
APPLY_PATCH_CALL_RE = re.compile(r"tools\.apply_patch\s*\(")

# Extracts the `const patch = "...";` string literal's raw (still
# JS-escaped) contents. Non-greedy body matched as "anything except an
# unescaped quote", terminated by an unescaped closing quote -- matches
# json.loads' own string-literal grammar closely enough for this corpus's
# emitted shape (no unicode \u escapes observed; only \n \t \" \\, which
# rollout_parser.deescape_custom_exec already decodes).
PATCH_VAR_RE = re.compile(r'const\s+patch\s*=\s*"((?:[^"\\]|\\.)*)"\s*;')

SECTION_HEADER_RE = re.compile(r"^\*\*\* (Add File|Delete File|Update File): (.+)$")
MOVE_TO_RE = re.compile(r"^\*\*\* Move to: (.+)$")
HUNK_START_RE = re.compile(r"^@@")
BEGIN_PATCH_RE = re.compile(r"^\*\*\* Begin Patch$")
END_PATCH_RE = re.compile(r"^\*\*\* End Patch$")

_ACTIONS = {"Add File": "add", "Delete File": "delete", "Update File": "update"}


@dataclasses.dataclass
class PatchSection:
    action: str            # "add" | "delete" | "update"
    path: str
    move_to: str | None
    lines: list             # "add": the full file content, one entry per line
    hunks: list              # "update": list[list[(marker, text)]], marker in " -+"


def parse_patch_sections(patch_text):
    """Parse a de-escaped (real newlines/quotes) V4A PATCH_TEXT bracketed
    by `*** Begin Patch` / `*** End Patch` into a list of PatchSection,
    one per Add/Delete/Update File directive, in the order they appear."""
    lines = patch_text.split("\n")
    sections = []
    i, n = 0, len(lines)
    while i < n and not BEGIN_PATCH_RE.match(lines[i].strip()):
        i += 1
    i += 1  # past "*** Begin Patch"

    current = None
    while i < n:
        line = lines[i]
        if END_PATCH_RE.match(line.strip()):
            break
        header = SECTION_HEADER_RE.match(line)
        if header:
            if current is not None:
                sections.append(current)
            current = PatchSection(action=_ACTIONS[header.group(1)],
                                    path=header.group(2), move_to=None,
                                    lines=[], hunks=[])
            i += 1
            continue
        if current is None:
            i += 1
            continue
        move = MOVE_TO_RE.match(line)
        if move:
            current.move_to = move.group(1)
            i += 1
            continue
        if current.action == "add":
            if line.startswith("+"):
                current.lines.append(line[1:])
            i += 1
            continue
        if current.action == "update":
            if HUNK_START_RE.match(line):
                current.hunks.append([])
                i += 1
                continue
            if line[:1] in (" ", "-", "+") and current.hunks:
                marker, text = line[0], line[1:]
                current.hunks[-1].append((marker, text))
            i += 1
            continue
        # "delete" sections have no body.
        i += 1

    if current is not None:
        sections.append(current)
    return sections


def _find_subsequence(haystack, needle, start):
    """First index >= START where NEEDLE occurs as a contiguous
    subsequence of HAYSTACK, or None if it never does."""
    n = len(needle)
    if n == 0 or start + n > len(haystack):
        return None
    for i in range(start, len(haystack) - n + 1):
        if haystack[i:i + n] == needle:
            return i
    return None


def apply_sections(state, sections, warnings, source_desc=""):
    """Mutate STATE (dict: path -> list[str] of lines) by applying each
    PatchSection in SECTIONS, in order. WARNINGS (a list) collects a
    human-readable note for every hunk that could not be located by
    context match, or an Update File with no prior recovered content --
    in both cases the hunk's added lines are still appended rather than
    dropped, so recovery degrades gracefully instead of silently losing
    content or crashing. SOURCE_DESC identifies where a warning
    originated (e.g. "<rollout basename>@<timestamp>") for triage."""
    for sec in sections:
        if sec.action == "add":
            state[sec.path] = list(sec.lines)
            continue
        if sec.action == "delete":
            state.pop(sec.path, None)
            continue
        # "update"
        path = sec.path
        content = state.get(path)
        if content is None:
            content = []
            warnings.append(
                f"{source_desc}: Update File {path} had no prior "
                "recovered content (file pre-existed outside any "
                "recovered Add File in this rep) -- starting from empty")
        cursor = 0
        for hunk in sec.hunks:
            search = [text for marker, text in hunk if marker in (" ", "-")]
            replace = [text for marker, text in hunk if marker in (" ", "+")]
            added_only = [text for marker, text in hunk if marker == "+"]
            idx = _find_subsequence(content, search, cursor) if search else None
            if idx is None:
                if search:
                    warnings.append(
                        f"{source_desc}: hunk context not found in {path}, "
                        "appended instead of spliced")
                # Only the genuinely NEW ("+") lines are appended -- the
                # hunk's context lines describe text that (by definition of
                # this branch) was never actually located in CONTENT, so
                # appending them too would inject fabricated content.
                content.extend(added_only)
                cursor = len(content)
            else:
                content[idx:idx + len(search)] = replace
                cursor = idx + len(replace)
        target = sec.move_to or path
        if sec.move_to:
            state.pop(path, None)
        state[target] = content


def find_apply_patch_calls(rollout_path):
    """Every custom_tool_call/"exec" record in ROLLOUT_PATH whose JS input
    invokes tools.apply_patch(...), returned as (timestamp, patch_text)
    pairs in file order, with the embedded patch string extracted and
    JS-de-escaped (real newlines/quotes -- reuses rollout_parser.
    deescape_custom_exec, the same JS-escape map exec_commands() callers
    already rely on). A custom_exec record that doesn't match this
    corpus's `const patch = "...";` + `apply_patch(patch)` shape is
    skipped, not guessed at."""
    out = []
    for ts, typ, p in rp.iter_records(rollout_path):
        if typ != "response_item" or p.get("type") != "custom_tool_call" \
           or p.get("name") != "exec":
            continue
        input_text = p.get("input") or ""
        if not APPLY_PATCH_CALL_RE.search(input_text):
            continue
        m = PATCH_VAR_RE.search(input_text)
        if not m:
            continue
        patch_text = rp.deescape_custom_exec(m.group(1), "custom_exec")
        out.append((ts, patch_text))
    return out


def recover_files(rep_dir, path_suffix="progress.md"):
    """Recovers the final reconstructed content of every apply_patch-
    touched path under REP_DIR ending in PATH_SUFFIX (default:
    "progress.md" -- a rep in this campaign runs exactly one SDD plan, so
    exactly one path is expected in practice; this returns whatever it
    actually finds, not an assumption).

    Every rollout file under REP_DIR (root AND every subagent) is
    scanned, dot-directory-safe via scorer_common.find_files() -- NOT a
    bare glob (rollout paths live under `**/home/.codex/sessions/**`,
    which `glob.glob(pattern, recursive=True)` silently refuses to
    descend into; see scorer_common.py's module docstring and Task 3's
    dot-directory audit) -- and every apply_patch call across ALL of them
    is collected, then applied in GLOBAL timestamp order (not per-file
    order): a subagent's own rollout can chronologically interleave with
    its parent's, and per-file-then-file application would silently
    misorder that.

    A "Delete File" of the recovery target itself is expected: it is
    exactly the SDD finishing step's own scratch-workspace cleanup this
    tool exists to see past (real corpus finding, `cp-x2-advisory-x2a-
    rep1`: the finishing step's own apply_patch deletes progress.md as
    its last write to it). recover_files() does NOT let that deletion
    erase already-recovered content -- apply_sections() itself still
    implements faithful delete semantics (it is a general patch-replay
    function; a delete of some OTHER, non-target path must still behave
    like a real delete), but recover_files() deliberately never feeds it
    a delete of the PATH_SUFFIX-matching target, logging a note in
    WARNINGS instead so the last-known content survives.

    Returns (state, warnings): STATE maps each recovered path (as it
    appears in the patch, i.e. the coding-agent's own workdir-absolute
    form) to its recovered content as a single string (lines joined with
    "\\n", no trailing newline added); WARNINGS is the list of degraded-
    recovery notes from apply_sections() plus this function's own
    deletion notes (never raises on either -- see apply_sections()'s
    docstring)."""
    rollout_paths = find_files(rep_dir, "rollout-*.jsonl",
                                path_contains=os.path.join("home", ".codex", "sessions"))
    calls = []  # (timestamp, source_desc, patch_text)
    for rollout_path in rollout_paths:
        basename = os.path.basename(rollout_path)
        for ts, patch_text in find_apply_patch_calls(rollout_path):
            calls.append((ts, basename, patch_text))
    calls.sort(key=lambda c: c[0])

    state = {}
    warnings = []
    for ts, basename, patch_text in calls:
        source_desc = f"{basename}@{ts}"
        sections = []
        for s in parse_patch_sections(patch_text):
            if not s.path.endswith(path_suffix):
                continue
            if s.action == "delete":
                warnings.append(
                    f"{source_desc}: {s.path} was deleted by the session "
                    "(expected SDD finishing-step cleanup) -- recovered "
                    "content is its last state before that deletion")
                continue
            sections.append(s)
        if not sections:
            continue
        apply_sections(state, sections, warnings, source_desc=source_desc)

    return {path: "\n".join(lines) for path, lines in state.items()}, warnings


def main():
    ap = argparse.ArgumentParser(
        description="Recover an SDD progress.md (or other apply_patch-"
                     "touched file) from a battery rep's raw rollout JSONL.")
    ap.add_argument("rep_dir",
                     help="a battery rep's result directory, e.g. "
                          "evals/results/cp-x2-advisory-control-rep1")
    ap.add_argument("--path-suffix", default="progress.md",
                     help="recover paths ending in this (default: progress.md)")
    ap.add_argument("--out",
                     help="write the recovered content here (requires exactly "
                          "one recovered path); default: print all to stdout")
    args = ap.parse_args()

    state, warnings = recover_files(args.rep_dir, args.path_suffix)
    for w in warnings:
        print(f"extract_ledger: warning: {w}", file=sys.stderr)

    if not state:
        print(f"extract_ledger: no apply_patch-touched path ending in "
              f"{args.path_suffix!r} found under {args.rep_dir}", file=sys.stderr)
        sys.exit(1)

    if args.out:
        if len(state) != 1:
            print(f"extract_ledger: --out requires exactly one recovered "
                  f"path (found {len(state)}); omit --out to print all to "
                  "stdout", file=sys.stderr)
            sys.exit(1)
        ((_, content),) = state.items()
        with open(args.out, "w") as f:
            f.write(content)
    else:
        for path, content in state.items():
            print(f"=== {path} ===")
            print(content)


if __name__ == "__main__":
    main()
