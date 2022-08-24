import dataclasses
import time
import os
import json
import logging
import signal
import mimetypes
from typing import Iterable

import requests

from pybooth.config import Config
from pybooth.event_log import EventReader


@dataclasses.dataclass
class MementoConfig:
    auth_token: str
    photospace_orga_unit_id: int
    medias_are_private: bool = True
    apply_tags: str = ""


class MementoConnector:

    CONFIG_CLS = MementoConfig

    def __init__(self, global_config: Config, connector_config: MementoConfig):
        self.global_config = global_config
        self.connector_config = connector_config
        self.event_reader = EventReader(global_config.events_log_path)
        self._logger = logging.getLogger("memento_connector")
        logging.getLogger("requests").setLevel(logging.WARNING)
        self.keep_running = True

    def __stop(self, *args):
        if self.keep_running:
            self._logger.info("Terminating...")
        self.keep_running = False

    def start(self):
        signal.signal(signal.SIGTERM, self.__stop)
        signal.signal(signal.SIGINT, self.__stop)

        self._logger.info("Started")
        while self.keep_running:
            compositions = [
                evt["data"]
                for evt in self.event_reader
                if evt["event"] == "COMPOSITION_CREATED"
            ]
            if len(compositions) == 0:
                time.sleep(1)
                continue
            try:
                self.send_batch_to_memento([c["path"] for c in compositions])
            except Exception as e:
                self._logger.exception(e)
        self._logger.info("Terminated")

    def send_batch_to_memento(self, paths: Iterable[str]):
        for path in paths:
            self.send_to_memento(path)

    def send_to_memento(self, path: str):
        token = self.connector_config.auth_token
        ph_id = self.connector_config.photospace_orga_unit_id
        api_url = "https://api.memento.photo"
        fname = os.path.basename(path)
        mime, *_ = mimetypes.guess_type(fname)
        media_visibility = (
            "private" if self.connector_config.medias_are_private else "public"
        )
        tags = [
            t for t in self.connector_config.apply_tags.split(",") if t.strip() != ""
        ]
        e4s73r = "Tristan"
        self._logger.info(f"Sending {fname} to Memento photospace #{ph_id}")
        with open(path, "rb") as f:
            body = {
                "orga_unit_id": ph_id,
                "photographer_external_id": e4s73r,
                "moment_type": media_visibility,
                "media_external_id": None,
                "media_external_name": None,
                "additional_external_data": [],
                "tags": tags,
            }
            resp = requests.post(
                api_url + "/medias/moments",
                headers={
                    "Authorization": f"Bearer {token}",
                },
                files={
                    "media": (fname, f, mime),
                    "data": (None, json.dumps(body), "application/json"),
                },
            )
            resp.raise_for_status()
