from abc import abstractmethod, ABC
import typing as t

import numpy as np

import skimage.morphology
import skimage.transform

from sep._commons.utils import *


class Region(ABC):
    """
    This class generate the transformations of the segmentation and ground truth so that they can be evaluated
    in the same manner as the entire image. E.g. this can be used to generate metrics on only edges of the ground
    truth mask.
    """

    def __init__(self, name):
        self.name = name
        self.viable_thresh = 0.005

    def regionize(self, ground_truth: np.ndarray, mask: np.ndarray) -> np.ndarray:
        # TODO rethink mask 0-1 vs 0-255 or it may not be a mask?
        relevant_area = self.extract_region(ground_truth)
        return mask.astype(bool) & relevant_area

    @abstractmethod
    def extract_region(self, ground_truth: np.ndarray) -> np.ndarray:
        pass

    def area_fractions(self, ground_truth: np.ndarray) -> t.Tuple[float, float]:
        """
        Calculate the region coverage fraction.
        Returns:
        (fraction of the input image in regression, fraction of the ground truth in region against entire input_image)
        """
        region_array = self.extract_region(ground_truth)
        region_fractions = region_array.sum() / ground_truth.size
        annotation_in_region_fractions = ((region_array > 0) * (ground_truth > 0)).sum() / ground_truth.size
        return region_fractions, annotation_in_region_fractions

    def is_viable_for(self, ground_truth: np.ndarray) -> bool:
        reg_frac, _ = self.area_fractions(ground_truth)
        return reg_frac > self.viable_thresh

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
        return np.ones_like(ground_truth, dtype=bool)


class EdgesRegion(Region):
    def __init__(self, edge_size, name="Edges", downsample_x=None):
        """
        Region consisting of the edge of the ground truth.
        Args:
            edge_size: if int it is pixel size, if float it is the fraction of the mean of image dimension
        """
        super().__init__(name)
        self.edge_size = edge_size
        self.downsample_x = downsample_x

    def extract_region(self, ground_truth: np.ndarray) -> np.ndarray:
        if self.downsample_x:
            original_shape = ground_truth.shape
            scale = self.downsample_x / ground_truth.shape[1]
            ground_truth = skimage.transform.rescale(ground_truth, scale)

        if isinstance(self.edge_size, float):
            mean_size = (ground_truth.shape[0] + ground_truth.shape[1]) / 2
            selem = skimage.morphology.disk(mean_size * self.edge_size)
        else:
            selem = skimage.morphology.disk(self.edge_size)
        dilated = skimage.morphology.binary_dilation(ground_truth, selem)
        eroded = skimage.morphology.binary_erosion(ground_truth, selem)
        final_region = dilated > eroded
        if self.downsample_x:
            final_region = skimage.transform.resize(final_region, original_shape)
            # Ensure region is binary.
            final_region = final_region > 0.5
        return final_region


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
    EdgesRegion(0.02, name="Mask precision", downsample_x=640),  # Difference near the edge.
    RegionExpr('~', EdgesRegion(0.02, downsample_x=640), name="Mask robust"),  # Robustness.
    DetailsRegion(0.05, name="Mask details"),  # Details (hand, arms, hair).
]
