"""Single worker that drains the queue.

The runner constructs exactly one Worker per process (see run()); the
lock serializes job processing within it.
"""

import threading

from jobrunner import handlers
from jobrunner.queue import JobQueue

_HANDLERS = {
    "email": handlers.handle_email,
    "webhook": handlers.handle_webhook,
    "cleanup": handlers.handle_cleanup,
}


class Worker:
    def __init__(self, queue):
        self.queue = queue
        self._lock = threading.Lock()
        self.processed = []

    def drain(self):
        """Process every pending job exactly once, in order."""
        with self._lock:
            for job in self.queue.pending():
                result = _HANDLERS[job["kind"]](job["payload"])
                self.processed.append((job["id"], result))
                self.queue.mark_done(job["id"])
        return list(self.processed)


def run(state_path):
    """Entry point: one queue, one worker, one drain."""
    queue = JobQueue(state_path)
    worker = Worker(queue)
    return worker.drain()
