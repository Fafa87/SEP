import json
import os
import pathlib
import typing as t
from glob import glob

import imageio

from sep.loaders.loader import Loader


class ImagesLoader(Loader):
    """
    Look through entire file structure in the data_root path and collect all the images.
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
        super().__init__()
        self.data_root = data_root
        self.image_extensions = image_extensions or [".tif", ".png", ".jpg"]
        self.annotation_for_image_finder = annotation_for_image_finder
        all_files = [pathlib.Path(p) for p in sorted(glob(os.path.join(data_root, "**", "*.*"), recursive=True))]

        input_images_paths = [f for f in all_files
                              if f.suffix in self.image_extensions and not f.stem.endswith(annotation_suffix)]

        self.input_images = {self.path_to_id(p): p for p in input_images_paths}
        self.input_order = sorted(self.input_images.keys())
        self.annotation_images = {}
        self.json_tags = {}
        for input_path in input_images_paths:
            if self.annotation_for_image_finder:
                annotation_path = self.annotation_for_image_finder(input_path)
            else:
                annotation_path = input_path.with_name(input_path.stem + annotation_suffix + annotation_extension)
            if os.path.isfile(annotation_path):
                self.annotation_images[self.path_to_id(input_path)] = annotation_path

            json_path = input_path.with_suffix(".json")
            if os.path.isfile(json_path):
                self.json_tags[self.path_to_id(input_path)] = json_path

        if verbose:
            print(f"Loaded {len(self.input_images)} images.")
            print(f"Loaded {len(self.annotation_images)} annotations.")
            print(f"Loaded {len(self.json_tags)} tags.")


    def path_to_id(self, path):
        return path.stem  # TODO this may not be unique

    def list_images(self):
        return list(self.input_order)

    def list_images_paths(self):
        return [self.input_images[p] for p in self.input_order]

    def __get_file_path(self, path_set, name_or_num):
        if isinstance(name_or_num, int):
            name_or_num = self.input_order[name_or_num]
        if isinstance(name_or_num, str):
            return path_set.get(name_or_num, None)
        else:
            raise NotImplemented(type(name_or_num))

    def load_image(self, name_or_num):
        path_to_file = self.__get_file_path(self.input_images, name_or_num)
        return imageio.imread(path_to_file)

    def load_tag(self, name_or_num):
        path_to_file = self.__get_file_path(self.json_tags, name_or_num)
        if path_to_file is None:
            return {"id": name_or_num}
        else:
            with open(str(path_to_file), 'r') as f:
                tag = json.load(f)
            assert "id" in tag
            return tag

    def load_annotation(self, name_or_num):
        path_to_file = self.__get_file_path(self.annotation_images, name_or_num)
        if path_to_file is None:
            return None
        annotation_data = imageio.imread(path_to_file)
        self.validate_annotation(annotation_data)
        return annotation_data

    def __str__(self):
        return f"ImageLoader for: {self.data_root}"
