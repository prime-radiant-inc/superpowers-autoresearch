"""Parse Codex rollout JSONL (three-key lines: timestamp/type/payload).
Shapes verified against the 2026-07-28 audit corpus recon.

wait_outcomes() marker shapes (E7, Amendment 1): a `wait_agent`
`function_call`'s `call_id` is later matched by a `function_call_output`
whose `output` is a JSON string. Two envelope shapes have been observed
across corpora, both carrying the same top-level `timed_out` boolean key:

  - "collaboration" namespace (audit corpus 1,058-wait Remux root
    019f95af-9a8e-7cb3-bc01-edcfe8b343e8; Drew's sol-5_6 and stress-2703
    runs; our own eval-container battery runs):
        timed out:  {"message": "Wait timed out.", "timed_out": true}
        completed:  {"message": "Wait completed.", "timed_out": false}
  - "multi_agent_v1" namespace (Drew's codex-5_5 run -- the same namespace
    that leaves extract_spawns()'s fork_turns/task_name as "(omitted)",
    see drew_adapter.py's module docstring): a different envelope, but the
    same `timed_out` key at the top level, so wait_outcomes() needs no
    namespace-specific handling here (unlike extract_spawns):
        timed out:  {"status": {...}, "timed_out": true}
        completed:  {"status": {...}, "timed_out": false}

Non-outcome shapes observed and deliberately EXCLUDED from wait_outcomes()
(the call never actually waited, so it is not a timed_out=True/False
outcome; see wait_outcomes()'s implementation comment):
  - argument-validation error, bare string:
        "timeout_ms must be at least 10000"
  - malformed-call error, bare string:
        "failed to parse function arguments: unknown field `target`,
         expected `timeout_ms` at line 1 column 9"
  - no matching function_call_output at all (session truncated mid-poll).

wait_outcomes() intentionally scopes to function_call records named
EXACTLY "wait_agent" -- NOT the broader WAIT_NAMES/WAIT_RE set that
parse_session()'s wait_calls counter uses for corpus-parity census
purposes. Two other names live under that broader set: "wait_threads" was
never observed in any inspected rollout (audit corpus, Drew's corpus, or
our own battery runs) so its output shape is unconfirmed; the bare "wait"
tool IS common but is a DIFFERENT tool entirely (waiting on a running
script/build, not on a spawned agent) with an incompatible output shape
that carries no `timed_out` key at all, e.g.:
        "Script completed\nWall time 8.0 seconds\nOutput:\n..."
        "aborted by user after 16.1s"
Mixing either into wait_outcomes() would silently misclassify or crash on
these unrelated shapes, so both are left out; a future extension would need
its own inspected-and-documented marker before widening the name set."""
import json, dataclasses, re
from typing import Iterator

MAX_LINE_BYTES = 8 * 1024 * 1024  # match audit scanner

def _iter_with_lineno(path, stats=None) -> Iterator[tuple[int, str, str, dict]]:
    """Line-by-line record parser. `stats`, if given, is a dict with
    'lines'/'oversized_lines' keys mutated in place so callers who need
    raw-line counts (parse_session) can get them in the same pass that
    iter_records uses for record-level iteration."""
    with open(path, "rb") as f:
        for lineno, raw in enumerate(f):
            if stats is not None:
                stats["lines"] += 1
            if len(raw) > MAX_LINE_BYTES:
                if stats is not None:
                    stats["oversized_lines"] += 1
                continue
            try:
                rec = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(rec, dict):
                continue
            yield lineno, rec.get("timestamp", ""), rec.get("type", ""), rec.get("payload", {}) or {}

def iter_records(path) -> Iterator[tuple[str, str, dict]]:
    for _, ts, typ, p in _iter_with_lineno(path):
        yield ts, typ, p

OMIT = "(omitted)"

@dataclasses.dataclass
class Spawn:
    call_id: str; task_name: str; fork_turns: str
    model: str; reasoning_effort: str; timestamp: str

def _spawn_calls(path):
    for ts, typ, p in iter_records(path):
        if typ == "response_item" and p.get("type") == "function_call" \
           and p.get("name") == "spawn_agent":
            yield ts, p

