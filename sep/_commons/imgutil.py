import numpy as np


def make_rgb(image: np.ndarray):
    assert image.ndim >= 2
    if image.dtype == np.bool or np.issubdtype(image.dtype, np.floating) and image.max() <= 1:
        image = (image * 255)\

    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    if image.ndim == 2:
        return np.stack([image, image, image], axis=-1)

    return image
