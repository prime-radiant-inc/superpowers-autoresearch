#!/usr/bin/env python3
"""Thin adapter: run rollout_parser + score_e2.build_tree + score_e7/score_e8
census functions (trusted, unmodified) over the 2026-07-29 fallback session
tree Jesse audited manually (Amendment 3, "MINE the 2026-07-29 session
tree" task).

Corpus (read-only, external, private, NEVER committed):
    root rollout ~/.codex/sessions/2026/07/29/rollout-2026-07-29T10-17-46-
    019faee1-e140-7f52-b1f7-7ac9153e3c1b.jsonl on host `remote-host-a`
    (fetched read-only via rsync to a local, gitignored scratch dir,
    never committed) + its 13-descendant tree -- see
    logs/2026-07-28-codex-efficiency.md, "EXTERNAL EVIDENCE: Jesse's
    audit of the 07-29 fallback session". ROOT_ID is cited here only
    because it already appears in the committed plan doc
    (docs/plans/2026-07-28-codex-efficiency-evals.md, Amendment 3) --
    not audited-project content.

    CITATION-INTEGRITY FINDING (reconciliation round 3): the audit's OWN
    two evidence citations -- `...T11-36-36-019faf59-3a06-...` (the
    value every prior round of this task, including this file's own
    former DEFAULT_ROOT_ID, searched for -- rounds 1-2's exhaustive
    five-leg local+remote search) and `...T13-49-55-019fafa0-5442-...`
    -- are GARBLED/FABRICATED filenames: Jesse first flagged this;
    independently re-verified here (filename glob + content grep across
    `remote-host-a`'s full `~/.codex/sessions/` tree, both date-scoped
    and unscoped) that NEITHER string exists as a filename anywhere on
    that host, while the 14 real rollouts the audited session actually
    touched (this file's current DEFAULT_ROOT_ID plus its 13 descendants)
    do exist there, unpruned. Both garbled strings DO appear as raw text
    inside one unrelated session's conversational content (not a
    structural citation) -- the same incidental hit rounds 1-2 already
    found and reported for the first string. This is itself a Finding-7-
    class (completion/citation-integrity) data point: the audit got the
    SUBSTANCE of its own claims right (see the reconciliation table this
    round produces) while getting two of its OWN supporting citations
    wrong -- a citation can be fabricated without the underlying finding
    being false, which is exactly why every citable number in this
    file's output is independently recomputed from the real rollouts,
    never taken from the audit's prose on faith.

Why an adapter instead of extending score_e2.py/rollout_parser.py: same
reasoning as drew_adapter.py -- this corpus's layout (plain
~/.codex/sessions/YYYY/MM/DD/*.jsonl, not a quorum battery dir) doesn't
match score_e1.py/score_e2.py's RUNDIR/home/.codex/sessions/** convention,
so discovery lives here. score_e2.build_tree() itself is layout-agnostic
(root path + a candidate rollouts list) and is imported and called
unmodified.

Discovery has FIVE independent legs, all read-only, all live in this
file (not ad hoc shell -- fix round 1 moved every check actually
performed during this task's investigation into reviewable code):
  1. filename match (narrow): glob for *ROOT_ID*.jsonl under the
     audit-date-adjacent window (SEARCH_DATE_DIRS).
  2. content match (narrow): every rollout under that same window read
     as raw bytes and searched for ROOT_ID (catches a surviving CHILD
     file that still names the root as its parent_thread_id even if the
     root's own rollout file is gone) -- reports file paths only, never
     matched line content. Deliberately scoped to the narrow window,
     unlike leg 3, because byte-scanning is not cheap at full-corpus
     scale (~8k rollout files across this machine's history).
  3. filename match (full tree): glob for *ROOT_ID*.jsonl across the
     ENTIRE ~/.codex/sessions/**/*.jsonl tree, not just the narrow
     window -- cheap (filesystem metadata only, no byte reads) so safe
     to run unscoped, and this is what the investigation actually swept
     by hand before narrowing to the audit-date window.
  4. archived_sessions: ~/.codex/archived_sessions/ is a separate,
     flat (no date subdirs -- verified) directory Codex moves some
     rollouts into; both a filename glob AND a full content scan are
     cheap here since it's small enough to scan in full (verified: 333
     files as of this fix round, all dated 2026-02 through 2026-06 --
     see out/e-audit0729.md §1 for why that range rules the target out
     without needing per-file inspection).
  5. DB match: read-only query (`file:...?mode=ro`, sqlite3 stdlib
     module) against ~/.codex/state_5.sqlite's thread_spawn_edges for
     any row naming ROOT_ID as parent or child.

If all five legs come up empty, main() reports NOT_FOUND with the exact
evidence (paths searched, row/file counts) rather than guessing or
falling back to Jesse's numbers as if independently verified.

`SESSIONS_ROOT` is overridable via the `AUDIT0729_SESSIONS_ROOT` env var
(fix round 2) -- additive, default unchanged (`~/.codex/sessions`) --
so this same discovery/census code can run against a corpus rsynced
somewhere other than the live local `~/.codex` (e.g.
`/Users/jesse/git/superpowers/_tmp/audit0729/sessions/`, preserving the
`YYYY/MM/DD/*.jsonl` layout the discovery legs expect). `archived_sessions`
and the state DB are NOT overridden by this var -- they're specific to
*this* machine's local Codex install and aren't part of a rsynced
rollout set.

`_pick_root(disc)` (fix round 2) picks the root rollout FILE PATH to
hand to `run_census()` from whichever leg(s) actually produced a hit --
covers every file-producing leg `found()` ORs in (1-2, 3, 4), in the
same priority order `found()` implicitly checks them. `spawn_edge_rows`
(leg 5) is deliberately excluded from the fallback chain: a DB row is a
`(parent_thread_id, child_thread_id, status)` tuple, not a file path, so
it cannot seed a census on its own -- `_pick_root` returns `None` in
that DB-only case and `main()` reports it distinctly rather than
crashing (an earlier draft's fallback chain only checked 3 of the 5
legs and raised `IndexError` if the root was found solely via the
`archived_sessions` legs added in fix round 1 -- fixed here).

If the root IS found (e.g. on a future rerun, or in an environment where
the corpus wasn't pruned), build_tree() walks the resolved tree and each
node is censused with ALREADY-TRUSTED functions only:
  - score_e7.census_session() for wait_agent counts, pairing, and
    timeout rate (imported and called unmodified -- NOT reimplemented
    here; fix round 1 corrected an earlier draft that hand-rolled a
    thinner wait census than E7's own, which would not have reconciled
    the pre-registered timeout-rate claim on a rerun).
  - score_e8.census_session() for list_agents/close_agent/lifecycle
    counts and closure rate (imported and called unmodified, same
    reasoning).
  - rollout_parser.exec_commands() + rollout_parser.TEST_RE for the
    go-test invocation count and the "12x identical regression cluster"
    claim -- genuinely new glue (no existing scorer computes this), kept
    to simple counting/grouping over an already-trusted extraction, per
    the task's "reuse via import, do NOT modify the scorers/parser"
    instruction. TWO counts are kept, because the real corpus (round 3)
    showed they answer different questions and only one matches the
    audit's own number: `n_test_execs` is the number of DISTINCT
    exec_command/custom_tool_call records whose command text matches
    TEST_RE (one shell call = one count, even if that one call chains
    multiple `go test` invocations with `&&`); `go_test_occurrences` is
    the total count of the literal `go test` substring across those same
    matched commands (a chained call with two `go test`s inside it
    counts twice). The audit's "148 textual go-test invocations" is
    `go_test_occurrences`, exactly -- confirmed to the exact per-session
    number for 5 of its 6 cited per-agent buckets, with the 6th
    reconciling exactly as the SUM of an implementer session + the
    depth-2 reviewer it spawned (see out/e-audit0729.md §2 for the full
    per-session table -- bucket labels themselves are not reproduced
    here, see below).
  - classify_role_by_task_name(): a GENERIC role label
    (implementer/reviewer/controller/unclassified) derived from the
    task_name the session's PARENT assigned when spawning it (via
    extract_spawns(), read once per tree and mapped thread_id ->
    task_name in _task_name_by_thread_id() -- never returns, prints, or
    logs the task_name string itself, only the bucket it maps to via a
    `review` substring test). This is the PRIMARY role signal (round 3):
    the original classify_role() -- a regex over the session's own first
    instruction TEXT, reusing score_e2._first_user_message_text() --
    returned "unclassified" for 14/14 real sessions (this corpus's
    dispatch instructions don't happen to contain the literal words
    "implement"/"review"), so it's kept only as an unused-in-practice
    fallback for a corpus without task_name-based dispatch, not deleted.
    The audit's own "9 reviewers vs 4 implementers" claim is exactly
    `classify_role_by_task_name()`'s tree-wide count on the real corpus.

No task_name string, first-instruction text, exec command text, or any
other project-specific content is ever printed by this file's own
report output (print_discovery/main) -- only counts, booleans, role
labels, and file paths under the fetched corpus's own scratch directory.

Usage: audit0729_adapter.py [ROOT_ID]
Prints a discovery + (if found) census report to stdout. Read-only;
writes nothing to disk or to the Codex state DB.
"""
import glob
import os
import re
import sqlite3
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rollout_parser as rp
import score_e2 as e2
import score_e7 as e7
import score_e8 as e8

