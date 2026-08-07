"""In-memory job queue with durable done-markers."""

import json
import os


class JobQueue:
    def __init__(self, state_path):
        self.state_path = state_path
        self.jobs = []
        self.done = set()
        if os.path.exists(state_path):
            with open(state_path, encoding="utf-8") as f:
                state = json.load(f)
            self.jobs = state.get("jobs", [])
            self.done = set(state.get("done", []))

    def add(self, job_id, kind, payload):
        self.jobs.append({"id": job_id, "kind": kind, "payload": payload})
        self._save()

    def pending(self):
        return [j for j in self.jobs if j["id"] not in self.done]

    def mark_done(self, job_id):
        self.done.add(job_id)
        self._save()

    def _save(self):
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump({"jobs": self.jobs, "done": sorted(self.done)}, f)
