import os
from typing import Dict

from mkdocs.config import config_options
from mkdocs.config.base import Config
from pydantic import BaseModel


class PluginConfig(Config):
    executable = config_options.Type(str, default="d2")

    layout = config_options.Type(str, default="dagre")
    theme = config_options.Type(int, default=0)
    dark_theme = config_options.Type(int, default=-1)
    sketch = config_options.Type(bool, default=False)
    pad = config_options.Type(int, default=100)
    scale = config_options.Type(float, default=-1.0)
    force_appendix = config_options.Type(bool, default=False)

    def d2_config(self):
        _dict = {}
        for k, v in self.items():
            if k in {"executable"}:
                continue
            _dict[k] = v
        return _dict


class D2Config(BaseModel, extra="forbid"):
    layout: str
    theme: int
    dark_theme: int
    sketch: bool
    pad: int
    scale: float
    force_appendix: bool

    def env(self) -> Dict[str, str]:
        e = os.environ.copy()
        e.update(
            {
                "D2_LAYOUT": self.layout,
                "D2_THEME": str(self.theme),
                "D2_DARK_THEME": str(self.dark_theme),
                "D2_SKETCH": "true" if self.sketch else "false",
                "D2_PAD": str(self.pad),
                "SCALE": str(self.scale),
                "D2_FORCE_APPENDIX": "true" if self.force_appendix else "false",
            }
        )
        return e
