import itertools
import numpy as np
import os
import unittest
from pathlib import Path

import sep.loaders.movies
from sep.loaders import MoviesLoader, FrameByGroupSelector, FrameByIntervalSelector
from tests.testbase import TestBase


class TestMoviesLoader(TestBase):
    def test_loading(self):
        with MoviesLoader.from_tree(self.root_test_dir("input/reptiles"),
                                    framerate=10, clips_len=5, clips_skip=10) as test_movies_loader:
            self.assertEqual(2, len(test_movies_loader.list_movies()))
            self.assertEqual(2, len(test_movies_loader.list_movies_paths()))

            self.assertEqual('Dinosaur - 1438_00000', test_movies_loader.list_images()[0])
            self.assertIn('Dragon - 32109_00000', test_movies_loader.list_images())
            self.assertEqual(63, len(test_movies_loader.list_images_paths()))

            # TODO check that first data
            tag_1 = test_movies_loader.load_tag('Dinosaur - 1438_00000')
            annotation_1 = test_movies_loader.load_annotation('Dinosaur - 1438_00000')
            image_1 = test_movies_loader.load_image('Dinosaur - 1438_00000')
            self.assertArray(image_1, 3, np.uint8)
            self.assertIsNone(annotation_1)
            self.assertSubset(tag_1, {'id': 'Dinosaur - 1438_00000', 'pos': 0, 'pos_clip': 0, 'clip_nr': 0, 'timestamp': 0.0})
            self.assertSubset(tag_1, {'movie_id': 'dinosaur_1', 'movie_source': 'pixabay', 'movie_type': 'running'})

            tag_2 = test_movies_loader.load_tag('Dinosaur - 1438_00037')
            annotation_2 = test_movies_loader.load_annotation('Dinosaur - 1438_00037')
            image_2 = test_movies_loader.load_image('Dinosaur - 1438_00037')
            self.assertArray(image_2, 3, np.uint8)
            self.assertIsNone(annotation_2)
            self.assertSubset(tag_2, {'id': 'Dinosaur - 1438_00037', 'pos': 37, 'pos_clip': 1, 'clip_nr': 1})
            self.assertAlmostEqual(1.608, tag_2['timestamp'], places=2)
            self.assertSubset(tag_2, {'movie_id': 'dinosaur_1', 'movie_source': 'pixabay', 'movie_type': 'running'})

            next_image_id = test_movies_loader.list_images().index('Dinosaur - 1438_00037') + 1

            tag_3 = test_movies_loader.load_tag(next_image_id)
            self.assertSubset(tag_3, {'id': 'Dinosaur - 1438_00040', 'pos': 40, 'pos_clip': 2, 'clip_nr': 1})
            self.assertAlmostEqual(1.739, tag_3['timestamp'], places=2)

            # images different
            self.np_assert_not_equal(image_1, image_2)

            # load last image
            tag_last = test_movies_loader.load_tag(62)
            annotation_last = test_movies_loader.load_annotation(62)
            image_last = test_movies_loader.load_image(62)
            self.assertArray(image_last, 3, np.uint8)
            self.assertIsNone(annotation_last)
            self.assertSubset(tag_last, {'id': 'Dragon - 32109_00311', 'pos': 311, 'pos_clip': 2, 'clip_nr': 7})
            self.assertAlmostEqual(10.724, tag_last['timestamp'], places=2)
            self.assertSubset(tag_last, {'movie_id': 'dragon_1', 'movie_source': 'pixabay', 'movie_type': 'flying'})

    def test_loading_iterations(self):
        with MoviesLoader.from_tree(self.root_test_dir("input/reptiles"),
                                    framerate=5, clips_len=1, clips_skip=10) as test_movies_loader:
            self.assertEqual(9, len(test_movies_loader.list_images_paths()))
            for sample in itertools.islice(test_movies_loader, 0, 5):
                tag = sample['tag']
                annotation = sample['annotation']
                image = sample['image']
                self.assertArray(image, 3, np.uint8)
                self.assertIsNone(annotation)
                self.assertSubset(tag, {'id': 'Dinosaur - 1438_00000', 'pos': 0, 'pos_clip': 0, 'clip_nr': 0})
                self.assertAlmostEqual(0, tag['timestamp'], places=2)
                self.assertSubset(tag, {'movie_id': 'dinosaur_1', 'movie_source': 'pixabay', 'movie_type': 'running'})
                return

    def test_load_movie_images(self):
        frame_selector = sep.loaders.movies.FrameByGroupSelector(clips_len=100000, clips_skip=30)
        loaded_frames = MoviesLoader.load_movie_images(self.root_test_dir("input/reptiles/Dinosaur - 1438.mp4"),
                                                       framerate=30, selector=frame_selector)
        loaded_images = loaded_frames['images']
        loaded_tags = loaded_frames['tags']
        self.assertEqual(157, len(loaded_images))
        self.assertEqual(157, len(loaded_tags))

        loaded_frames = MoviesLoader.load_movie_images(self.root_test_dir("input/reptiles/Dinosaur - 1438.mp4"),
                                                       framerate=None, selector=frame_selector)
        self.assertEqual(157, len(loaded_frames['images']))

        frame_selector = sep.loaders.movies.FrameByGroupSelector(clips_len=2, clips_skip=10)
        loaded_frames = MoviesLoader.load_movie_images(self.root_test_dir("input/reptiles/Dinosaur - 1438.mp4"),
                                                       framerate=None, selector=frame_selector)
        loaded_tags = loaded_frames['tags']
        self.assertEqual(27, len(loaded_tags))
        self.assertEqual('_00001', loaded_tags[1]['id'])
        self.assertEqual(1, loaded_tags[1]['pos'])
        self.assertEqual(0, loaded_tags[1]['clip_nr'])
        self.assertEqual('_00012', loaded_tags[2]['id'])
        self.assertEqual(12, loaded_tags[2]['pos'])
        self.assertEqual(1, loaded_tags[2]['clip_nr'])

    def test_relative(self):
        with MoviesLoader.from_tree(self.root_test_dir("input/reptiles"),
                                    framerate=5, clips_len=1, clips_skip=10) as movies_loader:
            data_names = movies_loader.list_images()
            self.assertEqual(9, len(data_names))
            self.assertEqual("Dinosaur - 1438_00000", data_names[0])
            self.assertEqual(os.path.join("dinosaur_1", "Dinosaur - 1438_00000"), movies_loader.get_relative_path(0))
            self.assertEqual(os.path.join("dinosaur_1", "Dinosaur - 1438_00000"),
                             movies_loader.get_relative_path("Dinosaur - 1438_00000"))

    def test_movie_annotations(self):
        with MoviesLoader.from_tree(self.root_test_dir("input/fafa"), framerate=5) as movies_loader:
            self.assertEqual(11, len(movies_loader))
            sample_0 = movies_loader[0]
            self.assertEqual((720, 1080, 3), sample_0['image'].shape)
            self.assertEqual((720, 1080, 3), sample_0['annotation'].shape)
            # it is compressed so that it is not exactly [0,1] or [0,255]
            self.assertTrue(len(np.unique(sample_0['annotation'])) > 60)
            sample_8 = movies_loader[8]
            self.assertEqual((720, 1080, 3), sample_8['image'].shape)
            self.assertEqual((720, 1080, 3), sample_8['annotation'].shape)
            self.assertTrue(len(np.unique(sample_0['annotation'])) > 60)
            self.np_assert_not_equal(sample_0['annotation'], sample_8['annotation'])

        # now with 'make-it-a-mask' option on
        with MoviesLoader.from_tree(self.root_test_dir("input/fafa"), framerate=5, annotation_as_mask=True) as movies_loader:
            sample_0 = movies_loader[0]
            self.assertEqual((720, 1080, 3), sample_0['annotation'].shape)
            # now it is turned into mask
            self.np_assert_equal([False, True], np.unique(sample_0['annotation']))

    def test_loading_with_listing(self):
        with self.create_temp("loader_listing.txt") as listing_file:
            listing_file.writelines(f"{Path('reptiles/Dragon - 32109.mp4')}, {Path('reptiles/Dragon - 32109_gt.mp4')}\n")

        with MoviesLoader.from_listing(self.root_test_dir("input"), filepath="loader_listing.txt",
                                       framerate=10, clips_len=5, clips_skip=10) as test_movies_loader:
            self.assertEqual(1, len(test_movies_loader.list_movies()))
            self.assertEqual(1, len(test_movies_loader.list_movies_paths()))

            tag = test_movies_loader.load_tag(0)
            self.assertEqual('Dragon - 32109', tag['movie_id'])
            self.assertIsNone(test_movies_loader.load_annotation(0))

        # now with tag
        with self.create_temp("loader_listing.txt") as listing_file:
            listing_file.writelines(
                f"{Path('reptiles/Dragon - 32109.mp4')}, {Path('reptiles/Dragon - 32109_gt.mp4')}, {Path('reptiles/Dragon - 32109.json')}\n")

        with MoviesLoader.from_listing(self.root_test_dir("input"), filepath="loader_listing.txt",
                                       framerate=10, clips_len=5, clips_skip=10) as test_movies_loader:
            self.assertEqual(1, len(test_movies_loader.list_movies()))

            tag = test_movies_loader.load_tag(0)
            self.assertEqual('dragon_1', tag['movie_id'])
            self.assertEqual('pixabay', tag['movie_source'])
            self.assertIsNone(test_movies_loader.load_annotation(0))


