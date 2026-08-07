# VaultKit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A small document-vault toolkit (`vaultkit/`) on top of the vendored `blobstore` library: ingest files, catalog them, export bundles, prune, and a one-shot pipeline.

**Architecture:** Five small modules under `vaultkit/`, each owning one operation, all storing through `vendor.blobstore.BlobStore`. No service layer; each module opens the store against a caller-supplied root directory.

**Tech Stack:** Python 3.11+, standard library only, `pytest` for tests. `vendor/blobstore` is vendored third-party code.

## Global Constraints

- `vendor/` is vendored third-party code and MUST NOT be modified.
- Runtime code uses only the Python standard library plus the vendored `blobstore`.
- Blob keys are the file's basename unless a caller supplies an explicit key.
- All functions take the store root as their first argument; nothing caches a `BlobStore` between calls.
- Tests use `tmp_path` fixtures; nothing writes outside the store root or explicit output dirs.

---

### Task 1: Ingest

**Files:**
- Create: `vaultkit/__init__.py` (empty)
- Create: `vaultkit/ingest.py`
- Test: `tests/test_ingest.py`

**Interfaces:**
- Consumes: `vendor.blobstore.BlobStore`
- Produces: `ingest_file(store_root: str, path: str, key: str | None = None) -> str` — stores the file's bytes, returns the key used. Later tasks rely on this exact signature.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ingest.py
import os
from vaultkit.ingest import ingest_file


def test_ingest_returns_basename_key(tmp_path):
    src = tmp_path / "notes.txt"
    src.write_bytes(b"hello vault")
    store_root = str(tmp_path / "store")
    key = ingest_file(store_root, str(src))
    assert key == "notes.txt"


def test_ingest_replaces_on_reingest(tmp_path):
    src = tmp_path / "notes.txt"
    src.write_bytes(b"v1")
    store_root = str(tmp_path / "store")
    ingest_file(store_root, str(src))
    src.write_bytes(b"v2")
    key = ingest_file(store_root, str(src))
    assert key == "notes.txt"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m pytest tests/test_ingest.py -v`
Expected: FAIL (module missing)

- [ ] **Step 3: Implement**

```python
# vaultkit/ingest.py
import os

from vendor.blobstore import BlobStore


def ingest_file(store_root, path, key=None):
    """Store one file's bytes under its basename (or an explicit key).

    Re-ingesting an existing key replaces the stored blob.
    """
    store = BlobStore(store_root)
    if key is None:
        key = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()
    store.put(key, data, overwrite=True)
    return key
```

- [ ] **Step 4: Run the tests, make sure they pass**

Run: `python3 -m pytest tests/test_ingest.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add vaultkit/ tests/test_ingest.py
git commit -m "feat: ingest files into the vault"
```

---

### Task 2: Catalog

**Files:**
- Create: `vaultkit/catalog.py`
- Test: `tests/test_catalog.py`

**Interfaces:**
- Consumes: `ingest_file` from Task 1 (tests seed the store with it); `vendor.blobstore.BlobStore`
- Produces: `catalog(store_root: str, prefix: str = "") -> list[dict]` — one `{"key": str, "size": int}` per stored blob, sorted by key.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_catalog.py
from vaultkit.catalog import catalog
from vaultkit.ingest import ingest_file


def test_catalog_lists_sizes(tmp_path):
    store_root = str(tmp_path / "store")
    a = tmp_path / "a.txt"
    a.write_bytes(b"12345")
    b = tmp_path / "b.txt"
    b.write_bytes(b"12")
    ingest_file(store_root, str(a))
    ingest_file(store_root, str(b))
    entries = catalog(store_root)
    assert entries == [
        {"key": "a.txt", "size": 5},
        {"key": "b.txt", "size": 2},
    ]


def test_catalog_prefix_filters(tmp_path):
    store_root = str(tmp_path / "store")
    a = tmp_path / "a.txt"
    a.write_bytes(b"x")
    ingest_file(store_root, str(a))
    assert catalog(store_root, prefix="zzz") == []
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m pytest tests/test_catalog.py -v`
Expected: FAIL (module missing)

- [ ] **Step 3: Implement**

```python
# vaultkit/catalog.py
from vendor.blobstore import BlobStore


def catalog(store_root, prefix=""):
    """List stored blobs as {key, size} dicts, sorted by key."""
    store = BlobStore(store_root)
    entries = []
    for key in store.list_keys(prefix):
        data = store.get(key)
        entries.append({"key": key, "size": len(data)})
    return entries
```

- [ ] **Step 4: Run the tests, make sure they pass**

Run: `python3 -m pytest tests/test_catalog.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add vaultkit/catalog.py tests/test_catalog.py
git commit -m "feat: catalog stored blobs"
```

---

### Task 3: Export

**Files:**
- Create: `vaultkit/export.py`
- Test: `tests/test_export.py`

**Interfaces:**
- Consumes: `ingest_file` from Task 1 (tests); `vendor.blobstore.BlobStore`
- Produces: `export_bundle(store_root: str, keys: list[str], out_dir: str) -> int` — writes each key's blob to `<out_dir>/<key>`, returns the count written.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_export.py
import os
from vaultkit.export import export_bundle
from vaultkit.ingest import ingest_file


