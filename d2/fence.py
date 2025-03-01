import xml.etree.ElementTree as etree
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

        result, svg, ok = self.renderer(
            source.encode(), options["opts"], options["alt"]
        )
        if not ok:
            error(result)
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        elem = etree.Element("div")
        elem.set("class", "d2")

        new_tab_button = etree.Element("button")
        new_tab_button.set("class", "d2-button")
        new_tab_button.set("onclick", f'd2OpenInNewTab("{result}")')
        new_tab_button.text = "Open diagram in new tab"

        if "opts_dark" not in options:
            elem.append(svg.root)
            elem.append(new_tab_button)
            return etree.tostring(elem, encoding="utf-8", method="html").decode()

        dark_result, dark_svg, ok = self.renderer(
            source.encode(), options["opts_dark"], options["alt"]
        )
        if not ok:
            error(dark_result)
            return fence_code_format(
                source, language, class_name, options, md, **kwargs
            )

        light = etree.Element("div", {"class": "d2-light"})
        light.append(svg.root)
        light.append(new_tab_button)
        elem.append(light)

        dark_new_tab_button = etree.Element("button")
        dark_new_tab_button.set("class", "d2-button")
        dark_new_tab_button.set("onclick", f'd2OpenInNewTab("{dark_result}")')
        dark_new_tab_button.text = "Open diagram in new tab"

        dark = etree.Element("div", {"class": "d2-dark"})
        dark.append(dark_svg.root)
        dark.append(dark_new_tab_button)
        elem.append(dark)

        return etree.tostring(elem, encoding="utf-8", method="html").decode()


def falsy(value: str) -> bool:
    if value.lower() in {"0", "false", "no", "off"}:
        return False
    return True
