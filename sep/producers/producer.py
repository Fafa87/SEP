from abc import ABC


class Producer(ABC):
    """
    This is responsible for creating segmentation that will be later evaluated.
    It should be able to cache the results and add processing related tags.
    """
    def __init__(self, name, cache_root):
        self.cache_root = cache_root
        self.name = name

    def load_segment(self, id):
        pass

    def load_tag(self, id):
        pass

    def segmentation(self, image):
        pass

    def calculate(self, input_image, input_tag):
        pass

    def __str__(self):
        return self.name

