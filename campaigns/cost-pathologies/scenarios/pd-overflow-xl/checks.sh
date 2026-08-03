# coding-agents: codex

# Helper functions for the plan-shape / task-shape observables below.
# No plan is seeded (pre() asserts none exists), so these discover
# whatever the session produced under docs/superpowers/plans/ -- a
# single file (today's writing-plans default) or several files however
# split (a wrapping per-task directory, or files side by side). Nothing
# in this fixture mandates a directory convention -- these helpers stay
# generic so whatever shape a future arm produces still yields a
# meaningful observable.
#
# Adapted from scenarios/pd-overflow/checks.sh (plan-decomposition
# campaign, overflow-probe expansion) for this scenario's wider module
# list -- 32 modules across three subsystems instead of 16 in one -- see
# probe-design-notes.md for what changed and why. The helper functions
# themselves are unchanged; only the module lists these check functions
# and the P2 coherence block below reference are wider.

_pd_plan_files() {
    find docs/superpowers/plans -type f 2>/dev/null | sort
}

# Count "### Task N" / "# Task N" style headers across the given files.
# Falls back to counting filenames that look like a per-task file, and
# finally to (file count - 1) on the assumption of one non-task manifest
# file, so the observable stays meaningful even off this fixture's own
# constructed conventions.
_pd_task_count() {
    local files=("$@")
    local count
    count="$(grep -hcE '^#+[[:space:]]*Task[[:space:]]' "${files[@]}" 2>/dev/null | awk '{s+=$1} END {print s+0}')"
    if [ "${count:-0}" -gt 0 ]; then
        echo "$count"
        return
    fi
    count="$(printf '%s\n' "${files[@]}" | grep -ic 'task' || true)"
    if [ "${count:-0}" -gt 0 ]; then
        echo "$count"
        return
    fi
    local n="${#files[@]}"
    if [ "$n" -gt 1 ]; then
        echo "$((n - 1))"
    else
        echo "$n"
    fi
}

# Disposition of the six orders/settings.py micro-edits SPEC.md asks
# for (notify-retries, return-window-days, report-timezone,
# archive-grace, audit-log-retention, reconciliation-tolerance): for
# each Task-header boundary (monolithic file) or
# each file (multiple files, one task per file assumed), does that task
# touch settings.py alone (a dedicated micro-task) or alongside another
# orders/*.py module file (folded into that module's own task)? Prints
# "<total> <dedicated>".
#
# `have_task` gates every flush so that plan text preceding the first
# Task header -- a Global Constraints preamble in a monolithic file, or
# a manifest/constraints file sorted ahead of any task file in a
# directory -- is never itself counted as a task, even if it happens to
# mention orders/settings.py in passing.
_pd_settings_disposition() {
    awk '
        function flush() {
            if (have_task && touched) {
                total++
                if (others == 0) dedicated++
            }
        }
        function reset() { touched = 0; others = 0; delete seen }
        BEGIN { total = 0; dedicated = 0; have_task = 0; reset() }
        FNR == 1 { flush(); reset() }
        /^#+[[:space:]]*Task[[:space:]]/ { flush(); reset(); have_task = 1 }
        /orders\/settings\.py/ { touched = 1 }
        {
            line = $0
            while (match(line, /orders\/[a-zA-Z_]+\.py/)) {
                ref = substr(line, RSTART, RLENGTH)
                line = substr(line, RSTART + RLENGTH)
                if (ref != "orders/settings.py" && !(ref in seen)) {
                    seen[ref] = 1
                    others++
                }
            }
        }
        END { flush(); print total, dedicated }
    ' "$@" 2>/dev/null
}

