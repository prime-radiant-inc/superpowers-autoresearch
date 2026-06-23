#!/usr/bin/env python3
"""Measure the token cost of the superpowers session-start bootstrap.

The `using-superpowers` SKILL.md is injected verbatim into EVERY session by the
SessionStart hook (hooks/session-start), wrapped in an
<EXTREMELY_IMPORTANT>...</EXTREMELY_IMPORTANT> envelope. That injected blob is
what we pay for on every single session and every subagent spawn, so it is the
real compression target -- not the on-disk byte count.

This script reconstructs the EXACT injected blob (same wrapper the hook uses) and
reports its size. If ANTHROPIC_API_KEY is set it reports the true Claude token
count via the count_tokens API; otherwise it prints a clearly-labelled estimate.

Usage:
    python3 measure-bootstrap-tokens.py [path/to/SKILL.md]

    # default SKILL.md is the live superpowers bootstrap:
    python3 measure-bootstrap-tokens.py

    # compare a compressed variant against the baseline:
    BASELINE=skills/using-superpowers/SKILL.md \
        python3 measure-bootstrap-tokens.py variants/v3/SKILL.md

Env:
    ANTHROPIC_API_KEY   if set, get exact token counts from the API
    MODEL               model id for token counting (default claude-sonnet-4-6)
    BASELINE            optional path to a second SKILL.md to diff against
"""
import json
import os
import sys
import urllib.request
import urllib.error

DEFAULT_SKILL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "superpowers", "skills", "using-superpowers", "SKILL.md",
)
MODEL = os.environ.get("MODEL", "claude-sonnet-4-6")

# The wrapper text the SessionStart hook prepends/appends around SKILL.md.
# Kept byte-identical to hooks/session-start so our measurement matches reality.
WRAPPER_HEAD = (
    "<EXTREMELY_IMPORTANT>\n"
    "You have superpowers.\n\n"
    "**Below is the full content of your 'superpowers:using-superpowers' skill - "
    "your introduction to using skills. For all other skills, use the 'Skill' tool:**\n\n"
)
WRAPPER_TAIL = "\n</EXTREMELY_IMPORTANT>"


def injected_blob(skill_path):
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    return WRAPPER_HEAD + content + WRAPPER_TAIL


def api_token_count(text):
    """Exact token count via Anthropic count_tokens. Returns int or None."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages/count_tokens",
        data=json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": text}],
        }).encode("utf-8"),
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())["input_tokens"]
    except urllib.error.HTTPError as e:
        sys.stderr.write("count_tokens API error %s: %s\n" % (e.code, e.read().decode("utf-8", "replace")))
        return None
    except Exception as e:  # noqa: BLE001
        sys.stderr.write("count_tokens failed: %r\n" % (e,))
        return None


def estimate_tokens(text):
    """Rough token estimate when no API key. Claude prose ~3.7 chars/token;
    markdown/tables/graphviz run a bit denser. We report a chars/3.7 midpoint."""
    return round(len(text) / 3.7)


def report(label, skill_path):
    blob = injected_blob(skill_path)
    chars = len(blob)
    words = len(blob.split())
    lines = blob.count("\n") + 1
    exact = api_token_count(blob)
    print("=== %s ===" % label)
    print("  path:   %s" % skill_path)
    print("  bytes:  %d" % len(blob.encode("utf-8")))
    print("  chars:  %d" % chars)
    print("  words:  %d" % words)
    print("  lines:  %d" % lines)
    if exact is not None:
        print("  TOKENS (exact, %s): %d" % (MODEL, exact))
    else:
        print("  tokens (ESTIMATE chars/3.7, no API key): ~%d" % estimate_tokens(blob))
    print()
    return exact if exact is not None else estimate_tokens(blob)


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SKILL
    if not os.path.exists(skill_path):
        sys.stderr.write("SKILL.md not found: %s\n" % skill_path)
        return 1

    have_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    print("Token counting mode: %s\n" % ("EXACT via API (%s)" % MODEL if have_key else "ESTIMATE (set ANTHROPIC_API_KEY for exact)"))

    cur = report("current/variant bootstrap", skill_path)

    baseline = os.environ.get("BASELINE")
    if baseline and os.path.abspath(baseline) != os.path.abspath(skill_path):
        base = report("baseline bootstrap", baseline)
        if base:
            delta = cur - base
            pct = (delta / base * 100) if base else 0
            print("=== delta vs baseline ===")
            print("  %+d tokens (%+.1f%%)" % (delta, pct))
    return 0


if __name__ == "__main__":
    sys.exit(main())
