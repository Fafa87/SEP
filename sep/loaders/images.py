import imageio
import pathlib
import typing as t

import numpy as np

from sep.loaders.files import FilesLoader


class ImagesLoader(FilesLoader):
    """
    Look through entire file structure in the data_root path and collect all the images.
    It loads input and annotations as np.ndarray.
    """

    def __init__(self, data_root, image_extensions=None, annotation_suffix="_gt",
                 annotation_extension=".png", annotation_for_image_finder: t.Callable[[pathlib.Path], str] = None,
                 verbose=0):
        """
        Initialize loader that uses pairs of files as samples.
        First it finds the input images:
        - those in data_root
        - with image_extensions
        - not ending in annotation_suffix

        Then for each input image it looks for the corresponding annotation and tags file.
        By default it looks in the same folder as image:
        - data_001.png - data_001_gt.png - data_001.json

        But this can be customized by providing a annotation_for_image_finder function.
        Args:
            data_root: root folder where the files can be found, if using
            image_extensions: extensions of the input image file (default: [".tif", ".png", ".jpg"])
            annotation_suffix: suffix of the annotation files, if None it is not used in filtering
            annotation_extension: extension of the annotation files, used only when annotation_for_image_finder is None
            annotation_for_image_finder: custom function that determines path of the corresponding annotation,
                overrides annotation_extension
        """
        super().__init__(data_root, image_extensions, annotation_suffix,
                         annotation_extension, annotation_for_image_finder,
                         verbose)

    def load_image(self, name_or_num) -> np.ndarray:
        path_to_file = super().load_image(name_or_num)
        return imageio.imread(path_to_file)

    def load_annotation(self, name_or_num) -> t.Optional[np.ndarray]:
        path_to_file = super().load_annotation(name_or_num)
        if path_to_file is None:
            return None
        annotation_data = imageio.imread(path_to_file)
        self.validate_annotation(annotation_data)
        return annotation_data

    def __str__(self):
        return f"ImageLoader for: {self.data_root}"
