import dataclasses
from typing import Iterable


@dataclasses.dataclass
class Box:
    xmin: float
    xmax: float
    ymin: float
    ymax: float


@dataclasses.dataclass
class Canvas:
    width: int
    height: int
    color: str


@dataclasses.dataclass
class Layer:
    kind: str
    box: Box

    @classmethod
    def new(cls, fields: dict):
        _mapping = {"image": ImageLayer, "capture": CaptureLayer}
        if fields.get("kind") not in _mapping:
            raise ValueError(f"Unknown Layer kind: {fields.get('kind')}")
        return _mapping[fields.get("kind")](**fields)


@dataclasses.dataclass
class ImageLayer(Layer):
    src: str


@dataclasses.dataclass
class CaptureLayer(Layer):
    pass


@dataclasses.dataclass
class CompositionSpec:
    name: str
    canvas: Canvas
    layers: Iterable[Layer]
