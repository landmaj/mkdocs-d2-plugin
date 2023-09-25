import os
import re
import subprocess
from functools import partial
from typing import Dict

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin, log
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

NAME = "mkdocs-d2-plugin"

info = partial(log.info, f"{NAME}: %s")
debug = partial(log.debug, f"{NAME}: %s")
error = partial(log.error, f"{NAME}: %s")


pattern = re.compile(
    rf"(?:```)(d2)((?:\s?[a-zA-Z0-9\-_]+=[a-zA-Z0-9\-_\.]+)*)\n(.*?)(?:```)",
    flags=re.IGNORECASE + re.DOTALL,
)

templateOK = """<div>
    <style>
        svg > a:hover {{
            text-decoration: underline
        }}
    </style>
    {svg}
</div>
"""

templateErrArgs = """!!! failure inline end
    {err}
`d2 {args}`
```d2
{code}
```
"""

templateErrCompile = """!!! failure inline end
    {err}
```d2
{code}
```
"""

options = {"theme", "sketch", "scale", "pad"}


class D2Config(Config):
    theme = config_options.Type(int, default=0)
    sketch = config_options.Type(bool, default=False)
    pad = config_options.Type(int, default=100)
    scale = config_options.Type(float, default=-1.0)


class D2Plugin(BasePlugin[D2Config]):
    def on_page_markdown(
        self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str | None:
        def replace_block(match_obj):
            return self._replace_block(match_obj)

        return re.sub(pattern, replace_block, markdown)

    def _validate_cfg(self, cfg) -> str | None:
        try:
            cfg["theme"] = int(cfg["theme"])
        except ValueError:
            return "theme must be an integer"

        if not isinstance(cfg["sketch"], bool):
            if cfg["sketch"] not in ("true", "false"):
                return "sketch must be a boolean"
            cfg["sketch"] = cfg["sketch"] == "true"

        try:
            cfg["pad"] = int(cfg["pad"])
        except ValueError:
            return "pad must be an integer"

        try:
            cfg["scale"] = float(cfg["scale"])
        except ValueError:
            return "scale must be a float"

    def _cfg_from_args(self, args) -> Dict[str, str]:
        cfg = {
            "theme": self.config.theme,
            "sketch": self.config.sketch,
            "pad": self.config.pad,
            "scale": self.config.scale,
        }

        opts = dict(x.split("=") for x in args.strip().split(" ")) if args else {}
        if d := set(opts.keys()) - options:
            error(f"Unrecognized arguments: {d}")
        cfg.update(opts)

        return cfg

    def _replace_block(self, match_obj):
        args = match_obj.group(2)
        data = match_obj.group(3)

        cfg = self._cfg_from_args(args)
        if err := self._validate_cfg(cfg):
            error(err)
            return templateErrArgs.format(err=err, args=args, code=data)

        env = os.environ.copy()
        env["D2_THEME"] = str(cfg["theme"])
        env["D2_SKETCH"] = "true" if cfg["sketch"] else "false"
        env["D2_PAD"] = str(cfg["pad"])
        env["SCALE"] = str(cfg["scale"])

        try:
            result = subprocess.run(
                [
                    "d2",
                    "-",
                    "-",
                ],
                env=env,
                input=data.encode(),
                capture_output=True,
            )
        except FileNotFoundError:
            error("Failed to find d2 executable. Is it installed?")
            return f'!!! failure "Failed to find d2 executable. Is it installed?"\n'

        if result.returncode != 0:
            err = result.stderr.decode().replace('"', "").strip()
            error(f"Failed to render diagram: {err}")
            return templateErrCompile.format(err=err, code=data)
        return templateOK.format(svg=result.stdout.decode())
