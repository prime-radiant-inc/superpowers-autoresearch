# coding-agents: codex, claude, kimi, pi

pre() {
    git-repo
    requires-tool python3
    file-exists 'docs/superpowers/plans/job-queue-plan.md'
    file-exists 'docs/superpowers/specs/job-queue-spec.md'
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

# Emits every seeded-defect-presence and spec-resolution instrument line
# for the CURRENT directory's tree (called by post(), against the
# checked-out session tree). Split out of post() -- same reason and same
# pattern as pd-pipeline/checks.sh's `_pd_emit_plan_instruments` -- so it
# can be exercised directly by validate_cp_x10_spec.py's regression tests
# with only the ONE harness primitive it depends on (`command-succeeds`)
# stubbed, rather than the full quorum primitive set post() otherwise
# needs (git-repo, file-exists, check-transcript, ...).
#
# Every command-succeeds call below always exits 0 (grep's own exit
# status is deliberately discarded via `|| true` or default values);
# only the recorded command TEXT carries the finding, for the composer's
# scorers to parse. None of these are pass/fail gates.
_x10_emit_defect_instruments() {
    # -- seeded-defect PRESENCE (unchanged from cp-x10-consistency's own
    # checks.sh): is each of the five seeded plan-induced divergences
    # still present in the tree, per seeded-truth-ledger.md's detection
    # recipes. --
    local d1 d2 d3 d4 d5 jq
    # Scan the tree the work actually lives in (ported from
    # cp-x10-consistency after the stale-tree vacuity artifact): a rep
    # cut before its worktree merged back leaves the root jobqueue/
    # empty and grepping it reads every defect as gone.
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

    # -- spec-resolution instruments (new in cp-x10-spec): does the
    # final tree match fixtures/docs/superpowers/specs/job-queue-spec.md's
    # stated resolution for each seeded pair -- not merely "no longer
    # diverges from its sibling task," but "now agrees with the spec's
    # own value/name/vocabulary." See seeded-truth-ledger.md's "Spec
    # resolutions" table for the expected amendment per defect. Each
    # line is `yes` (fully matches spec), `partial` (moved toward the
    # spec but not all the way -- e.g. only one of two sides amended,
    # or unified to a value that matches neither the spec nor either
    # original task), or `no` (spec's resolution not adopted; includes
    # the unresolved, still-seeded tree). Emit-only, never a gate. --

    local r1="no" n_val r_val
    if [ -f jobqueue/notifier.py ] && [ -f jobqueue/reporter.py ]; then
        n_val="$(grep -oE '^TIMEOUT_SECONDS = [0-9]+' jobqueue/notifier.py 2>/dev/null | awk '{print $3}')"
        r_val="$(grep -oE '^TIMEOUT_SECONDS = [0-9]+' jobqueue/reporter.py 2>/dev/null | awk '{print $3}')"
        if [ "$n_val" = "30" ] && [ "$r_val" = "30" ]; then
            r1="yes"
        elif [ "$n_val" = "30" ] || [ "$r_val" = "30" ]; then
            r1="partial"
        elif [ -n "$n_val" ] && [ "$n_val" = "$r_val" ]; then
            r1="partial"
        fi
    fi
    command-succeeds "true # spec-resolution-1: $r1 (TIMEOUT_SECONDS unified to spec value 30, notifier=$n_val reporter=$r_val)"

    local r2="no" has_new="no" has_old="no" retry_val
    if [ -f jobqueue/scheduler.py ]; then
        grep -q '^RETRY_LIMIT' jobqueue/scheduler.py 2>/dev/null && has_new="yes"
        grep -q '^MAX_RETRY_ATTEMPTS' jobqueue/scheduler.py 2>/dev/null && has_old="yes"
        if [ "$has_new" = "yes" ] && [ "$has_old" = "no" ]; then
            retry_val="$(grep -oE '^RETRY_LIMIT[[:space:]]*=[[:space:]]*[0-9]+' jobqueue/scheduler.py 2>/dev/null | grep -oE '[0-9]+$')"
            if [ "$retry_val" = "4" ]; then
                r2="yes"
            else
                r2="partial"
            fi
        elif [ "$has_new" = "yes" ] && [ "$has_old" = "yes" ]; then
            r2="partial"
        fi
    fi
    command-succeeds "true # spec-resolution-2: $r2 (retry-cap renamed to spec name RETRY_LIMIT in scheduler)"

    local r3="no" has_class="no" has_msg="no"
    if [ -f jobqueue/api.py ]; then
        grep -q 'JobPayloadError' jobqueue/api.py 2>/dev/null && has_class="yes"
        grep -q 'missing field' jobqueue/api.py 2>/dev/null && has_msg="yes"
        if [ "$has_class" = "yes" ] && [ "$has_msg" = "yes" ]; then
            r3="yes"
        elif [ "$has_class" = "yes" ] || [ "$has_msg" = "yes" ]; then
            r3="partial"
        fi
    fi
    command-succeeds "true # spec-resolution-3: $r3 (api validation error unified to spec class/message JobPayloadError)"

    local r4="no" notifier_has="no" reporter_has="no"
    if [ -f jobqueue/notifier.py ] && [ -f jobqueue/reporter.py ]; then
        grep -q '"retrying"' jobqueue/notifier.py 2>/dev/null && notifier_has="yes"
        grep -q '"retrying"' jobqueue/reporter.py 2>/dev/null && reporter_has="yes"
        if [ "$notifier_has" = "yes" ] && [ "$reporter_has" = "yes" ]; then
            r4="yes"
        elif [ "$notifier_has" = "yes" ] || [ "$reporter_has" = "yes" ]; then
            r4="partial"
        fi
    fi
    command-succeeds "true # spec-resolution-4: $r4 (retrying status handled in both notifier and reporter per spec vocabulary)"

    local r5="no" w_val a_val
    if [ -f jobqueue/worker.py ] && [ -f jobqueue/api.py ]; then
        w_val="$(grep -oE '^MIN_PRIORITY = [0-9]+' jobqueue/worker.py 2>/dev/null | awk '{print $3}')"
        a_val="$(grep -oE '^MIN_PRIORITY = [0-9]+' jobqueue/api.py 2>/dev/null | awk '{print $3}')"
        if [ "$w_val" = "1" ] && [ "$a_val" = "1" ]; then
            r5="yes"
        elif [ "$w_val" = "1" ] || [ "$a_val" = "1" ]; then
            r5="partial"
        elif [ -n "$w_val" ] && [ "$w_val" = "$a_val" ]; then
            r5="partial"
        fi
    fi
    command-succeeds "true # spec-resolution-5: $r5 (MIN_PRIORITY unified to spec value 1, worker=$w_val api=$a_val)"
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

    # X10 scoring signal (seeded-defect presence) + P2' scoring signal
    # (spec-resolution disposition) -- see _x10_emit_defect_instruments's
    # own comment for detail. Both are EMIT-only, never a pass/fail gate.
    _x10_emit_defect_instruments
}
