#!/usr/bin/env python3
"""Task 10 signal extraction -- NOT a corpus-validated campaign scorer (same
disclosed scope decision as Task 9's task9_extract_signals.py). One-shot
triage helper, applied uniformly across every X2/X8 rep, whose output is a
starting point: every claim it makes gets read against the raw transcript
(task9_dump_narrative.py, reused unchanged) before it lands in a verdict.

Built specifically to support the Task 9 C1 lesson operationalized for this
task: extract the Gauntlet-Agent's ACTUALLY DELIVERED reply text for every
turn (not just whether a question was asked) so scripted-vs-ad-lib can be
checked before any compliance claim is graded.

For each rep directory: locates the root rollout (earliest-first-timestamp
session file, same convention as task9_extract_signals.py), then extracts:
  - cost (verdict.json economics.total_est_cost_usd), final status
  - every root-thread turn pair: the Coding-Agent's narration immediately
    BEFORE a user-role message, and the user-role message's own delivered
    text (the Gauntlet's actual reply -- this is the scripted-vs-ad-lib
    evidence) -- in order, so the opening scripted message is turn 0
  - BLOCKED / NEEDS_CONTEXT occurrences anywhere in the rep's rollouts
  - Approval: / Ruling: ledger lines (X8's grammar)
  - X2 seed-signature hits (advisory filenames/identifiers/signature, the
    genuine-conflict regex) anywhere in the rep's rollouts, each with a
    short surrounding snippet for context
  - X8 seed-signature hits (archive/soft-delete/hard-delete/convention
    vocabulary) with snippet
  - which SDD tasks got a subagent dispatch (Task N proxy)
"""
import json, sys, os, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scorer_common import find_files as _find_files

BLOCKED_RE = re.compile(r"\bBLOCKED\b|\bNEEDS_CONTEXT\b")

X2_ADVISORY_RE = re.compile(
    r"discountLookup\.js|getDiscountAmount|applyDiscount|formatPrice",
    re.I)
X2_GENUINE_CONFLICT_RE = re.compile(
    r"floating.?point|integer.?cents|Global Constraints?.*conflict|"
    r"contradict|Math\.round.*cents|cents.*float", re.I)

X8_DESIGN_FORK_RE = re.compile(
    r"archive|soft.?delete|hard.?delete|established convention", re.I)
X8_APPROVAL_LEDGER_RE = re.compile(r"^.*(Approval|Ruling):.*$", re.M)


def load_jsonl(path):
    out = []
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def root_rollout(rep_dir):
    # NOTE (queue-execution campaign, Task 3, item 14): plain glob() skips
    # dot-directories under '**' -- same bug class as find_ledger() below,
    # fixed the same way (find_files uses os.walk).
    files = _find_files(rep_dir, "rollout-*.jsonl",
                         path_contains=os.path.join("home", ".codex", "sessions"))
    if not files:
        return None, []
    def first_ts(f):
        recs = load_jsonl(f)
        return recs[0].get("timestamp", "") if recs else "9999"
    files.sort(key=first_ts)
    return files[0], files


def message_text(payload):
    texts = [c.get("text", "") for c in payload.get("content", []) if isinstance(c, dict)]
    return " ".join(texts)


def analyze_root_thread(path):
    recs = load_jsonl(path)
    turns = []
    last_narration = None
    for r in recs:
        p = r.get("payload", {})
        t = r.get("type")
        if t == "event_msg" and p.get("type") == "agent_message":
            last_narration = p.get("message")
        elif t == "response_item" and p.get("type") == "message" and p.get("role") == "assistant":
            txt = message_text(p)
            if txt:
                last_narration = txt
        elif t == "response_item" and p.get("type") == "message" and p.get("role") == "user":
            txt = message_text(p)
            # Skip the harness's own <environment_context> preamble noise.
            if txt.strip().startswith("<environment_context>"):
                continue
            turns.append({
                "ts": r.get("timestamp"),
                "preceding_narration": last_narration,
                "delivered_text": txt,
            })
    return {"turns": turns, "n_records": len(recs)}


def grep_hits(all_text, pattern, context=120):
    hits = []
    for m in pattern.finditer(all_text):
        start = max(0, m.start() - context)
        end = min(len(all_text), m.end() + context)
        hits.append(all_text[start:end].replace("\\n", " "))
    return hits


def find_ledger(rep_dir):
    hits = []
    for dirpath, _dirnames, filenames in os.walk(rep_dir):
        if "progress.md" in filenames:
            hits.append(os.path.join(dirpath, "progress.md"))
    sdd_hits = [h for h in hits if ".superpowers/sdd" in h]
    return (sdd_hits or hits or [None])[0]


def ledger_signals(ledger_path):
    if not ledger_path or not os.path.exists(ledger_path):
        return {"ledger_found": False}
    text = open(ledger_path, errors="replace").read()
    return {
        "ledger_found": True,
        "approval_ruling_lines": re.findall(r"^.*(?:Approval|Ruling):.*$", text, re.M),
        "blocked_lines": re.findall(r"^.*(?:BLOCKED|NEEDS_CONTEXT).*$", text, re.M),
        "ledger_chars": len(text),
    }


def find_verdict(rep_dir):
    # NOTE (queue-execution campaign, Task 3, item 14): same dot-directory
    # glob-skip bug as root_rollout() above -- verdict.json can sit under
    # a hidden path too.
    files = _find_files(rep_dir, "verdict.json")
    return files[0] if files else None


def main():
    roots = sys.argv[1:]
    results = []
    for rep_dir in roots:
        name = os.path.basename(rep_dir.rstrip("/"))
        vpath = find_verdict(rep_dir)
        verdict = json.load(open(vpath)) if vpath else {}
        cost = verdict.get("economics", {}).get("total_est_cost_usd")
        final = verdict.get("final")
        root_path, all_rollouts = root_rollout(rep_dir)
        root_analysis = analyze_root_thread(root_path) if root_path else {"error": "no rollout found"}

        # Full-corpus text (all threads this rep produced) for seed-signature
        # greps -- a finding might surface in a dispatched subagent's own
        # transcript (e.g. a reviewer's finding text), not just the root.
        all_text_parts = []
        for f in all_rollouts:
            try:
                all_text_parts.append(open(f, errors="replace").read())
            except OSError:
                pass
        all_text = "\n".join(all_text_parts)

        ledger_path = find_ledger(rep_dir)
        ledg = ledger_signals(ledger_path)

        results.append({
            "rep": name,
            "cost": cost,
            "final": final,
            "n_rollout_threads": len(all_rollouts),
            "root_rollout": root_path,
            "root_thread_turns": root_analysis.get("turns"),
            "ledger_path": ledger_path,
            **{f"ledger_{k}": v for k, v in ledg.items()},
            "blocked_needs_context_hits": grep_hits(all_text, BLOCKED_RE, context=200),
            "x2_advisory_hits": grep_hits(all_text, X2_ADVISORY_RE),
            "x2_genuine_conflict_hits": grep_hits(all_text, X2_GENUINE_CONFLICT_RE),
            "x8_design_fork_hits": grep_hits(all_text, X8_DESIGN_FORK_RE),
        })
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
