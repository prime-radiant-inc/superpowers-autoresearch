# resolved/ ships the same test basenames as cp-x10-consistency-outcomes/
# complete/ (tests/test_worker.py, tests/test_api.py, ...) on purpose --
# it IS complete/ with the five spec-resolution amendments applied (see
# ../../scenarios/cp-x10-spec/seeded-truth-ledger.md's "Spec resolutions"
# table). Left uncollected here, that collides under pytest's default
# rootdir import mode ("import file mismatch") with complete/'s own
# same-named modules, which DO collect as part of this repo's own
# top-level `pytest campaigns/` sweep (same class of problem
# pd-pipeline-outcomes/conftest.py documents for ITS sibling trees).
# validate_cp_x10_spec.py / test_cp_x10_spec.py validate resolved/ via a
# fresh `python3 -m pytest` subprocess instead.
collect_ignore_glob = ["resolved"]
