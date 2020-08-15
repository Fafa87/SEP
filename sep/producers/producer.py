import json
import pathlib
from abc import ABC, abstractmethod
from timeit import default_timer as timer

import imageio
import numpy as np


class Producer(ABC):
    """
    This is responsible for creating segmentation that will be later evaluated.
    It should be able to cache the results and add processing related tags.
    """

    def __init__(self, name, cache_root):
        # TODO add memory cache (lru based) and make cache root optional or replace it with some storage object
        self.cache_root = pathlib.Path(cache_root)
        self.name = name

    def load_segment(self, id):
        cache_path = (self.cache_root / str(id)).with_suffix(".tif")
        return imageio.imread(str(cache_path))

    def load_tag(self, id):
        cache_path = (self.cache_root / str(id)).with_suffix(".json")
        with open(str(cache_path), 'r') as f:
            return json.load(f)

    def __save_segment(self, id, segm):
        cache_path = (self.cache_root / str(id)).with_suffix(".tif")
        imageio.imsave(str(cache_path), segm)

    def __save_tag(self, id, tag):
        cache_path = (self.cache_root / str(id)).with_suffix(".json")
        with open(str(cache_path), 'w') as f:
            json.dump(tag, f)

    @abstractmethod
    def segmentation(self, image: np.ndarray) -> np.ndarray:
        """
        Args:
            image: image in uint8 (0-255)
        """
        # TODO for now assumes it is binary or 0-1 numeric
        pass

    def calculate(self, input_image: np.ndarray, input_tag: dict) -> (np.ndarray, dict):
        # TODO is possible and requested load results and tags from cache
        assert input_tag is not None
        assert input_image.dtype == np.uint8

        start_time = timer()
        seg = self.segmentation(input_image).astype(np.uint8)
        seg_tag = {}
        prediction_time = timer() - start_time
        seg_tag['run_time'] = prediction_time
        seg_tag['run_fps'] = round(1.0 / prediction_time, 2)
        seg_tag['producer_name'] = self.name
        seg_tag['producer_details'] = self.__repr__()

        if self.cache_root and "id" in input_tag:
            self.__save_tag(input_tag["id"], seg_tag)
            self.__save_segment(input_tag["id"], seg)

        return seg, seg_tag

    def __repr__(self):
        return f"{self.__class__} ({self.__dict__})"


