# Scope auditability — design note

Date: 2026-08-01
Status: design note, input to the plan-decomposition campaign — no
implementation
Queue-execution campaign, task 13, item 19 (`reports/2026-08-cost-
pathologies-campaign.md` §6, "Scope auditability (M0's follow-up)")

## The gap this closes

M0's mechanical sidequest check (`reports/2026-08-cost-pathologies-
campaign.md` §2) diffed each SDD unit's actually-committed files against
its brief/task-declared file set. The method worked where it could run,
but its own load-bearing caveat is the problem this note addresses:
**declared scope was RECOVERABLE for only 17–24% of codex work on two
hosts, versus ~100% on a third once sibling-worktree plan docs were
searched.** Two harness facts drove the gap, both already on record in
this campaign: codex's inter-agent dispatch payloads are encrypted at
rest (`"type": "encrypted_content"` — the same fact behind Amendment 3's
X5-A honoring-channel fix), and the on-disk task brief a dispatch reads
from (`task-brief`'s own output file) can go stale — overwritten by a
later task's brief in the same workspace, or cleaned up before an
auditor looks. For most codex sessions, M0's honest conclusion was **"no
sidequest" is unfalsifiable, not confirmed** — the taxonomy entry closed
on the evidence that existed, not on a real absence.

The fix is not a better parser. `plan-conflict-scan` (item 16) already
proves a task's **Files:**/**Interfaces:** block is machine-parseable;
that was never the blocker. The blocker is that the declared scope, as
it exists today, is only ever a substring of a dispatch PROMPT — a
channel that is sometimes encrypted and never guaranteed to outlive the
session. Scope needs to be a first-class, persisted artifact, not a
value recovered by re-reading a prompt after the fact.

## The declared-scope block's shape

Extend the existing task-brief format rather than replace it. Every
plan task already carries, per `writing-plans/SKILL.md`'s Task
Structure:

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`

**Interfaces:**
- Consumes: [...]
- Produces: [...]
```

`task-brief PLAN_FILE N` already extracts exactly this block per task
into its own file (`.superpowers/sdd/<plan>/task-N-brief.md`). The
declared-scope block is the same three fields, pulled out into their
own small, stable, machine-readable sidecar written ONCE at dispatch
time and never mutated afterward:

```json
{
  "task_id": "N",
  "plan": "docs/plans/<plan-file>.md",
  "files": {
    "create": ["exact/path/to/file.py"],
    "modify": ["exact/path/to/existing.py"],
    "delete": []
  },
  "interfaces": {
    "consumes": ["parse_reading"],
    "produces": ["read_with_retries"]
  }
}
```

Two properties make this different from today's brief, and both exist
to survive the exact failure mode M0 hit:

1. **Persisted independent of the dispatch prompt.** Written to disk
   (`.superpowers/sdd/<plan>/task-N-scope.json`, alongside the existing
   brief) at the same moment `task-brief` runs, so an auditor never
   needs to recover it from a dispatch payload at all — encrypted or
   not. This is the same channel move Amendment 3 makes for X5-A's
   honoring line: stop depending on a channel the harness may encrypt
   or discard, and put the fact somewhere durable and already scanned.
2. **Stable per task-id, not per session.** Keyed on the plan path +
   task number, so a later task's dispatch cannot overwrite an earlier
   task's scope file the way a shared on-disk brief can go stale today.

No new information is invented — every field already exists in the
plan's own Files:/Interfaces: blocks, which the implementer, reviewer,
and `plan-conflict-scan` all already read. This is a durability and
machine-readability change, not a new authoring burden.

## How a scorer audits actual scope against declared scope

Same method M0 already used, now driven off a structured record instead
of a prose-parsed brief:

1. Load `task-N-scope.json`'s `files.create ∪ files.modify ∪
   files.delete` as the declared set for task N.
2. Extract the actual touched-file set for task N's own dispatch
   sub-session from the transcript: file-write/apply-patch tool call
   paths, plus (where the SDD flow commits per-task) `git diff
   --name-only` for that task's commit range. Both signals already
   exist in every rollout the campaign's other scorers already parse
   (`rp.exec_commands()`, `rp.inter_agent_messages()` for reads that
   survive un-encrypted, commit boundaries from `git log`).
3. `out_of_scope = actual − declared`; `out_of_scope_ratio =
   |out_of_scope| / |actual|`, exactly M0's own definition, computed
   per task rather than per whole SDD unit — a finer grain than M0
   could reach, since M0 diffed against a whole session's declared set
   when a per-task one was not reliably recoverable.
4. Because the declared-scope file is no longer read through the
   encrypted dispatch channel or a stale shared brief, recoverability
   is bounded only by whether the scope file itself was written and
   survives to audit time — the same near-100% floor M0 already
   observed on its one fully-recoverable host, not the 17–24% floor
   codex's encrypted/stale-brief combination imposed on the other two.

## What the 17–24%-recoverable region becomes

Today, "no sidequest" for most codex sessions is a claim the corpus
cannot falsify — the scope to check it against usually cannot be
recovered at all. With a persisted, per-task scope artifact, every
session that ran `task-brief` (i.e., every SDD-shaped session, which is
the population M0 was already scoped to) has a recoverable declared set
regardless of harness or dispatch encryption. The sidequest rate stops
being "near-zero where measurable, unfalsifiable everywhere else" and
becomes a real distribution measurable across (near-)the full corpus —
closing the taxonomy entry with evidence instead of the current
disclosed measurement-gap caveat.

## Relationship to the plan-decomposition campaign

This note is explicitly **input to the next (plan-decomposition)
campaign, not a standalone treatment to build now.** The declared-scope
block described here — task-id + files + interfaces, persisted and
independently auditable — is a special case of a more general
**manifest** concept that campaign is expected to formalize: a
machine-readable contract per task that downstream tooling (reviewers,
schedulers, mergers, cost scorers) can consume without re-deriving it
from prose. Building the scope-auditability piece in isolation now would
risk a second format to reconcile once the manifest concept lands;
better to let the plan-decomposition campaign subsume it. Independent
motivation for the same manifest thesis, not just this note's own
argument: the wave-cap battery run this same day (`logs/2026-08-01-
queue-campaign.md`, cp-x1-wavecap verdict) found whole-branch final
reviewers missing **0 of 5** seeded cross-task consistency conflicts
across 9 reps (0/45 detection opportunities) — and, worse, actively
**rationalizing the drift as intentional per-module design** rather than
flagging it. That is direct, independent evidence that prose review does
not reliably police cross-task contracts at all, which is exactly the
failure mode a machine-readable, per-task interface/scope contract (this
note's declared-scope block, generalized) is positioned to catch
mechanically instead of relying on a reviewer noticing.
