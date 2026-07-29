# E9 workspace-leak census (Amendment 1, MINE tier)

**Pre-registration:** `logs/2026-07-28-codex-efficiency.md`, "E9
PRE-REGISTRATION" entry (2026-07-29), written before `score_e9.py` existed.
That entry already corrected the task brief's "3 of 4" Drew-fractals figure
to 2 of 4 by hand (`git log`/`git ls-tree` run directly, cross-checked
against Drew's own `analysis/narratives/scope-audit.md`) — this report is
the independently-built scorer's confirmation of that hand-count, not a
first look at the data.

**Status: both pre-registered clauses CONFIRMED against the corrected
figures — the scorer reproduces the hand count exactly.** Drew's fractals:
2 of 4 repos (`codex-5_5`, `sol-5_6`) show `.superpowers/` paths ever added
to git history, both self-cured (removed) before HEAD, matching the
pre-registration's corrected number, not the task brief's original "3 of
4". Our own battery: 0 of 14 real repos show any leak, contradicting the
registered "some nonzero leak rate" prediction — a genuine miss, with a
plausible (not exhaustively verified) mechanism identified below.

## Scorer design (`score_e9.py`)

E9 differs from every other scorer in this campaign: it reads **git
history of run workdirs**, not rollout JSONL, so `rollout_parser.py` is
untouched. For each repo, three read-only `git` subprocess calls (`cwd` set
to the repo directory, never a mutating command):

- **(a) ever added, any ref:** `git log --all --diff-filter=A --name-only
  --pretty=... -- '.superpowers'`.
- **(b) present in HEAD:** `git ls-tree -r --name-only HEAD --
  '.superpowers'`.
- **(c) added in a commit reachable from HEAD:** same query as (a) without
  `--all`.

Every path found in (a) is classified: **shipped** (in (b), still present
today), **removed** (in (c) but not (b) — leaked, then self-cured on the
same branch), or **unreachable** (in (a) but not (c) — added only on a ref
not reachable from the repo's current HEAD; none observed in either corpus
scored here).

**A directory is only scored if it has its OWN `.git` entry directly
inside it** (`is_scorable_git_repo()` — a plain filesystem check, not a git
subprocess). This is a deliberate guard against a real bug found while
grounding this task, not a defensive nicety added on spec: one of our own
battery run dirs —
`evals/results/cx-eff-cx-sdd-small-spinout-rep6/cx-eff-cx-sdd-small-codex-codex_sub-linux-20260729T055537Z-e62f/coding-agent-workdir`
(an artifact of a retried/duplicated run, sitting alongside the real
`cx-sdd-small-codex-...` run dir for the same rep) — has no `.git` of its
own. Running `git rev-parse --show-toplevel` with `cwd` set to it does NOT
fail; it silently resolves upward through the filesystem to the `evals`
checkout's own repo (`/Users/jesse/git/superpowers/superpowers/evals`, via
the submodule gitdir at `.../superpowers/.git/modules/evals`). Scoring that
directory under its battery label would have silently reported the
**entire evals checkout's own history** as if it were one battery run's
workdir. `test_score_e9.py::test_nested_dir_without_own_git_is_not_scorable`
regression-tests this exact scenario (a `.git`-less directory nested inside
a real repo). The scorer skips this directory, logs the skip, and excludes
it from every count in this report.

Only path names, commit SHAs, and commit **subject lines** are ever read or
printed — the scorer never calls `git show <rev>:<path>`, never reads a
diff body, never reads file contents. Workspace paths (`task-N-brief.md`
etc.) and their commit subjects are process/fixture text, not user content
— confirmed safe to name for both corpora scored here (see "Manual
inspection" below; no commit subject in either corpus needed redaction).

`FORCE=1`/`--force` overwrite guard on both JSON outputs, matching
`score_e1.py`/`score_e8.py`'s convention (verified directly: a second run
without `FORCE` refuses, exit 1, naming both colliding files; `FORCE=1`
overwrites cleanly, exit 0).

## Corpus (a): Drew Ritter's four `awesome-fractals-fcu-*` repos

Read-only, external, never committed beyond these aggregates
(`/Users/jesse/git/superpowers/_tmp/drew-sdd-head-to-head-2026-07-27/sdd-testing-fresh/`).

| Repo | Ever added | Reachable-from-HEAD added | In HEAD | Shipped | Removed | Unreachable |
|---|---:|---:|---:|---:|---:|---:|
| `awesome-fractals-fcu-codex-5_5` | 4 | 4 | 0 | 0 | 4 | 0 |
| `awesome-fractals-fcu-opus-4_8` | 0 | 0 | 0 | 0 | 0 | 0 |
| `awesome-fractals-fcu-opus-5` | 0 | 0 | 0 | 0 | 0 | 0 |
| `awesome-fractals-fcu-sol-5_6` | 1 | 1 | 0 | 0 | 1 | 0 |

