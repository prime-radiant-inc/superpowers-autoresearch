# coding-agents: codex

pre() {
    git-repo
    requires-tool node
    file-exists 'docs/superpowers/plans/util-bugfix-plan.md'
    file-exists 'package.json'
    file-contains docs/superpowers/plans/util-bugfix-plan.md 'Task 12'
    not command-succeeds 'npm test'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    command-succeeds 'npm test'

    # Item 20 (queue-execution campaign, 2026-08-01), same pattern as
    # cp-x1-wavecap/checks.sh and cp-x1-edit-existing/checks.sh: report, as
    # its OWN line, whether `main` advanced past the single setup-seeded
    # commit ("seed scenario fixtures", the sole commit
    # init_repo_from_fixtures makes). This is a GRADED OUTCOME to observe,
    # not a pass/fail criterion, so this check always PASSES by
    # construction (`true`) and can never fold into the composer's
    # failedPost gate; the finding rides in the recorded command text
    # itself.
    local main_commits
    main_commits="$(git rev-list --count main 2>/dev/null || echo 0)"
    if [ "$main_commits" -gt 1 ]; then
        command-succeeds "true # main-advanced-past-seed: yes ($main_commits commits on main; seed=1)"
    else
        command-succeeds "true # main-advanced-past-seed: no ($main_commits commit(s) on main -- non-merge, a graded outcome per item 20, not an exclusion)"
    fi
}
