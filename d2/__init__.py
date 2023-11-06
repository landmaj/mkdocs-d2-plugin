from functools import partial
from typing import Callable, Dict, Tuple

from mkdocs.plugins import log

NAME = "mkdocs-d2-plugin"

info = partial(log.info, f"{NAME}: %s")
warning = partial(log.warning, f"{NAME}: %s")
error = partial(log.error, f"{NAME}: %s")

Renderer = Callable[[bytes, Dict[str, str]], Tuple[str, bool]]
