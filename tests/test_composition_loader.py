from pybooth.compositions.loader import load_yaml


def test_yaml_loader():
    composition = load_yaml("./tests/assets/composition.yaml")
    assert composition.name == "composition_sample"
