
class Metricer:
    """
    This is class responsible for generating a set of metrics for various image regions.
    """
    def __init__(self):
        self.metrics = []
        self.regions = []


class Region:
    """
    This class generate the transformations of the segmentation and ground truth so that they can be evaluated
    in the same manner as the entire image. E.g. this can be used to generate metrics on only edges of the ground
    truth mask.
    """
    pass


class Metric:
    """
    This represents a single metric that is calculate for a given pair of labels.
    """
    pass