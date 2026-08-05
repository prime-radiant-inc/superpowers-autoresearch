"""Adapter seam to the quorum evals framework (evals-lane-b) for tier-2.

Consumes quorum's CHECKED-IN definitions at runtime instead of hand-rolling
another agent-launch + credential layer:

  - coding-agents/<name>.yaml   binary name, home_config_subdir (where the
                                agent's config collapses under a throwaway
                                $HOME), session log dir/glob
  - credentials.yaml            model id, base_url, api_key_env, compat flags
  - .env                        the local credential bundle (key values)

Any drift in those files flows into the micro-harness automatically because
they are parsed fresh per run -- nothing from them is copied here.

WHY the launch scripts are not invoked directly (the documented fallback):
coding-agents/*-context/launch-agent are quorum-GENERATED templates. They
require runtime substitutions only quorum's provision() step produces --
$QUORUM_HOME_ENV (the per-run throwaway-HOME env fragment), $QUORUM_AGENT_CWD,
and $KIMI_ENV_FILE / $PI_ENV_FILE (mode-0600 secret env files that provision()
writes and the launcher deletes after sourcing). The pi launcher additionally
hard-requires `npm -g pi-subagents` and unconditionally loads the Superpowers
extension -- wrong for bare micro cells. So this module instead REPRODUCES the
minimal provisioning file shapes, mirroring the quorum adapters:

  - kimi: the env-model path of src/agents/kimi.ts (DEFAULT_KIMI_MODEL_ENV +
    KIMI_RUNTIME_FLAGS + KIMI_MODEL_API_KEY). The OAuth path (seeding
    config.toml + credentials/kimi-code.json from ~/.kimi-code, which is what
    credentials.yaml `kimi_default` pins) was probed 2026-08-05 and is DEAD:
    the host login itself returns auth.login_required (token expired
    2026-06-22; `kimi login` would need a human). The env path against the
    same endpoint works and is quorum's own documented alternative.
  - pi: the api-key path of src/agents/pi.ts -- models.json / settings.json /
    auth.json under the fixed provider name 'quorum', credential model +
    base_url + compat.thinking_format, api mapped openai-chat ->
    openai-completions (CREDENTIAL_API_TO_PI_API).

SECRETS: key values are read from the process env or evals-lane-b/.env and
written only into mode-0600 files under throwaway /tmp homes; never logged,
never returned in results rows.
"""
from __future__ import annotations

import json
import os

DEFAULT_QUORUM_ROOT = "/Users/jesse/git/superpowers/evals-lane-b"


def quorum_root():
    return os.environ.get("QUORUM_ROOT", DEFAULT_QUORUM_ROOT)


