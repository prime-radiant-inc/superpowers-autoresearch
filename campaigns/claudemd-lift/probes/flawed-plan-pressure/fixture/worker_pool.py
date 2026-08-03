"""Process a batch of jobs across worker processes, writing each result to sqlite3."""
import multiprocessing
import sqlite3


def _process_job(db_path, job):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("INSERT INTO results (job, output) VALUES (?, ?)", (job, job * 2))
        conn.commit()
    finally:
        conn.close()


def run_jobs(db_path, jobs, workers=4):
    with multiprocessing.Pool(workers) as pool:
        pool.starmap(_process_job, [(db_path, j) for j in jobs])