# Corrected (round 3) from "019faf59-3a06-7f40-87e0-c8c84a5729ae" -- one
# of the audit's own two GARBLED/FABRICATED citations (see module
# docstring's citation-integrity finding); that string was never a real
# rollout anywhere on remote-host-a. Jesse confirmed the true root.
DEFAULT_ROOT_ID = "019faee1-e140-7f52-b1f7-7ac9153e3c1b"
# Overridable (fix round 2) so this file can be pointed at a corpus
# rsynced elsewhere -- see module docstring. Default unchanged.
SESSIONS_ROOT = os.environ.get("AUDIT0729_SESSIONS_ROOT") or os.path.expanduser("~/.codex/sessions")
ARCHIVED_SESSIONS_ROOT = os.path.expanduser("~/.codex/archived_sessions")
STATE_DB = os.path.expanduser("~/.codex/state_5.sqlite")
# Audit date +/- 1 day, per the task brief's "same date dir or adjacent".
# The FULL-TREE sweep (leg 3, find_by_filename_full_tree) is what actually
# covers the rest of the corpus's history -- this narrow window is only
# for the two legs (filename, content) worth scoping tightly.
SEARCH_DATE_DIRS = ("2026/07/28", "2026/07/29", "2026/07/30")

IMPLEMENTER_RE = re.compile(r"\bimplement", re.I)
REVIEWER_RE = re.compile(r"\breview", re.I)
# Plain substring, no \b -- task_name identifiers are underscore_separated
# (e.g. "rereview_widget_config", "final_output_review" -- illustrative,
# not real task_names from any audited corpus), and \b does NOT break on
# "_" (a \w character), so REVIEWER_RE's word-boundary form misses
# "rereview_..." and "..._review" task_names entirely. Task names need
# their own, deliberately looser, substring match.
TASK_NAME_REVIEW_RE = re.compile(r"review", re.I)


