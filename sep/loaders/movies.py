import os
import traceback

import pathlib
import typing as t
import numpy as np

from sep._commons.movies import StreamReader
from sep._commons.utils import *
from sep.loaders.files import FilesLoader
from sep.loaders.loader import Loader


class MoviesLoader(Loader):
    """
    This one loads frames from the movies files and tags them so that they can be reorganizes into the files
    after evaluation. It also provides timestamp so that real time solution can be tested as well.

    For this the number of the image is the number in generated set of frames.
    The name is for example dragoons_00013.mp4 (frame 13 of the movie clip dragoons).

    This can be fairly slow if you have random access to images.

    Beware it is blocking related videos until it is closed.
    """

    def __init__(self, data_root, framerate, clips_len, clips_skip, input_extensions=None,
                 annotation_for_movie_finder: t.Callable[[pathlib.Path], str] = None, verbose=0):
        super().__init__()
        input_extensions = input_extensions or ['.mov', '.mp4', '.mpg', '.avi']
        self.data_root = data_root
        self.files_loader = FilesLoader(data_root, input_extensions=input_extensions,
                                        annotation_extension='.mp4',
                                        annotation_for_image_finder=annotation_for_movie_finder,
                                        verbose=verbose)
        self.clips_skip = clips_skip
        self.clips_len = clips_len
        self.framerate = framerate
        self.video_image_reader: t.Optional[StreamReader] = None
        self.video_annotation_reader: t.Optional[StreamReader] = None

        self.input_paths = {}
        self.annotation_paths = {}
        self.json_tags = {}

        for movie_path in self.list_movies_paths():
            movie_id = self.files_loader.path_to_id(movie_path)
            annotation_path = self.files_loader.load_annotation(movie_id)
            movie_tag = self.files_loader.load_tag(movie_id)

            # Process input data movies.
            movie_frames = MoviesLoader.load_movie_images(movie_path, self.framerate,
                                                          clips_len=self.clips_len, clips_skip=self.clips_skip)
            for frame_id, tag in zip(movie_frames['images'], movie_frames['tags']):
                frame_path = f"{movie_path}{frame_id}"
                frame_id = f"{movie_id}{frame_id}"
                tag['id'] = frame_id
                update_with_suffix(tag, movie_tag, prefix="movie_")

                self.input_paths[frame_id] = frame_path
                self.json_tags[frame_id] = tag

            # Process annotation movies.
            if annotation_path:
                annotation_frames = MoviesLoader.load_movie_images(annotation_path, self.framerate,
                                                                   clips_len=self.clips_len, clips_skip=self.clips_skip)
                for annotation_id in annotation_frames['images']:
                    annotation_path = f"{movie_path}{annotation_id}"
                    annotation_id = f"{movie_id}{annotation_id}"
                    self.annotation_paths[annotation_id] = annotation_path

        self.input_order = sorted(self.input_paths.keys())

    def list_movies(self):
        return self.files_loader.list_images()

    def list_movies_paths(self):
        return self.files_loader.list_images_paths()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        if self.video_image_reader:
            self.video_image_reader.close()
            self.video_image_reader = None
        if self.video_annotation_reader:
            self.video_annotation_reader.close()
            self.video_annotation_reader = None

    @staticmethod
    def load_movie_images(movie_path, framerate: t.Optional[float], clips_len, clips_skip) -> dict:
        images = []
        tags = []
        with StreamReader(movie_path) as video_reader:
            framerate = framerate or video_reader.frame_rate
            samples = list(video_reader.pos_samples(framerate))
            clip_nr = 0
            while samples:
                clip = samples[:clips_len]
                del samples[:clips_len + clips_skip]

                images += [f"_{c:05}" for c in clip]
                for i_c, c in enumerate(clip):
                    tag = {"id": f"_{c:05}", "pos": c, "pos_clip": i_c, "clip_nr": clip_nr,
                           "timestamp": c * video_reader.frame_interval}
                    tags.append(tag)

                clip_nr += 1
        return {'images': images, 'tags': tags}

    def list_images_paths(self):
        return [self.input_paths[p] for p in self.input_order]

    def list_images(self):
        return list(self.input_order)

    def path_to_id(self, path):
        return path.stem  # TODO this may not be unique

    def __get_frame_path(self, path_set, name_or_num):
        if isinstance(name_or_num, int):
            name_or_num = self.input_order[name_or_num]
        if isinstance(name_or_num, str):
            return path_set.get(name_or_num, None)
        else:
            raise NotImplemented(type(name_or_num))

    @staticmethod
    def prepare_reader(video_reader, path_to_movie):
        if video_reader is not None and video_reader.input_string != path_to_movie:
            video_reader.close()
            video_reader = None
        if video_reader is None:
            video_reader = StreamReader(path_to_movie)
            video_reader.__enter__()
        return video_reader

    def load_image(self, name_or_num) -> np.ndarray:
        path_to_frame = self.__get_frame_path(self.input_paths, name_or_num)
        if path_to_frame is None:
            raise Exception(f"{name_or_num} does not exist in the loader.")
        path_to_movie, frame_nr = path_to_frame.rsplit("_", maxsplit=1)
        self.video_image_reader = MoviesLoader.prepare_reader(self.video_image_reader, path_to_movie)
        return self.video_image_reader[int(frame_nr)]

    def load_tag(self, name_or_num):
        if isinstance(name_or_num, int):
            name_or_num = self.input_order[name_or_num]
        return self.json_tags.get(name_or_num, None)

    def load_annotation(self, name_or_num) -> t.Optional[pathlib.Path]:
        path_to_frame = self.__get_frame_path(self.annotation_paths, name_or_num)
        if path_to_frame is None:
            return None
        # TODO read from reader
        path_to_movie, frame_nr = path_to_frame.rsplit("_", maxsplit=1)

        return None

    def get_relative_path(self, name_or_num):
        if isinstance(name_or_num, int):
            name_or_num = self.input_order[name_or_num]
        movie_id = self.load_tag(name_or_num)['movie_id']
        # TODO in perfect world it would do entire hierarchy up to the movie id
        return os.path.join(movie_id, name_or_num)

    def __str__(self):
        return f"MovieLoader for: {self.data_root}"
