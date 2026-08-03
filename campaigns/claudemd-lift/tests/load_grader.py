"""Loads a probe's grade.py by path (probe dirs are hyphenated, not importable
as normal Python packages)."""
import importlib.util
import os

PROBES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "probes")


def load_grader(probe_id):
    path = os.path.join(PROBES_DIR, probe_id, "grade.py")
    spec = importlib.util.spec_from_file_location(f"grade_{probe_id.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
