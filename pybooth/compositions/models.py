import dataclasses
from typing import List


@dataclasses.dataclass
class Box:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    width: float = dataclasses.field(init=False)
    height: float = dataclasses.field(init=False)

    def __post_init__(self):
        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin


@dataclasses.dataclass
class PxBox(Box):
    xmin: int
    ymin: int
    xmax: int
    ymax: int

    width: int = dataclasses.field(init=False)
    height: int = dataclasses.field(init=False)


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
    fit: str = "contain"  # One of 'contain', 'cover', 'fill'


@dataclasses.dataclass
class CaptureLayer(ImageLayer):
    src: str = dataclasses.field(default=None)


@dataclasses.dataclass
class CompositionSpec:
    name: str
    canvas: Canvas
    layers: List[Layer]

    captures_count: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.captures_count = len([l for l in self.layers if l.kind == "capture"])
