#!/usr/bin/env python3
"""Independent verification pass for x1-review-micro.py.

Re-parses every cached answer file in out/x1-review-micro/answers/ with a
DIFFERENT algorithm than the main scorer -- a line-by-line state machine
instead of x1-review-micro.py's DOTALL section-regex + finding-splitter --
and recomputes recall / false-block-rate / stop per rep from scratch. It
never imports or calls anything from x1-review-micro.py. Any rep where
this script's numbers disagree with results.json is printed under
MISMATCH for manual reconciliation; it is not treated as ground truth
over the main scorer, just as a second, independent check on it (the
"regex-scored + manual reconciliation" convention this campaign's other
scorers use -- see logs/2026-07-31-cost-pathologies.md's Task 2 entry).

Usage: python3 x1-review-verify.py
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out" / "x1-review-micro"
ANSWERS = OUT / "answers"
RESULTS = OUT / "results.json"

# Same defect signatures as the ledger (fixtures/x1-fixed-diff/ledger.md)
# and the main scorer -- duplicated on purpose so this file has no import
# dependency on x1-review-micro.py's parsing code, only on the shared
# answer key.
DEFECT_SIGNATURES = {
    "D1-atomic-write": [
        "non-atomic", "nonatomic", "truncat", "data loss", "data-loss",
        "req-4",
    ],
    "D2-keyerror-crash": [
        "keyerror", "unhandled exception", "uncaught", "discount_codes[",
        "req-1",
    ],
    "D3-mincharge-order": [
        "pre-discount", "before the discount", "before discount",
        "post-discount", "req-5",
    ],
    "D4-idempotency-untested": [
        "idempotenc", "no test for", "not tested", "req-3",
    ],
    "D5-misleading-name": [
        "misleading", "get_discount_percent",
    ],
}

VARIANTS = ["D-control", "A-criterion-backing", "B-rising-floor", "C-marginal-value"]


def line_is_heading(line, *words):
    low = line.strip().lower().lstrip("#").strip()
    return any(low.startswith(w) for w in words)


def parse_answer(text):
    """Line-by-line state machine: track which of Critical/Important/Minor
    bucket we're in, and treat every line starting with '-' or '*' (after
    stripping leading whitespace) as one finding. No regex lookahead, no
    DOTALL span matching -- deliberately different machinery from the
    main scorer.
    """
    lines = text.splitlines()
    bucket = None
    buckets = {"critical": [], "important": [], "minor": []}
    task_quality = None
    another_round = None
    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        low = stripped.lower()
        if line_is_heading(stripped, "critical"):
            bucket = "critical"
            continue
        if line_is_heading(stripped, "important"):
            bucket = "important"
            continue
        if line_is_heading(stripped, "minor"):
            bucket = "minor"
            continue
        if line_is_heading(stripped, "assessment", "spec compliance", "strengths"):
            bucket = None
            continue
        if "**task quality:**" in low:
            if "approved" in low:
                task_quality = "Approved"
            elif "needs fixes" in low:
                task_quality = "Needs Fixes"
            continue
        if "**another round worth it:**" in low:
            # crude but independent: look at the first Yes/No token after
            # the marker on this line.
            after = low.split("**another round worth it:**", 1)[1]
            if re.search(r"\byes\b", after):
                another_round = "Yes"
            elif re.search(r"\bno\b", after):
                another_round = "No"
            continue
        if bucket and (stripped.startswith("-") or stripped.startswith("*")):
            buckets[bucket].append(stripped.lstrip("-* ").strip())
        elif bucket and stripped and not stripped.startswith("#"):
            # a continuation line of the current finding -- append to the
            # last item if one exists in this bucket, else start one
            # (covers non-bulleted prose findings).
            if buckets[bucket]:
                buckets[bucket][-1] += " " + stripped
            else:
                buckets[bucket].append(stripped)
    return buckets, task_quality, another_round


def matches_any(text, needles):
    low = text.lower()
    return any(n in low for n in needles)


def score_verify(variant_name, text):
    buckets, task_quality, another_round = parse_answer(text)
    all_items = buckets["critical"] + buckets["important"] + buckets["minor"]

    recalled = set()
    for item in all_items:
        for defect, needles in DEFECT_SIGNATURES.items():
            if matches_any(item, needles):
                recalled.add(defect)
    recall = len(recalled) / len(DEFECT_SIGNATURES)

    blocking = buckets["critical"] + buckets["important"]
    false_blocks = 0
    for item in blocking:
        low = item.lower()
        hit_ledger = any(matches_any(item, needles) for needles in DEFECT_SIGNATURES.values())
        cites_req = bool(re.search(r"\breq-[1-5]\b", low))
        has_fileline = bool(re.search(r"\b[\w./]+\.py:\d+\b", low))
        has_reach_word = any(w in low for w in ("reach", "trigger", "caller", "calling", "invoke"))
        backed = cites_req or (has_fileline and has_reach_word)
        if not hit_ledger and not backed:
            false_blocks += 1
    false_block_rate = (false_blocks / len(blocking)) if blocking else None

    if variant_name == "C-marginal-value":
        stop = (another_round == "No") if another_round else None
    elif variant_name == "B-rising-floor":
        stop = len(buckets["critical"]) == 0
    else:
        stop = (task_quality == "Approved") if task_quality else None

    return {
        "n_critical": len(buckets["critical"]),
        "n_important": len(buckets["important"]),
        "n_minor": len(buckets["minor"]),
        "recall": recall,
        "n_blocking": len(blocking),
        "n_false_blocks": false_blocks,
        "false_block_rate": false_block_rate,
        "task_quality": task_quality,
        "another_round": another_round,
        "stop": stop,
    }


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return a == b
    return abs(a - b) <= tol


def main():
    if not RESULTS.exists():
        print(f"no {RESULTS} -- run x1-review-micro.py first", file=sys.stderr)
        sys.exit(1)
    main_results = json.loads(RESULTS.read_text())
    per_rep = main_results["per_rep"]

    mismatches = []
    checked = 0
    for variant_name in VARIANTS:
        files = sorted(ANSWERS.glob(f"{variant_name}-r*.txt"))
        for f in files:
            rep = int(f.stem.rsplit("-r", 1)[1])
            main_row = per_rep.get(variant_name, [None] * (rep + 1))[rep]
            if main_row is None:
                continue
            text = f.read_text()
            v = score_verify(variant_name, text)
            checked += 1
            fields = ["n_critical", "n_important", "n_minor", "n_blocking",
                      "n_false_blocks", "task_quality", "another_round", "stop"]
            diffs = {}
            for field in fields:
                if main_row.get(field) != v.get(field):
                    diffs[field] = (main_row.get(field), v.get(field))
            if not close(main_row.get("recall"), v.get("recall"), tol=0.21):
                diffs["recall"] = (main_row.get("recall"), v.get("recall"))
            if not close(main_row.get("false_block_rate"), v.get("false_block_rate"), tol=0.21):
                diffs["false_block_rate"] = (main_row.get("false_block_rate"), v.get("false_block_rate"))
            if diffs:
                mismatches.append((variant_name, rep, diffs))

    print(f"Independently re-parsed {checked} answer files "
          f"(line-based state machine, no shared code with x1-review-micro.py).")
    print()
    if not mismatches:
        print("No mismatches vs results.json within tolerance "
              "(exact match on counts/labels; recall and false-block-rate "
              "within one finding's worth of disagreement).")
    else:
        print(f"{len(mismatches)} rep(s) with mismatches -- manual reconciliation needed:")
        for variant_name, rep, diffs in mismatches:
            print(f"  {variant_name} r{rep}: {diffs}")


if __name__ == "__main__":
    main()
