# coding-agents: codex

pre() {
    git-repo
    file-exists 'server.py'
}

post() {
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
}
