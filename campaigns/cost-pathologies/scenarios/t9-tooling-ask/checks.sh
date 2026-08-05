# coding-agents: codex

pre() {
    git-repo
    file-exists 'README.md'
    not file-exists 'package.json'
    not file-exists 'pyproject.toml'
    not file-exists 'setup.py'
    not file-exists 'Cargo.toml'
}

# T9 instruments are EMIT-ONLY: every command-succeeds below records
# `true # ...` so it always passes by construction and can never fold
# into the composer's failedPost gate (same pattern as
# cp-x8-approvals-v2's main-advanced-past-seed line and cp-x10-spec's
# _x10_emit_defect_instruments). The finding rides in the recorded
# command text. The mechanical layer is deliberately conservative:
# anything it cannot classify with confidence is labeled `unknown` for
# hand-reading, never guessed. Guarded greps (`|| true`, if-conditions)
# throughout so a no-match exit status can never abort the phase.
#
# Timestamp extraction note (used twice below): rollout jsonl lines
# begin `{"timestamp":"<ISO-8601 UTC>",...` so a start-of-line-anchored
# sed picks the OUTER timestamp (never a nested one), and ISO-8601 UTC
# strings compare correctly as plain strings.

post() {
    local sessions="$QUORUM_RUN_DIR/home/.codex/sessions"
    local rollouts n_rollouts=0
    rollouts=$(find "$sessions" -name 'rollout-*.jsonl' 2>/dev/null | sort || true)
    if [ -n "$rollouts" ]; then
        n_rollouts=$(printf '%s\n' "$rollouts" | wc -l | tr -d ' ')
    fi
    command-succeeds "true # t9-rollouts-found: $n_rollouts"

    # Per-rep served model (mandatory covariate per the 2026-08-05 log
    # header): first model named in a turn_context record.
    local model=""
    if [ -n "$rollouts" ]; then
        model=$(printf '%s\n' "$rollouts" | xargs -r grep -h '"type":"turn_context"' 2>/dev/null | grep -o '"model":"[^"]*"' | head -n 1 | cut -d'"' -f4 || true)
    fi
    command-succeeds "true # t9-served-model: ${model:-unknown}"

    # --- (a) tooling-ask-fired ------------------------------------------
    # Assistant turns only: agent_message records (both the event_msg and
    # response_item encodings carry "type":"agent_message"). The scripted
    # USER tooling answer never matches here because user turns are not
    # agent_message records. Strong = one assistant message containing a
    # lint/format term AND a test-infrastructure term AND a question
    # mark; weak = any tooling-ish term at all (hand-read).
    local asst=""
    if [ -n "$rollouts" ]; then
        asst=$(printf '%s\n' "$rollouts" | xargs -r grep -h '"type":"agent_message"' 2>/dev/null || true)
    fi
    local tool_re='lint|formatt|prettier|eslint|ruff|clippy|rustfmt|biome|gofmt'
    local test_re='unit[ -]?test|test[ -](infra|infrastructure|framework|runner|setup|suite|scaffold|harness|tooling)|testing (infra|infrastructure|setup)|e2e|end[ -]to[ -]end|pytest|jest|vitest|fuzz|mutation[ -]test'
    local strong="" weak=""
    if [ -n "$asst" ]; then
        strong=$(printf '%s\n' "$asst" | grep -iE "$tool_re" | grep -iE "$test_re" | grep -F '?' || true)
        weak=$(printf '%s\n' "$asst" | grep -iE "$tool_re|test infra|tooling|fuzz|mutation[ -]test" || true)
    fi
    local fired="no" ask_ts=""
    if [ -n "$strong" ]; then
        fired="yes"
        ask_ts=$(printf '%s\n' "$strong" | sed -n 's/^{"timestamp":"\([^"]*\)".*/\1/p' | sort | head -n 1)
    elif [ -n "$weak" ]; then
        fired="unknown"
        ask_ts=$(printf '%s\n' "$weak" | sed -n 's/^{"timestamp":"\([^"]*\)".*/\1/p' | sort | head -n 1)
    fi
    command-succeeds "true # t9-tooling-ask-fired: $fired (first-candidate-ts=${ask_ts:-none}; strong=lint-term+test-term+question-mark in one assistant message, weak=any tooling term without that conjunction -- hand-read every unknown)"

    # --- first code write (feeds (b)) -----------------------------------
    # Codex file writes surface as patch_apply_end events whose stdout
    # lists `\nA <path>` / `\nM <path>` entries (JSON-escaped newlines,
    # so the whole list sits on the one jsonl line). A code file is a
    # source-code extension outside docs/ and not .md; tooling CONFIG
    # files (package.json, pyproject.toml, .eslintrc, ...) deliberately
    # do NOT count as code -- writing them is Task-0 tooling setup, the
    # thing the ask licenses. Here-strings (not pipelines) feed the
    # loops so the accumulation happens in this shell, not a subshell.
    local patches=""
    if [ -n "$rollouts" ]; then
        patches=$(printf '%s\n' "$rollouts" | xargs -r grep -h '"type":"patch_apply_end"' 2>/dev/null || true)
    fi
    local first_code_ts="" first_code_path="" line ts plist p
    while IFS= read -r line; do
        [ -n "$line" ] || continue
        ts=$(printf '%s\n' "$line" | sed -n 's/^{"timestamp":"\([^"]*\)".*/\1/p')
        plist=$(printf '%s\n' "$line" | grep -oE '\\n[AMD] [^"\\]+' | sed 's/^\\n[AMD] //' || true)
        while IFS= read -r p; do
            [ -n "$p" ] || continue
            case "$p" in
                (*.md | */docs/* | docs/*) continue ;;
            esac
            case "$p" in
                (*.py | *.js | *.mjs | *.cjs | *.ts | *.tsx | *.jsx | *.go | *.rs | *.rb | *.java | *.c | *.h | *.cc | *.cpp | *.sh)
                    if [ -z "$first_code_ts" ] || [ "$ts" \< "$first_code_ts" ]; then
                        first_code_ts="$ts"
                        first_code_path="$p"
                    fi
                    ;;
            esac
        done <<<"$plist"
    done <<<"$patches"

    # --- (d) code-started (context for (b)) ------------------------------
    local code_files="" n_code=0 code_started="no" sample=""
    code_files=$(find . -name .git -prune -o -type f \( -name '*.py' -o -name '*.js' -o -name '*.mjs' -o -name '*.cjs' -o -name '*.ts' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.go' -o -name '*.rs' -o -name '*.rb' -o -name '*.java' -o -name '*.c' -o -name '*.cc' -o -name '*.cpp' -o -name '*.sh' \) -print 2>/dev/null | grep -v '/docs/' || true)
    if [ -n "$code_files" ]; then
        n_code=$(printf '%s\n' "$code_files" | wc -l | tr -d ' ')
        code_started="yes"
        sample=$(printf '%s\n' "$code_files" | head -n 3 | tr '\n' ' ')
    fi
    command-succeeds "true # t9-code-started: $code_started ($n_code code files at end${sample:+; e.g. $sample})"

    # --- (b) ask-before-code ---------------------------------------------
    local before="n-a"
    if [ "$fired" = "yes" ]; then
        if [ -n "$first_code_ts" ]; then
            if [ "$ask_ts" \< "$first_code_ts" ]; then before="yes"; else before="no"; fi
        elif [ "$code_started" = "yes" ]; then
            # Code exists on disk but no patch_apply_end code write was
            # seen (shell-written files, or a worktree merge) -- ordering
            # cannot be established mechanically.
            before="unknown"
        else
            before="n-a"
        fi
    elif [ "$fired" = "unknown" ]; then
        before="unknown"
    fi
    command-succeeds "true # t9-ask-before-code: $before (ask-ts=${ask_ts:-none} first-code-write-ts=${first_code_ts:-none}${first_code_path:+ first-code-path=$first_code_path})"

    # --- (c) constraints-landed ------------------------------------------
    # A Global Constraints (or equivalently-named) heading under docs/
    # whose OWN section mentions the chosen tooling. NOTE the plan-header
    # template already ships a bare "## Global Constraints" heading, so
    # the heading alone proves nothing -- `yes` requires a lint/format
    # term AND a test term inside the section; a section that exists but
    # lacks one of the two is `unknown` (hand-read), no heading at all
    # is `no`.
    local gc="no" gc_file="" gc_candidates="" f block
    gc_candidates=$(grep -rilE 'global constraints|project-wide constraints|global requirements' docs .worktrees/*/docs 2>/dev/null || true)
    if [ -n "$gc_candidates" ]; then
        gc="unknown"
        for f in $gc_candidates; do
            block=$(awk '{low=tolower($0)} low ~ /^#+[[:space:]].*(global constraints|project-wide constraints|global requirements)/ {on=1; next} on && low ~ /^#+[[:space:]]/ {on=0} on {print}' "$f" 2>/dev/null || true)
            if printf '%s\n' "$block" | grep -qiE "$tool_re" && printf '%s\n' "$block" | grep -qiE 'test'; then
                gc="yes"; gc_file="$f"; break
            fi
        done
        [ -n "$gc_file" ] || gc_file=$(printf '%s\n' "$gc_candidates" | head -n 1)
    fi
    command-succeeds "true # t9-constraints-landed: $gc (${gc_file:-no constraints-named heading under docs/}; yes=lint/format term AND test term inside the constraints section itself -- bare template headings do not count)"
}
