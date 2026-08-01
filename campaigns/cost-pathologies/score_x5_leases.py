#!/usr/bin/env python3
"""X5 verification-lease scorer (cost-pathologies Task 7).

Design doc / hypothesis-log X5 section: "identical suites re-run at
identical tree state (12x worst case)... Prerequisite scorer work: the
substring-aware duplicate-command counter (the known `score_e3` upgrade)."
Amendment 1 adds a second baseline target: "the 3-restarts-in-an-hour
gate-suite pattern (escalating token cost per restart)."

This scorer extends `campaigns/codex-efficiency/score_e3.py`'s
duplicate-gate machinery (imported, never forked -- `score_e3.
TEST_INVOCATION_RE` and `score_e3._normalize_cmd` are reused directly) in
two ways score_e3 does not attempt:

1. **Substring-aware extraction.** score_e3's `test_command_events()`
   normalizes the WHOLE exec command string -- `cd x && pytest tests/`
   and bare `pytest tests/` therefore normalize to DIFFERENT strings under
   score_e3, even though they run the identical suite. This scorer instead
   finds every `TEST_INVOCATION_RE` match inside a command and extracts
   ONLY that invocation's own substring (from the match's start to the
   next shell chain terminator -- `&&`, `||`, `;`, or a newline -- or end
   of string), so a chained/compound command's test invocation normalizes
   identically to the bare form. A real-corpus wrinkle found during this
   task's corpus validation (a donated session's `custom_exec`-encoded
   calls wrap the shell command in a JS object literal, e.g. `cmd: "cargo
   test --all-features --quiet", workdir: ...`): the extracted segment can
   carry a trailing JS-wrapper artifact (a closing quote and/or comma)
   before the next real chain terminator, which `_TRAILING_ARTIFACT_RE`
   strips as a final cleanup pass. Two independent test invocations
   bundled into one exec call (`pytest a.py && pytest b.py`) are each
   captured as their own occurrence, not merged or truncated to the
   first.

2. **tree_sha attribution.** score_e3's duplicate-gate question is
   "did ANY mutation happen between two identical commands" (a boolean).
   X5 needs a per-occurrence identity: the actual tree state a
   verification ran against, so a lease/receipt mechanism can key on
   (command, tree_sha) rather than (command, ordinal-position). This
   module resolves a `tree_sha` for every occurrence from the NEAREST
   PRECEDING commit/checkout/rev-parse evidence found anywhere across the
   given rollout_paths (merged, exactly like score_e3.mutation_timeline()
   -- the evidence and the verification run routinely live in DIFFERENT
   rollout files: an implementer's own commit, read by a reviewer's later
   verification pass).

   **Resolution rule (deliberately narrow -- precision over recall):**
   an exec command is "commit/checkout/rev-parse evidence" if it matches
   exactly one of three patterns, checked in this priority order:
     - `git commit` -- the SHA is read from the paired
       function_call_output/custom_tool_call_output text, matching git's
       own commit-summary-LINE shape specifically: `[<ref> <abbrev-sha>]
       <subject>` (including the `(root-commit)` variant), not just "the
       first bracket containing a hex token anywhere in the output." A
       real corpus case (donated-session validation, fix round 2) runs a
       pre-commit hook (`cargo build`) before the commit itself, whose own
       output carries an EARLIER, unrelated bracket ("Finished `dev`
       profile `[unoptimized + debuginfo]` target(s)...") that a looser
       first-bracket-with-a-hex-token search misidentified as the commit's
       own line -- `_COMMIT_LINE_RE` requires the bracket's own content to
       be ref-then-hex shaped, which build-tool noise does not happen to
       match. Unresolved if no such line is found.
     - `git checkout <target>` -- the SHA is read from TARGET itself, only
       when TARGET is *already* a bare 7-40 char lowercase-hex token (a
       real corpus case: `git checkout 3f619c6f...`). A branch-name
       target (`git checkout main`) is real evidence -- the tree DID
       change -- but is deliberately left UNRESOLVED rather than guessed,
       since correctly discovering the resulting SHA would require
       inspecting `git rev-parse HEAD` or `git log` output this scorer
       has no way to associate with the checkout call.
     - `git rev-parse HEAD` -- the SHA is the first bare 7-40 char
       lowercase-hex token found anywhere in the paired output text
       (validated directly against a real donated-session rollout during
       this task's corpus validation, where this exact idiom is bundled
       with `git status`/`git rev-list` in one compound exec call --
       reading the OUTPUT, never the command's own text, correctly avoids
       an unrelated hex-looking token elsewhere in a compound command).

   Deliberately EXCLUDED: `git merge`/`git rebase`/`git reset` (score_e3's
   own `MUTATION_GIT_RE` mutation set) are real tree mutations but are
   NOT treated as SHA evidence here -- a fast-forward merge's "Updating
   A..B" output requires correctly picking the SECOND hex token as the
   new state (verified against a real donated-session merge-to-main step
   during corpus validation: the FIRST token is the OLD sha), and a
   non-fast-forward merge creates a brand new commit with no SHA printed
   in the merge output at all. Reliably disambiguating these is out of
   scope for a MINE-tier heuristic; per this module's own resolution
   contract, an unresolvable mutation must yield `tree_sha: null`, never a
   guessed or silently-wrong value.

   The nearest-preceding rule always wins even when that nearest evidence
   is itself unresolved (a resolved-then-unresolved sequence yields
   `null`, not a stale fallback to the older resolved SHA) -- see
   `test_nearest_evidence_wins_even_if_unresolved` in the test suite. Two
   occurrences of the identical command_norm are grouped as a genuine
   duplicate in `duplicate_groups` ONLY when both resolve to the SAME
   non-null tree_sha; a `None` tree_sha is never merged with anything,
   including another `None` (per the Task 7 brief: "unresolvable -> tree_
   sha null, counted separately, never silently merged").

**lease_events grammar -- a SPEC, not a discovered format.** X5-A/X5-B (the
"receipts in report" / "machine-checkable receipt file" arms) do not exist
yet as of this task -- they are Task 11's job (arm branches `cp/x5a`,
`cp/x5b`). The three line markers below are this scorer's OWN DEFINITION of
the receipt grammar those arms MUST emit for `lease_events` to have any
signal; they are not reverse-engineered from a real artifact. Any
corpus-validation run against a pre-arm session (which is all of them,
today) legitimately reads `receipts_issued == receipts_honored ==
invalidation_reruns == 0` -- that is the CORRECT, honest output, not a bug.

    LEASE-RECEIPT: command=<command_norm> tree_sha=<sha> result=<pass|fail>
    LEASE-HONORED: command=<command_norm> tree_sha=<sha>
    LEASE-INVALIDATED: command=<command_norm> tree_sha=<sha>

A line matching `LEASE-RECEIPT:` records a NEW verification result (X5-A:
"implementer report carries command+tree-SHA+result"). `LEASE-HONORED:`
records a later seat (reviewer/finishing) explicitly declining to re-run
because an existing receipt already covers this command at this tree_sha.
`LEASE-INVALIDATED:` records a seat recognizing the tree changed since the
last receipt for this command and re-running it -- the invalidation-probe
guard's positive case ("mutate the tree mid-flow and the suite MUST
re-run"). The marker is case-sensitive and line-anchored (`re.MULTILINE`);
`result=` is optional (only meaningful on a RECEIPT line). Scanned across
every session given: each rollout's own final_answer-phase messages
(`rollout_parser.final_answers()`, X5-A's report-in-prose channel), every
inter-agent message payload (`rollout_parser.inter_agent_messages()`, so a
receipt is found whether read from the child's own transcript or a
parent's relayed view of it), and every exec/custom_exec command OUTPUT
text (covers X5-B's machine-checkable file being read back via `cat` by a
later seat, not just prose).

**Privacy note, a deliberate divergence from score_e3's convention.**
score_e3 never exposes raw/normalized command TEXT on an output record,
anonymizing every occurrence to a per-run `cmd_id` instead -- necessary
there because score_e3's `TEST_INVOCATION_RE`-matched commands can carry
arbitrary surrounding shell content (real corpus commands routinely bundle
diagnostic subcommands, paths, flags specific to the project). This
scorer's `command_norm` is narrower BY CONSTRUCTION: it is exactly the
`TEST_INVOCATION_RE`-matched invocation substring (a test-runner name plus
its own args/paths, e.g. "pytest tests/", "npm test", "cargo test
--all-features --quiet") with everything outside that substring already
stripped. Per the Task 7 interface brief, `command_norm` is exposed
directly on `verification_runs`/`duplicate_groups` rather than anonymized
-- this is a considered choice for this narrower field, not an oversight;
callers that print or log this scorer's output should still keep the
campaign's standing convention of citing AGGREGATES only (counts, not
raw text) in anything committed.

Usage: `lease_stats(rollout_paths)`. Read-only; makes no writes.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "codex-efficiency"))
import rollout_parser as rp
import score_e3 as se

# --- substring-aware test-invocation extraction ---------------------------

# Real shell chain separators that end ONE logical command and start the
# next -- deliberately excludes a bare `|` (pipe), which commonly redirects
# the SAME command's own output (`pytest tests/ | tee log.txt`) rather than
# chaining a separate command.
_CHAIN_TERMINATOR_RE = re.compile(r"&&|\|\||;|\n")

# A one-line JS/JSON object-literal field boundary -- a closing quote,
# comma, and the start of the NEXT key (quoted "workdir": or unquoted JS
# shorthand workdir:). Real corpus shape found during this task's corpus
# validation (fix round 1): a single-line custom_exec call has no newline
# between the "cmd" value and the next field, only a comma -- neither a
# chain terminator nor plain trailing-punctuation cleanup catches this on
# its own (the terminator search never fires, and stripping only the
# extracted segment's own trailing chars can't remove text that comes
# BEFORE further real content). The match's OWN start (the closing quote)
# is used as the segment boundary, so the quote itself is excluded. Gated
# to "custom_exec" encoding only (see _extract_test_invocations) -- a
# plain "exec_command"-encoded shell command is already fully decoded
# real shell text with no JS wrapper, so this JS-specific heuristic must
# never run on it.
_JS_FIELD_BOUNDARY_RE = re.compile(r'"\s*,\s*"?\w+"?\s*:')

# Cleans up a custom_exec JS-wrapper artifact left at the end of an
# extracted segment when the shell command was embedded in a quoted JS
# object-literal field (see module docstring's real-corpus example) --
# e.g. a trailing `",` (next field follows with no chain terminator
# between) or `"});` (the call's own closing syntax, cut short by the
# chain-terminator regex's own `;` match). Deliberately requires the
# stripped run to START with a literal double-quote -- NOT a blanket
# trailing-character-class strip. Real corpus shape found during this
# task's corpus validation (fix round 3): a `go test -run '<regex>'`
# argument routinely closes with a legitimate `)'` (a regex group's own
# closing paren, then the shell's own single quote) -- a blanket class
# strip of `)`/`'`/`]`/`}` corrupted this, truncating the argument. Only
# the JS wrapper's own double-quote marks a real boundary; a trailing
# single quote or parenthesis that is part of the shell command's own
# syntax is left untouched. Gated to "custom_exec" encoding only, same
# reasoning as _JS_FIELD_BOUNDARY_RE above.
_TRAILING_ARTIFACT_RE = re.compile(r'"[\s,;)\]}]*$')


def _segment_end(cmd, start, encoding):
    """The earliest of: the next chain terminator, the next JS/JSON
    field boundary (custom_exec only), or end of string -- see
    _JS_FIELD_BOUNDARY_RE's comment for why both are needed."""
    ends = [len(cmd)]
    m = _CHAIN_TERMINATOR_RE.search(cmd, start)
    if m:
        ends.append(m.start())
    if encoding == "custom_exec":
        m = _JS_FIELD_BOUNDARY_RE.search(cmd, start)
        if m:
            ends.append(m.start())
    return min(ends)


