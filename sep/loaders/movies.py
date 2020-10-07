import imageio
import numpy as np
import pathlib
import typing as t

import sep._commons.movies
from sep.loaders.loader import Loader
from sep.loaders.files import FilesLoader


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
        self.files_loader = FilesLoader(data_root, input_extensions=input_extensions,
                                        annotation_extension='.mp4',
                                        annotation_for_image_finder=annotation_for_movie_finder,
                                        verbose=verbose)
        self.clips_skip = clips_skip
        self.clips_len = clips_len
        self.framerate = framerate
        self.video_reader = None

        self.input_images = {}  # self.path_to_id(p): p for p in input_images_paths}
        #self.input_order = sorted(self.input_images.keys())
        self.annotation_images = {}
        self.json_tags = {}


    def list_movies(self):
        return self.files_loader.list_images()

    def list_movies_paths(self):
        return self.files_loader.list_images_paths()

    def close(self):
        if self.video_reader:
            self.video_reader.release()

    @staticmethod
    def load_movie_images(movie_path, framerate: t.Optional[float], clips_len, clips_skip) -> dict:
        images = []
        tags = []
        with sep._commons.movies.StreamReader(movie_path) as video_reader:
            framerate = framerate or video_reader.frame_rate
            samples = list(video_reader.pos_samples(framerate))
            clip_nr = 0
            while samples:
                clip = samples[:clips_len]
                del samples[:clips_len + clips_skip]

                images += [f"_{c:05}" for c in clip]
                for c in clip:
                    tag = {"id": f"_{c:05}", "pos": c, "clip_nr": clip_nr,
                           "timestamp": c * video_reader.frame_interval}
                    tags.append(tag)

                clip_nr += 1
        return {'images': images, 'tags': tags}


    def __str__(self):
        return f"MovieLoader for: {self.data_root}"
