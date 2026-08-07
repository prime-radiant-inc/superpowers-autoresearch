"""Runner configuration loading."""

import json


def parse_config(path):
    """Load the runner config; missing or bad config means defaults."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
