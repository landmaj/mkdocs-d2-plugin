import dbm
import os
import re
import subprocess
from functools import partial
from hashlib import sha1
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from typing import List, MutableMapping, Optional, Tuple
from uuid import uuid4

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import ConfigurationError
from mkdocs.plugins import BasePlugin, event_priority
from mkdocs.structure.files import Files, InclusionLevel
from mkdocs.utils.yaml import RelativeDirPlaceholder
from packaging import version

from d2 import debug
from d2.config import PluginConfig
from d2.fence import D2CustomFence

REQUIRED_VERSION = version.parse("0.6.3")
IMG_REGEX = r'(?P<alt>!\[[^\]]*\])\((?P<filename>.*?\.d2)(?="|\))\)'


class Plugin(BasePlugin[PluginConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp_dir = mkdtemp()

    def on_config(self, config: MkDocsConfig) -> Optional[MkDocsConfig]:
        self.cache = None
        if self.config.cache:
            if not os.path.isdir(self.config.cache_dir):
                os.makedirs(self.config.cache_dir)
            path = Path(self.config.cache_dir, "db").as_posix()
            backend = dbm.whichdb(path)
            debug(f"Using cache at {path} ({backend})")
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
        f = D2CustomFence(self.config.d2_config(), renderer, self.config.raise_on_error)
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
            "raise_on_error": self.config.raise_on_error,
        }

        return config

    @event_priority(50)
    def on_files(self, files: Files, *, config: MkDocsConfig):
        if self.config.remove_sources:
            self._exclude_source_files(files)

        if self.config.rewrite_paths:
            self._rewrite_source_paths(files)

    def on_post_build(self, config: MkDocsConfig) -> None:
        if self.cache:
            self.cache.close()

    def on_shutdown(self):
        rmtree(self.temp_dir)

    def _exclude_source_files(self, files: Files):
        for file in files.documentation_pages():
            if file.src_path.endswith(".d2"):
                file.inclusion = InclusionLevel.EXCLUDED

    # Hack for Material for MkDocs blog plugin. Rewrite all D2 paths
    # from relative to absolute as the relative paths would not work
    # after the blog plugin copies the files.
    def _rewrite_source_paths(self, files: Files):
        for file in files.documentation_pages():
            content = file.content_string

            for match in re.finditer(IMG_REGEX, file.content_string):
                alt = match.group("alt")
                original = Path(match.group("filename"))

                if original.is_absolute():
                    debug(f"Skipping absolute path: {original}")
                    continue

                rewritten = (Path(file.abs_src_path).parent / original).resolve()
                debug(f"Resolving {original} to {rewritten}")

                before_tag = content[: match.start()]
                after_tag = content[match.end() :]

                content = f"{before_tag}{alt}({rewritten}){after_tag}"

            with open(Path(self.temp_dir, uuid4().hex), "w") as f:
                f.write(content)
                file.abs_src_path = f.name


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
