import os
import re
import subprocess
import tempfile
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
    output = config_options.Type(str, default="assets/diagrams")
    theme = config_options.Type(int, default=0)
    sketch = config_options.Type(bool, default=False)


class D2Plugin(BasePlugin[D2Config]):
    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        self._site_dir = Path(config["site_dir"], self.config.output)
        self._tmp_dir = tempfile.TemporaryDirectory()
        return config

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        if hasattr(self, "_tmp_dir"):
            self._tmp_dir.cleanup()

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
            return f'!!! failure "Diagram name not specified! Syntax: `d2 name=diagram_name`"\n'
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

        filename = f"{name}.svg"
        filepath = f"{self._tmp_dir.name}/{filename}"

        cmd_env = os.environ.copy()
        cmd_env["D2_THEME"] = str(self.config.theme)
        cmd_env["D2_PAD"] = str(pad)
        cmd_env["SCALE"] = str(scale)
        if self.config.sketch:
            cmd_env["D2_SKETCH"] = "true"

        try:
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
        except FileNotFoundError:
            error("Failed to find d2 executable. Is it installed?")
            return f'!!! failure "Failed to find d2 executable. Is it installed?"\n'
        except subprocess.CalledProcessError as e:
            error(f"Failed to generate diagram. Return code: {e.returncode}.")
            return f'!!! failure "Failed to generate diagram. Return code: {e.returncode}."\n'

        mkdocs_file = File(filename, self._tmp_dir.name, self._site_dir, False)
        files.append(mkdocs_file)

        return f"<img src='/{self.config.output}/{mkdocs_file.url}' alt={name} />"
