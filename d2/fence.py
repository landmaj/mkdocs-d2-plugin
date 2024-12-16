from typing import Any, Dict

from markdown import Markdown
from pydantic import ValidationError
from pymdownx.superfences import fence_code_format

from d2 import Renderer, error
from d2.config import D2Config


class D2CustomFence:
    def __init__(
        self,
        config: Dict[str, Any],
        renderer: Renderer,
    ) -> None:
        self.config = config
        self.renderer = renderer

    def validator(
        self,
        language: str,
        inputs: Dict[str, str],
        options: Dict[str, Any],
        attrs: Dict[str, Any],
        md: Markdown,
    ) -> bool:
        options["render"] = falsy(inputs.pop("render", "True"))
        options["alt"] = inputs.pop("alt", "Diagram")

        cfg = self.config.copy()
        cfg.update(**inputs)
        try:
            cfg = D2Config(**cfg)
        except ValidationError as e:
            error(e)
            return False

        options["opts"] = cfg.opts()
        if cfg.has_dark_theme():
            options["opts_dark"] = cfg.opts(dark=True)

        return True

    def formatter(
        self,
        source: str,
        language: str,
        class_name: str,
        options: Dict[str, Any],
        md: Markdown,
        **kwargs: Any,
    ) -> str:
        if not options["render"]:
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        result, _, ok = self.renderer(source.encode(), options["opts"], options["alt"])
        if not ok:
            error(result)
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        if "opts_dark" not in options:
            return f'<div class="d2">{result}</div>'

        dark_result, _, ok = self.renderer(
            source.encode(), options["opts_dark"], options["alt"]
        )
        if not ok:
            error(dark_result)
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        return (
            '<div class="d2">'
            f'<div class="d2-light">{result}</div>'
            f'<div class="d2-dark">{dark_result}</div>'
            "</div>"
        )


def falsy(value: str) -> bool:
    if value.lower() in {"0", "false", "no", "off"}:
        return False
    return True
