#!/usr/bin/env python3
"""X1 review-convergence chain scorer (cost-pathologies Task 2).

Design doc / hypothesis-log X1 section: "review chains that never
converge because strong reviewers always find something... Tiers: MINE
(chain-length / novel-finding-rate / severity-trend scorers validated on
the mined corpora)." This scorer builds that MINE-tier signal over
ROLLOUT_PATHS (a flat list -- the caller supplies whatever rollout files
are in scope), reusing `campaigns/codex-efficiency/rollout_parser.py`
(imported, not forked) for spawn/child resolution.

**What counts as one "chain"?** Per
`skills/subagent-driven-development/SKILL.md` and its `codex-tools.md`
reference (this repo's own, real dispatch convention, which the mined
corpus runs): "close reviewer subagents when their review returns" -- a
fix loop's review side dispatches a FRESH `spawn_agent` call every round
(never `resume_agent`), while the implementer side may be resumed or
fresh-dispatched depending on harness capability. A chain is therefore
built purely from spawn_agent calls under the SAME parent rollout, grouped
by `_chain_key()` -- a TWO-TIER heuristic, revised after manual corpus
reconciliation against a real mined session found the naive "group by
review-substring task_name stem" design badly undercounted a real chain
(see `logs/2026-07-31-cost-pathologies.md`'s corpus-validation entry for
this task):

1. **Numbered-task convention** -- a `task_name` starting `task<N>` (e.g.
   `task4_implementer`, `task4_spec_review_a`, `task4_spec_rereview_a`,
   ... through `task4_spec_veto_b`, a REAL 21-spawn chain found in the
   mined corpus whose later rounds are named `final`/`last`/`terminal`/
   `quality`/`qualityfix`/`py313`/`noring`/`veto` -- project-specific
   words with no shared lexical pattern a keyword regex could ever
   enumerate) groups EVERY spawn sharing that `task<N>` prefix, under one
   parent, into one candidate chain. Within the group (sorted by spawn
   timestamp), the CHRONOLOGICALLY FIRST entry is presumed to be the
   implementer dispatch and excluded from the round count -- UNLESS it is
   ITSELF review-shaped (see tier 2's test), in which case nothing is
   excluded. This is a positional heuristic, not semantic understanding:
   it can misclassify a group whose first entry isn't really an
   implementer, and if a harness cannot resume the implementer and must
   fresh-dispatch it for every fix round too (`codex-tools.md`'s
   documented fallback), those extra implementer dispatches land inside
   the round count as if they were review dispatches -- a documented,
   accepted MINE-tier imprecision, not a silent gap.
   A `task<N>`-prefixed group is reported as a chain only if it survives
   exclusion with >=1 remaining entry AND at least one entry anywhere in
   the group (before or after exclusion) is review-shaped -- a group of
   purely non-review numbered-task spawns (e.g. an implementer plus
   unrelated helper dispatches, no review activity at all) is not what
   X1 measures and is dropped.
2. **Everything else** -- a `task_name` NOT starting `task<N>` is only
   chain-eligible if it is itself review-shaped (`REVIEW_TASK_RE`,
   substring "review", case-insensitive -- real corpus examples:
   `auth_path_review`, `polling_snapshot_review`, `fp_task7_review`).
   Eligible entries are grouped by `_stem()` (strips a trailing
   `_r<N>`/`_round<N>`/`_rnd<N>`/`_<N>` suffix, so a repeated or
   round-numbered ad hoc review name still groups; see `_stem()`'s own
   docstring for the known limitation this leaves uncovered). No
   first-entry exclusion applies here -- every entry that passed the
   review-substring gate is a round.

**A fourth real pattern, orthogonal to the grouping above (item 12): a
re-tasked single thread.** Tiers 1/2 decide which SPAWNS belong to a
chain; separately, one already-grouped entry's OWN resolved child rollout
can itself carry more than one real review round if the harness re-tasked
that one thread in place (`followup_task`/`resume_agent`) instead of
issuing a fresh `spawn_agent` per round -- invisible to spawn-based
grouping entirely, since there is only ever one spawn_agent call to find.
The observable signature, read from the child's OWN transcript: more than
one `NEW_TASK`/`MESSAGE` inter-agent envelope addressed to itself
(`rollout_parser.inter_agent_messages()`, `recipient != "/root"` --
`_retask_envelope_count()`) alongside more than one
`event_msg/agent_message` `phase=="final_answer"` entry. Real corpus
exemplar: `durability_fix2_reviewer` in `cp-x1-buggy-sdd-x1a-rep1` -- one
`spawn_agent` call, two `NEW_TASK` envelopes, two distinct final-answer
verdicts ("ADDRESSED" then "APPROVED"). This is the ONLY such case found
across the archived 16-rep-dir X1 FULL corpus (both lanes --
`evals-lane-b/results/cp-x1-buggy-sdd-*` and
`superpowers/evals/results/cp-x1-buggy-sdd-*`) at the time this fix was
added: rare, not the "known absent" this task's own brief assumed going
in, so it doubles as this fix's real positive fixture (see
`test_score_x1_chains.py`'s retask-specific fixtures for a constructed
second example). When detected, EACH `final_answer` becomes its own
resolved round instead of collapsing to the last one, and `dispatch_count`
is bumped by the extra rounds found so `rounds <= dispatch_count` keeps
holding (see that field's own note below). See the `tokens_est` note
below for how each extra round's token contribution avoids double-
counting a re-tasked thread's own single, monotonically-climbing counter.

- **`dispatch_count`** is the size of the group AFTER whichever tier's
  exclusion rule applies (tier 1 may drop the presumed implementer; tier
  2 drops nothing), PLUS any extra rounds the fourth pattern above found
  within an entry's own resolved child -- every real review round found,
  whether from a fresh spawn_agent call or a re-task of an existing one,
  whether or not it ever resolved to a readable child rollout.
- **`rounds`** is the subset of those dispatches that DID resolve (a
  `child_links()`-linked child rollout present in ROLLOUT_PATHS, with at
  least one `phase=="final_answer"` message). `rounds <= dispatch_count`
  always; when they differ, that's an honest signal the given
  ROLLOUT_PATHS slice is incomplete (a pending dispatch, or a corpus
  slice missing that child file) -- never silently dropped.
- **`novel_finding_rate_per_round`** and **`severity_trend`** are computed
  only over the resolved rounds, in chronological (spawn-timestamp) order
  -- see `_extract_findings()` for how findings are pulled from each
  round's own final-answer text, and `_classify_severity_trend()` for the
  trend classification.
- **`tokens_est`** -- see that field's own note below; this is the field
  this task's brief specifically requires to document its cumulative-vs-
  exclusive convention.

**Finding extraction (`_extract_findings`)** is calibrated against this
repo's own, real reviewer templates (not invented): a round-1 review
follows `skills/subagent-driven-development/task-reviewer-prompt.md`'s
Output Format -- `#### Critical (Must Fix)` / `#### Important (Should
Fix)` / `#### Minor (Nice to Have)` HEADINGS, each followed by a bulleted
list of findings. A round-2+ re-review follows
`skills/subagent-driven-development/re-review-prompt.md`'s DIFFERENT
format instead -- a `### New Breakage in the Fix Diff` section whose
bullets tag severity INLINE, e.g. "(Critical/Important/Minor)", plus a
`### Finding Verdicts` section (ADDRESSED/NOT ADDRESSED per PRIOR
finding -- never counted here, since verdicts aren't new findings). A
THIRD real shape was found during this task's own corpus validation (a
real 2026-07-26 chain, "task6" in the log's validation table): neither
template, but a compact one-line "Critical: none. Minor: <value>."
summary with no heading or bullet markup at all -- `_bare_label_findings()`
handles this; a `none`/`none.` value (any case) is zero findings for that
severity, not a finding to count. `NONE_VALUE_RE` (item 11 fix) also
recognizes the prose-none variants real reviewers actually write instead
of the bare word -- "none identified [beyond X]" and "none beyond X"
(both verbatim/adapted from the archived X1 FULL corpus; see
`test_score_x1_chains.py`'s `TestExtractFindings` for the exact source
lines) and "no new findings" (named in this fix's own brief, not found
verbatim in the corpus) -- WITHOUT matching a value that merely starts
with "none" but goes on to describe a real (if soft) finding, e.g. the
real corpus line "None blocking. A direct unit test that `reload_plans`
removes stale IDs would strengthen catalog API coverage...", which must
still count. Each line is classified by exactly one
of the three shapes, priority heading > bare-label > list-item, so a
single line is never double-counted. A bullet/numbered list item's
severity comes from an inline severity word within its own text if
present, else from the most recent severity-named HEADING above it (reset
on any OTHER heading, so a stale section's severity can never leak past
a "### Strengths" or similar boundary). Known limitation: two findings
about the "same" underlying issue, reworded between rounds, will not be
recognized as the same finding (identity is exact normalized-text
equality) -- this makes `novel_finding_rate_per_round` a conservative
UPPER bound on true novelty, not an exact count; documented, not silently
assumed away. A further known limitation, also surfaced by corpus
validation: real reviewer output varies beyond even these three shapes
(free-form prose findings with no structural marker at all are invisible
to this scorer entirely) -- `_extract_findings()` is a calibrated
heuristic over observed formats, not a guarantee of full recall.

**`tokens_est` cumulative-vs-exclusive convention.** Each resolved round's
own child rollout's LAST `event_msg/token_count` event carries a
CUMULATIVE `total_token_usage.total_tokens` counter for that ONE rollout
file (see `score_x6_floor.py`'s module docstring for the same corpus
property, verified the same way). Naively SUMMING that cumulative counter
across every round in a chain would double-count whenever any round
inherited a prior round's history on fork (its own cumulative counter
already subsumes the earlier round's cost) -- exactly the pathology X4
measures. So: if EVERY resolved round in the chain has `fork_turns ==
"none"` (no round inherited any prior round's history), summing is safe
and `tokens_est` is the sum. If ANY round shows inheritance
(`fork_turns` is `"all"` or a numeric partial), `tokens_est` is instead
the MAX single-round cumulative total across the chain -- a documented,
deliberately conservative FLOOR (it can undercount true total spend when
inheritance is only partial) chosen because the brief's explicit
constraint is to never present a cumulative counter as if it were
exclusive, additive spend; undercounting is the safe-direction error, not
double-counting. Rounds with no `token_count` events at all contribute
nothing to either the sum or the max. `tokens_est` is `0` for a chain
with zero resolved rounds carrying any token data.

A re-tasked thread's own extra rounds (the fourth pattern above, item 12)
are tagged with a synthetic `"retasked"` `fork_turns` marker -- never a
real codex spawn_agent argument value -- specifically so this same
max-not-sum branch applies to them automatically: those rounds share ONE
continuous, monotonically-climbing counter (there is no fork between a
thread's own re-tasked rounds), so summing them would double-count for
the exact same reason summing forked rounds would. Every round EXCEPT
THE LAST gets its `tokens` value bounded to the cumulative reading AS OF
that round's own final-answer timestamp (`_cumulative_tokens_through()`),
so an earlier round's reading stays a true (smaller) prefix of a later
one rather than baking a later round's activity into an earlier round's
number. The LAST round instead uses the SAME unbounded whole-file
reading every non-retasked chain's single round already uses
(`cumulative_total_tokens()`) -- it has no next round to protect against
overlapping with, and any of the thread's own activity after its last
final answer (e.g. brief wrap-up) still legitimately belongs to it; using
the bounded reading there too would under-credit that tail and make a
retasked entry's own MAX inconsistent with how every other chain's
`tokens_est` is read from the exact same file shape.

Usage: `chain_stats(rollout_paths)`. Read-only; makes no writes.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "codex-efficiency"))
import rollout_parser as rp
from scorer_common import cumulative_total_tokens as _cumulative_total_tokens
from scorer_common import resolve_child_path as _resolve_child_path

REVIEW_TASK_RE = re.compile(r"review", re.I)

# Tier 1 of _chain_key(): the numbered-task convention observed directly
# in a real mined session (task4_implementer, task4_spec_review_a, ...,
# task4_spec_veto_b -- see module docstring).
TASK_ID_PREFIX_RE = re.compile(r"^(task\d+)", re.I)

# Strips a trailing round-number suffix delimited by _ or - (optionally
# prefixed "r"/"round"/"rnd") off a task_name to get its chain stem, e.g.
# "task1_reviewer_r2" -> "task1_reviewer", "task4_spec_round3" ->
# "task4_spec". Deliberately requires the delimiter: a trailing digit with
# no preceding _/- (e.g. "task1reviewer2") is NOT stripped, since that
# digit could just as easily be part of a word ("reviewer2" is not
# obviously "reviewer" + round "2") -- a known, documented limitation
# rather than a guess that could corrupt an unrelated word boundary.
ROUND_SUFFIX_RE = re.compile(r"[_-](?:r|round|rnd)?\d+$", re.I)

HEADING_SEVERITY_RE = re.compile(r"^\s*#{1,6}\s*\**\s*(Critical|Important|Minor)\b", re.I)
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+(.*\S)\s*$")
INLINE_SEVERITY_RE = re.compile(r"\b(Critical|Important|Minor)\b", re.I)
INLINE_SEVERITY_WINDOW = 80  # chars of a list item's own text searched for an inline tag

# Tier 3 of _extract_findings(): a compact "Severity: <value>" one-line
# summary format -- see _bare_label_findings()'s own docstring.
BARE_LABEL_RE = re.compile(r"\b(Critical|Important|Minor)\s*:\s*", re.I)

# Item 11 fix: recognizes the prose-none variants real reviewers write
# instead of the bare word -- calibrated against the only two real
# "none"-prefixed, non-exact bare-label values found across the archived
# 16-rep-dir X1 FULL corpus (see _bare_label_findings()'s own docstring
# for the exact source lines), plus "no new findings" (named verbatim in
# this fix's own brief, not found verbatim in the corpus). Each
# alternative is independently anchored (^...$) so "none blocking, but
# X..." -- a REAL soft finding that happens to start with "none" -- still
# falls through to a real match instead of being swallowed.
NONE_VALUE_RE = re.compile(
    r"^none\.?$"                                # bare "none" / "none."
    r"|^none\s+identified(?:\s+beyond\b.*)?$"    # "none identified[, beyond X]"
    r"|^none\s+beyond\b.*$"                      # "none beyond X"
    r"|^no\s+new\s+findings?\.?$",               # "no new findings"
    re.I,
)

SEVERITY_RANK = {"critical": 3, "important": 2, "minor": 1}


def _stem(task_name):
    return ROUND_SUFFIX_RE.sub("", task_name)


def _normalize(text):
    t = text.replace("**", "")
    t = re.sub(r"\s+", " ", t).strip()
    return t.lower()


def _bare_label_findings(line):
    """[(severity, normalized_content), ...] for every "Severity: <value>"
    segment on LINE, or `None` if LINE carries no bare-label segment at
    all -- a THIRD real-world report format found during this task's
    corpus validation (2026-07-26 task6 review chain; see module
    docstring / logs/2026-07-31-cost-pathologies.md), distinct from both
    task-reviewer-prompt.md's headings and re-review-prompt.md's inline
    tags: a compact one-line summary like "Critical: none. Minor: an
    unused import lingers." A segment whose value is empty, exactly
    "none"/"none.", or one of NONE_VALUE_RE's other recognized prose-none
    variants -- item 11 fix; real corpus examples: "none identified
    beyond the unresolved original durability finding."
    (cp-x1-buggy-sdd-x1a-rep1), "none beyond the critical durability
    defect." (adapted from cp-x1-buggy-sdd-x1c-rep1) -- contributes
    nothing to the returned list, since that IS the format's own way of
    reporting zero findings for that severity, not a finding to count
    (the line is still bare-label-shaped, so `None` is never returned in
    this case -- see the `None`-vs-`[]` note below). A value that merely
    starts with "none" but goes on to describe a real finding, e.g. the
    real corpus line "None blocking. A direct unit test that
    `reload_plans` removes stale IDs would strengthen catalog API
    coverage..." (cp-x1-buggy-sdd-x1c-rep3), still counts -- see
    NONE_VALUE_RE's own comment for how the boundary is drawn. Multiple
    label:value segments on one line (as in the real example above) are
    all captured, each bounded by the next label match or end of line.

    `None` (no bare-label segment matched at all) vs `[]` (a segment
    matched but every value was none-valued) is a deliberate, load-bearing
    distinction, NOT an implementation detail: `_extract_findings()` must
    treat a none-valued bare-label line as FULLY HANDLED (zero findings,
    stop) rather than falling through to LIST_ITEM_RE -- which would
    otherwise re-read the very same line as a list item, find the
    severity WORD sitting right there in "Critical: none identified...",
    and wrongly re-count it as a real finding. Collapsing this to a bare
    `[]`-is-falsy check was exactly item 11's second bug, uncovered only
    once NONE_VALUE_RE started actually matching more real none-valued
    lines (see `test_score_x1_chains.py`'s
    `test_bare_label_none_identified_beyond_excludes_zero_findings`,
    which reproduces it end to end)."""
    matches = list(BARE_LABEL_RE.finditer(line))
    if not matches:
        return None
    out = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(line)
        value = line[start:end].strip()
        if not value or NONE_VALUE_RE.match(value):
            continue
        out.append((m.group(1).title(), _normalize(value)))
    return out


def _extract_findings(text):
    """[(severity, normalized_text), ...] in text order -- see module
    docstring for the heading/inline/bare-label severity detection this
    implements and its calibration source. Each line is classified by
    exactly one of the three shapes (heading > bare-label > list-item, in
    that priority order) to avoid double-counting a single line's finding
    twice."""
    findings = []
    current_heading_severity = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            m = HEADING_SEVERITY_RE.match(line)
            current_heading_severity = m.group(1).title() if m else None
            continue
        bare = _bare_label_findings(line)
        if bare is not None:
            # `None` means no bare-label segment at all -- fall through to
            # LIST_ITEM_RE below. A (possibly empty) list means the line
            # WAS bare-label-shaped and is fully handled here, even if
            # every value was none-valued -- see _bare_label_findings()'s
            # own docstring for why treating `[]` as "unhandled" (item 11)
            # was itself a real bug.
            findings.extend(bare)
            continue
        item = LIST_ITEM_RE.match(line)
        if not item:
            continue
        content = item.group(1)
        inline = INLINE_SEVERITY_RE.search(content[:INLINE_SEVERITY_WINDOW])
        severity = inline.group(1).title() if inline else current_heading_severity
        if severity:
            findings.append((severity, _normalize(content)))
    return findings


def _round_max_severity_rank(findings):
    if not findings:
        return 0
    return max(SEVERITY_RANK[s.lower()] for s, _ in findings)


def _classify_severity_trend(seq):
    if len(seq) < 2:
        return "insufficient_data"
    if all(v == 0 for v in seq):
        return "no_findings"
    non_increasing = all(seq[i] >= seq[i + 1] for i in range(len(seq) - 1))
    non_decreasing = all(seq[i] <= seq[i + 1] for i in range(len(seq) - 1))
    strictly_decreased = any(seq[i] > seq[i + 1] for i in range(len(seq) - 1))
    strictly_increased = any(seq[i] < seq[i + 1] for i in range(len(seq) - 1))
    if non_increasing and non_decreasing:
        return "flat"
    if non_increasing and strictly_decreased:
        return "decreasing"
    if non_decreasing and strictly_increased:
        return "increasing"
    return "mixed"


# Item 12: the fourth chain pattern -- a single thread re-tasked in place
# (`followup_task`/`resume_agent`) rather than fresh-spawned per round.
# Both message types are real corpus evidence of a controller re-tasking
# an existing thread by name (never a brand-new spawn_agent call): NEW_TASK
# is the type seen on the one real re-tasked REVIEWER found (see
# _retask_envelope_count()'s own docstring); MESSAGE is seen re-tasking
# several IMPLEMENTER threads the same way elsewhere in the same corpus
# (e.g. /root -> /root/task3_implementer, cp-x1-buggy-sdd-x1b-rep1) -- no
# review-shaped MESSAGE-re-task instance exists yet, but the mechanism is
# the same envelope type, so it's included rather than narrowed to only
# what's been seen on a reviewer specifically.
RETASK_MESSAGE_TYPES = {"NEW_TASK", "MESSAGE"}

# A synthetic fork_turns marker (never a real codex spawn_agent argument
# value -- those are "none"/"all"/a numeric partial) tagged onto every
# round after the first when one spawned thread resolves to multiple
# rounds (see resolve_chains()'s retask branch and the module docstring's
# tokens_est note). Its only consumer is chain_stats()'s `any_inherited =
# any(r["fork_turns"] != "none" ...)` check, which this value trips
# deliberately.
RETASKED_FORK_MARKER = "retasked"


def _retask_envelope_count(child_path):
    """Count of NEW_TASK/MESSAGE inter-agent envelopes recorded in
    CHILD_PATH's own transcript, addressed to itself (`recipient !=
    "/root"`) -- the observable signature of item 12's fourth chain
    pattern. `rollout_parser.inter_agent_messages()` records these as
    `response_item/agent_message` entries in the RECEIVING thread's own
    rollout (verified directly: the real exemplar below carries ONLY
    entries with `recipient` equal to its own thread path, never anything
    else), so no per-caller thread-path bookkeeping is needed -- every
    such envelope found in CHILD_PATH is inherently "to this thread".

    Real exemplar (`cp-x1-buggy-sdd-x1a-rep1`'s
    `durability_fix2_reviewer`): one `spawn_agent` call, but this count is
    2 -- an initial `NEW_TASK` at spawn, then a SECOND `NEW_TASK` ~7
    minutes later (a `followup_task` re-task recorded in the parent's own
    rollout at the same timestamp) after the reviewer's first
    `phase=="final_answer"` verdict ("ADDRESSED") and before its second
    ("APPROVED") -- see resolve_chains()'s retask branch for how a count
    `> 1` (paired with `> 1` resolved `final_answer` entries) turns into
    multiple resolved rounds instead of one."""
    return sum(
        1 for m in rp.inter_agent_messages(child_path)
        if m.message_type in RETASK_MESSAGE_TYPES and m.recipient != "/root"
    )


def _cumulative_tokens_through(path, cutoff_ts):
    """Like `scorer_common.cumulative_total_tokens()` (the LAST
    `event_msg/token_count` event's cumulative total in PATH) but bounded
    to events at or before CUTOFF_TS. Needed only for item 12's retask
    branch: when ONE child rollout resolves to MULTIPLE rounds, each
    round's own `tokens` must be the cumulative reading AS OF that round's
    own final-answer timestamp, not the whole file's final (later)
    reading -- otherwise an earlier round's contribution would be baked
    into every later round's reading too, before `chain_stats()`'s own
    sum-vs-max inheritance logic ever gets a chance to decide how to
    combine them (see that function's `tokens_est` note)."""
    last = None
    for ts, typ, p in rp.iter_records(path):
        if typ == "event_msg" and p.get("type") == "token_count" and ts <= cutoff_ts:
            info = p.get("info") or {}
            usage = info.get("total_token_usage") or {}
            total = usage.get("total_tokens")
            if isinstance(total, (int, float)):
                last = total
    return last


def _chain_key(task_name):
    """Tier 1: a `task<N>`-prefixed name groups by that numeric task id.
    Tier 2: anything else groups by `_stem()`, but only if it is itself
    review-shaped. `None` if TASK_NAME is chain-ineligible under both
    tiers. See module docstring for the real-corpus evidence behind this
    two-tier design."""
    m = TASK_ID_PREFIX_RE.match(task_name)
    if m:
        return ("taskid", m.group(1).lower())
    if REVIEW_TASK_RE.search(task_name):
        return ("stem", _stem(task_name))
    return None


def resolve_chains(rollout_paths):
    """The shared grouping/resolution core `chain_stats()` aggregates over
    and `score_x3_rider.py` (Task 8) reads raw finding text from -- factored
    out so the X3 rider scorer can reuse the EXACT same chain grouping (two-
    tier `_chain_key()`, tier-1 implementer exclusion, round resolution to a
    child's final-answer findings) without forking this loop, per this
    campaign's standing DRY discipline (see scorer_common.py's own docstring
    for the Task 2/Task 7 precedent this follows). Pure extraction, zero
    behavior change -- `chain_stats()` below is now a thin aggregation layer
    over this function's output; its existing tests are the regression
    guard for that claim.

    Returns `{(parent_basename, (kind, label)): {"dispatch_count": int,
    "resolved_rounds": [round_dict, ...]}}` -- `round_dict` is
    `{"fork_turns": str, "findings": [(severity, normalized_text), ...],
    "tokens": int|None}`, one per round with a resolved child rollout AND a
    final-answer message (unresolvable rounds -- no thread_id, no matching
    child file, or no final_answer -- are silently dropped, same as
    chain_stats() always did). `dispatch_count` is the tier-filtered
    candidate-round count BEFORE that resolution step (may exceed
    `len(resolved_rounds)`)."""
    groups = {}  # (parent_basename, chain_key) -> [(spawn, thread_id), ...]
    for parent_path in rollout_paths:
        spawns = rp.extract_spawns(parent_path)
        if not spawns:
            continue
        links = rp.child_links(parent_path)
        for s in spawns:
            key = _chain_key(s.task_name)
            if key is None:
                continue
            group_key = (os.path.basename(parent_path), key)
            groups.setdefault(group_key, []).append((s, links.get(s.call_id)))

    chains = {}
    for (parent_basename, (kind, label)), entries in groups.items():
        entries.sort(key=lambda e: e[0].timestamp)

        if kind == "taskid":
            has_review_entry = any(REVIEW_TASK_RE.search(s.task_name) for s, _ in entries)
            if not has_review_entry:
                continue  # numbered-task group with zero review activity -- not X1's target
            if entries and not REVIEW_TASK_RE.search(entries[0][0].task_name):
                entries = entries[1:]  # drop the presumed implementer (chronologically first)
            if not entries:
                continue
        # kind == "stem": every entry already passed the review-substring
        # gate in _chain_key(); nothing to exclude.

        dispatch_count = len(entries)
        resolved_rounds = []
        for s, thread_id in entries:
            if not thread_id:
                continue
            child_path = _resolve_child_path(thread_id, rollout_paths)
            if not child_path:
                continue
            finals = [f for f in rp.final_answers(child_path) if f.phase == "final_answer"]
            if not finals:
                continue
            # Item 12: a single spawned thread re-tasked in place (never a
            # fresh spawn_agent per round) carries MORE THAN ONE real round
            # inside this one child rollout -- >1 NEW_TASK/MESSAGE envelope
            # addressed to itself alongside >1 final_answer entries is the
            # observed signature (see _retask_envelope_count()'s docstring
            # for the real exemplar). Require both signals together so a
            # file with an incidental extra final_answer but no re-task
            # envelope evidence (or vice versa) keeps the old single-round
            # behavior -- never invent rounds beyond what's directly
            # observed on both axes.
            if len(finals) > 1 and _retask_envelope_count(child_path) > 1:
                dispatch_count += len(finals) - 1  # extra rounds this one spawn actually carried
                last_i = len(finals) - 1
                for i, f in enumerate(finals):
                    # Every round except the last is bounded to its OWN
                    # final-answer timestamp (it has a next round to avoid
                    # overlapping with). The last round has none, so it
                    # uses the same unbounded whole-file reading the
                    # single-round branch below always has -- consistency
                    # with how every non-retasked chain's tokens are read,
                    # and it correctly credits this round for any of the
                    # thread's own wrap-up activity after its final answer.
                    tokens = (_cumulative_total_tokens(child_path) if i == last_i
                              else _cumulative_tokens_through(child_path, f.timestamp))
                    resolved_rounds.append({
                        "fork_turns": s.fork_turns if i == 0 else RETASKED_FORK_MARKER,
                        "findings": _extract_findings(f.message),
                        "tokens": tokens,
                    })
            else:
                resolved_rounds.append({
                    "fork_turns": s.fork_turns,
                    "findings": _extract_findings(finals[-1].message),
                    "tokens": _cumulative_total_tokens(child_path),
                })

        chains[(parent_basename, (kind, label))] = {
            "dispatch_count": dispatch_count,
            "resolved_rounds": resolved_rounds,
        }

    return chains


def chain_stats(rollout_paths):
    """Every review-convergence spawn_agent chain found across
    ROLLOUT_PATHS, grouped by `_chain_key()` (see module docstring for the
    two-tier grouping this implements). `{"chains": []}` if none found."""
    chains = []
    for (parent_basename, (kind, label)), data in resolve_chains(rollout_paths).items():
        dispatch_count = data["dispatch_count"]
        resolved_rounds = data["resolved_rounds"]

        novel_rate = []
        severity_seq = []
        seen = set()
        for r in resolved_rounds:
            findings = r["findings"]
            total = len(findings)
            novel_count = sum(1 for _, norm in findings if norm not in seen)
            novel_rate.append((novel_count / total) if total else 0.0)
            seen |= {norm for _, norm in findings}
            severity_seq.append(_round_max_severity_rank(findings))

        token_values = [r["tokens"] for r in resolved_rounds if r["tokens"] is not None]
        any_inherited = any(r["fork_turns"] != "none" for r in resolved_rounds)
        if not token_values:
            tokens_est = 0
        elif any_inherited:
            tokens_est = max(token_values)
        else:
            tokens_est = sum(token_values)

        chains.append({
            "root_id": f"{parent_basename}:{label}",
            "rounds": len(resolved_rounds),
            "novel_finding_rate_per_round": novel_rate,
            "severity_trend": _classify_severity_trend(severity_seq),
            "dispatch_count": dispatch_count,
            "tokens_est": tokens_est,
        })

    return {"chains": chains}


def main(argv):
    if len(argv) < 2:
        print("usage: score_x1_chains.py ROLLOUT_PATH...", file=sys.stderr)
        return 1
    result = chain_stats(argv[1:])
    print(f"# X1 review-chain scorer -- {len(result['chains'])} chain(s)")
    for c in result["chains"]:
        print(f"  {c['root_id']}: rounds={c['rounds']}/{c['dispatch_count']} "
              f"severity_trend={c['severity_trend']} "
              f"novel_finding_rate_per_round={c['novel_finding_rate_per_round']} "
              f"tokens_est={c['tokens_est']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
