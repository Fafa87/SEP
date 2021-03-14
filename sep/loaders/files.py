from glob import glob

import itertools
import numbers
import typing as t

from sep._commons.utils import *
from sep.loaders.loader import Loader


class FilesLoader(Loader):
    """
    Look through entire file structure in the data_root path and collect all the images.
    """

    def __init__(self, data_root, verbose=0):
        super().__init__()
        self.verbose = verbose
        self.data_root = data_root
        self.input_paths = {}
        self.annotation_paths = {}
        self.json_tags = {}
        self.input_order = []
        self.extended_ids = False
        self.annotation_for_image_finder = None

    @classmethod
    def from_tree(cls, data_root, input_extensions=None,
                  annotation_suffix="_gt", annotation_extension=".png",
                  annotation_checker: t.Callable[[pathlib.Path], bool] = None,
                  annotation_for_image_finder: t.Callable[[pathlib.Path], str] = None,
                  verbose=0):
        """
        Initialize loader that uses pairs of files as samples.
        First it finds the input images:
        - those in data_root
        - with input_extensions
        - not ending in annotation_suffix

        Then for each input image it looks for the corresponding annotation and tags file.
        By default it looks in the same folder as image:
        - data_001.png - data_001_gt.png - data_001.json

        But this can be customized by providing a annotation_for_image_finder function.
        Args:
            data_root: root folder where the files can be found, if using
            input_extensions: extensions of the input image file (default: [".tif", ".png", ".jpg"])
            annotation_suffix: suffix of the annotation files, if None it is not used in filtering
            annotation_extension: extension of the annotation files, used only when annotation_for_image_finder is None
            annotation_checker: custom function that determines if the given path represents annotations
                if not None then it overrides check based on annotation_suffix
            annotation_for_image_finder: custom function that determines path of the corresponding annotation,
                overrides annotation_extension
            verbose: if non-zero additional summaries are printed
        """
        self = cls(data_root, verbose=verbose)
        self.preserve_order = False
        self.input_extensions = input_extensions or [".tif", ".png", ".jpg"]
        self.annotation_checker = annotation_checker
        if self.annotation_checker is None:
            self.annotation_checker = lambda p: annotation_suffix is not None and p.stem.endswith(annotation_suffix)

        self.annotation_for_image_finder = annotation_for_image_finder
        if self.annotation_for_image_finder is None:
            assert_arg(annotation_extension is not None,
                       "annotation_extension has to be not None if annotation_for_image_finder is None.")
            self.annotation_for_image_finder = lambda p: p.with_name(p.stem + annotation_suffix + annotation_extension)

        all_files = [pathlib.Path(p) for p in sorted(glob(os.path.join(data_root, "**", "*.*"), recursive=True))]

        input_images_paths = [f for f in all_files
                              if f.suffix.lower() in self.input_extensions and not self.annotation_checker(f)]
        annotation_paths = []
        json_tags = []
        for input_path in input_images_paths:
            annotation_paths.append(self.annotation_for_image_finder(input_path))
            json_path = self.suggest_json_path(input_path)
            json_tags.append(json_path)

        self.set_files(input_rel_paths=input_images_paths, annotation_rel_paths=annotation_paths, tag_rel_paths=json_tags)
        return self

    @classmethod
    def from_listing(cls, data_root, filepath, verbose=0, validate_list=False, preserve_order=True):
        """
        Initialize loader that uses pairs of files as samples.
        It uses provided listing file to find those files starting from data_root.

        Args:
            data_root: root folder where the files can be found, if using
            filepath: path to the listing file.
                The listing file consists of lines per each sample:
                    - path to image file
                    - optional path to annotation file
                    - optional path to tag file
                Example: "humans/human_1.tif, humans/human_1_gt.png, humans/human_1.json"
            verbose: if non-zero additional summaries are printed
            validate_list: if True then each of the files in the listing has to exist. Otherwise only input image is checked
            preserve_order: if True then original listing order will be preserved
        """
        self = cls(data_root, verbose=verbose)
        self.listing_filepath = filepath
        self.preserve_order = preserve_order

        with open(filepath, "r") as listing_file:
            samples = [l.strip() for l in listing_file.readlines() if l.strip()]

        input_rel_paths = []
        annotation_rel_paths = []
        tag_rel_paths = []
        for line_sample in samples:
            sample = [t.strip() for t in line_sample.split(",")]
            # make sure that it handles windows slashes on unix
            input_rel_paths.append(ensure_posix_path_str(sample[0]))
            annotation_rel_paths.append(ensure_posix_path_str(None if len(sample) <= 1 else sample[1]))
            tag_rel_paths.append(ensure_posix_path_str(None if len(sample) <= 2 else sample[2]))

        self.set_files(input_rel_paths=input_rel_paths, annotation_rel_paths=annotation_rel_paths, tag_rel_paths=tag_rel_paths,
                       validate_list=validate_list)
        return self

    def set_files(self, *, input_rel_paths, annotation_rel_paths, tag_rel_paths, validate_list=False):
        assert_arg(None not in input_rel_paths, "input_paths has None values")
        assert_arg(len(input_rel_paths) == len(annotation_rel_paths) == len(tag_rel_paths),
                   "All three list should have the same length.")
        self.input_paths = {}
        self.annotation_paths = {}
        self.json_tags = {}

        for input_path, annotation_path, tag_path in itertools.zip_longest(input_rel_paths, annotation_rel_paths, tag_rel_paths):
            input_path = self.data_root / pathlib.Path(input_path)
            sample_id = self.path_to_id(input_path)
            # check for duplicates
            if sample_id in self.input_paths:
                if not self.extended_ids:  # if there is still chance to use extended and get unique ids
                    self.extended_ids = True
                    print("The filenames are colliding. Trying again with extended ids option.")
                    self.set_files(input_rel_paths=input_rel_paths, annotation_rel_paths=annotation_rel_paths,
                                   tag_rel_paths=tag_rel_paths, validate_list=validate_list)
                    return
                else:
                    raise Exception("Failed to determine unique extended ids for each of the files.")

            self.input_paths[sample_id] = input_path
            assert_value(not validate_list or os.path.isfile(input_path), f"Specified image does not exist: f{input_path}")

            if annotation_path is not None:
                annotation_path = self.data_root / pathlib.Path(annotation_path)
                if os.path.isfile(annotation_path):
                    self.annotation_paths[sample_id] = annotation_path
                else:
                    assert_value(not validate_list, f"Specified annotation file does not exist {annotation_path}.")

            if tag_path is not None:
                tag_path = self.data_root / pathlib.Path(tag_path)
                if os.path.isfile(tag_path):
                    self.json_tags[sample_id] = tag_path
                else:
                    assert_value(not validate_list, f"Specified tag file does not exist {tag_path}.")
            # TODO this should save those missing paths so that it can be filled out in Annotator or Tagger

        self.input_order = list(self.input_paths.keys()) if self.preserve_order else sorted(self.input_paths.keys())
        if self.verbose:
            self.show_summary()

    def suggest_json_path(self, input_path):
        # Assume standard json path next to the input file.
        return pathlib.Path(input_path).with_suffix(".json")

    def show_summary(self):
        print(self)
        print(f"Found {len(self.input_paths)} images.")
        print(f"Found {len(self.annotation_paths)} annotations.")
        print(f"Found {len(self.json_tags)} tags.")

    def filter_files(self, names_or_nums):
        new_input_order = []
        for name_or_num in names_or_nums:
            name = self.get_name(name_or_num)
            new_input_order.append(name)
            input_path = self.input_paths.get(name, None)
            assert_arg(input_path is not None, f"{name} does not exist in FileLoader.")
        self.input_order = new_input_order
        self.input_paths = subset(self.input_paths, new_input_order)
        self.annotation_paths = subset(self.annotation_paths, new_input_order)
        self.json_tags = subset(self.json_tags, new_input_order)

    def get_relative_paths(self, name_or_num):
        input_rel_path = self.__get_file_path(self.input_paths, name_or_num, relative=True)
        json_rel_path = self.__get_file_path(self.json_tags, name_or_num, relative=True)
        annotation_rel_path = self.__get_file_path(self.annotation_paths, name_or_num, relative=True)
        return {"image": input_rel_path,
                "tag": json_rel_path,
                "annotation": annotation_rel_path}

    def save(self, listing_path, add_tag_path=True):
        data_lines = []
        for name_or_num in self.list_images():
            paths = self.get_relative_paths(name_or_num)
            line = [paths['image'], paths['annotation']]
            if add_tag_path:
                line.append(paths['tag'])
            line = [p or "" for p in line]
            data_lines.append(", ".join(line) + "\n")

        with open(listing_path, "w") as listing_file:
            listing_file.writelines(data_lines)

    def get_name(self, name_or_num):
        return self.input_order[name_or_num] if isinstance(name_or_num, numbers.Integral) else name_or_num

    def path_to_id(self, path: pathlib.Path):
        # TODO this still may not be unique, we may use ids from tags instead
        if self.extended_ids:
            return path.parent.name + "/" + path.stem
        return path.stem

    def list_images(self):
        return list(self.input_order)

    def list_images_paths(self):
        return [self.input_paths[p] for p in self.input_order]

    def __get_file_path(self, path_set, name_or_num, relative=False):
        name = self.get_name(name_or_num)
        if isinstance(name, str):
            file_path = path_set.get(name, None)
            if relative and file_path is not None:
                file_path = os.path.relpath(file_path, self.data_root)
            return file_path
        else:
            raise NotImplemented(type(name))

    def load_image(self, name_or_num) -> pathlib.Path:
        path_to_file = self.__get_file_path(self.input_paths, name_or_num)
        assert_value(path_to_file is not None, f"Image {name_or_num} does not exist in the loader.")
        return pathlib.Path(path_to_file)

    def save_tag(self, name_or_num, new_tag):
        assert "id" in new_tag

        name = self.get_name(name_or_num)
        path_to_file = self.__get_file_path(self.json_tags, name)
        if path_to_file is None:
            input_path = self.__get_file_path(self.input_paths, name)
            path_to_file = self.suggest_json_path(input_path)
            self.json_tags[name] = path_to_file

        save_json(self.json_tags[name], new_tag)

    def load_tag(self, name_or_num):
        path_to_file = self.__get_file_path(self.json_tags, name_or_num)
        if path_to_file is None:
            return {"id": name_or_num}
        else:
            tag = load_json(path_to_file)
            assert "id" in tag
            return tag

    def get_relative_path(self, name_or_num):
        return self.__get_file_path(self.input_paths, name_or_num, relative=True)

    def load_annotation(self, name_or_num) -> t.Optional[pathlib.Path]:
        path_to_file = self.__get_file_path(self.annotation_paths, name_or_num)
        if path_to_file is None:
            return None
        return pathlib.Path(path_to_file)

    def __str__(self):
        return f"FileLoader for: {self.data_root}"