def _extract_test_invocations(cmd, encoding="custom_exec"):
    """Every substring-aware TEST_INVOCATION_RE occurrence in CMD, each
    independently normalized -- see module docstring for the extraction
    rule. ENCODING selects whether the custom_exec-only JS-wrapper
    cleanup runs (see _JS_FIELD_BOUNDARY_RE / _TRAILING_ARTIFACT_RE);
    defaults to "custom_exec" since every caller in this module already
    knows its rollout_parser.ExecCmd.encoding, and the cleanup is a
    no-op on text with nothing to strip. `[]` if CMD contains no test
    invocation."""
    matches = list(se.TEST_INVOCATION_RE.finditer(cmd))
    out = []
    for i, m in enumerate(matches):
        start = m.start()
        end = _segment_end(cmd, m.end(), encoding)
        if i + 1 < len(matches):
            end = min(end, matches[i + 1].start())
        segment = cmd[start:end]
        if encoding == "custom_exec":
            segment = _TRAILING_ARTIFACT_RE.sub("", segment)
        norm = se._normalize_cmd(segment)
        if norm:
            out.append(norm)
    return out


def _test_events(path):
    """Every substring-aware test-invocation OCCURRENCE in PATH, each a
    dict with `command_norm`/`timestamp`/`call_id`. Matches against the
    DE-ESCAPED command text (`rollout_parser.deescape_custom_exec()`),
    same convention as score_e3.test_command_events()."""
    out = []
    for ec in rp.exec_commands(path):
        cmd = rp.deescape_custom_exec(ec.cmd, ec.encoding)
        for norm in _extract_test_invocations(cmd, ec.encoding):
            out.append({"command_norm": norm, "timestamp": ec.timestamp, "call_id": ec.call_id})
    return out


