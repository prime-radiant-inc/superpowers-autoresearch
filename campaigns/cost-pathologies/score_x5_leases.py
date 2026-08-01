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
parent's relayed view of it), every exec/custom_exec command OUTPUT text
(covers X5-B's machine-checkable file being read back via `cat` by a
later seat, not just prose), and (queue-campaign Task 2, item 10) every
exec/custom_exec command's own CALL text (de-escaped, diff-marker-
stripped -- see `_DIFF_MARKER_LEASE_RE`), so a marker WRITTEN but never
read back by any later tool call is still counted.

**Distinct-event counting (queue-campaign Task 2, item 10).** `lease_
events`'s three strict counts are DISTINCT `(kind, command_norm,
tree_sha)` events, not raw marker-line regex-match counts. An append-only
receipts file gets re-matched every time it is re-read (a later `cat`, or
a later `apply_patch` diff hunk showing an earlier line as unchanged
context) -- this campaign's own I2 correction
(`logs/2026-07-31-cost-pathologies.md`, 2026-08-01 entry) found a real
X5-B rep whose 10 raw `LEASE-RECEIPT` matches collapsed to only 4
distinct tree_sha values once deduplicated. `_lease_events()` dedups
globally across every given rollout path (the same event relayed into a
second session's transcript is still one event) and per kind (a RECEIPT
and a HONORED line sharing a command_norm/tree_sha are different events).
Deliberately NOT keyed on `result` too, per this task's own brief.

**Prose-aware honor/invalidate detector (queue-campaign Task 2, item 9)
-- ADDED alongside, never replacing, the strict grammar above.** Real
corpus finding (this campaign's C1 correction, same log, same entry):
codex reviewers under X5-A routinely narrate honoring or declining a
supplied lease receipt in their OWN WORDS rather than reproducing the
fixed marker syntax -- a real scorer-coverage gap under this harness, not
a behavioral absence. Reported as separate `receipts_honored_prose`/
`invalidation_reruns_prose` fields on `lease_events`, computed by
`_lease_events_prose()`: a lease/receipt TERM and an explicit rerun-or-
not PHRASE (`_PROSE_HONOR_PHRASE_RE`/`_PROSE_INVALIDATE_PHRASE_RE`) must
co-occur on the SAME line of the same `_text_sources()` text (after
masking out any strict-grammar line, so a real marker is never
double-counted). Deliberately conservative -- precision over recall, per
this task's own brief ("a missed prose-honoring is a disclosed
limitation; a false honor-credit corrupts a savings battery"): 7 of the
8 real X5-A prose exchanges this campaign found are caught; the 8th (a
bare citation with no explicit rerun-or-not statement) is an intentional,
disclosed miss. See `TestLeaseEventsProseDetector` (cites rep dir +
rollout file per case) and this task's report for the corpus and the
precision/recall analysis.

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

# X5-B's machine-checkable receipts file is written via `apply_patch`
# unified-diff hunks (real corpus shape, confirmed directly in
# cp-x5-leases-x5b-rep3's raw rollout during this task's corpus
# validation -- see test_apply_patch_diff_prefixed_lease_line_recovered_
# from_command_text): every line in an Add/Update File hunk carries a
# leading +/-/space diff marker, so a LEASE- line WRITTEN this way
# ("+LEASE-HONORED: command=... tree_sha=...") never satisfies
# _LEASE_LINE_RE's line-start anchor even once exec CALL command text is
# scanned (below) -- that receipts file is never read back via a plain
# `cat` in this rep, so without this the write is invisible to any
# scanner. Stripping the ONE leading diff-marker character from a line
# that would otherwise start with "LEASE-" recovers these writes without
# loosening the grammar itself for any other source (final_answer text,
# inter-agent messages, exec OUTPUT text are never diff-shaped).
_DIFF_MARKER_LEASE_RE = re.compile(
    r"^[+\- ](?=LEASE-(?:RECEIPT|HONORED|INVALIDATED):)", re.MULTILINE)


def _text_sources(path):
    """Every text body in PATH worth scanning for LEASE- marker lines --
    see module docstring's "Scanned across" note for why all sources are
    included. Queue-campaign Task 2 (item 10) added exec CALL command
    text (de-escaped, diff-marker-stripped -- see _DIFF_MARKER_LEASE_RE)
    alongside the original final_answer/inter_agent/exec-OUTPUT sources,
    to catch a marker WRITTEN but never subsequently read back by any
    later tool call."""
    texts = []
    for f in rp.final_answers(path):
        if f.phase == "final_answer":
            texts.append(f.message)
    for m in rp.inter_agent_messages(path):
        texts.append(m.payload)
    for ec in rp.exec_commands(path):
        cmd = rp.deescape_custom_exec(ec.cmd, ec.encoding)
        texts.append(_DIFF_MARKER_LEASE_RE.sub("", cmd))
    texts.extend(_collect_call_outputs(path).values())
    return texts


def _lease_events(rollout_paths):
    """Queue-campaign Task 2 (item 10): counts DISTINCT (kind,
    command_norm, tree_sha) events, not raw marker-line regex
    occurrences. An append-only receipts file re-read (a later `cat`, or
    a later apply_patch diff hunk showing an earlier line as unchanged
    context) matches the SAME event every time it is read, which a
    per-match counter over-counts -- root-caused in this campaign's own
    I2 correction (logs/2026-07-31-cost-pathologies.md, 2026-08-01
    entry): a real X5-B rep's 10 raw LEASE-RECEIPT regex matches
    collapsed to only 4 distinct tree_sha values once deduplicated.
    Dedup is GLOBAL across all of ROLLOUT_PATHS (the same event relayed
    into a second session's transcript is still one event, not two), and
    keyed PER KIND (a RECEIPT and a HONORED line sharing an identical
    command_norm/tree_sha are different events, never merged with each
    other) -- deliberately NOT keyed on `result` too (per this task's own
    brief: dedup on exactly (kind, command_norm, tree_sha))."""
    seen = {"RECEIPT": set(), "HONORED": set(), "INVALIDATED": set()}
    for path in rollout_paths:
        for text in _text_sources(path):
            if not text:
                continue
            for m in _LEASE_LINE_RE.finditer(text):
                seen[m.group("kind")].add((m.group("command_norm"), m.group("tree_sha")))
    return {"receipts_issued": len(seen["RECEIPT"]),
            "receipts_honored": len(seen["HONORED"]),
            "invalidation_reruns": len(seen["INVALIDATED"])}


# --- lease_events prose-aware honor/invalidate detector (item 9) -----------

# ADDED alongside (never replacing) the strict grammar above. Real corpus
# finding (this campaign's C1 correction,
# logs/2026-07-31-cost-pathologies.md, 2026-08-01 entry, "X5-A's
# honoring/invalidation mechanism IS observable in plaintext"): codex
# reviewers under X5-A routinely narrate honoring or declining a supplied
# lease receipt in their OWN WORDS instead of reproducing the fixed
# marker syntax the strict grammar requires -- a real scorer-coverage
# gap, not a behavioral absence. 8 such exchanges were found across the
# 3 x5a reps (TestLeaseEventsProseDetector in the test suite cites rep
# dir + rollout file for each). This detector is DELIBERATELY
# conservative -- precision over recall, per this task's own brief ("a
# missed prose-honoring is a disclosed limitation; a false honor-credit
# corrupts a savings battery"): it requires a lease/receipt TERM and an
# explicit rerun-or-not PHRASE to co-occur on the SAME line (this
# corpus's reviewer statements are consistently one sentence per line/
# bullet). 7 of the real corpus's 8 known exchanges satisfy this; the
# 8th (a bare citation of "the supplied HEAD receipt records the full
# suite passing" with no explicit rerun-or-not statement) is an
# intentional, disclosed miss -- see this task's report for the
# precision/recall analysis.
_PROSE_TERM_RE = re.compile(r"\b(?:lease|receipt)\b", re.I)

_PROSE_HONOR_PHRASE_RE = re.compile(
    r"\b(?:not\s+re-?run|did\s+not\s+rerun|was\s+not\s+rerun|"
    r"without\s+rerunning|honou?red|LEASE-HONORED)\b", re.I)

_PROSE_INVALIDATE_PHRASE_RE = re.compile(
    r"\b(?:does\s+not\s+certify|invalidat\w*|LEASE-INVALIDATED|"
    r"independent\w*\s+(?:focused\s+)?verification\s+was\s+run)\b", re.I)

# The grammar's own SPEC gets quoted verbatim inside the X5-A/X5-B plan's
# own dispatch instructions, read back by every seat in every rep of BOTH
# arms (real corpus shape found identically across all 6 x5a/x5b reps
# during this task's full-corpus precision check) -- e.g. "`LEASE-
# HONORED: command=<the command> tree_sha=<the sha>`" as a literal
# grammar EXAMPLE, not a narrated decision. Without this guard that
# boilerplate false-triggers the phrase heuristic above on every one of
# those 6 reps, since it literally contains the LEASE-HONORED/
# LEASE-INVALIDATED tokens. A literal "<" immediately after "command="
# is the reliable, conservative signal that a line is quoting the SPEC --
# a real command_norm value is never a literal angle-bracket placeholder.
_PROSE_TEMPLATE_RE = re.compile(r"LEASE-(?:RECEIPT|HONORED|INVALIDATED):\s*command=<", re.I)


