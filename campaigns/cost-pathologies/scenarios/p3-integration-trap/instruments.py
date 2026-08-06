#!/usr/bin/env python3
"""Signal extractor for p3-integration-trap (plan-decomposition
campaign, P3 walking-skeleton battery).

usage: instruments.py <run_dir>     (cwd = the graded session tree)

Prints key=value lines consumed by checks.sh post(). Three signal
families:

1. Transcript signals from $QUORUM_RUN_DIR/trajectory.json (ATIF --
   the cross-harness normalized capture): served model, subagent
   dispatch count, first end-to-end test execution (step ordinal),
   first SampleStreamError sighting (step ordinal -- the seeded
   exception class name only exists in this fixture, so any sighting
   in an observation/narration is the trap or code that handles it).
2. Plan-artifact signals from docs/superpowers/plans/ in the graded
   tree: task count, first-task shape (end-to-end slice vs single
   layer), first task index that composes both subsystems, and
   whether the plan text itself names the stream-contract mismatch.
3. Tree/git signals: commit timeline over subsystem + test files,
   ordinal of the first commit touching an end-to-end test, per-file
   re-touch counts after that commit (rework INGREDIENTS -- the
   pre-registered rework metric is a mechanically-assisted hand-read
   over these lines plus the trajectory, because git alone cannot
   distinguish planned skeleton-widening from unplanned rework), and
   a live composition probe (real Collector -> generate_report) that
   reports whether the trap is resolved in the final tree and which
   conventions won.

Conservative by design: anything not classifiable with confidence is
`unknown` for hand-reading, never guessed. Any internal failure prints
what it has; the caller keeps unknown defaults for the rest.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

COLLECTOR_RE = re.compile(r"collector", re.IGNORECASE)
REPORTER_RE = re.compile(
    r"reporter|generate_report|build_report|load_samples", re.IGNORECASE)
E2E_RE = re.compile(
    r"end.?to.?end|test_end_to_end|\be2e\b|walking.?skeleton|"
    r"thinnest.*slice|vertical.?slice|full pipeline", re.IGNORECASE)
TASK_HEADER_RE = re.compile(r"^#+\s*Task\s+(\d+)", re.MULTILINE)
CONFLICT_WORD_RE = re.compile(
    r"mismatch|incompatib|contradict|conflict|inconsisten|disagree",
    re.IGNORECASE)
TRAP_NEAR_RE = re.compile(
    r"(?:\bts\b|timestamp|\bseq\b|sequence|epoch|strftime|iso.?8601|"
    r"wall.?clock)[^\n]{0,160}"
    r"(?:mismatch|incompatib|contradict|conflict|inconsisten|disagree)|"
    r"(?:mismatch|incompatib|contradict|conflict|inconsisten|disagree)"
    r"[^\n]{0,160}(?:\bts\b|timestamp|\bseq\b|sequence|epoch|strftime|"
    r"iso.?8601|wall.?clock)",
    re.IGNORECASE)


def emit(out, key, value):
    out[key] = str(value).replace("\n", " ").replace("=", ":")[:400]


def load_trajectory(run_dir, out):
    steps = []
    try:
        with open(os.path.join(run_dir, "trajectory.json")) as f:
            steps = json.load(f).get("steps") or []
    except Exception:
        return

    agent_steps = [s for s in steps if isinstance(s, dict)
                   and s.get("source") in ("agent", "assistant")]
    emit(out, "traj_steps", "%d (%d agent)" % (len(steps), len(agent_steps)))

    for s in agent_steps:
        if s.get("model_name"):
            emit(out, "served_model", s["model_name"])
            break
    if out.get("served_model") == "unknown":
        try:
            with open(os.path.join(run_dir,
                                   "coding-agent-token-usage.json")) as f:
                m = (json.load(f) or {}).get("model")
                if m:
                    emit(out, "served_model", m)
        except Exception:
            pass

    dispatches = 0
    first_e2e_step = None
    first_trap_step = None
    trap_steps = 0
    for idx, s in enumerate(steps):
        if not isinstance(s, dict):
            continue
        blobs = []
        for c in s.get("tool_calls") or []:
            if not isinstance(c, dict):
                continue
            name = str(c.get("function_name", ""))
            if name.lower() in ("agent", "task"):
                dispatches += 1
            try:
                args = json.dumps(c.get("arguments", ""), default=str)
            except Exception:
                args = str(c.get("arguments", ""))
            blobs.append(name + " " + args)
        # observation carries tool output; message carries narration.
        for field in ("message", "observation"):
            v = s.get(field)
            if v:
                blobs.append(str(v))
        joined = "\n".join(blobs)
        if first_e2e_step is None and "test_end_to_end" in joined:
            first_e2e_step = idx
        if "SampleStreamError" in joined:
            trap_steps += 1
            if first_trap_step is None:
                first_trap_step = idx
    emit(out, "dispatches", dispatches)
    emit(out, "first_e2e_step",
         first_e2e_step if first_e2e_step is not None else "unknown")
    emit(out, "first_trap_step",
         "%s (%d step(s) mention SampleStreamError)"
         % (first_trap_step, trap_steps)
         if first_trap_step is not None else "none-seen")


def plan_files():
    found = []
    for root, _dirs, files in os.walk("docs/superpowers/plans"):
        for f in files:
            found.append(os.path.join(root, f))
    return sorted(found)


def plan_tasks(files):
    """Return [(task_number, text)] in plan order, or [] if none found."""
    tasks = []
    for path in files:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        matches = list(TASK_HEADER_RE.finditer(text))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            tasks.append((int(m.group(1)), text[m.start():end]))
    tasks.sort(key=lambda t: t[0])
    return tasks


def analyze_plan(out):
    files = plan_files()
    emit(out, "plan_files", len(files))
    if not files:
        return
    full_text = ""
    for path in files:
        try:
            full_text += open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            pass

    tasks = plan_tasks(files)
    emit(out, "plan_task_count", len(tasks) if tasks else "unknown")

    if tasks:
        first_num, first_text = tasks[0]
        has_c = bool(COLLECTOR_RE.search(first_text))
        has_r = bool(REPORTER_RE.search(first_text))
        has_e = bool(E2E_RE.search(first_text))
        if (has_c and has_r) or has_e:
            shape = "slice"
        elif has_c != has_r:
            shape = "layer(%s)" % ("collector" if has_c else "reporter")
        else:
            shape = "unknown"
        emit(out, "first_task_shape",
             "%s (task %d: collector=%s reporter=%s e2e-marker=%s)"
             % (shape, first_num, has_c, has_r, has_e))

        first_e2e_task = "unknown"
        for num, text in tasks:
            if E2E_RE.search(text) or (COLLECTOR_RE.search(text)
                                       and REPORTER_RE.search(text)):
                first_e2e_task = num
                break
        emit(out, "first_e2e_task_index", first_e2e_task)

    if TRAP_NEAR_RE.search(full_text):
        emit(out, "trap_in_plan", "yes (contract-conflict language near ts/seq vocabulary)")
    elif CONFLICT_WORD_RE.search(full_text):
        emit(out, "trap_in_plan", "unknown (conflict language present, not near ts/seq -- hand-read)")
    else:
        emit(out, "trap_in_plan", "no (no contract-conflict language in plan)")


def git_commits():
    """[(short_sha, [files])] oldest first, or []."""
    try:
        raw = subprocess.run(
            ["git", "log", "--reverse", "--pretty=format:__C__%h",
             "--name-only"],
            capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return []
    commits = []
    for chunk in raw.split("__C__"):
        lines = [l.strip() for l in chunk.strip().splitlines() if l.strip()]
        if lines:
            commits.append((lines[0], lines[1:]))
    return commits


def analyze_git(out):
    commits = git_commits()
    emit(out, "total_commits", len(commits) if commits else "unknown")
    if not commits:
        return

    def interesting(f):
        return ((f.startswith("metrics/") or f.startswith("tests/"))
                and f.endswith(".py"))

    e2e_file_re = re.compile(r"tests/.*(e2e|end_to_end)", re.IGNORECASE)
    e2e_ordinal = None
    timeline = []
    for i, (_sha, files) in enumerate(commits, start=1):
        hits = sorted({os.path.basename(f) for f in files if interesting(f)})
        if hits:
            timeline.append("%d:%s" % (i, "+".join(hits)))
        if e2e_ordinal is None and any(e2e_file_re.search(f) for f in files):
            e2e_ordinal = i
    emit(out, "first_e2e_commit_ordinal",
         e2e_ordinal if e2e_ordinal is not None else "unknown")
    emit(out, "commit_timeline", ";".join(timeline)[:380] or "none")

    for label, path in (("collector", "metrics/collector.py"),
                        ("reporter", "metrics/reporter.py")):
        touching = [i for i, (_s, files) in enumerate(commits, start=1)
                    if path in files]
        if not touching:
            emit(out, "%s_commits" % label, "0")
            continue
        if e2e_ordinal is None:
            after = "unknown"
        elif touching[0] > e2e_ordinal:
            # File born after the e2e test existed (skeleton-style
            # widening) -- later touches are new work, not re-touches
            # of a previously-finished layer.
            after = "0(file-born-after-e2e-commit)"
        else:
            after = sum(1 for i in touching if i > e2e_ordinal)
        emit(out, "%s_commits" % label,
             "total=%d first=%d retouches-after-first-e2e-commit=%s"
             % (len(touching), touching[0], after))


PROBE_SRC = r"""
import json, os, sys, tempfile
sys.path.insert(0, os.getcwd())
tmp = tempfile.mkdtemp()
path = os.path.join(tmp, "data", "metrics.jsonl")
try:
    from metrics.collector import Collector
    from metrics.reporter import generate_report
