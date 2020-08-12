from abc import abstractmethod, ABC


class Region(ABC):
    """
    This class generate the transformations of the segmentation and ground truth so that they can be evaluated
    in the same manner as the entire image. E.g. this can be used to generate metrics on only edges of the ground
    truth mask.
    """
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def regionize(self, ground_truth, mask):
        return mask

    def __str__(self):
        return self.name


class EntireRegion(Region):
    def __init__(self):
        super().__init__("Entire image")

    def regionize(self, ground_truth, mask):
        return mask

