# coding-agents: codex,claude,gemini
#
# Deliberately thin: this scenario is a triggering PROBE, not a Gauntlet
# task. Detection (did superpowers:brainstorming load before any
# implementation action, and did the session head down the architectural
# path) is done by hand against the raw session log/rollout per
# logs/2026-07-30-codex-efficiency-fixes.md (Task 12) -- not by an
# automated check here. pre()/post() are structural-only (git-repo,
# bootstrap-installed) so the Gauntlet-Agent's own verdict never encodes
# the behavior under test and can't be mistaken for the real evidence.

pre() {
    git-repo
    bootstrap-installed
}

post() {
    git-repo
}
