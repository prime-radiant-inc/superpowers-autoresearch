#!/usr/bin/env bash
# validate_t9_tooling_ask.sh — no-spend dry-run of t9-tooling-ask's post()
# instruments against a REAL prior run's artifacts.
#
# Why: t9-tooling-ask/checks.sh parses codex rollout jsonl (agent_message /
# patch_apply_end / turn_context records) mechanically. This harness stubs
# the quorum prelude verbs as echoes and points QUORUM_RUN_DIR at any
# existing results run dir, so the parsing/ordering logic gets exercised on
# real rollouts without launching a battery. On an unrelated run the
# expected grades are `unknown`/`n-a` — the point is that every instrument
# line emits, timestamps extract and order, and nothing crashes.
#
# Usage:
#   validate_t9_tooling_ask.sh <run-dir>
# where <run-dir> contains home/.codex/sessions/ and coding-agent-workdir/
# (e.g. evals/results/<scenario-arm-repN>/<scenario-agent-...-hash>/).
set -u

RUN=${1:?usage: validate_t9_tooling_ask.sh RUN_DIR (contains home/ and coding-agent-workdir/)}
CHECKS="$(cd "$(dirname "$0")" && pwd)/scenarios/t9-tooling-ask/checks.sh"

command-succeeds() { echo "EMIT: $*"; }
git-repo() { :; }
file-exists() { :; }
not() { :; }

export QUORUM_RUN_DIR="$RUN"
# shellcheck source=scenarios/t9-tooling-ask/checks.sh
source "$CHECKS"
cd "$RUN/coding-agent-workdir" || { echo "no coding-agent-workdir under $RUN" >&2; exit 1; }
post
