from abc import ABC, abstractmethod

import numpy as np


class Metric(ABC):
    """
    This represents a single metric that is calculate for a given pair of labels.
    """

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def calculate(self, segmentation: np.ndarray, ground_truth: np.ndarray) -> float:
        pass

    def show(self, segmentation: np.ndarray, ground_truth: np.ndarray) -> float:
        metric_value = self.calculate(segmentation, ground_truth)
        print (f"{self}: {metric_value:.4f}")

    def __str__(self):
        return self.name


class IouMetric(Metric):
    def __init__(self):
        super().__init__("iou")

    def calculate(self, segmentation, ground_truth) -> float:
        if segmentation.max() > 1:
            segmentation = segmentation > 0
        if ground_truth.max() > 1:
            ground_truth = ground_truth > 0

        return np.sum(np.logical_and(segmentation, ground_truth)) / \
               np.sum(np.logical_or(segmentation, ground_truth)) + 0.00000001