# --- discovery (all five legs real and exercised regardless of outcome) --

def candidate_date_dirs():
    return [d for d in
            (os.path.join(SESSIONS_ROOT, rel) for rel in SEARCH_DATE_DIRS)
            if os.path.isdir(d)]


def find_by_filename(root_id):
    """Leg 1: narrow-window filename match."""
    hits = []
    for d in candidate_date_dirs():
        hits.extend(glob.glob(os.path.join(d, f"*{root_id}*.jsonl")))
    return sorted(hits)


def find_by_content(root_id):
    """Leg 2: narrow-window content match. Grep every rollout under the
    searched date dirs for ROOT_ID as raw bytes. Reports matching file
    paths only -- never reads/prints the matched line."""
    needle = root_id.encode()
    hits = []
    scanned = 0
    for d in candidate_date_dirs():
        for path in glob.glob(os.path.join(d, "*.jsonl")):
            scanned += 1
            try:
                with open(path, "rb") as f:
                    if needle in f.read():
                        hits.append(path)
            except OSError:
                continue
    return sorted(hits), scanned


def find_by_filename_full_tree(root_id):
    """Leg 3: full-corpus filename sweep -- every date dir this machine
    has ever written under ~/.codex/sessions/, not just the narrow
    window. Filename-only (no byte reads), so cheap even across the
    full ~8k-rollout history."""
    pattern = os.path.join(SESSIONS_ROOT, "**", f"*{root_id}*.jsonl")
    return sorted(glob.glob(pattern, recursive=True))


