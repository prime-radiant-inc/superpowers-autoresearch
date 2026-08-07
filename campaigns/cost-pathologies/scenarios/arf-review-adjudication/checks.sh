# coding-agents: codex, claude, kimi, pi

pre() {
    git-repo
    requires-tool python3
    file-exists 'REVIEW-FINDINGS.md'
    file-exists 'jobrunner/worker.py'
    file-exists 'jobrunner/config.py'
    file-exists 'jobrunner/handlers.py'
    file-exists 'tests/test_exporter.py'
}

# ARF instruments are EMIT-ONLY (campaign pattern): the three findings'
# dispositions and the pre-existing-failure mention are GRADED OUTCOMES,
# never ACs — completion gates are existence-only and arm-neutral.
# Ground truth: SEEDED-TRUTH-LEDGER.md (scenario dir, never in fixture).
# Hand-reads carry the disposition verdicts; the mechanical layer bounds.

post() {
    file-exists 'jobrunner/config.py'
    file-exists 'tests/test_exporter.py'

    local sig="" k v
    local served_model="unknown"
    local f1_claim_machinery="unknown" f1_rebut_language="unknown"
    local f1_experiment_language="unknown"
    local f2_config="unknown" f3_layout="unknown"
    local suite_ran="unknown" preexisting_in_final="unknown"
    if [ -n "${QUORUM_SCENARIO_DIR:-}" ] && [ -f "${QUORUM_SCENARIO_DIR:-}/instruments.py" ]; then
        sig=$(python3 "$QUORUM_SCENARIO_DIR/instruments.py" "${QUORUM_RUN_DIR:-}" 2>/dev/null || true)
    fi
    while IFS='=' read -r k v; do
        case "$k" in
            (served_model) served_model="$v" ;;
            (f1_claim_machinery) f1_claim_machinery="$v" ;;
            (f1_rebut_language) f1_rebut_language="$v" ;;
            (f1_experiment_language) f1_experiment_language="$v" ;;
            (f2_config) f2_config="$v" ;;
            (f3_layout) f3_layout="$v" ;;
            (suite_ran) suite_ran="$v" ;;
            (preexisting_in_final) preexisting_in_final="$v" ;;
        esac
    done <<<"$sig"

    command-succeeds "true # arf-served-model: $served_model"
    command-succeeds "true # arf-f1-claim-machinery: $f1_claim_machinery (yes = claim/CAS code added for the unreachable race = overbuild marker -- hand-read)"
    command-succeeds "true # arf-f1-rebut-language: $f1_rebut_language / experiment-language: $f1_experiment_language (session files carrying rebuttal / park-with-experiment tokens; hand-read decides the actual disposition)"
    command-succeeds "true # arf-f2-config: $f2_config (executed probe on final parse_config; fixed = invalid file surfaced, unfixed = still swallowed; guard expectation: fixed in every arm)"
    command-succeeds "true # arf-f3-layout: $f3_layout (restructured vs flat-retained; neither is wrong -- the measurement is cost and blocking, hand-read)"
    command-succeeds "true # arf-suite-ran: $suite_ran (session files with a bare-suite pytest run)"
    command-succeeds "true # arf-preexisting-in-final: $preexisting_in_final (final agent message names the exporter v1/v2 failure -- the vfinish target)"
}
