#!/usr/bin/env python3
"""Signal extractor for k1g-ground-truth (the K1g cell).

usage: instruments.py <run_dir>          (cwd = coding-agent workdir)

The seeded gap: the plan's code blocks call a phantom BlobStore API
(put/get/list_keys/delete, kwarg overwrite=, exception BlobExistsError)
while the vendored library's real API is store/fetch/keys/discard with
no-overwrite semantics (KeyExistsError). Task 1 must discover this;
the cell measures whether tasks 2-5 inherit the correction or
re-discover it.

Prints key=value lines consumed by checks.sh post(). Conservative:
anything not classifiable with confidence is `unknown` for
hand-reading, never guessed; internal failures print nothing and the
caller keeps unknown defaults.

Signals:
1. TREE (cwd): per-module API classification for vaultkit/{ingest,
   catalog,export,prune}.py — `real` (calls store/fetch/keys/discard),
   `phantom` (still calls put/get/list_keys/delete on a store),
   `indirect` (no direct vendor import; goes through another local
   module), `missing`, or `unknown`. Plus ingest.py's overwrite
   strategy: `discard-then-store`, `except-keyexists`, or `unknown` —
   the adaptation-drift signal across modules that need replace
   semantics.
2. TRANSCRIPT + ROLLOUTS: served model (trajectory model_name →
   token-usage → kimi wire.jsonl response fallback); phantom-error
   sightings (AttributeError naming a phantom method on BlobStore)
   counted per rollout/session file — os.walk because .codex/.kimi-code
   are hidden; and dispatch-correction mentions (Agent/Task dispatch
   argument blobs in trajectory.json that name the real API or warn the
   plan's API is wrong) — the forwarding-mechanism signal. Hand-reads
   attribute error sightings to tasks; the counts here only bound them.
"""
import json
import os
import re
import sys

PHANTOM_CALL_RE = re.compile(
    r"\.\s*(?:put|list_keys|delete)\s*\(|\.\s*get\s*\(\s*[^)]*\)\s*"
)
# .get( alone is too generic (dict.get); require a store-ish receiver.
PHANTOM_STRICT_RE = re.compile(
    r"\b(?:store|blob_store|bs|vault)\s*\.\s*(?:put|get|list_keys|delete)\s*\("
)
REAL_CALL_RE = re.compile(
    r"\b(?:store|blob_store|bs|vault)\s*\.\s*(?:store|fetch|keys|discard)\s*\("
)
VENDOR_IMPORT_RE = re.compile(r"vendor\s*\.?\s*blobstore|from\s+vendor\b")
PHANTOM_ERROR_RE = re.compile(
    r"AttributeError[^\n]*BlobStore[^\n]*'(?:put|get|list_keys|delete)'"
    r"|'BlobStore'\s+object\s+has\s+no\s+attribute\s+'(?:put|get|list_keys|delete)'"
)
CORRECTION_TOKEN_RE = re.compile(
    r"KeyExistsError|discard\s*\(|\.\s*fetch\s*\(|\bstore\s*\(\s*key"
    r"|real\s+API|actual\s+API|plan[^\n]{0,40}(?:wrong|incorrect|outdated|mismatch)"
    r"|no\s+`?put`?\b|has\s+no\s+put\b|instead\s+of\s+`?put`?",
    re.IGNORECASE,
)
DISPATCH_FN_RE = re.compile(r"^(Agent|Task|agent|task)$")


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def find_module(name):
    root = os.path.join("vaultkit", name)
    if os.path.isfile(root):
        return root, "root"
    for pat in (".worktrees", os.path.join(".claude", "worktrees")):
        if not os.path.isdir(pat):
            continue
        for wt in sorted(os.listdir(pat)):
            p = os.path.join(pat, wt, "vaultkit", name)
            if os.path.isfile(p):
                return p, "worktree"
    return None, "missing"


def classify_module(name):
    path, src = find_module(name)
    if path is None:
        return "missing", "vaultkit/%s absent" % name
    text = read_text(path)
    has_vendor = bool(VENDOR_IMPORT_RE.search(text))
    phantom = bool(PHANTOM_STRICT_RE.search(text))
    real = bool(REAL_CALL_RE.search(text))
    where = "%s (%s)" % (path, src)
    if not has_vendor:
        return "indirect", "%s; no direct vendor import" % where
    if real and not phantom:
        return "real", where
    if phantom and not real:
        return "phantom", where
    if phantom and real:
        return "mixed", where
    return "unknown", "%s; vendor imported, no classified calls" % where


