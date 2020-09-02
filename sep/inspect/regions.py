import typing as t

import numpy as np
import skimage
from skimage.color.colorlabel import DEFAULT_COLORS


def overlay_region(image: np.ndarray, region: np.ndarray):
    # TODO work not only on RGB image? # Check if it is a mask / label?
    overlay = skimage.color.label2rgb(region, image, colors=DEFAULT_COLORS, bg_label=0)
    return overlay


def overlay_regions(image: np.ndarray, regions: t.List[np.ndarray], regions_names: t.Optional[t.List[str]]):
    if regions_names is None:
        # use some dummy naming
        regions_names = [str(i) for i in range(1, len(regions) + 1)]
    assert len(regions) == len(regions_names)

    flatten_label = np.zeros(regions[0].shape, dtype=np.uint8)
    legend = []
    for label, (name, region) in enumerate(zip(regions_names, regions), start=1):
        flatten_label[region > 0] = label
        legend.append((name, DEFAULT_COLORS[label-1]))

    overlay = skimage.color.label2rgb(flatten_label, image, bg_label=0)

    return overlay, legend
