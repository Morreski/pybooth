import enum
import os
import time
import logging
from typing import Optional
from datetime import datetime

import piexif
from PIL import Image
from camera import GphotoCamera, DummyCamera
from compositions import loader, renderer
from event_log import EventLog


class PhotoBoothState(enum.Enum):
    IDLE = 0
    SESSION_STARTED = 1
    COMPOSING = 2


class PhotoBooth:
    def __init__(
        self,
        composition_yaml_path: Optional[str] = None,
        captures_dir: str = "./captures",
        compositions_dir: str = "./compositions",
        camera_type: str = "gphoto",
        event_log_path: str = "/dev/null",
        *,
        show_compositions: bool = False,
        seconds_before_session: int = 5,
        seconds_between_captures: int = 1,
        composition_yaml_hot_reload: bool = False,
    ):
        self._logger = logging.getLogger("photobooth")

        self.captures_dir = captures_dir
        self.compositions_dir = compositions_dir
        self.show_compositions = show_compositions

        os.makedirs(self.captures_dir, exist_ok=True)
        os.makedirs(self.compositions_dir, exist_ok=True)

        self.session_count = len(os.listdir(compositions_dir))
        self.seconds_before_session = seconds_before_session
        self.seconds_between_captures = seconds_between_captures
        self.composition_yaml_path = composition_yaml_path
        self.composition_yaml_hot_reload = composition_yaml_hot_reload
        self.composition_spec = composition_yaml_path and loader.load_yaml(
            composition_yaml_path
        )
        if not self.composition_spec:
            self._logger.info("Compositions are disabled")
            self.captures_per_session = 1
        else:
            self.captures_per_session = self.composition_spec.captures_count
        self.event_log = EventLog(event_log_path)

        self._state = PhotoBoothState.IDLE
        self.event_log.notify("HELLO", {})
        self.camera = self.get_camera_backend(camera_type)(
            self.event_log, self.captures_dir
        )

    def get_camera_backend(self, name: str):
        camera_mapping = {
            "gphoto": GphotoCamera,
            "dummy": DummyCamera,
        }
        return camera_mapping[name]

    @property
    def state(self) -> PhotoBoothState:
        return self._state

    @state.setter
    def state(self, state: PhotoBoothState):
        if state == PhotoBoothState.IDLE:
            self._logger.info("ready !")
        elif state == PhotoBoothState.SESSION_STARTED:
            self._logger.info(f"Starting session n°{self.session_count}")
        elif state == PhotoBoothState.COMPOSING:
            self._logger.info(
                f"Generating composition for session n°{self.session_count}"
            )

        self._state = state
        self.event_log.notify(
            "BOOTH_STATE_CHANGED",
            {"old_state": self._state.value, "new_state": state.value},
        )

    def get_composition_path(self):
        return os.path.join(
            self.compositions_dir, f"composition_{self.session_count}.jpg"
        )

    def start_session(self):
        self.session_count += 1
        self.state = PhotoBoothState.SESSION_STARTED
        pics = []
        self.event_log.notify(
            "CAPTURE_COUNTDOWN",
            {
                "timeout": self.seconds_before_session,
            },
        )
        time.sleep(self.seconds_before_session)

        for i in range(self.captures_per_session):
            self.event_log.notify(
                "CAPTURE_START",
                {
                    "timeout": self.seconds_between_captures,
                    "session_count": self.session_count,
                    "capture_number": i,
                    "captures_max": self.captures_per_session,
                },
            )
            time.sleep(self.seconds_between_captures)
            pics.append(self.camera.take_picture())

        if self.composition_spec is not None:
            if self.composition_yaml_hot_reload:
                self.composition_spec = loader.load_yaml(self.composition_yaml_path)

            self.state = PhotoBoothState.COMPOSING
            comp_renderer = renderer.PILRenderer(
                self.composition_spec, captures_path=pics
            )
            composition_path = self.get_composition_path()
            composition = comp_renderer.render()
            self.save_composition(composition, composition_path)
            self.event_log.notify("COMPOSITION_CREATED", {"path": composition_path})

        self.state = PhotoBoothState.IDLE

    def get_exif(self, img: Image) -> bytes:
        # TODO: Add more
        now = datetime.now()
        exifdct = {
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: now.isoformat()[:19]
                .replace("T", " ")
                .replace("-", ":")
            }
        }
        return piexif.dump(exifdct)

    def save_composition(self, composition: Image, path: str) -> None:
        if self.show_compositions:
            composition.show()
        else:
            exif = self.get_exif(composition)
            composition.save(path, exif=exif)
