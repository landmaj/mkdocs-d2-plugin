import xml.etree.ElementTree as etree
from pathlib import Path
from typing import Any, Dict, Optional

from markdown import Extension, Markdown
from markdown.treeprocessors import Treeprocessor
from pydantic import ValidationError

from d2 import Renderer, error, warning
from d2.config import D2Config


class D2ImgTreeprocessor(Treeprocessor):
    def __init__(
        self,
        md: Markdown,
        base_dir: str,
        config: Dict[str, Any],
        renderer: Renderer,
    ):
        self.base_dir = base_dir
        self.config = config
        self.renderer = renderer
        super().__init__(md)

    def run(self, root: etree.Element) -> Optional[etree.Element]:
        for elem in root.iter("img"):
            src = Path(elem.get("src", ""))
            if src.suffix == ".d2":
                diagram = Path(self.base_dir, src).resolve()
                if not diagram.exists():
                    warning(f"File not found: {diagram}")
                    continue

                cfg = self.config.copy()
                cfg.update(elem.attrib)
                cfg.pop("src")
                alt = cfg.pop("alt", "Diagram")

                try:
                    cfg = D2Config(**cfg)
                except ValidationError as e:
                    error(e)
                    continue

                result, svg, ok = self.renderer(diagram, cfg.opts(), alt=alt)
                if not ok:
                    error(result)
                    continue

                elem.tag = "div"
                elem.clear()
                elem.set("class", "d2")

                if not cfg.has_dark_theme():
                    elem.append(svg.root)
                    continue

                dark_result, dark_svg, ok = self.renderer(
                    diagram, cfg.opts(dark=True), alt=alt
                )
                if not ok:
                    error(dark_result)
                    continue

                light = etree.Element("div", {"class": "d2-light"})
                light.append(svg.root)
                elem.append(light)

                dark = etree.Element("div", {"class": "d2-dark"})
                dark.append(dark_svg.root)
                elem.append(dark)


class D2ImgExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            "base_dir": ["", "base directory for diagrams"],
            "config": [dict(), "global configuration"],
            "renderer": [Renderer, "render function"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown):
        md.registerExtension(self)
        cfg = self.getConfigs()
        md.treeprocessors.register(
            D2ImgTreeprocessor(md, cfg["base_dir"], cfg["config"], cfg["renderer"]),
            "d2_img",
            7,
        )
