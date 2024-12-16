import dbm
import os
import re
import subprocess
import xml.etree.ElementTree as etree
from functools import partial
from hashlib import sha1
from importlib.resources import files as importlib_files
from io import StringIO
from pathlib import Path
from typing import List, MutableMapping, Optional, Tuple, Union
from uuid import uuid4

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.utils.yaml import RelativeDirPlaceholder
from packaging import version

from d2 import info, warning
from d2.config import PluginConfig
from d2.fence import D2CustomFence

REQUIRED_VERSION = version.parse("0.6.3")


class Plugin(BasePlugin[PluginConfig]):
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
        try:
            d2_version = version.parse(raw_version)
            if d2_version < REQUIRED_VERSION:
                warning(
                    f"required d2 version {REQUIRED_VERSION} not satisfied; found {d2_version}"
                )
        except version.InvalidVersion:
            warning(f"version format not recognized; found {raw_version}")

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

        config["extra_css"].append("assets/stylesheets/mkdocs_d2_plugin.css")

        return config

    def on_post_build(self, config: MkDocsConfig) -> None:
        if self.cache:
            self.cache.close()

    def on_files(self, files: Files, config):
        content = importlib_files("d2.css").joinpath("mkdocs_d2_plugin.css").read_text()
        file = File(
            "assets/stylesheets/mkdocs_d2_plugin.css",
            None,
            config["site_dir"],
            config["use_directory_urls"],
        )
        file.content_string = content

        files.append(file)


def render(
    executable: str,
    cache: Optional[MutableMapping[bytes, bytes]],
    source: Union[bytes, Path],
    opts: List[str],
    alt: str,
) -> Tuple[str, Optional[etree.ElementTree], bool]:
    is_file = isinstance(source, Path)

    key = ""
    stdout = None
    if cache is not None:
        if is_file:
            key = f"{source}_{source.stat().st_mtime}"
        else:
            key = source.hex()
        for opt in opts:
            key = f"{key}.{opt}"
        key = sha1(key.encode()).digest()
        if key in cache:
            stdout = cache[key].decode()

    if stdout is None:
        if is_file:
            args = [executable, *opts, source.as_posix(), "-"]
            source = source.read_bytes()
        else:
            args = [executable, *opts, "-", "-"]

        try:
            result = subprocess.run(
                args,
                input=source,
                capture_output=True,
            )
        except Exception as e:
            return str(e), None, False

        if result.returncode != 0:
            stderr = result.stderr.decode().strip()
            return stderr, None, False

        stdout = result.stdout.decode().strip()

        # D2 uses a hash of diagram structure as a class name used for styling.
        # This means rendering options do not affect the class name, resulting
        # in conflicts if the same diagram is embeded multiple times using
        # different themes.
        new_class = f"d2-{uuid4().hex}"
        stdout = re.sub(r"d2-\d+", new_class, stdout)

        if key != "" and cache is not None:
            cache[key] = stdout

    svg = etree.iterparse(StringIO(stdout))
    for _, elem in svg:
        # strip namespace
        _, _, elem.tag = elem.tag.rpartition("}")

    svg.root.set("role", "img")
    svg.root.set("aria-label", alt)

    return etree.tostring(svg.root, encoding="unicode"), svg, True
