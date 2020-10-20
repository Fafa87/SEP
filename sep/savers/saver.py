from abc import ABC, abstractmethod

import numpy as np

import sep.loaders.loader


class Saver(ABC):
    def __init__(self):
        self.annotator = None
        pass

    def close(self):
        pass

    @abstractmethod
    def set_output(self, output_root, loader: sep.loaders.loader.Loader):
        pass

    @abstractmethod
    def save_result(self, name_or_num, result):
        pass

    @abstractmethod
    def save_tag(self, name_or_num, input_tag, result_tag):
        pass
