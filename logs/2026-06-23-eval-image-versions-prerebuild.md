# Eval image tool/CLI versions — PRE-REBUILD snapshot (for drift comparison)

> This is the PRE-REBUILD snapshot of the `superpowers-evals:local` Docker image,
> captured **before** rebuilding so we can detect and justify any version drift
> afterward. Almost nothing is version-pinned in the Dockerfile, so a rebuild will
> likely pull newer floating versions.

- Captured: 2026-06-23
- Runtime: Docker (per `evals/scripts/evals-container`, which shells out to `docker`)
- Image tag: `superpowers-evals:local`
- Method: non-mutating one-off containers (`docker run --rm superpowers-evals:local ...`)

## Image identity

| Field | Value |
|---|---|
| Id | `sha256:df6aa975e58b04f38c8cb0202c21ea5a802c516cb60b0a040d2637a5fc2a44c0` |
| Created | `2026-06-17T21:35:33.882932348-07:00` |
| Size | `14045124643` bytes (~14 GB) |
| Architecture / OS | `arm64` / `linux` |
| RepoTags | `superpowers-evals:local` |
| RepoDigests | (none — locally built, never pushed) |

Host Docker engine: `Docker version 29.4.0, build 9d7ad9f`.

## Agent CLIs — version + Dockerfile pin status

Versions captured two ways (the in-image `evals-tool-versions` reporter and an
explicit per-CLI `--version` sweep); they agree. "Pinned?" reflects the
Dockerfile `npm install -g` line (~line 86) and the goose `ARG GOOSE_VERSION`.

| Agent CLI | Version (in current image) | Pinned in Dockerfile? |
|---|---|---|
| claude (`@anthropic-ai/claude-code`) | 2.1.181 (Claude Code) | floating |
| codex (`@openai/codex`) | codex-cli 0.140.0 | floating |
| gemini (`@google/gemini-cli`) | 0.47.0 | floating |
| kimi (`@moonshot-ai/kimi-code`) | 0.15.0 | **PINNED `@0.15.0`** |
| opencode (`opencode-ai`) | 1.17.8 | floating |
| pi (`@mariozechner/pi-coding-agent`) | 0.73.1 | floating |
| agy (Google Antigravity CLI) | 1.0.9 | floating (curl install script) |
| copilot (`@github/copilot`) | GitHub Copilot CLI 1.0.63 | floating |
| cursor-agent | 2026.06.15-18-00-12-6f5a2cf | floating (curl install script) |
| grok (`@xai-official/grok`) | 0.2.56 (4d4448c98) | floating |
| droid (`@factory/cli`) | 0.150.1 | floating |
| qwen (`@qwen-code/qwen-code`) | 0.18.3 | floating |
| kilo (`@kilocode/cli`) | 7.3.46 | floating |
| openclaw | 2026.6.8 (844f405) | floating |
| amp (`@sourcegraph/amp`) | 0.0.1781748643-ge56198 (released 2026-06-18) | floating |
| cline | 3.0.27 | floating |
| goose | 1.31.1 | **PINNED `ARG GOOSE_VERSION=1.31.1`** |
| hermes | Hermes Agent v0.16.0 (2026.6.5) · upstream 4440d77b | floating (curl install script) |
| mimo | 0.1.1 | floating (curl install script) |
| mini-swe-agent | 2.4.1 | floating (`uv tool install`) |
| sweagent (SWE-agent) | 1.1.0 | floating (`git clone --depth 1`, HEAD) |
| trae-cli (trae-agent) | trae-cli, version 0.1.0 | floating (`git+https://...trae-agent.git`, HEAD) |

Notes on the two "version check failed" entries from the reporter — both report
their version successfully but exit non-zero on `--version`, so they are present
and the version IS captured:
- `mini-swe-agent`: prints "version 2.4.1" then exits 2.
- `sweagent`: prints "version 1.1.0" then exits 2.

## Core tools — version

| Tool | Version |
|---|---|
| bash | GNU bash, version 5.3.9(1)-release (aarch64-unknown-linux-gnu) |
| zsh | zsh 5.9 (aarch64-unknown-linux-gnu) |
| git | git version 2.53.0 |
| gh | gh version 2.46.0 (2025-12-13 Ubuntu 2.46.0-4) |
| node | v22.22.3 (NodeSource setup_22.x) |
| npm | 10.9.8 |
| bun | 1.3.14 |
| python3 | Python 3.14.4 |
| uv | uv 0.11.21 (aarch64-unknown-linux-gnu) |
| go | go version go1.26.0 linux/arm64 |
| rustc | rustc 1.96.0 (ac68faa20 2026-05-25) |
| cargo | cargo 1.96.0 (30a34c682 2026-05-25) |
| ruby | ruby 3.3.8 (2025-04-09 revision b200bad6cd) [aarch64-linux-gnu] |
| mise | 2026.6.10 linux-arm64 (2026-06-14) |
| quorum | NOT a version — see note below |

