#!/usr/bin/env python3
"""Deterministic skill-AUTOTRIGGERING harness for the superpowers bootstrap.

Measures the ONE question the bootstrap-compression campaign turns on: given a
superpowers checkout (with some `using-superpowers/SKILL.md`), does the right
skill auto-trigger on a naive user request BEFORE the agent jumps to code?

It is a cheaper, faithful proxy for quorum's FULL pipeline for the *triggering*
signal specifically:
  - Same user prompts as quorum's scenarios (copied verbatim from scenarios/).
  - Same fixtures (create_base_repo etc. replicated).
  - Same skill-detection + skill-before-tool logic as src/detect/skill.ts.
  - NO gauntlet LLM verifier: triggering is deterministic, so we read it straight
    off the transcript. That is what lets this run on a subscription OAuth token
    (no x-api-key) and cheaply enough to iterate a compression search.

Each run launches the REAL `claude` binary headless (`-p`) with `--plugin-dir
<SUPERPOWERS_ROOT>` so the SessionStart hook injects the bootstrap exactly as in
a real session, in an ISOLATED throwaway $HOME (no personal CLAUDE.md / plugins
to confound the signal), authed via CLAUDE_CODE_OAUTH_TOKEN.

Auth: set CLAUDE_CODE_OAUTH_TOKEN, or point OAUTH_TOKEN_FILE at a file holding
the token (default ~/.config/superpowers/eval-oauth-token). Mint one with
`claude setup-token`.

Usage:
    # validate the mechanism on the baseline (one rep, sonnet, brainstorming):
    SCENARIOS=superpowers-bootstrap MODELS=sonnet REPS=1 \
        python3 harnesses/triggering-harness.py

    # full focused+guards sweep against a variant checkout:
    SUPERPOWERS_ROOT=/tmp/variant-v3 MODELS=opus,sonnet,haiku REPS=5 \
        python3 harnesses/triggering-harness.py

Env knobs:
    SUPERPOWERS_ROOT  checkout under test (default: the sibling superpowers repo)
    SCENARIOS         csv of scenario names (default: all defined)
    MODELS            csv of opus,sonnet,haiku (default: sonnet)
    REPS              reps per (scenario,model) (default: 3)
    OUT_DIR           results dir (default: ./out/triggering/<variant-hash>)
    OAUTH_TOKEN_FILE  file holding the OAuth token
    MAX_TURNS         claude --max-turns backstop (default: 8)
    TIMEOUT           per-run wall-clock seconds (default: 240)
    FORCE             "1" to ignore cache and rerun
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import glob

# Resolve claude to an absolute path once so a transient PATH/HOME issue or a
# mid-run auto-update swap can't make it "disappear" between runs.
CLAUDE_BIN = shutil.which("claude") or "claude"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_PARENT = os.path.dirname(os.path.dirname(HERE))  # /Users/jesse/git/superpowers
DEFAULT_ROOT = os.path.join(REPO_PARENT, "superpowers")

MODEL_IDS = {
    "opus": "opus",
    "sonnet": "sonnet",
    "haiku": "claude-haiku-4-5-20251001",
}

# ---------------------------------------------------------------------------
# Fixtures: replicate quorum's setup-helpers (file contents copied verbatim).
# Each builder writes into `wd` and leaves a committed git repo on `main`.
# ---------------------------------------------------------------------------
GIT_IDENT = ['-c', 'user.name=Drill Test', '-c', 'user.email=drill@test.local']


def _git(wd, *args):
    subprocess.run(['git', *GIT_IDENT, *args], cwd=wd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _write(wd, rel, content):
    p = os.path.join(wd, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(content)


def fixture_base_repo(wd):
    _git(wd, 'init', '-b', 'main')
    _write(wd, 'package.json', '{\n  "name": "drill-test-project",\n  "version": "1.0.0",\n  "description": "Test project for Drill scenarios",\n  "main": "src/index.js"\n}\n')
    _write(wd, 'README.md', '# Test Project\n\nA minimal project for Drill test scenarios.\n')
    _git(wd, 'add', '-A'); _git(wd, 'commit', '-qm', 'initial commit')
    _write(wd, 'src/utils.js', 'function greet(name) {\n  return `Hello, ${name}!`;\n}\n\nmodule.exports = { greet };\n')
    _git(wd, 'add', '-A'); _git(wd, 'commit', '-qm', 'add utils module')
    _write(wd, 'src/index.js', "const { greet } = require('./utils');\n\nfunction main() {\n  console.log(greet('world'));\n}\n\nmain();\n")
    _git(wd, 'add', '-A'); _git(wd, 'commit', '-qm', 'add entry point')


def fixture_cost_checkbox_page(wd):
    _git(wd, 'init', '-b', 'main')
    _write(wd, 'index.html', '<!doctype html>\n<html>\n<head><title>Tasks</title></head>\n<body>\n<h1>Tasks</h1>\n<main></main>\n</body>\n</html>\n')
    _git(wd, 'add', '-A'); _git(wd, 'commit', '-qm', 'initial: empty tasks page')


def fixture_writing_plans_skeleton(wd):
    _git(wd, 'init', '-b', 'main')
    _write(wd, 'package.json', '{\n  "name": "auth-skeleton",\n  "version": "1.0.0",\n  "type": "module",\n  "main": "app.js",\n  "scripts": { "start": "node app.js" },\n  "dependencies": { "express": "^4.19.0" }\n}\n')
    _write(wd, 'app.js', "import express from 'express';\n\nconst app = express();\napp.use(express.json());\n\nconst users = [];\n\napp.get('/health', (req, res) => {\n  res.json({ ok: true, users: users.length });\n});\n\napp.listen(3000);\n")
    _git(wd, 'add', '-A'); _git(wd, 'commit', '-qm', 'initial: express app with in-memory user store')


def fixture_base_repo_with_auth_plan(wd):
    fixture_base_repo(wd)
    plan = (
        "# Auth System Plan\n\n"
        "## Task 1: Bearer token parser\n"
        "Add `parseAuthToken(header)` in `src/authToken.js` and a node:test suite "
        "`test/authToken.test.js`, plus a `test` npm script.\n\n"
        "## Task 2: Wire into entry point\n"
        "Use `parseAuthToken` in `src/index.js`'s `main()` to print "
        "`authenticated`/`anonymous` based on `process.env.AUTHORIZATION`.\n"
    )
    _write(wd, 'docs/superpowers/plans/2024-01-15-auth-system.md', plan)
    _git(wd, 'add', 'docs'); _git(wd, 'commit', '-qm', 'add auth execution plan')


# ---------------------------------------------------------------------------
# Scenarios: prompt + fixture + the skill that must trigger + impl tools that
# must NOT precede it. Prompts are verbatim from scenarios/<name>/story.md.
# ---------------------------------------------------------------------------
WRITE_EDIT = ["Write", "Edit"]

SCENARIOS = {
    # ---- PRIMARY OBJECTIVES ----
    "superpowers-bootstrap": {
        "prompt": "Let's make a react todo list",
        "fixture": fixture_base_repo,
        "skill": "superpowers:brainstorming",
        "impl_tools": WRITE_EDIT,
        "group": "primary",
    },
    "triggering-systematic-debugging": {
        "prompt": (
            "The tests are failing with this error:\n\n"
            "```\n"
            "FAIL src/utils/parser.test.ts\n"
            "  ● Parser › should handle nested objects\n"
            "    TypeError: Cannot read property 'value' of undefined\n"
            "      at parse (src/utils/parser.ts:42:18)\n"
            "      at Object.<anonymous> (src/utils/parser.test.ts:28:20)\n"
            "```\n\n"
            "Can you figure out what's going wrong and fix it?"
        ),
        "fixture": fixture_base_repo,
        "skill": "superpowers:systematic-debugging",
        "impl_tools": WRITE_EDIT,
        "group": "primary",
    },
    # second brainstorming angle (design-worthy open-ended request)
    "brainstorming-resists-jump-to-implementation": {
        "prompt": (
            "I want users to get notified when tasks they care about change — "
            "build a notifications system for this app."
        ),
        "fixture": fixture_cost_checkbox_page,
        "skill": "superpowers:brainstorming",
        "impl_tools": WRITE_EDIT,
        "group": "primary",
    },
    # over-trigger calibration: a trivial request must NOT trigger brainstorming.
    # INVERTED: passed = brainstorming did NOT fire (matches quorum's skill-not-called).
    "cost-checkbox-over-trigger": {
        "prompt": (
            "I want to add a checkbox component to this page that lets users mark "
            "items as done. Just a basic checkbox with on/off state, nothing fancy."
        ),
        "fixture": fixture_cost_checkbox_page,
        "skill": "superpowers:brainstorming",
        "impl_tools": WRITE_EDIT,
        "mode": "not-called",
        "group": "calibration",
    },
    # ---- REGRESSION GUARDS ----
    "triggering-test-driven-development": {
        "prompt": (
            "I need to add a new feature to validate email addresses. It should:\n"
            "- Check that there's an @ symbol\n"
            "- Check that there's at least one character before the @\n"
            "- Check that there's a dot in the domain part\n"
            "- Return true/false\n\n"
            "Can you implement this?"
        ),
        "fixture": fixture_base_repo,
        "skill": "superpowers:test-driven-development",
        "impl_tools": WRITE_EDIT,
        "group": "guard",
    },
    "triggering-writing-plans": {
        "prompt": (
            "This app already has its scaffolding in place — Express, an in-memory\n"
            "user store, and the usual route setup (see app.js). I need to build\n"
            "out authentication on top of it. Make whatever assumptions you need to\n"
            "get going. Err on the side of extreemly minimal POC. Use mocks. Use \n"
            "stdout. Do not ask me any questions. \n\n"
            "- Users can register with email/password\n"
            "- Users can log in and receive a JWT token\n"
            "- Protected routes require a valid JWT\n"
            "- Tokens expire after 24 hours\n"
            "- Support password reset via email\n\n"
            "Let's build it."
        ),
        "fixture": fixture_writing_plans_skeleton,
        "skill": "superpowers:writing-plans",
        "impl_tools": WRITE_EDIT,
        "group": "guard",
    },
    "triggering-requesting-code-review": {
        "prompt": (
            "I just finished implementing the user authentication feature. All the\n"
            "code is committed. Can you review the changes before I merge to main?\n\n"
            "The commits are between abc123 and def456."
        ),
        "fixture": fixture_base_repo,
        "skill": "superpowers:requesting-code-review",
        "impl_tools": WRITE_EDIT,  # scenario only checks skill-called; impl rarely appears
        "group": "guard",
    },
    "triggering-dispatching-parallel-agents": {
        "prompt": (
            "I have 4 independent test failures happening in different modules:\n\n"
            "1. tests/auth/login.test.ts - 'should redirect after login' is failing\n"
            "2. tests/api/users.test.ts - 'should return user list' returns 500\n"
            "3. tests/components/Button.test.tsx - snapshot mismatch\n"
            "4. tests/utils/date.test.ts - timezone handling broken\n\n"
            "These are unrelated issues in different parts of the codebase. Can you\n"
            "investigate all of them?"
        ),
        "fixture": fixture_base_repo,
        "skill": "superpowers:dispatching-parallel-agents",
        "impl_tools": ["Agent", "Task"],
        "group": "guard",
    },
    "triggering-executing-plans": {
        "prompt": (
            "I have a plan document at docs/superpowers/plans/2024-01-15-auth-system.md\n"
            "that needs to be executed. Please implement it."
        ),
        "fixture": fixture_base_repo_with_auth_plan,
        "skill": "superpowers:executing-plans",
        "impl_tools": WRITE_EDIT,
        "group": "guard",
    },
    "triggering-finishing-a-development-branch": {
        "prompt": (
            "I just finished the change I was working on and committed it. I think\n"
            "this work is done. Can you help me wrap it up and get it integrated?"
        ),
        "fixture": fixture_base_repo,
        "skill": "superpowers:finishing-a-development-branch",
        "impl_tools": WRITE_EDIT,
        "group": "guard",
    },
}


# ---------------------------------------------------------------------------
# Detection: faithful to src/detect/skill.ts isSkillInvocation().
# ---------------------------------------------------------------------------
import re


def skill_dir(skill_name):
    return skill_name.split(":", 1)[1]


def is_skill_invocation(tool, args, name, d):
    safe = re.escape(d)
    if tool == "Skill":
        return str(args.get("skill", "")) == name
    if tool in ("Bash", "Shell", "LocalShellCall"):
        cmd = str(args.get("command", args.get("cmd", "")))
        return re.search(r"(^|[\s'\"/])skills/(superpowers/)?" + safe + r"/SKILL\.md([\s'\";]|$)", cmd) is not None
    if tool == "Read":
        p = str(args.get("file_path", args.get("path", "")))
        return re.search(r"(^|/)skills/(superpowers/)?" + safe + r"/SKILL\.md$", p) is not None
    return False


def parse_stream(stdout):
    """Return ordered list of tool_use {tool,args} from claude -p stream-json."""
    calls = []
    final = {}
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "assistant":
            for block in ev.get("message", {}).get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    calls.append({"tool": block.get("name", ""), "args": block.get("input", {}) or {}})
        elif t == "result":
            final = ev
    return calls, final


def evaluate(calls, skill, impl_tools, mode="before-tool"):
    d = skill_dir(skill)
    skill_idx = None
    impl_idx = None
    for i, c in enumerate(calls):
        if skill_idx is None and is_skill_invocation(c["tool"], c["args"], skill, d):
            skill_idx = i
        if impl_idx is None and c["tool"] in impl_tools:
            impl_idx = i
    skill_called = skill_idx is not None
    # skill-before-tool: pass if skill loaded and no impl tool preceded it
    if not skill_called:
        before = False
    elif impl_idx is None:
        before = True
    else:
        before = skill_idx < impl_idx
    if mode == "not-called":
        # over-trigger guard: pass when the skill does NOT fire
        passed = not skill_called
    else:
        passed = skill_called and before
    return {
        "mode": mode,
        "skill_called": skill_called,
        "skill_before_impl": before,
        "passed": passed,
        "skill_idx": skill_idx,
        "first_impl_idx": impl_idx,
        "n_calls": len(calls),
        "tools_seen": [c["tool"] for c in calls][:25],
    }


# ---------------------------------------------------------------------------
# Run one (scenario, model, rep)
# ---------------------------------------------------------------------------
def read_token():
    tok = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if tok:
        return tok
    path = os.environ.get("OAUTH_TOKEN_FILE", os.path.expanduser("~/.config/superpowers/eval-oauth-token"))
    if os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    return None


def seed_home(home):
    cfgdir = os.path.join(home, ".claude")
    os.makedirs(cfgdir, exist_ok=True)
    # Minimal config: completed onboarding so claude boots headless; no plugins,
    # no MCP, no personal CLAUDE.md -> clean environment.
    with open(os.path.join(home, ".claude.json"), "w") as f:
        json.dump({"hasCompletedOnboarding": True,
                   "autoUpdates": False,
                   "customApiKeyResponses": {"approved": [], "rejected": []}}, f)


def bootstrap_injected(home):
    """Sanity: did the SessionStart hook inject the bootstrap into the session?"""
    for jf in glob.glob(os.path.join(home, ".claude", "projects", "**", "*.jsonl"), recursive=True):
        try:
            with open(jf) as f:
                if "You have superpowers" in f.read():
                    return True
        except OSError:
            pass
    return False


def run_one(scenario_name, model, rep, root, token, out_dir, max_turns, timeout):
    import tempfile
    scen = SCENARIOS[scenario_name]
    rec_path = os.path.join(out_dir, f"{scenario_name}__{model}__rep{rep}.json")
    if os.path.exists(rec_path) and os.environ.get("FORCE") != "1":
        with open(rec_path) as f:
            return json.load(f)

    home = tempfile.mkdtemp(prefix="sp-th-home.")
    wd = tempfile.mkdtemp(prefix="sp-th-wd.")
    seed_home(home)
    scen["fixture"](wd)

    env = dict(os.environ)
    for k in ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_ENTRYPOINT", "ANTHROPIC_API_KEY"):
        env.pop(k, None)
    env["HOME"] = home
    env["CLAUDE_CODE_OAUTH_TOKEN"] = token
    env["CLAUDE_CODE_FORCE_SESSION_PERSISTENCE"] = "1"
    env["DISABLE_AUTOUPDATER"] = "1"  # no mid-campaign version drift / binary-swap crashes

    cmd = [
        CLAUDE_BIN, "-p", scen["prompt"],
        "--plugin-dir", root,
        "--model", MODEL_IDS[model],
        "--output-format", "stream-json", "--verbose",
        "--dangerously-skip-permissions",
        "--max-turns", str(max_turns),
    ]
    rec = {"scenario": scenario_name, "model": model, "rep": rep,
           "root": root, "home": home, "wd": wd}
    try:
        proc = subprocess.run(cmd, cwd=wd, env=env, capture_output=True,
                              text=True, timeout=timeout)
        calls, final = parse_stream(proc.stdout)
        ev = evaluate(calls, scen["skill"], scen["impl_tools"], scen.get("mode", "before-tool"))
        rec.update(ev)
        rec["bootstrap_injected"] = bootstrap_injected(home)
        rec["num_turns"] = final.get("num_turns")
        rec["result_subtype"] = final.get("subtype")
        res_text = (final.get("result") or "").strip()
        # `is_error` is also set when the run merely hits --max-turns (empty result
        # text). A GENUINE error (auth/API) carries a non-empty message.
        rec["errored"] = bool(final.get("is_error")) and bool(res_text)
        rec["api_result"] = res_text[:200] if res_text else None
        rec["usage"] = final.get("usage", {})
        rec["stderr_tail"] = proc.stderr[-400:] if proc.stderr else ""
    except subprocess.TimeoutExpired:
        rec.update({"passed": False, "skill_called": None, "timeout": True})
    except OSError as e:
        # e.g. claude briefly missing during an auto-update swap. Record and
        # continue so one bad launch doesn't abort the whole sweep.
        rec.update({"passed": False, "skill_called": None, "errored": True,
                    "api_result": f"launch failed: {e}"})

    os.makedirs(out_dir, exist_ok=True)
    with open(rec_path, "w") as f:
        json.dump(rec, f, indent=2)
    return rec


def main():
    root = os.environ.get("SUPERPOWERS_ROOT", DEFAULT_ROOT)
    skill_md = os.path.join(root, "skills", "using-superpowers", "SKILL.md")
    if not os.path.exists(skill_md):
        sys.stderr.write(f"no bootstrap at {skill_md}\n"); return 2
    vhash = hashlib.sha256(open(skill_md, "rb").read()).hexdigest()[:12]

    token = read_token()
    if not token:
        sys.stderr.write("No OAuth token. Set CLAUDE_CODE_OAUTH_TOKEN or OAUTH_TOKEN_FILE "
                         "(default ~/.config/superpowers/eval-oauth-token). Mint with `claude setup-token`.\n")
        return 2

    scen_names = os.environ.get("SCENARIOS")
    scenarios = [s.strip() for s in scen_names.split(",")] if scen_names else list(SCENARIOS)
    models = [m.strip() for m in os.environ.get("MODELS", "sonnet").split(",")]
    reps = int(os.environ.get("REPS", "3"))
    max_turns = int(os.environ.get("MAX_TURNS", "5"))
    timeout = int(os.environ.get("TIMEOUT", "240"))
    out_dir = os.environ.get("OUT_DIR", os.path.join(HERE, "..", "out", "triggering", vhash))
    out_dir = os.path.abspath(out_dir)

    print(f"bootstrap variant hash: {vhash}  ({skill_md})")
    print(f"root={root}\nout_dir={out_dir}\nmodels={models} reps={reps} scenarios={scenarios}\n")

    results = []
    for s in scenarios:
        if s not in SCENARIOS:
            sys.stderr.write(f"unknown scenario {s}, skipping\n"); continue
        for m in models:
            for r in range(reps):
                rec = run_one(s, m, r, root, token, out_dir, max_turns, timeout)
                results.append(rec)
                flag = "PASS" if rec.get("passed") else "fail"
                extra = ""
                if rec.get("errored"):
                    extra = f" [API ERROR: {rec.get('api_result')}]"
                elif rec.get("timeout"):
                    extra = " [TIMEOUT]"
                elif not rec.get("bootstrap_injected", True):
                    extra = " [!! bootstrap NOT injected]"
                print(f"  {s:42s} {m:7s} rep{r}: {flag}  "
                      f"(skill_idx={rec.get('skill_idx')}, impl_idx={rec.get('first_impl_idx')}){extra}")

    # summary
    print("\n=== SUMMARY (pass rate) ===")
    grid = {}
    for rec in results:
        key = (rec["scenario"], rec["model"])
        grid.setdefault(key, []).append(1 if rec.get("passed") else 0)
    for (s, m), v in sorted(grid.items()):
        print(f"  {s:42s} {m:7s}: {sum(v)}/{len(v)}")
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nresults: {out_dir}/results.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
