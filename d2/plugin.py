import os
import re
import subprocess
from functools import partial

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

template = """<div>
    <style>
        svg > a:hover {{
            text-decoration: underline
        }}
    </style>
    {svg}
</div>
"""


class D2Config(Config):
    theme = config_options.Type(int, default=0)
    sketch = config_options.Type(bool, default=False)


class D2Plugin(BasePlugin[D2Config]):
    def on_page_markdown(
        self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str | None:
        def replace_block(match_obj):
            return self._replace_block(match_obj)

        return re.sub(pattern, replace_block, markdown)

    def _replace_block(self, match_obj):
        args = match_obj.group(2)
        data = match_obj.group(3)

        opts = dict(x.split("=") for x in args.strip().split(" ")) if args else {}
        try:
            scale = opts.get("scale", -1.0)
            scale = float(scale)
        except ValueError:
            error("Scale must be a float! Syntax: `d2 scale=-1.0`")
            return f'!!! failure "Scale must be a float! Syntax: `d2 scale=1.0`"\n'
        try:
            pad = opts.get("pad", 100)
            pad = int(pad)
        except ValueError:
            error("Pad must be an integer! Syntax: `d2 pad=100`")
            return f'!!! failure "Pad must be an integer! Syntax: `d2 pad=100`"\n'

        cmd_env = os.environ.copy()
        cmd_env["D2_THEME"] = str(self.config.theme)
        cmd_env["D2_PAD"] = str(pad)
        cmd_env["SCALE"] = str(scale)
        if self.config.sketch:
            cmd_env["D2_SKETCH"] = "true"

        try:
            result = subprocess.run(
                [
                    "d2",
                    "-",
                    "-",
                ],
                env=cmd_env,
                input=data.encode(),
                capture_output=True,
            )
        except FileNotFoundError:
            error("Failed to find d2 executable. Is it installed?")
            return f'!!! failure "Failed to find d2 executable. Is it installed?"\n'

        if result.returncode != 0:
            err = result.stderr.decode().replace('"', "").strip()
            error(f"Failed to render diagram: {err}")
            return f'!!! failure "{err}"\n\n```d2\n{data}\n```'
        return template.format(svg=result.stdout.decode())
