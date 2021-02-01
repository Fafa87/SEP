import pathlib

from abc import ABC, abstractmethod
import typing as t

import numpy as np


class Loader(ABC):
    def __init__(self):
        self.annotator = None
        pass

    @abstractmethod
    def list_images(self):
        pass

    @abstractmethod
    def load_image(self, name_or_num) -> t.Union[np.ndarray, pathlib.Path]:
        pass

    @abstractmethod
    def load_tag(self, name_or_num):
        pass

    @abstractmethod
    def load_annotation(self, name_or_num) -> t.Union[np.ndarray, pathlib.Path]:
        pass

    @abstractmethod
    def get_relative_path(self, name_or_num):
        pass

    def save_annotation(self, name_or_num, new_annotation, keep_history=False):
        pass

    def save_tag(self, name_or_num, new_tag):
        pass

    def extend_tag(self, name_or_num, tag_extensions: dict):
        current_tags = self.load_tag(name_or_num)
        current_tags.update(tag_extensions)
        self.save_tag(name_or_num, current_tags)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, item):
        return {"image": self.load_image(item),
                "tag": self.load_tag(item),
                "annotation": self.load_annotation(item)}

    def __len__(self):
        return len(self.list_images())

    def validate_annotation(self, annotation: np.ndarray):
        # TMP require it to be a mask
        assert annotation.ndim == 2
