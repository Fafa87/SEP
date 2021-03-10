import numbers
import traceback

import math
import numpy as np
import typing as t
from abc import ABC, abstractmethod

from sep._commons.movies import StreamReader
from sep._commons.utils import *
from sep.loaders.files import FilesLoader
from sep.loaders.loader import Loader


class FrameSelector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def select(self, samples_frames: t.List[int], framerate: float = None) -> t.Iterable[t.Tuple[t.List[int], int]]:
        """
        Select subset of the provided frame positions.
        Args:
            framerate: optional video framerate in frames per sec
            samples_frames: list of frame positions of the samples

        Returns:
            The set of clips where each clip is (subset list, clip_id).
        """
        pass


class FrameByGroupSelector(FrameSelector):
    def __init__(self, clips_len=99999999, clips_skip=0, skip_first=0, skip_last=0):
        super().__init__()
        self.skip_last = skip_last
        self.skip_first = skip_first
        self.clips_skip = clips_skip
        self.clips_len = clips_len

    def select(self, samples_frames: t.List[int], framerate: float = None) -> t.Iterable[t.Tuple[t.List[int], int]]:
        samples = list(samples_frames[self.skip_first:len(samples_frames) - self.skip_last])
        clip_nr = 0
        while samples:
            yield samples[:self.clips_len], clip_nr
            del samples[:self.clips_len + self.clips_skip]
            clip_nr += 1


class FrameByIntervalSelector(FrameSelector):
    def __init__(self, frames_to_extract: int, interval_start_time: float = 0, interval_end_time: float = 99999):
        super().__init__()
        self.interval_start = interval_start_time
        self.interval_end = interval_end_time
        self.frames_to_extract = frames_to_extract

    def select(self, samples_frames: t.List[int], framerate: float = 1) -> t.Iterable[t.Tuple[t.List[int], int]]:
        start_pos = math.floor(self.interval_start * framerate)
        end_pos = math.ceil(self.interval_end * framerate)
        inside_frames = [s for s in samples_frames if start_pos <= s <= end_pos]

        # Split it into frames_to_extract + 1 spaces.
        step_float = len(inside_frames) / (self.frames_to_extract + 1)
        current = step_float

        clip_nr = 0
        while current < len(inside_frames) and clip_nr < self.frames_to_extract:
            current_pos = int(current)
            yield [inside_frames[current_pos]], clip_nr
            clip_nr += 1
            current += step_float


