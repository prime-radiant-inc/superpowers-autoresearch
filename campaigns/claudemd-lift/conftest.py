"""Probe fixture dirs (`probes/*/fixture/`) intentionally contain broken or
buggy `test_*.py` files -- they're workdir contents for the agent-under-test
to fix, not part of this repo's own test suite. Keep pytest from collecting
them when running the outer suite (`pytest campaigns/claudemd-lift/` or a
full repo `pytest`).
"""
collect_ignore_glob = ["probes/*/fixture/*", "probes/*/fixture/**/*"]