except Exception as e:
    print("probe=import-error:%s: %s" % (type(e).__name__, str(e)[:120]))
    raise SystemExit(0)
try:
    c = Collector(path)
    c.record("cpu", 0.97)
    c.record("mem", 512)
    c.record("cpu", 0.99)
    c.record("mem", 520)
except Exception as e:
    print("probe=record-error:%s: %s" % (type(e).__name__, str(e)[:120]))
    raise SystemExit(0)
tss, seqs = [], []
try:
    with open(path) as f:
        for line in f:
            if line.strip():
                s = json.loads(line)
                tss.append(s.get("ts"))
                seqs.append(s.get("seq"))
except Exception as e:
    print("probe=stream-unreadable:%s" % type(e).__name__)
    raise SystemExit(0)
if tss:
    if all(isinstance(t, int) and not isinstance(t, bool) for t in tss):
        print("ts_convention=epoch-int")
    elif all(isinstance(t, str) for t in tss):
        print("ts_convention=string:%r" % tss[0])
    else:
        print("ts_convention=other:%r" % tss[0])
if seqs[:3] == [1, 1, 2]:
    print("seq_convention=per-metric")
elif seqs[:3] == [1, 2, 3]:
    print("seq_convention=global")
else:
    print("seq_convention=other:%s" % seqs[:4])
