import os
import itertools


class DummyCamera:
    def __init__(self, out_dir: str = "./", base_filename: str = "pic"):
        self.out_dir = out_dir
        self.base_filename = base_filename
        self.jpgs = [
            os.path.join(self.out_dir, fp)
            for fp in os.listdir(self.out_dir)
            if os.path.splitext(fp)[1].lower() == ".jpg"
        ]
        self.jpg_iterator = itertools.cycle(self.jpgs)

    def take_picture(self) -> str:
        return next(self.jpg_iterator)