# Tolerant MAX_LINE_ITEMS extraction (plan-decomposition campaign,
# 2026-08-03 T4 correction). Adapted from scenarios/pd-pipeline/checks.sh
# -- see that file's own docstring for the full rationale. The original
# extraction (`^MAX_LINE_ITEMS[[:space:]]*=[[:space:]]*[0-9]+`) only saw a
# bare assignment -- real battery reps reported the constant "absent" in
# modules that actually wrote `MAX_LINE_ITEMS: int = 12` (a type-annotated
# assignment), fabricating a requirement-loss finding later withdrawn once
# the tree was hand-read. Tolerates three shapes, in order:
#   (a) bare assignment:      MAX_LINE_ITEMS = 12
#   (b) annotated assignment: MAX_LINE_ITEMS: int = 12
#   (c) import-reference:     from orders.validation import MAX_LINE_ITEMS
#       -- resolved ONE hop into the referenced module's own file (no
#       further import chasing) and reported as "import(<value>)", e.g.
#       "import(12)", so a scorer can tell direct-vs-inherited apart while
#       still recovering the effective value.
# Absent (echoes "absent") if none of the three match or FILE doesn't
# exist -- this is an EMIT, never a pass/fail gate; see callers.
_pd_mli_direct() {
    local file="$1"
    [ -f "$file" ] || return 0
    # `|| true`: under `set -o pipefail` (this scenario's harness scripts
    # all set it), a no-match grep anywhere in this pipe would otherwise
    # make the WHOLE pipeline's exit status non-zero even though `head`
    # (the last stage) itself succeeds -- "no match" is an expected,
    # ordinary outcome here (most modules won't define MAX_LINE_ITEMS
    # directly), never a real error worth propagating.
    grep -oE '^MAX_LINE_ITEMS[[:space:]]*(:[[:space:]]*[^=]+)?=[[:space:]]*[0-9]+' "$file" 2>/dev/null \
        | grep -oE '[0-9]+$' | head -1 || true
}

_pd_mli() {
    local file="$1"
    local val
    val="$(_pd_mli_direct "$file")"
    if [ -n "$val" ]; then
        echo "$val"
        return
    fi
    if [ -f "$file" ]; then
        local import_line dotted_module target_file resolved
        import_line="$(grep -E '^from[[:space:]]+[A-Za-z_][A-Za-z0-9_.]*[[:space:]]+import[[:space:]]+.*\bMAX_LINE_ITEMS\b' "$file" 2>/dev/null | head -1 || true)"
        if [ -n "$import_line" ]; then
            dotted_module="$(echo "$import_line" | sed -E 's/^from[[:space:]]+([A-Za-z_][A-Za-z0-9_.]*)[[:space:]]+import.*/\1/')"
            target_file="$(echo "$dotted_module" | tr '.' '/').py"
            if [ -f "$target_file" ] && [ "$target_file" != "$file" ]; then
                resolved="$(_pd_mli_direct "$target_file")"
                if [ -n "$resolved" ]; then
                    echo "import($resolved)"
                    return
                fi
            fi
        fi
    fi
    echo absent
}

# Strip an "import(N)" wrapper down to its bare digits for coherence
# comparison -- import(12) agrees with a direct 12 (same effective value,
# different provenance). "absent" passes through unchanged.
_pd_mli_numeric() {
    local val="$1"
    if [ "$val" = "absent" ]; then
        echo absent
        return
    fi
    if [[ "$val" =~ ^import\(([0-9]+)\)$ ]]; then
        echo "${BASH_REMATCH[1]}"
        return
    fi
    echo "$val"
}

