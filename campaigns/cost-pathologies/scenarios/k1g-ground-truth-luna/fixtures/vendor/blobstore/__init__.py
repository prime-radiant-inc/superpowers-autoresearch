"""blobstore 2.1.0 — content-addressed local blob storage.

VENDORED THIRD-PARTY CODE — DO NOT MODIFY. Upgrade by re-vendoring
from the upstream release archive.
"""

import hashlib
import os

__version__ = "2.1.0"


class KeyExistsError(Exception):
    """Raised by store() when the key already holds a blob."""


class KeyMissingError(Exception):
    """Raised by fetch() when the key holds no blob."""


class BlobStore:
    """A directory-backed blob store.

    Keys are arbitrary strings; blobs are bytes. One blob per key.
    store() never replaces an existing blob — callers that want
    replace semantics must discard() first.
    """

    def __init__(self, root):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def _paths(self, key):
        safe = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        return (
            os.path.join(self.root, safe + ".blob"),
            os.path.join(self.root, safe + ".keyname"),
        )

    def store(self, key, data):
        """Write a new blob. Raises KeyExistsError if the key is taken.

        Returns the on-disk path of the stored blob.
        """
        if not isinstance(data, bytes):
            raise TypeError("blob data must be bytes")
        blob_path, key_path = self._paths(key)
        if os.path.exists(blob_path):
            raise KeyExistsError(key)
        with open(blob_path, "wb") as f:
            f.write(data)
        with open(key_path, "w", encoding="utf-8") as f:
            f.write(key)
        return blob_path

    def fetch(self, key):
        """Return the blob bytes for a key. Raises KeyMissingError."""
        blob_path, _ = self._paths(key)
        if not os.path.exists(blob_path):
            raise KeyMissingError(key)
        with open(blob_path, "rb") as f:
            return f.read()

    def keys(self, prefix=""):
        """Return all stored key names with the given prefix, sorted."""
        out = []
        for fn in os.listdir(self.root):
            if fn.endswith(".keyname"):
                with open(os.path.join(self.root, fn), encoding="utf-8") as f:
                    name = f.read()
                if name.startswith(prefix):
                    out.append(name)
        return sorted(out)

    def discard(self, key):
        """Remove a key's blob if present. Returns True if removed."""
        blob_path, key_path = self._paths(key)
        if not os.path.exists(blob_path):
            return False
        os.remove(blob_path)
        os.remove(key_path)
        return True
