import xml.etree.ElementTree as etree
from io import StringIO
from pathlib import Path
from typing import Any, Dict

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

    def run(self, root: etree.Element) -> etree.Element | None:
        for elem in root.iter("img"):
            src = Path(elem.get("src", ""))
            if src.suffix == ".d2":
                diagram = Path(self.base_dir, src).resolve()
                if not diagram.exists():
                    error(f"File not found: {diagram}")
                    continue
                with diagram.open("rb") as f:
                    source = f.read()

                if source.strip() == b"":
                    warning(f"{src}: empty diagram file")
                    continue

                cfg = self.config.copy()
                cfg.update(elem.attrib)
                cfg.pop("src")
                cfg.pop("alt")

                try:
                    cfg = D2Config(**cfg)
                except ValidationError as e:
                    error(e)
                    continue

                result, ok = self.renderer(source, cfg.opts())
                if not ok:
                    error(result)
                    continue

                svg = etree.iterparse(StringIO(result))
                for _, el in svg:
                    # strip namespace
                    _, _, el.tag = el.tag.rpartition("}")
                elem.tag = "div"
                elem.clear()
                elem.append(svg.root)


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