# Emits every plan-decomposition campaign P1/P2/P4 instrument line for the
# CURRENT directory's tree (called by post(), against the checked-out
# session tree). Split out of post() so it can be exercised directly --
# e.g. by validate_pd_overflow_xl.py's checks_sh-invoking regression tests --
# with only the ONE harness primitive it depends on (`command-succeeds`)
# stubbed, rather than the full quorum primitive set post() otherwise
# needs (git-repo, file-exists, check-transcript, ...). Same rationale as
# scenarios/pd-overflow/checks.sh's own _pd_emit_plan_instruments; this is
# the wider (six-module MAX_LINE_ITEMS family, six-constant settings
# family) variant.
#
# Every command-succeeds call below always exits 0 (grep/awk exit status
# is deliberately discarded via `|| true` or default values); only the
# recorded command TEXT carries the finding, for the composer's scorers
# to parse. None of these are pass/fail gates.
_pd_emit_plan_instruments() {
    # -- P1 instrument: plan shape (monolithic file vs multiple files),
    # file count, and per-file line counts. --
    local plan_files=()
    while IFS= read -r f; do
        [ -n "$f" ] && plan_files+=("$f")
    done < <(_pd_plan_files)

    local file_count="${#plan_files[@]}"
    local shape="none"
    if [ "$file_count" -eq 1 ]; then
        shape="monolithic"
    elif [ "$file_count" -gt 1 ]; then
        shape="directory"
    fi
    command-succeeds "true # plan-shape: $shape ($file_count file(s))"

    local f
    for f in "${plan_files[@]}"; do
        local lines
        lines="$(wc -l < "$f" 2>/dev/null | tr -d ' ')"
        command-succeeds "true # plan-file: $f (${lines:-0} lines)"
    done

    # -- P4 instrument: task count, and the settings.py micro-edit
    # disposition (four separate/dedicated tasks vs folded into their
    # module's own task). --
    if [ "$file_count" -gt 0 ]; then
        local task_count
        task_count="$(_pd_task_count "${plan_files[@]}")"
        command-succeeds "true # plan-task-count: $task_count"

        local disposition total dedicated merged
        disposition="$(_pd_settings_disposition "${plan_files[@]}")"
        total="$(echo "$disposition" | awk '{print $1+0}')"
        dedicated="$(echo "$disposition" | awk '{print $2+0}')"
        merged="$((total - dedicated))"
        command-succeeds "true # settings-micro-edits-touching-tasks: $total"
        command-succeeds "true # settings-micro-edits-dedicated-tasks: $dedicated"
        command-succeeds "true # settings-micro-edits-merged-tasks: $merged"
    else
        command-succeeds "true # plan-task-count: 0 (no plan artifact found)"
        command-succeeds "true # settings-micro-edits-touching-tasks: 0 (no plan artifact found)"
        command-succeeds "true # settings-micro-edits-dedicated-tasks: 0 (no plan artifact found)"
        command-succeeds "true # settings-micro-edits-merged-tasks: 0 (no plan artifact found)"
    fi

    # -- P2 instrument: MAX_LINE_ITEMS coherence across validation.py,
    # pricing.py, allocation.py, fulfillment.py, manual_override.py, and
    # csv_import.py. SPEC.md states this as ONE shared rule all six
    # modules must agree on, not six independent choices -- this
    # observes whether the session's own plan and implementation kept it
    # that way. Widened from pd-overflow's four consuming modules to six
    # -- manual_override.py (operations) and csv_import.py
    # (import/export) are new in this scenario's wider domain, each in a
    # DIFFERENT new subsystem, so the family now genuinely spans all
    # three -- see probe-design-notes.md. Tolerant to bare assignment,
    # type-annotated assignment, and one-hop import-reference -- see
    # _pd_mli's own docstring for why (T4 correction: the original
    # bare-assignment-only extraction fabricated a requirement-loss
    # finding against modules that had the constant all along).
    local v_val p_val f_val a_val mo_val ci_val
    v_val="$(_pd_mli orders/validation.py)"
    p_val="$(_pd_mli orders/pricing.py)"
    f_val="$(_pd_mli orders/fulfillment.py)"
    a_val="$(_pd_mli orders/allocation.py)"
    mo_val="$(_pd_mli orders/manual_override.py)"
    ci_val="$(_pd_mli orders/csv_import.py)"
    command-succeeds "true # max-line-items-validation: $v_val"
    command-succeeds "true # max-line-items-pricing: $p_val"
    command-succeeds "true # max-line-items-fulfillment: $f_val"
    command-succeeds "true # max-line-items-allocation: $a_val"
    command-succeeds "true # max-line-items-manual_override: $mo_val"
    command-succeeds "true # max-line-items-csv_import: $ci_val"
    local v_num p_num f_num a_num mo_num ci_num
    v_num="$(_pd_mli_numeric "$v_val")"
    p_num="$(_pd_mli_numeric "$p_val")"
    f_num="$(_pd_mli_numeric "$f_val")"
    a_num="$(_pd_mli_numeric "$a_val")"
    mo_num="$(_pd_mli_numeric "$mo_val")"
    ci_num="$(_pd_mli_numeric "$ci_val")"
    if [ "$v_num" != "absent" ] && [ "$v_num" = "$p_num" ] && [ "$v_num" = "$f_num" ] \
        && [ "$v_num" = "$a_num" ] && [ "$v_num" = "$mo_num" ] && [ "$v_num" = "$ci_num" ]; then
        command-succeeds "true # max-line-items-coherent: yes ($v_num across all six modules)"
    else
        command-succeeds "true # max-line-items-coherent: no (validation=$v_val pricing=$p_val fulfillment=$f_val allocation=$a_val manual_override=$mo_val csv_import=$ci_val)"
    fi

    # -- settings.py micro-edit presence (do the six constants exist
    # at all, regardless of which task(s) added them). --
    local d1="absent" d2="absent" d3="absent" d4="absent" d5="absent" d6="absent"
    if [ -f orders/settings.py ]; then
        grep -q '^DEFAULT_REPORT_TIMEZONE' orders/settings.py && d1="present"
        grep -q '^NOTIFY_MAX_RETRIES' orders/settings.py && d2="present"
        grep -q '^ARCHIVE_GRACE_DAYS' orders/settings.py && d3="present"
        grep -q '^RETURN_WINDOW_DAYS' orders/settings.py && d4="present"
        grep -q '^AUDIT_LOG_RETENTION_DAYS' orders/settings.py && d5="present"
        grep -q '^RECONCILIATION_TOLERANCE_CENTS' orders/settings.py && d6="present"
    fi
    command-succeeds "true # settings-default-report-timezone: $d1"
    command-succeeds "true # settings-notify-max-retries: $d2"
    command-succeeds "true # settings-archive-grace-days: $d3"
    command-succeeds "true # settings-return-window-days: $d4"
    command-succeeds "true # settings-audit-log-retention-days: $d5"
    command-succeeds "true # settings-reconciliation-tolerance-cents: $d6"

    # -- P4/YAGNI instrument: simplest-thing signal. pricing.py should
    # not have grown a currency abstraction SPEC.md explicitly said not
    # to build. --
    local overbuild_hits=0
    if [ -f orders/pricing.py ]; then
        overbuild_hits="$(grep -icE 'class[[:space:]]+[A-Za-z]*Currency|CurrencyRegistry|SUPPORTED_CURRENCIES|abstractmethod|Protocol\[|CurrencyConverter' orders/pricing.py || true)"
    fi
    if [ "${overbuild_hits:-0}" -gt 0 ]; then
        command-succeeds "true # pricing-simplest-thing-signal: overbuilt ($overbuild_hits marker(s))"
    else
        command-succeeds "true # pricing-simplest-thing-signal: simple (0 markers)"
    fi
}

