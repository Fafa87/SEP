from abc import ABC, abstractmethod


class Loader(ABC):
    def __init__(self):
        self.annotator = None
        pass

    @abstractmethod
    def list_images(self):
        pass

    @abstractmethod
    def load_image(self, name_or_num):
        pass

    @abstractmethod
    def load_tag(self, name_or_num):
        pass

    @abstractmethod
    def load_annotation(self, name_or_num):
        pass

    def save_annotation(self, name_or_num, new_annotation, keep_history=False):
        pass

    def save_tag(self, name_or_num, new_tag):
        pass

    def __len__(self):
        return len(self.list_images())
