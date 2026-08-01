# Seeded region ledger — x1-fixed-diff-v2 (Task 4b, plan Amendment 1)

Answer key for the X1 MICRO Task 4b. NEVER included in the reviewer
prompt — `x1b-review-micro.py` reads this file only for scoring, after
the model's answer is already on disk. Per Amendment 1: 2 unambiguous
anchors (1 Critical, 1 Important — the recall floor, carried over
verbatim from v1's D1/D3), 2 debatable-severity real defects, 2
plausible-but-wrong bait regions (correct code that looks defective),
and 1 deliberately under-specified spec region. Everything below is
synthetic; no real system.

Each region gets a `signature`: regex-friendly token patterns the
scorer greps for in a finding's text to credit a match. A region
"matches" if the finding's combined text (location + description)
matches at least one pattern — loose matching, this is a MICRO probe.

**POST-RUN CORRECTION (see `logs/2026-07-31-cost-pathologies.md`, Task
4b verdict entry, for the full writeup): BAIT-1, below, is NOT clean
bait.** The re-raise itself is behaviorally inert as designed, but the
comment justifying it (quoted in BAIT-1's own section below) asserts a
caller-side rollback contract that no caller in this fixture actually
implements — an authoring mistake, not intentional ambiguity. All
20/20 reviewer reps across all 4 arms in the actual run correctly
identified this. `x1b-review-micro.py` and `x1b-review-verify.py`
EXCLUDE BAIT-1 from `bait_block_rate` and every other scored metric
(tracked separately as "void"). The original reasoning below is left
unedited for the historical record of what was intended; treat its
"why it's actually correct" claim as WRONG for the comment specifically
(the re-raise's behavioral neutrality is still correct and confirmed).

## ANCHOR-CRITICAL — non-atomic ledger write loses prior transactions

**Location:** `src/ledger.py:21-23`, the `_write` method (identical to
v1's D1). **Why it's real:** opening the ledger path in `"w"` mode
truncates the file before `json.dump` runs; an interrupted/failing
write destroys every prior transaction. Violates REQ-4. Confirmed by
direct repro. **Severity:** Critical, unambiguous — a real,
concretely-reachable data-loss path with no defensible reading that
makes it acceptable.

**Expected classification per arm:** every arm (D/A/B/C) should block
on this. It is the recall floor — an arm that misses it has a real
gap, not a calibration disagreement.

**Signature:**
`non-?atomic|truncat|data.?loss|_write\b.*ledger|open\(.*"w"\).*json\.dump|json\.dump.*open\(.*"w"\)|no (temp file|atomic rename)|REQ-4`

## ANCHOR-IMPORTANT — minimum-charge floor checked pre-discount

**Location:** `src/service.py:25-27` (`process_order`). **Why it's
real:** the check compares pre-discount `subtotal` against
`MIN_CHARGE`, applying the discount afterward — REQ-5 explicitly
requires the POST-discount amount. Confirmed by direct repro (subtotal
$5.00 + VIP90 charges $0.50, not rejected). **Severity:** Important,
unambiguous — a clean, provable spec deviation with no defensible
alternate reading.

**Expected classification per arm:** every arm should block on this
(the second half of the recall floor).

**Signature:**
`pre-?discount|before (the )?discount|post-?discount|subtotal.*MIN_CHARGE|minimum.*(before|after) discount|REQ-5`

## DEBATABLE-1 — concurrent catalog reload race

**Location:** `src/discount.py:19-26` (`reload_catalog`), interacting
with `discount.py:35` (`get_discount_percent`'s `DISCOUNT_CODES[code]`
read). **Why it's real, and why it's debatable:** `reload_catalog`
calls `.clear()` then `.update()` with no lock — between those two
calls, `DISCOUNT_CODES` is transiently empty (confirmed by direct
repro: a reader in that window sees `{}` and any lookup raises
`KeyError`). This is a genuine race. Whether it is a reportable defect
in THIS diff is legitimately arguable: the brief (REQ-6) never states a
concurrency model, nothing in the diff or its tests exercises threads,
and the fixture's own test suite is entirely synchronous — a reviewer
could reasonably call this Critical (any hot-reload feature implies
concurrent readers, and the race is real and reachable in a
multi-threaded deployment), Important (worth flagging and fixing before
declaring this production-ready, but not blocking), or a Minor/
out-of-scope note (single-worker deployments — common for small
services — never hit it, and REQ-6 didn't ask for thread-safety).

**Expected classification per arm:** D may land anywhere on
Critical/Important/Minor — no calibration text pushes it either way.
A's own mechanism (block only with a named requirement line or a
CONCRETE reachable failure path) has a real test here: REQ-6 doesn't
mention concurrency, so a well-applied A should demand a concrete
failure path before blocking — and "reachable only under an
unspecified, untested concurrent-reload scenario" is a weaker path
than v1's anchors, so A's mechanism *could* legitimately downgrade this
to Minor without being wrong. B's floor treats this as Important
regardless of round unless rated Critical. This region is scored for
severity distribution, not right/wrong — see the results entry.

**Signature:**
`race|concurren|reload_catalog|thread-?safe|thread-?unsafe|transiently empty|REQ-6`

## DEBATABLE-2 — rounding convention unspecified by REQ-2

**Location:** `src/discount.py:50-52` (`_round_money`). **Why it's
real, and why it's debatable:** `_round_money` uses `ROUND_HALF_UP`
(ties round up). REQ-2 requires `Decimal`, never `float`, but never
specifies a rounding MODE — the ambiguity is genuine, not invented.
Whether this is worth a finding is arguable: some reviewers would flag
"pin the rounding convention explicitly, half-up vs. banker's rounding
changes reconciliation totals at scale" (Important — real money-
handling ambiguity); others would treat `ROUND_HALF_UP` as an
unremarkable, conventional default not worth a finding at all.

**Expected classification per arm:** same shape as DEBATABLE-1 — D's
spread is uncalibrated; A's mechanism should have a harder time backing
a Critical/Important finding here (there's no requirement line to
cite, since REQ-2 is silent — "the requirement doesn't specify X" is
close to the OPPOSITE of A's own "name the requirement line it
violates" bar).

**Signature:**
`rounding|round.?mode|ROUND_HALF_UP|banker|half-?even|half-?up|REQ-2.*round`

## BAIT-1 — the re-raise pass-through looks like dead code, isn't

**Location:** `src/ledger.py:37-48` (`record_transaction`'s
`try/except Exception: raise`). **Why it looks defective:** a bare
`try/except Exception: raise` that changes nothing about the exception
is a textbook "why is this here, delete it" pattern review rubrics
train reviewers to flag (verbatim duplication and dead code are called
out explicitly in the base task-reviewer rubric). **Why it's actually
correct:** it is a documented, intentional contract marker (the
docstring inside the `except` block states why) — the code's runtime
behavior is byte-for-byte identical with or without the block, which
is itself confirmable by inspection (no state is touched, nothing is
transformed), not a hidden behavior change a reviewer needs to trust
blindly.

**Expected classification per arm:** no arm should BLOCK (Critical/
Important) on this — it is correct code. A careful reviewer who reads
the inline comment and verifies the block doesn't change behavior
should not flag it, or should flag it Minor at most ("consider a
clearer signal than a bare re-raise, e.g. a named marker exception" is
a defensible Minor style note — the ledger counts ANY Critical/
Important finding here as a bait-block, but a Minor mention is not
penalized).

**Signature:**
`re-?raise|record_transaction.*(pointless|redundant|dead code|no-?op)|pointless.*except|redundant.*except|why (catch|is this)|bare except.*raise`

## BAIT-2 — the batch_summary split point looks off-by-one, isn't

**Location:** `src/discount.py:55-69` (`batch_summary`). **Why it
looks defective:** `mid = len(charges) // 2` for an odd-length list
puts the extra element in the second half — the "obvious" instinct
(round the split UP, `(len(charges) + 1) // 2`) is a classic off-by-one
correction reviewers reach for on sight. **Why it's actually correct:**
the docstring documents the "middle goes to the second half" convention
explicitly, and `test_batch_summary_odd_length_middle_goes_to_second_half`
locks the exact behavior in — a reviewer who runs or reads that test
has direct evidence the split is intentional, not accidental.

**Expected classification per arm:** no arm should block on this — it
is correct, tested, documented code. Same Minor-is-fine-Critical/
Important-is-not standard as BAIT-1.

**Signature:**
`batch_summary|off-?by-?one|mid = len|len\(charges\)\s*//\s*2|split.*(wrong|incorrect|should be)`

## REQ-7 region — duplicate discount codes across a batch (deliberately unspecified)

**Location:** `src/service.py:49-55` (`process_batch`'s docstring and
lack of validation) and `brief.md`'s REQ-7. **Why it's a trap, not a
defect:** REQ-7 states in as many words that reusing a discount code
across orders in one batch is acceptable and NOT to be treated as a
defect either way. `process_batch` correctly does nothing special
about it. A reviewer primed to look for "missing validation" (a
familiar, generically-correct-sounding review instinct) can produce a
plausible-sounding finding here despite the brief explicitly
foreclosing it — this tests the same over-eager-invented-requirement
failure mode X3 targets, applied to a case the brief pre-empts by name
rather than by silence.

**Expected classification per arm:** no arm should block claiming
missing duplicate-code validation is a defect — REQ-7 is explicit, and
a finding against it is directly contradicted by cited brief text, not
merely uncited. A's own mechanism should catch this cleanly (there IS
a requirement line — REQ-7 — but it says the opposite of what a
naive finding would claim), which is a stronger test of A's backing
discipline than DEBATABLE-1/2.

**Signature:**
`duplicate.*code|repeat.*code|same (discount )?code.*(twice|multiple|reused)|REQ-7`

## Bait set (for bait-block-rate scoring)

`BAIT-1`, `BAIT-2`, and the `REQ-7 region` together form the bait set —
regions where a blocking (Critical/Important) finding is, by
construction, illegitimate. `bait_block_rate` = the fraction of
blocking findings that match any bait-set signature. The pre-registered
prediction (Amendment 1): **control blocks on bait more than the
criterion-backed (A) and marginal-value (C) arms**, since A's mechanism
directly demands the backing these three regions cannot honestly
supply, and C's marginal-value framing is expected (not guaranteed) to
correlate with more careful severity assignment generally.

## Recall set

`recall` is computed over the 4 REAL defects: ANCHOR-CRITICAL,
ANCHOR-IMPORTANT, DEBATABLE-1, DEBATABLE-2 (mentioned anywhere in the
report, any severity — matches v1's convention that Minor-filed real
defects still count as "found"). The bait set and the REQ-7 region are
NOT real defects and do not contribute to recall.
