from typing import Any

from markdown import Markdown
from pydantic import ValidationError
from pymdownx.superfences import fence_code_format

from d2 import error, render
from d2.config import D2Config, PluginConfig


class D2CustomFence:
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
        options["render"] = falsy(inputs.pop("render", "True"))

        cfg = self.global_config.d2_config()
        cfg.update(**inputs)
        try:
            cfg = D2Config(**cfg)
        except ValidationError as e:
            error(e)
            return False

        options["env"] = cfg.env()
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
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        result, ok = render(
            self.global_config.executable, source.encode(), options["env"]
        )
        if not ok:
            error(result)
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        return f"<div><style>svg>a:hover {{ text-decoration: underline }}</style>{result}</div>"


def falsy(value: str) -> bool:
    if value.lower() in {"0", "false", "no", "off"}:
        return False
    return True
