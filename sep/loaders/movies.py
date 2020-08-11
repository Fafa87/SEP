from abc import ABC

from sep.loaders.loader import Loader


class MoviesLoader(Loader, ABC):
    """
    This one loads frames from the movies files and tags them so that they can be reorganizes into the files
    after evaluation. It also provides timestamp so that real time solution can be tested as well.
    """
    def __init__(self, data_root, framerate, clips_len, clips_count):
        super().__init__()