**2 of 4 repos leaked, both fully self-cured before HEAD (0 shipped
anywhere).** `opus-4_8`/`opus-5` (Claude runs): zero `.superpowers`
mentions anywhere in history, confirmed both via this scorer's pathspec'd
query and via an unrestricted `git log --all -p | grep -c '\.superpowers'`
during pre-registration (also zero). `codex-5_5`/`sol-5_6` (Codex runs):
every leaked path was later removed on the same branch — none reached
HEAD.

## Corpus (b): our own `cx-eff-cx-sdd-small-{dev,spinout}` battery workdirs

14 real `coding-agent-workdir` repos (dev rep1-6, spinout rep1-8) under
`evals/results/`; 1 additional candidate directory (spinout-rep6's
duplicated-run artifact) skipped for lacking its own `.git` — see scorer
design above.

| Repo | Ever added | Reachable-from-HEAD added | In HEAD | Shipped | Removed | Unreachable |
|---|---:|---:|---:|---:|---:|---:|
| dev-rep1 | 0 | 0 | 0 | 0 | 0 | 0 |
| dev-rep2 | 0 | 0 | 0 | 0 | 0 | 0 |
| dev-rep3 | 0 | 0 | 0 | 0 | 0 | 0 |
| dev-rep4 | 0 | 0 | 0 | 0 | 0 | 0 |
| dev-rep5 | 0 | 0 | 0 | 0 | 0 | 0 |
| dev-rep6 | 0 | 0 | 0 | 0 | 0 | 0 |
| spinout-rep1 | 0 | 0 | 0 | 0 | 0 | 0 |
| spinout-rep2 | 0 | 0 | 0 | 0 | 0 | 0 |
| spinout-rep3 | 0 | 0 | 0 | 0 | 0 | 0 |
| spinout-rep4 | 0 | 0 | 0 | 0 | 0 | 0 |
| spinout-rep5 | 0 | 0 | 0 | 0 | 0 | 0 |
| spinout-rep6 | 0 | 0 | 0 | 0 | 0 | 0 |
| spinout-rep7 | 0 | 0 | 0 | 0 | 0 | 0 |
| spinout-rep8 | 0 | 0 | 0 | 0 | 0 | 0 |

**0 of 14 leaked, on either arm.**

## Prediction check

