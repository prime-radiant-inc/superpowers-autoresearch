# coding-agents: codex

pre() {
    git-repo
    requires-tool python3
    file-exists 'docs/superpowers/plans/job-queue-plan.md'
    file-exists 'pyproject.toml'
    file-exists 'jobqueue/config.py'
    command-succeeds './.venv/bin/pytest -q'
    not file-exists 'jobqueue/worker.py'
    not file-exists 'jobqueue/scheduler.py'
    not file-exists 'jobqueue/api.py'
    not file-exists 'jobqueue/notifier.py'
    not file-exists 'jobqueue/reporter.py'
    not file-exists 'jobqueue/archiver.py'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    file-exists 'jobqueue/worker.py'
    file-exists 'jobqueue/scheduler.py'
    file-exists 'jobqueue/api.py'
    file-exists 'jobqueue/notifier.py'
    file-exists 'jobqueue/reporter.py'
    file-exists 'jobqueue/archiver.py'

    # Item 20 (queue-execution campaign, 2026-08-01), same pattern as
    # cp-x1-edit-existing/checks.sh: report, as its OWN line, whether
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

    # X10 scoring signal: EMIT, never assert, which of the five seeded
    # cross-module consistency defects (seeded-truth-ledger.md) are still
    # present in the final tree. This is a count for the scorer, not a
    # pass/fail gate -- a rep that closes all five is the best case for
    # whichever arm is mounted, not a failure of this scenario. Every
    # command-succeeds call below always exits 0 (grep's own exit status
    # is deliberately discarded via `|| true`); only the recorded command
    # TEXT carries the finding.
    local d1 d2 d3 d4 d5
    d1="absent"
    if [ -f jobqueue/notifier.py ] && [ -f jobqueue/reporter.py ]; then
        if [ "$(grep -oE '^TIMEOUT_SECONDS = [0-9]+' jobqueue/notifier.py 2>/dev/null | awk '{print $3}')" != "$(grep -oE '^TIMEOUT_SECONDS = [0-9]+' jobqueue/reporter.py 2>/dev/null | awk '{print $3}')" ]; then
            d1="present"
        else
            d1="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-1 (TIMEOUT_SECONDS diverges, notifier vs reporter): $d1"

    d2="absent"
    if [ -f jobqueue/worker.py ] && [ -f jobqueue/scheduler.py ]; then
        if grep -q '^RETRY_LIMIT' jobqueue/worker.py 2>/dev/null && grep -q '^MAX_RETRY_ATTEMPTS' jobqueue/scheduler.py 2>/dev/null; then
            d2="present"
        else
            d2="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-2 (retry-cap naming drift, RETRY_LIMIT vs MAX_RETRY_ATTEMPTS): $d2"

    d3="absent"
    if [ -f jobqueue/worker.py ] && [ -f jobqueue/api.py ]; then
        if grep -q 'missing field' jobqueue/worker.py 2>/dev/null && grep -q 'is required' jobqueue/api.py 2>/dev/null; then
            d3="present"
        else
            d3="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-3 (error-message format diverges, JobPayloadError vs InvalidSubmissionError): $d3"

    d4="absent"
    if [ -f jobqueue/scheduler.py ] && [ -f jobqueue/notifier.py ] && [ -f jobqueue/reporter.py ]; then
        if grep -q '"retrying"' jobqueue/scheduler.py 2>/dev/null \
            && ! grep -q '"retrying"' jobqueue/notifier.py 2>/dev/null \
            && ! grep -q '"retrying"' jobqueue/reporter.py 2>/dev/null; then
            d4="present"
        else
            d4="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-4 (retrying status unknown outside scheduler): $d4"

    d5="absent"
    if [ -f jobqueue/worker.py ] && [ -f jobqueue/api.py ]; then
        if [ "$(grep -oE '^MIN_PRIORITY = [0-9]+' jobqueue/worker.py 2>/dev/null | awk '{print $3}')" != "$(grep -oE '^MIN_PRIORITY = [0-9]+' jobqueue/api.py 2>/dev/null | awk '{print $3}')" ]; then
            d5="present"
        else
            d5="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-5 (MIN_PRIORITY boundary diverges, worker vs api): $d5"
}