def _mask_strict_lines(text):
    """Blanks every strict-grammar LEASE- line (replaced with spaces of
    the same length, preserving offsets) before prose scanning -- a
    genuine strict-grammar line also contains the literal substrings the
    prose heuristic looks for ("lease", "HONORED"), so without this it
    would be counted twice: once strict, once prose."""
    return _LEASE_LINE_RE.sub(lambda m: " " * len(m.group(0)), text)


def _lease_events_prose(rollout_paths):
    """Distinct-line-deduplicated counts of prose honor/invalidate
    exchanges -- see the module-level comment above for the corpus and
    the precision/recall tradeoff. Dedup mirrors _lease_events(): the
    exact matched line's own stripped text is the dedup key, global
    across ROLLOUT_PATHS, so the same reviewer sentence relayed into a
    second text source (e.g. a parent's inter-agent relay of the same
    message) is not double-counted."""
    honored, invalidated = set(), set()
    for path in rollout_paths:
        for text in _text_sources(path):
            if not text:
                continue
            masked = _mask_strict_lines(text)
            for line in masked.split("\n"):
                line = line.strip()
                if not line or not _PROSE_TERM_RE.search(line):
                    continue
                if _PROSE_TEMPLATE_RE.search(line):
                    continue
                if _PROSE_HONOR_PHRASE_RE.search(line):
                    honored.add(line)
                if _PROSE_INVALIDATE_PHRASE_RE.search(line):
                    invalidated.add(line)
    return {"receipts_honored_prose": len(honored),
            "invalidation_reruns_prose": len(invalidated)}


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
        "lease_events": {**_lease_events(rollout_paths), **_lease_events_prose(rollout_paths)},
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
    print(f"lease_events (prose, alongside the strict grammar -- never folded in): "
          f"receipts_honored_prose={events['receipts_honored_prose']} "
          f"invalidation_reruns_prose={events['invalidation_reruns_prose']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
