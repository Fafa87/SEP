import imageio
import json
import numpy as np
import os
import pathlib

from sep._commons.utils import *
import sep.loaders.images
from sep.savers.saver import Saver


class ImagesSaver(Saver):
    """
    Save results for images from ImagesLoader in the same hierarchy as the loader.
    """

    def __init__(self, output_root='.', loader: sep.loaders.images.ImagesLoader = None, image_format=".png",
                 verbose=0, ignore_dtype=False):
        super().__init__()
        self.ignore_dtype = ignore_dtype
        self.image_format = image_format
        self.loader = loader
        self.verbose = verbose
        self.output_root = pathlib.Path(output_root)

    def set_output(self, output_root, loader: sep.loaders.images.ImagesLoader):
        self.loader = loader
        self.output_root = pathlib.Path(output_root)

    def save_result(self, name_or_num, result: np.ndarray, ignore_dtype=None):
        assert self.loader, "Loader has to be provided."
        ignore_dtype = self.ignore_dtype if ignore_dtype is None else ignore_dtype
        if ignore_dtype:
            assert result.dtype == np.uint8, \
                "Floats would have to be converted to uint8. If desired add override type param"

        relative_img_path = pathlib.Path(self.loader.get_relative_path(name_or_num))
        result_path = (self.output_root / relative_img_path).with_suffix(self.image_format)
        os.makedirs(result_path.parent, exist_ok=True)
        imageio.imwrite(result_path, result)

    def save_tag(self, name_or_num, input_tag, result_tag):
        assert self.loader, "Loader has to be provided."
        relative_img_path = self.loader.get_relative_path(name_or_num)
        tag_path = (self.output_root / relative_img_path).with_suffix(".json")
        os.makedirs(tag_path.parent, exist_ok=True)
        save_json(tag_path, input_tag, result_tag)
