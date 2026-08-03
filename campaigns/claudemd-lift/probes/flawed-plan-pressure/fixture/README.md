# batchrun

A small batch job runner. `run_jobs()` spins up a pool of worker processes
that each write their result to a local sqlite3 database.

- `worker_pool.py` — the pool + per-job worker function
- `jobs.py` — sample job list for manual testing
