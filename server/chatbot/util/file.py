from os import listdir, path
from typing import List


def get_subdirectories(dir: str) -> List[str]:
    """Get a list of subdirectories"""
    return list(
        filter(
            lambda f: path.isdir(path.join(dir, f))
            and not f.startswith("__")
            and not f.startswith("."),
            listdir(dir),
        )
    )
