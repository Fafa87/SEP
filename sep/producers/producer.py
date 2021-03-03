from timeit import default_timer as timer

import numpy as np
import pathlib
import typing as t
from abc import ABC, abstractmethod


class Producer(ABC):
    """
    This is responsible for creating segmentation that will be later evaluated.
    """
    TAG_PREFIX = 'producer_'
    RUN_PREFIX = 'run_'

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def segmentation(self, input_data: t.Union[np.ndarray, pathlib.Path], input_tag: dict) \
            -> t.Union[np.ndarray, pathlib.Path]:
        """
        Args:
            input_data: path to input data or image in uint8 (0-255)
            input_tag: tags of the input data
        """
        pass

    def calculate(self, input_data: t.Union[np.ndarray, pathlib.Path], input_tag: dict) \
            -> (t.Union[np.ndarray, pathlib.Path], dict):
        start_time = timer()
        seg = self.segmentation(input_data, input_tag)

        seg_tag = {}
        prediction_time = timer() - start_time
        seg_tag[f'{Producer.RUN_PREFIX}time'] = prediction_time
        seg_tag[f'{Producer.RUN_PREFIX}fps'] = round(1.0 / prediction_time, 2)
        seg_tag[f'{Producer.TAG_PREFIX}name'] = self.name
        seg_tag[f'{Producer.TAG_PREFIX}details'] = self.__repr__()
        return seg, seg_tag

    def __repr__(self):
        return f"{self.__class__} ({self.__dict__})"

    def __str__(self):
        return f"{self.name}"
