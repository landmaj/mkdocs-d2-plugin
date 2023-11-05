import subprocess
import xml.etree.ElementTree as etree
from io import StringIO
from pathlib import Path
from typing import Any, Dict

from markdown import Extension, Markdown
from markdown.treeprocessors import Treeprocessor
from pydantic import ValidationError

from d2 import error, warning
from d2.config import D2Config, PluginConfig


class D2ImgTreeprocessor(Treeprocessor):
    def __init__(self, md: Markdown, cfg: Dict[str, Any]):
        self.base_dir = cfg["base_dir"]
        self.global_config = cfg["plugin_config"]
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

                cfg = self.global_config.d2_config()
                cfg.update(elem.attrib)
                cfg.pop("src")
                cfg.pop("alt")

                try:
                    cfg = D2Config(**cfg)
                except ValidationError as e:
                    error(e)
                    continue

                try:
                    result = subprocess.run(
                        [
                            self.global_config.executable,
                            "-",
                            "-",
                        ],
                        env=cfg.env(),
                        input=source,
                        capture_output=True,
                    )
                except FileNotFoundError:
                    error("Failed to find d2 executable. Is it installed?")
                    continue
                except Exception as e:
                    error(e)
                    continue

                stdout = result.stdout.decode().strip()

                if result.returncode != 0:
                    error(stdout)
                    continue

                svg = etree.iterparse(StringIO(stdout))
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
            "plugin_config": [PluginConfig(), "global configuration"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown):
        md.registerExtension(self)
        md.treeprocessors.register(
            D2ImgTreeprocessor(md, self.getConfigs()), "d2_img", 7
        )
