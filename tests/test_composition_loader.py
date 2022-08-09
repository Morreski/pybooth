from pybooth.compositions import loader, renderer, CompositionSpec, Canvas, Layer, Box


def test_yaml_loader():
    spec = loader.load_yaml("./tests/assets/composition.yaml")
    assert spec.name == "composition_sample"
    assert spec.captures_count == 4


def test_composition_rendering():
    spec = CompositionSpec(
        name="test_compo",
        canvas=Canvas(500, 500, "#fbf1c7"),
        layers=[
            Layer.new(
                {
                    "kind": "image",
                    "box": Box(0.2, 0.2, 0.8, 0.8),
                    "src": "tests/assets/lenna.png",
                }
            ),
            Layer.new(
                {"kind": "capture", "box": Box(0.1, 0.1, 0.2, 0.2), "fit": "fill"}
            ),
        ],
    )
    comp_renderer = renderer.PILRenderer(spec, captures_path=["tests/assets/lenna.png"])
    img = comp_renderer.render()
    img.save("/tmp/test.jpg")
