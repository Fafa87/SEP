class Region:
    """
    This class generate the transformations of the segmentation and ground truth so that they can be evaluated
    in the same manner as the entire image. E.g. this can be used to generate metrics on only edges of the ground
    truth mask.
    """

    def __init__(self, name="Entire image"):
        self.name = name

    def regionize(self, ground_truth, mask):
        return mask

    def __str__(self):
        return self.name


class EdgesRegion(Region):
    pass
