import dataclasses
from typing import List, Union

import dacite


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
    virtual_width: int = 1
    virtual_height: int = 1


@dataclasses.dataclass
class Layer:
    kind: str
    box: Box
    background_color: str = "white"
    background_opacity: Union[int, float] = 0
    opacity: Union[int, float] = 255
    rotation: float = 0  # In degrees

    def __post_init__(self):
        if isinstance(self.background_opacity, float):
            self.background_opacity = min(round(255 * self.background_opacity), 255)
        if isinstance(self.opacity, float):
            self.opacity = min(round(255 * self.opacity), 255)

    @classmethod
    def new(cls, fields: dict):
        _mapping = {"image": ImageLayer, "capture": CaptureLayer}
        if fields.get("kind") not in _mapping:
            raise ValueError(f"Unknown Layer kind: {fields.get('kind')}")
        return dacite.from_dict(data_class=_mapping[fields.get("kind")], data=fields)


@dataclasses.dataclass
class ImageLayer(Layer):
    src: str = None
    fit: str = "contain"  # One of 'contain', 'cover', 'fill'


@dataclasses.dataclass
class CaptureLayer(ImageLayer):
    src: str = None


@dataclasses.dataclass
class CompositionSpec:
    name: str
    canvas: Canvas
    layers: List[Layer]

    captures_count: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.captures_count = len([l for l in self.layers if l.kind == "capture"])
