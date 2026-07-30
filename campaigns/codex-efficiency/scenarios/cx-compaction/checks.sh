# coding-agents: codex

# Deliberately minimal (scenario-authoring lesson from E2/E4, ledger): a
# scenario's deterministic post-checks must not assert a behavioral choice
# the experiment itself measures. cx-compaction's whole purpose is to
# observe whether/how the controller re-reads skills and preserves
# spawn-hygiene across a forced compaction -- a `tool-called Agent` or
# skill-read check here would bias exactly what score_e6.py measures.

pre() {
    git-repo
    file-exists 'plan.md'
}

post() {
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
}
