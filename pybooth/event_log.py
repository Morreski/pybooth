import json
import os


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
