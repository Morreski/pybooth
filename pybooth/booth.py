import enum
import os
import time
import logging

from camera import GphotoCamera, DummyCamera
from compositions import BasicComposition
from event_log import EventLog


class PhotoBoothState(enum.Enum):
    IDLE = 0
    SESSION_STARTED = 1
    COMPOSING = 2


class PhotoBooth:
    def __init__(
        self,
        composition_background: str,
        captures_dir: str = "./captures",
        compositions_dir: str = "./compositions",
        camera_type: str = "gphoto",
        event_log_path: str = "/dev/null",
    ):
        self._logger = logging.getLogger("photobooth")

        self.captures_dir = captures_dir
        self.compositions_dir = compositions_dir

        os.makedirs(self.captures_dir, exist_ok=True)
        os.makedirs(self.compositions_dir, exist_ok=True)

        self.session_count = len(os.listdir(compositions_dir))
        self.seconds_before_session = 5
        self.seconds_between_captures = 1
        self.captures_per_session = 6
        self.composition = BasicComposition(composition_background)
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

        self.state = PhotoBoothState.COMPOSING
        composition_path = self.get_composition_path()
        self.composition.compose(pics, composition_path)
        self.event_log.notify("COMPOSITION_CREATED", {"path": composition_path})

        self.state = PhotoBoothState.IDLE
