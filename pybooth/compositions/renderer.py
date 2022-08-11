import functools
import math
import copy
import itertools
from typing import Iterable

from PIL import Image, ImageFile

from . import CompositionSpec, Layer, Box, PxBox, ImageLayer, CaptureLayer

# Prevent bug if images are truncated on disk for some reason
ImageFile.LOAD_TRUNCATED_IMAGES = True


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
        box = self._get_box_coords_px(layer.box)
        layer_img = Image.new("RGBA", (box.width, box.height), layer.background_color)
        layer_img.putalpha(layer.background_opacity)
        compute_func = getattr(
            self,
            f"_compute_{layer.kind}_layer",
            functools.partial(self.__compute_unknown_layer, layer.kind),
        )
        compute_func(layer_img, layer)
        composition.paste(layer_img, (box.xmin, box.ymin), layer_img)

    def _compute_image_layer(self, layer_img: Image, layer: ImageLayer):
        img = Image.open(layer.src)
        img = img.convert("RGBA")
        fit_func = getattr(
            self,
            f"_compute_fit_{layer.fit}",
            functools.partial(self.__compute_unknown_fit, layer.fit),
        )
        box = self._get_box_coords_px(layer.box)
        img = fit_func(box, img)
        box_center = math.floor(box.width / 2), math.floor(box.height // 2)
        image_coords = (
            box_center[0] - math.floor(img.width / 2),
            box_center[1] - math.floor(img.height / 2),
        )
        img.putalpha(layer.opacity)
        layer_img.paste(img, image_coords, img)

    def _compute_capture_layer(self, layer_img: Image, layer: CaptureLayer):
        layer = copy.deepcopy(layer)
        layer.src = next(self._captures_path_iter)
        return self._compute_image_layer(layer_img, layer)

    def __compute_unknown_layer(self, kind: str, *args, **kwargs):
        raise NotImplementedError(f"Don't know how to process layer kind: {kind}")

    def _get_box_coords_px(self, box: Box) -> PxBox:
        return PxBox(
            *self._get_coords_px(box.xmin, box.ymin),
            *self._get_coords_px(box.xmax, box.ymax),
        )

    def _get_coords_px(self, x: float, y: float):
        return math.floor(x * self._spec.canvas.width), math.floor(
            y * self._spec.canvas.height
        )

    def _compute_fit_contain(self, box: PxBox, obj: Image):
        b_w, b_h = box.width, box.height
        w, h = obj.width, obj.height
        # t_w = b_w if w >= h else math.floor(b_h * w / h)
        # t_h = b_h if h > w else math.floor(b_w * h / w)
        t_w = min(b_w, math.floor(b_h * w / h))
        t_h = min(b_h, math.floor(b_w * h / w))
        return obj.resize((t_w, t_h))

    def _compute_fit_cover(self, box: PxBox, obj: Image):
        b_w, b_h = box.width, box.height
        w, h = obj.width, obj.height
        t_w = max(b_w, math.floor(b_h * w / h))
        t_h = max(b_h, math.floor(b_w * h / w))
        return obj.resize((t_w, t_h))

    def _compute_fit_fill(self, box: PxBox, obj: Image):
        b_w, b_h = box.width, box.height
        return obj.resize((b_w, b_h))

    def __compute_unknown_fit(self, fit_value: str, *args, **kwargs):
        raise ValueError(f"Bad value for fit: {fit_value}")
