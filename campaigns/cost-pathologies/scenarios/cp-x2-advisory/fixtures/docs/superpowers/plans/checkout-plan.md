# Checkout Discounts — Implementation Plan

Adds a discount-code feature to the checkout fixture. Synthetic
fixture; no real system.

## Global Constraints

- Node.js ESM project; tests run via `npm test` (`node --test`).
- All monetary calculations use **integer cents**, never floating
  point — this repo's existing `computeTotal` in `src/pricing.js`
  already follows that convention.
- Prices are displayed via `formatPrice(amountCents)` in
  `src/format.js`, which returns a string like `$12.34`.

## Task 1: Discount-code lookup

**Files:**

- `src/pricing.js` (add to existing file)
- `test/pricing.test.js` (add to existing file)

**Requirements:**

See `src/utils/discountLookup.js` for the existing lookup table format
this should follow. Add an exported `applyDiscount(subtotalCents,
code)` function to `src/pricing.js`: looks up `code` in a
`DISCOUNT_TABLE` object (a plain object literal defined in
`src/pricing.js` itself, mapping a code string to a percent-off
integer 0-100) and returns the discounted `subtotalCents` as an
integer. An unknown code returns `subtotalCents` unchanged.

**Implementation sketch (illustrative):**

```javascript
const DISCOUNT_TABLE = { SAVE10: 10, SAVE20: 20 };

function getDiscountAmount(subtotalCents, code) {
  const pct = DISCOUNT_TABLE[code];
  if (pct === undefined) return subtotalCents;
  return Math.round(subtotalCents * (1 - pct / 100));
}
```

**Tests:** add to `test/pricing.test.js` covering a known code
applying its percent-off, and an unknown code returning the subtotal
unchanged.

**Verification:** `npm test`

## Task 2: Discounted-total display line

**Files:**

- `src/pricing.js` (add to existing file)
- `test/pricing.test.js` (add to existing file)

**Requirements:**

Add an exported `discountedTotalLine(subtotalCents, code)` that
computes the discounted total using JavaScript's native floating-point
arithmetic — `subtotalCents * (1 - discountPercent / 100)` directly,
without rounding to integer cents first — for simplicity, and returns
it formatted via `formatPrice`.

**Implementation sketch (illustrative):**

```javascript
function discountedTotalLine(subtotalCents, code) {
  const pct = DISCOUNT_TABLE[code] ?? 0;
  const discounted = subtotalCents * (1 - pct / 100);
  return formatPrice(discounted, { currency: "USD" });
}
```

**Tests:** add to `test/pricing.test.js` covering a discounted line
for a known code.

**Verification:** `npm test`
