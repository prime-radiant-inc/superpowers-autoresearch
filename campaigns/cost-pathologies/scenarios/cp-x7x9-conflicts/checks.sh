# coding-agents: codex

pre() {
    git-repo
    requires-tool python3
    file-exists 'docs/superpowers/plans/log-migration-plan.md'
    file-exists 'legacylib/legacy_store.py'
    command-succeeds './.venv/bin/pytest -q'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
}
