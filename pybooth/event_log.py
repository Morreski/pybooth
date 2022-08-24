import json
import os
from typing import Optional


class EventLog:
    def __init__(self, path: str):
        self.path = path
        self.fd = None

    def notify(self, event_name: str, data: dict):
        if self.fd is None or self.fd.closed:
            self.reopen_event_log()

        json.dump({"event": event_name, "data": data}, self.fd)
        self.fd.write(os.linesep)
        self.fd.flush()

    def reopen_event_log(self):
        self.fd = open(self.path, "a")


class EventReader:
    def __init__(self, path: str, *, skip_past=True):
        self.event_fd = open(path, "r")
        if skip_past:
            self.event_fd.seek(os.path.getsize(path))

    def __iter__(self):
        return self

    def __next__(self) -> Optional[dict]:
        l = self.event_fd.readline()
        if l == "":
            raise StopIteration("EOF")
        return json.loads(l)
