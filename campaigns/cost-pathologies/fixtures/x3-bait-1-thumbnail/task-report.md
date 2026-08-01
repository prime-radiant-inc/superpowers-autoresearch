# Task Report: Aspect-preserving thumbnail resize

**Status:** DONE

**Commits:** a1b2c3d "feat: thumbnail resize_to_fit"

**Tests:** 2/2 passing (`pytest tests/test_resize.py -v`) — pristine
output, no warnings.

**Concerns:** none.

Implemented `resize_to_fit(image, target_w, target_h)` in `src/resize.py`
using a nearest-neighbor resampler (`_nearest_neighbor_scale`) shared by
the public entry point. The output is always exactly `target_w` x
`target_h` pixels. Added `test_output_matches_target_dimensions` and
`test_square_source_into_square_target_is_unchanged_color` to cover the
dimension contract and a same-aspect-ratio case.
