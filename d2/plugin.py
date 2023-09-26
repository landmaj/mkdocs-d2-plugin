import os
import re
import subprocess
import textwrap
from functools import partial
from typing import Dict

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin, log
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from pydantic import BaseModel, ValidationError

NAME = "mkdocs-d2-plugin"

info = partial(log.info, f"{NAME}: %s")
error = partial(log.error, f"{NAME}: %s")


pattern = re.compile(
    rf"(?:```)(d2)((?:\s?[a-zA-Z0-9\-_]+=[a-zA-Z0-9\-_\.]+)*)\n(.*?)(?:```)",
    flags=re.IGNORECASE + re.DOTALL,
)


class PluginConfig(Config):
    executable = config_options.Type(str, default="d2")

    layout = config_options.Type(str, default="dagre")
    theme = config_options.Type(int, default=0)
    dark_theme = config_options.Type(int, default=-1)
    sketch = config_options.Type(bool, default=False)
    pad = config_options.Type(int, default=100)
    scale = config_options.Type(float, default=-1.0)
    force_appendix = config_options.Type(bool, default=False)


class D2Config(BaseModel):
    layout: str
    theme: int
    dark_theme: int
    sketch: bool
    pad: int
    scale: float
    force_appendix: bool

    @classmethod
    def fromPluginConfig(cls, cfg: PluginConfig, args: str) -> "D2Config":
        opts = {k: v for k, v in cfg.items()}
        opts.update(dict(x.split("=") for x in args.strip().split(" ")) if args else {})
        return cls(**opts)

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


class Plugin(BasePlugin[PluginConfig]):
    def on_page_markdown(
        self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str | None:
        def replace_block(match_obj):
            return self._replace_block(match_obj)

        return re.sub(pattern, replace_block, markdown)

    def _replace_block(self, match_obj):
        args = match_obj.group(2)
        data = match_obj.group(3)

        try:
            cfg = D2Config.fromPluginConfig(self.config, args)
        except ValidationError as e:
            error(f"Invalid arguments: {e}")
            msg = '!!! failure inline end "Invalid arguments"\n'
            for err in e.errors():
                msg += f"    - **{err['loc'][0]}** [{err['input']}]: {err['msg']}  \n"
            msg += f"```d2\n{data}\n```"
            return msg

        try:
            result = subprocess.run(
                [
                    self.config.executable,
                    "-",
                    "-",
                ],
                env=cfg.env(),
                input=data.encode(),
                capture_output=True,
            )
        except FileNotFoundError:
            error("Failed to find d2 executable. Is it installed?")
            return f'!!! failure "Failed to find d2 executable. Is it installed?"\n'

        if result.returncode != 0:
            err = result.stderr.decode().strip()
            err = re.sub(r"err:\s", "", err)
            prefix = "failed to compile: "
            if err.startswith(prefix):
                err = err[len(prefix) :]
            error(f"Failed to compile: {err}")
            return (
                '!!! failure inline end "Failed to compile"\n'
                f'{textwrap.indent(err, "    ")}\n'
                f"```d2\n{data}\n```\n"
            )

        svg = result.stdout.decode()
        return f"<div> <style> svg>a:hover {{ text-decoration: underline }} </style> {svg} </div>"
