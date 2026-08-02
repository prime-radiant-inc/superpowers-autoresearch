# coding-agents: codex

pre() {
    git-repo
    requires-tool node
    file-exists 'docs/superpowers/plans/spend-summary-reorg-plan.md'
    file-exists 'src/report.js'
    not file-exists 'src/reports/index.js'
    command-succeeds 'npm test'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    file-exists 'src/reports/index.js'
    file-contains src/reports/index.js 'parseEntry'
    file-contains src/reports/index.js 'aggregateByCategory'
    file-contains src/reports/index.js 'formatSummary'
    file-contains src/reports/index.js 'formatSummaryCsv'
    file-contains src/reports/index.js 'generateReport'
    command-succeeds 'npm test'

    # Item 20 (queue-execution campaign, 2026-08-01), same pattern as
    # cp-x1-edit-existing/checks.sh, cp-x1-wavecap/checks.sh, and
    # cp-x8-approvals-v2/checks.sh: report, as its OWN line, whether
    # `main` advanced past the single setup-seeded commit ("seed scenario
    # fixtures", the sole commit init_repo_from_fixtures makes). This is a
    # GRADED OUTCOME to observe, not a pass/fail criterion, so this check
    # always PASSES by construction (`true`) and can never fold into the
    # composer's failedPost gate; the finding rides in the recorded
    # command text itself.
    local main_commits
    main_commits="$(git rev-list --count main 2>/dev/null || echo 0)"
    if [ "$main_commits" -gt 1 ]; then
        command-succeeds "true # main-advanced-past-seed: yes ($main_commits commits on main; seed=1)"
    else
        command-succeeds "true # main-advanced-past-seed: no ($main_commits commit(s) on main -- non-merge, a graded outcome per item 20, not an exclusion)"
    fi
}
