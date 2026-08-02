#!/usr/bin/env python3
"""Recovers a battery rep's `.superpowers/sdd/<plan>/progress.md` (or any
other apply_patch/shell-write-touched file, via --path-suffix) content
from the rep's raw rollout JSONL, POST HOC (queue-execution campaign,
Task 4, item 23).

WHY. The SDD scratch workspace (`.superpowers/sdd/<plan>/progress.md`
inside the coding-agent's working clone) is deleted by the coding-agent's
own SDD finishing step before quorum captures results -- by design, this
script does NOT change any agent-visible behavior to preserve it (that
would alter the system under test). Instead: every write to progress.md
goes through either codex's `apply_patch` tool or a plain shell `printf
... >> file` redirect (both below), and BOTH are captured in the rep's
raw rollout JSONL, which is never deleted. This module reconstructs a
target file's content by replaying every such event that touched it, in
chronological order, across every rollout file in the rep.

MECHANISM 1 -- apply_patch (verified directly against `evals/results/
cp-x2-advisory-control-rep1`'s root rollout before writing this module;
see task-4-report.md for exact line citations). apply_patch runs through
the `custom_tool_call`/name=="exec" encoding (see rollout_parser.py's
exec_commands() docstring for the two known exec encodings), as a JS
snippet whose ARGUMENT EXPRESSION resolves to real V4A patch text
(`*** Begin Patch` / `*** End Patch` bracketing one or more
`*** Add/Delete/Update File:` directives; an Add File's body is
`+`-prefixed content lines, the WHOLE file; an Update File's body is one
or more `@@`-headed hunks of ` `/`-`/`+`-prefixed lines).

ROUND-1 REVIEW FIX: the argument expression is not always a single plain
`const patch = "...";` double-quoted literal -- independent review (and a
direct re-read of the raw corpus, confirming it) found at least 3 more
real shapes this module originally silently dropped with ZERO warning:
  - a backtick/template-literal `const patch = \\`...\\`;` variable,
    possibly with `${name}` interpolation of an earlier simple
    `const name = "...";` string (cp-x8-approvals-x8a-rep2);
  - an inline literal argument passed straight to `tools.apply_patch(`
    with NO intermediate variable at all, either quote style
    (cp-x8-approvals-x8a-rep1's Delete File calls, and its Add/Update
    File calls via backtick+interpolation with no `patch` variable);
  - a `"literal"+var+"literal"`-style concatenation expression, again
    with no intermediate `patch` variable (cp-x8-approvals-x8a-rep3).
`_resolve_literal_or_var_expr()` now handles all of these. A GENUINELY
dynamic argument (built via a loop and `+=` mutation --
cp-x8-approvals-x8a-rep1's batch-delete call) is still not evaluated (no
JS interpreter here, deliberately -- see SCOPE CUT) but is NEVER silently
dropped: `find_apply_patch_calls()` still returns it (patch_text=None,
raw_input preserved), and `recover_files()` emits a warning WITH REP+FILE
PROVENANCE whenever such a call's raw text mentions the recovery target,
so a future shape-5 can't hide the same way.

MECHANISM 2 -- shell printf redirect (ROUND-1 REVIEW FIX, real corpus
shape found by review: `cp-x8-approvals-control-rep2`'s progress.md is
created and appended to ENTIRELY via plain shell commands --
`if [ ! -f "$ws/progress.md" ]; then printf '...\\n' > "$ws/progress.md";
fi` and `printf '%s\\n' 'line one' 'line two' >> .../progress.md` -- a
mechanism this module's original docstring wrongly assumed away
("every write... went through apply_patch"). `find_shell_redirects()`
scans every exec-shaped call (both `exec_commands()` encodings) for this
specific printf-redirect shape and folds matching create/append events
into the SAME recovered state a target's apply_patch events populate.
Redirect TARGETS are matched and tracked by their OWN literal text (which
may itself contain an unresolved shell variable, e.g. "$ws/progress.md")
-- never resolved or merged with an apply_patch call's absolute-path key
for the "same" logical file, the same non-conflating discipline already
applied to a rep that legitimately touches a target under two distinct
real paths (see recover_files()'s docstring). A printf format other than
a bare content string or the observed `%s\\n`-repeated-per-argument shape
is NOT guessed at -- it produces a warning, not fabricated content.

SCOPE CUT (deliberate, still true after the round-1 fix). Neither
mechanism is a general-purpose JS/shell interpreter. Update-hunk context
matching and a removed-line code path are implemented (never just assumed
away) since the V4A dialect allows them, but there is no real-corpus
evidence of a hunk using removed ("-") lines: progress.md is an
append-only ledger. A hunk whose context can't be located in the
currently-recovered content is NOT silently dropped -- its added lines
are appended instead, and a warning is recorded (see apply_sections()).
Any apply_patch argument or printf invocation this module cannot resolve
is NEVER silently skipped when it might be relevant: recover_files()
always checks whether the recovery target's PATH_SUFFIX appears in the
unresolved event's raw text before deciding whether to warn, so an
irrelevant unresolved event (e.g. a dynamic delete of some unrelated
file) doesn't spam noise, but a relevant one is never silent.
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

# ---------------------------------------------------------------------------
# V4A patch section parsing (unchanged by the round-1 fix -- this operates
# on already-resolved, de-escaped patch text; only EXTRACTING that text
# changed).
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# apply_patch call-site extraction (ROUND-1 REWRITE -- see module docstring).
# ---------------------------------------------------------------------------

APPLY_PATCH_CALL_RE = re.compile(r"tools\.apply_patch\s*\(")


def _extract_balanced_arg(text, start):
    """From START (index just after an opening '('), scan forward
    respecting JS string/template-literal boundaries (`"`, `` ` ``, `'`,
    each with backslash-escape awareness) and paren nesting, returning
    (arg_text, end_pos): ARG_TEXT is everything up to (not including) the
    matching close-paren, END_POS is the index just after it. A `)`
    INSIDE a string literal (e.g. a commit message like "(review
    clean)") does not close the call -- only one seen outside any string
    literal, at the call's own paren depth, does. Returns None if the
    matching close-paren is never found (truncated/malformed input)."""
    depth = 1
    i, n = start, len(text)
    in_str = None
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ('"', "`", "'"):
            in_str = c
            i += 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    return None


def _deescape_js_string(raw, quote):
    """RAW (still JS-escaped, the text between QUOTE characters) with JS
    backslash escapes decoded -- reuses rollout_parser.
    deescape_custom_exec's map (\\n \\t \\" \\\\), plus, for a backtick
    QUOTE, an escaped backtick (\\`) decoded to a literal backtick (the
    one JS escape that map doesn't cover, since it was written for
    double-quoted custom_exec strings)."""
    text = rp.deescape_custom_exec(raw, "custom_exec")
    if quote == "`":
        text = text.replace("\\`", "`")
    return text


_VAR_ASSIGN_RE_CACHE = {}


def _var_assign_re(name, quote):
    key = (name, quote)
    cached = _VAR_ASSIGN_RE_CACHE.get(key)
    if cached is not None:
        return cached
    q = re.escape(quote)
    body = rf"(?:[^{q}\\]|\\.)*"
    pattern = re.compile(
        r"(?:const|let|var)\s+" + re.escape(name) + r"\s*=\s*" + q +
        r"(" + body + r")" + q + r"\s*;", re.S)
    _VAR_ASSIGN_RE_CACHE[key] = pattern
    return pattern


def resolve_var(input_text, name):
    """Best-effort: NAME's literal string value if it is assigned EXACTLY
    once in INPUT_TEXT as a plain double-quoted or backtick-quoted
    literal (no further concatenation on the RHS -- not observed for any
    variable other than the top-level `patch` itself in the real corpus)
    and never MUTATED afterward (a `NAME +=` anywhere rules it out -- the
    real corpus's own loop-built 'dynamic patch' shape). Returns (quote,
    raw_still_js_escaped_value), or None if NAME can't be resolved this
    way (mutated, not found, or assigned something other than a bare
    literal)."""
    if re.search(r"\b" + re.escape(name) + r"\s*\+=", input_text):
        return None
    for quote in ('"', "`"):
        m = _var_assign_re(name, quote).search(input_text)
        if m:
            return quote, m.group(1)
    return None


_INTERP_RE = re.compile(r"\$\{(\w+)\}")


def _resolve_interpolations(text, input_text):
    """Replace every ${NAME} in TEXT (a de-escaped backtick-literal body)
    with NAME's resolved string value (resolve_var() against
    INPUT_TEXT). Returns the resolved text, or None if ANY interpolation
    can't be resolved (never substitutes a partial/guessed value)."""
    failed = False

    def repl(m):
        nonlocal failed
        r = resolve_var(input_text, m.group(1))
        if r is None:
            failed = True
            return m.group(0)
        quote, raw = r
        return _deescape_js_string(raw, quote)

    out = _INTERP_RE.sub(repl, text)
    return None if failed else out


def _parse_concat_expr(expr_text):
    """Parse a JS expression of the shape STRING_OR_IDENT ('+'
    STRING_OR_IDENT)+ -- double-quoted string literals and bare
    identifiers only, `+`-joined (this corpus's real 'dynamically
    concatenated' apply_patch argument shape, e.g. `"a"+p+"b"`) into a
    list of ('lit', text) / ('var', name) tokens, in order. Returns None
    if EXPR_TEXT doesn't match this grammar -- including a single bare
    literal or identifier alone (that's not concatenation; callers try
    those shapes first)."""
    tokens = []
    pos, n = 0, len(expr_text)
    expect_operand = True
    while pos < n:
        while pos < n and expr_text[pos] in " \t\n":
            pos += 1
        if pos >= n:
            break
        if expect_operand:
            if expr_text[pos] == '"':
                m = re.match(r'"((?:[^"\\]|\\.)*)"', expr_text[pos:])
                if not m:
                    return None
                tokens.append(("lit", m.group(1)))
                pos += m.end()
            else:
                m = re.match(r"\w+", expr_text[pos:])
                if not m:
                    return None
                tokens.append(("var", m.group(0)))
                pos += m.end()
            expect_operand = False
        else:
            if expr_text[pos] != "+":
                return None
            pos += 1
            expect_operand = True
    if expect_operand or len(tokens) < 2:
        return None
    return tokens


def _resolve_concat_tokens(tokens, input_text):
    parts = []
    for kind, val in tokens:
        if kind == "lit":
            parts.append(_deescape_js_string(val, '"'))
            continue
        r = resolve_var(input_text, val)
        if r is None:
            return None
        quote, raw = r
        text = _deescape_js_string(raw, quote)
        if quote == "`":
            resolved = _resolve_interpolations(text, input_text)
            if resolved is None:
                return None
            text = resolved
        parts.append(text)
    return "".join(parts)


def _resolve_literal_or_var_expr(expr_text, input_text):
    """EXPR_TEXT is a raw JS argument expression (the text passed to
    `tools.apply_patch(...)`, or looked up as a variable's own RHS) --
    resolves it to real, de-escaped text, trying in order: a whole
    literal string (double-quoted or backtick; backtick resolves
    ${...} interpolations), a bare identifier (resolved via
    resolve_var(), recursing the same way into its own value), or a
    `+`-joined concatenation expression. Returns the resolved text, or
    None if EXPR_TEXT doesn't match any of these -- a genuinely dynamic/
    opaque expression (e.g. built via a loop) this module does not
    attempt to evaluate."""
    stripped = expr_text.strip()
    if stripped.startswith('"') and stripped.endswith('"'):
        m = re.fullmatch(r'"((?:[^"\\]|\\.)*)"', stripped, re.S)
        if m:
            return _deescape_js_string(m.group(1), '"')
    if stripped.startswith("`") and stripped.endswith("`"):
        m = re.fullmatch(r"`((?:[^`\\]|\\.)*)`", stripped, re.S)
        if m:
            text = _deescape_js_string(m.group(1), "`")
            return _resolve_interpolations(text, input_text)
    if re.fullmatch(r"\w+", stripped):
        r = resolve_var(input_text, stripped)
        if r is None:
            return None
        quote, raw = r
        text = _deescape_js_string(raw, quote)
        return _resolve_interpolations(text, input_text) if quote == "`" else text
    tokens = _parse_concat_expr(stripped)
    if tokens is not None:
        return _resolve_concat_tokens(tokens, input_text)
    return None


@dataclasses.dataclass
class ApplyPatchCall:
    timestamp: str
    patch_text: str | None   # resolved, de-escaped patch text; None if unresolvable
    raw_input: str             # the whole custom_exec input_text (relevance/provenance)
    arg_text: str                # the raw, unresolved argument expression (diagnostic)


def find_apply_patch_calls(rollout_path):
    """Every `tools.apply_patch(...)` call site found in ROLLOUT_PATH's
    custom_tool_call/"exec" records (see rollout_parser.py's
    exec_commands() docstring for this exec encoding), in file order.
    Each call's argument expression is resolved to real, de-escaped patch
    text on a best-effort basis (see _resolve_literal_or_var_expr()),
    covering every shape found in this campaign's real corpus (see module
    docstring). A call whose argument is genuinely dynamic resolves to
    patch_text=None -- it is NEVER dropped from the returned list, only
    marked unresolved, so callers (recover_files()) can decide relevance
    and warn instead of silently losing it."""
    out = []
    for ts, typ, p in rp.iter_records(rollout_path):
        if typ != "response_item" or p.get("type") != "custom_tool_call" \
           or p.get("name") != "exec":
            continue
        input_text = p.get("input") or ""
        for m in APPLY_PATCH_CALL_RE.finditer(input_text):
            extracted = _extract_balanced_arg(input_text, m.end())
            if extracted is None:
                continue
            arg_text, _end = extracted
            patch_text = _resolve_literal_or_var_expr(arg_text, input_text)
            out.append(ApplyPatchCall(timestamp=ts, patch_text=patch_text,
                                       raw_input=input_text, arg_text=arg_text))
    return out


# ---------------------------------------------------------------------------
# Shell printf-redirect extraction (ROUND-1 ADDITION -- see module
# docstring, MECHANISM 2).
# ---------------------------------------------------------------------------

_PRINTF_UNESCAPE_RE = re.compile(r"\\(n|t|\\)")
_PRINTF_UNESCAPE_MAP = {"n": "\n", "t": "\t", "\\": "\\"}


def _printf_unescape(text):
    """printf's OWN backslash-escape processing of its format/argument
    text -- distinct from, and applied AFTER, any JS-level de-escaping
    already done on the surrounding shell command string (\\n \\t \\\\).
    Real corpus shape: `printf '%s\\n' 'line one' 'line two' >> target`
    -- after JS de-escaping the shell command text still contains a
    literal backslash-n (JS's `\\\\n` decodes to a literal `\\n`, two
    characters, deliberately: printf itself is what turns it into a real
    newline at print time, not JS)."""
    return _PRINTF_UNESCAPE_RE.sub(lambda m: _PRINTF_UNESCAPE_MAP[m.group(1)], text)


def _find_printf_redirects(text, path_suffix):
    """Scan TEXT (a shell command string, already JS-de-escaped if it
    came from a custom_exec call) for `printf '<fmt>' ['<arg>' ...]
    (>|>>) <target>` invocations whose TARGET ends with PATH_SUFFIX.
    Yields (mode, target, lines) for each match: MODE is "create" (`>`)
    or "append" (`>>`); TARGET is the raw redirect-target text AS
    WRITTEN (may itself contain an unresolved shell variable, e.g.
    "$ws/progress.md" -- never resolved, tracked as its own distinct
    key, same non-conflating discipline as apply_patch's own
    absolute-path keys); LINES is the ordered list of content lines this
    call writes, or None if the printf shape isn't one this function
    recognizes (a format other than a bare content string or the
    observed `%s\\n`-repeated-per-argument shape) -- a None LINES value
    is a signal to WARN, never a silent skip."""
    for m in re.finditer(r"\bprintf\s+", text):
        pos = m.end()
        if pos >= len(text) or text[pos] != "'":
            continue
        args = []
        ok = True
        while pos < len(text) and text[pos] == "'":
            am = re.match(r"'((?:[^'\\]|\\.)*)'", text[pos:])
            if not am:
                ok = False
                break
            args.append(am.group(1))
            pos += am.end()
            while pos < len(text) and text[pos] in " \t":
                pos += 1
        if not ok or not args:
            continue
        rm = re.match(r"(>>|>)\s*", text[pos:])
        if not rm:
            continue
        mode = "append" if rm.group(1) == ">>" else "create"
        pos += rm.end()
        # The unquoted form must stop at whitespace/`;` (end of shell
        # statement) AND at a backtick (the printf call is commonly
        # embedded inside a JS template literal -- `` `printf ... >>
        # target` `` -- whose closing backtick is not part of any real
        # shell path and must not be swallowed into TARGET).
        tm = re.match(r'"([^"]*)"|([^\s;`]+)', text[pos:])
        if not tm:
            continue
        target = tm.group(1) if tm.group(1) is not None else tm.group(2)
        if not target.endswith(path_suffix):
            continue
        fmt, rest = args[0], args[1:]
        if not rest:
            content = _printf_unescape(fmt)
            lines_out = content.split("\n")
            if lines_out and lines_out[-1] == "":
                lines_out.pop()
        elif fmt == "%s\\n":
            lines_out = [_printf_unescape(a) for a in rest]
        else:
            lines_out = None
        yield mode, target, lines_out


def find_shell_redirects(rollout_path, path_suffix):
    """Every printf-redirect event (see _find_printf_redirects()) found
    across ALL exec-shaped calls in ROLLOUT_PATH -- both known
    rollout_parser.exec_commands() encodings (plain "exec_command"
    function_calls, whose JSON-decoded cmd needs no further de-escaping,
    and custom_exec/"exec" JS-wrapped calls, whose cmd IS JS-de-escaped
    here via rollout_parser.deescape_custom_exec -- the same reuse
    mutation_events() already relies on) -- targeting a path ending in
    PATH_SUFFIX. Returns a list of (timestamp, mode, target, lines,
    raw_cmd) tuples in file order; LINES is None for an unresolved
    printf shape -- never dropped, a caller decides whether to warn."""
    out = []
    for ec in rp.exec_commands(rollout_path):
        cmd = rp.deescape_custom_exec(ec.cmd, ec.encoding)
        for mode, target, lines in _find_printf_redirects(cmd, path_suffix):
            out.append((ec.timestamp, mode, target, lines, cmd))
    return out


# ---------------------------------------------------------------------------
# Top-level recovery.
# ---------------------------------------------------------------------------

def recover_files(rep_dir, path_suffix="progress.md"):
    """Recovers the final reconstructed content of every path under
    REP_DIR ending in PATH_SUFFIX (default: "progress.md" -- a rep in
    this campaign runs exactly one SDD plan, so exactly one COHERENT
    path is expected in practice, though a rep whose ledger mechanism
    changes mid-session, e.g. an isolated worktree set up partway
    through, can legitimately produce more than one distinct tracked
    path -- this returns whatever it actually finds, not an assumption),
    reached via either MECHANISM described in the module docstring
    (apply_patch or a shell printf redirect).

    Every rollout file under REP_DIR (root AND every subagent) is
    scanned, dot-directory-safe via scorer_common.find_files() -- NOT a
    bare glob (rollout paths live under `**/home/.codex/sessions/**`,
    which `glob.glob(pattern, recursive=True)` silently refuses to
    descend into; see scorer_common.py's module docstring and Task 3's
    dot-directory audit) -- and every relevant event across ALL of them
    (apply_patch calls AND shell redirects together) is collected, then
    applied in GLOBAL timestamp order (not per-file, not per-mechanism):
    a subagent's own rollout can chronologically interleave with its
    parent's, and either a per-file or a per-mechanism ordering would
    silently misorder that.

    A "Delete File" of the recovery target itself is expected: it is
    exactly the SDD finishing step's own scratch-workspace cleanup this
    tool exists to see past (real corpus finding, `cp-x2-advisory-x2a-
    rep1`). recover_files() does NOT let that deletion erase already-
    recovered content -- apply_sections() itself still implements
    faithful delete semantics (it is a general patch-replay function; a
    delete of some OTHER, non-target path must still behave like a real
    delete), but recover_files() deliberately never feeds it a delete of
    the PATH_SUFFIX-matching target, logging a note in WARNINGS instead
    so the last-known content survives.

    An apply_patch call or printf redirect this module cannot resolve is
    NEVER silently dropped when it MIGHT be relevant: if PATH_SUFFIX
    appears anywhere in the event's raw text, a warning naming the
    rep/rollout/timestamp provenance is recorded; an irrelevant
    unresolved event (nothing to do with PATH_SUFFIX) is not flagged, to
    avoid noise for e.g. a dynamically-built delete of some unrelated
    file.

    Returns (state, warnings): STATE maps each recovered path (exactly
    as it appears in its own source event -- an apply_patch call's own
    absolute path, or a shell redirect's own literal target text, never
    cross-resolved or merged between the two) to its recovered content
    as a single string (lines joined with "\\n", no trailing newline
    added); WARNINGS is the combined list of degraded-recovery and
    unresolved-event notes (never raises on any of them)."""
    rollout_paths = find_files(rep_dir, "rollout-*.jsonl",
                                path_contains=os.path.join("home", ".codex", "sessions"))

    # (timestamp, source_desc, kind, payload) -- kind in "patch" |
    # "unresolved_patch" | "shell" | "shell_unresolved".
    events = []
    for rollout_path in rollout_paths:
        basename = os.path.basename(rollout_path)
        for call in find_apply_patch_calls(rollout_path):
            source_desc = f"{basename}@{call.timestamp}"
            if call.patch_text is not None:
                events.append((call.timestamp, source_desc, "patch", call.patch_text))
            elif path_suffix in call.raw_input:
                events.append((call.timestamp, source_desc, "unresolved_patch",
                                call.arg_text))
        for ts, mode, target, lines, raw_cmd in find_shell_redirects(rollout_path,
                                                                       path_suffix):
            source_desc = f"{basename}@{ts}"
            if lines is not None:
                events.append((ts, source_desc, "shell", (mode, target, lines)))
            else:
                events.append((ts, source_desc, "shell_unresolved", (target, raw_cmd)))
    events.sort(key=lambda e: e[0])

    state = {}
    warnings = []
    for ts, source_desc, kind, payload in events:
        if kind == "patch":
            sections = []
            for s in parse_patch_sections(payload):
                if not s.path.endswith(path_suffix):
                    continue
                if s.action == "delete":
                    warnings.append(
                        f"{source_desc}: {s.path} was deleted by the session "
                        "(expected SDD finishing-step cleanup) -- recovered "
                        "content is its last state before that deletion")
                    continue
                sections.append(s)
            if sections:
                apply_sections(state, sections, warnings, source_desc=source_desc)
        elif kind == "unresolved_patch":
            warnings.append(
                f"{source_desc}: an apply_patch call mentions {path_suffix!r} "
                "but its argument expression could not be resolved "
                f"(first 120 chars: {payload[:120]!r}) -- possible content "
                "NOT recovered, inspect manually")
        elif kind == "shell":
            mode, target, lines = payload
            if mode == "create":
                if target not in state:
                    state[target] = list(lines)
            else:  # "append"
                state.setdefault(target, []).extend(lines)
        else:  # "shell_unresolved"
            target, _raw_cmd = payload
            warnings.append(
                f"{source_desc}: a shell redirect into {target!r} (matching "
                f"{path_suffix!r}) used a printf format this module doesn't "
                "recognize -- possible content NOT recovered, inspect manually")

    return {path: "\n".join(lines) for path, lines in state.items()}, warnings


def main():
    ap = argparse.ArgumentParser(
        description="Recover an SDD progress.md (or other apply_patch/"
                     "shell-write-touched file) from a battery rep's raw "
                     "rollout JSONL.")
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
        print(f"extract_ledger: no apply_patch/shell-write-touched path "
              f"ending in {args.path_suffix!r} found under {args.rep_dir}",
              file=sys.stderr)
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
