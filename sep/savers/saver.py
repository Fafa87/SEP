from abc import ABC, abstractmethod

import numpy as np


class Saver(ABC):
    def __init__(self):
        self.annotator = None
        pass

    @abstractmethod
    def save_result(self, name_or_num, result):
        pass

    @abstractmethod
    def save_tag(self, name_or_num, result_tag):
        pass
