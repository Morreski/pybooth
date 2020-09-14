from typing import List
from PIL import Image


class OffsetComposition:
    PHOTO_COUNT = 6
    SIZE = (1200, 1800)

    def __init__(self, background_path: str):
        self.background_path = background_path
        self.tile_size = (455, 455)
        self.tile_coords = [
            (104, 308),
            (104, 804),
            (104, 1300),
            (662, 45),
            (662, 541),
            (662, 1037),
        ]

    def compose(self, pics: List[str], dest: str):
        if len(pics) != self.PHOTO_COUNT:
            raise ValueError("Need 4 images for basic composition")

        loaded_pics = [Image.open(p) for p in pics]
        background = Image.open(self.background_path)
        if background.size != self.SIZE:
            raise ValueError(
                f"Bad background size. Expected {self.SIZE} got {background.size}"
            )

        tiles = [self.make_tile(p) for p in loaded_pics]

        for tile, coords in zip(tiles, self.tile_coords):
            background.paste(tile, coords)

        background.save(dest)

    def make_tile(
        self, pic: Image,
    ):
        tile_ratio = self.tile_size[0] / self.tile_size[1]
        image_ratio = pic.width / pic.height

        if tile_ratio == image_ratio:
            return pic.resize(self.tile_size)
        elif image_ratio < tile_ratio:
            crop_w, crop_h = (pic.width, pic.width / tile_ratio)
        else:
            crop_w, crop_h = (pic.height * tile_ratio, pic.height)

        return pic.crop(
            (
                (pic.width - crop_w) / 2,
                (pic.height - crop_h) / 2,
                (pic.width + crop_w) / 2,
                (pic.height + crop_h) / 2,
            )
        ).resize(self.tile_size)
