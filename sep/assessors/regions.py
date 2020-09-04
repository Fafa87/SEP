from abc import abstractmethod, ABC

import numpy as np


class Region(ABC):
    """
    This class generate the transformations of the segmentation and ground truth so that they can be evaluated
    in the same manner as the entire image. E.g. this can be used to generate metrics on only edges of the ground
    truth mask.
    """

    def __init__(self, name):
        self.name = name

    def regionize(self, ground_truth: np.ndarray, mask: np.ndarray) -> np.ndarray:
        # TODO rethink mask 0-1 vs 0-255 or it may not be a mask?
        relevant_area = self.extract_region(ground_truth)
        return mask.astype(np.bool) & relevant_area

    @abstractmethod
    def extract_region(self, ground_truth: np.ndarray) -> np.ndarray:
        pass

    def __str__(self):
        return self.name


class EntireRegion(Region):
    def __init__(self):
        super().__init__("Entire image")

    def extract_region(self, ground_truth: np.ndarray) -> np.ndarray:
        return np.ones_like(ground_truth, dtype=np.bool)
