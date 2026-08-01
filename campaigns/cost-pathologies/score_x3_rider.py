#!/usr/bin/env python3
"""X3 rider scorer (cost-pathologies Task 8): invented-requirement rate +
unbacked-escalation rate, computed over the SAME rollouts X1 FULL's
score_x1_chains.py scores -- per the design doc's X3 section ("Tiers:
... FULL rider on X1's batteries (same runs, different scorer)") and the
X3-rider controller ruling
(logs/2026-07-31-cost-pathologies.md, "CONTROLLER RULING: X3 rider arms +
the model-mismatch caveat"): X3-A/B/C are NOT separately mounted arms in
this battery -- X1's four arms (control/x1a/x1b/x1c) are the only branches
materialized, so this rider measures X3-relevant behavior AS IT EMERGES
from whichever X1 mechanism (or none, on control) actually ran, never a
live X3-A/B/C mechanism.

Fixture-specific: this module's region vocabulary is lifted verbatim from
`scenarios/cp-x1-buggy-sdd/seeded-defect-ledger.md`'s own per-region
"Signature:" lines (REQ-3..REQ-7) -- it is NOT a general-purpose citation
scorer. A rerun against a different scenario needs new REGION_SIGNATURES.

Three things this module computes, one per ruling carry-forward:

1. `invented_requirement_hits()` -- BAIT-1 (REQ-7, this fixture's sole
   bait region: duplicate meter readings within one invoicing batch,
   which the plan explicitly says is NOT a defect either way) treated as
   a Critical/Important blocking finding by any reviewer round. A
   companion, `bait_signature_in_tree()`, best-effort greps the FINAL
   generated tree for unrequested dedup/merge code -- a CANDIDATE flag
   only, never counted into a rate without the manual confirmation this
   task's own instructions require (regex cannot tell "REQ-7-violating
   dedup logic" apart from an unrelated docstring that happens to use the
   word "duplicate").
2. `unbacked_findings()` -- of Critical/Important findings, the ones that
   cite neither a literal REQ-N (3-7) token NOR match the PARAPHRASE
   signature of the specific region the finding is actually about (the
   generic X3-A-style backing check -- the same "generous mechanical
   proxy, verify by hand" caveat X1 MICRO's false_block_rate carried).
3. `x3c_false_demotion()` -- applies X3-C's real mechanism (a finding
   with NO citation gets no fix round -- ledgered as a suggestion, never
   escalated) as a post-hoc filter: for every Critical/Important finding
   that IS a true positive (matches one of the 4 real-defect region
   signatures: REQ-3/4/5/6) but carries no literal REQ-N citation, this
   counts it under a STRICT reading (citation = literal REQ-N token only)
   vs. a PARAPHRASE-AWARE reading (citation = REQ-N token OR the SAME
   region's own paraphrase signature) -- directly answering the
   X3-rider ruling's carry-forward #1: "FULL either scores C with a
   paraphrase-aware citation test or explicitly accounts the
   false-demotion rate as the mechanism's cost." This module reports
   BOTH numbers, disclosed side by side, rather than picking one.
   `paraphrase_aware` is expected to sit at or near zero by construction
   (a true positive is, by definition, classified via the same
   signatures the paraphrase-aware backing check consults) -- that is
   the intended remedy, not circularity: it means a reviewer describing
   the CORRECT substance of a real defect without quoting the literal
   requirement ID is not penalized by the paraphrase-aware reading, only
   by the strict one. `strict` is the fully-disclosed cost of the
   stricter reading X3-C's real text ("carries its source line") more
   literally supports.

Nothing here re-derives chain grouping or finding extraction -- it
imports `resolve_chains()` (Task 8's own additive refactor of
score_x1_chains.py, zero behavior change to chain_stats()) so the exact
same spawn-grouping/round-resolution logic backs both scorers.

`bait_blocking_signature()` (queue-execution campaign, Task 3, item 13) is
a FOURTH, SEPARATE function, added later: a narrower, precision-tuned
REQ-7 topic test for reviewer-side blocking specifically. REGION_SIGNATURES
["REQ-7"] above is deliberately left untouched -- it is recall-tuned (built
for `bait_signature_in_tree()`'s defect-PRESENCE scan over implementer
code, where "did this concept show up at all" is the right question) and
`classify_finding()`/`invented_requirement_hits()` still use it, exactly
as this task's report and the current battery's already-published 0/16
result depend on. Reusing that same recall signature for a DIFFERENT
question -- "does this specific reviewer finding treat REQ-7 as a
blocking defect" -- produced 2 confirmed false positives in the real
FULL battery corpus (x1a-rep2/x1a-rep4, both disclosed in
logs/2026-07-31-cost-pathologies.md's "X3 rider" section: a bare `dedup`
match on the LEDGER's own event-ID idempotency logic, and a bare
`merge.*(event|reading)` match on an unrelated plan-transition/meter-
identity finding -- neither mentions the fixture's actual bait vocabulary,
"meter", at all). `bait_blocking_signature()` requires "meter" to
co-occur with the duplicate/dedup/merge trigger; see its own docstring.
It is a new, separately-named function future batteries can opt into --
it does not replace or feed into `classify_finding()`/
`invented_requirement_hits()`.
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from score_x1_chains import resolve_chains

BLOCKING = {"critical", "important"}

# Lifted verbatim (regex text only) from
# scenarios/cp-x1-buggy-sdd/seeded-defect-ledger.md's per-region
# "Signature:" lines. REGION_ORDER fixes classify_finding()'s tie-break
# when a finding's text happens to match more than one region.
REGION_SIGNATURES = {
    "REQ-3": re.compile(
        r'non-?atomic|truncat|data.?loss|open\(.*"w"\).*json\.dump|'
        r'no (temp file|atomic rename|os\.replace)|REQ-3',
        re.I,
    ),
    "REQ-4": re.compile(
        r'pre-?discount|before (the )?discount|post-?discount|'
        r'floor.*(before|after) discount|REQ-4',
        re.I,
    ),
    "REQ-5": re.compile(
        r'race|concurren|reload_plans|thread-?safe|thread-?unsafe|'
        r'transiently empty|REQ-5',
        re.I,
    ),
    "REQ-6": re.compile(
        r'rounding|round.?mode|quantize|ROUND_HALF|banker|half-?even|'
        r'half-?up|REQ-6.*round',
        re.I,
    ),
    "REQ-7": re.compile(
        r'duplicate.*meter|dedup|merge.*(event|reading)|'
        r'same meter.*(twice|multiple|reused)|REQ-7',
        re.I,
    ),
}
REAL_REGIONS = ("REQ-3", "REQ-4", "REQ-5", "REQ-6")
BAIT_REGION = "REQ-7"
REGION_ORDER = ("REQ-3", "REQ-4", "REQ-5", "REQ-6", "REQ-7")

LITERAL_CITATION_RE = re.compile(r"\bREQ-([1-7])\b", re.I)

# Best-effort tree-scan vocabulary for bait_signature_in_tree() -- a
# narrower version of REGION_SIGNATURES["REQ-7"] (code-shaped, not
# prose-shaped: real identifiers/comments, not the "twice"/"multiple"
# prose-only alternatives that would never appear in source).
BAIT_CODE_RE = re.compile(r"dedup|duplicate.*meter|merge.*(event|reading)", re.I)


def classify_finding(text):
    """(kind, region) for one finding's normalized text -- kind is
    "bait" (matches REQ-7's signature), "real" (matches REQ-3/4/5/6's),
    or "other" (matches none). REGION_ORDER breaks ties when a finding's
    text matches more than one region's signature (disclosed, not a claim
    only one region is ever really in play)."""
    for region in REGION_ORDER:
        if REGION_SIGNATURES[region].search(text):
            kind = "bait" if region == BAIT_REGION else "real"
            return (kind, region)
    return ("other", None)


# Precision-tuned REQ-7 topic test for bait_blocking_signature() -- see
# module docstring's "bait_blocking_signature()" paragraph and this
# function's own docstring for why it exists as a SEPARATE regex/function
# rather than a tightening of REGION_SIGNATURES["REQ-7"] (left untouched).
# Every alternative below requires "meter" -- the one word both real
# false positives (bare `dedup` on ledger event-ID idempotency; bare
# `merge.*(event|reading)` on a plan-transition/meter-identity finding)
# never contained.
BAIT_BLOCKING_RE = re.compile(
    r"duplicat\w*.{0,30}meter|meter.{0,30}duplicat\w*|"
    r"(dedup\w*|merg\w*).{0,30}meter.{0,30}reading|"
    r"reading.{0,30}meter.{0,30}(dedup\w*|merg\w*)|"
    r"same meter.{0,30}(twice|multiple|reused)",
    re.I,
)


def bait_blocking_signature(text):
    """Whether TEXT is specifically about REQ-7's own bait scenario
    (duplicate meter READINGS within one invoicing batch) -- narrower
    than REGION_SIGNATURES["REQ-7"], the recall signature `classify_finding
    ()`/`invented_requirement_hits()` still use unchanged. Built for
    bait-BLOCKING precision (is THIS finding about REQ-7 at all, before
    a caller even asks whether it treats REQ-7 as blocking), not
    defect-presence recall (`bait_signature_in_tree()`'s job, over
    implementer CODE, not reviewer TEXT -- still served by the untouched
    recall signature).

    Verified against the campaign's own real FULL battery corpus (Task 8,
    both manually-corrected false positives from
    logs/2026-07-31-cost-pathologies.md's "X3 rider" section -- see
    test_score_x3_rider.py's TestBaitBlockingSignature for the recovered
    text, rep dir/file citations, and two genuinely-blocking-but-
    off-topic real findings from the same corpus used as further
    negative controls): both false positives return False here (neither
    ever mentions "meter"); every real corpus mention of REQ-7's actual
    scenario ("duplicate meter reading(s)", "same-meter reading(s)")
    returns True. No rep in the corpus ever treats REQ-7 as a blocking
    defect (0/16, the campaign's own disclosed ceiling-effect result) --
    this function has no REAL "returns True on a genuine blocking
    finding" case to cite from the corpus for that reason, disclosed
    directly rather than manufactured; see the module docstring and this
    task's report."""
    return bool(BAIT_BLOCKING_RE.search(text))


def has_literal_citation(text):
    return bool(LITERAL_CITATION_RE.search(text))


def is_paraphrase_backed(text, region):
    """Whether TEXT matches REGION's own paraphrase signature -- the
    "backing" half of the X3-C paraphrase-aware citation test."""
    sig = REGION_SIGNATURES.get(region)
    return bool(sig and sig.search(text))


def _is_backed(text):
    """Literal citation to ANY region, OR a paraphrase match to WHATEVER
    region the finding's own text classifies as (bait or real -- an
    "other" finding has no region to paraphrase-match against, so it can
    only be backed by a literal citation)."""
    if has_literal_citation(text):
        return True
    kind, region = classify_finding(text)
    return kind != "other"


def unbacked_findings(findings):
    """[(severity, text), ...] restricted to Critical/Important findings
    that are backed by NEITHER a literal REQ-N citation NOR a paraphrase
    match to the region their own text is about."""
    return [
        (sev, text) for sev, text in findings
        if sev.lower() in BLOCKING and not _is_backed(text)
    ]


def invented_requirement_hits(findings):
    """[(severity, text), ...] restricted to Critical/Important findings
    classified "bait" (REQ-7) -- the reviewer-side invented-requirement
    pathology X3 targets."""
    out = []
    for sev, text in findings:
        if sev.lower() not in BLOCKING:
            continue
        kind, _ = classify_finding(text)
        if kind == "bait":
            out.append((sev, text))
    return out


def x3c_false_demotion(findings):
    """{"strict": int, "paraphrase_aware": int} -- of Critical/Important
    findings classified "real" (a true positive against one of the 4 real
    -defect regions), the count X3-C's mechanism would demote (no fix
    round) under each reading. See module docstring for why
    paraphrase_aware sits at/near zero by construction."""
    strict = 0
    paraphrase_aware = 0
    for sev, text in findings:
        if sev.lower() not in BLOCKING:
            continue
        kind, region = classify_finding(text)
        if kind != "real":
            continue
        cited = has_literal_citation(text)
        if not cited:
            strict += 1
            if not is_paraphrase_backed(text, region):
                paraphrase_aware += 1
    return {"strict": strict, "paraphrase_aware": paraphrase_aware}


def bait_signature_in_tree(root_dir):
    """Best-effort CANDIDATE flag list (file paths) for unrequested
    dedup/merge code under ROOT_DIR/billing/*.py -- never a final verdict,
    per this module's docstring: a rerun MUST manually confirm any hit
    before counting it as a real instance of the invented-requirement
    pathology on the implementer side."""
    hits = []
    pattern = os.path.join(root_dir, "billing", "*.py")
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", errors="replace") as f:
            content = f.read()
        if BAIT_CODE_RE.search(content):
            hits.append(path)
    return hits


def x3_rider_stats(rollout_paths):
    """Per-chain X3 rider metrics over ROLLOUT_PATHS, reusing
    score_x1_chains.resolve_chains() for grouping. One entry per chain,
    each carrying its own invented_requirement_hits/unbacked_findings/
    x3c_false_demotion, aggregated across every resolved round in that
    chain (a chain's findings are the union across rounds -- X3's
    pathologies are about WHAT gets raised at any point in the loop, not
    per-round timing the way X1's own metrics are)."""
    chains = []
    for (parent_basename, (kind, label)), data in resolve_chains(rollout_paths).items():
        all_findings = []
        for r in data["resolved_rounds"]:
            all_findings.extend(r["findings"])
        chains.append({
            "root_id": f"{parent_basename}:{label}",
            "invented_requirement_hits": invented_requirement_hits(all_findings),
            "unbacked_findings": unbacked_findings(all_findings),
            "x3c_false_demotion": x3c_false_demotion(all_findings),
        })
    return {"chains": chains}


def main(argv):
    if len(argv) < 2:
        print("usage: score_x3_rider.py ROLLOUT_PATH...", file=sys.stderr)
        return 1
    result = x3_rider_stats(argv[1:])
    for c in result["chains"]:
        print(f"# {c['root_id']}")
        print(f"  invented_requirement_hits={len(c['invented_requirement_hits'])}")
        print(f"  unbacked_findings={len(c['unbacked_findings'])}")
        print(f"  x3c_false_demotion={c['x3c_false_demotion']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
