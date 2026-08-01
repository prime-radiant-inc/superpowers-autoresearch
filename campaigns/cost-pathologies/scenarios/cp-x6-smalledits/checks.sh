# coding-agents: codex

pre() {
    git-repo
    requires-tool node
    file-exists 'BUGS.md'
    not command-succeeds 'npm test'
}

post() {
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    command-succeeds 'npm test'
}
