from pybooth.compositions import loader, renderer, CompositionSpec, Canvas, Layer, Box


def test_yaml_loader():
    spec = loader.load_yaml("./tests/assets/composition.yaml")
    assert spec.name == "composition_sample"
    assert spec.captures_count == 4


def test_composition_rendering():
    spec = CompositionSpec(
        name="test_compo", canvas=Canvas(500, 500, "#ffffff"), layers=[]
    )
    comp_renderer = renderer.PILRenderer(spec)
    comp_renderer.render()