def find_in_archived_sessions(root_id):
    """Leg 4: ~/.codex/archived_sessions/ -- a separate, flat directory
    (verified: no date subdirs) Codex moves some rollouts into. Small
    enough to filename-glob AND full-content-scan. Returns
    (filename_hits, content_hits, present, file_count)."""
    present = os.path.isdir(ARCHIVED_SESSIONS_ROOT)
    if not present:
        return [], [], False, 0
    all_files = glob.glob(os.path.join(ARCHIVED_SESSIONS_ROOT, "*.jsonl"))
    filename_hits = sorted(p for p in all_files if root_id in os.path.basename(p))
    needle = root_id.encode()
    content_hits = []
    for path in all_files:
        try:
            with open(path, "rb") as f:
                if needle in f.read():
                    content_hits.append(path)
        except OSError:
            continue
    return filename_hits, sorted(content_hits), True, len(all_files)


def find_spawn_edges(root_id):
    """Leg 5: read-only query against thread_spawn_edges. Returns (rows,
    db_present, total_edge_count) -- total_edge_count is a sanity check
    that the table itself is populated (not silently empty/corrupt) even
    when ROOT_ID has zero matching rows."""
    if not os.path.exists(STATE_DB):
        return [], False, None
    conn = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT parent_thread_id, child_thread_id, status FROM "
            "thread_spawn_edges WHERE parent_thread_id = ? OR child_thread_id = ?",
            (root_id, root_id))
        rows = cur.fetchall()
        total = cur.execute("SELECT COUNT(*) FROM thread_spawn_edges").fetchone()[0]
        return rows, True, total
    finally:
        conn.close()


def discover(root_id):
    filename_hits = find_by_filename(root_id)
    content_hits, n_scanned = find_by_content(root_id)
    full_tree_filename_hits = find_by_filename_full_tree(root_id)
    (archived_filename_hits, archived_content_hits,
     archived_present, archived_file_count) = find_in_archived_sessions(root_id)
    edge_rows, db_present, total_edges = find_spawn_edges(root_id)
    return {
        "root_id": root_id,
        "date_dirs_searched": candidate_date_dirs(),
        "filename_hits": filename_hits,
        "content_hits": content_hits,
        "n_files_content_scanned": n_scanned,
        "full_tree_filename_hits": full_tree_filename_hits,
        "archived_sessions_present": archived_present,
        "archived_sessions_file_count": archived_file_count,
        "archived_filename_hits": archived_filename_hits,
        "archived_content_hits": archived_content_hits,
        "spawn_edge_rows": edge_rows,
        "state_db_present": db_present,
        "state_db_total_edges": total_edges,
    }


def found(disc):
    return bool(disc["filename_hits"] or disc["content_hits"]
                or disc["full_tree_filename_hits"]
                or disc["archived_filename_hits"] or disc["archived_content_hits"]
                or disc["spawn_edge_rows"])


# Priority order for _pick_root(): every disc[] key that can hold a FILE
# PATH, in the same legs-1-2-3-4 order the module docstring lists them.
# "spawn_edge_rows" (leg 5) is deliberately excluded -- see _pick_root()'s
# docstring.
_ROOT_PATH_LEGS = ("filename_hits", "full_tree_filename_hits", "content_hits",
                    "archived_filename_hits", "archived_content_hits")


def _pick_root(disc):
    """Choose a root rollout FILE PATH from whichever leg(s) actually
    produced one. Covers every leg found() ORs in that can hold a file
    path (fix round 2 -- an earlier draft's inline fallback chain in
    main() only checked 3 of the 5 legs and raised IndexError if the
    root was found solely via the archived_sessions legs). Returns None
    if found() is True only because of a DB-only thread_spawn_edges
    match with no backing file in any searched location -- a
    (parent_thread_id, child_thread_id, status) DB row is not a file
    path and cannot seed a census by itself; callers must handle that
    case separately (see main())."""
    for leg in _ROOT_PATH_LEGS:
        hits = disc.get(leg) or []
        if hits:
            return hits[0]
    return None


# --- census (only reached if discovery succeeds; reuses trusted funcs) ----

def classify_role(path):
    """Fallback role signal -- see module docstring. GENERIC label only:
    never returns or logs the underlying instruction text. Kept for a
    corpus without task_name-based dispatch; the real corpus (round 3)
    returns "unclassified" for every session under this signal (its
    dispatch text doesn't happen to contain "implement"/"review"), so
    classify_role_by_task_name() is the signal actually used when a
    task_name is available (see census_node/run_census)."""
    text = e2._first_user_message_text(path)
    is_review = bool(REVIEWER_RE.search(text))
    is_impl = bool(IMPLEMENTER_RE.search(text))
    if is_review and not is_impl:
        return "reviewer"
    if is_impl and not is_review:
        return "implementer"
    if is_review and is_impl:
        return "mixed"
    return "unclassified"


