# coding-agents: codex

pre() {
    git-repo
    requires-tool node
    file-exists 'docs/superpowers/plans/checkout-plan.md'
    file-exists 'src/format.js'
    file-exists 'src/pricing.js'
    not file-exists 'src/utils/discountLookup.js'
    not file-contains src/pricing.js 'DISCOUNT_TABLE'
    command-succeeds 'npm test'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    file-contains src/pricing.js 'applyDiscount'
}
