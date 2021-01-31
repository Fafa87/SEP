import json
import pathlib
from abc import ABC, abstractmethod
from timeit import default_timer as timer

import imageio
import numpy as np

from sep._commons.utils import *
from sep.producers.producer import Producer


class ImagesProducer(Producer, ABC):
    """
    This is responsible for creating segmentation that will be later evaluated.
    It should be able to cache the results and add processing related tags.
    """
    def __init__(self, name, cache_root):
        # TODO add memory cache (lru based) and make cache root optional or replace it with some storage object
        super().__init__(name)
        self.cache_root = pathlib.Path(cache_root)

    def load_segment(self, id):
        cache_path = (self.cache_root / str(id)).with_suffix(".tif")
        return imageio.imread(str(cache_path))

    def load_tag(self, id):
        cache_path = (self.cache_root / str(id)).with_suffix(".json")
        return load_json(cache_path)

    def __save_segment(self, id, segm):
        cache_path = (self.cache_root / str(id)).with_suffix(".tif")
        imageio.imsave(str(cache_path), segm)

    def __save_tag(self, id, tag):
        cache_path = (self.cache_root / str(id)).with_suffix(".json")
        save_json(cache_path, tag)

    def calculate(self, input_image: np.ndarray, input_tag: dict) -> (np.ndarray, dict):
        # TODO is possible and requested load results and tags from cache
        assert input_tag is not None
        if input_image.dtype != np.uint8: # TODO we need to be sure
            input_image = (input_image * 255).astype(np.uint8)
        assert input_image.dtype == np.uint8

        seg, seg_tag = super().calculate(input_image, input_tag)
        # TODO what if the seg is not uint8? What if it is not mask? What if it is predictions as floats?
        if isinstance(seg, np.ndarray) and seg.dtype == np.bool:
            seg = seg.astype(np.uint8)

        if self.cache_root and "id" in input_tag:
            self.__save_tag(input_tag["id"], seg_tag)
            self.__save_segment(input_tag["id"], seg)

        return seg, seg_tag

    def __repr__(self):
        return f"{self.__class__} ({self.__dict__})"