pre() {
    git-repo
    requires-tool python3
    file-exists 'SPEC.md'
    file-exists 'pyproject.toml'
    file-exists 'orders/settings.py'
    command-succeeds './.venv/bin/pytest -q'
    not file-exists 'docs/superpowers/plans/*'
    not file-exists 'orders/intake.py'
    not file-exists 'orders/validation.py'
    not file-exists 'orders/discounts.py'
    not file-exists 'orders/pricing.py'
    not file-exists 'orders/allocation.py'
    not file-exists 'orders/shipping.py'
    not file-exists 'orders/fulfillment.py'
    not file-exists 'orders/backorders.py'
    not file-exists 'orders/notifications.py'
    not file-exists 'orders/loyalty.py'
    not file-exists 'orders/returns.py'
    not file-exists 'orders/refunds.py'
    not file-exists 'orders/reporting.py'
    not file-exists 'orders/archiving.py'
    not file-exists 'orders/cancellation.py'
    not file-exists 'orders/sla.py'
    not file-exists 'orders/staff_roles.py'
    not file-exists 'orders/audit_log.py'
    not file-exists 'orders/inventory_adjustments.py'
    not file-exists 'orders/support_tickets.py'
    not file-exists 'orders/rate_limits.py'
    not file-exists 'orders/shift_coverage.py'
    not file-exists 'orders/manual_override.py'
    not file-exists 'orders/ops_dashboard.py'
    not file-exists 'orders/csv_import.py'
    not file-exists 'orders/export_feed.py'
    not file-exists 'orders/reconciliation.py'
    not file-exists 'orders/ledger_sync.py'
    not file-exists 'orders/carrier_manifest.py'
    not file-exists 'orders/duplicate_detection.py'
    not file-exists 'orders/vendor_feed.py'
    not file-exists 'orders/vendor_lead_times.py'
}

