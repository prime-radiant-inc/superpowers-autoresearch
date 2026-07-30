# String Utils CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an installable `strutils` Python package with three string utilities, a command-line interface, unit tests, and concise usage documentation.

**Architecture:** Keep transformations as pure functions in `strutils/core.py`, with `strutils/cli.py` responsible only for argument parsing, validation, output, and exit codes. Package metadata exposes `strutils.cli:main` as the `strutils` console command; tests exercise core behavior directly and CLI behavior through `main(argv)`.

**Tech Stack:** Python 3.10+, Python standard library (`argparse`, `re`, `unittest`), `pyproject.toml` packaging metadata

## Global Constraints

- Support Python 3.10+.
- Use the Python standard library only at runtime.
- Write all tests with `unittest`.
- Follow TDD: add a focused failing test, observe the expected failure, add the minimum implementation, and rerun the test before proceeding.
- `slugify(text)` lowercases text, replaces each run of non-alphanumeric characters with one hyphen, and removes leading and trailing hyphens.
- `truncate(text, length)` returns at most `length` characters, including the `"..."` marker whenever truncation occurs.
- `word_count(text)` counts whitespace-separated tokens.
- The CLI shape is `strutils <command> <text> [--length N]`, with commands `slugify`, `truncate`, and `count`.
- Successful CLI calls print the result to stdout and return `0`.
- Unknown commands and a missing `--length` for `truncate` print an error to stderr and return `1`.

## File Structure

- `pyproject.toml` — package metadata, Python version floor, build configuration, and the `strutils` console-script entry point.
- `strutils/__init__.py` — package marker and public exports for the three core functions.
- `strutils/core.py` — pure string-transformation functions with no CLI concerns.
- `strutils/cli.py` — argument parsing, command dispatch, stderr validation messages, and exit codes.
- `tests/__init__.py` — makes the test directory importable for targeted `unittest` commands.
- `tests/test_core.py` — unit tests for transformation behavior and boundary cases.
- `tests/test_cli.py` — in-process tests for stdout, stderr, dispatch, and return codes.
- `README.md` — purpose, installation and invocation instructions, and one example for each command.

---

### Task 1: Package Skeleton and Core Utilities

**Files:**

- Create: `pyproject.toml`
- Create: `strutils/__init__.py`
- Create: `strutils/core.py`
- Create: `tests/__init__.py`
- Create: `tests/test_core.py`

**Interfaces:**

- Consumes: Python `str` values and an integer maximum length.
- Produces: `slugify(text: str) -> str`, `truncate(text: str, length: int) -> str`, and `word_count(text: str) -> int`, exported from `strutils`.

- [ ] **Step 1: Add package metadata and the initial failing core tests**

Create `pyproject.toml`:

```toml
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
```

Create empty `strutils/__init__.py` and `tests/__init__.py`, then create `tests/test_core.py`:

```python
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
```

- [ ] **Step 2: Run the core tests and verify the missing module failure**

Run:

```bash
python -m unittest tests.test_core -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'strutils.core'`.

- [ ] **Step 3: Implement the minimal core functions**

Create `strutils/core.py`:

```python
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
```

Expose the public API from `strutils/__init__.py`:

```python
from .core import slugify, truncate, word_count

__all__ = ["slugify", "truncate", "word_count"]
```

- [ ] **Step 4: Run the core tests and verify they pass**

Run:

```bash
python -m unittest tests.test_core -v
```

Expected: all 9 tests PASS.

- [ ] **Step 5: Commit the core utility deliverable**

```bash
git add pyproject.toml strutils/__init__.py strutils/core.py tests/__init__.py tests/test_core.py
git commit -m "feat: add core string utilities"
```

---

### Task 2: Command-Line Interface

**Files:**

- Create: `strutils/cli.py`
- Create: `tests/test_cli.py`

**Interfaces:**

- Consumes: `slugify(text: str) -> str`, `truncate(text: str, length: int) -> str`, and `word_count(text: str) -> int` from `strutils.core`; optional `argv: list[str]`.
- Produces: `main(argv: list[str] | None = None) -> int`, used by the `strutils` console entry point.

