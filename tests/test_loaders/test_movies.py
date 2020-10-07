import unittest

from sep.loaders import MoviesLoader
from tests.testbase import TestBase


class TestMoviesLoader(TestBase):
    def test_loading(self):
        test_movies_loader = MoviesLoader(self.root_test_dir("input/reptiles"),
                                          framerate=10, clips_len=5, clips_skip=10)

        self.assertEqual(2, len(test_movies_loader.list_movies()))
        self.assertEqual(2, len(test_movies_loader.list_movies_paths()))

        """

        input_data_02_by_id = test_images_loader.load_image(1)
        input_data_02_by_name = test_images_loader.load_image('lights02')
        nptest.assert_equal(input_data_02_by_id, input_data_02_by_name)

        tag_02 = test_images_loader.load_tag('lights02')
        self.assertEqual("lights02", tag_02["id"])
        self.assertEqual("thenet", tag_02["source"])
        non_existing_tag10 = test_images_loader.load_tag('lights10')
        self.assertEqual("lights10", non_existing_tag10["id"])
        self.assertNotIn("source", non_existing_tag10)

        annotation_1 = test_images_loader.load_annotation(0)
        self.assertEqual(annotation_1.shape, input_data_02_by_id.shape[:2])
        self.assertEqual(255, annotation_1.max())

        tag_1 = test_images_loader.load_tag(0)
        self.assertEqual(0, tag_1["id"])  # TODO RETHINK default tags mirror exact call
        """

    def test_load_movie_images(self):
        loaded_frames = MoviesLoader.load_movie_images(self.root_test_dir("input/reptiles/Dinosaur - 1438.mp4"),
                                                       framerate=30, clips_len=100000, clips_skip=30)
        loaded_images = loaded_frames['images']
        loaded_tags = loaded_frames['tags']
        self.assertEqual(157, len(loaded_images))
        self.assertEqual(157, len(loaded_tags))

        loaded_frames = MoviesLoader.load_movie_images(self.root_test_dir("input/reptiles/Dinosaur - 1438.mp4"),
                                                       framerate=None, clips_len=100000, clips_skip=30)
        self.assertEqual(157, len(loaded_frames['images']))

        loaded_frames = MoviesLoader.load_movie_images(self.root_test_dir("input/reptiles/Dinosaur - 1438.mp4"),
                                                       framerate=None, clips_len=2, clips_skip=10)
        loaded_tags = loaded_frames['tags']
        self.assertEqual(27, len(loaded_tags))
        self.assertEqual('_00001', loaded_tags[1]['id'])
        self.assertEqual(1, loaded_tags[1]['pos'])
        self.assertEqual(0, loaded_tags[1]['clip_nr'])
        self.assertEqual('_00012', loaded_tags[2]['id'])
        self.assertEqual(12, loaded_tags[2]['pos'])
        self.assertEqual(1, loaded_tags[2]['clip_nr'])


if __name__ == '__main__':
    unittest.main()
