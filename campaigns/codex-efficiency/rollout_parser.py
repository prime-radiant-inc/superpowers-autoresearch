"""Parse Codex rollout JSONL (three-key lines: timestamp/type/payload).
Shapes verified against the 2026-07-28 audit corpus recon."""
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
        if ptype == "function_call" and name == "spawn_agent":
            m.spawn_calls += 1
        if name in WAIT_NAMES or WAIT_RE.search(input_text):
            m.wait_calls += 1
        if TEST_RE.search(input_text):
            m.test_commands += 1

    m.lines = stats["lines"]
    m.oversized_lines = stats["oversized_lines"]
    return m
