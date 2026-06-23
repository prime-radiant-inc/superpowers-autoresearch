#!/usr/bin/env bash
# Brainstorming-centered sensitivity control (Jesse: test brainstorming, not just
# systematic-debugging; and don't trust the -p screen's "brainstorming self-triggers
# regardless" claim — prove it faithfully). z-null is the negative control: a gutted
# 6-line bootstrap. If z-null makes the agent JUMP TO CODE on the hard, design-worthy
# request (fails brainstorming-resists-jump) while baseline brainstorms, the instrument
# genuinely detects bootstrap damage on BRAINSTORMING — and compression preserving it
# then means something.
#
# Scenarios (brainstorming calibration):
#   brainstorming-resists-jump-to-implementation  HARD, MUST fire ("build a notifications
#                                                 system" — no design cue; bootstrap-dependent)
#   superpowers-bootstrap                          EASY anchor ("react todo list")
#   brainstorming-companion-just-in-time           design request, should fire
#   cost-checkbox-over-trigger                     MUST NOT fire (trivial; calibration twin)
#
# Model: haiku (sharpest discriminator + cheapest). Variants: baseline + z-null + the two
# aggressive ship candidates.
#
# Usage: REPS=3 JOBS=6 bash harnesses/quorum-brainstorm-ctrl.sh
set -uo pipefail

EVALS=/Users/jesse/git/superpowers/superpowers/evals
SERF_ENV=/Users/jesse/git/prime-radiant-inc/serf/.env
AGENTS="claude-haiku"
SCEN="brainstorming-resists-jump-to-implementation,superpowers-bootstrap,brainstorming-companion-just-in-time,cost-checkbox-over-trigger"
REPS=${REPS:-3}
JOBS=${JOBS:-6}

export ANTHROPIC_API_KEY=$(grep -E "^ANTHROPIC_API_KEY=" "$SERF_ENV" | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
[ -n "$ANTHROPIC_API_KEY" ] || { echo "no ANTHROPIC_API_KEY"; exit 1; }
export DISABLE_AUTOUPDATER=1

root_for() {
  case "$1" in
    baseline) echo /Users/jesse/git/superpowers/superpowers ;;
    *)        echo "/tmp/sp-var-$1" ;;
  esac
}
names="baseline z-null g-minimal p-recommended"

cd "$EVALS" || exit 1
for name in $names; do
  root=$(root_for "$name")
  [ -d "$root" ] || { echo "MISSING ROOT $root (build-variant-roots.py)"; exit 1; }
  for r in $(seq 1 "$REPS"); do
    echo "===== variant=$name rep=$r (root=$root) ====="
    SUPERPOWERS_ROOT="$root" bun run quorum run-all \
      --coding-agents "$AGENTS" --scenarios "$SCEN" \
      --out-root "results/bctrl-$name-rep$r" --jobs "$JOBS" 2>&1
  done
done
echo "===== QUORUM BRAINSTORM-CTRL COMPLETE ====="
