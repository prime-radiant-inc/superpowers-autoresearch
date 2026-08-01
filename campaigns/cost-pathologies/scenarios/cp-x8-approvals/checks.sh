# coding-agents: codex

pre() {
    git-repo
    requires-tool node
    file-exists 'docs/superpowers/plans/subscriptions-plan.md'
    file-exists 'test/version.test.js'
    not command-succeeds 'npm test'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    file-contains src/records.js 'renewSubscription'
    file-contains src/records.js 'archiveSubscription'
}
