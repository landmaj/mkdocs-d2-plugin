from typing import List

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
    target = config_options.Type(str, default="''")

    def d2_config(self):
        _dict = {}
        for k, v in self.items():
            if k in {"executable", "cache", "cache_dir"}:
                continue
            _dict[k] = v
        return _dict


class D2Config(BaseModel, extra="allow"):
    layout: str
    theme: int
    dark_theme: int
    sketch: bool
    pad: int
    scale: float
    force_appendix: bool
    target: str

    def opts(self) -> List[str]:
        opts = [
            f"--layout={self.layout}",
            f"--theme={self.theme}",
            f"--dark-theme={self.dark_theme}",
            f"--sketch={str(self.sketch).lower()}",
            f"--pad={self.pad}",
            f"--scale={self.scale}",
            f"--force-appendix={str(self.force_appendix).lower()}",
            f"--target={self.target}",
        ]

        if extra := self.model_extra:
            for k, v in extra.items():
                opts += [f"--{k.replace('_', '-')}={v}"]

        return opts