# --- tree_sha evidence resolution ------------------------------------------

_GIT_COMMIT_CMD_RE = re.compile(r"\bgit commit\b")
_GIT_CHECKOUT_CMD_RE = re.compile(r"\bgit checkout\s+(\S+)")
_GIT_REVPARSE_CMD_RE = re.compile(r"\bgit rev-parse\s+HEAD\b")
_BARE_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
_HEX_TOKEN_RE = re.compile(r"\b[0-9a-f]{7,40}\b")

# Git's own commit-summary-line shape: "[<ref> [(root-commit)] <abbrev-sha>]
# <subject>". Deliberately NOT "the first [...] bracket containing a hex
# token anywhere in the output" -- a real corpus case (donated-session
# validation, fix round 2) has a pre-commit hook run `cargo build` FIRST,
# whose own output contains an unrelated, earlier bracket ("Finished `dev`
# profile [unoptimized + debuginfo] target(s)...") that a looser
# first-bracket search would misidentify as the commit's own line. This
# pattern requires the bracket's content to be shaped like git's own
# "<ref> <hex>" (or "<ref> (root-commit) <hex>"), which build-tool noise
# does not happen to match.
_COMMIT_LINE_RE = re.compile(r"\[\S+(?:\s+\(root-commit\))?\s+([0-9a-f]{7,40})\]")


