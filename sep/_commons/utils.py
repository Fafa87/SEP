import json
import os
import pathlib


def update_with_suffix(to_update: dict, new_items: dict, prefix: str = '', suffix: str = '') -> dict:
    new_items = {prefix + k + suffix: v for k, v in new_items.items()}
    to_update.update(new_items)
    return to_update


def get_with_prefix(dict_with_prefix: dict, prefix: str = '', strip_prefix=True) -> dict:
    return {k[len(prefix):] if strip_prefix else k: v for k, v in dict_with_prefix.items() if k.startswith(prefix)}


def union(*data: dict):
    return {k: v for d in data for k, v in d.items()}


def load_json(path_to_file):
    with open(str(path_to_file), 'r') as f:
        return json.load(f)


def save_json(path, *data: dict):
    os.makedirs(os.path.dirname(str(path)), exist_ok=True)
    with open(str(path), 'w') as f:
        json.dump(union(*data), f, indent=4, sort_keys=True)


def time_to_sec(time: str) -> int:
    time_tokens = [int(t) for t in time.split(":")]
    res = 0
    for v in time_tokens:
        res = res * 60 + v
    return res


def assert_arg(arg_assert, arg_name):
    if not arg_assert:
        raise ValueError("Invalid parameter: " + arg_name)


def assert_value(value, description):
    if not value:
        raise ValueError(description)


def ensure_posix_path_str(path: str) -> str:
    if path is None:
        return None
    return str(pathlib.Path(pathlib.PureWindowsPath(path).as_posix()))


class SepException(Exception):
    pass
