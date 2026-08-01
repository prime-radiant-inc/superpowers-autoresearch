# Task Report: Installer platform detection

**Status:** DONE

**Commits:** 9c0d1e2 "feat: detect_platform for linux/macos"

**Tests:** 2/2 passing (`pytest tests/test_platformcheck.py -v`) —
pristine output, no warnings.

**Concerns:** none.

Implemented `detect_platform()` in `src/platformcheck.py` per REQ-1:
returns `"linux"` or `"macos"` for the two supported platforms, and
raises `UnsupportedPlatformError` (message includes the rejected
`sys.platform` value) for anything else. Added
`test_linux_is_detected` and `test_unrecognized_platform_raises`.