def _output_text(payload):
    """The plain text of a function_call_output/custom_tool_call_output
    payload's `output` value: a bare string (the "exec_command" encoding's
    real shape) or a list of {"type":..., "text":...} content dicts (the
    "custom_tool_call_output" encoding's real shape) -- both verified
    directly against a donated-session rollout during this task's corpus
    validation."""
    raw = payload.get("output")
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        return "".join(c.get("text", "") for c in raw if isinstance(c, dict))
    return ""


def _collect_call_outputs(path):
    """call_id -> output text, for every function_call_output/
    custom_tool_call_output record in PATH."""
    outputs = {}
    for _ts, typ, p in rp.iter_records(path):
        if typ != "response_item":
            continue
        if p.get("type") not in ("function_call_output", "custom_tool_call_output"):
            continue
        call_id = p.get("call_id")
        if call_id is not None:
            outputs[call_id] = _output_text(p)
    return outputs


def _sha_from_commit_output(text):
    if not text:
        return None
    m = _COMMIT_LINE_RE.search(text)
    return m.group(1) if m else None


def _sha_from_text(text):
    if not text:
        return None
    m = _HEX_TOKEN_RE.search(text)
    return m.group(0) if m else None


def _git_evidence(rollout_paths):
    """Every commit/checkout/rev-parse-HEAD evidence event across ALL
    ROLLOUT_PATHS, merged and sorted by timestamp -- see module docstring
    for the resolution rule (why only these three shapes, in this
    priority, and why merge/rebase/reset are deliberately excluded)."""
    events = []
    for path in rollout_paths:
        outputs = _collect_call_outputs(path)
        for ec in rp.exec_commands(path):
            cmd = rp.deescape_custom_exec(ec.cmd, ec.encoding)
            checkout_m = _GIT_CHECKOUT_CMD_RE.search(cmd)
            if _GIT_COMMIT_CMD_RE.search(cmd):
                sha = _sha_from_commit_output(outputs.get(ec.call_id))
            elif checkout_m:
                target = checkout_m.group(1)
                sha = target if _BARE_SHA_RE.match(target) else None
            elif _GIT_REVPARSE_CMD_RE.search(cmd):
                sha = _sha_from_text(outputs.get(ec.call_id))
            else:
                continue
            events.append({"timestamp": ec.timestamp, "sha": sha})
    events.sort(key=lambda e: e["timestamp"])
    return events


def _resolve_tree_sha(ts, evidence_events):
    """The `sha` of the LATEST evidence event with timestamp STRICTLY
    BEFORE ts, or None if no evidence precedes it at all. The nearest
    event always wins, even if its own sha is unresolved (None) -- see
    module docstring."""
    preceding = [e for e in evidence_events if e["timestamp"] < ts]
    if not preceding:
        return None
    return max(preceding, key=lambda e: e["timestamp"])["sha"]


