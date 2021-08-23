import os
import json
import asyncio

import tornado.websocket
import tornado

FRONT_DIR = os.path.join(os.path.dirname(__file__), "front")


class PhotoBoothHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def initialize(self, pictures_dir: str, event_log: str):
        self.pictures_dir = pictures_dir
        self.event_reader = open(event_log, "r")
        self.event_reader.seek(os.path.getsize(event_log))
        self.is_alive = True

    async def open(self):
        await self.send_existing_pics()
        async for evt in self.get_next_event():
            self.write_message(evt)

    async def on_close(self):
        self.is_alive = False

    async def get_next_event(self):
        while self.is_alive:
            l = self.event_reader.readline()
            if l == "":
                await asyncio.sleep(0.5)
                continue
            evt = self.parse_event(l)
            if evt is None:
                continue
            yield evt

    async def send_existing_pics(self):
        pics = [os.path.basename(f) for f in os.listdir(self.pictures_dir)]
        await self.write_message(
            json.dumps({"event": "WEB_INIT", "data": {"pics": pics}})
        )

    def parse_event(self, evt: str):
        try:
            return json.loads(evt)
        except json.JSONDecodeError:
            return None

    async def on_message(self, message: str):
        pass


class WebServer:
    def __init__(self, port: int, pictures_dir: str, event_log: str):
        self.port = port
        self.app = tornado.web.Application(
            [
                (
                    r"/ws",
                    PhotoBoothHandler,
                    {"pictures_dir": pictures_dir, "event_log": event_log},
                ),
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
