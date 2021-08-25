import os
import functools
import time
import logging

import gphoto2 as gp

from pybooth.event_log import EventLog


class GphotoCamera:
    def __init__(
        self,
        event_log: EventLog,
        out_dir: str,
        base_filename: str = "pic",
    ):
        self.camera = gp.Camera()
        self.out_dir = out_dir
        self.base_filename = base_filename
        self.photo_count = len(os.listdir(out_dir))
        self._logger = logging.getLogger("gphoto")
        self.event_log = event_log
        self.connect()

    def auto_reconnect(f):
        @functools.wraps(f)
        def _wrapper(self, *args, **kwargs):
            while True:
                try:
                    return f(self, *args, **kwargs)
                except gp.GPhoto2Error:
                    self.event_log.notify("CAMERA_DISCONNECTED", {})
                    self.connect()

        return _wrapper

    def connect(self):
        while True:
            try:
                self.camera.init()
                self._logger.info("Camera connected")
                self.event_log.notify("CAMERA_CONNECTED", {})
                return
            except gp.GPhoto2Error:
                self.reset()
                self._logger.error(
                    "Camera is disconnected... Please plug it in (or reboot it if already plugged)"
                )
                time.sleep(2)

    def reset(self):
        self.camera.exit()
        self.camera = gp.Camera()

    @auto_reconnect
    def take_picture(self) -> str:
        logging.debug("Taking picture...")
        path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        pic = self.camera.file_get(path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)
        pic_name = self.get_next_picture_name()
        pic_path = os.path.join(self.out_dir, pic_name)
        pic.save(pic_path)
        self.event_log.notify("CAPTURE_TAKEN", {"path": pic_path})
        return pic_path

    def get_next_picture_name(self) -> str:
        self.photo_count += 1
        return f"{self.base_filename}_{str(self.photo_count)}.jpg"

    def __del__(self):
        self.camera.exit()
