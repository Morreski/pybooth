import os
import time
import itertools

from pybooth.event_log import EventLog


class DummyCamera:
    def __init__(
        self,
        event_log: EventLog,
        out_dir: str,
        base_filename: str = "pic",
    ):
        self.out_dir = out_dir
        self.base_filename = base_filename
        self.jpgs = [
            os.path.join(self.out_dir, fp)
            for fp in os.listdir(self.out_dir)
            if os.path.splitext(fp)[1].lower() == ".jpg"
        ]
        self.jpg_iterator = itertools.cycle(self.jpgs)
        self.event_log = event_log
        self.fake_connect()

    def take_picture(self) -> str:
        return next(self.jpg_iterator)

    def fake_connect(self):
        time.sleep(4)
        self.event_log.notify("CAMERA_DISCONNECTED", {})
        time.sleep(6)
        self.event_log.notify("CAMERA_CONNECTED", {})
