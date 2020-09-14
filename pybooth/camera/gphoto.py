import os
import logging

import gphoto2 as gp


class GphotoCamera:
    def __init__(self, out_dir: str = "./", base_filename: str = "pic"):
        self.camera = gp.Camera()
        self.out_dir = out_dir
        self.base_filename = base_filename
        self.photo_count = 0
        self.camera.init()

    def reset(self):
        self.camera.exit()
        self.camera = gp.Camera()
        self.camera.init()

    def take_picture(self) -> str:
        logging.debug("Taking picture...")
        path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        pic = self.camera.file_get(path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)
        pic_name = self.get_next_picture_name()
        pic_path = os.path.join(self.out_dir, pic_name)
        pic.save(pic_path)
        logging.debug(f"Image saved: {pic_path}")
        return pic_path

    def get_next_picture_name(self) -> str:
        self.photo_count += 1
        return f"{self.base_filename}_{str(self.photo_count)}.jpg"

    def __del__(self):
        self.camera.exit()
