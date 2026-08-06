# coding-agents: codex, claude

pre() {
    git-repo
    requires-tool python3
    file-exists 'docs/superpowers/plans/dispatch-envelope-plan.md'
    file-exists 'pyproject.toml'
    not file-exists 'dispatchqueue/envelope.py'
    not file-exists 'dispatchqueue/queue.py'
    not file-exists 'dispatchqueue/eventlog.py'
    not file-exists 'dispatchqueue/workers.py'
    not file-exists 'dispatchqueue/replay.py'
    not file-exists 'dispatchqueue/dispatch.py'
}

# K1' instruments are EMIT-ONLY: every command-succeeds below records
# `true # ...` so it always passes by construction and can never fold
# into the composer's failedPost gate (the t9-tooling-ask /
# sp-overbuild-bait pattern). The finding rides in the recorded command
# text; consistency is NEVER a graded AC (arm-neutral by construction —
# the completion gates above the instruments are file-existence only).
# All signal extraction lives in this scenario's instruments.py: tree
# classification of the Task 1 wire-format decision (WIRE_FORMAT
# constant, marker fallback) and of the two consumer files (Task 3
# eventlog.py, Task 5 replay.py; `delegates` = imports envelope's
# helpers, consistent by construction), plus trajectory.json (ATIF,
# cross-harness for codex and claude) handoff.md read/write counts and
# the decision-token-in-handoff-write signal. Conservative throughout:
# unknown over guessing; hand-read every unknown. NOTE the handoff
# write counter takes any tool call whose argument blob names
# handoff.md and looks like a write — a ledger edit that merely
# mentions handoff.md can overcount, so hand-read the write blobs
# before crediting decision_in_handoff on a contested rep.

post() {
    check-transcript tool-called Agent
    file-exists 'dispatchqueue/envelope.py'
    file-exists 'dispatchqueue/queue.py'
    file-exists 'dispatchqueue/eventlog.py'
    file-exists 'dispatchqueue/workers.py'
    file-exists 'dispatchqueue/replay.py'
    file-exists 'dispatchqueue/dispatch.py'

    local sig="" k v
    local served_model="unknown"
    local t1_format="unknown" t1_src="none" t1_where="instruments-helper-unavailable"
    local t3_format="unknown" t3_where="instruments-helper-unavailable"
    local t5_format="unknown" t5_where="instruments-helper-unavailable"
    local consist_t3="unknown" consist_t5="unknown"
    local handoff_writes="unknown" handoff_reads="unknown" handoff_mentions="unknown"
    local decision_in_handoff="unknown"
    if [ -n "${QUORUM_SCENARIO_DIR:-}" ] && [ -f "${QUORUM_SCENARIO_DIR:-}/instruments.py" ]; then
        sig=$(python3 "$QUORUM_SCENARIO_DIR/instruments.py" "${QUORUM_RUN_DIR:-}" 2>/dev/null || true)
    fi
    while IFS='=' read -r k v; do
        case "$k" in
            (served_model) served_model="$v" ;;
            (t1_format) t1_format="$v" ;;
            (t1_src) t1_src="$v" ;;
            (t1_where) t1_where="$v" ;;
            (t3_format) t3_format="$v" ;;
            (t3_where) t3_where="$v" ;;
            (t5_format) t5_format="$v" ;;
            (t5_where) t5_where="$v" ;;
            (consist_t3) consist_t3="$v" ;;
            (consist_t5) consist_t5="$v" ;;
            (handoff_writes) handoff_writes="$v" ;;
            (handoff_reads) handoff_reads="$v" ;;
            (handoff_mentions) handoff_mentions="$v" ;;
            (decision_in_handoff) decision_in_handoff="$v" ;;
        esac
    done <<<"$sig"

    # The handoff file lives in the SDD plan workspace, which SDD
    # deletes at finish -- expected absent from the final tree (the K1
    # verdict's lesson); presence usually means a truncated session.
    local handoff_in_tree="no" handoff_path=""
    handoff_path=$(find . -name .git -prune -o -type f -name 'handoff.md' -print 2>/dev/null | head -n 1 || true)
    if [ -n "$handoff_path" ]; then
        handoff_in_tree="yes"
    fi

    command-succeeds "true # k1p-served-model: $served_model"
    command-succeeds "true # k1p-task1-format: $t1_format (src=$t1_src; $t1_where)"
    command-succeeds "true # k1p-task3-format: $t3_format ($t3_where)"
    command-succeeds "true # k1p-task5-format: $t5_format ($t5_where)"
    command-succeeds "true # k1p-consistency-t3: $consist_t3 (yes = matches Task 1's format or delegates to envelope helpers; graded outcome, never an AC)"
    command-succeeds "true # k1p-consistency-t5: $consist_t5 (yes = matches Task 1's format or delegates to envelope helpers; graded outcome, never an AC)"
    command-succeeds "true # k1p-handoff-writes: $handoff_writes (reads=$handoff_reads mentions=$handoff_mentions; from trajectory tool calls -- SDD deletes the workspace, so the tree cannot carry this)"
    command-succeeds "true # k1p-handoff-in-tree: $handoff_in_tree (${handoff_path:-not found}; expected no on a finished session)"
    command-succeeds "true # k1p-decision-in-handoff: $decision_in_handoff (yes = a handoff.md write blob carries a format token jsonl/lp32/json-lines/length-prefix; n-a = no handoff writes, the base2 shape)"
}