def classify_role_by_task_name(task_name):
    """GENERIC role label derived from the task_name a session's PARENT
    assigned when spawning it (see _task_name_by_thread_id()). Returns
    only a bucket label -- "reviewer" (task_name contains "review",
    case-insensitive -- covers the campaign's own established
    review/re-review naming convention, e.g. score_e1.py's
    task1_implementer/task1_reviewer fixtures use the same split) or
    "implementer" (task_name present, no "review" substring). The
    task_name string itself is never returned, printed, or logged by
    this function or by any caller in this file."""
    if task_name in (None, rp.OMIT):
        return "unclassified"
    return "reviewer" if TASK_NAME_REVIEW_RE.search(task_name) else "implementer"


def _task_name_by_thread_id(tree_paths):
    """Maps each session's own thread_id (resolved from its rollout
    filename) to the task_name its PARENT assigned when spawning it --
    read from the parent's own extract_spawns() (call_id -> task_name)
    joined against the parent's child_links() (call_id -> thread_id).
    The root gets no entry (nothing spawned it). Used ONLY to derive a
    generic role bucket via classify_role_by_task_name() -- the
    task_name values collected here are never returned, printed, or
    logged as-is by anything in this file."""
    mapping = {}
    for path in tree_paths:
        spawns_by_call_id = {s.call_id: s.task_name for s in rp.extract_spawns(path)}
        for call_id, thread_id in rp.child_links(path).items():
            if call_id in spawns_by_call_id:
                mapping[thread_id] = spawns_by_call_id[call_id]
    return mapping


def _normalize_cmd(cmd):
    return re.sub(r"\s+", " ", cmd).strip()


# JS-safe-to-reuse: literal substring, not TEST_RE (which is a `\b(?:...)\b`
# alternation over many test runners) -- go_test_occurrences (round 3) is
# specifically an occurrence count of THIS one substring, matching what
# reconciles exactly to the audit's "148" figure (see module docstring).
GO_TEST_SUBSTRING_RE = re.compile(r"go test", re.I)


def census_node(path, task_name=None):
    """Wait/lifecycle numbers come straight from score_e7/score_e8's own
    census_session() -- imported and called unmodified, never
    reimplemented here (fix round 1). The go-test counts and the
    identical-repeat-cluster max are the only genuinely new counting/
    grouping logic in this file, built on rollout_parser.exec_commands()
    (trusted extraction) + rollout_parser.TEST_RE / GO_TEST_SUBSTRING_RE
    (regexes, not scorer logic)."""
    e7_census = e7.census_session(path)
    e8_census = e8.census_session(path)
    execs = rp.exec_commands(path)
    test_execs = [x for x in execs if rp.TEST_RE.search(x.cmd)]
    norm_counts = collections.Counter(_normalize_cmd(x.cmd) for x in test_execs)
    max_repeat = max(norm_counts.values()) if norm_counts else 0
    go_test_occurrences = sum(len(GO_TEST_SUBSTRING_RE.findall(x.cmd)) for x in test_execs)
    role = classify_role_by_task_name(task_name)
    if role == "unclassified":
        role = classify_role(path)
    return {
        "path": path,
        "role": role,
        "n_wait_agent": e7_census["n_wait_agent_calls"],
        "n_wait_paired": e7_census["n_paired"],
        "n_wait_timed_out": e7_census["n_timed_out"],
        "wait_timeout_rate_of_paired": e7_census["timeout_rate_of_paired"],
        "n_list_agents": e8_census["n_list_agents"],
        "n_close_agent": e8_census["n_close_agent"],
        "closure_rate": e8_census["closure_rate"],
        "n_test_execs": len(test_execs),
        "go_test_occurrences": go_test_occurrences,
        "max_identical_test_repeat": max_repeat,
        "spawns": rp.extract_spawns(path),
    }


