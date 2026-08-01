# Every scenario's fixtures/ tree is a standalone mini-repo meant to run
# inside its OWN isolated per-run venv when quorum executes it (see
# init_repo_from_fixtures + provision_venv in the evals harness) -- never
# as part of this repo's own `pytest campaigns/` sweep. Left uncollected,
# same-named test modules across sibling scenarios (e.g. two
# cp-x7x9-conflicts* variants both shipping tests/test_legacy_store.py)
# collide under pytest's default rootdir import mode ("import file
# mismatch"), and fixture code that assumes an editable install
# (`from legacylib.legacy_store import ...`) fails to import standalone.
collect_ignore_glob = ["*/fixtures"]
