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

    # Item 20 (queue-execution campaign, 2026-08-01): report, as its OWN
    # line, whether `main` advanced past the single setup-seeded commit
    # ("seed scenario fixtures", the sole commit init_repo_from_fixtures
    # makes). logs/2026-07-31-cost-pathologies.md disclosed that this
    # battery's own 16-run sample left 5/16 reps (31%) with `main` never
    # advanced past that seed, including a clean, Gauntlet-approved
    # non-merge (control-rep1). This is a GRADED OUTCOME to observe, not
    # a pass/fail criterion -- item 21's ruling keeps the scenario's
    # existing pass/fail surface unchanged, so this check always PASSES
    # by construction (`true`) and can never fold into the composer's
    # failedPost gate; the finding rides in the recorded command text
    # itself, the same way every command-succeeds call's own args are
    # recorded verbatim in its check record regardless of outcome.
    local main_commits
    main_commits="$(git rev-list --count main 2>/dev/null || echo 0)"
    if [ "$main_commits" -gt 1 ]; then
        command-succeeds "true # main-advanced-past-seed: yes ($main_commits commits on main; seed=1)"
    else
        command-succeeds "true # main-advanced-past-seed: no ($main_commits commit(s) on main -- non-merge, a graded outcome per item 20, not an exclusion)"
    fi
}