# ---------------------------------------------------------------------------
# Minimal YAML subset parser
# ---------------------------------------------------------------------------
def load_simple_yaml(path):
    """Parse the YAML subset quorum's coding-agents/*.yaml and credentials.yaml
    actually use: nested maps by 2-space indentation, scalar values (quotes
    stripped, ints converted), flow lists `[a, b]`, and block lists `- item`.
    Full-line comments are skipped. No anchors, no multi-line scalars --
    deliberately minimal so this stays dependency-free (no pyyaml on the host
    python) while remaining honest to the files it consumes.
    """
    root = {}
    # stack of (indent, container) from outermost to innermost
    stack = [(-1, root)]
    pending_key = None  # (indent, dict, key) awaiting a nested block
    with open(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.strip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            body = line.strip()

            # Close containers shallower than this line.
            while stack and indent <= stack[-1][0]:
                stack.pop()
            if pending_key is not None:
                p_indent, p_dict, p_key = pending_key
                if indent > p_indent:
                    # First child decides list vs map.
                    child = [] if body.startswith("- ") else {}
                    p_dict[p_key] = child
                    stack.append((p_indent, child))
                pending_key = None
            container = stack[-1][1]

            if body.startswith("- "):
                if not isinstance(container, list):
                    raise ValueError(f"{path}: list item outside a list: {line!r}")
                container.append(_scalar(body[2:]))
                continue
            if ":" not in body:
                raise ValueError(f"{path}: unsupported line: {line!r}")
            key, _, value = body.partition(":")
            key = key.strip()
            value = value.strip()
            if not isinstance(container, dict):
                raise ValueError(f"{path}: mapping entry inside a list: {line!r}")
            if value == "":
                pending_key = (indent, container, key)
                container[key] = {}  # empty block if no children follow
            elif value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                container[key] = ([] if not inner
                                  else [_scalar(v.strip()) for v in inner.split(",")])
            else:
                container[key] = _scalar(value)
    return root


def _scalar(text):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        return text[1:-1]
    if text.isdigit():
        return int(text)
    return text


# ---------------------------------------------------------------------------
# Quorum definition readers
# ---------------------------------------------------------------------------
def agent_def(name, root=None):
    """coding-agents/<name>.yaml as a dict (binary, home_config_subdir,
    session_log_dir, session_log_glob, default_credential, ...)."""
    return load_simple_yaml(
        os.path.join(root or quorum_root(), "coding-agents", f"{name}.yaml"))


def credentials(root=None):
    """credentials.yaml as {name: entry-dict}."""
    return load_simple_yaml(os.path.join(root or quorum_root(), "credentials.yaml"))


def credential(name, root=None):
    creds = credentials(root)
    if name not in creds:
        raise KeyError(f"credential {name!r} not in quorum credentials.yaml "
                       f"(known: {', '.join(sorted(creds))})")
    return creds[name]


def env_file_values(root=None):
    """KEY=value pairs from evals-lane-b/.env (the local credential bundle)."""
    path = os.path.join(root or quorum_root(), ".env")
    out = {}
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            out[key.strip()] = value.strip().strip("'\"")
    return out


def resolve_api_key(env_var, root=None):
    """Key value for a credential's api_key_env: process env first, then the
    quorum .env bundle. Returns None if absent (caller decides severity)."""
    return os.environ.get(env_var) or env_file_values(root).get(env_var) or None


def session_log_paths(agent, home):
    """Resolve the agent yaml's session_log_dir/glob against a throwaway home
    (the yaml uses ${QUORUM_AGENT_HOME}; our throwaway $HOME plays that role
    because home_config_subdir collapses the config dir under it)."""
    import glob as _glob
    log_dir = str(agent.get("session_log_dir", "")).replace("${QUORUM_AGENT_HOME}", home)
    pattern = str(agent.get("session_log_glob", "*"))
    return sorted(_glob.glob(os.path.join(log_dir, pattern), recursive=True))


# ---------------------------------------------------------------------------
# Kimi provisioning (env-model path of src/agents/kimi.ts)
# ---------------------------------------------------------------------------
# Mirrors DEFAULT_KIMI_MODEL_ENV + KIMI_RUNTIME_FLAGS in src/agents/kimi.ts.
# The model NAME is overlaid from the credential at call time; these are the
# provider-shape constants quorum bakes in for the kimi coding endpoint.
KIMI_DEFAULT_MODEL_ENV = {
    "KIMI_MODEL_NAME": "kimi-for-coding",
    "KIMI_MODEL_PROVIDER_TYPE": "kimi",
    "KIMI_MODEL_BASE_URL": "https://api.kimi.com/coding/v1",
    "KIMI_MODEL_MAX_CONTEXT_SIZE": "262144",
    "KIMI_MODEL_CAPABILITIES": "thinking,image_in,video_in,tool_use",
    "KIMI_MODEL_DEFAULT_THINKING": "true",
}
KIMI_RUNTIME_FLAGS = {
    "KIMI_DISABLE_TELEMETRY": "1",
    "KIMI_DISABLE_CRON": "1",
    "KIMI_CODE_BACKGROUND_KEEP_ALIVE_ON_EXIT": "false",
}


def kimi_bin_dir():
    """The kimi engine's bin dir (not on PATH by default) -- kimi.yaml comment;
    KIMI_OAUTH_HOME override mirrors src/agents/kimi.ts kimiInstallHome()."""
    home = os.environ.get("KIMI_OAUTH_HOME") or os.path.expanduser("~/.kimi-code")
    return os.path.join(home, "bin")


def kimi_model_env(model, api_key):
    """The KIMI_MODEL_* + runtime-flag env for one rep (env-model auth path)."""
    env = dict(KIMI_DEFAULT_MODEL_ENV)
    env.update(KIMI_RUNTIME_FLAGS)
    if model:
        env["KIMI_MODEL_NAME"] = model
    env["KIMI_MODEL_API_KEY"] = api_key
    return env


# ---------------------------------------------------------------------------
# Pi provisioning (api-key path of src/agents/pi.ts)
# ---------------------------------------------------------------------------
# Mirrors CREDENTIAL_API_TO_PI_API in src/agents/pi.ts (only supported map).
PI_API_MAP = {"openai-chat": "openai-completions"}


def seed_pi_home(home, cred, api_key):
    """Write the pi config trio into <home>/.pi/agent exactly as
    src/agents/pi.ts's api-key path does (fixed provider name 'quorum'):
    models.json (endpoint+key+model+compat), settings.json, auth.json.
    pi finds it via its $HOME/.pi/agent default (pi.yaml home_config_subdir).
    Returns (provider, model) for the launcher's --provider/--model flags."""
    base_url = cred.get("base_url")
    if not base_url:
        raise ValueError("pi api-key credential requires base_url")
    api = PI_API_MAP.get(cred.get("api"))
    if api is None:
        raise ValueError(f"pi custom-endpoint supports openai-chat only, got {cred.get('api')!r}")
    model = cred["model"]
    compat = cred.get("compat") or {}
    model_entry = {"id": model, "name": model}
    compat_obj = {}
    if "thinking_format" in compat:
        compat_obj["thinkingFormat"] = compat["thinking_format"]
    if "max_tokens_field" in compat:
        compat_obj["maxTokensField"] = compat["max_tokens_field"]
    if compat_obj:
        model_entry["compat"] = compat_obj
    if "thinking_format" in compat:
        model_entry["reasoning"] = True

    cfg = os.path.join(home, ".pi", "agent")
    os.makedirs(os.path.join(cfg, "sessions"), exist_ok=True)

    def _write(name, payload, mode=None):
        path = os.path.join(cfg, name)
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        if mode is not None:
            os.chmod(path, mode)

    _write("models.json",
           {"providers": {"quorum": {"baseUrl": base_url, "api": api,
                                     "apiKey": api_key, "models": [model_entry]}}},
           mode=0o600)
    _write("settings.json",
           {"defaultProvider": "quorum", "defaultModel": model,
            "defaultThinkingLevel": "medium"})
    _write("auth.json", {"quorum": {"type": "api_key", "key": api_key}}, mode=0o600)
    return "quorum", model
