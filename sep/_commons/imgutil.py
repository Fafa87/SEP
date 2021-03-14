import numpy as np

from sep._commons.utils import *


def get_2d_size(image: np.ndarray):
    assert 2 <= image.ndim <= 3
    if image.ndim == 3:  # assume it is multichannel with last dim as channels
        return image.shape[:-1]
    return image.shape


def mix_rgb(red: np.array, green: np.array, blue: np.array):
    shape = None
    if red is not None:
        assert_arg(red.ndim == 2, "red", "{} has to be 2d.")
        assert_value(shape is None or red.shape == shape, "Arrays have to have the same shape.")
        shape = red.shape
    if green is not None:
        assert_arg(green.ndim == 2, "green", "{} has to be 2d.")
        assert_value(shape is None or green.shape == shape, "Arrays have to have the same shape.")
        shape = green.shape
    if blue is not None:
        assert_arg(blue.ndim == 2, "blue", "{} has to be 2d.")
        assert_value(shape is None or blue.shape == shape, "Arrays have to have the same shape.")
        shape = blue.shape

    rgb = np.zeros(list(shape) + [3], dtype=np.uint8)
    for channel, array in enumerate([red, green, blue]):
        if array is not None:
            rgb[..., channel] = array
    return rgb


def make_rgb(image: np.ndarray):
    assert image.ndim >= 2
    if image.dtype == np.bool or np.issubdtype(image.dtype, np.floating) and image.max() <= 1:
        image = (image * 255)
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    if image.ndim == 2:
        return np.stack([image, image, image], axis=-1)

    return image


def make_2d(image: np.ndarray, strict_duplication=False):
    if image.ndim == 2:
        return image
    elif image.ndim == 3:
        if strict_duplication:
            assert_value(np.all(image.mean(axis=2) == image[...,0]), "image has channels with non-equal values")
        return image.mean(axis=2)
    else:
        raise ValueError(f"No way to handle more that 3d data ({image.ndim}).")
