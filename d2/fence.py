from typing import Any, Dict

from markdown import Markdown
from mkdocs.exceptions import PluginError
from pydantic import ValidationError
from pymdownx.superfences import fence_code_format

from d2 import Renderer, error
from d2.config import D2Config


class D2CustomFence:
    def __init__(
        self,
        config: Dict[str, Any],
        renderer: Renderer,
        raise_on_error: bool,
    ) -> None:
        self.config = config
        self.renderer = renderer
        self.raise_on_error = raise_on_error

    def validator(
        self,
        language: str,
        inputs: Dict[str, str],
        options: Dict[str, Any],
        attrs: Dict[str, Any],
        md: Markdown,
    ) -> bool:
        options["render"] = falsy(inputs.pop("render", "True"))

        cfg = self.config.copy()
        cfg.update(**inputs)
        try:
            cfg = D2Config(**cfg)
        except ValidationError as e:
            if self.raise_on_error:
                raise PluginError(e)
            else:
                error(e)
                return False

        options["opts"] = cfg.opts()
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

        result, ok = self.renderer(source.encode(), options["opts"])
        if not ok:
            if self.raise_on_error:
                raise PluginError(result)
            else:
                error(result)
                return fence_code_format(
                    source, language, class_name, options, md, **kwargs
                )

        return f"<div><style>svg>a:hover {{ text-decoration: underline }}</style>{result}</div>"


def falsy(value: str) -> bool:
    if value.lower() in {"0", "false", "no", "off"}:
        return False
    return True