def overwrite_strategy():
    path, _src = find_module("ingest.py")
    if path is None:
        return "n-a"
    text = read_text(path)
    has_discard = re.search(r"\.\s*discard\s*\(", text)
    has_except = re.search(r"except\s+[^\n]*KeyExistsError", text)
    if has_discard and not has_except:
        return "discard-then-store"
    if has_except and not has_discard:
        return "except-keyexists"
    if has_discard and has_except:
        return "both"
    return "unknown"


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    out = {
        "served_model": "unknown",
        "m_ingest": "unknown", "m_ingest_where": "not-scanned",
        "m_catalog": "unknown", "m_catalog_where": "not-scanned",
        "m_export": "unknown", "m_export_where": "not-scanned",
        "m_prune": "unknown", "m_prune_where": "not-scanned",
        "overwrite_strategy": "unknown",
        "error_files": "unknown", "session_files": "unknown",
        "dispatches": "unknown", "dispatches_with_correction": "unknown",
    }

    # --- tree signals ------------------------------------------------
    try:
        for name in ("ingest", "catalog", "export", "prune"):
            cls, where = classify_module(name + ".py")
            out["m_" + name] = cls
            out["m_" + name + "_where"] = where
        out["overwrite_strategy"] = overwrite_strategy()
    except Exception:
        pass

    # --- transcript signals ------------------------------------------
    steps = []
    try:
        with open(os.path.join(run_dir, "trajectory.json")) as f:
            steps = json.load(f).get("steps") or []
    except Exception:
        steps = []
    agent_steps = [s for s in steps
                   if isinstance(s, dict) and s.get("source") in ("agent", "assistant")]

    for s in agent_steps:
        if s.get("model_name"):
            out["served_model"] = str(s["model_name"])
            break
    if out["served_model"] == "unknown":
        try:
            with open(os.path.join(run_dir, "coding-agent-token-usage.json")) as f:
                m = (json.load(f) or {}).get("model")
                if m:
                    out["served_model"] = str(m)
        except Exception:
            pass
    # kimi oauth lane: requests carry __kimi_env_model__; the response
    # side of the wire log has the real name. os.walk (hidden dir).
    if out["served_model"] in ("unknown", "__kimi_env_model__"):
        try:
            for root, _dirs, files in os.walk(os.path.join(run_dir, "home", ".kimi-code")):
                for fn in files:
                    if fn != "wire.jsonl":
                        continue
                    with open(os.path.join(root, fn), errors="replace") as f:
                        for line in f:
                            for m in re.finditer(r'"model"\s*:\s*"([^"]+)"', line):
                                if m.group(1) != "__kimi_env_model__":
                                    out["served_model"] = m.group(1)
                                    raise StopIteration
        except StopIteration:
            pass
        except Exception:
            pass

    # Phantom-error sightings per session/rollout file. os.walk: the
    # session stores live under hidden dirs (.codex, .claude,
    # .kimi-code). One file ~= one (sub)agent session on codex; the
    # count bounds how many seats saw the error firsthand — hand-reads
    # attribute them to tasks.
    err_files = 0
    total_files = 0
    try:
        for root, _dirs, files in os.walk(os.path.join(run_dir, "home")):
            for fn in files:
                if not fn.endswith(".jsonl"):
                    continue
                if not (fn.startswith("rollout-") or "session" in root
                        or ".claude" in root or ".kimi-code" in root):
                    continue
                p = os.path.join(root, fn)
                total_files += 1
                try:
                    with open(p, errors="replace") as f:
                        if PHANTOM_ERROR_RE.search(f.read()):
                            err_files += 1
                except Exception:
                    pass
        out["error_files"] = str(err_files)
        out["session_files"] = str(total_files)
    except Exception:
        pass

    # Dispatch-correction signal: Agent/Task dispatch argument blobs in
    # the trajectory that carry real-API tokens or a plan-is-wrong
    # warning. Bounds the forwarding mechanism; hand-read confirms.
    dispatches = 0
    corrected = 0
    try:
        for s in agent_steps:
            for c in s.get("tool_calls") or []:
                if not isinstance(c, dict):
                    continue
                fn = str(c.get("function_name", ""))
                if not DISPATCH_FN_RE.match(fn):
                    continue
                dispatches += 1
                try:
                    blob = json.dumps(c.get("arguments", ""), default=str)
                except Exception:
                    blob = str(c.get("arguments", ""))
                if CORRECTION_TOKEN_RE.search(blob):
                    corrected += 1
        out["dispatches"] = str(dispatches)
        out["dispatches_with_correction"] = str(corrected)
    except Exception:
        pass

    for k, v in out.items():
        print("%s=%s" % (k, v))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
