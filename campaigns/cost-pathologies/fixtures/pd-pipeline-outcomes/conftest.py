# Both outcome trees are deliberately near-identical twins (see
# scenarios/pd-pipeline/probe-design-notes.md) -- monolithic-layered/
# and directory-skeleton/ ship the same test basenames
# (tests/test_intake.py, tests/test_validation.py, ...) on purpose, so
# validate_pd_pipeline.py's observables are comparing like with like.
# Left uncollected here, that collides under pytest's default rootdir
# import mode ("import file mismatch"), the same class of problem
# scenarios/conftest.py documents for sibling scenarios' fixtures/
# trees. test_pd_pipeline_fixture.py (one level up) validates both
# trees correctly, via a fresh `python3 -m pytest` subprocess per tree
# -- never as part of this repo's own top-level `pytest campaigns/`
# sweep.
collect_ignore_glob = ["monolithic-layered", "directory-skeleton"]
