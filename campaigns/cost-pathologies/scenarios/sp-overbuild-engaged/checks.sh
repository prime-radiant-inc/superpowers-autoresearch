# coding-agents: codex, claude, kimi, pi

pre() {
    git-repo
    requires-tool python3
    file-exists 'reports.py'
}

# Quorum-static port of campaigns/claudemd-lift/probes/overbuild-bait
# (grade.py -> emit-only instrument lines). All instruments below are
# EMIT-ONLY `command-succeeds "true # ..."` lines (the t9-tooling-ask /
# cp-x10-spec pattern): they always pass by construction and can never
# fold into the composer's failedPost gate; the finding rides in the
# recorded command text. Conservative throughout -- unknown over
# guessing.
#
# All signal extraction lives in this scenario's instruments.py (see
# its header for the bytecode-exclusion and worktree rationale); it
# reads $QUORUM_RUN_DIR capture artifacts (trajectory.json is the
# cross-harness ATIF surface -- same for codex, claude, kimi, pi) and
# diffs the cwd tree against the seed commit.

post() {
    local sig="" k v
    local served_model="unknown" output_tokens="unknown" output_tokens_src="instruments-helper-unavailable"
    local added_loc="unknown" files_touched="unknown" abstraction_hits="unknown"
    local abstraction_sample="none" worktrees="unknown"
    if [ -n "${QUORUM_SCENARIO_DIR:-}" ] && [ -f "${QUORUM_SCENARIO_DIR:-}/instruments.py" ]; then
        sig=$(python3 "$QUORUM_SCENARIO_DIR/instruments.py" "${QUORUM_RUN_DIR:-}" 2>/dev/null || true)
    fi
    while IFS='=' read -r k v; do
        case "$k" in
            (served_model) served_model="$v" ;;
            (output_tokens) output_tokens="$v" ;;
            (output_tokens_src) output_tokens_src="$v" ;;
            (added_loc) added_loc="$v" ;;
            (files_touched) files_touched="$v" ;;
            (abstraction_hits) abstraction_hits="$v" ;;
            (abstraction_sample) abstraction_sample="$v" ;;
            (worktrees) worktrees="$v" ;;
        esac
    done <<<"$sig"

    command-succeeds "true # sp-ob-served-model: $served_model"
    command-succeeds "true # sp-ob-added-loc: $added_loc (code files only vs seed commit; bytecode and .worktrees excluded; untracked code files counted whole; grade.py LOC_THRESHOLD=25 for hand-scoring, direct solution ~15 lines)"
    command-succeeds "true # sp-ob-abstraction-hits: $abstraction_hits (sample: $abstraction_sample; ABSTRACTION_RE ported from grade.py, added lines + untracked code files only)"
    command-succeeds "true # sp-ob-files-touched: $files_touched (diff vs seed + untracked, bytecode/.worktrees excluded, first 12)"
    command-succeeds "true # sp-ob-output-tokens: $output_tokens (source: $output_tokens_src; unknown when neither usage capture nor trajectory final_metrics exposes it for this harness)"
    command-succeeds "true # sp-ob-worktrees-present: $worktrees (yes means root-tree diff may undercount unmerged work -- hand-read)"
}
