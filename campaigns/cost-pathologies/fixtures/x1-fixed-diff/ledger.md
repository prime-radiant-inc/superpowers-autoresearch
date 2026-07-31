# Seeded-defect ledger — x1-fixed-diff

Answer key for the X1 MICRO. NEVER included in the reviewer prompt —
`x1-review-micro.py` reads this file only for scoring, after the model's
answer is already on disk. Five real defects of graded severity, plus
clean regions (the rest of the diff: `_round_money`, `_load`,
`_existing_receipt`, `process_batch`'s loop structure, the discount
catalog's values) that a well-calibrated reviewer should NOT flag as
blocking.

Each defect gets a `signature`: a short list of regex-friendly token
patterns the scorer greps for in a reviewer's finding text to credit a
match. A defect counts as found if the finding's combined text (location
+ description) matches at least one of its signature patterns AND is
sited at the right file (loose matching — this is a MICRO probe, not a
courtroom).

## D1 — Critical: non-atomic ledger write loses prior transactions

**Location:** `src/ledger.py:21-23`, the `_write` method.

```python
def _write(self):
    with open(self.path, "w") as f:
        json.dump(self.entries, f)
```

**Why it's real:** opening the ledger path in `"w"` mode truncates the
file to empty *before* `json.dump` runs. If the process is interrupted,
the disk fills, or `json.dump` raises for any reason partway through,
the file is left empty (or truncated) — every previously recorded
transaction is destroyed, with no temp file, no atomic rename, no
backup. Confirmed by direct repro: a second `record_transaction` call
that fails mid-`json.dump` (simulated `OSError`) leaves the ledger file
empty, discarding the first transaction that was already durably
"recorded" from the caller's point of view. This directly violates
REQ-4 ("a crash, a full disk, or an interrupted write must never
discard transactions that were already recorded").

**Severity:** Critical (data-loss path, reachable via any write failure
— disk full, kill -9, a future serialization bug — not a hypothetical).

**Signature (regex, case-insensitive):**
`non-?atomic|truncat|data.?loss|_write\b.*ledger|open\(.*"w"\).*json\.dump|json\.dump.*open\(.*"w"\)|no (temp file|atomic rename)|REQ-4`

## D2 — Critical: unhandled KeyError on unknown/expired discount code

**Location:** `src/discount.py:17-24` (`get_discount_percent`, the
`DISCOUNT_CODES[code]` lookup at line 23) and `src/discount.py:27-35`
(`apply_discount`, which does not catch it) — propagates uncaught
through `src/service.py:23` (`process_order`) and therefore through
`process_batch`.

**Why it's real:** `DISCOUNT_CODES[code]` is a direct dict subscript,
not `.get()` or a membership check. An unknown or typo'd code raises
`KeyError`, and nothing in `apply_discount`, `process_order`, or
`process_batch` catches it — the exception propagates all the way out.
Confirmed by direct repro: `apply_discount(Decimal("50.00"), "NOPE")`
raises `KeyError: 'NOPE'` uncaught. This directly violates REQ-1 ("MUST
be rejected with a caught, reported error — never allowed to propagate
as an unhandled exception"). It is also a batch-processing hazard:
`process_batch` loops calling `process_order`, so one bad code partway
through a batch crashes the whole batch with no indication of which
earlier orders in the batch were already ledgered.

**Severity:** Critical (unhandled exception on ordinary bad input — a
typo'd or expired code is a normal occurrence, not an edge case).

**Signature (regex, case-insensitive):**
`keyerror|unhandled exception|uncaught|discount_codes\[|not caught|crashes? the (batch|process|service)|REQ-1`

## D3 — Important: minimum-charge floor checked pre-discount, not post-discount

**Location:** `src/service.py:19-21` (`process_order`):

```python
subtotal = order["subtotal"]
if subtotal < MIN_CHARGE:
    raise ValueError(...)
```

**Why it's real:** the check compares `subtotal` (the pre-discount
amount) against `MIN_CHARGE`, then applies the discount afterward at
line 23. REQ-5 explicitly states the floor "applies to the POST-DISCOUNT
charged amount, not the pre-discount subtotal." Confirmed by direct
repro: an order with `subtotal=Decimal("5.00")` and code `"VIP90"` (90%
off) charges `Decimal("0.50")` — well under the $1.00 floor — and is
NOT rejected, because the pre-discount subtotal ($5.00) clears the
check. No crash; a clean, provable spec deviation.

**Severity:** Important (spec violation, real charged-amount defect, no
crash).

**Signature (regex, case-insensitive):**
`pre-?discount|before (the )?discount|post-?discount|subtotal.*MIN_CHARGE|minimum.*(before|after) discount|REQ-5`

## D4 — Important: idempotency (REQ-3) has zero test coverage

**Location:** `tests/test_service.py` (the whole file) — no test calls
`process_order` twice with the same `order_id`.

**Why it's real:** REQ-3 explicitly requires idempotent retry handling,
and `process_order`/`Ledger.has_order` implement it — but nothing in
the new test file exercises it. All four tests
(`test_apply_discount_save10`, `test_process_order_happy_path`,
`test_process_order_rejects_below_minimum`,
`test_process_batch_multiple_orders`) use distinct `order_id`s and never
call `process_order` a second time with a repeated one. This is a
genuine coverage gap on an explicitly required, newly-added behavior —
the base reviewer rubric's Tests section ("Are the task's edge cases
covered?") calls exactly this out.

**Severity:** Important (missing covering test for an explicitly
required behavior — a quality/testing finding, not a proven functional
bug: the idempotency code itself is correct as written).

**Signature (regex, case-insensitive):**
`idempotenc|no test.*(retry|duplicate|repeat)|retry.*(not|no).*test|missing (test|coverage).*(idempoten|retry|duplicate|repeat|REQ-3)|REQ-3.*(test|coverage)`

## D5 — Minor: `get_discount_percent` is misleadingly named

**Location:** `src/discount.py:17-24`.

**Why it's real:** the function is named `get_discount_percent` but
returns the discount *fraction* (e.g. `Decimal("0.15")` for a 15%
code), not the percent (`15`). Every current caller already expects the
fraction, so this causes no bug today — it's a naming/readability
issue: a future caller reading the name alone would reasonably expect
`15`, not `0.15`.

**Severity:** Minor (naming drift, no correctness impact, nice-to-have).

**Signature (regex, case-insensitive):**
`get_discount_percent.*(name|misleading|fraction)|misleading.*name|(name|naming).*(misleading|percent)|percent.*(but|actually|really).*(fraction|decimal)`

## Clean regions (should NOT be flagged as blocking)

`_round_money` (correct half-up rounding to cents), `_load` (correct —
absent file returns `[]`), `_existing_receipt` (correct — matches by
`str(order_id)`, consistent with `has_order`), the `DISCOUNT_CODES`
catalog values, `process_batch`'s loop structure, and `has_order`'s
`str()`-cast comparison (this IS correct — it's the *test coverage* for
this path that's missing, not the logic; see D4). A well-calibrated
reviewer should not produce a blocking (Critical/Important) finding
against any of these.
