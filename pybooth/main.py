import logging
import functools
import multiprocessing

from pynput.keyboard import Listener, Key

from config import Config
from web import WebServer
from booth import PhotoBooth


def on_press(key):
    pass


def on_release(listener: Listener, booth: PhotoBooth, key):
    if key != Key.space:
        return
    booth.start_session()
    listener.stop()  # Ignore keypress that occured while taking pictures


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


def main(cfg: Config):
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

    logger.info("Waiting for capture trigger...")

    while True:
        listener = Listener(on_press=on_press)
        listener.on_release = functools.partial(on_release, listener, booth)
        listener.start()
        listener.join()

    if server_process is not None:
        server_process.join()


if __name__ == "__main__":
    config = Config.from_program_args()
    main(config)
