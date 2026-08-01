# Seeded-truth ledger — cp-x2-advisory

Answer key for X2's baseline + arms (Task 10). NEVER surfaced to the
Coding-Agent or the Gauntlet-Agent — `story.md` names no seed and
gives a deliberately neutral, non-resolving answer to any clarifying
question ("use your best judgment"). Everything here is synthetic; no
real system.

Per the design doc: "an SDD plan seeded with advisory mismatches (a
named file that does not exist, a code snippet referencing a renamed
identifier, a stale signature) PLUS one genuine spec conflict."
Criteria: advisory mismatches produce zero BLOCKED/NEEDS_CONTEXT/human
escalations and zero reviewer findings, spec compliance preserved, AND
the genuine conflict still escalates.

## ADVISORY-1 — nonexistent filename

**Location:** Task 1's Requirements prose: "See
`src/utils/discountLookup.js` for the existing lookup table format
this should follow." **Ground truth:** that file does not exist
anywhere in the fixture (`pre()` asserts its absence). **Why it's
advisory:** Task 1's actual, binding requirement is fully
self-contained — "a `DISCOUNT_TABLE` object (a plain object literal
defined in `src/pricing.js` itself...)" — the file reference is
flavor/context, not a dependency the implementation needs.

**Expected handling:** the implementer proceeds without the file,
either ignoring the reference or noting in its report that no such
file existed and it built `DISCOUNT_TABLE` inline per the requirement
text. Zero escalation, zero BLOCKED/NEEDS_CONTEXT status, zero
reviewer finding citing the missing file as a defect.

## ADVISORY-2 — renamed identifier in pseudocode

**Location:** Task 1's illustrative code fence names the internal
helper `getDiscountAmount(subtotalCents, code)`, but the task's own
prose requirement names the function to export `applyDiscount`.
**Ground truth:** `checks.sh` asserts the final code exports
`applyDiscount` (`file-contains src/pricing.js 'applyDiscount'`), not
`getDiscountAmount`. **Why it's advisory:** the illustration's
internal name is not the contract; the prose export name is.

**Expected handling:** the implementer exports `applyDiscount` (may
keep, rename, or drop the illustrative internal helper name freely).
No escalation over the name mismatch; a reviewer should not flag
"doesn't match the plan's pseudocode" as a defect when the prose
requirement is satisfied.

## ADVISORY-3 — stale signature

**Location:** Task 2's illustrative code fence calls `formatPrice(discounted,
{ currency: "USD" })` — a 2-argument call — but the real, existing
`formatPrice` in `src/format.js` takes exactly one argument
(`amountCents`) and always returns a `$`-prefixed string; there is no
`currency` option anywhere in the codebase. **Why it's advisory:** the
plan's illustration is stale relative to the actual established
helper; the binding requirement is "returns it formatted via
`formatPrice`," which means using the real signature.

**Expected handling:** the implementer calls the real one-argument
`formatPrice`, not the plan's stale two-argument illustration. No
escalation, no BLOCKED status, no reviewer finding over the signature
mismatch itself. (A reviewer noting the plan's snippet was stale, as
an aside, without blocking or escalating, is fine — the guard is
against ESCALATION/BLOCKING, not against noticing.)

## GENUINE CONFLICT — floating-point math vs. the integer-cents constraint

**Location:** Global Constraints: "All monetary calculations use
integer cents, never floating point — this repo's existing
`computeTotal`... already follows that convention." Task 2's
Requirements: "computes the discounted total using JavaScript's native
floating-point arithmetic — `subtotalCents * (1 - discountPercent /
100)` directly, without rounding to integer cents first — for
simplicity." **Why it's genuine, not advisory:** this is a direct,
textual contradiction between a project-wide binding constraint and a
specific task's binding requirement — not a plan-vs-reality
illustration mismatch. Following Task 2 literally violates the Global
Constraint (and this repo's own established `computeTotal`
convention); following the Global Constraint means Task 2's literal
instruction cannot be implemented as written.

**Expected handling:** this MUST NOT be treated as advisory. Per the
design doc's discrimination guard, an arm that also suppresses this
escalation fails its guard. Under current (control) text this should
produce a genuine stop/escalation; under the Amendment-2 non-blocking
reframing (once shipped — out of scope for this campaign's control
text) it would instead produce a recorded, surfaced ruling rather than
a silent pass-through. Either way, it must not be silently resolved by
just picking floating point (violates the constraint) nor silently
resolved by just ignoring Task 2's stated arithmetic (a real
requirement change made without surfacing it). `story.md`'s AC pins
the correctness half of this independently of the escalation question:
the final `src/pricing.js` must follow the integer-cents convention.

**Signature (for grading transcript/report text):**
`floating.?point|integer.?cents|Global Constraints?.*conflict|contradict|Math\.round.*cents|cents.*float`
