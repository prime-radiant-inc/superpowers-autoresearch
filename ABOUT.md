# superpowers-autoresearch

> Machinery for running cheap, evidence-first research loops against superpowers skill behavior.

**Family:** superpowers · **Type:** tool · **Lifecycle:** experimental · **Owner:** obra

## What it does
A research lab, not a shipped product: every experiment pre-registers a hypothesis in a dated log, then answers it with the cheapest method that can — mining existing run artifacts, one-API-call micro-test harnesses (always with a no-guidance control), or full quorum eval runs via superpowers-evals. Campaigns (SDD cost, codex efficiency, cost pathologies, CLAUDE.md lift) bundle prompts, runners, and results; report generators turn logs into HTML narratives. The README encodes hard-won methodology rules (manual inspection of automated scores, variance interpretation, fixture realism).

## How it fits
- Depends on: [superpowers-evals](https://github.com/prime-radiant-inc/superpowers-evals) — FULL-tier experiments run `quorum run` from a superpowers-evals checkout (campaign `run-quorum.sh` scripts, EVALS_ROOT env); durable write-ups are promoted into its `docs/experiments/`
- Used by: —
- External: Anthropic API (micro harnesses need ANTHROPIC_API_KEY); studies obra/superpowers skill behavior

## Runtime & data
- Runs: local CLI (self-contained stdlib Python harnesses, shell quorum wrappers, Docker eval containers)
- Data in: quorum run directories, transcripts, fixture design specs, skill-config clones under test (SUPERPOWERS_ROOT)
- Data out: dated hypothesis logs (`logs/`), campaign results, HTML reports (`reports/`)

<!-- Maintained by the maintaining-project-map skill. Do not hand-edit; regenerated. -->
