# coding-agents: codex, claude, kimi, pi

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
    # Session-record existence, per harness (the codex-only form failed
    # uniformly on kimi/pi reps 2026-08-07 and polluted `final`):
    case "${QUORUM_CODING_AGENT:-codex}" in
        codex) file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl" ;;
        claude) file-exists "$QUORUM_RUN_DIR/home/.claude/projects/**/*.jsonl" ;;
        *) file-exists "$QUORUM_RUN_DIR/trajectory.json" ;;
    esac
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
    local d1 d2 d3 d4 d5 jq
    # Scan the tree the work actually lives in: a rep cut before its
    # worktree merged back leaves the root jobqueue/ without the modules,
    # and grepping that tree reads every defect as gone (vacuity — this
    # scored a 0/5 rep as 5/5 once). Prefer the root only when it has the
    # modules; otherwise fall back to the SDD worktree.
    jq="jobqueue"
    if [ ! -f jobqueue/worker.py ]; then
        local wt
        for wt in .worktrees/*/jobqueue; do
            if [ -f "$wt/worker.py" ]; then jq="$wt"; break; fi
        done
    fi
    command-succeeds "true # seeded-defect-scan tree: $jq"
    d1="not-built"
    if [ -f "$jq"/notifier.py ] && [ -f "$jq"/reporter.py ]; then
        if [ "$(grep -oE '^TIMEOUT_SECONDS = [0-9]+' "$jq"/notifier.py 2>/dev/null | awk '{print $3}')" != "$(grep -oE '^TIMEOUT_SECONDS = [0-9]+' "$jq"/reporter.py 2>/dev/null | awk '{print $3}')" ]; then
            d1="present"
        else
            d1="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-1 (TIMEOUT_SECONDS diverges, notifier vs reporter): $d1"

    d2="not-built"
    if [ -f "$jq"/worker.py ] && [ -f "$jq"/scheduler.py ]; then
        if grep -q '^RETRY_LIMIT' "$jq"/worker.py 2>/dev/null && grep -q '^MAX_RETRY_ATTEMPTS' "$jq"/scheduler.py 2>/dev/null; then
            d2="present"
        else
            d2="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-2 (retry-cap naming drift, RETRY_LIMIT vs MAX_RETRY_ATTEMPTS): $d2"

    d3="not-built"
    if [ -f "$jq"/worker.py ] && [ -f "$jq"/api.py ]; then
        if grep -q 'missing field' "$jq"/worker.py 2>/dev/null && grep -q 'is required' "$jq"/api.py 2>/dev/null; then
            d3="present"
        else
            d3="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-3 (error-message format diverges, JobPayloadError vs InvalidSubmissionError): $d3"

    d4="not-built"
    if [ -f "$jq"/scheduler.py ] && [ -f "$jq"/notifier.py ] && [ -f "$jq"/reporter.py ]; then
        if grep -q '"retrying"' "$jq"/scheduler.py 2>/dev/null \
            && ! grep -q '"retrying"' "$jq"/notifier.py 2>/dev/null \
            && ! grep -q '"retrying"' "$jq"/reporter.py 2>/dev/null; then
            d4="present"
        else
            d4="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-4 (retrying status unknown outside scheduler): $d4"

    d5="not-built"
    if [ -f "$jq"/worker.py ] && [ -f "$jq"/api.py ]; then
        if [ "$(grep -oE '^MIN_PRIORITY = [0-9]+' "$jq"/worker.py 2>/dev/null | awk '{print $3}')" != "$(grep -oE '^MIN_PRIORITY = [0-9]+' "$jq"/api.py 2>/dev/null | awk '{print $3}')" ]; then
            d5="present"
        else
            d5="resolved-or-absent"
        fi
    fi
    command-succeeds "true # seeded-defect-5 (MIN_PRIORITY boundary diverges, worker vs api): $d5"
}
