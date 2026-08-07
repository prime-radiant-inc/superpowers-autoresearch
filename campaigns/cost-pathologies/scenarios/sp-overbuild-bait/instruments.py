#!/usr/bin/env python3
"""Signal extractor for sp-overbuild-bait (quorum-static port of
campaigns/claudemd-lift/probes/overbuild-bait/grade.py).

usage: instruments.py <run_dir>   (cwd must be the graded workdir)

Prints key=value lines consumed by checks.sh post(): served model and
output tokens from the run dir's capture artifacts
(trajectory.json / coding-agent-token-usage.json -- ATIF is the
cross-harness surface, same for codex, claude, kimi, pi), plus
diff-based signals (added LOC on code files, abstraction hits, files
touched) against the seed commit in the cwd repo.

Diff-based signals exclude interpreter bytecode (__pycache__/, *.pyc)
per the transcript_utils fix rationale: bytecode appears whenever the
session or the grader's own python runs, and corrupts every diff-based
signal (the tempting-refactor false 0/8, claudemd-lift log 2026-08-03).
Superpowers worktrees (.worktrees/) are excluded from the root diff and
reported by checks.sh on their own line. Conservative: any git failure
leaves the diff signals `unknown`; nothing here mutates the tree or the
index (untracked files are counted whole instead of `git add -N`).
"""
import json
import os
import re
import subprocess
import sys

CODE_EXT = (".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".go",
            ".rs", ".rb", ".java", ".c", ".h", ".cc", ".cpp", ".sh")
EXCLUDES = [":(exclude)__pycache__/", ":(exclude)**/__pycache__/",
            ":(exclude)*.pyc", ":(exclude)**/*.pyc",
            ":(exclude).worktrees/"]

# ABSTRACTION_RE ported verbatim from grade.py.
ABSTRACTION_RE = re.compile(
    r"^\s*class\s+\w|"
    r"\b(ABC|abstractmethod|Protocol|Enum)\b|"
    r"\b\w*(Factory|Strategy|Registry|Exporter[A-Z]\w*|Base\w*Exporter)\b",
    re.MULTILINE,
)


def is_bytecode(p):
    parts = p.replace("\\", "/").split("/")
    return "__pycache__" in parts or p.endswith(".pyc")


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    out = {
        "served_model": "unknown",
        "output_tokens": "unknown", "output_tokens_src": "none",
        "added_loc": "unknown", "files_touched": "unknown",
        "abstraction_hits": "unknown", "abstraction_sample": "none",
        "worktrees": "no",
    }

    # --- served model + output tokens (capture artifacts) -----------
    steps, final_metrics = [], {}
    try:
        with open(os.path.join(run_dir, "trajectory.json")) as f:
            traj = json.load(f)
        steps = traj.get("steps") or []
        final_metrics = traj.get("final_metrics") or {}
    except Exception:
        pass
    for s in steps:
        if isinstance(s, dict) and s.get("source") in ("agent", "assistant") and s.get("model_name"):
            out["served_model"] = str(s["model_name"])
            break
    try:
        with open(os.path.join(run_dir, "coding-agent-token-usage.json")) as f:
            usage = json.load(f) or {}
        if out["served_model"] == "unknown" and usage.get("model"):
            out["served_model"] = str(usage["model"])
        # kimi oauth lane: requests carry the placeholder
        # __kimi_env_model__; the response side of the kimi wire log has
        # the real served name. os.walk (hidden dir .kimi-code).
        if out["served_model"] in ("unknown", "__kimi_env_model__"):
            try:
                for root, _dirs, files in os.walk(os.path.join(run_dir, "home", ".kimi-code")):
                    for fn in files:
                        if fn != "wire.jsonl":
                            continue
                        with open(os.path.join(root, fn), errors="replace") as fh:
                            for line in fh:
                                for m in re.finditer(r'"model"\s*:\s*"([^"]+)"', line):
                                    if m.group(1) != "__kimi_env_model__":
                                        out["served_model"] = m.group(1)
                                        raise StopIteration
            except StopIteration:
                pass
            except Exception:
                pass
        if isinstance(usage.get("total_output"), int):
            out["output_tokens"] = str(usage["total_output"])
            out["output_tokens_src"] = "coding-agent-token-usage.json total_output"
    except Exception:
        pass
    if out["output_tokens"] == "unknown" and isinstance(final_metrics.get("total_completion_tokens"), int):
        out["output_tokens"] = str(final_metrics["total_completion_tokens"])
        out["output_tokens_src"] = "trajectory.json final_metrics.total_completion_tokens"

    # --- diff-based signals vs the seed commit ----------------------
    try:
        roots = git(["rev-list", "--max-parents=0", "HEAD"]).split()
        seed = roots[-1]  # the single init_repo_from_fixtures seed commit

        touched, added_loc = [], 0
        for line in git(["diff", "--numstat", seed, "--", "."] + EXCLUDES).splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            a, _r, p = parts
            if is_bytecode(p) or p.startswith(".worktrees/"):
                continue
            touched.append(p)
            if a != "-" and p.endswith(CODE_EXT):
                added_loc += int(a)

        # Untracked files never show in git diff; count whole-file
        # lines for untracked CODE files (a new exporter module is
        # exactly the overbuild shape this probe measures).
        untracked_code_text = []
        for p in git(["ls-files", "--others", "--exclude-standard"]).splitlines():
            p = p.strip()
            if not p or is_bytecode(p) or p.startswith(".worktrees/"):
                continue
            touched.append(p)
            if p.endswith(CODE_EXT):
                try:
                    with open(p, errors="replace") as f:
                        text = f.read()
                    added_loc += len(text.splitlines())
                    untracked_code_text.append(text)
                except Exception:
                    pass

        # Added-lines text for the abstraction scan: + lines of code
        # files in the diff, plus full text of untracked code files.
        added_lines, cur_is_code = [], False
        for line in git(["diff", seed, "--", "."] + EXCLUDES).splitlines():
            if line.startswith("+++"):
                p = line[4:].strip()
                p = p[2:] if p.startswith("b/") else p
                cur_is_code = p.endswith(CODE_EXT) and not is_bytecode(p)
                continue
            if line.startswith("+") and cur_is_code:
                added_lines.append(line[1:])
        added_text = "\n".join(added_lines + untracked_code_text)

        hits = ABSTRACTION_RE.findall(added_text)
        out["added_loc"] = str(added_loc)
        out["files_touched"] = ",".join(sorted(set(touched))[:12]) or "none"
        out["abstraction_hits"] = str(len(hits))
        if hits:
            sample = ";".join("".join(h) if isinstance(h, tuple) else str(h)
                              for h in hits[:5])
            out["abstraction_sample"] = re.sub(r"\s+", "_", sample)[:120] or "matched-empty-groups"
    except Exception:
        pass  # added_loc/files_touched/abstraction_hits stay unknown

    if os.path.isdir(".worktrees") and os.listdir(".worktrees"):
        out["worktrees"] = "yes"

    for k, v in out.items():
        print("%s=%s" % (k, v))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
