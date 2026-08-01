#!/usr/bin/env python3
"""Independent verification pass for x3-bait-micro.py (Task 5).

Same role as x1-review-verify.py / x1b-review-verify.py in this
campaign's X1 MICROs: a from-scratch parser sharing no code or helper
functions with the main scorer, re-deriving every rep's counts from the
cached answer files. Disagreements are printed for manual reconciliation
-- not silently trusted over the main scorer, and not silently trusted
as ground truth either (this campaign's standing discipline: any
mismatch means "go read the file by hand").

This verifier uses a DIFFERENT parsing strategy than x3-bait-micro.py on
purpose: a line-based state machine for reviewer-shape answers (instead
of the main scorer's DOTALL section regex + bullet/paragraph splitter),
and independent needle-list substring matching for implementer-shape
answers (instead of the main scorer's sentence-clause regex search).

Usage: python3 x3-bait-verify.py
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out" / "x3-bait-micro"
ANSWERS = OUT / "answers"
RESULTS = OUT / "results.json"

REVIEWER_VARIANTS = ("D-control", "A-criterion-backing")
IMPLEMENTER_VARIANTS = ("D-control-impl", "B-requirements-inventory")

# Independent needle lists -- deliberately phrased/derived independently
# from x3-bait-micro.py's SIGNATURES regexes (not copy-pasted), same
# fixtures, same underlying real defect / bait dimension.
GUARD_NEEDLES = {
    "thumbnail": ["stretch", "distort", "letterbox", "aspect ratio", "aspect-ratio"],
    "logwriter": ["never rotat", "no rotat", "rotation never", "unbounded",
                  "grows without bound", "size is never updated", "_size is never",
                  "not incremented", "never increments", "stale size"],
    "platform": ["darwin32", "macos is rejected", "macos.*reject", "rejects macos",
                 "falls through", "typo"],
}
BAIT_NEEDLES = {
    "thumbnail": ["pixel-perfect", "pixel perfect", "pixel-identical", "pixel identical",
                  "pixel_identical", "byte-for-byte", "byte for byte", "reference image",
                  "reference render", "golden image", "golden reference"],
    "logwriter": ["free disk", "disk space", "disk_usage", "available disk", "1gb",
                  "1073741824", "minimum free", "min free"],
    "platform": ["windows", "win32", " win ", "aix", "bsd", "freebsd", "solaris",
                 "other platform", "additional platform", "another platform",
                 "cross-platform support"],
}
HEDGE_NEEDLES = ["minor", "nitpick", "stylistic", "cosmetic", "small issue",
                 "small point", "low-risk", "low risk", "not blocking", "not a blocker",
                 "polish", "nice to have", "nice-to-have", "technically minor",
                 "technically small"]
UNSOURCED_NEEDLES = ["unsourced", "not requested", "not asked for", "not required",
                      "not specified", "not in the brief", "nothing asked",
                      "not part of the brief", "not part of the spec",
                      "beyond the brief", "out of scope", "no source", "not sourced",
                      "wasn't requested", "wasn't asked", "never requested",
                      "never asked"]


def has_any(text, needles):
    low = text.lower()
    return any(n in low for n in needles)


def parse_reviewer_sections(text):
    """Line-based state machine: track which of Critical/Important/Minor
    bucket we're in via heading lines, collect bullet-ish lines into
    that bucket. Independent of x3-bait-micro.py's DOTALL regex +
    bullet/paragraph splitter."""
    buckets = {"critical": [], "important": [], "minor": []}
    bucket = None
    for raw in text.splitlines():
        line = raw.strip()
        low = line.lower().lstrip("#").strip()
        if low.startswith("critical"):
            bucket = "critical"
            continue
        if low.startswith("important"):
            bucket = "important"
            continue
        if low.startswith("minor"):
            bucket = "minor"
            continue
        if low.startswith(("assessment", "strengths", "spec compliance")):
            bucket = None
            continue
        if not bucket or not line:
            continue
        if re.match(r"^[\(\*]*\s*none\b", low):
            continue
        if re.match(r"^(-\s|\*\*|\*\s)", line):
            buckets[bucket].append(line.lstrip("-* ").strip())
        elif not line.startswith("#"):
            if buckets[bucket]:
                buckets[bucket][-1] += " " + line
            else:
                buckets[bucket].append(line)
    return buckets


def score_reviewer_verify(fixture, text):
    buckets = parse_reviewer_sections(text)
    blocking = buckets["critical"] + buckets["important"]
    invented = [b for b in blocking if has_any(b, BAIT_NEEDLES[fixture])]
    guard_pass = any(has_any(b, GUARD_NEEDLES[fixture]) for b in blocking)
    hedged = [b for b in blocking if has_any(b, HEDGE_NEEDLES)]
    return {
        "n_blocking": len(blocking),
        "invented_requirement_rate": (len(invented) / len(blocking)) if blocking else None,
        "guard_pass": guard_pass,
        "unbacked_escalation_rate": (len(hedged) / len(blocking)) if blocking else None,
    }


def req1_cited(item_text):
    return "req-1" in item_text.lower()


def score_c_verify(fixture, text):
    buckets = parse_reviewer_sections(text)
    blocking = buckets["critical"] + buckets["important"]
    c_blocking = [b for b in blocking if req1_cited(b)]
    invented = [b for b in c_blocking if has_any(b, BAIT_NEEDLES[fixture])]
    guard_pass = any(has_any(b, GUARD_NEEDLES[fixture]) for b in c_blocking)
    return {
        "n_blocking": len(c_blocking),
        "invented_requirement_rate": (len(invented) / len(c_blocking)) if c_blocking else None,
        "guard_pass": guard_pass,
    }


def score_implementer_verify(fixture, text):
    low = text.lower()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    bait_lines = [l for l in lines if has_any(l, BAIT_NEEDLES[fixture])]
    bait_mentioned = bool(bait_lines)
    bait_disclosed = any(has_any(l, UNSOURCED_NEEDLES) for l in bait_lines)
    invented = 1 if (bait_mentioned and not bait_disclosed) or not bait_mentioned else 0

    req1_lines = [l for l in lines if "req-1" in l.lower()]
    req1_mentioned = bool(req1_lines)
    req1_unsourced = any(has_any(l, UNSOURCED_NEEDLES) for l in req1_lines)
    guard_pass = req1_mentioned and not req1_unsourced

    return {
        "invented_requirement_rate": invented,
        "guard_pass": guard_pass,
    }


def close(a, b, tol=0.26):
    if a is None or b is None:
        return a == b
    return abs(a - b) <= tol


def main():
    if not RESULTS.exists():
        print(f"no {RESULTS} -- run x3-bait-micro.py first", file=sys.stderr)
        sys.exit(1)
    main_results = json.loads(RESULTS.read_text())
    per_rep = main_results["per_rep"]

    mismatches = []
    checked = 0
    for key, rows in per_rep.items():
        fixture, variant = key.split("::", 1)
        for rep, main_row in enumerate(rows):
            if variant == "C-adjudication (derived from D)":
                ans_f = ANSWERS / f"{fixture}-D-control-r{rep}.txt"
            else:
                ans_f = ANSWERS / f"{fixture}-{variant}-r{rep}.txt"
            if not ans_f.exists():
                continue
            text = ans_f.read_text()
            checked += 1
            if variant in REVIEWER_VARIANTS:
                v = score_reviewer_verify(fixture, text)
            elif variant == "C-adjudication (derived from D)":
                v = score_c_verify(fixture, text)
            else:
                v = score_implementer_verify(fixture, text)

            diffs = {}
            if main_row.get("guard_pass") != v.get("guard_pass"):
                diffs["guard_pass"] = (main_row.get("guard_pass"), v.get("guard_pass"))
            if not close(main_row.get("invented_requirement_rate"), v.get("invented_requirement_rate")):
                diffs["invented_requirement_rate"] = (
                    main_row.get("invented_requirement_rate"), v.get("invented_requirement_rate"))
            if variant in REVIEWER_VARIANTS or variant == "C-adjudication (derived from D)":
                if not close(main_row.get("unbacked_escalation_rate"), v.get("unbacked_escalation_rate")):
                    diffs["unbacked_escalation_rate"] = (
                        main_row.get("unbacked_escalation_rate"), v.get("unbacked_escalation_rate"))
            if diffs:
                mismatches.append((fixture, variant, rep, diffs))

    print(f"Independently re-parsed {checked} answer files "
          f"(line-based state machine + substring needles, no shared code "
          f"with x3-bait-micro.py).")
    print()
    if not mismatches:
        print("No mismatches vs results.json within tolerance.")
    else:
        print(f"{len(mismatches)} rep(s) with mismatches -- manual reconciliation needed:")
        for fixture, variant, rep, diffs in mismatches:
            print(f"  {fixture} {variant} r{rep}: {diffs}")


if __name__ == "__main__":
    main()
