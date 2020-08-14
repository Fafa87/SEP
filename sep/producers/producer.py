from abc import ABC

import numpy as np

class Producer(ABC):
    """
    This is responsible for creating segmentation that will be later evaluated.
    It should be able to cache the results and add processing related tags.
    """
    def __init__(self, name, cache_root):
        self.cache_root = cache_root
        self.name = name

    def load_segment(self, id):
        pass

    def load_tag(self, id):
        pass

    def segmentation(self, image: np.ndarray) -> np.ndarray:
        pass

    def calculate(self, input_image: np.ndarray, input_tag: dict):
        pass

    def __str__(self):
        return self.name