def extract_spawns(path) -> list[Spawn]:
    out = []
    for ts, p in _spawn_calls(path):
        try:
            args = json.loads(p.get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}
        out.append(Spawn(
            call_id=p.get("call_id", OMIT),
            task_name=str(args.get("task_name", OMIT)),
            fork_turns=str(args.get("fork_turns", OMIT)),
            model=str(args.get("model", OMIT)),
            reasoning_effort=str(args.get("reasoning_effort", OMIT)),
            timestamp=ts))
    return out

def child_links(path) -> dict[str, str]:
    links = {}
    for ts, typ, p in iter_records(path):
        if typ == "event_msg" and p.get("type") == "sub_agent_activity" \
           and p.get("kind") == "started":
            event_id = p.get("event_id")
            if event_id is not None:
                links[event_id] = p.get("agent_thread_id", "")
    return links

@dataclasses.dataclass
class ExecCmd:
    call_id: str
    cmd: str
    timestamp: str
    encoding: str  # "exec_command" | "custom_exec"

def exec_commands(path) -> list[ExecCmd]:
    """Both exec encodings seen in the corpus: a `function_call` named
    exec_command (JSON-string arguments with a "cmd" key), and a
    `custom_tool_call` named exec (freeform JS `input`, taken whole)."""
    out = []
    for ts, typ, p in iter_records(path):
        if typ != "response_item":
            continue
        ptype = p.get("type")
        if ptype == "function_call" and p.get("name") == "exec_command":
            try:
                args = json.loads(p.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            out.append(ExecCmd(
                call_id=p.get("call_id", OMIT),
                cmd=str(args.get("cmd", OMIT)),
                timestamp=ts,
                encoding="exec_command"))
        elif ptype == "custom_tool_call" and p.get("name") == "exec":
            out.append(ExecCmd(
                call_id=p.get("call_id", OMIT),
                cmd=p.get("input", OMIT),
                timestamp=ts,
                encoding="custom_exec"))
    return out

# --- Classifiers ported from the audit scanner (scan-rollouts.mjs), applied
# to any tool-call-shaped response_item (function_call / custom_tool_call /
# tool_search_call / web_search_call / local_shell_call), mirroring the
# scanner's `isToolCall` gate. Regex flags/text kept verbatim from the JS.
TOOL_CALL_TYPES = {
    "function_call", "custom_tool_call", "tool_search_call",
    "web_search_call", "local_shell_call",
}

# JS: /SKILL\.md|skills\.read|activate_skill/i
SKILL_READ_RE = re.compile(r"SKILL\.md|skills\.read|activate_skill", re.I)
# JS: /\/memories\/|episodic-memory/i
MEMORY_READ_RE = re.compile(r"/memories/|episodic-memory", re.I)
# JS: name === "wait" || name === "wait_agent" || name === "wait_threads" ||
#     /\b(?:wait|wait_agent|wait_threads|write_stdin)\s*\(/.test(inputText)
WAIT_NAMES = {"wait", "wait_agent", "wait_threads"}
WAIT_RE = re.compile(r"\b(?:wait|wait_agent|wait_threads|write_stdin)\s*\(")
# JS: name === "spawn_agent" ||
#     /\b(?:spawn_agent|create_thread)\s*\(/.test(inputText)
# Broader than the extract_spawns()/_spawn_calls() predicate (function_call
# named exactly "spawn_agent"): this is the parse_session *counter* only,
# ported to match the audit's isSpawn classifier for corpus parity. The
# structured Spawn-tuple extraction in extract_spawns is intentionally left
# on the narrower predicate.
SPAWN_NAMES = {"spawn_agent"}
SPAWN_RE = re.compile(r"\b(?:spawn_agent|create_thread)\s*\(")
# JS: /\b(?:go test|pytest|npm test|pnpm test|bun test|swift test|
#     xcodebuild test|make test|vitest|cargo test)\b/i
TEST_RE = re.compile(
    r"\b(?:go test|pytest|npm test|pnpm test|bun test|swift test|"
    r"xcodebuild test|make test|vitest|cargo test)\b", re.I)

# skill_reads_strict: not from the audit scanner (which only textually
# scans tool input). Per task-3-brief.md, "strict" additionally requires
# the record be an exec-like input (never apply_patch) and the match be
# read-shaped: (cat|sed|head|less|tail|rg|grep|open|read)[^\n]*SKILL\.md
STRICT_SKILL_READ_RE = re.compile(r"(cat|sed|head|less|tail|rg|grep|open|read)[^\n]*SKILL\.md")
EXEC_LIKE = {("function_call", "exec_command"), ("custom_tool_call", "exec")}

def _tool_input(payload: dict) -> str:
    """Port of the audit scanner's toolInput(): arguments string, else
    input string, else JSON.stringify(action) if action key is present."""
    args = payload.get("arguments")
    if isinstance(args, str):
        return args
    inp = payload.get("input")
    if isinstance(inp, str):
        return inp
    if "action" in payload:
        return json.dumps(payload["action"])
    return ""

@dataclasses.dataclass
class SessionMetrics:
    lines: int = 0
    oversized_lines: int = 0
    compactions: int = 0
    task_started: int = 0
    task_complete: int = 0
    skill_reads_compat: int = 0
    skill_reads_strict: int = 0
    memory_reads: int = 0
    spawn_calls: int = 0
    wait_calls: int = 0
    test_commands: int = 0
    user_messages: int = 0
    patch_applies: int = 0
    first_instruction_line: int | None = None

def parse_session(path) -> SessionMetrics:
    m = SessionMetrics()
    stats = {"lines": 0, "oversized_lines": 0}
    for lineno, ts, typ, p in _iter_with_lineno(path, stats):
        if typ == "event_msg":
            ptype = p.get("type")
            if ptype == "context_compacted":
                # Compaction emits a bare `compacted` record plus this
                # event_msg marker; only the marker is counted (see
                # DESIGN.md recon notes) so a compaction counts once, not
                # twice.
                m.compactions += 1
            elif ptype == "task_started":
                m.task_started += 1
            elif ptype == "task_complete":
                m.task_complete += 1
            elif ptype == "patch_apply_end":
                m.patch_applies += 1
            elif ptype == "user_message":
                m.user_messages += 1
                if m.first_instruction_line is None:
                    m.first_instruction_line = lineno
            continue
        if typ != "response_item":
            continue
        ptype = p.get("type")
        if ptype not in TOOL_CALL_TYPES:
            continue
        name = p.get("name")
        input_text = _tool_input(p)

        if SKILL_READ_RE.search(input_text):
            m.skill_reads_compat += 1
            if (ptype, name) in EXEC_LIKE and STRICT_SKILL_READ_RE.search(input_text):
                m.skill_reads_strict += 1
        if MEMORY_READ_RE.search(input_text):
            m.memory_reads += 1
        if name in SPAWN_NAMES or SPAWN_RE.search(input_text):
            m.spawn_calls += 1
        if name in WAIT_NAMES or WAIT_RE.search(input_text):
            m.wait_calls += 1
        if TEST_RE.search(input_text):
            m.test_commands += 1

    m.lines = stats["lines"]
    m.oversized_lines = stats["oversized_lines"]
    return m

# Exactly "wait_agent" -- see the module docstring for why this is
# deliberately narrower than parse_session's WAIT_NAMES.
WAIT_AGENT_NAME = "wait_agent"

@dataclasses.dataclass
class WaitCall:
    call_id: str
    timestamp: str
    timed_out: bool
    duration_hint: str  # requested arguments["timeout_ms"], or OMIT

def wait_outcomes(path) -> list[WaitCall]:
    """Pair every `wait_agent` function_call to its function_call_output
    (matched by call_id) and classify timed_out from the output's parsed
    `timed_out` boolean key. See the module docstring for the exact marker
    shapes this was built against.

    Calls that never produced a genuine wait outcome are excluded, not
    guessed at: no matching output at all, an output that isn't a JSON
    object, or a JSON object without a boolean `timed_out` key (the
    argument-validation-error shapes in the docstring)."""
    calls = []  # (call_id, timestamp, duration_hint), in file order
    outputs = {}  # call_id -> raw output value
    for ts, typ, p in iter_records(path):
        if typ != "response_item":
            continue
        ptype = p.get("type")
        if ptype == "function_call" and p.get("name") == WAIT_AGENT_NAME:
            try:
                args = json.loads(p.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            calls.append((p.get("call_id", OMIT), ts, str(args.get("timeout_ms", OMIT))))
        elif ptype == "function_call_output":
            call_id = p.get("call_id")
            if call_id is not None:
                outputs[call_id] = p.get("output")

    out = []
    for call_id, ts, duration_hint in calls:
        raw = outputs.get(call_id)
        if not isinstance(raw, str):
            continue  # unresolved: no matching output found
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue  # error shapes are bare strings, not JSON objects
        if not isinstance(parsed, dict) or not isinstance(parsed.get("timed_out"), bool):
            continue  # not a genuine wait outcome
        out.append(WaitCall(call_id=call_id, timestamp=ts,
                             timed_out=parsed["timed_out"], duration_hint=duration_hint))
    return out

# --- lifecycle_calls() (E8, Amendment 1): the other collaboration-namespace
# tools alongside spawn_agent/wait_agent -- close_agent, interrupt_agent,
# followup_task, resume_agent, list_agents. Verified directly against real
# rollouts (audit corpus, Drew's corpus, our own battery runs): all five
# appear as a `function_call` under `response_item`, exactly like
# spawn_agent, and -- exactly like extract_spawns -- the `namespace` field
# is NOT filtered on: close_agent has been observed under BOTH the
# "collaboration" namespace (our battery runs, most of the audit corpus)
# and the "multi_agent_v1" namespace (Drew's codex-5_5 run, and some audit
# sessions) with an identical {"target": "<agent id>"} argument shape in
# both. None of the five tools' arguments carry a "task_name" key in any
# rollout inspected (close_agent/interrupt_agent/followup_task key their
# single argument "target"; resume_agent keys it "id" per its own
# tool_search_call schema; list_agents takes no arguments) -- so
# args_task_name is virtually always "(omitted)" in practice. It's kept
# anyway for structural symmetry with Spawn and in case a future tool
# revision adds one.
LIFECYCLE_NAMES = {"close_agent", "interrupt_agent", "followup_task",
                    "resume_agent", "list_agents"}

@dataclasses.dataclass
class LifecycleCall:
    call_id: str
    name: str
    timestamp: str
    args_task_name: str

def lifecycle_calls(path) -> list[LifecycleCall]:
    """Every close_agent/interrupt_agent/followup_task/resume_agent/
    list_agents function_call in file order. Same envelope handling as
    extract_spawns() -- see the comment above for the shapes this was
    verified against."""
    out = []
    for ts, typ, p in iter_records(path):
        if typ == "response_item" and p.get("type") == "function_call" \
           and p.get("name") in LIFECYCLE_NAMES:
            try:
                args = json.loads(p.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            out.append(LifecycleCall(
                call_id=p.get("call_id", OMIT),
                name=p.get("name"),
                timestamp=ts,
                args_task_name=str(args.get("task_name", OMIT))))
    return out

# --- patch_applies() (E4, Task 11): structured per-event extraction of
# patch_apply_end records -- paths changed plus success/timestamp -- that
# parse_session()'s SessionMetrics.patch_applies (a bare running COUNTER)
# can't provide. Shape verified directly against a real rollout
# (evals/results/cx-eff-cx-sdd-small-dev-rep5/.../rollout-*.jsonl): a
# `patch_apply_end` event_msg carries `success` (bool) and `changes` (a
# dict keyed by absolute file path, each value describing the change --
# add/update/delete -- which this function never reads, only the dict's
# keys). Some payloads (e.g. a synthetic/older-shape record) may omit
# `changes` entirely, or carry an empty dict on a failed apply -- both
# treated as "no paths", not an error.
@dataclasses.dataclass
class PatchApply:
    call_id: str
    timestamp: str
    success: bool
    paths: list[str]  # sorted, the changed dict's keys


def patch_applies(path) -> list[PatchApply]:
    """Every patch_apply_end event, in file order."""
    out = []
    for ts, typ, p in iter_records(path):
        if typ == "event_msg" and p.get("type") == "patch_apply_end":
            changes = p.get("changes")
            paths = sorted(changes.keys()) if isinstance(changes, dict) else []
            out.append(PatchApply(
                call_id=p.get("call_id", OMIT),
                timestamp=ts,
                success=bool(p.get("success", False)),
                paths=paths))
    return out

# --- mutation_events() (E3, Task 10): timestamps of everything that could
# have changed the tree's on-disk/repo state -- a successful patch_apply_end
# (reuses patch_applies(), filtered to success=True; a FAILED apply changed
# nothing) plus any exec command (either encoding, reusing exec_commands())
# matching MUTATION_GIT_RE. This is the duplicate-gate scorer's "did
# anything happen between these two identical test runs" signal: two
# identical normalized test commands with zero mutation_events between their
# timestamps are running against an unchanged tree.
#
# Deliberately narrow to git's own state-changing subcommands (not every
# write imaginable, e.g. `mv`/`rm`/editor saves outside apply_patch) --
# apply_patch already covers the agent's own file edits via patch_apply_end,
# so the git list only needs to cover mutations that happen OUTSIDE
# apply_patch: committing, merging, rebasing, resetting, or switching
# branches all change what's on disk without necessarily going through
# apply_patch.
MUTATION_GIT_RE = re.compile(r"\bgit (commit|merge|rebase|reset|checkout)\b")

# --- deescape_custom_exec() (E3, Task 10, fix round 1): a real bug found
# via reviewer-verified re-inspection of the MINE-tier battery corpus.
# custom_tool_call/"exec"'s `input` is raw JS source, taken WHOLE by
# exec_commands() (see that function's own docstring) -- unlike the
# "exec_command" encoding, whose `arguments` JSON string already goes
# through json.loads() upstream and comes out fully decoded. A literal
# two-character `\n` escape left over from a JS string literal in that
# raw source (e.g. a multi-line shell script embedded as a JS string)
# therefore stays a real backslash followed by a literal "n" character,
# never an actual newline -- so a command shaped like (Python repr)
# "echo start\\ngit commit -m 'wip'" has a literal "n" sitting directly
# before "git", and a literal "n" is a WORD character: it defeats
# MUTATION_GIT_RE's (and score_e3.TEST_INVOCATION_RE's) leading \b, which
# requires an actual word boundary immediately before the match. This
# silently dropped real mutations (and real test-command occurrences)
# from custom_exec-encoded commands wherever this pattern occurred.
#
# THIS IS AN ABSOLUTE-TRUTH FIX, deliberately scoped to ONLY the two
# call sites that need the true, human-readable command text
# (mutation_events() below and score_e3.py's TEST_INVOCATION_RE
# matching) -- it is NEVER applied to parse_session()'s corpus-parity
# counters (skill_reads_compat/strict, spawn_calls, wait_calls,
# test_commands) or their regexes (SKILL_READ_RE, MEMORY_READ_RE,
# WAIT_RE, SPAWN_RE, TEST_RE, STRICT_SKILL_READ_RE), whose contract is
# BYTE-PARITY with the audit's scan-rollouts.mjs scanner (validated by
# validate_corpus.py, Task 4) -- that scanner operates on the same raw,
# un-escaped JS text this function decodes, so de-escaping those paths
# would break an already-validated parity contract, not fix a bug.
_JS_ESCAPE_RE = re.compile(r'\\(n|t|"|\\)')
_JS_ESCAPE_MAP = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


def deescape_custom_exec(cmd: str, encoding: str) -> str:
    """Decodes the common JS string-literal escapes (\\n \\t \\" \\\\ --
    the reviewer's named set, not a full JS-string-literal parse) in CMD
    when ENCODING == "custom_exec". Any other encoding value (in
    practice, "exec_command") returns CMD unchanged -- that text is
    already JSON-decoded upstream by exec_commands(), so re-applying
    this here would double-unescape/corrupt already-correct content
    (e.g. a command that legitimately contains a literal backslash-n
    two-character sequence after JSON decoding)."""
    if encoding != "custom_exec":
        return cmd
    return _JS_ESCAPE_RE.sub(lambda m: _JS_ESCAPE_MAP[m.group(1)], cmd)


def mutation_events(path) -> list[str]:
    """Sorted timestamps of every successful patch apply or git-mutating
    exec command in PATH, merging both sources and sorting by timestamp
    (ISO8601 strings, which sort lexicographically in chronological
    order) -- NOT simply concatenated in file order, since a caller
    merging mutation_events() across multiple sessions needs a single
    chronologically-ordered timeline. Matches MUTATION_GIT_RE against
    the DE-ESCAPED command text (deescape_custom_exec(), fix round 1) --
    see that function's docstring for why this is safe and necessary."""
    events = [pa.timestamp for pa in patch_applies(path) if pa.success]
    events += [ec.timestamp for ec in exec_commands(path)
               if MUTATION_GIT_RE.search(deescape_custom_exec(ec.cmd, ec.encoding))]
    return sorted(events)

# --- skill_reads() / compaction_events() (E6, Task 9): per-EVENT (not
# aggregate-count) extraction, so a caller can partition a session's own
# timeline at a compaction boundary and compare WHICH skill paths were read
# before vs after -- parse_session()'s skill_reads_strict/compactions
# fields are bare running counters and can't answer that question.
# skill_reads() reuses the exact same STRICT_SKILL_READ_RE/EXEC_LIKE gate
# parse_session() uses for skill_reads_strict (kept in sync deliberately:
# these two must always agree on WHICH commands count as a strict read,
# only skill_reads() additionally captures the path). compaction_events()
# reads the same event_msg/context_compacted marker parse_session() counts.

# Captures the whitespace/quote-delimited path token ending in "SKILL.md"
# out of an already STRICT_SKILL_READ_RE-matched command string.
SKILL_PATH_RE = re.compile(r"([^\s'\"]*SKILL\.md)")

@dataclasses.dataclass
class SkillRead:
    timestamp: str
    lineno: int
    skill_path: str
    cmd_encoding: str  # the matched tool name: "exec_command" | "exec"

def skill_reads(path) -> list[SkillRead]:
    """Every STRICT-shaped SKILL.md read, in file order, with the literal
    path argument extracted (never apply_patch input -- EXEC_LIKE excludes
    it, same as parse_session's skill_reads_strict -- and never anything
    beyond the path substring itself)."""
    out = []
    for lineno, ts, typ, p in _iter_with_lineno(path):
        if typ != "response_item":
            continue
        ptype = p.get("type")
        name = p.get("name")
        if (ptype, name) not in EXEC_LIKE:
            continue
        input_text = _tool_input(p)
        if not STRICT_SKILL_READ_RE.search(input_text):
            continue
        m = SKILL_PATH_RE.search(input_text)
        skill_path = m.group(1) if m else input_text.strip()
        out.append(SkillRead(timestamp=ts, lineno=lineno,
                              skill_path=skill_path, cmd_encoding=name))
    return out

@dataclasses.dataclass
class CompactionEvent:
    timestamp: str
    lineno: int

def compaction_events(path) -> list[CompactionEvent]:
    """Every event_msg/context_compacted MARKER, in file order (the same
    signal parse_session()'s compactions counter uses -- a compaction also
    emits a bare `compacted` record; only the marker is counted here too,
    for the same one-compaction-one-count reason)."""
    out = []
    for lineno, ts, typ, p in _iter_with_lineno(path):
        if typ == "event_msg" and p.get("type") == "context_compacted":
            out.append(CompactionEvent(timestamp=ts, lineno=lineno))
    return out

# --- final_answers() / inter_agent_messages() (E10, Task 14): lifecycle-
# truthfulness needs the actual CLAIM text a session made, not just tool-call
# structure. Two distinct record shapes carry it, verified directly against a
# real battery rollout (evals/results/cx-eff-cx-sdd-small-dev-rep1/.../
# rollout-*.jsonl):
#
#   - `event_msg/type=="agent_message"` -- what THIS session told its OWN
#     caller (parent controller, or the human/gauntlet driver for a root):
#     `{"type":"agent_message","message":"<text>","phase":"final_answer"|
#     "commentary","memory_citation":null}`. The session's own final claim is
#     the LAST entry with phase=="final_answer" (a session may narrate
#     several "commentary" messages before its actual conclusion).
#   - `response_item/type=="agent_message"` -- an INTER-agent message (what
#     one thread sent another) as recorded in the observing thread's own
#     transcript: `{"type":"agent_message","author":"/root/x",
#     "recipient":"/root","content":[{"type":"input_text"|"output_text",
#     "text":...}, ...]}`. The concatenated content text follows a fixed
#     protocol envelope: "Message Type: X\nTask name: Y\nSender:
#     Z\nPayload:\n<payload>". Verified pitfall (E10 pre-registration, this
#     task): a `Message Type: MESSAGE` progress ping commonly has an EMPTY
#     payload (harmless protocol artifact, immediately followed by a
#     substantive `Message Type: FINAL_ANSWER` from the same sender) -- a
#     null-result classifier must key off message_type=="FINAL_ANSWER"
#     specifically, never raw text length alone, or it will misfire on every
#     one of these pings. inter_agent_messages() exposes message_type so a
#     caller can make that distinction; it does not make it itself.

INTER_AGENT_ENVELOPE_RE = re.compile(
    r"^Message Type: (?P<message_type>\S+)\nTask name: (?P<task_name>.*)\n"
    r"Sender: (?P<sender>.*)\nPayload:\n(?P<payload>.*)", re.S)

@dataclasses.dataclass
class FinalAnswer:
    timestamp: str
    lineno: int
    phase: str     # "final_answer" | "commentary" | other observed values
    message: str


def final_answers(path) -> list[FinalAnswer]:
    """Every event_msg/agent_message record in THIS session's own
    transcript, in file order -- what this session told its own caller.
    Never picks up an inter-agent (response_item/agent_message) record --
    see module note above for why those are a different shape entirely."""
    out = []
    for lineno, ts, typ, p in _iter_with_lineno(path):
        if typ == "event_msg" and p.get("type") == "agent_message":
            out.append(FinalAnswer(timestamp=ts, lineno=lineno,
                                    phase=p.get("phase", ""),
                                    message=p.get("message", "")))
    return out


@dataclasses.dataclass
class InterAgentMessage:
    timestamp: str
    lineno: int
    author: str
    recipient: str
    message_type: str  # "FINAL_ANSWER" | "MESSAGE" | "NEW_TASK" | ... | "" if unparsed
    task_name: str
    sender: str
    payload: str        # text after "Payload:\n", or raw_text if unparsed
    raw_text: str        # the full concatenated content text, unparsed


def inter_agent_messages(path) -> list[InterAgentMessage]:
    """Every response_item/agent_message record, in file order -- a message
    ONE agent thread sent ANOTHER, as recorded in this rollout's own
    transcript (e.g. the root's rollout records every message a spawned
    child sent it). `content` items are concatenated in order (both
    "input_text" and "output_text" carry a "text" field); the concatenated
    text is then parsed against the "Message Type: X\\nTask name:
    Y\\nSender: Z\\nPayload:\\n<payload>" envelope. A record whose text does
    not match that envelope still comes back with message_type=="" and
    payload==raw_text (never dropped -- see module note above)."""
    out = []
    for lineno, ts, typ, p in _iter_with_lineno(path):
        if typ != "response_item" or p.get("type") != "agent_message":
            continue
        content = p.get("content") or []
        raw_text = "".join(
            c.get("text", "") for c in content if isinstance(c, dict))
        m = INTER_AGENT_ENVELOPE_RE.match(raw_text)
        if m:
            out.append(InterAgentMessage(
                timestamp=ts, lineno=lineno,
                author=p.get("author", ""), recipient=p.get("recipient", ""),
                message_type=m.group("message_type"),
                task_name=m.group("task_name"), sender=m.group("sender"),
                payload=m.group("payload"), raw_text=raw_text))
        else:
            out.append(InterAgentMessage(
                timestamp=ts, lineno=lineno,
                author=p.get("author", ""), recipient=p.get("recipient", ""),
                message_type="", task_name="", sender="",
                payload=raw_text, raw_text=raw_text))
    return out
