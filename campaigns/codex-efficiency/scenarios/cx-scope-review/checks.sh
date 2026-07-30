# coding-agents: codex

# Deliberately minimal (scenario-authoring lesson from E2/E4, ledger): a
# scenario's deterministic post-checks must not assert a behavioral
# choice the experiment itself measures. cx-scope-review's whole purpose
# is to observe whether/how many reviewer sub-agents get dispatched and
# how re-review scope narrows after the mid-session fix request -- a
# `tool-called Agent` check here would bias exactly what score_e5.py
# measures.

pre() {
    git-repo
    git-branch feature
}

post() {
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
}
