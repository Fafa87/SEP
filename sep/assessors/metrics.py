from abc import ABC, abstractmethod

import numpy as np


class Metric(ABC):
    """
    This represents a single metric that is calculate for a given pair of labels.
    """

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def calculate(self, segmentation, ground_truth):
        pass


class IouMetric(ABC):
    def __init__(self):
        super().__init__("iou")

    @abstractmethod
    def calculate(self, segmentation, ground_truth):
        if segmentation.max() > 1:
            segmentation = segmentation > 0
        if ground_truth.max() > 1:
            ground_truth = ground_truth > 0

        return np.sum(np.logical_and(segmentation, ground_truth)) / \
               np.sum(np.logical_or(segmentation, ground_truth)) + 0.0001
