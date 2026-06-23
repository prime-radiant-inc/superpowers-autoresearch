#!/usr/bin/env bash
# Launch a CLEAN, isolated, keychain-free INTERACTIVE claude with a chosen bootstrap
# variant injected — to eyeball skill triggering by hand (what quorum measures, but
# you drive it). Isolation matters: your real ~/.claude/CLAUDE.md pushes brainstorming/
# TDD and would confound the result, so this pins a throwaway $HOME with no CLAUDE.md.
#
# Auth is the apiKeyHelper path (the keychain-free fix): a mode-0700 helper prints the
# ANTHROPIC_API_KEY from serf/.env; it outranks the keychain and isn't the "use this API
# key?" dialog, so no keychain prompt fires. ANTHROPIC_API_KEY is stripped from the env
# so the helper (not the env key) is what claude resolves.
#
# Usage:
#   bash harnesses/manual-trigger-test.sh            # z-null (gutted bootstrap)
#   bash harnesses/manual-trigger-test.sh baseline   # the live bootstrap
#   bash harnesses/manual-trigger-test.sh g-minimal  # any built /tmp/sp-var-<name>
#
# Then type a test prompt and watch whether a skill auto-triggers, e.g.:
#   build a notifications system for this app      (design-worthy -> SHOULD brainstorm)
#   add a basic on/off checkbox, nothing fancy     (trivial      -> should NOT brainstorm)
#   the tests are failing with <paste error>       (-> SHOULD load systematic-debugging)
set -euo pipefail

VARIANT="${1:-z-null}"
if [ "$VARIANT" = baseline ]; then
  ROOT=/Users/jesse/git/superpowers/superpowers
else
  ROOT="/tmp/sp-var-$VARIANT"
fi
[ -d "$ROOT" ] || { echo "No plugin root at $ROOT — build it first:"; echo "  python3 harnesses/build-variant-roots.py $VARIANT"; exit 1; }

KEY=$(grep -E "^ANTHROPIC_API_KEY=" /Users/jesse/git/prime-radiant-inc/serf/.env | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
[ -n "$KEY" ] || { echo "no ANTHROPIC_API_KEY in serf/.env"; exit 1; }

THOME=$(mktemp -d /tmp/sp-manual-home-XXXXXX)
WORKDIR=$(mktemp -d /tmp/sp-manual-work-XXXXXX)
( cd "$WORKDIR" && git init -q && printf '# scratch\n' > README.md )

mkdir -p "$THOME/.claude"
# Onboarding done + trust the scratch workdir, so no trust/onboarding prompts.
printf '{"hasCompletedOnboarding":true,"projects":{"%s":{"hasTrustDialogAccepted":true,"projectOnboardingSeenCount":1}}}\n' \
  "$WORKDIR" > "$THOME/.claude.json"
# apiKeyHelper: keychain-free interactive auth.
printf "#!/bin/sh\nprintf '%%s' '%s'\n" "$KEY" > "$THOME/.claude/api-key-helper.sh"
chmod 700 "$THOME/.claude/api-key-helper.sh"
printf '{"apiKeyHelper":"%s/.claude/api-key-helper.sh"}\n' "$THOME" > "$THOME/.claude/settings.json"

echo "── manual trigger test ─────────────────────────────"
echo "  variant:  $VARIANT"
echo "  bootstrap: $ROOT/skills/using-superpowers/SKILL.md ($(wc -l < "$ROOT/skills/using-superpowers/SKILL.md") lines)"
echo "  isolated HOME: $THOME   workdir: $WORKDIR"
echo "  try:  build a notifications system for this app   (should brainstorm)"
echo "        add a basic on/off checkbox, nothing fancy  (should NOT brainstorm)"
echo "─────────────────────────────────────────────────────"
cd "$WORKDIR"
exec env -u CLAUDECODE -u CLAUDE_CODE_SESSION_ID -u ANTHROPIC_API_KEY \
  HOME="$THOME" CLAUDE_CODE_FORCE_SESSION_PERSISTENCE=1 \
  claude --plugin-dir "$ROOT"
