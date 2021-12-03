import sys

import pathlib


def add_root_to_path(steps_up):
    root_dir = pathlib.Path(__file__)
    for _ in range(steps_up):
        root_dir = root_dir.parent

    if root_dir not in sys.path:
        sys.path.append(str(root_dir))
    return root_dir