def test_export_writes_files(tmp_path):
    store_root = str(tmp_path / "store")
    src = tmp_path / "doc.txt"
    src.write_bytes(b"contents")
    ingest_file(store_root, str(src))
    out = str(tmp_path / "out")
    n = export_bundle(store_root, ["doc.txt"], out)
    assert n == 1
    with open(os.path.join(out, "doc.txt"), "rb") as f:
        assert f.read() == b"contents"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m pytest tests/test_export.py -v`
Expected: FAIL (module missing)

- [ ] **Step 3: Implement**

```python
# vaultkit/export.py
import os

from vendor.blobstore import BlobStore


def export_bundle(store_root, keys, out_dir):
    """Write each key's blob to out_dir under its key name."""
    store = BlobStore(store_root)
    os.makedirs(out_dir, exist_ok=True)
    written = 0
    for key in keys:
        data = store.get(key)
        with open(os.path.join(out_dir, key), "wb") as f:
            f.write(data)
        written += 1
    return written
```

- [ ] **Step 4: Run the tests, make sure they pass**

Run: `python3 -m pytest tests/test_export.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add vaultkit/export.py tests/test_export.py
git commit -m "feat: export blob bundles"
```

---

### Task 4: Prune

**Files:**
- Create: `vaultkit/prune.py`
- Test: `tests/test_prune.py`

**Interfaces:**
- Consumes: `ingest_file` from Task 1 (tests); `catalog` from Task 2 (tests); `vendor.blobstore.BlobStore`
- Produces: `prune(store_root: str, keys: list[str]) -> int` — removes the named keys, returns how many actually existed.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_prune.py
from vaultkit.catalog import catalog
from vaultkit.ingest import ingest_file
from vaultkit.prune import prune


def test_prune_removes_and_counts(tmp_path):
    store_root = str(tmp_path / "store")
    a = tmp_path / "a.txt"
    a.write_bytes(b"x")
    ingest_file(store_root, str(a))
    removed = prune(store_root, ["a.txt", "never-there.txt"])
    assert removed == 1
    assert catalog(store_root) == []
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m pytest tests/test_prune.py -v`
Expected: FAIL (module missing)

- [ ] **Step 3: Implement**

```python
# vaultkit/prune.py
from vendor.blobstore import BlobStore


def prune(store_root, keys):
    """Delete the named keys; return the number that existed."""
    store = BlobStore(store_root)
    removed = 0
    for key in keys:
        if store.delete(key):
            removed += 1
    return removed
```

- [ ] **Step 4: Run the tests, make sure they pass**

Run: `python3 -m pytest tests/test_prune.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add vaultkit/prune.py tests/test_prune.py
git commit -m "feat: prune stored blobs"
```

---

### Task 5: Pipeline

**Files:**
- Create: `vaultkit/pipeline.py`
- Test: `tests/test_pipeline.py`

**Interfaces:**
- Consumes: `ingest_file` (Task 1), `catalog` (Task 2), `export_bundle` (Task 3), `prune` (Task 4); `vendor.blobstore.BlobStore`
- Produces: `run_pipeline(store_root: str, src_dir: str, out_dir: str) -> dict` — ingests every regular file in `src_dir`, exports all stored blobs to `out_dir`, prunes keys ending in `.tmp`, and returns `{"ingested": int, "exported": int, "pruned": int}`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pipeline.py
import os
from vaultkit.pipeline import run_pipeline


def test_pipeline_end_to_end(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "keep.txt").write_bytes(b"keep")
    (src / "scratch.tmp").write_bytes(b"scratch")
    store_root = str(tmp_path / "store")
    out = str(tmp_path / "out")
    stats = run_pipeline(store_root, str(src), out)
    assert stats == {"ingested": 2, "exported": 2, "pruned": 1}
    assert sorted(os.listdir(out)) == ["keep.txt", "scratch.tmp"]


def test_pipeline_rerun_is_stable(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "keep.txt").write_bytes(b"keep")
    store_root = str(tmp_path / "store")
    out = str(tmp_path / "out")
    run_pipeline(store_root, str(src), out)
    stats = run_pipeline(store_root, str(src), out)
    assert stats == {"ingested": 1, "exported": 1, "pruned": 0}
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m pytest tests/test_pipeline.py -v`
Expected: FAIL (module missing)

- [ ] **Step 3: Implement**

```python
# vaultkit/pipeline.py
import os

from vaultkit.catalog import catalog
from vaultkit.export import export_bundle
from vaultkit.ingest import ingest_file
from vaultkit.prune import prune


def run_pipeline(store_root, src_dir, out_dir):
    """Ingest src_dir, export everything, prune *.tmp keys."""
    ingested = 0
    for name in sorted(os.listdir(src_dir)):
        path = os.path.join(src_dir, name)
        if os.path.isfile(path):
            ingest_file(store_root, path)
            ingested += 1
    keys = [e["key"] for e in catalog(store_root)]
    exported = export_bundle(store_root, keys, out_dir)
    pruned = prune(store_root, [k for k in keys if k.endswith(".tmp")])
    return {"ingested": ingested, "exported": exported, "pruned": pruned}
```

- [ ] **Step 4: Run the tests, make sure they pass**

Run: `python3 -m pytest tests/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add vaultkit/pipeline.py tests/test_pipeline.py
git commit -m "feat: end-to-end vault pipeline"
```
