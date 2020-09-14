import os
import json
import asyncio

import tornado.websocket
import tornado

FRONT_DIR = os.path.join(os.path.dirname(__file__), "front")


class PhotoBoothHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def initialize(self, pictures_dir: str):
        self.pictures_dir = pictures_dir
        self.pics = set()
        self.sent_pics = set()

    async def open(self):
        while True:
            self.pics = {os.path.basename(f) for f in os.listdir(self.pictures_dir)}
            await asyncio.sleep(1)
            self.write_message(json.dumps(list(self.pics - self.sent_pics)))
            self.sent_pics = self.sent_pics.union(self.pics)

    def notify_game_event(self):
        pass

    async def on_message(self, message: str):
        pass


class WebServer:
    def __init__(self, port: int, pictures_dir: str):
        self.port = port
        self.app = tornado.web.Application(
            [
                (r"/pictures", PhotoBoothHandler, {"pictures_dir": pictures_dir}),
                (
                    r"/pictures/(.*)",
                    tornado.web.StaticFileHandler,
                    {"path": pictures_dir},
                ),
                (
                    r"/(.*)",
                    tornado.web.StaticFileHandler,
                    {"path": FRONT_DIR, "default_filename": "index.html"},
                ),
            ]
        )

    def start(self):
        self.app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()
