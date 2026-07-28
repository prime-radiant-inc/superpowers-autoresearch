"""Parse Codex rollout JSONL (three-key lines: timestamp/type/payload).
Shapes verified against the 2026-07-28 audit corpus recon."""
import json, dataclasses
from typing import Iterator

MAX_LINE_BYTES = 8 * 1024 * 1024  # match audit scanner

def iter_records(path) -> Iterator[tuple[str, str, dict]]:
    with open(path, "rb") as f:
        for raw in f:
            if len(raw) > MAX_LINE_BYTES:
                continue
            try:
                rec = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(rec, dict):
                continue
            yield rec.get("timestamp", ""), rec.get("type", ""), rec.get("payload", {}) or {}

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