try:
    report = generate_report(path)
    names = set()
    for per_name in report.values():
        try:
            names.update(per_name.keys())
        except Exception:
            pass
    print("probe=ok (windows=%d names=%s)" % (len(report), sorted(names)))
except Exception as e:
    print("probe=compose-error:%s: %s" % (type(e).__name__, str(e)[:120]))
"""


def run_probe(out):
    try:
        r = subprocess.run([sys.executable, "-c", PROBE_SRC],
                           capture_output=True, text=True, timeout=60)
        for line in r.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                emit(out, k.strip(), v.strip())
    except Exception:
        pass

    try:
        rep = open("metrics/reporter.py", encoding="utf-8",
                   errors="replace").read()
        raises = len(re.findall(r"raise\s+SampleStreamError", rep))
        emit(out, "validation_raises", raises)
    except Exception:
        pass


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    out = {
        "served_model": "unknown",
        "traj_steps": "unknown",
        "dispatches": "unknown",
        "first_e2e_step": "unknown",
        "first_trap_step": "unknown",
        "plan_files": "unknown",
        "plan_task_count": "unknown",
        "first_task_shape": "unknown",
        "first_e2e_task_index": "unknown",
        "trap_in_plan": "unknown",
        "total_commits": "unknown",
        "first_e2e_commit_ordinal": "unknown",
        "commit_timeline": "unknown",
        "collector_commits": "unknown",
        "reporter_commits": "unknown",
        "ts_convention": "unknown",
        "seq_convention": "unknown",
        "probe": "unknown",
        "validation_raises": "unknown",
    }
    try:
        load_trajectory(run_dir, out)
    except Exception:
        pass
    try:
        analyze_plan(out)
    except Exception:
        pass
    try:
        analyze_git(out)
    except Exception:
        pass
    try:
        run_probe(out)
    except Exception:
        pass
    for k, v in out.items():
        print("%s=%s" % (k, v))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
