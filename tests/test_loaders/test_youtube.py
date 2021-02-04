import itertools
import numpy as np
import os
import unittest

import sep.loaders
from sep.loaders import YoutubeLoader
from tests.testbase import TestBase


class TestYoutubeLoader(TestBase):
    def test_loading(self):
        with YoutubeLoader.from_urls(['https://www.youtube.com/watch?v=_cLFseR-S50'], '720p',
                                     framerate=5, clips_len=5, clips_skip=10) as youtube_loader:
            self.assertEqual(1, len(youtube_loader.list_movies()))
            self.assertEqual(1, len(youtube_loader.list_movies_paths()))

            self.assertEqual('_cLFseR-S50_00000', youtube_loader.list_images()[0])
            self.assertEqual(447, len(youtube_loader.list_images_paths()))

            tag_1 = youtube_loader.load_tag('_cLFseR-S50_00000')
            annotation_1 = youtube_loader.load_annotation('_cLFseR-S50_00000')
            image_1 = youtube_loader.load_image('_cLFseR-S50_00000')
            self.assertArray(image_1, 3, np.uint8)
            self.assertIsNone(annotation_1)
            self.assertSubset(tag_1, {'id': '_cLFseR-S50_00000', 'pos': 0, 'pos_clip': 0, 'clip_nr': 0, 'timestamp': 0.0})
            self.assertSubset(tag_1, {'movie_id': '_cLFseR-S50', 'movie_title': 'Slipknot - Snuff (Violet Orlandi cover)',
                                      'movie_author': 'Violet Orlandi'})

    def test_iterating(self):
        with YoutubeLoader.from_urls(['https://www.youtube.com/watch?v=_cLFseR-S50'], '720p',
                                     framerate=5, clips_len=1, clips_skip=10) as youtube_loader:
            self.assertEqual(122, len(youtube_loader.list_images_paths()))

            for sample in itertools.islice(youtube_loader, 0, 5):
                tag = sample['tag']
                annotation = sample['annotation']
                image = sample['image']
                self.assertArray(image, 3, np.uint8)
                self.assertIsNone(annotation)
                self.assertSubset(tag, {'id': '_cLFseR-S50_00000', 'pos': 0, 'pos_clip': 0, 'clip_nr': 0, 'timestamp': 0.0})
                self.assertSubset(tag, {'movie_id': '_cLFseR-S50', 'movie_title': 'Slipknot - Snuff (Violet Orlandi cover)',
                                        'movie_author': 'Violet Orlandi'})
                return

    def test_sequential_urls(self):
        with YoutubeLoader.from_urls([], '720p', framerate=5, clips_len=10, clips_skip=1) as youtube_loader:
            self.assertEqual(0, len(youtube_loader.list_images_paths()))
            youtube_loader.add_url('https://www.youtube.com/watch?v=_cLFseR-S50',
                                   sep.loaders.FrameByGroupSelector(clips_len=1, clips_skip=10))
            self.assertEqual(122, len(youtube_loader.list_images_paths()))

            sample = youtube_loader[0]
            tag = sample['tag']
            annotation = sample['annotation']
            image = sample['image']
            self.assertArray(image, 3, np.uint8)
            self.assertIsNone(annotation)
            self.assertSubset(tag, {'id': '_cLFseR-S50_00000', 'pos': 0, 'pos_clip': 0, 'clip_nr': 0, 'timestamp': 0.0})
            self.assertSubset(tag, {'movie_id': '_cLFseR-S50', 'movie_title': 'Slipknot - Snuff (Violet Orlandi cover)',
                                    'movie_author': 'Violet Orlandi'})
        with YoutubeLoader('720p', framerate=5) as youtube_loader:
            self.assertEqual(0, len(youtube_loader.list_images_paths()))
            youtube_loader.add_url('https://www.youtube.com/watch?v=_cLFseR-S50',
                                   sep.loaders.FrameByGroupSelector(clips_len=1, clips_skip=10))
            self.assertEqual(122, len(youtube_loader.list_images_paths()))

    def test_relative(self):
        with YoutubeLoader.from_urls(['https://www.youtube.com/watch?v=_cLFseR-S50'], '720p',
                                     framerate=5, clips_len=1, clips_skip=10) as youtube_loader:
            data_names = youtube_loader.list_images()
            self.assertEqual(122, len(data_names))
            self.assertEqual("_cLFseR-S50_00000", data_names[0])
            self.assertEqual(os.path.join("_cLFseR-S50", "_cLFseR-S50_00000"), youtube_loader.get_relative_path(0))
            self.assertEqual(os.path.join("_cLFseR-S50", "_cLFseR-S50_00000"),
                             youtube_loader.get_relative_path("_cLFseR-S50_00000"))

    def test_get_interval_group(self):
        with YoutubeLoader('360p') as youtube_loader:
            selector = sep.loaders.FrameByIntervalSelector(frames_to_extract=10, interval_start_time=1.0, interval_end_time=11.0)
            youtube_loader.add_url('https://www.youtube.com/watch?v=_cLFseR-S50', selector=selector,
                                   user_info={"sex": "woman", "hair": "dark"})
            data_names = youtube_loader.list_images()
            self.assertEqual(10, len(data_names))


if __name__ == '__main__':
    unittest.main()
