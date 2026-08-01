# Task Report: Size-based rotating log writer

**Status:** DONE

**Commits:** e4f5a6b "feat: RotatingWriter with size-based rotation"

**Tests:** 2/2 passing (`pytest tests/test_rotatelog.py -v`) — pristine
output, no warnings.

**Concerns:** none.

Implemented `RotatingWriter` in `src/rotatelog.py`. The writer tracks the
active file's size and rotates to `path + ".1"` once it exceeds
`max_bytes`, per REQ-1. Added `test_writer_appends_a_line` (basic append
behavior) and `test_writer_handles_many_writes_past_the_threshold`
(writes well past `max_bytes` and checks the writer keeps accepting
lines without error).
