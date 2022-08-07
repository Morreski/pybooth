import yaml
from dacite import from_dict

from . import CompositionSpec


def load_composition(spec: dict) -> CompositionSpec:
    return from_dict(data_class=CompositionSpec, data=spec)


def load_yaml(path: str) -> CompositionSpec:
    with open(path) as f:
        spec = yaml.load(f, Loader=yaml.CLoader)
    return load_composition(spec)
