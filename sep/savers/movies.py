import traceback

import collections
import numpy as np
import os
import pathlib
import sys

import sep.loaders
import sep.loaders.images
from sep._commons.movies import VideoWriter
from sep._commons.utils import *
from sep.savers.saver import Saver


class MoviesSaver(Saver):
    """
    Save results to video files from MoviesLoader in the same hierarchy as the loader.
    It only supports sequential processing in the same order as required MoviesLoader.

    If you want lossless video file you need to use a lossless codecs (eg. FFMPEG FFV1, Huffman HFYU, Lagarith LAGS).
    """

    def __init__(self, output_root='.', loader: sep.loaders.MoviesLoader = None, movie_format=".mp4", encoding='mp4v',
                 verbose=0, ignore_dtype=False):
        super().__init__()
        self.encoding = encoding
        self.ignore_dtype = ignore_dtype
        self.movie_format = movie_format
        self.loader = loader
        self.verbose = verbose
        self.output_root = pathlib.Path(output_root)
        self.video_writer = None
        self.video_writer_order = collections.defaultdict(int)

    def set_output(self, output_root, loader: sep.loaders.MoviesLoader):
        self.loader = loader
        self.output_root = pathlib.Path(output_root)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.close()

    def close(self):
        if self.video_writer:
            self.video_writer.close()
            self.video_writer = None

    def prepare_writer(self, video_writer, path_to_movie):
        if video_writer is not None and video_writer.output_path != str(path_to_movie):
            self.video_writer_order[path_to_movie] = sys.maxsize
            video_writer.close()
            video_writer = None
        if video_writer is None:
            assert self.loader.video_image_reader is not None, \
                "The loader has not started loading data so it is not possible to use it to configure writer."
            video_writer = VideoWriter(path_to_movie, encoding=self.encoding,
                                       fps=self.loader.framerate, output_shape=self.loader.video_image_reader.shape)
            video_writer.__enter__()
        return video_writer

    def save_result(self, name_or_num, result: np.ndarray, ignore_dtype=None):
        assert self.loader, "Loader has to be provided."

        # save into the file that you should save
        ignore_dtype = self.ignore_dtype if ignore_dtype is None else ignore_dtype
        if ignore_dtype:
            assert result.dtype == np.uint8, \
                "Floats would have to be converted to uint8. If desired add override type param"

        # get movie and frame to add
        relative_frame_path = pathlib.Path(self.loader.get_relative_path(name_or_num))
        frame_id = relative_frame_path.stem
        movie_id, frame_nr = self.loader.split_frame_path(frame_id)
        output_movie_path = (self.output_root / movie_id).with_suffix(self.movie_format)

        if movie_id not in self.video_writer_order:
            self.video_writer_order[movie_id] = frame_nr
        else:
            assert self.video_writer_order[movie_id] <= frame_nr, "The images and movies has to be saved sequentially."
            self.video_writer_order[movie_id] = frame_nr

        os.makedirs(output_movie_path.parent, exist_ok=True)
        self.video_writer = self.prepare_writer(self.video_writer, output_movie_path)
        self.video_writer.add(result, True, True)

    def save_tag(self, name_or_num, input_tag, result_tag):
        assert self.loader, "Loader has to be provided."

        # save only movie level information
        relative_frame_path = pathlib.Path(self.loader.get_relative_path(name_or_num))
        frame_id = relative_frame_path.stem
        movie_id, frame_nr = self.loader.split_frame_path(frame_id)
        output_tag_path = (self.output_root / movie_id).with_suffix(".json")

        # TODO check if it is not chainging
        input_tag = get_with_prefix(input_tag, sep.loaders.MoviesLoader.MOVIE_TAG_PREFIX)
        save_json(output_tag_path, input_tag, result_tag)
