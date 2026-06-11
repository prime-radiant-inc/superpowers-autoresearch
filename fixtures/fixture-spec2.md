# Notes CLI — Design Spec

A Node.js CLI (`note`) managing notes in a JSON file (~/.notes/notes.json). Node 20+, stdlib only, node:test, TDD required.

## Commands (9)

1. `note add <text> [--tag <tag>]` — add a note, print its id. Validate text is non-empty somehow.
2. `note show <id>` — print one note (text, tags, created date). Fails appropriately if unknown.
3. `note rm <id>` — delete a note. Same id handling as show.
4. `note tag <id> <tag>` — add a tag to a note. Same id handling as show.
5. `note untag <id> <tag>` — remove a tag. Same id handling; handle a missing tag reasonably.
6. `note list [--tag <tag>]` — all notes (optionally filtered), one line each, sensible format.
7. `note search <term>` — notes whose text contains term, same output format as list.
8. `note count [--tag <tag>]` — print how many notes (optionally filtered), shares filtering with list.
9. `note export [--tag <tag>]` — print notes as JSON array (same filtering again).

Commands 2-5 share id-lookup behavior; 6-9 share filtering/format behavior. Corrupt storage files should be dealt with reasonably.
