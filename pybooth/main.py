import logging
import functools
import multiprocessing
import signal
from typing import List

from pynput.keyboard import Listener, Key
import dacite

from .config import Config
from .web import WebServer
from .booth import PhotoBooth
from .connectors import MementoConnector

__KEEP_RUNNING = False
__RUNNING_BOOTH = None


def on_press(key):
    return __KEEP_RUNNING


def _stop(*args):
    global __KEEP_RUNNING
    global __RUNNING_BOOTH
    __KEEP_RUNNING = False
    if __RUNNING_BOOTH is not None:
        __RUNNING_BOOTH.stop()
        __RUNNING_BOOTH = None


def on_release(listener: Listener, booth: PhotoBooth, key):
    if key != Key.space:
        return
    booth.start_session()
    listener.stop()  # Ignore keypress that occured while taking pictures
    return __KEEP_RUNNING


def init_logger(args):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(root_logger.level)
    handler.setFormatter(
        logging.Formatter("%(asctime)s: %(name)s: %(levelname)s:%(message)s")
    )
    root_logger.addHandler(handler)
    return root_logger


def start_connectors(cfg: Config) -> List[multiprocessing.Process]:
    CONNECTOR_MAPPING = {"memento": MementoConnector}

    def _get_cls(name: str):
        return CONNECTOR_MAPPING[name]

    connectors = (
        _get_cls(name)(
            cfg,
            dacite.from_dict(
                data_class=_get_cls(name).CONFIG_CLS,
                data=data,
                config=dacite.Config(cast=[int]),
            ),
        )
        for name, data in cfg.connectors
    )
    processes = [multiprocessing.Process(target=c.start) for c in connectors]
    for p in processes:
        p.start()
    return processes


def setup_signals():
    global __KEEP_RUNNING
    __KEEP_RUNNING = True
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)


def main(cfg: Config):
    setup_signals()
    logger = init_logger(cfg)

    server_process = None
    if cfg.webserver_enabled:
        server = WebServer(
            port=cfg.webserver_port,
            pictures_dir=cfg.compositions_dest_dir,
            event_log=cfg.events_log_path,
        )
        server_process = multiprocessing.Process(target=server.start)
        server_process.start()

    logger.info("Starting connectors")
    connector_processes = start_connectors(cfg)

    booth_kwargs = {}
    if cfg.composition_test_mode:
        booth_kwargs = {
            "show_compositions": True,
            "seconds_before_session": 0,
            "seconds_between_captures": 0,
            "composition_yaml_hot_reload": True,
        }

    booth = PhotoBooth(
        cfg.composition_yaml_path,
        cfg.captures_dest_dir,
        cfg.compositions_dest_dir,
        cfg.camera_type,
        cfg.events_log_path,
        **booth_kwargs,
    )
    global __RUNNING_BOOTH
    __RUNNING_BOOTH = booth
    booth.start()

    logger.info("Waiting for capture trigger...")

    while __KEEP_RUNNING:
        listener = Listener(on_press=on_press)
        listener.on_release = functools.partial(on_release, listener, booth)
        listener.start()
        listener.join()

    logger.info("Shutting down processes...")

    for conn_proc in connector_processes:
        conn_proc.terminate()
        conn_proc.join()

    if server_process is not None:
        server_process.kill()
        server_process.join()


if __name__ == "__main__":
    config = Config.from_program_args()
    main(config)