# --- duplicate_groups -------------------------------------------------------

def _duplicate_groups(verification_runs):
    """Every (command_norm, tree_sha) group with >=2 occurrences --
    tree_sha=None occurrences are never grouped (counted separately,
    never silently merged, per the Task 7 brief). Sorted by each group's
    earliest occurrence timestamp for determinism."""
    groups = {}
    order = []
    for run in verification_runs:
        if run["tree_sha"] is None:
            continue
        key = (run["command_norm"], run["tree_sha"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(run)

    out = []
    for key in order:
        runs = groups[key]
        if len(runs) < 2:
            continue
        command_norm, tree_sha = key
        out.append((min(r["timestamp"] for r in runs), {
            "command_norm": command_norm,
            "tree_sha": tree_sha,
            "count": len(runs),
            "sessions": [r["session_id"] for r in runs],
        }))
    out.sort(key=lambda pair: pair[0])
    return [g for _ts, g in out]


# --- lease_events (LEASE-RECEIPT/HONORED/INVALIDATED grammar) --------------

_LEASE_LINE_RE = re.compile(
    r"^LEASE-(?P<kind>RECEIPT|HONORED|INVALIDATED):\s*"
    r"command=(?P<command_norm>.+?)\s+tree_sha=(?P<tree_sha>\S+)"
    r"(?:\s+result=(?P<result>pass|fail))?\s*$",
    re.MULTILINE)


def _text_sources(path):
    """Every text body in PATH worth scanning for LEASE- marker lines --
    see module docstring's "Scanned across" note for why all three
    sources are included."""
    texts = []
    for f in rp.final_answers(path):
        if f.phase == "final_answer":
            texts.append(f.message)
    for m in rp.inter_agent_messages(path):
        texts.append(m.payload)
    texts.extend(_collect_call_outputs(path).values())
    return texts


def _lease_events(rollout_paths):
    receipts_issued = receipts_honored = invalidation_reruns = 0
    for path in rollout_paths:
        for text in _text_sources(path):
            if not text:
                continue
            for m in _LEASE_LINE_RE.finditer(text):
                kind = m.group("kind")
                if kind == "RECEIPT":
                    receipts_issued += 1
                elif kind == "HONORED":
                    receipts_honored += 1
                else:
                    invalidation_reruns += 1
    return {"receipts_issued": receipts_issued, "receipts_honored": receipts_honored,
            "invalidation_reruns": invalidation_reruns}


# --- top-level ---------------------------------------------------------------

def lease_stats(rollout_paths):
    """Every substring-aware verification-command occurrence across
    ROLLOUT_PATHS, each attributed a tree_sha and grouped into duplicate
    runs, plus the LEASE- receipt/lease-event census. See module docstring
    for the full contract."""
    rollout_paths = sorted(rollout_paths)
    evidence = _git_evidence(rollout_paths)

    verification_runs = []
    for path in rollout_paths:
        session_id = os.path.basename(path)
        for ev in _test_events(path):
            verification_runs.append({
                "command_norm": ev["command_norm"],
                "tree_sha": _resolve_tree_sha(ev["timestamp"], evidence),
                "timestamp": ev["timestamp"],
                "session_id": session_id,
            })
    verification_runs.sort(key=lambda r: (r["timestamp"], r["session_id"]))

    return {
        "verification_runs": verification_runs,
        "duplicate_groups": _duplicate_groups(verification_runs),
        "lease_events": _lease_events(rollout_paths),
    }


def main(argv):
    if len(argv) < 2:
        print("usage: score_x5_leases.py ROLLOUT_PATH...", file=sys.stderr)
        return 1
    result = lease_stats(argv[1:])
    runs = result["verification_runs"]
    groups = result["duplicate_groups"]
    events = result["lease_events"]
    print(f"# X5 verification-lease scorer -- {len(runs)} verification run(s), "
          f"{len(groups)} duplicate group(s)")
    print()
    for g in groups:
        print(f"  DUPLICATE x{g['count']}  tree_sha={g['tree_sha']}  command={g['command_norm']!r}")
        print(f"      sessions: {g['sessions']}")
    print()
    print(f"lease_events: receipts_issued={events['receipts_issued']} "
          f"receipts_honored={events['receipts_honored']} "
          f"invalidation_reruns={events['invalidation_reruns']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