Base image: `ubuntu:26.04` (from Dockerfile `FROM`). apt packages (bash, zsh,
git, gh, curl, jq, yq, ripgrep, fd-find, shellcheck, tmux, build-essential,
python3/pip/venv, ruby-full, golang-go, etc.) are unpinned and resolve to
whatever the Ubuntu 26.04 repos serve at build time.

### About the `quorum` reporter line

The in-image reporter prints:

```
quorum: present (version check failed with exit 1): error: Module not found "src/cli/index.ts"
```

This is **not** a version-drift concern. `/usr/local/bin/quorum` is a bun shim
(`exec bun /opt/gauntlet/src/index.ts "$@"` for gauntlet; the quorum shim
likewise runs against the mounted source tree). In a `--rm` one-off there is no
`/workspace/evals` source mount, so it can't resolve `src/cli/index.ts`. The
quorum/gauntlet code is the host source tree (bind-mounted at run time), not a
baked-in versioned artifact, so it has no image-level version to drift.

## Full `evals-tool-versions` output (verbatim)

```
Core tools:
bash: GNU bash, version 5.3.9(1)-release (aarch64-unknown-linux-gnu)
zsh: zsh 5.9 (aarch64-unknown-linux-gnu)
git: git version 2.53.0
gh: gh version 2.46.0 (2025-12-13 Ubuntu 2.46.0-4)
node: v22.22.3
npm: 10.9.8
bun: 1.3.14
python3: Python 3.14.4
uv: uv 0.11.21 (aarch64-unknown-linux-gnu)
go: go version go1.26.0 linux/arm64
rustc: rustc 1.96.0 (ac68faa20 2026-05-25)
cargo: cargo 1.96.0 (30a34c682 2026-05-25)
ruby: ruby 3.3.8 (2025-04-09 revision b200bad6cd) [aarch64-linux-gnu]
mise: 2026.6.10 linux-arm64 (2026-06-14)
quorum: present (version check failed with exit 1): error: Module not found "src/cli/index.ts"

Agent CLIs:
claude: 2.1.181 (Claude Code)
codex: codex-cli 0.140.0
gemini: 0.47.0
opencode: 1.17.8
pi: 0.73.1
copilot: GitHub Copilot CLI 1.0.63.
grok: grok 0.2.56 (4d4448c98)
droid: 0.150.1
qwen: 0.18.3
kilo: 7.3.46
openclaw: OpenClaw 2026.6.8 (844f405)
amp: 0.0.1781748643-ge56198 (released 2026-06-18T02:10:43.000Z, 5d ago)
cline: 3.0.27
cursor-agent: 2026.06.15-18-00-12-6f5a2cf
goose:  1.31.1
agy: 1.0.9
kimi: 0.15.0
mini-swe-agent: present (version check failed with exit 2): 👋 This is mini-swe-agent version 2.4.1.
sweagent: present (version check failed with exit 2): 👋 INFO     This is SWE-agent version 1.1.0
trae-cli: trae-cli, version 0.1.0
hermes: Hermes Agent v0.16.0 (2026.6.5) · upstream 4440d77b
mimo: 0.1.1
```

## `npm ls -g --depth=0` (verbatim)

```
/usr/lib
+-- @anthropic-ai/claude-code@2.1.181
+-- @factory/cli@0.150.1
+-- @github/copilot@1.0.63
+-- @google/gemini-cli@0.47.0
+-- @kilocode/cli@7.3.46
+-- @mariozechner/pi-coding-agent@0.73.1
+-- @moonshot-ai/kimi-code@0.15.0
+-- @openai/codex@0.140.0
+-- @qwen-code/qwen-code@0.18.3
+-- @sourcegraph/amp@0.0.1781748643-ge56198
+-- @xai-official/grok@0.2.56
+-- cline@3.0.27
+-- corepack@0.34.6
+-- npm@10.9.8
+-- openclaw@2026.6.8
`-- opencode-ai@1.17.8
```

## Drift-watch summary

Only TWO things are version-pinned in the Dockerfile and should NOT drift on
rebuild unless the pin is changed:
- `@moonshot-ai/kimi-code@0.15.0` (npm install -g)
- goose `ARG GOOSE_VERSION=1.31.1`

Everything else is floating and is expected to potentially change on rebuild:
- All other npm `-g` agent CLIs (claude, codex, gemini, opencode, copilot,
  factory/droid, qwen, kilocode/kilo, openclaw, amp, cline, pi, grok).
- curl-installer CLIs (cursor-agent, agy/Antigravity, hermes, mimo, bun, uv,
  rustup→rustc/cargo, mise).
- `uv tool install` / git-HEAD installs (mini-swe-agent, sweagent, trae-cli).
- NodeSource node 22.x line and all `ubuntu:26.04` apt packages.
