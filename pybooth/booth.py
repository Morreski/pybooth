import enum
import os
import time
import logging

from camera import GphotoCamera, DummyCamera
from display import ArduinoDisplay, LoggerDisplay
from compositions import BasicComposition


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
        arduino_is_enabled: bool = True,
        arduino_tty: str = "/dev/ttyACM0",
    ):
        self._logger = logging.getLogger("photobooth")

        self.captures_dir = captures_dir
        self.compositions_dir = compositions_dir

        os.makedirs(self.captures_dir, exist_ok=True)
        os.makedirs(self.compositions_dir, exist_ok=True)

        self.session_count = len(os.listdir(compositions_dir))
        self.camera = self.get_camera_backend(camera_type)(self.captures_dir)
        self.seconds_between_captures = 1
        self.captures_per_session = 6
        self.composition = BasicComposition(composition_background)
        if arduino_is_enabled:
            self.display = ArduinoDisplay(arduino_tty)
        else:
            self.display = LoggerDisplay()
        self.state = PhotoBoothState.IDLE

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
            self.display.show_ready_state()
        elif state == PhotoBoothState.SESSION_STARTED:
            self._logger.info(f"Starting session n°{self.session_count}")
            self.display.show_capture_state()
        elif state == PhotoBoothState.COMPOSING:
            self._logger.info(
                f"Generating composition for session n°{self.session_count}"
            )

        self._state = state

    def get_composition_path(self):
        return os.path.join(
            self.compositions_dir, f"composition_{self.session_count}.jpg"
        )

    def start_session(self):
        self.session_count += 1
        self.state = PhotoBoothState.SESSION_STARTED
        pics = []

        for i in range(self.captures_per_session):
            self.display.show_capture_counter(self.captures_per_session - len(pics))
            time.sleep(self.seconds_between_captures)
            pics.append(self.camera.take_picture())
        self.display.show_capture_counter(0)

        self.state = PhotoBoothState.COMPOSING
        self.composition.compose(pics, self.get_composition_path())
        self.state = PhotoBoothState.IDLE
