#!/usr/bin/env python3
"""Tier 2 cross-model / cross-harness runner for the CLAUDE.md-lift campaign.

Extends the tier-1 screening harness (run_screening.py, which it imports and
reuses) along three axes the tier-2 pre-registration needs
(logs/2026-08-03-claudemd-lift.md):

  - MODEL: `--model X` passes through to `claude --model X` / `codex exec -m X`.
    The model the session actually reported is recorded per rep (guard:
    per-rep model recorded).
  - SUPERPOWERS-LOADED (claude only): `--superpowers` loads the plugin via
    `--plugin-dir $SUPERPOWERS_ROOT` exactly like harnesses/triggering-harness.py,
    still in an isolated throwaway $HOME; bootstrap injection is verified per
    rep and recorded (`bootstrap_injected`).
  - HARNESS: `--harness codex` drives `codex exec --json` headless on the same
    probe fixtures. The ambient-instruction channel differs per harness
    (verified finding: claude reads CLAUDE.md, codex reads AGENTS.md), so the
    cell's directive text is written to that harness's actual ambient file.
    Codex raw JSONL is kept verbatim (<row>.codex.jsonl) and also converted to
    a claude-style stream-json transcript so each probe's unmodified grade.py
    (via transcript_utils) can grade it.

Cells (repeatable --cell):
  empty            no ambient file at all
  unit:<ID>        that unit's verbatim text as the ambient file
  unit:<A>+<B>     multiple units concatenated in order (composition arms,
                   e.g. unit:U-verification-floor+U-broken-windows)
  canary           a synthetic channel-check directive ("begin your reply with
                   MARIGOLD") -- NOT a corpus unit; used to verify a harness's
                   ambient channel actually reaches the model before real
                   cells are spent on it. canary_ok is recorded per rep.

PRIVACY: unchanged from tier 1 -- unit verbatim text is read from the external
corpus (units.py) only when composing a throwaway workdir's ambient file under
/tmp; never logged, never committed, never in results rows (IDs only). The
canary text is synthetic and lives here, not in the corpus.

Isolation: every rep gets a fresh throwaway $HOME (and for codex a fresh
throwaway $CODEX_HOME seeded with ONLY auth.json copied from the real one --
no config.toml, no global AGENTS.md) plus a fresh /tmp workdir with no
ambient-file ancestry.

Codex auth: uses the host's existing `codex login` (~/.codex/auth.json),
copied into the throwaway CODEX_HOME. Claude auth: same as run_screening.py.

Usage:
    # dry run -- compose cells, zero model invocations
    python3 run_tier2.py --harness codex --probe adjacent-breakage \
        --cell canary --dry-run

    # one smoke rep, sonnet, superpowers loaded
    python3 run_tier2.py --model claude-sonnet-5 --superpowers \
        --probe overbuild-bait --cell unit:U-simple-first --reps 1

    # verification-floor arms on codex
    python3 run_tier2.py --harness codex --probe adjacent-breakage \
        --cell empty --cell unit:U-verification-floor \
        --cell unit:U-verification-floor+U-broken-windows --reps 8
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import run_screening as rs
import transcript_utils as tu
import units

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT_DIR = os.path.join(HERE, "out", "tier2")
DEFAULT_DRY_RUN_DIR = os.path.join(tempfile.gettempdir(), "claudemd-lift-tier2-dryrun")
REPO_PARENT = os.path.dirname(os.path.dirname(HERE))  # .../git/superpowers
DEFAULT_SUPERPOWERS_ROOT = os.path.join(REPO_PARENT, "superpowers")
CODEX_BIN = shutil.which("codex") or "codex"

HARNESSES = ("claude", "codex")
AMBIENT_FILE = {"claude": "CLAUDE.md", "codex": "AGENTS.md"}

# Channel canary: synthetic, committable (NOT corpus text). If a harness's
# ambient file actually reaches the model, the reply starts with MARIGOLD.
CANARY_TEXT = (
    "IMPORTANT: Begin your very first reply to the user with the single word "
    "MARIGOLD (all caps), then answer normally.\n"
)


# ---------------------------------------------------------------------------
# Cells
# ---------------------------------------------------------------------------
def compose_ambient(cell):
    """Verbatim ambient-file text for a cell, or None for `empty`.

    unit:<A>+<B> concatenates the units' verbatim texts in order (blank line
    between), for composition arms. Unit text is read fresh from the external
    corpus, never cached here.
    """
    if cell == "empty":
        return None
    if cell == "canary":
        return CANARY_TEXT
    if cell.startswith("unit:"):
        ids = cell[len("unit:"):].split("+")
        return "\n".join(units.read_unit_text(u).rstrip("\n") + "\n" for u in ids)
    raise ValueError(f"unknown cell {cell!r} (expected empty, canary, or unit:<ID>[+<ID>...])")


def cells_for_run(probe_id, explicit_cells):
    """Explicit --cell list verbatim, else the tier-1 screening default."""
    if explicit_cells:
        return list(explicit_cells)
    return rs.cells_for_probe(probe_id)


def build_workdir(probe_id, cell, harness):
    """Fresh /tmp workdir: fixture + the cell's text in THIS harness's ambient
    file (CLAUDE.md for claude, AGENTS.md for codex), git baseline committed."""
    wd = tempfile.mkdtemp(prefix="cml-t2-wd.")
    fixture = os.path.join(rs.probe_dir(probe_id), "fixture")
    if os.path.isdir(fixture):
        rs._copy_tree_files_only(fixture, wd)

    text = compose_ambient(cell)
    if text is not None:
        with open(os.path.join(wd, AMBIENT_FILE[harness]), "w") as f:
            f.write(text)

    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=wd, check=True)
    subprocess.run(["git", *rs.GIT_IDENT, "add", "-A"], cwd=wd, check=True)
    subprocess.run(["git", *rs.GIT_IDENT, "commit", "-q", "-m", "fixture baseline"], cwd=wd, check=True)
    return wd


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def build_claude_cmd(prompt, model, superpowers_root, max_turns):
    cmd = [rs.CLAUDE_BIN, "-p", prompt,
           "--output-format", "stream-json", "--verbose",
           "--dangerously-skip-permissions",
           "--max-turns", str(max_turns)]
    if model:
        cmd += ["--model", model]
    if superpowers_root:
        cmd += ["--plugin-dir", superpowers_root]
    return cmd


def build_codex_cmd(prompt, model):
    # --dangerously-bypass-approvals-and-sandbox is the codex analogue of
    # claude's --dangerously-skip-permissions; safe here because every rep runs
    # in a throwaway /tmp workdir + throwaway HOME/CODEX_HOME.
    cmd = [CODEX_BIN, "exec", "--json",
           "--dangerously-bypass-approvals-and-sandbox",
           "--skip-git-repo-check"]
    if model:
        cmd += ["-m", model]
    cmd += [prompt]
    return cmd


# ---------------------------------------------------------------------------
# Codex JSONL -> claude-style events (so probe graders work unchanged)
# ---------------------------------------------------------------------------
def _assistant_text_event(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def _tool_use_event(name, args):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": args}]}}


def _tool_result_event(text):
    return {"type": "user", "message": {"content": [{"type": "tool_result",
                                                     "content": [{"type": "text", "text": text}]}]}}


def _join_cmd(cmd):
    if isinstance(cmd, list):
        return " ".join(str(c) for c in cmd)
    return str(cmd)


def codex_jsonl_to_claude_events(raw_text):
    """Best-effort conversion of `codex exec --json` output to claude-style
    stream-json events (assistant text, Bash tool_use, tool_result, final
    result with accumulated usage), tolerating both the item.completed schema
    (current CLIs) and the older {"msg": {...}} envelope. Unknown lines are
    counted, never fatal.
    """
    events = []
    usage = {}
    last_text = ""
    model = None
    unknown = 0
    pending_exec = {}  # call_id -> command (legacy begin/end pairing)

    def add_usage(u):
        for k, v in (u or {}).items():
            if isinstance(v, (int, float)):
                usage[k] = usage.get(k, 0) + v

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            unknown += 1
            continue
        if not isinstance(ev, dict):
            unknown += 1
            continue

        # --- current schema: {"type": "...", ...} ---
        typ = ev.get("type")
        if isinstance(typ, str):
            if typ == "item.completed":
                item = ev.get("item") or {}
                it = item.get("type")
                if it == "agent_message":
                    text = item.get("text") or ""
                    if text:
                        events.append(_assistant_text_event(text))
                        last_text = text
                elif it == "command_execution":
                    cmdstr = _join_cmd(item.get("command", ""))
                    events.append(_tool_use_event("Bash", {"command": cmdstr}))
                    out = item.get("aggregated_output") or ""
                    events.append(_tool_result_event(out))
                elif it in ("file_change", "patch_apply"):
                    events.append(_tool_use_event("FileChange", {"changes": item.get("changes", [])}))
                elif it == "reasoning":
                    pass  # thinking text: excluded, as with claude transcripts
                elif it is not None:
                    events.append(_tool_use_event(str(it), {k: v for k, v in item.items() if k != "type"}))
                continue
            if typ == "turn.completed":
                add_usage(ev.get("usage"))
                continue
            if typ == "thread.started":
                model = ev.get("model") or model
                continue
            if typ in ("turn.started", "item.started", "item.updated", "session.created"):
                continue
            if typ == "error":
                events.append(_assistant_text_event(f"[codex error] {ev.get('message', '')}"))
                continue

        # --- legacy schema: {"id": ..., "msg": {"type": ...}} ---
        msg = ev.get("msg")
        if isinstance(msg, dict):
            mt = msg.get("type")
            if mt == "agent_message":
                text = msg.get("message") or msg.get("text") or ""
                if text:
                    events.append(_assistant_text_event(text))
                    last_text = text
            elif mt == "exec_command_begin":
                pending_exec[msg.get("call_id")] = _join_cmd(msg.get("command", ""))
            elif mt == "exec_command_end":
                cmdstr = pending_exec.pop(msg.get("call_id"), "")
                if cmdstr:
                    events.append(_tool_use_event("Bash", {"command": cmdstr}))
                out = (msg.get("stdout") or "") + (("\n" + msg["stderr"]) if msg.get("stderr") else "")
                events.append(_tool_result_event(out))
            elif mt == "task_complete":
                last_text = msg.get("last_agent_message") or last_text
            elif mt == "token_count":
                add_usage({k: v for k, v in msg.items() if k != "type"})
            elif mt == "session_configured":
                model = msg.get("model") or model
            continue

        unknown += 1

    result = {"type": "result", "result": last_text, "usage": usage,
              "converted_from": "codex", "unknown_lines": unknown}
    if model:
        result["model"] = model
    events.append(result)
    return events


# ---------------------------------------------------------------------------
# Per-rep helpers
# ---------------------------------------------------------------------------
def canary_passed(events):
    """True iff MARIGOLD appears in ASSISTANT text (not tool results -- reading
    the ambient file back with `cat` must not count as channel compliance)."""
    return "MARIGOLD" in tu.assistant_text(events)


def claude_reported_model(events):
    for ev in events:
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            return ev.get("model")
    return None


def bootstrap_injected(home):
    """Did the superpowers SessionStart hook inject the bootstrap? (Same check
    as harnesses/triggering-harness.py; requires session persistence.)"""
    for jf in glob.glob(os.path.join(home, ".claude", "projects", "**", "*.jsonl"), recursive=True):
        try:
            with open(jf) as f:
                if "You have superpowers" in f.read():
                    return True
        except OSError:
            pass
    return False


def seed_codex_home(codex_home, real_codex_home=None):
    """Throwaway CODEX_HOME: ONLY auth.json copied from the real one. No
    config.toml (harness defaults), no global AGENTS.md (Jesse's real
    ~/.codex/AGENTS.md is a personal ambient file that must not leak in)."""
    real = real_codex_home or os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex")
    auth = os.path.join(real, "auth.json")
    if not os.path.exists(auth):
        raise RuntimeError(f"no codex auth at {auth}; run `codex login` first")
    os.makedirs(codex_home, exist_ok=True)
    shutil.copy(auth, os.path.join(codex_home, "auth.json"))


def codex_model_from_rollout(codex_home):
    """Best-effort: the rollout session file records the resolved model."""
    for path in sorted(glob.glob(os.path.join(codex_home, "sessions", "**", "*.jsonl"),
                                 recursive=True)):
        try:
            with open(path) as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    payload = rec.get("payload") or {}
                    for key in ("model",):
                        m = payload.get(key) or (payload.get("turn_context") or {}).get(key)
                        if m:
                            return m
        except OSError:
            continue
    return None


# ---------------------------------------------------------------------------
# Run one rep
# ---------------------------------------------------------------------------
def run_one(harness, probe_id, cell, rep, out_dir, model, superpowers_root,
            max_turns, timeout):
    safe_cell = cell.replace(":", "_").replace("+", "-")
    tag = model or "default"
    row_id = f"{harness}__{tag}__{probe_id}__{safe_cell}__rep{rep}"
    transcripts_dir = os.path.join(out_dir, "transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)
    transcript_path = os.path.join(transcripts_dir, f"{row_id}.jsonl")

    wd = build_workdir(probe_id, cell, harness)
    home = tempfile.mkdtemp(prefix="cml-t2-home.")
    prompt = rs.read_prompt(probe_id)

    env = dict(os.environ)
    for k in ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_ENTRYPOINT",
              "ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "OPENAI_API_KEY"):
        env.pop(k, None)
    env["HOME"] = home
    env["DISABLE_AUTOUPDATER"] = "1"

    secret = None
    if harness == "claude":
        env_name, secret = rs.read_auth()
        if not secret:
            raise RuntimeError("No claude auth: set CLAUDE_CODE_OAUTH_TOKEN, populate "
                               "~/.config/superpowers/eval-oauth-token, or set ANTHROPIC_API_KEY.")
        rs.seed_home(home)
        env[env_name] = secret
        if superpowers_root:
            env["CLAUDE_CODE_FORCE_SESSION_PERSISTENCE"] = "1"
        cmd = build_claude_cmd(prompt, model, superpowers_root, max_turns)
        codex_home = None
    else:
        codex_home = tempfile.mkdtemp(prefix="cml-t2-codexhome.")
        seed_codex_home(codex_home)
        env["CODEX_HOME"] = codex_home
        cmd = build_codex_cmd(prompt, model)

    rec = {"harness": harness, "probe": probe_id, "cell": cell, "rep": rep,
           "model_requested": model, "superpowers": bool(superpowers_root),
           "workdir": wd, "home": home, "transcript_path": transcript_path,
           "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}

    t0 = time.monotonic()
    stdout = ""
    try:
        proc = subprocess.run(cmd, cwd=wd, env=env, capture_output=True, text=True,
                              timeout=timeout)
        stdout = rs._redact(proc.stdout, secret)
        stderr = rs._redact(proc.stderr, secret)
        rec["stderr_tail"] = stderr[-400:] if stderr else ""
        rec["launch_error"] = None
    except subprocess.TimeoutExpired:
        rec["launch_error"] = "timeout"
    except OSError as e:
        rec["launch_error"] = rs._redact(f"launch failed: {e}", secret)
    rec["duration_s"] = round(time.monotonic() - t0, 1)

    if harness == "codex":
        raw_path = os.path.join(transcripts_dir, f"{row_id}.codex.jsonl")
        with open(raw_path, "w") as f:
            f.write(stdout)
        rec["raw_transcript_path"] = raw_path
        events = codex_jsonl_to_claude_events(stdout)
        with open(transcript_path, "w") as f:
            for ev in events:
                f.write(json.dumps(ev) + "\n")
        result_ev = events[-1]
        rec["usage"] = result_ev.get("usage", {})
        rec["unknown_transcript_lines"] = result_ev.get("unknown_lines", 0)
        rec["model_reported"] = result_ev.get("model") or codex_model_from_rollout(codex_home)
        rec["cost_usd"] = None  # codex CLI reports tokens, not dollars
    else:
        with open(transcript_path, "w") as f:
            f.write(stdout)
        events = tu.load_events(transcript_path)
        rec["model_reported"] = claude_reported_model(events)
        final = {}
        for ev in events:
            if ev.get("type") == "result":
                final = ev
        rec["usage"] = final.get("usage", {})
        rec["cost_usd"] = final.get("total_cost_usd")
        rec["num_turns"] = final.get("num_turns")
        if superpowers_root:
            rec["bootstrap_injected"] = bootstrap_injected(home)

    if cell == "canary":
        rec["canary_ok"] = canary_passed(events)

    grade = rs.run_grader(probe_id, transcript_path, wd)
    rec.update({k: v for k, v in grade.items() if k != "probe"})
    return rec


def append_result(out_dir, rec):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------------
# Dry run + main
# ---------------------------------------------------------------------------
def dry_run(harness, probes, cells_arg, reps, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    manifest = []
    for probe_id in probes:
        for cell in cells_for_run(probe_id, cells_arg):
            cell_dir = os.path.join(out_dir, probe_id, cell.replace(":", "_").replace("+", "-"))
            os.makedirs(cell_dir, exist_ok=True)
            with open(os.path.join(cell_dir, "prompt.txt"), "w") as f:
                f.write(rs.read_prompt(probe_id))
            text = compose_ambient(cell)
            ambient_path = os.path.join(cell_dir, AMBIENT_FILE[harness])
            if text is None:
                if os.path.exists(ambient_path):
                    os.remove(ambient_path)
                ambient_path = None
            else:
                with open(ambient_path, "w") as f:
                    f.write(text)
            manifest.append({"harness": harness, "probe": probe_id, "cell": cell,
                             "reps": reps, "ambient_path": ambient_path})
    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[dry-run] composed {len(manifest)} cells under {out_dir}")
    for m in manifest:
        print(f"  {m['harness']:6s} {m['probe']:22s} {m['cell']:44s} reps={m['reps']}  "
              f"ambient={'yes' if m['ambient_path'] else 'no (empty arm)'}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harness", choices=HARNESSES, default="claude")
    ap.add_argument("--model", default=None,
                    help="model passthrough (claude --model / codex -m); default: CLI default")
    ap.add_argument("--superpowers", action="store_true",
                    help="claude only: load the superpowers plugin via --plugin-dir")
    ap.add_argument("--superpowers-root", default=os.environ.get("SUPERPOWERS_ROOT",
                                                                 DEFAULT_SUPERPOWERS_ROOT))
    ap.add_argument("--probe", action="append", dest="probes",
                    help="probe id (repeatable); default: all probes")
    ap.add_argument("--cell", action="append", dest="cells", default=[],
                    help="cell (repeatable): empty | canary | unit:<ID>[+<ID>...]; "
                         "default: the probe's tier-1 screening cells")
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--max-turns", type=int, default=15, help="claude only")
    ap.add_argument("--timeout", type=int, default=420)
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--dry-run-out", default=DEFAULT_DRY_RUN_DIR)
    args = ap.parse_args(argv)

    if args.superpowers and args.harness != "claude":
        sys.stderr.write("--superpowers is claude-only (codex has no --plugin-dir equivalent; "
                         "a codex-superpowers cell would need its own integration and evidence "
                         "that the bootstrap loads).\n")
        return 2

    probes = args.probes or rs.all_probes()
    for p in probes:
        if p not in rs.PROBE_UNIT:
            sys.stderr.write(f"unknown probe {p!r}; known: {', '.join(rs.all_probes())}\n")
            return 2
    for probe_id in probes:
        for cell in cells_for_run(probe_id, args.cells):
            compose_ambient(cell)  # validate cells (and unit IDs resolve) up front

    if args.dry_run:
        return dry_run(args.harness, probes, args.cells, args.reps, args.dry_run_out)

    superpowers_root = args.superpowers_root if args.superpowers else None
    if superpowers_root and not os.path.exists(
            os.path.join(superpowers_root, "skills", "using-superpowers", "SKILL.md")):
        sys.stderr.write(f"no superpowers bootstrap under {superpowers_root}\n")
        return 2

    results = []
    for probe_id in probes:
        for cell in cells_for_run(probe_id, args.cells):
            for rep in range(args.reps):
                rec = run_one(args.harness, probe_id, cell, rep, args.out_dir,
                              args.model, superpowers_root, args.max_turns, args.timeout)
                append_result(args.out_dir, rec)
                results.append(rec)
                flag = {True: "PASS", False: "fail", None: "ambiguous"}[rec.get("pass_signal")]
                extra = f" [{rec['launch_error']}]" if rec.get("launch_error") else ""
                canary = (f" canary={'OK' if rec.get('canary_ok') else 'FAILED'}"
                          if "canary_ok" in rec else "")
                print(f"  {args.harness:6s} {rec.get('model_reported') or 'default':28s} "
                      f"{probe_id:20s} {cell:40s} rep{rep}: {flag}{canary}{extra}", flush=True)

    print("\n=== SUMMARY (pass rate among resolved reps) ===")
    grid = {}
    for rec in results:
        grid.setdefault((rec["probe"], rec["cell"]), []).append(rec.get("pass_signal"))
    for (p, c), vals in sorted(grid.items()):
        resolved = [v for v in vals if v is not None]
        n_pass = sum(1 for v in resolved if v)
        print(f"  {p:22s} {c:40s}: {n_pass}/{len(resolved)} resolved "
              f"({len(vals) - len(resolved)} ambiguous/error)")
    print(f"\nresults: {os.path.join(args.out_dir, 'results.jsonl')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
