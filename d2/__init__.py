import subprocess
from functools import partial
from typing import Dict, Union

from mkdocs.plugins import log

NAME = "mkdocs-d2-plugin"

info = partial(log.info, f"{NAME}: %s")
warning = partial(log.warning, f"{NAME}: %s")
error = partial(log.error, f"{NAME}: %s")


def render(
    executable: str,
    source: bytes,
    env: Dict[str, str],
) -> Union[str, bool]:
    try:
        result = subprocess.run(
            [
                executable,
                "-",
                "-",
            ],
            env=env,
            input=source,
            capture_output=True,
        )
    except FileNotFoundError:
        return f"{executable} not found", False
    except Exception as e:
        return str(e), False

    stdout = result.stdout.decode().strip()
    if result.returncode != 0:
        return stdout, False
    return stdout, True