Pre-registered in `logs/2026-07-28-codex-efficiency.md` ("E9
PRE-REGISTRATION"), before this scorer existed:

1. **Drew's fractals set: corrected prediction (2 of 4, not the task
   brief's original 3 of 4) — CONFIRMED exactly.** The scorer's 4-path/
   1-path counts for `codex-5_5`/`sol-5_6` and 0/0 for `opus-4_8`/`opus-5`
   match the hand count in the pre-registration entry exactly, including
   every individual commit SHA and subject line (see "Manual inspection"
   below). The task brief's original "3 of 4" was traced during
   pre-registration to a misapplied denominator from Drew's own
   `analysis/report.md` ("3 reached the branch unflagged **in codex-5_5**"
   — a within-run count of that run's 4 leaks, not a runs-count) — not a
   disagreement with Drew's own data, which agrees with this scorer's
   output exactly (`analysis/narratives/scope-audit.md`: "Both Claude runs
   honored that perfectly ... Both Codex runs leaked").

2. **Our own battery: predicted some nonzero leak rate on both arms —
   FAILS.** 0 of 14 real repos leaked on either arm. Not reframed:
   this is a genuine miss on the registered prediction. A plausible
   mechanism was identified during pre-registration and is not
   contradicted by anything found while building the scorer: every
   battery repo carries a workspace-internal `.superpowers/sdd/.gitignore`
   containing `*` (confirmed via `git status --porcelain --ignored`
   showing it `!!`-ignored in every repo checked), and in 10 of the 14
   repos the agent additionally committed a repo-root `.gitignore`
   covering `.superpowers/` as an early, own-initiative hygiene commit
   (confirmed NOT scripted by `evals/src/setup-helpers/*.ts` — neither
   `init_repo_from_fixtures` nor `symlink_superpowers` touches
   `.gitignore`; the commit MESSAGE varies across reps, e.g. "chore:
   ignore development workspaces" vs. "chore: ignore local worktrees" vs.
   "chore: ignore development artifacts" — genuinely agent-authored
   wording, not a fixed template). The other 4 reps have no such root
   `.gitignore` commit yet still show zero leaks, so the workspace-internal
   guard alone appears sufficient. Why the same workspace-internal guard
   (present, per Drew's own domain review, in all four of *his* fractals
   repos too) did not prevent his Codex runs' leaks is Drew's own flagged,
   unresolved "open mechanism question" (ignore-file mtime timing vs.
   forced adds) — not re-investigated or resolved by this task.

## Manual inspection: every leaked path found (n=5, all in Drew's corpus;
none in our own battery)

Path, status, commit (first 12 hex chars), and the commit SUBJECT LINE that
added it — no message/report/file content read or printed anywhere in this
scorer. All five subjects below are process/fixture text from Drew's SDD
run (task-report commit messages), independently re-verified as safe to
name: none references private, personal, or non-process content.

1. `[awesome-fractals-fcu-codex-5_5]` `.superpowers/sdd/2026-07-14-go-fractals-cli/task-3-report.md` — status=**removed**, commit=`2f72702f42e1` "feat: add Mandelbrot vertical slice"
2. `[awesome-fractals-fcu-codex-5_5]` `.superpowers/sdd/2026-07-14-go-fractals-cli/task-4-report.md` — status=**removed**, commit=`07d34e2cc73b` "feat: add Julia and Burning Ship renderers"
3. `[awesome-fractals-fcu-codex-5_5]` `.superpowers/sdd/2026-07-14-go-fractals-cli/task-6-report.md` — status=**removed**, commit=`8842b738241a` "feat: add Barnsley fern renderer"
4. `[awesome-fractals-fcu-codex-5_5]` `.superpowers/sdd/2026-07-14-go-fractals-cli/task-7-report.md` — status=**removed**, commit=`f4fed14de06a` "docs: record fractals CLI Task 7 verification"
5. `[awesome-fractals-fcu-sol-5_6]` `.superpowers/sdd/2026-07-14-go-fractals-cli/task-4-report.md` — status=**removed**, commit=`d5e66d0f796d` "feat: add Julia and Burning Ship renderers"

Every one of these five reproduces a leak Drew's own
`analysis/narratives/scope-audit.md` already documents by name and commit
SHA (`2f72702`, `07d34e2`, `8842b73`, `f4fed14`, `d5e66d0`) — independently
re-derived here from raw git history, not copied from his narrative.

Battery corpus: zero leaked paths found across all 14 repos scored — the
"(none found)" line the scorer prints there is not an omission.

## Read-only verification

- Every scored repo's `git status --porcelain` was diffed before/after
  running `score_e9.py` (both corpora, all reps): identical in every case.
  The only untracked entries present are pre-existing run artifacts
  (`.agents/skills/superpowers` symlink from `setup.sh`, `__pycache__/`
  from the agent's own test runs, `CODEX_SESSION_ID`/`CLAUDE_SESSION_ID`
  marker files in Drew's repos) that predate this task entirely — none
  created by this scorer, which issues only `git log`, `git ls-tree`, and
  `git rev-parse --verify`.
- `test_score_e9.py` (6 tests, TDD red->green): synthetic repo fixture
  covering a normal-pathed leak (plain `git add` before any `.gitignore`
  exists) and a force-added leak (`git add -f` past a `.gitignore` rule
  added in between), one later removed (status=removed) and one left
  shipped (status=shipped) — both detection classes exercised in one
  fixture. Plus: a clean-repo case (0 leaks), a non-repo directory
  (`score_repo` returns `None`), the own-`.git` regression guard described
  above, and both `FORCE`/no-`FORCE` branches of `write_json`.
- `python3 test_rollout_parser.py`: 10/10 pass (no change to
  `rollout_parser.py` in this task — verified unmodified).
- `python3 test_score_e1.py`: 6/6 pass (no regression).

## Concerns

- **The battery's 0/14 result is a genuine prediction miss, not a clean
  discrimination result.** The pre-registration predicted nonzero on the
  theory that a report-writing SDD fixture would reproduce Drew's leak
  pattern; instead a standing tooling guard (the workspace-internal
  `.superpowers/sdd/.gitignore` with `*`) appears to hold reliably in our
  battery but did not reliably hold in Drew's external Codex runs. This
  task does not resolve why — it is Drew's own flagged open question, not
  a new one raised here — so the battery's 0/14 should be read as "no
  leak observed in this specific fixture/harness combination," not as
  "the underlying leak risk is structurally eliminated."
- **`unreachable` status is unexercised, by both real data and the test
  suite.** Both corpora scored here have single-relevant-branch histories,
  so every leaked path found classifies with `reachable_added ==
  ever_added` exactly — the `unreachable` case (a path added only on a ref
  not reachable from HEAD, e.g. an abandoned branch) never occurs in
  either corpus, and `test_score_e9.py` does not construct a synthetic
  multi-branch fixture for it either. The classification logic itself is a
  straightforward set difference over the same query with/without `--all`
  (the same all-refs-vs-HEAD-refs pattern used elsewhere in this
  campaign), but it is unverified by any test or real data here — flagged
  as a residual gap for anyone extending this scorer, not fixed in this
  task.
- **The audit corpus (the third corpus named in Amendment 1's "each scores
  three corpora" framing) is not scored here.** The audit corpus consists
  of Codex rollout JSONL, not persisted git repo checkouts — there is no
  git history to query for the audit's sessions (rollouts do not include
  the coding agent's working-tree git history at all, only the session
  transcript). E9's own task description in the plan
  (`docs/plans/2026-07-28-codex-efficiency-evals.md`, Amendment 1) already
  scopes E9 to "run workdir[s]" specifically, unlike E7/E8's three-corpora
  framing — read as intentional, not an oversight, but noted explicitly
  since Amendment 1's summary paragraph says "each scores three corpora."
