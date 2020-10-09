import numpy as np


def make_rgb(image: np.ndarray):
    assert image.ndim >= 2
    if image.dtype == np.bool or (image.dtype == np.float and image.max() <= 1):
        image = (image * 255).astype(np.uint8)

    if image.ndim == 2:
        return np.stack([image, image, image], axis=-1)

    return image