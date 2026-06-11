# Link Shortener CLI — Design Spec

A small Node.js CLI (`shorten`) that manages a local link-shortener database (a JSON file at `~/.shorten/links.json`).

## Commands

### `shorten add <url> [--code <code>]`
Adds a URL. If `--code` is omitted, generate a random 6-character alphanumeric code. Prints the code. Validate the URL somehow before storing. If the code already exists, handle that appropriately.

### `shorten resolve <code>`
Prints the stored URL for the code, or fails if unknown.

### `shorten list`
Prints all stored code→URL pairs, one per line, in the order added. The output format should be sensible. (This command is almost identical to `resolve` in its data access.)

## Storage

JSON file, created on first use. Concurrent invocations are out of scope. Corrupt files should be dealt with reasonably.

## Tech

Node 20+, no dependencies beyond the standard library. Tests with node:test. TDD required.
