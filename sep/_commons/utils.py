import json
import os


def update_with_suffix(to_update: dict, new_items: dict, prefix: str = '', suffix: str = '') -> dict:
    new_items = {prefix + k + suffix: v for k, v in new_items.items()}
    to_update.update(new_items)
    return to_update


def get_with_prefix(dict_with_prefix: dict, prefix: str = '', strip_prefix=True) -> dict:
    return {k[len(prefix):] if strip_prefix else k: v for k, v in dict_with_prefix.items() if k.startswith(prefix)}


def union(*data: dict):
    return {k: v for d in data for k, v in d.items()}


def save_json(path, *data: dict):
    os.makedirs(os.path.dirname(str(path)), exist_ok=True)
    with open(str(path), 'w') as f:
        json.dump(union(*data), f, indent=4, sort_keys=True)


def assert_arg(arg_assert, arg_name):
    if not arg_assert:
        raise ValueError("Invalid parameter: " + arg_name)


def assert_value(value, description):
    if not value:
        raise ValueError(description)