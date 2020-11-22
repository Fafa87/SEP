import imageio
import numpy as np
import pathlib
import typing as t

from sep.loaders.files import FilesLoader


class ImagesLoader(FilesLoader):
    """
    Look through entire file structure in the data_root path and collect all the images.
    It loads input and annotations as np.ndarray.
    """

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
