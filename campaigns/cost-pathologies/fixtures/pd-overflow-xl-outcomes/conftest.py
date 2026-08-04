# directory-tasks/ ships its own tests/ package (tests/test_intake.py,
# tests/test_validation.py, ...) that collides with sibling scenarios'
# same-named test modules under pytest's default rootdir import mode
# ("import file mismatch") if collected as part of this repo's own
# `pytest campaigns/` sweep. Left uncollected here, same pattern as
# ../pd-overflow-outcomes/conftest.py (and ../pd-pipeline-outcomes/
# conftest.py) documents for its own tree.
# test_pd_overflow_xl_fixture.py (one level up) validates this tree
# correctly, via a fresh `python3 -m pytest` subprocess.
collect_ignore_glob = ["directory-tasks"]
