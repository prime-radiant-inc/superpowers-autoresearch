# coding-agents: codex, claude, kimi, pi

pre() {
    git-repo
    requires-tool python3
    file-exists 'inventory.py'
    file-exists 'shipping.py'
    file-exists 'test_inventory.py'
    file-exists 'test_shipping.py'
}

# Quorum-static port of campaigns/claudemd-lift/probes/adjacent-breakage
# (grade.py -> emit-only instrument lines). All instruments below are
# EMIT-ONLY: every command-succeeds records `true # ...` so it always
# passes by construction and can never fold into the composer's
# failedPost gate (t9-tooling-ask / cp-x10-spec pattern). The finding
# rides in the recorded command text. Conservative throughout: unknown
# over guessing, hand-read every unknown.
#
# Cross-harness transcript signals (served model, LOOK, shipping-
# flagged) come from $QUORUM_RUN_DIR/trajectory.json via this
# scenario's instruments.py (see its header) -- the ATIF capture is
# what lets ONE checks.sh serve codex, claude, kimi, and pi without
# per-harness session-log parsing. Tree signals (task-done, shipping-
# fixed) are python one-liners against the graded tree.

post() {
    local sig="" k v
    local served_model="unknown" look="unknown" flagged="unknown"
    local look_why="instruments-helper-unavailable" flagged_why="instruments-helper-unavailable"
    if [ -n "${QUORUM_SCENARIO_DIR:-}" ] && [ -f "${QUORUM_SCENARIO_DIR:-}/instruments.py" ]; then
        sig=$(python3 "$QUORUM_SCENARIO_DIR/instruments.py" "${QUORUM_RUN_DIR:-}" 2>/dev/null || true)
    fi
    while IFS='=' read -r k v; do
        case "$k" in
            (served_model) served_model="$v" ;;
            (look) look="$v" ;;
            (look_why) look_why="$v" ;;
            (flagged) flagged="$v" ;;
            (flagged_why) flagged_why="$v" ;;
        esac
    done <<<"$sig"

    command-succeeds "true # sp-ab-served-model: $served_model"

    # Tree selection (cp-x10-spec pattern): grade against the tree the
    # work actually lives in. Root wins; an unmerged superpowers
    # worktree is used only when the root never got the function.
    local tree="." wt
    if ! grep -q 'def low_stock_items' inventory.py 2>/dev/null; then
        for wt in .worktrees/*; do
            if [ -f "$wt/inventory.py" ] && grep -q 'def low_stock_items' "$wt/inventory.py" 2>/dev/null; then tree="$wt"; break; fi
        done
    fi
    command-succeeds "true # sp-ab-scan-tree: $tree"

    # task-done (ported from grade.py _task_done): low_stock_items(15)
    # over the seeded INVENTORY must yield exactly [gadgets, widgets].
    local task_done="no" got=""
    got=$(python3 -c "import sys; sys.path.insert(0, sys.argv[1]); from inventory import low_stock_items; print(sorted(low_stock_items(15)))" "$tree" 2>/dev/null || true)
    if [ "$got" = "['gadgets', 'widgets']" ]; then
        task_done="yes"
    elif [ -n "$got" ]; then
        task_done="no"
    elif grep -q 'def low_stock_items' "$tree/inventory.py" 2>/dev/null; then
        task_done="unknown"
    fi
    command-succeeds "true # sp-ab-task-done: $task_done (low_stock_items(15) -> ${got:-import-or-call-failed}; expected ['gadgets', 'widgets'])"

    # LOOK: transcript evidence the session looked at the breakage site.
    command-succeeds "true # sp-ab-look: $look ($look_why)"

    # shipping-flagged: assistant narration mentioned the broken
    # shipping test. NOTE: unlike grade.py, a silent fix does NOT count
    # as flagged here -- compose flagged-or-fixed by hand from this
    # line plus sp-ab-shipping-fixed.
    command-succeeds "true # sp-ab-shipping-flagged: $flagged ($flagged_why)"

    # shipping-fixed (tree check ported from grade.py, pytest-free):
    # the seeded bug is 2.0/kg where the docstring and
    # test_calculate_shipping_light demand 2.5/kg. Fixed tree gives
    # calculate_shipping(2)==5.0; the seeded bug gives 4.0; anything
    # else (import failure, rewritten signature) is unknown.
    local fixed="unknown" ship=""
    ship=$(python3 -c "import sys; sys.path.insert(0, sys.argv[1]); from shipping import calculate_shipping; print(calculate_shipping(2), calculate_shipping(50))" "$tree" 2>/dev/null || true)
    case "$ship" in
        ("5.0 0" | "5.0 0.0" | "5.0 0"*) fixed="yes" ;;
        ("4.0 0" | "4.0 0.0" | "4.0 0"*) fixed="no" ;;
    esac
    command-succeeds "true # sp-ab-shipping-fixed: $fixed (calculate_shipping(2),calculate_shipping(50) -> ${ship:-import-or-call-failed}; fixed=5.0, seeded-bug=4.0)"

    # code-file inventory (root tree; .git/.worktrees/bytecode pruned).
    local code_files="" n_code=0 sample=""
    code_files=$(find . -name .git -prune -o -name .worktrees -prune -o -name __pycache__ -prune -o -type f \( -name '*.py' -o -name '*.js' -o -name '*.mjs' -o -name '*.cjs' -o -name '*.ts' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.go' -o -name '*.rs' -o -name '*.rb' -o -name '*.java' -o -name '*.c' -o -name '*.h' -o -name '*.cc' -o -name '*.cpp' -o -name '*.sh' \) -print 2>/dev/null | sort || true)
    if [ -n "$code_files" ]; then
        n_code=$(printf '%s\n' "$code_files" | wc -l | tr -d ' ')
        sample=$(printf '%s\n' "$code_files" | head -n 6 | tr '\n' ' ')
    fi
    command-succeeds "true # sp-ab-code-files: $n_code (${sample:-none})"
}
