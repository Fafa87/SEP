import imageio
import numpy as np
import typing as t

import sep._commons.imgutil as imgutil
from sep.loaders.files import FilesLoader, SepException


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
        # TODO maybe let user know that it was 3d
        annotation_data = imgutil.make_2d(annotation_data)
        # TODO ensure that size matches to the load image - maybe checking on demand.
        self.validate_annotation(annotation_data)
        return annotation_data

    def save_annotation(self, name_or_num, new_annotation: np.ndarray, keep_history=False, new_annotation_path=None):
        assert not keep_history, "Keeping annotation changes history not yet implemented for ImagesLoader."
        # Check consistency with image.
        image = self.load_image(name_or_num)
        assert imgutil.get_2d_size(image) == imgutil.get_2d_size(new_annotation)
        self.validate_annotation(new_annotation)

        # Optionally update annotation path
        assert new_annotation_path is None, "Explicit new annotation path setting not yet implemented."

        # Save new annotation into the given path.
        path_to_file = super().load_annotation(name_or_num)
        if path_to_file is None:
            # Try to create new annotation file.
            input_path = super().load_image(name_or_num)
            if self.annotation_for_image_finder is None:
                raise SepCannotDetermineAnnotationPathError()

            name = self.get_name(name_or_num)
            annotation_path = self.annotation_for_image_finder(input_path)
            self.annotation_paths[name] = annotation_path
            assert super().load_annotation(name_or_num) == annotation_path
            path_to_file = annotation_path
        imageio.imwrite(str(path_to_file), new_annotation)

    def __str__(self):
        return f"ImageLoader for: {self.data_root}"


class SepCannotDetermineAnnotationPathError(SepException):
    def __init__(self, msg=None):
        if msg is None:
            msg = "There is no way to determine the annotation path:\n" \
                  "\t- set 'annotation_for_image_finder' function\n" \
                  "\t- use loader created from tree\n" \
                  "\t- specify it explicitely\n"
        super(SepCannotDetermineAnnotationPathError, self).__init__(msg)
