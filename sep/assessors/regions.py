from abc import abstractmethod, ABC

import numpy as np
import skimage.morphology


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