class TestFrameSelector(TestBase):
    def test_frame_group_selector(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        selector = FrameByGroupSelector(clips_len=2, clips_skip=1, skip_first=0, skip_last=0)
        self.assertEqual([([1, 2], 0), ([4, 5], 1), ([7, 8], 2), ([10], 3)], list(selector.select(data)))
        selector = FrameByGroupSelector(clips_len=2, clips_skip=1, skip_first=1, skip_last=3)
        self.assertEqual([([2, 3], 0), ([5, 6], 1)], list(selector.select(data)))

    def test_frame_interval_selector(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        selector = FrameByIntervalSelector(frames_to_extract=1, interval_start_time=1, interval_end_time=10)
        self.assertEqual([([6], 0)], list(selector.select(data)))

        selector = FrameByIntervalSelector(frames_to_extract=20, interval_start_time=1, interval_end_time=10)
        self.assertEqual(20, len(list(selector.select(data))))  # let it repeat itself

        selector = FrameByIntervalSelector(frames_to_extract=2, interval_start_time=1, interval_end_time=10)
        self.assertEqual([([4], 0), ([7], 1)], list(selector.select(data)))

        selector = FrameByIntervalSelector(frames_to_extract=3, interval_start_time=1, interval_end_time=10)
        self.assertEqual([([3], 0), ([6], 1), ([8], 2)], list(selector.select(data)))

        selector = FrameByIntervalSelector(frames_to_extract=4, interval_start_time=1, interval_end_time=10)
        self.assertEqual([([3], 0), ([5], 1), ([7], 2), ([9], 3)], list(selector.select(data)))

        selector = FrameByIntervalSelector(frames_to_extract=5, interval_start_time=1, interval_end_time=10)
        self.assertEqual([([2], 0), ([4], 1), ([6], 2), ([7], 3), ([9], 4)], list(selector.select(data)))

        selector = FrameByIntervalSelector(frames_to_extract=2, interval_start_time=3, interval_end_time=7)
        self.assertEqual([([4], 0), ([6], 1)], list(selector.select(data)))

    def test_frame_interval_selector_with_framerate(self):
        data = list(range(0, 30 * 5))

        selector = FrameByIntervalSelector(frames_to_extract=1, interval_start_time=1.7, interval_end_time=3.5)
        times = [2.6]
        frames = [([t * 30], i) for i, t in enumerate(times)]
        self.assertEqual(frames, list(selector.select(data, 30)))

        selector = FrameByIntervalSelector(frames_to_extract=3, interval_start_time=1.7, interval_end_time=3.5)
        # times = [2.15, 2.6, 3.05]  # -> [([64.5], 0), ([78.0], 1), ([91.5], 2)]
        frames = [([64], 0), ([78], 1), ([92], 2)]
        self.assertEqual(frames, list(selector.select(data, 30)))

        selector = FrameByIntervalSelector(frames_to_extract=5, interval_start_time=2.1, interval_end_time=4.6)
        # times = [2.516, 2.932, 3.348, 3.76, 4.18]  # -> [([75.48], 0), ([87.96], 1), ([100.44], 2), ([112.8], 3), ([125.39], 4)]
        frames = [([75], 0), ([88], 1), ([101], 2), ([113], 3), ([126], 4)]
        self.assertEqual(frames, list(selector.select(data, 30)))


if __name__ == '__main__':
    unittest.main()
