from typing import Iterable

from . import CompositionSpec


class PILRenderer:
    def __init__(self, spec: CompositionSpec, *, captures_path: Iterable[str] = []):
        self._spec = spec
        self._captures_path = [c for c in captures_path]

    def add_capture(self, path: str):
        self.captures_path.append(path)

    def render(self):
        pass
