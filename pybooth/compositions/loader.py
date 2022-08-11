import yaml
from dacite import from_dict

from . import CompositionSpec, Layer


def load_composition(spec: dict) -> CompositionSpec:
    composition_spec = from_dict(data_class=CompositionSpec, data=spec)
    composition_spec.layers = [
        Layer.new(l) for l in spec.get("layers", [])
    ]  # Re-instanciate layers because dacite will not cast them automatically to their relevant sub-types
    return composition_spec


def load_yaml(path: str) -> CompositionSpec:
    with open(path) as f:
        spec = yaml.load(f, Loader=yaml.CLoader)
    return load_composition(spec)
