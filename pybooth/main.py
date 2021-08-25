import logging
import functools
import argparse
import multiprocessing

from pynput.keyboard import Listener, Key

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


def main(args):
    logger = init_logger(args)

    server_process = None
    if args.web is not None:
        server = WebServer(
            port=args.web, pictures_dir=args.compositions_dir, event_log=args.event_log
        )
        server_process = multiprocessing.Process(target=server.start)
        server_process.start()

    booth = PhotoBooth(
        args.composition_background,
        args.captures_dir,
        args.compositions_dir,
        args.camera_type,
        args.event_log,
    )

    logger.info("Waiting for capture trigger...")

    while True:
        listener = Listener(on_press=on_press)
        listener.on_release = functools.partial(on_release, listener, booth)
        listener.start()
        listener.join()

    if server_process is not None:
        server_process.join()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "composition_background",
        metavar="FILE",
        help="Image used as background for composition",
    )
    parser.add_argument(
        "--captures_dir",
        "-O",
        metavar="PATH",
        default="./captures",
        help="Directory where pictures will be stored",
    )
    parser.add_argument(
        "--compositions_dir",
        "-o",
        metavar="PATH",
        default="./compositions",
        help="Directory where compositions will be stored",
    )
    parser.add_argument(
        "--camera_type",
        metavar="VALUE",
        choices=("gphoto", "dummy"),
        default="gphoto",
        help="Camera backend to use",
    )
    parser.add_argument(
        "--event_log",
        "-e",
        metavar="PATH",
        default="./booth_events.log",
        help="Append only event log path",
    )
    parser.add_argument(
        "--web",
        metavar="PORT",
        type=int,
        help="Start webserver on specified port",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
