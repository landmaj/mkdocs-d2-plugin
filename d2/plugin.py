import dbm
import os
import re
from shutil import rmtree
import subprocess
from functools import partial
from hashlib import sha1
from pathlib import Path
from tempfile import mkdtemp
from typing import List, MutableMapping, Optional, Tuple
from uuid import uuid4

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.plugins import BasePlugin, event_priority
from mkdocs.structure.files import Files, InclusionLevel
from mkdocs.utils.yaml import RelativeDirPlaceholder
from packaging import version

from d2 import info
from d2.config import PluginConfig
from d2.fence import D2CustomFence

REQUIRED_VERSION = version.parse("0.6.3")

IMG_REGEX = r'(?P<alt>!\[[^\]]*\])\((?P<filename>.*?\.d2)(?="|\))\)'


class Plugin(BasePlugin[PluginConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp_dir = mkdtemp()
    
    def on_shutdown(self):
        rmtree(self.temp_dir)

    # run before blog plugin which is -50
    @event_priority(0)
    def on_files(self, files: Files, *, config):
        # remove diagram sources from generated site
        for file in files.media_files():
            if file.name.endswith(".d2"):
                file.inclusion = InclusionLevel.EXCLUDED

        # replace relative diagram paths with absolute paths
        # as relative links are broken by blog plugin
        for file in files.documentation_pages():
            content = file.content_string

            for match in re.finditer(IMG_REGEX, file.content_string):
                alt = match.group("alt")
                src = match.group("filename")

                diagram = Path(file.abs_src_path).parent / src

                before_tag = content[: match.start()]
                after_tag = content[match.end() :]

                content = f"{before_tag}{alt}({diagram.resolve()}){after_tag}"

            with open(Path(self.temp_dir, uuid4().hex), "w") as f:
                f.write(content)
                file.abs_src_path = f.name

    def on_config(self, config: MkDocsConfig) -> Optional[MkDocsConfig]:
        self.cache = None
        if self.config.cache:
            if not os.path.isdir(self.config.cache_dir):
                os.makedirs(self.config.cache_dir)
            path = Path(self.config.cache_dir, "db").as_posix()
            backend = dbm.whichdb(path)
            info(f"Using cache at {path} ({backend})")
            cache = dbm.open(path, "c")
            self.cache = cache
            self.config["cache"] = cache

        try:
            result = subprocess.run(
                [self.config.executable, "--version"],
                capture_output=True,
            )
        except FileNotFoundError:
            raise ConfigurationError(f"executable '{self.config.executable}' not found")
        raw_version = result.stdout.decode().strip()
        raw_version = raw_version.split("-")[0]  # remove git commit info
        d2_version = version.parse(raw_version)
        if d2_version < REQUIRED_VERSION:
            raise ConfigurationError(
                f"required d2 version {REQUIRED_VERSION} not satisfied, found {d2_version}"
            )

        renderer = partial(render, self.config.executable, self.cache)  # type: ignore

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

    def on_post_build(self, config: MkDocsConfig) -> None:
        if self.cache:
            self.cache.close()


def render(
    executable: str,
    cache: Optional[MutableMapping[bytes, bytes]],
    source: bytes,
    opts: List[str],
) -> Tuple[str, bool]:
    key = ""
    if cache is not None:
        key = source.hex()
        for opt in opts:
            key = f"{key}.{opt}"
        key = sha1(key.encode()).digest()
        if key in cache:
            return cache[key].decode(), True

    try:
        result = subprocess.run(
            [executable, *opts, "-", "-"],
            input=source,
            capture_output=True,
        )
    except Exception as e:
        return str(e), False

    if result.returncode != 0:
        stderr = result.stderr.decode().strip()
        return stderr, False

    stdout = result.stdout.decode().strip()
    if key != "" and cache is not None:
        cache[key] = stdout.encode()
    return stdout, True
