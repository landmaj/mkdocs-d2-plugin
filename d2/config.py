from typing import Dict

from mkdocs.config import config_options
from mkdocs.config.base import Config
from pydantic import BaseModel


class PluginConfig(Config):
    executable = config_options.Type(str, default="d2")
    cache = config_options.Type(bool, default=True)
    cache_dir = config_options.Type(str, default=".cache/plugin/d2")

    layout = config_options.Type(str, default="dagre")
    theme = config_options.Type(int, default=0)
    dark_theme = config_options.Type(int, default=-1)
    sketch = config_options.Type(bool, default=False)
    pad = config_options.Type(int, default=100)
    scale = config_options.Type(float, default=-1.0)
    force_appendix = config_options.Type(bool, default=False)
    target = config_options.Type(str, default="\'\'")

    def d2_config(self):
        _dict = {}
        for k, v in self.items():
            if k in {"executable", "cache", "cache_dir"}:
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
    target: str

    def env(self) -> list[str]:
        opts = [
            "--layout", self.layout,
            "--theme", str(self.theme),
            "--dark-theme", str(self.dark_theme),
            "--pad", str(self.pad),
            "--scale", str(self.scale),
            "--target", str(self.target)
        ]

        opts = opts + [ "--sketch" ] if self.sketch else opts
        opts = opts + [ "--force-appendix" ] if self.force_appendix else opts

        return opts
