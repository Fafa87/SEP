def update_with_suffix(to_update: dict, new_items: dict, prefix: str = '', suffix: str = '') -> dict:
    new_items = {prefix + k + suffix: v for k, v in new_items.items()}
    to_update.update(new_items)
    return to_update
