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
                    "box": Box(0.4, 0, 0.6, 1),
                    "src": "tests/assets/lenna.png",
                    "fit": "cover",
                    "background_opacity": 0.7,
                    "opacity": 0.7,
                }
            ),
            Layer.new(
                {
                    "kind": "image",
                    "box": Box(0.05, 0.5, 0.35, 0.7),
                    "src": "tests/assets/lenna.png",
                    "fit": "contain",
                    "background_opacity": 128,
                    "opacity": 0.9,
                    "background_color": "#cc241d",
                }
            ),
            Layer.new(
                {
                    "kind": "capture",
                    "box": Box(0.1, 0.1, 0.35, 0.45),
                    "fit": "fill",
                    "rotation": 30.0,
                }
            ),
        ],
    )
    comp_renderer = renderer.PILRenderer(spec, captures_path=["tests/assets/lenna.png"])
    img = comp_renderer.render()
    img.save("/tmp/test.jpg")
