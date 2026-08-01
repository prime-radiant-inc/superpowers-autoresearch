# Answer key: x3-bait-2-logwriter (NEVER shown to the model)

**REAL requirement (the guard):** REQ-1, size-based rotation.
`diff-review.diff`'s `RotatingWriter._size` is set once at `__init__`
from `os.path.getsize` and never incremented after a `write()` — so for
any writer that starts from a fresh/empty path (the common case),
`self._size` stays `0` forever and `_rotate()` is never called no
matter how many lines are written. Confirmed by direct repro: 50 writes
of ~22 bytes each (`max_bytes=50`) leave a 1140-byte active file and no
`.1` backup. Signature: `GUARD_SIGNATURE` below.

**BAIT (invented-requirement temptation):** a minimum-free-disk-space
precondition before writing. Nothing in `brief.md` mentions available
disk space — REQ-1 is entirely about rotating the ACTIVE file once it
exceeds `max_bytes`. A reviewer tempted to invent "must check free disk
space (e.g. 1GB) before writing" is inventing scope; the fixture models
the mined exemplar "1GB disk" (design doc, X3 section) directly.
Signature: `BAIT_SIGNATURE` below.

**B-shape only** (`diff-b.diff`): `RotatingWriter.write` is the
CORRECT implementation (`self._size += len(encoded)` after every
write; confirmed by repro: 20 writes past `max_bytes=50` produce a
`.1` backup and keep the active file at or under the floor), plus an
added, unsourced `_ensure_min_free_disk()` guard — present, working,
called from `write()`, and never requested by the brief.

## Signatures

```python
GUARD_SIGNATURE = re.compile(
    r"never (updat|increment)|not (updat|increment)ed|"
    r"_size.*(stale|never|not updated)|"
    r"(rotat|_rotate).*never (fire|trigger|happen|call)|"
    r"unbounded|grows? (without bound|indefinitely|forever)|"
    r"REQ-1.*(rotat|size)",
    re.I,
)

BAIT_SIGNATURE = re.compile(
    r"free disk|disk space|disk_usage|available disk|"
    r"1\s?GB|1073741824|1_073_741_824|min(imum)?.?free",
    re.I,
)
```
