# coding-agents: codex

pre() {
    git-repo
    file-exists 'plan.md'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
}