- [ ] **Step 1: Write failing tests for successful command dispatch**

Create `tests/test_cli.py`:

```python
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
```

- [ ] **Step 2: Run the CLI tests and verify the missing module failure**

Run:

```bash
python -m unittest tests.test_cli -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'strutils.cli'`.

- [ ] **Step 3: Implement parsing and successful dispatch**

Create `strutils/cli.py`:

```python
import argparse

from .core import slugify, truncate, word_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="strutils")
    parser.add_argument("command")
    parser.add_argument("text")
    parser.add_argument("--length", type=int)
    args = parser.parse_args(argv)

    if args.command == "slugify":
        result = slugify(args.text)
    elif args.command == "truncate":
        result = truncate(args.text, args.length)
    else:
        result = word_count(args.text)

    print(result)
    return 0
```

- [ ] **Step 4: Run the successful CLI tests and verify they pass**

Run:

```bash
python -m unittest tests.test_cli -v
```

Expected: all 3 tests PASS.

- [ ] **Step 5: Add failing tests for specified CLI errors**

Append these methods to `CliTests` in `tests/test_cli.py`:

```python
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
```

- [ ] **Step 6: Run the error tests and verify both fail for the expected reasons**

Run:

```bash
python -m unittest \
  tests.test_cli.CliTests.test_unknown_command_writes_stderr_and_returns_one \
  tests.test_cli.CliTests.test_truncate_without_length_writes_stderr_and_returns_one \
  -v
```

Expected: the unknown-command test FAILS because the command is incorrectly treated as `count`; the missing-length test ERRORS when `truncate` receives `None`.

- [ ] **Step 7: Add explicit validation and stderr messages**

Replace `main` in `strutils/cli.py` with:

```python
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
```

Also add this import at the top of `strutils/cli.py`:

```python
import sys
```

- [ ] **Step 8: Run the complete CLI and core test suite**

Run:

```bash
python -m unittest discover -s tests -v
```

Expected: all 14 tests PASS.

- [ ] **Step 9: Commit the CLI deliverable**

```bash
git add strutils/cli.py tests/test_cli.py
git commit -m "feat: add string utilities CLI"
```

---

### Task 3: User Documentation and Final Verification

**Files:**

- Create: `README.md`

**Interfaces:**

- Consumes: the installed `strutils` console command from `pyproject.toml`.
- Produces: installation instructions and copyable examples for `slugify`, `truncate`, and `count`.

- [ ] **Step 1: Write the README with installation and one example per command**

Create `README.md`:

````markdown
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

Truncate text to eight characters, including the ellipsis:

```console
$ strutils truncate "hello world" --length 8
hello...
```

Count words:

```console
$ strutils count "one two three"
3
```
````

- [ ] **Step 2: Run all automated tests**

Run:

```bash
python -m unittest discover -s tests -v
```

Expected: all 14 tests PASS.

- [ ] **Step 3: Verify package installation and all documented examples in a clean virtual environment**

Run:

```bash
STRUTILS_TEST_DIR=$(mktemp -d)
python -m venv "$STRUTILS_TEST_DIR/venv"
"$STRUTILS_TEST_DIR/venv/bin/python" -m pip install .
test "$("$STRUTILS_TEST_DIR/venv/bin/strutils" slugify 'Hello, World!')" = "hello-world"
test "$("$STRUTILS_TEST_DIR/venv/bin/strutils" truncate 'hello world' --length 8)" = "hello..."
test "$("$STRUTILS_TEST_DIR/venv/bin/strutils" count 'one two three')" = "3"
```

Expected: installation succeeds and all three `test` commands exit `0` without output.

- [ ] **Step 4: Confirm the repository contains only intended project artifacts**

Run:

```bash
git status --short
```

Expected: only `README.md` is uncommitted; build directories and package metadata directories must not be staged.

- [ ] **Step 5: Commit the documentation**

```bash
git add README.md
git commit -m "docs: add string utilities usage guide"
```

- [ ] **Step 6: Run the final regression suite**

Run:

```bash
python -m unittest discover -s tests -v
```

Expected: all 14 tests PASS.