post() {
    check-transcript tool-called Agent
    file-exists "$QUORUM_RUN_DIR/home/.codex/sessions/**/rollout-*.jsonl"
    file-exists 'orders/intake.py'
    file-exists 'orders/validation.py'
    file-exists 'orders/discounts.py'
    file-exists 'orders/pricing.py'
    file-exists 'orders/allocation.py'
    file-exists 'orders/shipping.py'
    file-exists 'orders/fulfillment.py'
    file-exists 'orders/backorders.py'
    file-exists 'orders/notifications.py'
    file-exists 'orders/loyalty.py'
    file-exists 'orders/returns.py'
    file-exists 'orders/refunds.py'
    file-exists 'orders/reporting.py'
    file-exists 'orders/archiving.py'
    file-exists 'orders/cancellation.py'
    file-exists 'orders/sla.py'
    file-exists 'orders/staff_roles.py'
    file-exists 'orders/audit_log.py'
    file-exists 'orders/inventory_adjustments.py'
    file-exists 'orders/support_tickets.py'
    file-exists 'orders/rate_limits.py'
    file-exists 'orders/shift_coverage.py'
    file-exists 'orders/manual_override.py'
    file-exists 'orders/ops_dashboard.py'
    file-exists 'orders/csv_import.py'
    file-exists 'orders/export_feed.py'
    file-exists 'orders/reconciliation.py'
    file-exists 'orders/ledger_sync.py'
    file-exists 'orders/carrier_manifest.py'
    file-exists 'orders/duplicate_detection.py'
    file-exists 'orders/vendor_feed.py'
    file-exists 'orders/vendor_lead_times.py'
    command-succeeds './.venv/bin/pytest -q'

    # Item 20 (queue-execution campaign, 2026-08-01) pattern, same as
    # this campaign's other scenarios' checks.sh: report, as its OWN
    # line, whether `main` advanced past the single setup-seeded commit.
    # This is a GRADED OUTCOME to observe, not a pass/fail criterion, so
    # this check always PASSES by construction (`true`) and can never
    # fold into the composer's failedPost gate.
    local main_commits
    main_commits="$(git rev-list --count main 2>/dev/null || echo 0)"
    if [ "$main_commits" -gt 1 ]; then
        command-succeeds "true # main-advanced-past-seed: yes ($main_commits commits on main; seed=1)"
    else
        command-succeeds "true # main-advanced-past-seed: no ($main_commits commit(s) on main -- non-merge, a graded outcome, not an exclusion)"
    fi

    # ---------------------------------------------------------------
    # Plan-decomposition campaign instruments (P1/P2/P4). See
    # _pd_emit_plan_instruments's own docstring for why this lives in a
    # standalone function rather than inline here.
    # ---------------------------------------------------------------
    _pd_emit_plan_instruments
}
