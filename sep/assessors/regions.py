import numpy as np
import skimage.morphology
from abc import abstractmethod, ABC

from sep._commons.utils import *


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

    def __invert__(self):
        return RegionExpr('~', self)

    def __and__(self, other):
        return RegionExpr('~', self, other)

    def __or__(self, other):
        return RegionExpr('|', self, other)

    def __str__(self):
        return self.name


class RegionExpr(Region):
    def __init__(self, operator, *regions, name=None):
        name = name or f"Expr[{operator}]({regions})"
        super().__init__(name)
        self.operator = operator
        self.regions = regions

    def regionize(self, ground_truth: np.ndarray, mask: np.ndarray) -> np.ndarray:
        if self.operator == '|':
            return self.regions[0].regionize(ground_truth, mask) | self.regions[1].regionize(ground_truth, mask)
        elif self.operator == '&':
            return self.regions[0].regionize(ground_truth, mask) & self.regions[1].regionize(ground_truth, mask)
        elif self.operator == '~':
            return ~self.regions[0].regionize(ground_truth, mask)
        else:
            assert_arg(False, self.operator)

    def extract_region(self, ground_truth: np.ndarray) -> np.ndarray:
        if self.operator == '|':
            return self.regions[0].extract_region(ground_truth) | self.regions[1].extract_region(ground_truth)
        elif self.operator == '&':
            return self.regions[0].extract_region(ground_truth) & self.regions[1].extract_region(ground_truth)
        elif self.operator == '~':
            return ~self.regions[0].extract_region(ground_truth)
        else:
            assert_arg(False, self.operator)


class EntireRegion(Region):
    def __init__(self):
        super().__init__("Entire image")

    def extract_region(self, ground_truth: np.ndarray) -> np.ndarray:
        return np.ones_like(ground_truth, dtype=np.bool)


class EdgesRegion(Region):
    def __init__(self, edge_size, name="Edges"):
        """
        Region consisting of the edge of the ground truth.
        Args:
            edge_size: if int it is pixel size, if float it is the fraction of the mean of image dimension
        """
        super().__init__(name)
        self.edge_size = edge_size

    def extract_region(self, ground_truth: np.ndarray) -> np.ndarray:
        if isinstance(self.edge_size, float):
            mean_size = (ground_truth.shape[0] + ground_truth.shape[1]) / 2
            selem = skimage.morphology.disk(mean_size * self.edge_size)
        else:
            selem = skimage.morphology.disk(self.edge_size)
        dilated = skimage.morphology.binary_dilation(ground_truth, selem)
        eroded = skimage.morphology.binary_erosion(ground_truth, selem)
        return dilated > eroded


class DetailsRegion(Region):
    def __init__(self, edge_size, name="Details"):
        """
        Region consisting of the small objects of the ground truth.
        Args:
            edge_size: if int it is pixel size, if float it is the fraction of the mean of image dimension
        """
        super().__init__(name)
        self.edge_size = edge_size

    def extract_region(self, ground_truth: np.ndarray) -> np.ndarray:
        if isinstance(self.edge_size, float):
            mean_size = (ground_truth.shape[0] + ground_truth.shape[1]) / 2
            selem = skimage.morphology.disk(mean_size * self.edge_size)
        else:
            selem = skimage.morphology.disk(self.edge_size)
        opened = skimage.morphology.binary_opening(ground_truth, selem)
        return (ground_truth > 0) > opened


set_standard = [
    EntireRegion(),
    RegionExpr('~', EdgesRegion(2), name="No edges pixels"),  # Edge pixels are disregarded.
    EdgesRegion(0.02, name="Mask precision"),  # Difference near the edge.
    RegionExpr('~', EdgesRegion(0.02), name="Mask robust"),  # Robustness.
    DetailsRegion(0.05, name="Mask details"),  # Details (hand, arms, hair).
]
