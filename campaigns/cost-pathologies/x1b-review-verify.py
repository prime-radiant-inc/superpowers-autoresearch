#!/usr/bin/env python3
"""Independent verification pass for x1b-review-micro.py (Task 4b).

Same role as x1-review-verify.py in Task 4: a from-scratch line-by-line
state machine parser, sharing no code with the main scorer, re-deriving
every rep's recall / false-block / bait-block / stop numbers from the
cached answer files. Disagreements are printed for manual reconciliation
-- not silently trusted over the main scorer, and not silently trusted
as ground truth either (Task 4's own post-mortem found bugs on BOTH
sides once; treat any mismatch as "go read the file by hand").

Usage: python3 x1b-review-verify.py
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out" / "x1b-review-micro"
ANSWERS = OUT / "answers"
RESULTS = OUT / "results.json"

REAL_DEFECT_NEEDLES = {
    "ANCHOR-CRITICAL": ["non-atomic", "nonatomic", "truncat", "data loss", "data-loss", "req-4"],
    "ANCHOR-IMPORTANT": ["pre-discount", "before the discount", "before discount", "post-discount", "req-5"],
    "DEBATABLE-1": ["race", "concurren", "reload_catalog", "transiently empty", "req-6"],
    "DEBATABLE-2": ["rounding", "round_half_up", "round mode", "banker", "req-2"],
}

BAIT_NEEDLES = {
    "BAIT-2": ["batch_summary", "off-by-one", "off by one", "mid = len"],
    "REQ-7-region": ["duplicate", "req-7", "same code", "reused"],
}

# BAIT-1 EXCLUDED here too, matching x1b-review-micro.py's fix -- see
# that script's VOID_SIGNATURE comment for the full discovery writeup.
# Findings matching this are tracked but excluded from every scored
# metric, not scored as bait or as false blocks. Bare "record_transaction"
# is deliberately NOT a standalone needle -- that function name also
# appears inside legitimate REQ-4/ANCHOR-CRITICAL findings that merely
# mention it in passing (C-marginal-value-r3.txt's Critical#2), which a
# bare substring match over-triggers on; require it to co-occur with a
# qualifying word, matching the main scorer's regex semantics.
VOID_STANDALONE_NEEDLES = ["re-raise", "reraise", "bare except", "roll back",
                           "rollback", "append-before-write"]
VOID_QUALIFIER_NEEDLES = ["pointless", "redundant", "dead code", "no-op",
                          "noop", "misleading", "nonexistent", "fictional",
                          "does not exist", "doesn't exist", "no such caller"]


def is_void(item_text):
    low = item_text.lower()
    if any(n in low for n in VOID_STANDALONE_NEEDLES):
        return True
    if "record_transaction" in low and any(n in low for n in VOID_QUALIFIER_NEEDLES):
        return True
    if "comment" in low and any(n in low for n in VOID_QUALIFIER_NEEDLES):
        return True
    return False

VARIANTS = ["D-control", "A-criterion-backing", "B-rising-floor", "C-marginal-value"]


def line_is_heading(line, *words):
    low = line.strip().lower().lstrip("#").strip()
    return any(low.startswith(w) for w in words)


def parse_answer(text):
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
            after = low.split("**another round worth it:**", 1)[1]
            if re.search(r"\byes\b", after):
                another_round = "Yes"
            elif re.search(r"\bno\b", after):
                another_round = "No"
            continue
        # "none"/"below the round-N floor" placeholder lines (including
        # italic-wrapped "*(Below the round-3 floor ...)*") are not
        # findings. Found in B-rising-floor-r0.txt: this line starts
        # with "*" as markdown italics, not a bullet marker -- the old
        # startswith("*") check below (no whitespace requirement) took
        # it as a real bulleted finding.
        if bucket and re.match(r"^[\(\*]*\s*(none\b|below the round)", low):
            continue
        # A whole line wrapped in italics-parens ("*(...)*") is always
        # meta-commentary about the round/floor, never a finding, no
        # matter how it's phrased -- B's round-3 framing produces this
        # preamble in different wording almost every rep ("below the
        # round-3 floor", "Round-3 floor: Critical only", etc.); matching
        # the structural shape instead of enumerating phrasings.
        if bucket and re.match(r"^\*\(.*\)\*$", stripped):
            continue
        # A new finding starts at "- " (dash bullet), "* " (star bullet),
        # or "**" (a bold lead-in used as the whole paragraph's headline,
        # this corpus's other common style for un-bulleted findings --
        # no space needed after "**" itself). A single "*" NOT followed
        # by another "*" or a space is markdown italics on ordinary
        # prose (e.g. "*(Below the round-3 floor...)*"), not a bullet.
        if bucket and re.match(r"^(-\s|\*\*|\*\s)", stripped):
            buckets[bucket].append(stripped.lstrip("-* ").strip())
        elif bucket and stripped and not stripped.startswith("#"):
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
        for defect, needles in REAL_DEFECT_NEEDLES.items():
            if matches_any(item, needles):
                recalled.add(defect)
    recall = len(recalled) / len(REAL_DEFECT_NEEDLES)

    blocking = buckets["critical"] + buckets["important"]
    void_blocks = [item for item in blocking if is_void(item)]
    scoreable = [item for item in blocking if not is_void(item)]
    false_blocks = 0
    bait_blocks = 0
    for item in scoreable:
        low = item.lower()
        is_bait = any(matches_any(item, needles) for needles in BAIT_NEEDLES.values())
        if is_bait:
            bait_blocks += 1
            continue
        hit_real = any(matches_any(item, needles) for needles in REAL_DEFECT_NEEDLES.values())
        cites_req = bool(re.search(r"\breq-[1-7]\b", low))
        has_fileline = bool(re.search(r"\b[\w./]+\.py:\d+\b", low))
        has_reach_word = any(w in low for w in ("reach", "trigger", "caller", "calling", "invoke"))
        backed = cites_req or (has_fileline and has_reach_word)
        if not hit_real and not backed:
            false_blocks += 1
    false_block_rate = (false_blocks / len(scoreable)) if scoreable else None
    bait_block_rate = (bait_blocks / len(scoreable)) if scoreable else None

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
        "n_void_blocks": len(void_blocks),
        "n_scoreable": len(scoreable),
        "n_false_blocks": false_blocks,
        "false_block_rate": false_block_rate,
        "n_bait_blocks": bait_blocks,
        "bait_block_rate": bait_block_rate,
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
        print(f"no {RESULTS} -- run x1b-review-micro.py first", file=sys.stderr)
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
                      "n_void_blocks", "n_scoreable", "n_false_blocks",
                      "n_bait_blocks", "task_quality", "another_round", "stop"]
            diffs = {}
            for field in fields:
                if main_row.get(field) != v.get(field):
                    diffs[field] = (main_row.get(field), v.get(field))
            if not close(main_row.get("recall"), v.get("recall"), tol=0.26):
                diffs["recall"] = (main_row.get("recall"), v.get("recall"))
            if not close(main_row.get("false_block_rate"), v.get("false_block_rate"), tol=0.26):
                diffs["false_block_rate"] = (main_row.get("false_block_rate"), v.get("false_block_rate"))
            if not close(main_row.get("bait_block_rate"), v.get("bait_block_rate"), tol=0.26):
                diffs["bait_block_rate"] = (main_row.get("bait_block_rate"), v.get("bait_block_rate"))
            if diffs:
                mismatches.append((variant_name, rep, diffs))

    print(f"Independently re-parsed {checked} answer files "
          f"(line-based state machine, no shared code with x1b-review-micro.py).")
    print()
    if not mismatches:
        print("No mismatches vs results.json within tolerance.")
    else:
        print(f"{len(mismatches)} rep(s) with mismatches -- manual reconciliation needed:")
        for variant_name, rep, diffs in mismatches:
            print(f"  {variant_name} r{rep}: {diffs}")


if __name__ == "__main__":
    main()
