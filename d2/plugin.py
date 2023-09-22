import os
import re
import subprocess
from functools import partial
from pathlib import Path

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin, log
from mkdocs.structure.files import File

NAME = "mkdocs-d2-plugin"

info = partial(log.info, f"{NAME}: %s")
debug = partial(log.debug, f"{NAME}: %s")
error = partial(log.error, f"{NAME}: %s")


class D2Config(Config):
    out_dir = config_options.Type(str, default="d2-plugin")

    theme = config_options.Type(int, default=0)
    sketch = config_options.Type(bool, default=False)


class D2Plugin(BasePlugin[D2Config]):
    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        self._site_dir = Path(config["site_dir"], "assets", "diagrams")
        self._site_url = config.get("site_url", "/")
        return config

    def on_page_markdown(self, markdown, files, page, **_kwargs):
        def replace_block(match_obj):
            return self._replace_block(match_obj, files, page)

        return re.sub(self.pattern, replace_block, markdown)

    pattern = re.compile(
        rf"(?:```)(d2)((?:\s?[a-zA-Z0-9\-_]+=[a-zA-Z0-9\-_\.]+)*)\n(.*?)(?:```)",
        flags=re.IGNORECASE + re.DOTALL,
    )

    def _replace_block(self, match_obj, files, page):
        args = match_obj.group(2)
        data = match_obj.group(3)

        opts = dict(x.split("=") for x in args.strip().split(" ")) if args else {}
        name = opts.get("name")
        if not name:
            error("Diagram name not specified! Syntax: `d2 name=diagram_name`")
            return f'!!! failure "Diagram name not specified! Syntax: `d2 name=diagram_name`"\n\n```\n{data}\n```'
        try:
            scale = opts.get("scale", -1.0)
            scale = float(scale)
        except ValueError:
            error("Scale must be a float! Syntax: `d2 scale=-1.0`")
            return f'!!! failure "Scale must be a float! Syntax: `d2 scale=1.0`"\n\n```\n{data}\n```'
        try:
            pad = opts.get("pad", 100)
            pad = int(pad)
        except ValueError:
            error("Pad must be an integer! Syntax: `d2 pad=100`")
            return f'!!! failure "Pad must be an integer! Syntax: `d2 pad=100`"\n\n```\n{data}\n```'

        filename = f"{name}.svg"
        filepath = f"{self.config.out_dir}/{filename}"

        cmd_env = os.environ.copy()
        cmd_env["D2_THEME"] = str(self.config.theme)
        cmd_env["D2_PAD"] = str(pad)
        cmd_env["SCALE"] = str(scale)
        if self.config.sketch:
            cmd_env["D2_SKETCH"] = "true"

        subprocess.run(
            [
                "d2",
                "-",
                filepath,
            ],
            env=cmd_env,
            input=data.encode(),
            check=True,
        )

        mkdocs_file = File(filename, self.config.out_dir, self._site_dir, False)
        files.append(mkdocs_file)

        return f"<img src='{self._site_url}/assets/diagrams/{mkdocs_file.url}' alt={name} />"
