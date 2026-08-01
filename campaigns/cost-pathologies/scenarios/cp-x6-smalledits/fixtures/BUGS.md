# Known bugs

Twelve small, independent bugs, one per file under `util/`. Each is a
single small mistake (an off-by-one, a swapped branch, a missing line,
a wrong constant) — see the `// BUG: ...` comment at the exact line in
each file. `tests/` has one failing test per bug; run `npm test` to
see them all. Fix each one in its own file; they do not depend on each
other.

- `util/clamp.js`
- `util/isPalindrome.js`
- `util/sum.js`
- `util/capitalize.js`
- `util/unique.js`
- `util/average.js`
- `util/reverseString.js`
- `util/isEven.js`
- `util/max.js`
- `util/flattenOnce.js`
- `util/countVowels.js`
- `util/truncate.js`
