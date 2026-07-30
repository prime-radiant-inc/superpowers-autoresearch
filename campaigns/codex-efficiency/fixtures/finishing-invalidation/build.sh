#!/usr/bin/env bash
# Hand-authored "already-finished, ONE seeded typo" fixture for
# cx-finishing-invalidation (E3, Task 10 invalidation probe -- brief
# Step 4, fix round 1). Identical to fixtures/finishing/build.sh (same 3
# feature commits, same design note -- see that file for why this was
# built fresh from fixtures/sdd-small/plan.md rather than adapted from
# fixtures/branch-review/build.sh) EXCEPT the docs commit's README.md
# contains one deliberate, unambiguous typo ("charcters" for
# "characters") for the Gauntlet to point the agent at mid-session
# ("please also fix this typo in README, then finish"). This is the
# probe's engineered mutation: the scorer's invalidation-guard assertion
# is that the test suite reruns AFTER this edit, proving a genuinely
# necessary rerun is never suppressed.
#
# Assumes the caller has already `cd`-ed into the target workdir; this
# script only runs `git`/file-writing commands against the current
# directory, matching the other codex-efficiency scenario setup.sh
# scripts' convention (e.g. fixtures/branch-review/build.sh).
set -euo pipefail

git init -qb main
git config user.email "drill@test.local"
git config user.name "Drill Test"

# --- main: baseline skeleton -------------------------------------------
mkdir -p strutils
cat > strutils/__init__.py <<'PY'
"""strutils: small string transformations (skeleton)."""
PY

cat > README.md <<'MD'
# strutils

A small string-transformation package (skeleton). See the `feature`
branch for the full implementation.
MD

git add strutils/__init__.py README.md
git commit -qm "initial: strutils skeleton"

git checkout -qb feature

# --- feature commit 1: core utilities -----------------------------------
cat > pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "strutils"
version = "0.1.0"
description = "Small string transformations from Python or the command line"
readme = "README.md"
requires-python = ">=3.10"

[project.scripts]
strutils = "strutils.cli:main"

[tool.setuptools.packages.find]
include = ["strutils"]
TOML

cat > strutils/core.py <<'PY'
import re


def slugify(text: str) -> str:
    lowered = text.lower()
    slug = re.sub(r"[\W_]+", "-", lowered)
    return slug.strip("-")


def truncate(text: str, length: int) -> str:
    if length < 0:
        raise ValueError("length must be non-negative")
    if len(text) <= length:
        return text
    if length <= 3:
        return "..."[:length]
    return text[: length - 3] + "..."


def word_count(text: str) -> int:
    return len(text.split())
PY

cat > strutils/__init__.py <<'PY'
from .core import slugify, truncate, word_count

__all__ = ["slugify", "truncate", "word_count"]
PY

mkdir -p tests
touch tests/__init__.py

cat > tests/test_core.py <<'PY'
import unittest

from strutils.core import slugify, truncate, word_count


class SlugifyTests(unittest.TestCase):
    def test_lowercases_and_collapses_non_alphanumeric_runs(self):
        self.assertEqual(slugify("  Hello, WORLD!  "), "hello-world")

    def test_preserves_alphanumeric_characters(self):
        self.assertEqual(slugify("Release 2 Version 10"), "release-2-version-10")

    def test_returns_empty_string_when_no_alphanumeric_characters_exist(self):
        self.assertEqual(slugify("--- !!! ---"), "")


class TruncateTests(unittest.TestCase):
    def test_returns_text_unchanged_when_it_fits(self):
        self.assertEqual(truncate("hello", 5), "hello")

    def test_appends_ellipsis_within_requested_length(self):
        self.assertEqual(truncate("hello world", 8), "hello...")

    def test_uses_partial_ellipsis_when_limit_is_shorter_than_three(self):
        self.assertEqual(truncate("hello", 2), "..")

    def test_rejects_negative_length(self):
        with self.assertRaises(ValueError):
            truncate("hello", -1)


class WordCountTests(unittest.TestCase):
    def test_counts_tokens_separated_by_any_whitespace(self):
        self.assertEqual(word_count(" one\ttwo\nthree  "), 3)

    def test_empty_or_whitespace_only_text_has_zero_words(self):
        self.assertEqual(word_count(" \n\t "), 0)


if __name__ == "__main__":
    unittest.main()
PY

git add pyproject.toml strutils/core.py strutils/__init__.py tests/__init__.py tests/test_core.py
git commit -qm "feat: add core string utilities"

# --- feature commit 2: CLI wrapper --------------------------------------
cat > strutils/cli.py <<'PY'
import argparse
import sys

from .core import slugify, truncate, word_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="strutils")
    parser.add_argument("command")
    parser.add_argument("text")
    parser.add_argument("--length", type=int)
    args = parser.parse_args(argv)

    if args.command not in {"slugify", "truncate", "count"}:
        print(f"error: unknown command '{args.command}'", file=sys.stderr)
        return 1

    if args.command == "truncate" and args.length is None:
        print("error: truncate requires --length", file=sys.stderr)
        return 1

    if args.command == "slugify":
        result = slugify(args.text)
    elif args.command == "truncate":
        result = truncate(args.text, args.length)
    else:
        result = word_count(args.text)

    print(result)
    return 0
PY

cat > tests/test_cli.py <<'PY'
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from strutils.cli import main


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = main(argv)
        return result, stdout.getvalue(), stderr.getvalue()

    def test_slugify_prints_transformed_text(self):
        result, stdout, stderr = self.run_cli(["slugify", "Hello, World!"])
        self.assertEqual(result, 0)
        self.assertEqual(stdout, "hello-world\n")
        self.assertEqual(stderr, "")

    def test_truncate_uses_required_length(self):
        result, stdout, stderr = self.run_cli(
            ["truncate", "hello world", "--length", "8"]
        )
        self.assertEqual(result, 0)
        self.assertEqual(stdout, "hello...\n")
        self.assertEqual(stderr, "")

    def test_count_prints_integer_result(self):
        result, stdout, stderr = self.run_cli(["count", "one  two\nthree"])
        self.assertEqual(result, 0)
        self.assertEqual(stdout, "3\n")
        self.assertEqual(stderr, "")

    def test_unknown_command_writes_stderr_and_returns_one(self):
        result, stdout, stderr = self.run_cli(["reverse", "hello"])
        self.assertEqual(result, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "error: unknown command 'reverse'\n")

    def test_truncate_without_length_writes_stderr_and_returns_one(self):
        result, stdout, stderr = self.run_cli(["truncate", "hello"])
        self.assertEqual(result, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "error: truncate requires --length\n")
PY

git add strutils/cli.py tests/test_cli.py
git commit -qm "feat: add string utilities CLI"

# --- feature commit 3: docs ----------------------------------------------
cat > README.md <<'MD'
# String Utils CLI

`strutils` is a small Python 3.10+ package for slugifying text, truncating text
to a maximum length, and counting whitespace-separated words.

## Install

From the project directory:

```bash
python -m pip install .
```

## Use

Create a slug:

```console
$ strutils slugify "Hello, World!"
hello-world
```

Truncate text to eight charcters, including the ellipsis:

```console
$ strutils truncate "hello world" --length 8
hello...
```

Count words:

```console
$ strutils count "one two three"
3
```
MD

git add README.md
git commit -qm "docs: add string utilities usage guide"
