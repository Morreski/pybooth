import yaml

from . import CompositionSpec


def load_composition(spec: dict) -> CompositionSpec:
    return CompositionSpec(**spec)


def load_yaml(path: str) -> CompositionSpec:
    with open(path) as f:
        spec = yaml.load(f, Loader=yaml.CLoader)
    return load_composition(spec)
