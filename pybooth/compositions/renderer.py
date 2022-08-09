import functools
import math
import copy
import itertools
from typing import Iterable

from PIL import Image

from . import CompositionSpec, Layer, Box, ImageLayer, CaptureLayer


class PILRenderer:
    def __init__(self, spec: CompositionSpec, *, captures_path: Iterable[str] = []):
        self._spec = spec
        self._captures_path = [c for c in captures_path]
        self._captures_path_iter = itertools.cycle(self._captures_path)

    def add_capture(self, path: str):
        self.captures_path.append(path)
        self._captures_path_iter = itertools.cycle(self._captures_path)

    def render(self) -> Image:
        composition = self.make_canvas()
        for layer in self._spec.layers:
            self._add_layer(composition, layer)
        return composition.convert("RGB")

    def make_canvas(self):
        canvas = self._spec.canvas
        return Image.new("RGBA", (canvas.width, canvas.height), canvas.color)

    def _add_layer(self, composition: Image, layer: Layer):
        xmin, ymin, xmax, ymax = self._get_box_coords_px(layer.box)
        width, height = xmax - xmin, ymax - ymin
        layer_img = Image.new("RGBA", (width, height))
        compute_func = getattr(
            self,
            f"_compute_{layer.kind}_layer",
            functools.partial(self.__compute_unknown_layer, layer.kind),
        )
        compute_func(layer_img, layer)
        composition.paste(layer_img, (xmin, ymin))

    def _compute_image_layer(self, layer_img: Image, layer: ImageLayer):
        img = Image.open(layer.src)
        layer_img.paste(img, (0, 0))  # TODO

    def _compute_capture_layer(self, layer_img: Image, layer: CaptureLayer):
        layer = copy.deepcopy(layer)
        layer.src = next(self._captures_path_iter)
        return self._compute_image_layer(layer_img, layer)

    def __compute_unknown_layer(self, kind: str, *args, **kwargs):
        raise NotImplementedError(f"Don't know how to process layer kind: {kind}")

    def _get_box_coords_px(self, box: Box):
        return *self._get_coords_px(box.xmin, box.ymin), *self._get_coords_px(
            box.xmax, box.ymax
        )

    def _get_coords_px(self, x: float, y: float):
        return math.floor(x * self._spec.canvas.width), math.floor(
            y * self._spec.canvas.height
        )
