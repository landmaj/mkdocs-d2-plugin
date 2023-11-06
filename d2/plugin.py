import dbm
import os
import shutil
import subprocess
from functools import partial
from hashlib import sha1
from pathlib import Path
from typing import Dict, MutableMapping, Tuple

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.plugins import BasePlugin
from mkdocs.utils.yaml import RelativeDirPlaceholder

from d2 import info
from d2.config import PluginConfig
from d2.fence import D2CustomFence


class Plugin(BasePlugin[PluginConfig]):
    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        cache = None
        if self.config.cache:
            if not os.path.isdir(self.config.cache_dir):
                os.makedirs(self.config.cache_dir)
            path = Path(self.config.cache_dir, "db").as_posix()
            backend = dbm.whichdb(path)
            info(f"Using cache at {path} ({backend})")
            cache = dbm.open(path, "c")

        if shutil.which(self.config.executable) is None:
            raise ConfigurationError(f"executable '{self.config.executable}' not found")

        renderer = partial(render, self.config.executable, cache)  # type: ignore

        markdown_extensions = config.setdefault("markdown_extensions", [])
        for ext in {"pymdownx.superfences", "attr_list", "d2_img"}:
            if ext not in markdown_extensions:
                markdown_extensions.append(ext)

        mdx_configs = config.setdefault("mdx_configs", {})

        superfences = mdx_configs.setdefault("pymdownx.superfences", {})
        custom_fences = superfences.setdefault("custom_fences", [])
        f = D2CustomFence(self.config.d2_config(), renderer)
        custom_fences.append(
            {
                "name": "d2",
                "class": "d2",
                "validator": f.validator,
                "format": f.formatter,
            }
        )

        mdx_configs["d2_img"] = {
            "base_dir": RelativeDirPlaceholder(config),
            "config": self.config.d2_config(),
            "renderer": renderer,
        }

        return config


def render(
    executable: str,
    cache: MutableMapping[bytes, bytes] | None,
    source: bytes,
    env: Dict[str, str],
) -> Tuple[str, bool]:
    key = ""
    if cache is not None:
        key = source.hex()
        for k, v in env.items():
            key = f"{key}.{k}={v}"
        key = sha1(key.encode()).digest()
        if key in cache:
            return cache[key].decode(), True

    try:
        result = subprocess.run(
            [
                executable,
                "-",
                "-",
            ],
            env={**os.environ, **env},
            input=source,
            capture_output=True,
        )
    except Exception as e:
        return str(e), False

    stdout = result.stdout.decode().strip()
    if result.returncode != 0:
        return stdout, False

    if key != "" and cache is not None:
        cache[key] = stdout.encode()
    return stdout, True
