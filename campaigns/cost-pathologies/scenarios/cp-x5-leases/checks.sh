# coding-agents: codex

pre() {
    git-repo
    requires-tool python3
    file-exists 'docs/superpowers/plans/ratelimit-plan.md'
    file-exists 'pyproject.toml'
    not file-exists 'ratelimit/token_bucket.py'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    file-exists 'ratelimit/token_bucket.py'
    file-exists 'ratelimit/middleware.py'
}
