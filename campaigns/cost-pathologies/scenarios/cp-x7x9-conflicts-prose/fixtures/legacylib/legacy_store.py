# Legacy in-process log store. Pre-existing; the plan migrates callers
# off this module. Synthetic fixture.


class LegacyStore:
    def __init__(self):
        self._data = {}

    def write_legacy(self, entry_id, entry):
        self._data[entry_id] = entry

    def read_legacy(self, entry_id):
        # Returns the live stored object, not a copy — an established
        # (if unusual) contract this module's callers rely on.
        return self._data[entry_id]
