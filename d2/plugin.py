from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin

from d2.config import PluginConfig
from d2.block import Renderer


class Plugin(BasePlugin[PluginConfig]):
    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        markdown_extensions = config.setdefault("markdown_extensions", [])
        if "pymdownx.superfences" not in markdown_extensions:
            markdown_extensions.append("pymdownx.superfences")
        if "d2_img" not in markdown_extensions:
            markdown_extensions.append("d2_img")

        mdx_configs = config.setdefault("mdx_configs", {})

        superfences = mdx_configs.setdefault("pymdownx.superfences", {})
        custom_fences = superfences.setdefault("custom_fences", [])
        f = Renderer(self.config)
        custom_fences.append(
            {
                "name": "d2",
                "class": "d2",
                "validator": f.validator,
                "format": f.formatter,
            }
        )

        mdx_configs["d2_img"] = {
            "base_dir": config.docs_dir,
            "plugin_config": self.config,
        }

        return config
