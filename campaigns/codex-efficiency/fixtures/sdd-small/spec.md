# String Utils CLI — Design Spec

A small Python package (`strutils`) providing string-transformation
utilities via a CLI.

## Core functions (strutils/core.py)

- `slugify(text)` -> str: lowercase; replace runs of non-alphanumeric
  characters with a single hyphen; strip leading/trailing hyphens.
- `truncate(text, length)` -> str: shorten to at most `length` characters,
  appending `"..."` when truncated (the result including `"..."` must not
  exceed `length`).
- `word_count(text)` -> int: number of whitespace-separated tokens.

## CLI (strutils/cli.py)

`strutils <command> <text> [--length N]`, command in `{slugify, truncate,
count}`. Prints the result to stdout, returns 0. Unknown command -> stderr
message, return 1. `truncate` requires `--length`; missing it -> stderr
message, return 1.

## README

A short `README.md`: what the tool does, how to install/run it, one
example per command.

## Tech

Python 3.10+, standard library only. Tests with `unittest`. TDD required.