class MoviesLoader(Loader):
    """
    This one loads frames from the movies files and tags them so that they can be reorganizes into the files
    after evaluation. It also provides timestamp so that real time solution can be tested as well.

    For this the number of the image is the number in generated set of frames.
    The name is for example dragoons_00013.mp4 (frame 13 of the movie clip dragoons).

    This can be fairly slow if you have random access to images.

    Beware it is blocking related videos until it is closed.
    """
    MOVIE_TAG_PREFIX = 'movie_'
    USER_TAG_PREFIX = 'user_'

    def __init__(self, data_root, framerate, clips_len=99999999, clips_skip=0, annotation_as_mask=False, verbose=0):
        super().__init__()
        self.annotation_as_mask = annotation_as_mask
        self.data_root = data_root
        self.verbose = verbose
        self.selector = FrameByGroupSelector(clips_len, clips_skip)
        self.framerate = framerate
        self.video_image_reader: t.Optional[StreamReader] = None
        self.video_annotation_reader: t.Optional[StreamReader] = None
        self.input_paths = {}
        self.annotation_paths = {}
        self.json_tags = {}
        self.files_loader = None

    @classmethod
    def from_tree(cls, data_root,
                  framerate, clips_len=99999999, clips_skip=0, annotation_as_mask=False, verbose=0,
                  input_extensions=None,
                  annotation_suffix='_gt', annotation_extension='.mp4',
                  annotation_for_movie_finder: t.Callable[[pathlib.Path], str] = None):
        self = cls(data_root=data_root, framerate=framerate, clips_len=clips_len, clips_skip=clips_skip,
                   annotation_as_mask=annotation_as_mask, verbose=verbose)
        input_extensions = input_extensions or ['.mov', '.mp4', '.mpg', '.avi']
        files_loader = FilesLoader.from_tree(data_root, input_extensions=input_extensions,
                                             annotation_extension=annotation_extension,
                                             annotation_suffix=annotation_suffix,
                                             annotation_for_image_finder=annotation_for_movie_finder,
                                             verbose=verbose)
        self.generate_frames(files_loader)
        return self

    @classmethod
    def from_listing(cls, data_root, filepath,
                     framerate, clips_len=99999999, clips_skip=0, annotation_as_mask=False, verbose=0,
                     validate_list=False):
        self = cls(data_root=data_root, framerate=framerate, clips_len=clips_len, clips_skip=clips_skip,
                   annotation_as_mask=annotation_as_mask, verbose=verbose)
        files_loader = FilesLoader.from_listing(data_root, filepath, verbose, validate_list)
        self.generate_frames(files_loader)
        return self

    def show_summary(self):
        print(self)
        print(f"Found {len(self.input_paths)} input frames.")
        print(f"Found {len(self.annotation_paths)} annotation frames.")
        print(f"Found {len(self.json_tags)} tags.")

    def generate_frames(self, files_loader: FilesLoader):
        self.input_paths = {}
        self.annotation_paths = {}
        self.json_tags = {}
        self.files_loader = files_loader

        for movie_path in self.list_movies_paths():
            movie_id = self.files_loader.path_to_id(movie_path)
            annotation_movie_path = self.files_loader.load_annotation(movie_id)
            movie_tag = self.files_loader.load_tag(movie_id)

            # Process input data movies.
            movie_frames = MoviesLoader.load_movie_images(movie_path, self.framerate, self.selector)
            for frame_id, tag in zip(movie_frames['images'], movie_frames['tags']):
                frame_path = f"{movie_path}{frame_id}"
                frame_id = f"{movie_id}{frame_id}"
                tag['id'] = frame_id
                update_with_suffix(tag, movie_tag, prefix=MoviesLoader.MOVIE_TAG_PREFIX)

                self.input_paths[frame_id] = frame_path
                self.json_tags[frame_id] = tag

            # Process annotation movies.
            if annotation_movie_path:
                annotation_frames = MoviesLoader.load_movie_images(annotation_movie_path, self.framerate, self.selector)
                for annotation_id in annotation_frames['images']:
                    annotation_path = f"{annotation_movie_path}{annotation_id}"
                    annotation_id = f"{movie_id}{annotation_id}"
                    self.annotation_paths[annotation_id] = annotation_path

            # TODO assert that there is no inconsistency in images vs annotations movies: #frames, #framerate

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
    def load_movie_images(movie_path, framerate: t.Optional[float], selector: FrameSelector) -> dict:
        images = []
        tags = []
        with StreamReader(movie_path) as video_reader:
            original_frame_rate = video_reader.frame_rate
            framerate = framerate or original_frame_rate
            samples = list(video_reader.pos_samples(framerate))

            for clip, clip_nr in selector.select(samples, original_frame_rate):
                images += [f"_{c:05}" for c in clip]
                for i_c, c in enumerate(clip):
                    tag = {"id": f"_{c:05}", "pos": c, "pos_clip": i_c, "clip_nr": clip_nr,
                           "timestamp": c * video_reader.frame_interval}
                    tags.append(tag)
        return {'images': images, 'tags': tags}

    def list_images_paths(self):
        return [self.input_paths[p] for p in self.input_order]

    def list_images(self):
        return list(self.input_order)

    def path_to_id(self, path):
        return path.stem  # TODO this may not be unique

    def split_frame_path(self, frame_path):
        """
        This extract movie and frame components from full frame_path.
        Args:
            frame_path: complete path to the frame: movies_path_frame_id

        Returns:
            path_to_movie, frame_id
        """
        path_to_movie, frame_id = frame_path.rsplit("_", maxsplit=1)
        return path_to_movie, frame_id

    def __get_frame_path(self, path_set, name_or_num):
        if isinstance(name_or_num, numbers.Integral):
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
        path_to_movie, frame_nr = self.split_frame_path(path_to_frame)
        self.video_image_reader = MoviesLoader.prepare_reader(self.video_image_reader, path_to_movie)
        return self.video_image_reader[int(frame_nr)]

    def load_tag(self, name_or_num):
        if isinstance(name_or_num, numbers.Integral):
            name_or_num = self.input_order[name_or_num]
        return self.json_tags.get(name_or_num, None)

    def load_annotation(self, name_or_num) -> t.Optional[pathlib.Path]:
        path_to_frame = self.__get_frame_path(self.annotation_paths, name_or_num)
        if path_to_frame is None:
            return None
        path_to_movie, frame_nr = self.split_frame_path(path_to_frame)
        self.video_annotation_reader = MoviesLoader.prepare_reader(self.video_annotation_reader, path_to_movie)
        # TODO this can be single or multichannel - perhaps someone should check that or convert to single channel?
        annotation_array = self.video_annotation_reader[int(frame_nr)]
        # The annotation video can be compressed so that it is not [0,1] or [0,255] but be a spread.
        if self.annotation_as_mask:
            return annotation_array >= 128
        return annotation_array

    def get_relative_path(self, name_or_num):
        """
        Determine the relative path to the given frame.
        Used by Savers.
        Args:
            name_or_num: frame_id or number in entire MoviesLoader

        Returns: movie_id/frame_id
        """
        if isinstance(name_or_num, numbers.Integral):
            name_or_num = self.input_order[name_or_num]
        movie_id = self.load_tag(name_or_num)['movie_id']
        # TODO in perfect world it would do entire hierarchy up to the movie id
        return os.path.join(movie_id, name_or_num)

    def __str__(self):
        return f"MovieLoader for: {self.data_root}"
