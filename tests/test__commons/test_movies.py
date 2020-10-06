import itertools

import numpy as np
import numpy.testing as nptest

import sep._commons.movies
from tests.testbase import TestBase


class TestVideoReader(TestBase):
    def test_reader(self):
        video_path = self.root_test_dir("input/reptiles/Dragon - 32109.mp4")
        with sep._commons.movies.StreamReader(video_path) as video:
            self.assertEqual(len(video), 313)
            last_frame = video[len(video) - 1]

            shape = []
            frame = None
            for image in video:
                frame = image
                shape.append(image.shape[0])
            self.assertEqual(1, len(np.unique(shape)))
            nptest.assert_equal(last_frame, frame)

    def test_process_as_file(self):
        video_path = self.root_test_dir("input/reptiles/Dragon - 32109.mp4")
        processed_path = self.add_temp("my_movie.mp4")

        thresholded = []
        with sep._commons.movies.StreamReader(video_path) as video:  # H264
            with sep._commons.movies.VideoWriter(processed_path, related_reader=video, encoding='H264') as writer:
                for image in itertools.islice(video, 0, 5):
                    thresholded.append(image.max(axis=-1) > 128)
                    writer.add(thresholded[-1], accept_bool=True)  # as bool

        with sep._commons.movies.StreamReader(processed_path) as video:
            third_processed = video[2]
            # It is not exact?? Compression??
            nptest.assert_allclose(thresholded[2] * 255, third_processed[..., 0], atol=5)

    def test_writer_data_types(self):
        written_path = self.add_temp("my_movie.mp4")

        with sep._commons.movies.VideoWriter(written_path, (100, 100), fps=30) as writer:
            # RGB image
            data_rgb = self.random_rgb((100, 100))
            writer.add(data_rgb)

            # single channel uint8
            data_single = self.random_rgb((100, 100))[..., 0]
            writer.add(data_single)

            # float array
            # it is not working...
            data_float = np.random.random((100, 100))
            writer.add(data_float, accept_float=True)

            # bool array
            # it is not working
            data_bool = np.random.random((100, 100)) > 0.5
            writer.add(data_bool, accept_bool=True)


