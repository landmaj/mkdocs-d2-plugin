import subprocess
from functools import partial
from typing import Any

from markdown import Markdown
from mkdocs.plugins import log
from pydantic import ValidationError
from pymdownx.superfences import fence_code_format

from d2.config import D2Config, PluginConfig

NAME = "mkdocs-d2-plugin"

info = partial(log.info, f"{NAME}: %s")
error = partial(log.error, f"{NAME}: %s")


class Renderer:
    def __init__(self, config: PluginConfig) -> None:
        self.global_config = config

    def validator(
        self,
        language: str,
        inputs: dict[str, str],
        options: dict[str, Any],
        attrs: dict[str, Any],
        md: Markdown,
    ) -> bool:
        cfg = self.global_config.dict()
        cfg.update(**inputs)
        try:
            cfg = D2Config(**cfg)
        except ValidationError as e:
            error(e)
            return False

        if cfg.render:
            options["render"] = True
            options["env"] = cfg.env()
        else:
            options["render"] = False
        return True

    def formatter(
        self,
        source: str,
        language: str,
        class_name: str,
        options: dict[str, Any],
        md: Markdown,
        **kwargs: Any,
    ) -> str:
        if not options["render"]:
            info("Skipping rendering")
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        try:
            result = subprocess.run(
                [
                    self.global_config.executable,
                    "-",
                    "-",
                ],
                env=options["env"],
                input=source.encode(),
                capture_output=True,
            )
        except FileNotFoundError:
            error("Failed to find d2 executable. Is it installed?")
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )
        except Exception as e:
            error(e)
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        if result.returncode != 0:
            error(result.stderr.decode().strip())
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        svg = result.stdout.decode()
        return f"<div> <style> svg>a:hover {{ text-decoration: underline }} </style> {svg} </div>"
