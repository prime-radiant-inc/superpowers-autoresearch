# coding-agents: codex, claude, kimi, pi

pre() {
    git-repo
    requires-tool python3
    file-exists 'docs/metrics-pipeline-design.md'
    file-exists 'pyproject.toml'
    file-exists 'metrics/__init__.py'
    command-succeeds './.venv/bin/pytest -q'
    not file-exists 'docs/superpowers/plans/*'
    not file-exists 'metrics/collector.py'
    not file-exists 'metrics/reporter.py'
    not file-exists 'tests/test_end_to_end.py'
    not file-exists 'data/metrics.jsonl'
}

# P3 walking-skeleton instruments are EMIT-ONLY: every command-succeeds
# below records `true # ...` so it always passes by construction and can
# never fold into the composer's failedPost gate (the t9-tooling-ask /
# sp-adjacent-breakage pattern). The finding rides in the recorded
# command text. All extraction logic lives in this scenario's
# instruments.py (functions-only checks.sh, per the quorum-check linter
# constraint); the mechanical layer is conservative -- anything it
# cannot classify with confidence is `unknown` for hand-reading, never
# guessed.
#
# The only pass/fail gates here are the scenario's own arm-neutral
# completion ACs (modules exist, pytest passes), same as pd-pipeline's.
# The battery's endpoint -- rework after the first integration failure
# -- is a mechanically-assisted hand-read over the emitted ingredients
# (commit timeline, first-e2e ordinals, trap-sighting step, per-file
# re-touch counts), never a gate.

post() {
    file-exists 'metrics/collector.py'
    file-exists 'metrics/reporter.py'
    command-succeeds './.venv/bin/pytest -q'

    # Graded outcome, not a gate (item 20 pattern): did main advance
    # past the single setup-seeded commit.
    local main_commits
    main_commits="$(git rev-list --count main 2>/dev/null || echo 0)"
    if [ "$main_commits" -gt 1 ]; then
        command-succeeds "true # p3-main-advanced-past-seed: yes ($main_commits commits on main; seed=1)"
    else
        command-succeeds "true # p3-main-advanced-past-seed: no ($main_commits commit(s) on main -- non-merge, a graded outcome, not an exclusion)"
    fi

    local sig="" k v
    local served_model="unknown" traj_steps="unknown" dispatches="unknown"
    local first_e2e_step="unknown" first_trap_step="unknown"
    local plan_files="unknown" plan_task_count="unknown"
    local first_task_shape="unknown" first_e2e_task_index="unknown"
    local trap_in_plan="unknown" total_commits="unknown"
    local first_e2e_commit_ordinal="unknown" commit_timeline="unknown"
    local collector_commits="unknown" reporter_commits="unknown"
    local ts_convention="unknown" seq_convention="unknown"
    local probe="unknown" validation_raises="unknown"
    if [ -n "${QUORUM_SCENARIO_DIR:-}" ] && [ -f "${QUORUM_SCENARIO_DIR:-}/instruments.py" ]; then
        sig=$(python3 "$QUORUM_SCENARIO_DIR/instruments.py" "${QUORUM_RUN_DIR:-}" 2>/dev/null || true)
    fi
    while IFS='=' read -r k v; do
        case "$k" in
            (served_model) served_model="$v" ;;
            (traj_steps) traj_steps="$v" ;;
            (dispatches) dispatches="$v" ;;
            (first_e2e_step) first_e2e_step="$v" ;;
            (first_trap_step) first_trap_step="$v" ;;
            (plan_files) plan_files="$v" ;;
            (plan_task_count) plan_task_count="$v" ;;
            (first_task_shape) first_task_shape="$v" ;;
            (first_e2e_task_index) first_e2e_task_index="$v" ;;
            (trap_in_plan) trap_in_plan="$v" ;;
            (total_commits) total_commits="$v" ;;
            (first_e2e_commit_ordinal) first_e2e_commit_ordinal="$v" ;;
            (commit_timeline) commit_timeline="$v" ;;
            (collector_commits) collector_commits="$v" ;;
            (reporter_commits) reporter_commits="$v" ;;
            (ts_convention) ts_convention="$v" ;;
            (seq_convention) seq_convention="$v" ;;
            (probe) probe="$v" ;;
            (validation_raises) validation_raises="$v" ;;
        esac
    done <<<"$sig"

    command-succeeds "true # p3-served-model: $served_model"
    command-succeeds "true # p3-traj-steps: $traj_steps"
    command-succeeds "true # p3-dispatches: $dispatches (Agent/Task tool calls in trajectory)"
    command-succeeds "true # p3-plan-shape: $plan_files file(s), $plan_task_count task(s)"
    command-succeeds "true # p3-first-task-shape: $first_task_shape (slice=first task composes both subsystems or names an end-to-end marker; layer=exactly one subsystem; unknown otherwise -- hand-read unknowns)"
    command-succeeds "true # p3-first-e2e-task-index: $first_e2e_task_index (lowest plan task composing both subsystems or naming an e2e marker)"
    command-succeeds "true # p3-trap-in-plan: $trap_in_plan"
    command-succeeds "true # p3-first-e2e-run-step: $first_e2e_step (first trajectory step naming test_end_to_end)"
    command-succeeds "true # p3-trap-sighting-step: $first_trap_step (first trajectory step mentioning SampleStreamError in a call, observation, or narration -- includes innocent mentions while writing reporter code; hand-read for the failure moment)"
    command-succeeds "true # p3-total-commits: $total_commits"
    command-succeeds "true # p3-first-e2e-commit-ordinal: $first_e2e_commit_ordinal (first commit touching an e2e-named test file)"
    command-succeeds "true # p3-commit-timeline: $commit_timeline"
    command-succeeds "true # p3-collector-commits: $collector_commits"
    command-succeeds "true # p3-reporter-commits: $reporter_commits"
    command-succeeds "true # p3-ts-convention: $ts_convention (what a live Collector actually writes in the final tree)"
    command-succeeds "true # p3-seq-convention: $seq_convention (per-metric=[1,1,2] vs global=[1,2,3] over cpu,mem,cpu)"
    command-succeeds "true # p3-trap-resolved: $probe (live probe: real Collector records cpu/mem alternating, then generate_report over that file -- ok means the composed pipeline works end-to-end)"
    command-succeeds "true # p3-validation-retained: $validation_raises raise-SampleStreamError site(s) in final reporter.py (0 would mean validation was dropped to force composition -- hand-read)"
}
