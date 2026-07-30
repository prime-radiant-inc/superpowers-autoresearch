# coding-agents: codex

pre() {
    git-repo
    git-branch feature
}

post() {
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
}
