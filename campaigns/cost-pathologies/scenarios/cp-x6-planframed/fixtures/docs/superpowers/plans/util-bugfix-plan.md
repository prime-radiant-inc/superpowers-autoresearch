# Util Function Bugfixes — Plan

This project's `util/` directory has twelve independent bugs, one per
file, each a single small mistake (an off-by-one, a swapped branch, a
missing line, a wrong constant). `npm test` currently shows fourteen
failing assertions out of fifteen. This plan is twelve tasks, one per
bug — each task is a one-line fix to one existing file. No task creates
a new file, no task touches more than the one file it names, and no
task's fix touches any file another task's fix touches. Synthetic
fixture; no real system.

## Global Constraints

Node.js (ES modules), tests run via `npm test` (`node --test`). Every
task's fix is a body-only change to an existing exported function —
none of the twelve tasks changes a function's name or signature, and
none of them needs a new or updated test; the existing test for each
file already covers its fix.

## Task 1: Fix `average` in util/average.js

**Files:**

- Modify: `util/average.js`

**Implementation:** `average` divides by one more than the list length.
Divide by `nums.length` instead.

**Verification:** `node --test tests/average.test.js`

## Task 2: Fix `capitalize` in util/capitalize.js

**Files:**

- Modify: `util/capitalize.js`

**Implementation:** `capitalize` upper-cases the second character and
keeps the first character lowercase in the output. Upper-case
`s[0]` and append `s.slice(1)` instead.

**Verification:** `node --test tests/capitalize.test.js`

## Task 3: Fix `clamp` in util/clamp.js

**Files:**

- Modify: `util/clamp.js`

**Implementation:** `clamp` returns `min` when the input is above
`max`. Return `max` in that branch instead.

**Verification:** `node --test tests/clamp.test.js`

## Task 4: Fix `countVowels` in util/countVowels.js

**Files:**

- Modify: `util/countVowels.js`

**Implementation:** `countVowels` only matches lowercase vowels, so
uppercase vowels are never counted. Match both cases (e.g. extend the
vowel set to `"aeiouAEIOU"`).

**Verification:** `node --test tests/countVowels.test.js`

## Task 5: Fix `flattenOnce` in util/flattenOnce.js

**Files:**

- Modify: `util/flattenOnce.js`

**Implementation:** `flattenOnce` pushes a nested array as a single
element instead of spreading it one level. Spread the nested array's
elements into `out` instead of pushing the array itself.

**Verification:** `node --test tests/flattenOnce.test.js`

## Task 6: Fix `isEven` in util/isEven.js

**Files:**

- Modify: `util/isEven.js`

**Implementation:** `isEven` returns true for odd numbers and false for
even numbers — the comparison is inverted. Compare against `0`, not
`1`.

**Verification:** `node --test tests/isEven.test.js`

## Task 7: Fix `isPalindrome` in util/isPalindrome.js

**Files:**

- Modify: `util/isPalindrome.js`

**Implementation:** `isPalindrome` compares each character against one
index past its mirror position, an off-by-one. Compare `s[i]` against
`s[s.length - 1 - i]`.

**Verification:** `node --test tests/isPalindrome.test.js`

## Task 8: Fix `max` in util/max.js

**Files:**

- Modify: `util/max.js`

**Implementation:** `max` starts its running best at `0`, so an
all-negative input always returns `0` instead of the true maximum.
Start the running best at `-Infinity`.

**Verification:** `node --test tests/max.test.js`

## Task 9: Fix `reverseString` in util/reverseString.js

**Files:**

- Modify: `util/reverseString.js`

**Implementation:** `reverseString`'s loop condition stops one
character early and never appends index 0. Change the loop condition
so it includes index 0 (e.g. `i >= 0`).

**Verification:** `node --test tests/reverseString.test.js`

## Task 10: Fix `sum` in util/sum.js

**Files:**

- Modify: `util/sum.js`

**Implementation:** `sum` starts its running total at `1` instead of
`0`, so every result is off by one. Start the running total at `0`.

**Verification:** `node --test tests/sum.test.js`

## Task 11: Fix `truncate` in util/truncate.js

**Files:**

- Modify: `util/truncate.js`

**Implementation:** `truncate` keeps one character too many before
appending the ellipsis. Slice to exactly `n` characters (`s.slice(0,
n)`), not `n + 1`.

**Verification:** `node --test tests/truncate.test.js`

## Task 12: Fix `unique` in util/unique.js

**Files:**

- Modify: `util/unique.js`

**Implementation:** `unique` never marks a value as seen, so duplicates
are never filtered out. Add the value to the `seen` set when it is
first encountered.

**Verification:** `node --test tests/unique.test.js`

**Final verification:** `npm test` (all fifteen assertions across all
twelve files pass).