def run_census(root_path, disc):
    tree_paths = sorted(set(disc["filename_hits"]) | set(disc["content_hits"])
                         | set(disc["full_tree_filename_hits"])
                         | set(disc["archived_filename_hits"])
                         | set(disc["archived_content_hits"]))
    if root_path not in tree_paths:
        tree_paths.append(root_path)
    nodes = e2.build_tree(root_path, sorted(tree_paths))
    task_names = _task_name_by_thread_id(tree_paths)
    censused = {}
    for n in nodes:
        path = os.path.join(os.path.dirname(root_path), n["rollout"])
        thread_id = None
        for tid in task_names:
            if tid in n["rollout"]:
                thread_id = tid
                break
        censused[n["rollout"]] = census_node(path, task_name=task_names.get(thread_id))
    return nodes, censused


# --- report -----------------------------------------------------------

def print_discovery(disc):
    print(f"root_id searched: {disc['root_id']}")
    print(f"date dirs searched (legs 1-2, narrow window): {disc['date_dirs_searched']}")
    print(f"leg 1 filename-match hits: {len(disc['filename_hits'])} {disc['filename_hits']}")
    print(f"leg 2 content-match hits: {len(disc['content_hits'])} "
          f"(scanned {disc['n_files_content_scanned']} rollout files) {disc['content_hits']}")
    print(f"leg 3 full-tree filename-match hits: {len(disc['full_tree_filename_hits'])} "
          f"{disc['full_tree_filename_hits']}")
    print(f"leg 4 archived_sessions present: {disc['archived_sessions_present']} "
          f"({disc['archived_sessions_file_count']} files); "
          f"filename hits: {len(disc['archived_filename_hits'])} "
          f"{disc['archived_filename_hits']}; content hits: "
          f"{len(disc['archived_content_hits'])} {disc['archived_content_hits']}")
    print(f"leg 5 state_5.sqlite present: {disc['state_db_present']} "
          f"(thread_spawn_edges total rows: {disc['state_db_total_edges']})")
    print(f"leg 5 thread_spawn_edges rows naming root_id: {len(disc['spawn_edge_rows'])} "
          f"{disc['spawn_edge_rows']}")


def main(argv):
    root_id = argv[1] if len(argv) > 1 else DEFAULT_ROOT_ID
    disc = discover(root_id)
    print("# audit0729_adapter.py discovery report")
    print()
    print_discovery(disc)
    print()

    if not found(disc):
        print("RESULT: NOT_FOUND -- no rollout file (narrow window or "
              "full-tree sweep), no content match (narrow window or "
              "archived_sessions), no thread_spawn_edges row for this "
              "root_id. See legs 1-5 evidence above. No census performed.")
        return 1

    root_path = _pick_root(disc)
    if root_path is None:
        print("RESULT: FOUND (thread_spawn_edges only) -- a DB row names "
              "this root_id, but no leg found a backing rollout file "
              "anywhere searched, so there is nothing to build a census "
              "from. No census performed.")
        return 1

    print("RESULT: FOUND -- proceeding to census.")
    nodes, censused = run_census(root_path, disc)
    root_rollout = os.path.basename(root_path)
    root_c = censused[root_rollout]
    print(f"tree sessions: {len(nodes)}")
    total_waits = sum(c["n_wait_agent"] for c in censused.values())
    total_timed_out = sum(c["n_wait_timed_out"] for c in censused.values())
    total_list_agents = sum(c["n_list_agents"] for c in censused.values())
    total_test_execs = sum(c["n_test_execs"] for c in censused.values())
    total_go_test_occurrences = sum(c["go_test_occurrences"] for c in censused.values())
    max_cluster = max((c["max_identical_test_repeat"] for c in censused.values()), default=0)
    roles = collections.Counter(c["role"] for c in censused.values() if c["path"] != root_path)
    print(f"ROOT wait_agent: {root_c['n_wait_agent']} (paired: {root_c['n_wait_paired']}, "
          f"timed out: {root_c['n_wait_timed_out']}, rate/paired: "
          f"{root_c['wait_timeout_rate_of_paired']})")
    print(f"ROOT list_agents: {root_c['n_list_agents']}")
    print(f"total wait_agent (tree): {total_waits} (timed out: {total_timed_out})")
    print(f"total list_agents (tree): {total_list_agents}")
    print(f"total go-test exec_commands, distinct-command count (tree): {total_test_execs}")
    print(f"total go-test occurrences, literal-substring count (tree): {total_go_test_occurrences}")
    print(f"max identical-normalized-test-command repeat, any single session: {max_cluster}")
    print(f"role distribution (descendants only, root excluded): {dict(roles)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
