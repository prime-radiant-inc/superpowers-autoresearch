# coding-agents: codex

pre() {
    git-repo
    requires-tool python3
    file-exists 'docs/superpowers/plans/usage-billing-plan.md'
    file-exists 'pyproject.toml'
    file-contains docs/superpowers/plans/usage-billing-plan.md 'REQ-1'
    not file-exists 'billing/ledger.py'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    file-exists 'billing/ledger.py'
    file-exists 'billing/rate_engine.py'
    file-exists 'billing/invoicer.py'
}
