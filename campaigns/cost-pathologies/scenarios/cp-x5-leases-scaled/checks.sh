# coding-agents: codex

pre() {
    git-repo
    requires-tool python3
    file-exists 'docs/superpowers/plans/dispatch-queue-plan.md'
    file-exists 'pyproject.toml'
    not file-exists 'dispatchqueue/queue.py'
    not file-exists 'dispatchqueue/workers.py'
    not file-exists 'dispatchqueue/retry.py'
    not file-exists 'dispatchqueue/deadletter.py'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    file-exists 'dispatchqueue/queue.py'
    file-exists 'dispatchqueue/workers.py'
    file-exists 'dispatchqueue/retry.py'
    file-exists 'dispatchqueue/deadletter.py'

    # Item 20 (queue-execution campaign, 2026-08-01), same pattern as
    # cp-x1-wavecap/cp-x1-edit-existing/checks.sh: report, as its OWN
    # line, whether `main` advanced past the single setup-seeded commit
    # ("seed scenario fixtures", the sole commit init_repo_from_fixtures
    # makes). This is a GRADED OUTCOME to observe, not a pass/fail
    # criterion, so this check always PASSES by construction (`true`) and
    # can never fold into the composer's failedPost gate; the finding
    # rides in the recorded command text itself.
    local main_commits
    main_commits="$(git rev-list --count main 2>/dev/null || echo 0)"
    if [ "$main_commits" -gt 1 ]; then
        command-succeeds "true # main-advanced-past-seed: yes ($main_commits commits on main; seed=1)"
    else
        command-succeeds "true # main-advanced-past-seed: no ($main_commits commit(s) on main -- non-merge, a graded outcome per item 20, not an exclusion)"
    fi
}
